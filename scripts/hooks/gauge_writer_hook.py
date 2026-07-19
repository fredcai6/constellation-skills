#!/usr/bin/env python3
"""gauge_writer_hook.py -- Claude Code PostToolUse hook: Context Governor gauge
WRITER (Module 2, write side; issue #180).

On every tool call, senses context fill from the session transcript and
atomically writes `.agent-work/<work_id>/gauge.json` for the engine-side
reader (#181) to consume. See docs/GAUGE_WRITER_HOOK.md for the wiring,
the exact transcript shape this depends on, and what breaks it.

Design contract (frozen DESIGN_SPEC #178, Module 2 post-review amendments):

- Fail-open. Any error anywhere is swallowed; the hook never blocks or
  fails the tool call it's attached to. Every handler is wrapped.
- Skip-on-uncertainty, NEVER fabricate. If fill can't be computed
  confidently (missing transcript, no usable usage record, missing
  timestamp, unresolvable work_id), write NOTHING -- the existing gauge
  file is left exactly as it was and ages into staleness naturally. A
  fabricated 0.0 would read as genuine low fill and could suppress a
  nudge that should have fired.
- Record is FROZEN, four fields only (identical to #181's reader):
  {schema_version: int, fill_fraction: float 0..1, model: str,
  observed_at: ISO-8601 str -- the SAMPLED moment, not write time}.
- Atomic write: tmp file + os.replace. A concurrent reader of gauge.json
  never observes a torn/partial record -- it always sees either the
  complete prior record or the complete new one.
- Session->spine binding is REUSED, not re-derived: `spine_rail.py`
  (this hook's sibling in the same PostToolUse rail) already maintains
  `.agent-work/.spine-rail-binding.json` mapping session_id -> spine
  path. `<work_id>` is that spine path's parent directory. If no binding
  exists for this session (e.g. no `checklist_engine.py claim` has run
  yet), the work_id is unresolvable and the hook skips -- this is a
  documented coupling, not a new mechanism (see docs/GAUGE_WRITER_HOOK.md).
- The X2 "strategic-compact" technique: the transcript is JSONL; each
  top-level (non-sidechain) assistant message carries a `usage` block.
  Because Claude Code resends the full conversation on every turn, the
  LATEST such record's `input_tokens + cache_creation_input_tokens +
  cache_read_input_tokens` IS the current total context size (not a sum
  across lines/turns). Sidechain entries (subagent turns, `isSidechain:
  true`) are a different context window entirely and are skipped.
- Stdlib only. Windows-friendly: UTF-8 I/O, native paths, no /tmp literals.
"""

import importlib.util
import json
import os
import sys
from pathlib import Path

SCHEMA_VERSION = 1

# Context-window token capacity per model (standard tier). Calibration TBD:
# every model shipped today shares 200k; kept as a table (not one constant)
# because #181's gauge_reader already keys SOFT/HARD thresholds per model,
# and a future model with a different window only needs a new row here.
MODEL_WINDOWS = {
    "claude-opus-4-8": 200_000,
    "claude-sonnet-5": 200_000,
    "claude-haiku-4-5-20251001": 200_000,
    "claude-fable-5": 200_000,
}
DEFAULT_WINDOW = 200_000  # unknown model -> standard-tier default, not a guess of 0

# Bounded reverse-scan window (bytes) -- see docs/GAUGE_WRITER_HOOK.md. Real
# transcripts run into the tens of MB; a full forward parse every tool call
# would be wasteful. The latest usage record is always near the tail, so
# reading the last TAIL_BYTES and scanning backward is enough in practice.
# If nothing usable is found in that window, skip-on-uncertainty applies --
# this is a deliberate bounded-cost choice, not a silent truncation bug.
TAIL_BYTES = 2_000_000


# --- reuse the hook rail's session->spine binding (never re-derive) --------

