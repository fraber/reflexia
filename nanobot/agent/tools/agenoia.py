"""Agenoia Memory writer tool for Dream runs.

Shells out to the standalone Agenoia writer (``/home/nanobot/bench/agenoia_writer.py``)
in ``--source history --incremental`` mode, admitting new ``memory/history.jsonl``
entries as ``ag_memory_items`` + evidence rows on the po52dev ]po[ database.

The writer keeps its own cursor (``memory/.agenoia-state.json``) independent of
Dream's ``.dream-cursor``, so it can run as a parallel consumer of the same
history stream without interfering with MEMORY.md consolidation.

Write-only by design: the query/retrieval part of Agenoia Memory is NOT wired
here (retrieval goes through the projop skill / REST).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool

logger = logging.getLogger(__name__)

_DEFAULT_SCRIPT = "/home/nanobot/bench/agenoia_writer.py"
_DEFAULT_MODEL = "z-ai/glm-5.3-flash"
_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
_CONFIG_PATH = os.environ.get("NANOBOT_CONFIG_PATH", "/home/nanobot/.nanobot/config.json")
_OUTPUT_TAIL_CHARS = 4_000  # keep the tail of writer output (summary lines live at the end)


def _resolve_api_key() -> str:
    """API key for the writer's extraction stage: env first, then nanobot config.json."""
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key:
        return key
    try:
        cfg = json.loads(Path(_CONFIG_PATH).read_text(encoding="utf-8"))
        return ((cfg.get("providers", {}) or {}).get("openrouter", {}) or {}).get("apiKey") or ""
    except Exception:  # noqa: BLE001 - config may be absent/malformed; writer degrades to heuristic
        return ""


class AgenoiaWriteTool(Tool):
    """Admit new history facts into Agenoia Memory (po52dev) during Dream runs."""

    # Not auto-discovered for the main agent loop: this tool is registered
    # explicitly inside Dream's restricted Phase-2 tool registry only.
    _plugin_discoverable = False

    @property
    def name(self) -> str:
        return "agenoia_write"

    @property
    def description(self) -> str:
        return (
            "Incrementally admit new conversation-history facts into Agenoia Memory "
            "(po52dev PostgreSQL). Runs the standalone writer over the workspace "
            "memory/history.jsonl using its own cursor. Call it ONCE, near the end of "
            "the Dream run, after all memory-file edits are done. Returns the writer's "
            "stage summary."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "Preview only: run stages up to admission decision without "
                        "writing anything to the database (default false)."
                    ),
                },
            },
            "required": [],
        }

    def __init__(
        self,
        script_path: str = _DEFAULT_SCRIPT,
        workspace: Path | None = None,
        model: str | None = None,
        max_statements: int = 0,
        timeout: int = 900,
    ):
        self.script_path = script_path
        self.workspace = workspace
        self.model = model or os.environ.get("AGENOIA_MODEL", _DEFAULT_MODEL)
        self.max_statements = max_statements  # 0 = unlimited admission budget
        self.timeout = timeout

    def _build_cmd(self, dry_run: bool) -> list[str]:
        history = Path(self.workspace) / "memory" / "history.jsonl" if self.workspace else None
        if history is None or not history.exists():
            raise FileNotFoundError(f"history.jsonl not found: {history}")
        cmd = [
            "python3",
            self.script_path,
            "--source", "history",
            str(history),
            "--workspace", str(self.workspace),
            "--incremental",
            "--api-base", _OPENROUTER_BASE,
            "--api-key", _resolve_api_key(),
            "--model", self.model,
        ]
        if self.max_statements:
            cmd += ["--max-statements", str(self.max_statements)]
        if dry_run:
            cmd.append("--dry-run")
        return cmd

    async def execute(self, dry_run: bool = False, **_: Any) -> str:
        cmd = self._build_cmd(dry_run)
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
        except asyncio.TimeoutError:
            return f"agenoia_write timed out after {self.timeout}s (no partial writes reported)."
        except FileNotFoundError as e:
            return f"agenoia_write failed to start: {e}"
        text = out.decode("utf-8", errors="replace")
        if len(text) > _OUTPUT_TAIL_CHARS:
            text = "…\n" + text[-_OUTPUT_TAIL_CHARS:]
        return f"exit_code={proc.returncode}\n{text}"
