#!/usr/bin/env python3
"""Focused debug: why does the pending future vanish after POST /v1/jobs?"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer

from tests.test_channel import FakeBus, make_channel
from nanobot.bus.events import OutboundMessage


async def main():
    ch = make_channel()
    print("channel type:", type(ch).__name__)
    print("has _jobs:", hasattr(ch, "_jobs"))

    # instrument _run_job
    orig = ch._run_job

    async def traced(job_id, ctx, fut):
        print(f"[trace] _run_job start {job_id} chat={ctx['chat_id']}")
        try:
            await orig(job_id, ctx, fut)
            print(f"[trace] _run_job done {job_id}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[trace] _run_job RAISED {e!r}")

    ch._run_job = traced

    app = web.Application()
    app.router.add_post(ch.jobs_path, ch.handle_job_start)
    app.router.add_get(ch.jobs_path + "/{job_id}", ch.handle_job_status)
    server = TestServer(app)
    await server.start_server()
    base = str(server.make_url("")).rstrip("/")

    async with aiohttp.ClientSession() as http:
        r = await http.post(base + "/v1/jobs", json={
            "user_id": "624", "messages": [{"role": "user", "content": "hi"}]})
        print("POST ->", r.status, await r.text())
        await asyncio.sleep(0.1)
        print("pending keys:", list(ch._pending.keys()))
        print("job tasks:", ch._job_tasks)

        # resolve manually like send() would
        msg = OutboundMessage(channel=ch.name, chat_id="po-user-624",
                              content="hello &#x1f604;", metadata={})
        await ch.send(msg)
        await asyncio.sleep(0.1)
        st = await (await http.get(base + "/v1/jobs/" + r_json if False else "")) if False else None
    await server.close()


asyncio.run(main())
