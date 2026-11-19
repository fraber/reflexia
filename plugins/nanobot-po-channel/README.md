# nanobot-po-channel

`projop-openai` — a nanobot channel plugin that exposes a **synchronous,
OpenAI-compatible HTTP endpoint** so a GUI can talk to nanobot on behalf of a
]project-open[ user.

## Wire protocol

`POST /v1/chat/completions`

```json
{
  "model": "qwen2.5",
  "user_id": 8799,
  "auth_token": "<optional ]po[ auto-login token>",
  "messages": [
    {"role": "user", "content": "hi!"},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "What is your LLM name?"}
  ]
}
```

* `model` is informational — nanobot replies with its configured model.
* `user_id` (required) maps to a stable per-human session: `chat_id = po-user-{user_id}`.
* `auth_token` is passed through in message metadata (`po_token`) for later
  per-user REST calls; v1 performs **no validation** (handled on the ]po[ side).
* The full `messages` list is treated as **authoritative** (see below).

### Response (HTTP 200)

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1756062000,
  "model": "qwen2.5",
  "choices": [{"index": 0, "finish_reason": "stop",
               "message": {"role": "assistant", "content": "..."}}],
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
  "nanobot": {"chat_id": "po-user-8799", "latency_ms": 1234}
}
```

### Errors (OpenAI-style `{"error": {...}}`)

| Status | Meaning |
|--------|---------|
| 400    | malformed payload (bad JSON, missing `user_id`, bad roles, last message not `user`) |
| 403    | sender not in channel `allow_from` |
| 409    | same user already has a request in flight |
| 500    | internal failure while processing |
| 504    | agent did not reply within `timeout_seconds` |

Tool-level failures (e.g. a ]po[ REST error) are *narrated by the agent* in the
normal 200 reply — the agent sees the tool error and explains it.

## Async jobs (timer-only polling)

For clients that must not hold an HTTP connection open for the whole agent run
(the ]po[ GUI's `chat.tcl`), the same payload can be submitted asynchronously:

```
POST /v1/jobs          same payload as /v1/chat/completions
                 -> 202 {"job_id": "<32-hex>"}

GET  /v1/jobs/{job_id} -> {"job_id": ..., "status": "running"|"done"|"error",
                           "elapsed_s": <int>, "reply": "...", "error": "..."}
```

- Unknown or expired ids answer `{"status": "error", "reason": "expired"}`
  with HTTP 200, so pollers can treat every response uniformly.
- Jobs are timer-only: no partial text streaming (the installed nanobot core
  does not deliver stream deltas to channels).
- Sync requests and jobs share the per-user concurrency guard (409 both ways).
- Finished jobs are kept until TTL (`job_ttl_seconds`, default 600 s) and then
  swept.

## History semantics

Only the last user message of the client's `messages` list is forwarded;
nanobot's own per-chat session history is authoritative for conversation
context. Earlier entries in the client list are validated but otherwise
ignored — no mirror, no divergence detection.

## Config (`config.json` → `channels`)

```json
"projop-openai": {
  "enabled": true,
  "host": "127.0.0.1",
  "port": 8090,
  "path": "/v1/chat/completions",
  "timeout_seconds": 300,
  "jobs_path": "/v1/jobs",
  "job_ttl_seconds": 600,
  "allow_from": ["*"]
}
```

## Install (when approved)

```bash
/home/nanobot/nanobot/venv/bin/pip install -e /home/nanobot/.nanobot/workspace/plugins/nanobot-po-channel
```

then add the config block above and restart nanobot. The entry point group is
`nanobot.channels`, name `projop-openai`.

## Limitations (v1)

* No streaming (single synchronous reply), no token validation, no media.
* `system`/`developer` messages in the client list are ignored; nanobot's own
  system prompt always applies.
* Your installed nanobot (venv, 0.2.1) is older than the source tree at
  /home/nanobot/nanobot: installed uses _progress-style metadata flags on
  outbound messages; the newer source uses an event field.
  The plugin targets the installed version.
  If you ever switch to an editable install of the newer tree, send() needs a
  one-line adjustment.
  
