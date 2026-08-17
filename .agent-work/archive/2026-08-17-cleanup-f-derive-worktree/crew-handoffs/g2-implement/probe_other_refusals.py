#!/usr/bin/env python3
"""Evidence probe: the refusals that are NOT the origin comparison still refuse.

Removing a guard is only safe if it removed exactly one thing. This drives the
engine's other refusal paths through `main()` against an origin-stamped spine,
FROM THE SPINE'S OWN WORKTREE (so the origin comparison was satisfied even at
base and cannot be what produces these refusals), and reports the exit code and
whether stderr carried REFUSED for each.

Run identically before and after the g2 change; the two outputs must match.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "scripts" / "checklist_engine.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("engine_refusal_probe", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_in(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", *args],
        cwd=str(cwd), check=True, capture_output=True, text=True,
    )


def _spine(worktree: str) -> dict:
    def gate(gid, status="pending", pre=None):
        return {
            "id": gid, "title": gid, "imperative": f"do {gid}",
            "preconditions": pre or [], "postconditions": [
                {"id": "c1", "statement": "done", "check": None, "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": status, "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }

    return {
        "work_id": "w1", "type": "gated", "items": ["g1", "g2"],
        "origin": {"work_id": "w1", "worktree": worktree, "opened_by": "init_work_area"},
        "tasks": {
            "g1": gate("g1"),
            "g2": gate("g2", pre=[{"id": "p1", "statement": "g1 done",
                                   "check": None, "satisfied": False}]),
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


CASES = [
    ("a verb naming a task that does not exist",
     ["start", "no-such-gate", "--session-id", "s1"]),
    ("a gate whose precondition is unmet",
     ["start", "g2", "--session-id", "s1"]),
    ("a mutating verb from a session that does not hold the lease",
     ["start", "g1", "--session-id", "an-impostor"]),
    ("a mutating verb with no session id at all",
     ["start", "g1"]),
    ("advance with an unmet postcondition",
     ["advance", "g1", "--session-id", "s1", "--why", "because"]),
    ("advance with no running understanding",
     ["advance", "g1", "--session-id", "s1"]),
    ("release by a session that does not hold the lease, unforced",
     ["release", "--session-id", "an-impostor"]),
]


def main() -> int:
    engine = _load_engine()
    here = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve() / "wt"
        (worktree / ".agent-work" / "w1").mkdir(parents=True)
        _git_in(worktree, "init", "-q")
        spine_path = worktree / ".agent-work" / "w1" / "spine.json"

        for label, argv in CASES:
            spine_path.write_text(json.dumps(_spine(worktree.as_posix()), indent=2),
                                  encoding="utf-8")
            journal = spine_path.parent / "spine.json.journal"
            if journal.exists():
                journal.unlink()
            os.chdir(worktree)
            try:
                # Establish the lease as s1 first, so "impostor" cases are
                # refused for LEASE reasons and not for want of a lease.
                with contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    engine.main(["--file", str(spine_path), "claim", "--session-id", "s1",
                                 "--claimed-by", "implementer", "--worktree", "."])
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    code = engine.main(["--file", str(spine_path), *argv])
            finally:
                os.chdir(here)
            print(f"exit={code} refused={'REFUSED:' in err.getvalue()!s:<5} {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