def _load_spine_rail():
    """Load scripts/hooks/spine_rail.py by file path -- robust regardless of
    whether this module is run as a script or imported by a test (mirrors
    tests/test_spine_rail.py's own loading technique). Returns None if the
    sibling module is missing or fails to load; callers then skip (the
    binding becomes unresolvable, which is itself a valid skip-on-uncertainty
    outcome -- see docs/GAUGE_WRITER_HOOK.md)."""
    try:
        path = Path(__file__).resolve().parent / "spine_rail.py"
        spec = importlib.util.spec_from_file_location("spine_rail", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


_spine_rail = _load_spine_rail()


def resolve_gauge_path(project_dir: Path, session_id):
    """.agent-work/<work_id>/gauge.json, sibling to spine.json, resolved via
    the existing session->spine binding. None if unresolvable (no sibling
    module, no session_id, no binding entry, no spine path recorded)."""
    try:
        if _spine_rail is None or not session_id:
            return None
        binding = _spine_rail.load_binding(project_dir)
        entry = binding.get(session_id)
        if not entry or not entry.get("spine"):
            return None
        return Path(entry["spine"]).parent / "gauge.json"
    except Exception:
        return None


# --- X2 strategic-compact: parse transcript, sum latest usage record -------

def _iter_tail_lines_reverse(path, max_bytes=TAIL_BYTES):
    """Yield non-blank lines from the tail of `path`, most-recent-first,
    reading at most max_bytes from the end. Never raises."""
    size = os.path.getsize(path)
    read_size = min(size, max_bytes)
    with open(path, "rb") as f:
        f.seek(size - read_size)
        data = f.read(read_size)
    text = data.decode("utf-8", errors="ignore")
    lines = text.split("\n")
    if size > read_size:
        # the first fragment is a partial line (we seeked mid-file) -- drop it
        lines = lines[1:]
    for line in reversed(lines):
        line = line.strip()
        if line:
            yield line


def find_latest_usage(transcript_path):
    """Scan the transcript tail for the most recent main-chain (non-sidechain)
    assistant message carrying a usage record. Returns (model, total_tokens,
    observed_at), or None if nothing usable is found in the scanned window."""
    try:
        for line in _iter_tail_lines_reverse(transcript_path):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("type") != "assistant" or d.get("isSidechain"):
                continue
            msg = d.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            model = msg.get("model")
            observed_at = d.get("timestamp")
            if not model or not observed_at:
                continue
            total = 0
            ok = True
            for field in (
                "input_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            ):
                v = usage.get(field)
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    ok = False
                    break
                total += v
            if not ok:
                continue
            return model, total, observed_at
        return None
    except Exception:
        return None


def compute_record(transcript_path):
    """Build the frozen 4-field record, or None if fill can't be computed
    confidently. None here means "write nothing" -- never a placeholder."""
    try:
        found = find_latest_usage(transcript_path)
        if found is None:
            return None
        model, total_tokens, observed_at = found
        window = MODEL_WINDOWS.get(model, DEFAULT_WINDOW)
        if not window or window <= 0:
            return None
        fill = max(0.0, min(1.0, total_tokens / window))
        return {
            "schema_version": SCHEMA_VERSION,
            "fill_fraction": fill,
            "model": model,
            "observed_at": observed_at,
        }
    except Exception:
        return None


# --- atomic write ------------------------------------------------------------

def _atomic_write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f)
    os.replace(tmp, path)  # atomic on POSIX and Windows alike


# --- PostToolUse handler ------------------------------------------------------

def handle_post_tool_use(data: dict, project_dir: Path) -> dict:
    """Compute + atomically write the gauge record. NEVER raises; NEVER
    blocks; NEVER writes on uncertainty. Always returns {} (this hook never
    influences the tool call)."""
    try:
        transcript_path = data.get("transcript_path")
        if not transcript_path or not os.path.isfile(transcript_path):
            return {}
        gauge_path = resolve_gauge_path(project_dir, data.get("session_id"))
        if gauge_path is None:
            return {}
        record = compute_record(transcript_path)
        if record is None:
            return {}
        _atomic_write_json(gauge_path, record)
        return {}
    except Exception:
        return {}


# --- dispatch ----------------------------------------------------------------

def main(argv, stdin_text) -> int:
    """Single-purpose hook (PostToolUse only) -- no event-name dispatch is
    needed; the settings.json wiring registers this script for PostToolUse
    specifically (see docs/GAUGE_WRITER_HOOK.md). Always exits 0."""
    try:
        try:
            data = json.loads(stdin_text) if stdin_text and stdin_text.strip() else {}
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        project_dir = (
            _spine_rail.resolve_project_dir()
            if _spine_rail is not None
            else Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        )
        handle_post_tool_use(data, project_dir)
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    try:
        _stdin = sys.stdin.read()
    except Exception:
        _stdin = ""
    sys.exit(main(sys.argv, _stdin))
