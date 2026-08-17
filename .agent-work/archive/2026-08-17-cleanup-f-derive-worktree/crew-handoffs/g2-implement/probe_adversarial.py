#!/usr/bin/env python3
"""Adversarial probe: was the removed comparison the ONLY thing preventing harm?

The harm the comparison was introduced against is TWO CONTROLLING AGENTS on one
spine -- "a lost-and-resurrected parent session once produced two controlling
agents in one worktree" (docs/CHECKLIST_SCHEMA.md, the engine-session section).

This drives that scenario from a FOREIGN tree, which is the only place the
comparison ever bit, and reports what refuses the second agent. Run before and
after; the harm case must be refused on both sides, and by the LEASE.

It also reports the one genuine behaviour delta, stated rather than hidden:
what a foreign agent can now do to an UNCLAIMED spine.
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
    spec = importlib.util.spec_from_file_location("engine_adv_probe", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_in(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", *args],
        cwd=str(cwd), check=True, capture_output=True, text=True,
    )


def _spine(worktree: str) -> dict:
    return {
        "work_id": "w1", "type": "gated", "items": ["g1"],
        "origin": {"work_id": "w1", "worktree": worktree, "opened_by": "init_work_area"},
        "tasks": {"g1": {
            "id": "g1", "title": "g1", "imperative": "do g1",
            "preconditions": [], "postconditions": [
                {"id": "c1", "statement": "done", "check": None, "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }},
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


def main() -> int:
    engine = _load_engine()
    here = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp).resolve()
        worktree, foreign = base / "wt", base / "elsewhere"
        (worktree / ".agent-work" / "w1").mkdir(parents=True)
        foreign.mkdir()
        _git_in(worktree, "init", "-q")
        _git_in(foreign, "init", "-q")
        spine_path = worktree / ".agent-work" / "w1" / "spine.json"

        def run(cwd: Path, argv: list[str]) -> tuple[int, str]:
            os.chdir(cwd)
            err = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    code = engine.main(["--file", str(spine_path), *argv])
            finally:
                os.chdir(here)
            return code, err.getvalue().strip().splitlines()[-1] if err.getvalue().strip() else ""

        def reset():
            spine_path.write_text(json.dumps(_spine(worktree.as_posix()), indent=2),
                                  encoding="utf-8")
            j = spine_path.parent / "spine.json.journal"
            if j.exists():
                j.unlink()

        print("=== HARM CASE: a second controlling agent, arriving from a FOREIGN tree")
        reset()
        c, _ = run(worktree, ["claim", "--session-id", "agent-one",
                              "--claimed-by", "commander", "--worktree", "."])
        print(f"  agent-one claims from the spine's own worktree : exit={c}")
        c, msg = run(foreign, ["claim", "--session-id", "agent-two",
                               "--claimed-by", "commander", "--worktree", "."])
        print(f"  agent-two claims from a foreign tree           : exit={c}")
        print(f"    -> {msg[:150]}")
        c, msg = run(foreign, ["start", "g1", "--session-id", "agent-two"])
        print(f"  agent-two mutates from a foreign tree          : exit={c}")
        print(f"    -> {msg[:150]}")
        state = json.loads(spine_path.read_text(encoding="utf-8"))
        print(f"  lease still held by                            : "
              f"{state['engine_session']['session_id']}")
        print(f"  gate status                                    : "
              f"{state['tasks']['g1']['status']}")

        print()
        print("=== THE BEHAVIOUR DELTA, stated: an UNCLAIMED spine, foreign tree")
        reset()
        c, msg = run(foreign, ["claim", "--session-id", "a-stranger",
                               "--claimed-by", "commander", "--worktree", "."])
        print(f"  a stranger claims an unclaimed spine from afar : exit={c}")
        if msg:
            print(f"    -> {msg[:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
