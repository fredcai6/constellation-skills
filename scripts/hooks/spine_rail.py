#!/usr/bin/env python3
"""spine_rail.py -- Claude Code hook suite for the Constellation spine rail.

One script, dispatched by event name (argv[1]): Stop, SessionStart, PostToolUse.
It is a deterrent that refuses dishonest turn-ends mid-spine and re-injects
resume doctrine after compaction, judging the ENGINE'S OWN TRUTH -- the spine
state file plus its journal sidecar -- and NEVER the agent's prose.

Design contract (frozen DESIGN_SPEC #138 channel B, D3):

- Fail-open. Any error anywhere prints nothing and exits 0. A hook must never
  crash or hang a turn. Every handler is wrapped and returns {} on trouble.
- State-file facts ONLY. Decisions read the spine JSON (json.load) and count the
  journal lines. The agent's words (last_assistant_message, etc.) are never
  parsed for a decision.
- Read the spine STATE FILE directly; do NOT subprocess the engine. This is a
  deliberate, spec-accepted LOCALITY COST: this module re-encodes the engine's
  TERMINAL statuses (a second place that knows "what is terminal") in exchange
  for robustness in headless/subagent contexts and clean unit-testability.
- Discovery is the PostToolUse hook's ONLY job: it watches Bash commands for the
  engine's claim/release verbs and maintains a session->spine binding. It is NOT
  a second source of mid-flight truth -- Stop always reads the spine file the
  binding points at.
- Three registrations only (Stop, SessionStart, PostToolUse). No PreCompact.
- 3-strike escape hatch so a genuinely stuck agent is never trapped.

Stdlib only (json, os, sys, shlex, pathlib). Windows-friendly: UTF-8 writes,
native paths, no /tmp literals.
"""

import json
import os
import shlex
import sys
from pathlib import Path

# The engine's terminal statuses, re-encoded here on purpose (see docstring).
TERMINAL = {"complete", "skipped"}

# --- stable marker substrings (asserted by tests; hook contract) -------------

STUCK_MSG = (
    "SPINE-RAIL: released turn-end after 3 no-progress nudges. The rail is "
    "standing down for this turn so a genuinely stuck run is not trapped. If a "
    "gate is still open, block the gate through the engine so the blocker "
    "bubbles to the parent, then investigate -- do not silently abandon it."
)


# --- project dir + scratch file locations ------------------------------------

def resolve_project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def _agent_work(project_dir: Path) -> Path:
    return project_dir / ".agent-work"


def binding_path(project_dir: Path) -> Path:
    return _agent_work(project_dir) / ".spine-rail-binding.json"


def nudge_path(project_dir: Path) -> Path:
    return _agent_work(project_dir) / ".spine-rail-nudges.json"


def _load_json_map(path: Path) -> dict:
    """Load a JSON object map; return {} on absent/corrupt/non-object."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_json_map(path: Path, data: dict) -> None:
    """Atomically write a JSON object map. Never raises."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass


def load_binding(project_dir: Path) -> dict:
    return _load_json_map(binding_path(project_dir))


def save_binding(project_dir: Path, data: dict) -> None:
    _save_json_map(binding_path(project_dir), data)


def load_nudges(project_dir: Path) -> dict:
    return _load_json_map(nudge_path(project_dir))


def save_nudges(project_dir: Path, data: dict) -> None:
    _save_json_map(nudge_path(project_dir), data)


# --- pure state-file readers -------------------------------------------------

