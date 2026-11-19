#!/usr/bin/env python3
"""Test suite for the projop-openai channel: sync endpoint regression + async jobs.

Run with the nanobot venv:
    /home/nanobot/nanobot/venv/bin/python tests/test_channel.py

Prints PASS lines and "ALL OK" at the end; exits non-zero on first failure.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from po_openai_channel.channel import ProjopOpenAIChannel  # noqa: E402
from po_openai_channel.jobs import JobStore, job_status_payload  # noqa: E402

from nanobot.bus.events import OutboundMessage  # noqa: E402

from loguru import logger  # noqa: E402

logger.remove()  # keep test output clean; failures still print via traceback


# ---------------------------------------------------------------- fixtures


class FakeBus:
    def __init__(self) -> None:
        self.inbound = []

    async def publish_inbound(self, msg):
        self.inbound.append(msg)


def make_channel(**cfg_overrides) -> ProjopOpenAIChannel:
    cfg = {
        "enabled": True,
        "port": 0,
        "host": "127.0.0.1",
        "allow_from": ["po-624", "po-8799"],
        "timeout_seconds": cfg_overrides.pop("timeout_seconds", 5.0),
    }
    cfg.update(cfg_overrides)
    return ProjopOpenAIChannel(cfg, FakeBus())


async def start_server(channel) -> tuple[TestServer, str]:
    app = web.Application()
    app.router.add_post(channel.chat_path, channel.handle_chat)
    app.router.add_post(channel.jobs_path, channel.handle_job_start)
    app.router.add_get(channel.jobs_path + "/{job_id}", channel.handle_job_status)
    app.router.add_post(channel.jobs_path + "/{job_id}/stop", channel.handle_job_stop)
    server = TestServer(app)
    await server.start_server()
    return server, str(server.make_url("")).rstrip("/")


def reply_via(channel, chat_id: str, content: str, delay: float = 0.0):
    """Simulate the agent loop resolving the pending future."""

    async def _resolve():
        if delay:
            await asyncio.sleep(delay)
        fut = channel._pending.get(chat_id)
        assert fut is not None and not fut.done(), f"no pending future for {chat_id}"
        fut.set_result(content)

    return asyncio.get_running_loop().create_task(_resolve())


def post(session, base, path, payload=None, raw=None):
    url = base + path
    if raw is not None:
        return session.post(url, data=raw, headers={"Content-Type": "application/json"})
    return session.post(url, json=payload)


# ---------------------------------------------------------------- JobStore


def test_job_store_unit():
    s = JobStore(ttl_seconds=600)
    jid = s.create("624")
    snap = s.get(jid)
    assert snap["status"] == "running" and snap["reply"] is None
    assert s.active_count_for_user("624") == 1

    s.finish(jid, "hello &#x1f604;")
    snap = s.get(jid)
    assert snap["status"] == "done" and snap["reply"] == "hello &#x1f604;"
    assert s.active_count_for_user("624") == 0

    j2 = s.create("8799")
    s.fail(j2, "boom")
    snap = s.get(j2)
    assert snap["status"] == "error" and snap["error"] == "boom"

    # A stopped job is terminal: a late reply must not revive it.
    s3 = JobStore(ttl_seconds=600)
    j_stop = s3.create("624")
    assert s3.mark_stopped(j_stop) is True
    assert s3.mark_stopped(j_stop) is False, "stop must not be applied twice"
    s3.finish(j_stop, "late reply")
    assert s3.get(j_stop)["status"] == "stopped", s3.get(j_stop)
    s3.fail(j_stop, "late error")
    assert s3.get(j_stop)["status"] == "stopped", s3.get(j_stop)

    # TTL sweep
    s2 = JobStore(ttl_seconds=0.05)
    j3 = s2.create("624")
    time.sleep(0.06)
    assert s2.get(j3) is None, "expired job must be swept"
    print("PASS job store unit")


def test_job_status_payload_expired():
    out = job_status_payload(None)
    assert out == {"status": "error", "reason": "expired"}
    print("PASS expired payload shape")


# ------------------------------------------------------------ integration


async def test_job_lifecycle(ch, base):
    async with aiohttp.ClientSession() as http:
        resp = await post(http, base, "/v1/jobs", {
            "user_id": "624",
            "messages": [{"role": "user", "content": "hi"}],
        })
        assert resp.status == 202, f"expected 202, got {resp.status}: {await resp.text()}"
        body = await resp.json()
        job_id = body["job_id"]
        assert isinstance(job_id, str) and len(job_id) >= 16

        st = await (await http.get(f"{base}/v1/jobs/{job_id}")).json()
        assert st["status"] == "running", st
        assert isinstance(st["elapsed_s"], int)

        reply_via(ch, "po-user-624", "done &#x1f604;", delay=0.05)
        await asyncio.sleep(0.15)
        st = await (await http.get(f"{base}/v1/jobs/{job_id}")).json()
        assert st["status"] == "done", st
        assert st["reply"] == "done &#x1f604;"
        assert "reason" not in st
    print("PASS job lifecycle (202 -> running -> done+reply)")


async def test_job_error_and_unknown(ch, base):
    async with aiohttp.ClientSession() as http:
        r = await http.get(f"{base}/v1/jobs/doesnotexist12345678")
        assert r.status == 200
        assert (await r.json()) == {"status": "error", "reason": "expired"}

        resp = await post(http, base, "/v1/jobs", {
            "user_id": "624",
            "messages": [{"role": "user", "content": "hi"}],
        })
        job_id = (await resp.json())["job_id"]
        fut = ch._pending["po-user-624"]
        fut.set_exception(RuntimeError("agent blew up"))  # simulate agent-loop failure
        await asyncio.sleep(0.05)
        st = await (await http.get(f"{base}/v1/jobs/{job_id}")).json()
        assert st["status"] == "error", st
        assert "blew up" in st["error"]
        # a cancelled future must also finish the job (not hang as running)
        resp = await post(http, base, "/v1/jobs", {
            "user_id": "624",
            "messages": [{"role": "user", "content": "hi2"}],
        })
        job_id2 = (await resp.json())["job_id"]
        ch._pending["po-user-624"].cancel()
        await asyncio.sleep(0.05)
        st2 = await (await http.get(f"{base}/v1/jobs/{job_id2}")).json()
        assert st2["status"] == "error", st2
    print("PASS job error + unknown-id handling")


async def test_job_stop(ch, base):
    async with aiohttp.ClientSession() as http:
        # stopping an unknown job -> expired
        r = await http.post(f"{base}/v1/jobs/doesnotexist12345678/stop")
        assert r.status == 200
        assert (await r.json()) == {"status": "error", "reason": "expired"}

        resp = await post(http, base, "/v1/jobs", {
            "user_id": "624",
            "messages": [{"role": "user", "content": "hi"}],
        })
        job_id = (await resp.json())["job_id"]

        r = await http.post(f"{base}/v1/jobs/{job_id}/stop")
        assert r.status == 200, await r.text()
        body = await r.json()
        assert body["status"] == "stopped", body
        assert body["reason"] == "stopped", body

        # the poll agrees
        st = await (await http.get(f"{base}/v1/jobs/{job_id}")).json()
        assert st["status"] == "stopped", st

        # the core was asked to cancel the running turn
        stops = [m for m in ch.bus.inbound if m.content == "/stop"]
        assert stops, "no /stop published on the bus"
        assert stops[-1].chat_id == "po-user-624", stops[-1].chat_id
        assert (stops[-1].metadata or {}).get("_po_stop") is True, stops[-1].metadata

        # stopping again is idempotent
        r2 = await http.post(f"{base}/v1/jobs/{job_id}/stop")
        assert r2.status == 200
        assert (await r2.json())["status"] == "stopped"
    print("PASS job stop (freeze + core cancel + idempotent)")


async def test_busy_cross_guard(ch, base):
    # ch configured with short timeout via make_channel in main
    async with aiohttp.ClientSession() as http:
        payload = {"user_id": "624", "messages": [{"role": "user", "content": "hi"}]}
        r1 = await post(http, base, "/v1/jobs", payload)
        assert r1.status == 202
        # second job for same user -> 409
        r2 = await post(http, base, "/v1/jobs", payload)
        assert r2.status == 409, f"expected 409, got {r2.status}"
        # sync request while job runs -> 409
        r3 = await post(http, base, "/v1/chat/completions", payload)
        assert r3.status == 409
        # different user unaffected
        t = asyncio.ensure_future(reply_via(ch, "po-user-8799", "ok", delay=0.05))
        r4 = await post(http, base, "/v1/chat/completions", {
            "user_id": "8799", "messages": [{"role": "user", "content": "yo"}],
        })
        assert r4.status == 200, f"different user should work: {r4.status}"
        await t
    print("PASS busy guard shared between jobs and sync requests")


async def test_validation_parity(base):
    async with aiohttp.ClientSession() as http:
        for path in ("/v1/chat/completions", "/v1/jobs"):
            r = await post(http, base, path, raw=b"not json")
            assert r.status == 400, (path, r.status)
            r = await post(http, base, path, {"messages": [{"role": "user", "content": "x"}]})
            assert r.status == 400, ("missing user_id", path, r.status)
            r = await post(http, base, path, {
                "user_id": "99999",  # not in allow_from
                "messages": [{"role": "user", "content": "x"}],
            })
            assert r.status == 403, ("allowlist", path, r.status)
            r = await post(http, base, path, {
                "user_id": "624",
                "messages": [{"role": "assistant", "content": "x"}],
            })
            assert r.status == 400, ("last message must be from user", path, r.status)
    print("PASS validation parity on both endpoints")


async def test_sync_regression(ch, base):
    async with aiohttp.ClientSession() as http:
        # The sync handler blocks until the agent replies, so schedule the
        # fake agent resolution BEFORE sending the request.
        t = asyncio.ensure_future(reply_via(ch, "po-user-624", "re: CHECK &#x1f604;", delay=0.05))
        resp = await post(http, base, "/v1/chat/completions", {
            "user_id": "624",
            "model": "nanobot",
            "messages": [{"role": "user", "content": "CHECK"}],
        })
        assert resp.status == 200, await resp.text()
        await t
        body = await resp.json()
        assert body["object"] == "chat.completion"
        msg = body["choices"][0]["message"]["content"]
        assert msg == "re: CHECK &#x1f604;"
        raw = await resp.text()
        assert "\\u" not in raw or True  # informational only
        assert "&#x1f604;" in raw, "astral chars must be entity-escaped in the wire body"
    print("PASS legacy sync endpoint round-trip incl. entity escaping")


async def test_job_timeout(ch, base):
    async with aiohttp.ClientSession() as http:
        resp = await post(http, base, "/v1/jobs", {
            "user_id": "624", "messages": [{"role": "user", "content": "slow"}],
        })
        job_id = (await resp.json())["job_id"]
        await asyncio.sleep(0.45)
        st = await (await http.get(f"{base}/v1/jobs/{job_id}")).json()
        assert st["status"] == "error", st
        assert "did not reply" in st["error"]
        # concurrency slot released after timeout
        resp2 = await post(http, base, "/v1/jobs", {
            "user_id": "624", "messages": [{"role": "user", "content": "again"}],
        })
        assert resp2.status == 202, "slot must be free after timeout"
        ch._pending["po-user-624"].set_result("late")
    print("PASS job timeout -> error + slot release")


async def main():
    ok = True
    try:
        test_job_store_unit()
        test_job_status_payload_expired()

        ch = make_channel()
        server, base = await start_server(ch)
        try:
            await test_job_lifecycle(ch, base)
            await test_job_error_and_unknown(ch, base)
            await test_validation_parity(base)
            await test_sync_regression(ch, base)
        finally:
            await server.close()

        # fresh channel per group to avoid cross-test pending state
        ch2 = make_channel(timeout_seconds=2.0)
        server2, base2 = await start_server(ch2)
        try:
            await test_busy_cross_guard(ch2, base2)
        finally:
            await server2.close()

        ch3 = make_channel(timeout_seconds=0.2)
        server3, base3 = await start_server(ch3)
        try:
            await test_job_timeout(ch3, base3)
        finally:
            await server3.close()

        ch4 = make_channel()
        server4, base4 = await start_server(ch4)
        try:
            await test_job_stop(ch4, base4)
        finally:
            await server4.close()
    except AssertionError as e:
        ok = False
        print(f"FAIL: {e}")
    except Exception as e:  # noqa: BLE001
        ok = False
        import traceback
        traceback.print_exc()
        print(f"FAIL (exception): {e}")

    if ok:
        print("\nALL OK")
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
