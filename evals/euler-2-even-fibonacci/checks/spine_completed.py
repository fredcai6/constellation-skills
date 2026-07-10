#!/usr/bin/env python
"""PROCESS check (gating): a constellation engine spine reached a TERMINAL state.

This check BITES. It does not merely stat a path -- it locates the spine JSON the
workflow wrote and PARSES it, asserting a terminal/complete status. An in-progress
or absent spine FAILs (non-zero). The runner's ``--dry-run-fail`` synthesizes an
``{"status": "in-progress"}`` spine; this check catches it and returns FAIL, which
is the proof the check is not vacuous.

Spine locations searched (run-dir contract, per scripts/run_skill_eval.py::_run_once
and the dry-run launchers which write ``<run-dir>/spine.json``):

  <run-dir>/spine.json                              contract-level spine (what the
                                                    dry-run launchers write; where a
                                                    real run may also drop one)
  <run-dir>/workspace/**/.agent-work/**/spine.json  a live engine run's spine, written
                                                    inside the agent's workspace

The corpus copy under ``workspace/.claude/`` is excluded so a bundled
``*_SPINE.template.json`` can never satisfy the check.

Usage: ``python spine_completed.py <run-dir>``  ->  exit 0 pass / non-zero fail,
one evidence line on stdout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TERMINAL = {"done", "complete", "completed", "terminal", "closed", "archived"}


def spine_is_terminal(data: dict) -> bool:
    """True iff the parsed spine is in a terminal/complete state.

    Handles two shapes: the simple ``{"status": "..."}`` form the dry-run launcher
    writes, and the engine's gated form ``{"tasks": {id: {"status": ...}}}`` where
    terminal means every task is ``complete``."""
    if not isinstance(data, dict):
        return False
    status = data.get("status")
    if isinstance(status, str) and status.strip().lower() in TERMINAL:
        return True
    tasks = data.get("tasks")
    if isinstance(tasks, dict) and tasks:
        statuses = [
            (t.get("status") or "").strip().lower()
            for t in tasks.values()
            if isinstance(t, dict)
        ]
        if statuses and all(s == "complete" for s in statuses):
            return True
    return False


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
    for sp in spines:
        try:
            data = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if spine_is_terminal(data):
            print(f"PASS spine_completed: terminal spine at {sp}")
            return 0
    print(
        f"FAIL spine_completed: found {len(spines)} spine(s) but none reached a "
        f"terminal/complete state"
    )
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("FAIL spine_completed: missing <run-dir> argument")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
