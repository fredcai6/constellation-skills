#!/usr/bin/env python
"""Recovery classifier over the durable crew-run registry.

After a parent-session loss it is ambiguous whether a crew is dead, running,
resumable, or already done. This reads `.agent-work/<work-id>/crew-runs.json`
and CLASSIFIES each recorded attempt from three facts only — its recorded
status, whether its PID is still alive, and whether its result artifact exists —
so Commander gets a durable, recoverable signal instead of guessing from
scattered process state.

Commander runs this before `execute` and before each crew dispatch, and may only
launch a new crew when recovery reports NO unresolved running/resumable/
conflicting attempt for the same work-id/gate/role/worktree.

`classify_entry` is a PURE function over (entry, alive_predicate,
result_exists_predicate); it never touches a real process or filesystem itself,
so every state is directly unit-tested. This module does NOT relaunch, advance
gates, repair git, or integrate results — it only reports.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Callable

_RUN_CREW = Path(__file__).resolve().parent / "run_crew.py"
_spec = importlib.util.spec_from_file_location("run_crew", _RUN_CREW)
run_crew = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("run_crew", run_crew)
_spec.loader.exec_module(run_crew)

# State labels — one per registry entry.
STATE_COMPLETE = "complete"            # completed & result exists; do not rerun
STATE_ACTIVE = "active"                # running & pid alive; block duplicate launch
STATE_RESUMABLE = "resumable"          # not running, result missing, resumable -> resume
STATE_NEEDS_ABANDON = "needs-abandon"  # not running, result missing, not resumable
STATE_CONFLICT = "conflict"            # conflicting active lock; human/Commander decision
STATE_ABANDONED = "abandoned"          # explicitly retired; never blocks a launch
STATE_FAILED = "failed"                # terminal failed with no recoverable result

# States that mean "do not launch a duplicate for this gate/role/worktree".
UNRESOLVED_STATES = {STATE_ACTIVE, STATE_RESUMABLE, STATE_CONFLICT}

AlivePredicate = Callable[[object], bool]
ResultPredicate = Callable[[dict], bool]


def classify_entry(
    entry: dict,
    alive: AlivePredicate,
    result_present: ResultPredicate,
) -> str:
    """PURE recovery classification of one registry entry.

    Decides a single state label from the entry's recorded status, whether its
    PID is alive (`alive(pid)`), and whether its result artifact exists
    (`result_present(entry)`):

      * abandoned                              -> abandoned (retired; ignore)
      * completed & result exists              -> complete (do not rerun)
      * completed but result missing           -> needs-abandon (claimed done, nothing landed)
      * running & pid alive                    -> active (block duplicate launch)
      * running & pid dead, result exists      -> complete (it finished before dying)
      * running & pid dead, result missing,
        resumable                              -> resumable (resume by session name)
      * running & pid dead, not resumable      -> needs-abandon (explicit abandon/relaunch)
      * resumable & result exists              -> complete
      * resumable, result missing              -> resumable
      * failed & result exists                 -> complete
      * failed, no result                      -> needs-abandon
    """
    status = entry.get("status")
    has_result = bool(result_present(entry))
    is_alive = bool(alive(entry.get("pid")))
    resumable = bool(entry.get("resumable", True))

    if status == "abandoned" or entry.get("abandoned"):
        return STATE_ABANDONED

    if status == "completed":
        return STATE_COMPLETE if has_result else STATE_NEEDS_ABANDON

    if status == "running":
        if is_alive:
            return STATE_ACTIVE
        if has_result:
            return STATE_COMPLETE  # finished before the parent/pid died
        return STATE_RESUMABLE if resumable else STATE_NEEDS_ABANDON

    if status == "resumable":
        if has_result:
            return STATE_COMPLETE
        if is_alive:
            return STATE_ACTIVE
        return STATE_RESUMABLE

    if status == "failed":
        return STATE_COMPLETE if has_result else STATE_NEEDS_ABANDON

    # Unknown/missing status with a live pid is a conflicting active lock the
    # Commander/human must resolve; otherwise it needs an explicit decision.
    if is_alive:
        return STATE_CONFLICT
    return STATE_NEEDS_ABANDON


def detect_conflicts(entries: list[dict], states: list[str]) -> list[tuple[dict, dict]]:
    """Pairs of entries that are BOTH active/resumable for the same
    work-id/gate/role/worktree — a two-crews-one-worktree collision. Returns the
    later entry paired with the earlier one it conflicts with."""
    conflicts: list[tuple[dict, dict]] = []
    seen: dict[tuple, dict] = {}
    for entry, state in zip(entries, states):
        if state not in (STATE_ACTIVE, STATE_RESUMABLE):
            continue
        key = (
            entry.get("work_id"),
            entry.get("gate"),
            entry.get("role"),
            entry.get("worktree"),
        )
        if key in seen:
            conflicts.append((entry, seen[key]))
        else:
            seen[key] = entry
    return conflicts


_BEHAVIOR = {
    STATE_COMPLETE: "recoverable/complete; do not rerun",
    STATE_ACTIVE: "active crew (pid alive); block duplicate launch",
    STATE_RESUMABLE: "resume using the stored session name (run_crew.py --resume)",
    STATE_NEEDS_ABANDON: "not running and no result; require explicit --abandon ... --relaunch",
    STATE_CONFLICT: "conflicting active lock; STOP and require Commander/human decision",
    STATE_ABANDONED: "explicitly abandoned; ignored (does not block a launch)",
    STATE_FAILED: "failed; require explicit --abandon ... --relaunch",
}


def classify_registry(
    entries: list[dict],
    *,
    alive: AlivePredicate,
    result_present: ResultPredicate,
) -> list[tuple[dict, str]]:
    """Classify every entry, upgrading members of a same-target collision to
    `conflict` so Commander stops rather than blindly resuming/launching."""
    states = [classify_entry(e, alive, result_present) for e in entries]
    for later, _earlier in detect_conflicts(entries, states):
        for i, e in enumerate(entries):
            if e is later:
                states[i] = STATE_CONFLICT
    return list(zip(entries, states))


def _default_result_present(root: Path) -> ResultPredicate:
    def predicate(entry: dict) -> bool:
        result = entry.get("result")
        return bool(result) and run_crew.result_exists(result, root)

    return predicate


def report(
    entries: list[tuple[dict, str]],
    out: Callable[[str], object] = print,
) -> int:
    """Print one human-readable line per entry plus a summary. Returns a nonzero
    exit code when any unresolved (active/resumable/conflict) attempt remains, so
    Commander can gate a new launch on a zero exit."""
    if not entries:
        out("no recorded crews for this work-id")
        return 0

    unresolved = 0
    for entry, state in entries:
        name = entry.get("session_name", entry.get("crew_id", "<unknown>"))
        behavior = _BEHAVIOR.get(state, state)
        out(f"{name}: {state.upper()} — {behavior}")
        if state in UNRESOLVED_STATES:
            unresolved += 1

    out(f"summary: {len(entries)} crew(s), {unresolved} unresolved")
    return 1 if unresolved else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".", type=Path, help="repo root (default: cwd)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    try:
        entries = run_crew.load_registry(run_crew.registry_path(args.work_id, root))
    except run_crew.CrewLaunchError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    classified = classify_registry(
        entries,
        alive=run_crew.process_alive,
        result_present=_default_result_present(root),
    )
    return report(classified)


if __name__ == "__main__":
    raise SystemExit(main())
