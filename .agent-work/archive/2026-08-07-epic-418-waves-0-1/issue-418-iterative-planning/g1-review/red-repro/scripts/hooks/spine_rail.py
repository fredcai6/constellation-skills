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
from datetime import datetime, timezone
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


def _is_old_shape_binding_entry(entry: dict) -> bool:
    """True if `entry` looks like the OLD flat per-session binding value
    (`{spine, engine_session, worktree}`) rather than the NEW nested
    `{abs_spine_path: {spine, engine_session, worktree, claimed_at}}` map.

    A `"spine"` key present DIRECTLY on `entry` is the old shape's signature --
    the new shape's values are themselves dicts keyed by abs_spine_path, never
    a literal `"spine"` key at this level.
    """
    return "spine" in entry


def load_binding(project_dir: Path) -> dict:
    """Load `session_id -> {abs_spine_path: {spine, engine_session, worktree,
    claimed_at}}`.

    An old-shape (flat, pre-#202) entry under a session_id is treated as
    ABSENT for that session_id -- fail-open, never a crash and never a silent
    misinterpretation as a new-shape entry (decision:binding-schema-may-change).
    No in-place migration: the file self-heals as sessions re-claim under the
    new writer.
    """
    raw = _load_json_map(binding_path(project_dir))
    try:
        return {
            sid: entry
            for sid, entry in raw.items()
            if isinstance(entry, dict) and not _is_old_shape_binding_entry(entry)
        }
    except Exception:
        return {}


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


# --- worktree attribution (subagent session-sharing guard) -------------------

def _same_path(a, b) -> bool:
    """True if a and b name the same path after normcase+normpath.

    Fail-SAFE: on ANY exception return True. A comparison failure must never
    spuriously relax the rail into treating a driving session as foreign.
    """
    try:
        if not isinstance(a, str) or not isinstance(b, str):
            return True  # un-comparable input -> fail safe, do not relax
        na = os.path.normcase(os.path.normpath(a))
        nb = os.path.normcase(os.path.normpath(b))
        return na == nb
    except Exception:
        return True


