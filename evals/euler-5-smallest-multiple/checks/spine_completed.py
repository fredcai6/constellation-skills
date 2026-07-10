#!/usr/bin/env python
"""PROCESS check (gating): a constellation ENGINE spine reached a terminal state
WITH engine-written provenance -- not merely agent-written JSON (issue #127).

The old check trusted plain JSON state: a spine whose tasks were all marked
``complete`` passed, no matter WHO wrote that state. A cheap headless model that
never invoked the engine could HAND-WRITE a spine.json with every step
``complete`` and fabricated evidence notes and sail through -- fabrication was one
forgotten field from passing (epic-101 live-acceptance attempt 6). This check now
demands the fingerprints the engine ALWAYS leaves and a template-copying
fabricator does NOT get for free:

  1. Terminal gated shape: a ``tasks`` map with EVERY task ``complete``. The bare
     ``{"status": "done"}`` form no longer passes on its own -- it carries zero
     provenance and is exactly the cheapest thing a fabricator writes. (The
     runner's ``--dry-run`` now synthesizes a real engine-shaped spine, so its
     self-smoke still bites strictly.)
  2. A plausible ``engine_session`` lease block. The shipped spine TEMPLATE has no
     ``engine_session`` key at all -- only the engine's ``claim`` verb writes one,
     with all of session_id / status / claimed_at / last_heartbeat / claimed_by /
     worktree / previous_session_id / takeover_reason. The claim/heartbeat/release
     timestamps must parse as ISO-8601 and be MONOTONIC (claimed <= heartbeat <=
     released). A fabricator must now forge a whole lease with a monotonic lifecycle,
     not just flip statuses.
  3. Engine evidence grammar. Every evidence id matches the engine's
     ``e-<task>-<n>`` form and is ``produced_by`` engine or human; at least one
     engine-produced ``command-output`` exists (the engine runs command checks);
     and every SATISFIED command / git-change-policy condition is backed by the
     matching engine-produced evidence (or, when waived, a human ``waiver``) its
     ``satisfied_by`` names.

This is NOT tamper-proof -- the agent owns the filesystem and could forge all of
the above. The bar (issue #127) is deliberately lower: raise fabrication cost
ABOVE just-doing-the-work cost. Forging a monotonic lease plus grammar-correct,
cross-consistent evidence for ten gates is more work than running the engine,
which is the point. A hash-chained engine journal sidecar would raise the bar
further but requires changing the engine itself; it is intentionally out of scope
here (see issue #127).

Spine locations searched (run-dir contract, per scripts/run_skill_eval.py::_run_once):

  <run-dir>/spine.json                              contract-level spine
  <run-dir>/workspace/**/.agent-work/**/spine.json  a live engine run's spine

The corpus copy under ``workspace/.claude/`` is excluded so a bundled
``*_SPINE.template.json`` can never satisfy the check.

Usage: ``python spine_completed.py <run-dir>``  ->  exit 0 pass / non-zero fail,
one evidence line on stdout.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Engine evidence ids are `e-<task-id>-<n>` (checklist_engine._new_evidence_id).
EVIDENCE_ID_RE = re.compile(r"^e-[a-z0-9][a-z0-9-]*-\d+$")
# Engine-written engine_session fields (checklist_engine.claim writes all of these).
SESSION_FIELDS = (
    "session_id", "status", "claimed_at", "last_heartbeat",
    "claimed_by", "worktree", "previous_session_id", "takeover_reason",
)
ENGINE_CHECK_KINDS = ("command", "git-change-policy")


def _parse_iso(value):
    """Parse an ISO-8601 timestamp (tolerating a trailing 'Z'), or None. Naive
    timestamps are assumed UTC so comparisons never raise on tz-mixing."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def all_tasks_complete(data: dict) -> bool:
    """True iff the engine's gated form has a non-empty ``tasks`` map with EVERY
    task ``complete``. The bare ``{"status": ...}`` form is deliberately NOT
    accepted here (it carries no provenance)."""
    tasks = data.get("tasks")
    if not (isinstance(tasks, dict) and tasks):
        return False
    statuses = [
        (t.get("status") or "").strip().lower()
        for t in tasks.values()
        if isinstance(t, dict)
    ]
    return bool(statuses) and all(s == "complete" for s in statuses)


