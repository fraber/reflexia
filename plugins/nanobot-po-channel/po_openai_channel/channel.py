"""projop-openai: synchronous OpenAI-compatible HTTP channel for ]project-open[ users.

Wire protocol (POST {path})::

    {
      "model": "qwen2.5",              # informational only; nanobot's model replies
      "user_id": 8799,                 # required; ]po[ user id
      "auth_token": "...",             # optional; passed through in metadata
      "messages": [ {"role": "user"|"assistant"|"system", "content": "..."} ]
    }

Response (HTTP 200)::

    {"id": "chatcmpl-...", "object": "chat.completion", "created": 1756062000,
     "model": "<as requested>", "choices": [{"index": 0, "finish_reason": "stop",
     "message": {"role": "assistant", "content": "..."}}],
     "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
     "nanobot": {"chat_id": "po-user-8799", "latency_ms": 1234}}

Errors use OpenAI-style error JSON with meaningful HTTP status codes:
400 bad payload, 401/403 denied by allow_from, 409 same user still processing,
504 agent timeout, 500 internal.

Async jobs (timer-only): POST {jobs_path} accepts the same payload and
answers 202 {"job_id": "..."} immediately; the agent runs in a background
task. GET {jobs_path}/{job_id} reports {"status": "running"|"done"|"error",
"elapsed_s", "reply", "error"}; unknown/expired ids answer
{"status": "error", "reason": "expired"}. Jobs share the per-chat
concurrency guard with sync requests. While a job runs, model reasoning
("thinking") chunks are buffered per job and reported as "reasoning"
(live segment), "reasoning_prev" and "reasoning_count" fields.

History semantics: only the last user message is forwarded; nanobot's own
per-chat session history is authoritative for conversation context.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
import uuid
from typing import Any

from aiohttp import web

from nanobot.bus.events import OutboundMessage
from nanobot.channels.base import BaseChannel

from .jobs import JobStore, job_status_payload

CHANNEL_NAME = "projop-openai"

_VALID_ROLES = ("user", "assistant", "system", "developer")


# --------------------------------------------------------------------------- #
# Pure helpers (kept module-level so they are unit-testable without a server)
# --------------------------------------------------------------------------- #


def normalize_messages(raw: Any) -> list[tuple[str, str]]:
    """Validate an OpenAI-style message list and normalize it to (role, text) pairs.

    Accepts string content as well as OpenAI "content parts" arrays. Raises
    ValueError with a precise message on any malformed input.
    """
    if not isinstance(raw, list) or not raw:
        raise ValueError("'messages' must be a non-empty array")
    out: list[tuple[str, str]] = []
    for i, m in enumerate(raw):
        if not isinstance(m, dict):
            raise ValueError(f"messages[{i}] must be an object")
        role = m.get("role")
        if role not in _VALID_ROLES:
            raise ValueError(f"messages[{i}].role must be one of {_VALID_ROLES}, got {role!r}")
        content = m.get("content")
        if isinstance(content, list):
            text = "".join(
                p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"
            )
        elif isinstance(content, str):
            text = content
        elif content is None:
            text = ""
        else:
            raise ValueError(f"messages[{i}].content must be a string or content-parts array")
        out.append((role, text.strip()))
    if out[-1][0] != "user":
        raise ValueError("the last message must have role 'user'")
    return out


def openai_error(message: str, err_type: str = "invalid_request_error", code: str | None = None) -> dict[str, Any]:
    err: dict[str, Any] = {"message": message, "type": err_type}
    if code:
        err["code"] = code
    return {"error": err}


def completion_response(model: str, content: str, chat_id: str, latency_ms: int) -> dict[str, Any]:
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": content},
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "nanobot": {"chat_id": chat_id, "latency_ms": latency_ms},
    }


_ASTRAL_CHAR_RE = re.compile(r"[\U00010000-\U0010FFFF]")


def json_dumps_utf8(data: Any) -> str:
    """Serialize JSON as raw UTF-8, with astral characters HTML-escaped.

    The receiving NaviServer runs Tcl 8.5, whose UTF-8 decoder handles at
    most 3-byte sequences: each byte of a 4-byte sequence (astral
    characters, e.g. most emoji) is promoted to a separate Latin-1-range
    character — mojibake like "ðŸ˜„". BMP multi-byte characters (é, 中,
    ✨) decode fine and stay raw.

    Astral characters are therefore emitted as HTML numeric entities
    (&#x1f604;). Entities are pure ASCII, survive util::http decoding,
    util::json::parse and Tcl 8.5 untouched, and the browser renders
    them natively when the reply is inserted into the chat page.
    """
    serialized = json.dumps(data, ensure_ascii=False)
    return _ASTRAL_CHAR_RE.sub(lambda m: f"&#x{ord(m.group()):x};", serialized)


# --------------------------------------------------------------------------- #
# Channel
# --------------------------------------------------------------------------- #


class ProjopOpenAIChannel(BaseChannel):
    """Synchronous OpenAI-compatible HTTP channel keyed by ]po[ user id."""

    name = CHANNEL_NAME

    def __init__(self, config: Any, bus) -> None:
        super().__init__(config, bus)
        cfg = config if isinstance(config, dict) else {}
        self.host = str(cfg.get("host", "127.0.0.1"))
        self.port = int(cfg.get("port", 8090))
        self.chat_path = str(cfg.get("path", "/v1/chat/completions"))
        self.timeout_seconds = float(cfg.get("timeout_seconds", 300))
        # Shared REST secret minted by createserver52-docker.sh as apm_parameter
        # NanobotRESTSharedSecret; consumed by REST tools, not by the channel itself.
        self.po_rest_secret = str(cfg.get("poRestSecret") or cfg.get("po_rest_secret") or "") or None
        self.jobs_path = str(cfg.get("jobs_path", "/v1/jobs"))
        self.job_ttl_seconds = float(cfg.get("job_ttl_seconds", 600))
        self._runner: web.AppRunner | None = None
        # chat_id -> Future resolving with the assistant reply text
        self._pending: dict[str, asyncio.Future[str]] = {}
        # Timer-only async jobs (POST/GET {jobs_path}); see jobs.py
        self._jobs = JobStore(ttl_seconds=self.job_ttl_seconds)
        self._job_tasks: set[asyncio.Task] = set()
        # job_id -> runner task, so a stop request can cancel the waiter
        self._job_runners: dict[str, asyncio.Task] = {}
        # chat_id -> running job id, for send_reasoning_* buffering
        self._active_jobs: dict[str, str] = {}

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        app = web.Application()
        app.router.add_post(self.chat_path, self.handle_chat)
        app.router.add_post(self.jobs_path, self.handle_job_start)
        app.router.add_get(self.jobs_path + "/{job_id}", self.handle_job_status)
        app.router.add_post(self.jobs_path + "/{job_id}/stop", self.handle_job_stop)
        app.router.add_get("/healthz", self.handle_health)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()
        self.logger.info(f"{self.name} listening on http://{self.host}:{self.port}{self.chat_path}")

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
        for fut in self._pending.values():
            if not fut.done():
                fut.cancel()
        self._pending.clear()
        for task in list(self._job_tasks):
            task.cancel()
        self._job_tasks.clear()
        self._job_runners.clear()
        self._jobs.clear()
        self._active_jobs.clear()

    # -- outbound ------------------------------------------------------------

    async def send(self, msg: OutboundMessage) -> None:
        """Resolve the waiting HTTP request with the final assistant reply.

        Intermediate runtime messages (progress hints, tool hints, reasoning /
        stream deltas) are flagged with ``_``-prefixed metadata keys by the
        agent loop and are ignored here — only plain messages resolve futures.
        """
        meta = msg.metadata or {}
        if any(str(k).startswith("_") and v for k, v in meta.items()):
            return
        if not (msg.content or "").strip():
            # Empty outbound (e.g. blank pre-tool assistant turn) is never a
            # final reply — resolving the future with "" produces an empty
            # bubble and orphans the real reply arriving seconds later.
            self.logger.info(f"ignoring empty outbound for {msg.chat_id}")
            return
        fut = self._pending.get(msg.chat_id)
        if fut is not None and not fut.done():
            # --- PROBE-G0: reply text as received from nanobot core --------
            try:
                self.logger.info(
                    f"PROBE-G0 recv: chat={msg.chat_id} repr={msg.content[:40]!r} "
                    f"utf8_hex={msg.content.encode('utf-8', 'surrogatepass')[:48].hex()}"
                )
            except Exception:
                self.logger.exception("PROBE-G0 failed")
            fut.set_result(msg.content)
        else:
            self.logger.warning(f"reply for {msg.chat_id} has no pending request: {msg.content[:80]!r}")

    # -- reasoning ("thinking") hooks ----------------------------------------

    async def send_reasoning_delta(
        self, chat_id: str, delta: str, metadata: dict | None = None
    ) -> None:
        """Buffer a model-reasoning chunk onto the chat's running job.

        The channel manager routes _reasoning_delta messages here whenever
        show_reasoning is enabled (core default: True). metadata may carry
        inbound request fields (incl. po_token) - never used or logged.
        Sync requests have no job, so their reasoning is dropped.
        """
        job_id = self._active_jobs.get(chat_id)
        if job_id is not None and delta:
            self._jobs.append_reasoning(job_id, delta)

    async def send_reasoning_end(self, chat_id: str, metadata: dict | None = None) -> None:
        """Close the live reasoning segment (one per agent-loop iteration)."""
        job_id = self._active_jobs.get(chat_id)
        if job_id is not None:
            self._jobs.end_reasoning_segment(job_id)

    # -- inbound ---------------------------------------------------------

    async def handle_health(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "channel": self.name}, dumps=json_dumps_utf8)

    async def _validate_request(self, request: web.Request) -> tuple[dict | None, web.Response | None]:
        """Shared validation for the sync and job endpoints.

        Returns (ctx, None) on success or (None, error_response) on failure,
        with identical status codes and bodies for both endpoints.
        """
        try:
            payload = await request.json()
        except Exception:
            return None, web.json_response(openai_error("request body must be valid JSON"), status=400, dumps=json_dumps_utf8)
        if not isinstance(payload, dict):
            return None, web.json_response(openai_error("request body must be a JSON object"), status=400, dumps=json_dumps_utf8)

        user_id = payload.get("user_id")
        if user_id in (None, ""):
            return None, web.json_response(openai_error("'user_id' is required"), status=400, dumps=json_dumps_utf8)
        user_id = str(user_id)

        try:
            msgs = normalize_messages(payload.get("messages"))
        except ValueError as e:
            return None, web.json_response(openai_error(str(e)), status=400, dumps=json_dumps_utf8)

        requested_model = str(payload.get("model") or "nanobot")
        auth_token = payload.get("auth_token") or ""

        chat_id = f"po-user-{user_id}"
        sender_id = f"po-{user_id}"

        # Per-thread sessions (D9): chat.tcl / chat-start.tcl forward the
        # ]po[ ag_chat_thread id; the session key (chat_id) becomes
        # "po-user-<uid>-t<thread_id>" so each thread keeps its own
        # nanobot history. Absent/empty thread_id keeps the classic key.
        thread_id = str(payload.get("thread_id") or "").strip()
        if thread_id:
            if not re.fullmatch(r"[0-9]+", thread_id):
                return None, web.json_response(
                    openai_error(f"invalid thread_id {thread_id!r}"),
                    status=400,
                    dumps=json_dumps_utf8,
                )
            chat_id = f"po-user-{user_id}-t{thread_id}"

        # Fail fast on policy rejection instead of hanging until the timeout.
        if not self.is_allowed(sender_id):
            return None, web.json_response(
                openai_error(
                    f"sender {sender_id} is not allowed; add them to 'allow_from'",
                    "permission_error",
                ),
                status=403,
                dumps=json_dumps_utf8,
            )

        # Only the newest user turn is forwarded; nanobot's session history
        # provides the conversation context.
        content = msgs[-1][1]

        # Sync requests and jobs share the per-chat concurrency guard: a
        # pending future means either a sync request or a running job.
        if chat_id in self._pending and not self._pending[chat_id].done():
            return None, web.json_response(
                openai_error(
                    f"a request for user {user_id} is already being processed",
                    "timeout_error",
                    "busy",
                ),
                status=409,
                dumps=json_dumps_utf8,
            )

        ctx = {
            "user_id": user_id,
            "requested_model": requested_model,
            "auth_token": auth_token,
            "chat_id": chat_id,
            "sender_id": sender_id,
            "content": content,
        }
        return ctx, None

    async def handle_chat(self, request: web.Request) -> web.Response:
        started = time.monotonic()
        ctx, err = await self._validate_request(request)
        if err is not None:
            return err

        # Fraber 2028-08-25
        self.logger.info(
            f"Received message: user={ctx['user_id']} content={ctx['content'][:80]!r}"
        )

        loop = asyncio.get_running_loop()
        fut: asyncio.Future[str] = loop.create_future()
        self._pending[ctx["chat_id"]] = fut

        try:
            await self._handle_message(
                sender_id=ctx["sender_id"],
                chat_id=ctx["chat_id"],
                content=ctx["content"],
                metadata={
                    "po_user_id": ctx["user_id"],
                    "po_token": ctx["auth_token"],
                    "openai_model": ctx["requested_model"],
                },
            )
            reply = await asyncio.wait_for(fut, timeout=self.timeout_seconds)
        except asyncio.TimeoutError:
            self._pending.pop(ctx["chat_id"], None)
            return web.json_response(
                openai_error(
                    f"agent did not reply within {self.timeout_seconds:.0f}s",
                    "timeout_error",
                    "agent_timeout",
                ),
                status=504,
                dumps=json_dumps_utf8,
            )
        except Exception as e:  # noqa: BLE001 — surface any failure to the client
            self._pending.pop(ctx["chat_id"], None)
            self.logger.exception("failed processing request for {}", ctx["chat_id"])
            return web.json_response(openai_error(str(e), "internal_error"), status=500, dumps=json_dumps_utf8)

        self._pending.pop(ctx["chat_id"], None)

        latency_ms = int((time.monotonic() - started) * 1000)
        _resp = completion_response(ctx["requested_model"], reply, ctx["chat_id"], latency_ms)
        # --- PROBE-G1/G2: reply text vs serialized response body --------
        try:
            self.logger.info(
                f"PROBE-G1 reply: repr={reply[:40]!r} "
                f"utf8_hex={reply.encode('utf-8', 'surrogatepass')[:48].hex()}"
            )
            _body = json_dumps_utf8(_resp)
            self.logger.info(
                f"PROBE-G2 body: len={len(_body)} "
                f"head_hex={_body.encode('utf-8', 'surrogatepass')[:200].hex()}"
            )
        except Exception:
            self.logger.exception("PROBE-G1/G2 failed")
        return web.json_response(
            _resp,
            dumps=json_dumps_utf8,
        )

    # -- async jobs (timer-only) ---------------------------------------------

    async def handle_job_start(self, request: web.Request) -> web.Response:
        """Accept a chat turn and answer immediately with a job id.

        The agent runs in a background task; clients poll GET {jobs_path}/{id}.
        Same payload contract and validation as the sync endpoint.
        """
        ctx, err = await self._validate_request(request)
        if err is not None:
            return err

        # Jobs additionally respect their own per-user running-job guard.
        if self._jobs.active_count_for_user(ctx["user_id"]) > 0:
            return web.json_response(
                openai_error(
                    f"a request for user {ctx['user_id']} is already being processed",
                    "timeout_error",
                    "busy",
                ),
                status=409,
                dumps=json_dumps_utf8,
            )

        loop = asyncio.get_running_loop()
        fut: asyncio.Future[str] = loop.create_future()
        self._pending[ctx["chat_id"]] = fut
        job_id = self._jobs.create(ctx["user_id"])
        self._active_jobs[ctx["chat_id"]] = job_id

        task = asyncio.create_task(self._run_job(job_id, ctx, fut))
        self._job_tasks.add(task)
        self._job_runners[job_id] = task

        def _cleanup(t: asyncio.Task, jid: str = job_id) -> None:
            self._job_tasks.discard(t)
            if self._job_runners.get(jid) is t:
                self._job_runners.pop(jid, None)

        task.add_done_callback(_cleanup)

        return web.json_response({"job_id": job_id}, status=202, dumps=json_dumps_utf8)

    async def _run_job(self, job_id: str, ctx: dict, fut: asyncio.Future[str]) -> None:
        chat_id = ctx["chat_id"]
        try:
            await self._handle_message(
                sender_id=ctx["sender_id"],
                chat_id=chat_id,
                content=ctx["content"],
                metadata={
                    "po_user_id": ctx["user_id"],
                    "po_token": ctx["auth_token"],
                    "openai_model": ctx["requested_model"],
                },
            )
            reply = await asyncio.wait_for(fut, timeout=self.timeout_seconds)
            self._jobs.finish(job_id, reply)
        except asyncio.TimeoutError:
            self._jobs.fail(job_id, f"agent did not reply within {self.timeout_seconds:.0f}s")
        except asyncio.CancelledError:
            # Distinguish shutdown (this task was cancelled) from a cancelled
            # request future: only propagate on real task cancellation.
            if asyncio.current_task().cancelling() > 0:
                raise
            self._jobs.fail(job_id, "request cancelled")
        except Exception as e:  # noqa: BLE001 — record any failure on the job
            self.logger.exception(f"job {job_id} failed for {chat_id}")
            self._jobs.fail(job_id, str(e))
        finally:
            if self._pending.get(chat_id) is fut:
                self._pending.pop(chat_id, None)
            self._active_jobs.pop(chat_id, None)

    async def handle_job_status(self, request: web.Request) -> web.Response:
        """Poll a job. Unknown/expired ids answer status=error/reason=expired."""
        job_id = request.match_info["job_id"]
        return web.json_response(job_status_payload(self._jobs.get(job_id)), dumps=json_dumps_utf8)

    async def handle_job_stop(self, request: web.Request) -> web.Response:
        """Cancel a running job and answer with its (new) status.

        Same envelope as the poll endpoint, so a client can use the reply
        as its next poll result. Unknown/expired ids answer
        status=error/reason=expired (HTTP 200), like the poll endpoint.
        """
        job_id = request.match_info.get("job_id", "")
        if not re.fullmatch(r"[0-9a-f]{32}", job_id):
            return web.json_response(
                {"status": "error", "reason": "expired"}, dumps=json_dumps_utf8
            )
        job = self._jobs.get(job_id)
        if job is None:
            return web.json_response(
                {"status": "error", "reason": "expired"}, dumps=json_dumps_utf8
            )
        if job["status"] == "running":
            await self._stop_job(job_id, job)
        return web.json_response(
            job_status_payload(self._jobs.get(job_id)), dumps=json_dumps_utf8
        )

    async def _stop_job(self, job_id: str, job: dict) -> None:
        """Cancel the agent turn behind a job and freeze it as stopped.

        The running turn belongs to the core agent loop, not to this
        channel: it is cancelled through the core's own priority command
        ("/stop"), published on the bus under the very session key the
        turn runs with, so the core restores its partial-context
        checkpoint. The channel-side runner merely waits for the reply
        future, so it is dropped as well - the job stops waiting at once
        instead of running into the reply timeout.
        """
        # Recover the session key from the active-job registry (sync
        # requests and jobs share the per-chat concurrency guard, so the
        # running job's chat_id - including its "-t<thread_id>" suffix -
        # is the one mapped to this job_id). Fallback: classic key.
        chat_id = next(
            (cid for cid, jid in self._active_jobs.items() if jid == job_id),
            f"po-user-{job['user_id']}",
        )
        sender_id = f"po-{job['user_id']}"

        # Freeze first: a reply racing in must not flip the state back.
        self._jobs.mark_stopped(job_id)

        # Ask the core to cancel the agent turn for this session. The
        # "_po_stop" marker makes the core's confirmation reply ignored
        # by send() (it filters "_"-prefixed metadata).
        try:
            await self._handle_message(
                sender_id=sender_id,
                chat_id=chat_id,
                content="/stop",
                metadata={"_po_stop": True},
            )
        except Exception:  # noqa: BLE001 - a failed stop must not 500
            self.logger.exception(f"failed to publish /stop for job {job_id}")

        # Drop the channel-side waiter: its reply is no longer wanted.
        fut = self._pending.get(chat_id)
        if fut is not None and not fut.done():
            fut.cancel()
        task = self._job_runners.get(job_id)
        if task is not None and not task.done():
            task.cancel()
