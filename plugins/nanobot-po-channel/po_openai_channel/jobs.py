"""Timer-only async job store for the projop-openai channel.

Jobs let ]po['s chat.tcl hand a message to nanobot and poll for completion
instead of holding a synchronous HTTP connection open for the whole agent
run. A job carries status and elapsed time, plus the final reply once
done. Answer-text streaming is still not possible (the installed nanobot
core does not deliver stream deltas to channels), but model *reasoning*
("thinking") chunks do arrive via the send_reasoning_delta/end hooks and
are buffered here per job as discrete segments (one per agent-loop
iteration).

Wire contract:

    POST /v1/jobs          -> 202 {"job_id": "<hex>"}
    GET  /v1/jobs/{id}     -> {"job_id": ..., "status": "running"|"done"|"error",
                               "elapsed_s": <int>, "reply": "...", "error": "..."}
    POST /v1/jobs/{id}/stop -> cancels the running turn, answers the same
                               envelope with status "stopped"

While running and reasoning exists, three extra fields are reported:
"reasoning" (live segment text), "reasoning_prev" (earlier segments
joined by blank lines), "reasoning_count" (int).

Unknown or expired job ids answer {"status": "error", "reason": "expired"}
with HTTP 200 so that simple clients can treat polling uniformly.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

# Per-segment cap: reasoning can ramble and polls ship the full live text.
MAX_REASONING_CHARS = 20000


class JobStore:
    """In-memory job registry with TTL sweeping."""

    def __init__(self, ttl_seconds: float = 600.0) -> None:
        self.ttl_seconds = float(ttl_seconds)
        self._jobs: dict[str, dict[str, Any]] = {}

    # -- lifecycle -----------------------------------------------------------

    def create(self, user_id: str) -> str:
        """Register a new running job and return its id."""
        self.sweep()
        job_id = uuid.uuid4().hex
        now = time.time()
        self._jobs[job_id] = {
            "job_id": job_id,
            "user_id": str(user_id),
            "status": "running",
            "created_at": now,
            "finished_at": None,
            "reply": None,
            "error": None,
            # reasoning ("thinking") trace: one segment per agent-loop
            # iteration; reasoning_open marks a segment still receiving text
            "reasoning_segments": [],
            "reasoning_open": False,
        }
        return job_id

    def get(self, job_id: str) -> dict[str, Any] | None:
        """Return a snapshot of the job, or None if unknown/expired."""
        self.sweep()
        job = self._jobs.get(job_id)
        return dict(job) if job is not None else None

    def finish(self, job_id: str, reply: str) -> None:
        job = self._jobs.get(job_id)
        # A stopped job stays stopped: a reply racing in must not revive it.
        if job is not None and job["status"] == "running":
            job["status"] = "done"
            job["reply"] = reply
            job["finished_at"] = time.time()

    def fail(self, job_id: str, error: str) -> None:
        job = self._jobs.get(job_id)
        # Same as finish(): a terminal state is never overwritten.
        if job is not None and job["status"] == "running":
            job["status"] = "error"
            job["error"] = str(error)[:500]
            job["finished_at"] = time.time()

    def mark_stopped(self, job_id: str) -> bool:
        """Freeze a running job as stopped. True if it transitioned.

        The job keeps its reasoning trace but never reaches "done", so a
        reply that races in after the stop is dropped.
        """
        job = self._jobs.get(job_id)
        if job is None or job["status"] != "running":
            return False
        job["status"] = "stopped"
        job["finished_at"] = time.time()
        job["reasoning_open"] = False
        return True

    # -- reasoning ("thinking") trace ----------------------------------------

    def append_reasoning(self, job_id: str, delta: str) -> None:
        """Append a reasoning chunk to the job's live (open) segment.

        Each agent-loop iteration gets its own segment: a new segment
        starts when none is open (first chunk, or after
        end_reasoning_segment). Oversized segments keep only their tail.
        """
        job = self._jobs.get(job_id)  # live dict, not the get() snapshot
        if job is None or not delta:
            return
        segments = job["reasoning_segments"]
        if not job["reasoning_open"] or not segments:
            segments.append("")
            job["reasoning_open"] = True
        seg = segments[-1] + str(delta)
        if len(seg) > MAX_REASONING_CHARS:
            seg = "…" + seg[-MAX_REASONING_CHARS:]
        segments[-1] = seg

    def end_reasoning_segment(self, job_id: str) -> None:
        """Close the live reasoning segment; the next chunk opens a new one."""
        job = self._jobs.get(job_id)
        if job is not None:
            job["reasoning_open"] = False

    def active_count_for_user(self, user_id: str) -> int:
        user_id = str(user_id)
        return sum(
            1
            for j in self._jobs.values()
            if j["user_id"] == user_id and j["status"] == "running"
        )

    def sweep(self) -> None:
        """Drop jobs older than the TTL (measured from creation)."""
        cutoff = time.time() - self.ttl_seconds
        stale = [jid for jid, j in self._jobs.items() if j["created_at"] < cutoff]
        for jid in stale:
            del self._jobs[jid]

    def clear(self) -> None:
        self._jobs.clear()


def job_status_payload(job: dict[str, Any] | None) -> dict[str, Any]:
    """Build the GET response body for a job snapshot (or None)."""
    if job is None:
        return {"status": "error", "reason": "expired"}
    now = time.time()
    elapsed = int((job["finished_at"] or now) - job["created_at"])
    out: dict[str, Any] = {
        "job_id": job["job_id"],
        "status": job["status"],
        "elapsed_s": max(0, elapsed),
    }
    segments = job.get("reasoning_segments") or []
    if segments:
        out["reasoning"] = segments[-1]
        out["reasoning_count"] = len(segments)
        if len(segments) > 1:
            out["reasoning_prev"] = "\n\n".join(segments[:-1])
    if job["status"] == "done":
        out["reply"] = job["reply"]
    if job["status"] == "error":
        out["reason"] = "agent_error"
        out["error"] = job["error"]
    if job["status"] == "stopped":
        out["reason"] = "stopped"
    return out