def engine_session_plausible(data: dict) -> tuple[bool, str]:
    """Whether the spine carries an engine-written ``engine_session`` lease with a
    monotonic claim->heartbeat(->release) lifecycle. The template ships without
    this block, so its mere presence-in-engine-shape is the load-bearing signal."""
    sess = data.get("engine_session")
    if not isinstance(sess, dict):
        return False, ("no engine_session lease block -- the shipped spine template "
                       "carries none; only the engine's `claim` writes one")
    missing = [k for k in SESSION_FIELDS if k not in sess]
    if missing:
        return False, f"engine_session missing engine-written field(s) {missing}"
    sid = sess.get("session_id")
    if not isinstance(sid, str) or not sid.strip():
        return False, "engine_session.session_id is empty"
    status = sess.get("status")
    if status not in ("active", "released"):
        return False, f"engine_session.status {status!r} is not an engine lifecycle state"
    claimed = _parse_iso(sess.get("claimed_at"))
    if claimed is None:
        return False, "engine_session.claimed_at is not an ISO-8601 timestamp"
    hb = _parse_iso(sess.get("last_heartbeat"))
    if hb is None:
        return False, "engine_session.last_heartbeat is not an ISO-8601 timestamp"
    if hb < claimed:
        return False, "engine_session.last_heartbeat precedes claimed_at (non-monotonic lease)"
    if status == "released":
        rel = _parse_iso(sess.get("released_at"))
        if rel is None:
            return False, "released engine_session has no parseable released_at"
        if rel < hb:
            return False, "engine_session.released_at precedes last_heartbeat (non-monotonic)"
    return True, f"engine_session {sid!r} plausible (status={status})"


def evidence_grammar_ok(data: dict) -> tuple[bool, str]:
    """Whether the spine's evidence matches engine grammar and cross-verifies the
    engine-checked conditions. Catches hand-written evidence that flips statuses
    without the engine-produced records the engine would have left."""
    tasks = data.get("tasks")
    if not isinstance(tasks, dict):
        return False, "no tasks to carry evidence"
    all_ev: list[dict] = []
    for t in tasks.values():
        if isinstance(t, dict):
            all_ev.extend(ev for ev in (t.get("evidence") or []) if isinstance(ev, dict))
    if not all_ev:
        return False, "no engine evidence on any task (a driven spine records evidence)"
    for ev in all_ev:
        eid = ev.get("id")
        if not (isinstance(eid, str) and EVIDENCE_ID_RE.match(eid)):
            return False, f"evidence id {eid!r} is off the engine grammar e-<task>-<n>"
        if ev.get("produced_by") not in ("engine", "human"):
            return False, f"evidence {eid} produced_by {ev.get('produced_by')!r} is not engine/human"
    engine_cmd = [
        ev for ev in all_ev
        if ev.get("type") == "command-output" and ev.get("produced_by") == "engine"
    ]
    if not engine_cmd:
        return False, "no engine-produced command-output evidence (engine runs command checks)"
    ev_by_id = {ev.get("id"): ev for ev in all_ev}
    for t in tasks.values():
        if not isinstance(t, dict):
            continue
        for c in (t.get("postconditions") or []) + (t.get("preconditions") or []):
            chk = c.get("check") or {}
            if chk.get("kind") not in ENGINE_CHECK_KINDS or not c.get("satisfied"):
                continue
            sb = c.get("satisfied_by")
            ev = ev_by_id.get(sb)
            if c.get("waived"):
                if ev is None or ev.get("type") != "waiver" or ev.get("produced_by") != "human":
                    return False, f"waived engine check {c.get('id')!r} lacks a human waiver record"
                continue
            if ev is None:
                return False, f"engine check {c.get('id')!r} satisfied_by {sb!r} has no matching evidence"
            if ev.get("produced_by") != "engine" or ev.get("type") not in ("command-output", "artifact-policy"):
                return False, f"engine check {c.get('id')!r} not backed by engine-produced evidence"
    return True, f"evidence grammar OK ({len(all_ev)} items, {len(engine_cmd)} engine command-output)"


def spine_has_engine_provenance(data: dict) -> tuple[bool, str]:
    """Composite gate: terminal gated shape AND engine_session plausibility AND
    engine evidence grammar. Returns (ok, reason)."""
    if not isinstance(data, dict):
        return False, "spine is not a JSON object"
    if not all_tasks_complete(data):
        return False, "not all tasks reached `complete` (or not the engine's gated tasks form)"
    ok, why = engine_session_plausible(data)
    if not ok:
        return False, why
    ok, why = evidence_grammar_ok(data)
    if not ok:
        return False, why
    return True, why


def find_spines(run_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    top = run_dir / "spine.json"
    if top.is_file():
        candidates.append(top)
    workspace = run_dir / "workspace"
    if workspace.is_dir():
        for p in workspace.rglob("spine.json"):
            if ".claude" in p.relative_to(workspace).parts:
                continue
            candidates.append(p)
    return candidates


def main(run_dir_arg: str) -> int:
    run_dir = Path(run_dir_arg)
    spines = find_spines(run_dir)
    if not spines:
        print("FAIL spine_completed: no spine.json under <run-dir>/ or workspace/.agent-work/")
        return 1
    last_reason = ""
    for sp in spines:
        try:
            data = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        ok, reason = spine_has_engine_provenance(data)
        if ok:
            print(f"PASS spine_completed: engine-driven terminal spine at {sp} ({reason})")
            return 0
        last_reason = reason
    print(
        f"FAIL spine_completed: found {len(spines)} spine(s) but none is an "
        f"engine-driven terminal spine (last: {last_reason})"
    )
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("FAIL spine_completed: missing <run-dir> argument")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