def _foreign_worktree(data: dict, b: dict) -> bool:
    """True only when the stopping session's cwd is positively a DIFFERENT
    worktree than the binding's recorded worktree.

    Returns True iff both `data["cwd"]` and `b["worktree"]` are truthy AND
    `_same_path` says they differ. Absent either -> False: no positive mismatch
    evidence, so the rail does not relax (and `_same_path`'s fail-safe True keeps
    an errored comparison from reading as foreign).
    """
    try:
        cwd = data.get("cwd")
        worktree = b.get("worktree")
        if not cwd or not worktree:
            return False
        return not _same_path(cwd, worktree)
    except Exception:
        return False


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def handle_post_tool_use(data: dict, project_dir: Path) -> dict:
    """Maintain the session->spine binding from engine claim/release commands.

    One session_id can hold a binding into more than one distinct spine at
    once (#202) -- the binding is keyed by the RESOLVED ABSOLUTE SPINE PATH
    itself (`abs_spine`), not by worktree or cwd
    (decision:key-binding-by-spine-path-not-worktree-or-cwd). A claim writes
    only `binding[sid][abs_spine]`, leaving any other abs_spine_path entries
    for that sid untouched; a release removes only that one entry.

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
        file_val = _extract_opt(tokens, "--file")
        cwd = data.get("cwd") or str(project_dir)
        abs_spine = _resolve_abs(file_val, cwd, project_dir) if file_val else None
        if not abs_spine:
            return {}  # nothing to key the entry by -- fail-open, no write
        binding = load_binding(project_dir)
        if verb == "claim":
            engine_session = _extract_opt(tokens, "--session-id")
            sid_bindings = dict(binding.get(sid) or {})
            sid_bindings[abs_spine] = {
                "spine": abs_spine,
                "engine_session": engine_session,
                "worktree": cwd,
                "claimed_at": _now_iso(),
            }
            binding[sid] = sid_bindings
            save_binding(project_dir, binding)
        else:  # release
            sid_bindings = binding.get(sid)
            if sid_bindings and abs_spine in sid_bindings:
                sid_bindings = dict(sid_bindings)
                del sid_bindings[abs_spine]
                if sid_bindings:
                    binding[sid] = sid_bindings
                else:
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


def _entry_mid_flight_view(data: dict, entry: dict):
    """Per-entry mid-flight check, unchanged in substance from the pre-#202
    single-entry logic -- just factored so decide_stop can apply it to every
    bound abs_spine_path entry for a session_id, not just one.

    Returns None if this entry is NOT a genuine mid-flight blocker (foreign
    worktree, unreadable spine, released/inactive lease, or an honest engine
    block); else `(spine_path, spine_dict, aid)`.
    """
    spine_path = entry.get("spine")
    if not spine_path:
        return None
    if _foreign_worktree(data, entry):
        return None  # stopping session is not THIS entry's driver (subagent
        # sharing the parent's session_id claimed a spine in its own worktree)
    spine = load_spine(spine_path)
    if spine is None:
        return None  # unreadable -> allow
    lease = spine.get("engine_session") or {}
    if lease.get("status") != "active":
        return None  # run closed -> allow
    aid = active_id(spine)
    tasks = spine.get("tasks") or {}
    if aid is not None and (tasks.get(aid) or {}).get("status") == "blocked":
        return None  # honest engine block -> allow
    return spine_path, spine, aid


def decide_stop(data: dict, project_dir: Path) -> dict:
    """Block the Stop if ANY non-foreign bound entry for this session_id is
    genuinely mid-flight (same per-entry semantics as the pre-#202 single-
    entry version, just applied across every abs_spine_path entry now bound
    under `sid`). The nudge-tracking / 3-strike escape hatch stays keyed by
    `sid` ALONE -- never fragmented per-entry, which would weaken the escape
    hatch.
    """
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        sid_bindings = binding.get(sid) or {}
        if not sid_bindings:
            return {}  # no binding -> allow

        mid_flight = []
        for entry in sid_bindings.values():
            view = _entry_mid_flight_view(data, entry)
            if view is not None:
                mid_flight.append(view)

        if not mid_flight:
            return {}  # every bound entry is foreign/unreadable/closed/honest-blocked -> allow

        # Mid-flight: aggregate a single progress signal across every
        # mid-flight entry (never fragment nudges[sid] per-entry).
        seq = sum(journal_seq(spine_path) for spine_path, _, _ in mid_flight)
        active_ids = sorted(
            "{}::{}".format(spine_path, aid) for spine_path, _, aid in mid_flight
        )
        nudges = load_nudges(project_dir)
        prior = nudges.get(sid) or {"count": 0, "journal_seq": -1, "active_id": None}
        progress = (seq != prior.get("journal_seq")) or (active_ids != prior.get("active_id"))
        count = (0 if progress else prior.get("count", 0)) + 1
        nudges[sid] = {"count": count, "journal_seq": seq, "active_id": active_ids}
        save_nudges(project_dir, nudges)

        if count >= 3:
            # Escape hatch: allow the stop, but leave a loud marker.
            return {"continue": True, "systemMessage": STUCK_MSG}

        _, spine, aid = mid_flight[0]
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
    """Best-effort fallback: EVERY .agent-work/*/spine.json with an active
    lease and a non-None active id, as a list of `(spine_dict, spine_path)`
    tuples in glob order (session->spine binding is preferred; this is the
    last-resort discovery path). Empty list if none found.

    Returning every match (not just the first) is deliberate: the caller
    needs a COUNT to tell an unambiguous single active spine from an
    ambiguous multi-spine scan (#261 bind-on-resume), while still wanting
    the same "first match" spine for the advisory-context injection it did
    before this match ever mattered. One glob pass serves both."""
    try:
        base = _agent_work(project_dir)
        matches = []
        for spath in base.glob("*/spine.json"):
            spine = load_spine(str(spath))
            if not isinstance(spine, dict):
                continue
            lease = spine.get("engine_session") or {}
            if lease.get("status") == "active" and active_id(spine) is not None:
                matches.append((spine, str(spath)))
        return matches
    except Exception:
        return []


def decide_session_start(data: dict, project_dir: Path) -> dict:
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        sid_bindings = (binding.get(sid) or {}) if sid else {}
        # Per-entry iteration mirroring decide_stop's already-generalized
        # pattern (#202/#261): `sid_bindings` is a dict of abs_spine_path ->
        # entry (never a flat {spine, ...} directly). Take the FIRST entry
        # (natural dict.values() order) that has a spine and is not foreign
        # -- same "first match" tone as _scan_active_spine below.
        spine = None
        for entry in sid_bindings.values():
            if entry.get("spine") and not _foreign_worktree(data, entry):
                spine = load_spine(entry.get("spine"))
                break
        if spine is None:
            matches = _scan_active_spine(project_dir)  # best-effort fallback
            if matches:
                spine = matches[0][0]  # first match, same tone as before
            if len(matches) == 1 and sid:
                # Unambiguous (decision:no-bind-on-ambiguous-scan): exactly
                # one active-leased spine on disk and no positional-count
                # confusion about which one it is -- bind this session to it,
                # same shape g1's claim writer uses, so a resumed/compacted
                # session that never itself ran `claim` still gets a binding
                # (#261) and gauge_writer_hook.resolve_gauge_path stops
                # returning empty for it. Zero or 2+ matches: inject context
                # (below) but write NO binding -- ambiguity is not ours to
                # silently resolve.
                own_spine, own_spine_path = matches[0]
                lease_for_bind = own_spine.get("engine_session") or {}
                sid_bindings2 = dict(binding.get(sid) or {})
                sid_bindings2[own_spine_path] = {
                    "spine": own_spine_path,
                    "engine_session": lease_for_bind.get("session_id"),
                    "worktree": data.get("cwd") or str(project_dir),
                    "claimed_at": _now_iso(),
                }
                binding[sid] = sid_bindings2
                save_binding(project_dir, binding)
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