def load_spine(spine_path) -> dict | None:
    """json.load the spine state file. Return None on any failure."""
    try:
        with open(spine_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def active_id(spine: dict):
    """First item id whose task status is NOT terminal; None if all terminal."""
    try:
        items = spine.get("items") or []
        tasks = spine.get("tasks") or {}
        for iid in items:
            task = tasks.get(iid) or {}
            if task.get("status") not in TERMINAL:
                return iid
        return None
    except Exception:
        return None


def journal_seq(spine_path) -> int:
    """Progress signal: count of non-blank lines in <spine_path>.journal.

    0 if the journal is absent or unreadable. NEVER raises.
    """
    try:
        jpath = str(spine_path) + ".journal"
        count = 0
        with open(jpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    except Exception:
        return 0


def reconstruct_current(spine: dict) -> str:
    """Rebuild the engine's `current` output from the state file (no subprocess).

    Optional `LEASE active: ...` line, then `ACTIVE <aid> [<status>] -- <imp>`
    or `DONE: no open items.` when every item is terminal.
    """
    lines = []
    lease = spine.get("engine_session") or {}
    if lease.get("status") == "active":
        lines.append(
            "LEASE active: {sid} (by {by}, heartbeat {hb})".format(
                sid=lease.get("session_id"),
                by=lease.get("claimed_by"),
                hb=lease.get("last_heartbeat"),
            )
        )
    aid = active_id(spine)
    if aid is None:
        lines.append("DONE: no open items.")
    else:
        task = (spine.get("tasks") or {}).get(aid) or {}
        lines.append(
            "ACTIVE {aid} [{status}] -- {imp}".format(
                aid=aid,
                status=task.get("status"),
                imp=task.get("imperative"),
            )
        )
    return "\n".join(lines)


# --- PostToolUse: command-token parsing --------------------------------------

def _tokenize(command: str) -> list:
    try:
        return shlex.split(command)
    except Exception:
        return command.split()


def _extract_verb(tokens: list):
    """Positional verb after the engine script token, skipping the global
    --file <path> option. Returns None if not found."""
    idx = None
    for i, tok in enumerate(tokens):
        if "checklist_engine.py" in tok:
            idx = i
            break
    if idx is None:
        return None
    i = idx + 1
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--file":
            i += 2
            continue
        if tok.startswith("--file="):
            i += 1
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok
    return None


def _extract_opt(tokens: list, name: str):
    """Value of `--name value` or `--name=value`; None if absent."""
    prefix = name + "="
    for i, tok in enumerate(tokens):
        if tok == name:
            return tokens[i + 1] if i + 1 < len(tokens) else None
        if tok.startswith(prefix):
            return tok[len(prefix):]
    return None


def _resolve_abs(file_val: str, cwd, project_dir: Path) -> str:
    try:
        p = Path(file_val)
        if p.is_absolute():
            return str(p)
        base = Path(cwd) if cwd else project_dir
        return str((base / p).resolve())
    except Exception:
        return file_val


def handle_post_tool_use(data: dict, project_dir: Path) -> dict:
    """Maintain the session->spine binding from engine claim/release commands.

    PostToolUse NEVER blocks -- always returns {}.
    """
    try:
        command = ((data.get("tool_input") or {}).get("command")) or ""
        if not command:
            return {}
        tokens = _tokenize(command)
        if not any("checklist_engine.py" in tok for tok in tokens):
            return {}
        verb = _extract_verb(tokens)
        if verb not in ("claim", "release"):
            return {}
        sid = data.get("session_id")
        if not sid:
            return {}
        binding = load_binding(project_dir)
        if verb == "claim":
            file_val = _extract_opt(tokens, "--file")
            engine_session = _extract_opt(tokens, "--session-id")
            cwd = data.get("cwd") or str(project_dir)
            abs_spine = _resolve_abs(file_val, cwd, project_dir) if file_val else None
            binding[sid] = {
                "spine": abs_spine,
                "engine_session": engine_session,
                "worktree": cwd,
            }
            save_binding(project_dir, binding)
        else:  # release
            if sid in binding:
                del binding[sid]
                save_binding(project_dir, binding)
            nudges = load_nudges(project_dir)
            if sid in nudges:
                del nudges[sid]
                save_nudges(project_dir, nudges)
        return {}
    except Exception:
        return {}


# --- Stop: refuse dishonest mid-spine turn-ends ------------------------------

def _mid_flight_reason(spine: dict, aid) -> str:
    if aid is None:
        return (
            "SPINE MID-FLIGHT: every item is terminal but the engine lease is "
            "still ACTIVE -- the run is not closed until the lease is released. "
            "Run the engine's release verb to close the lease before ending "
            "your turn; do not end your turn to wait with an open lease."
        )
    imperative = ((spine.get("tasks") or {}).get(aid) or {}).get("imperative") or ""
    return (
        "SPINE MID-FLIGHT: gate {aid} is still open -- you are in the MIDDLE of "
        "the spine, not at its end, so ending your turn now abandons an active "
        "run. Keep working the gate -- do not end your turn to wait. "
        "Next imperative: {imp} "
        "If this is an honest stop (genuinely blocked or out of scope), use the "
        "engine's block verb to bubble the blocker to the parent, or waive the "
        "check with human authority -- do not just stop."
    ).format(aid=aid, imp=imperative)


def decide_stop(data: dict, project_dir: Path) -> dict:
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        b = binding.get(sid)
        if not b:
            return {}  # no binding -> allow
        spine_path = b.get("spine")
        if not spine_path:
            return {}
        spine = load_spine(spine_path)
        if spine is None:
            return {}  # unreadable -> allow
        lease = spine.get("engine_session") or {}
        if lease.get("status") != "active":
            return {}  # run closed -> allow
        aid = active_id(spine)
        tasks = spine.get("tasks") or {}
        if aid is not None and (tasks.get(aid) or {}).get("status") == "blocked":
            return {}  # honest engine block -> allow

        # Mid-flight: aid non-blocked, OR aid is None while lease still active.
        seq = journal_seq(spine_path)
        nudges = load_nudges(project_dir)
        prior = nudges.get(sid) or {"count": 0, "journal_seq": -1, "active_id": None}
        progress = (seq != prior.get("journal_seq")) or (aid != prior.get("active_id"))
        count = (0 if progress else prior.get("count", 0)) + 1
        nudges[sid] = {"count": count, "journal_seq": seq, "active_id": aid}
        save_nudges(project_dir, nudges)

        if count >= 3:
            # Escape hatch: allow the stop, but leave a loud marker.
            return {"continue": True, "systemMessage": STUCK_MSG}

        reason = _mid_flight_reason(spine, aid)
        ctx = "ENGINE current -> " + reconstruct_current(spine)
        return {
            "decision": "block",
            "reason": reason,
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": ctx,
            },
        }
    except Exception:
        return {}


# --- SessionStart: re-inject resume doctrine after compaction ----------------

def _scan_active_spine(project_dir: Path):
    """Best-effort fallback: first .agent-work/*/spine.json with an active
    lease and a non-None active id. (session->spine binding is preferred.)"""
    try:
        base = _agent_work(project_dir)
        for spath in base.glob("*/spine.json"):
            spine = load_spine(str(spath))
            if not isinstance(spine, dict):
                continue
            lease = spine.get("engine_session") or {}
            if lease.get("status") == "active" and active_id(spine) is not None:
                return spine
        return None
    except Exception:
        return None


def decide_session_start(data: dict, project_dir: Path) -> dict:
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        b = binding.get(sid) if sid else None
        spine = None
        if b and b.get("spine"):
            spine = load_spine(b.get("spine"))
        if spine is None:
            spine = _scan_active_spine(project_dir)  # best-effort fallback
        if spine is None:
            return {}
        lease = spine.get("engine_session") or {}
        if lease.get("status") != "active":
            return {}
        if active_id(spine) is None:
            return {}
        resume_ctx = (
            "RESUMING an active Constellation spine run after a restart or "
            "compaction. ENGINE current -> " + reconstruct_current(spine) + " "
            "Pick the run back up at this gate and drive it through the engine. "
            "Remember release-is-last: the run is not done until you release the "
            "engine lease."
        )
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": resume_ctx,
            },
        }
    except Exception:
        return {}


# --- dispatch ----------------------------------------------------------------

def main(argv, stdin_text) -> int:
    """Dispatch by event name (argv[1]); print result JSON only if non-empty;
    always exit 0. Wrapped: any exception -> print nothing, exit 0 (fail-open)."""
    try:
        event = argv[1] if len(argv) > 1 else ""
        try:
            data = json.loads(stdin_text) if stdin_text and stdin_text.strip() else {}
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        project_dir = resolve_project_dir()
        if event == "Stop":
            result = decide_stop(data, project_dir)
        elif event == "SessionStart":
            result = decide_session_start(data, project_dir)
        elif event == "PostToolUse":
            result = handle_post_tool_use(data, project_dir)
        else:
            result = {}
        if result:
            print(json.dumps(result))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    try:
        _stdin = sys.stdin.read()
    except Exception:
        _stdin = ""
    sys.exit(main(sys.argv, _stdin))
