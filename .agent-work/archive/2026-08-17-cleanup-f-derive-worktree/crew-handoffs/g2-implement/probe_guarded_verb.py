#!/usr/bin/env python3
"""Evidence probe, run identically BEFORE and AFTER the g2 change.

Drives ONE guarded verb (`start`) through `checklist_engine.main()` against an
origin-stamped spine, from three cwds -- the spine's own worktree, a foreign
git worktree, a non-git directory -- and reports, for each:

  * the exit code and whether stderr carried REFUSED,
  * EVERY git subprocess the engine actually spawned during the call, recorded
    by wrapping `subprocess.run` in the engine module rather than inferred.

Prints a stable, diffable block. No arguments.
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
    spec = importlib.util.spec_from_file_location("engine_probe", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_in(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", *args],
        cwd=str(cwd), check=True, capture_output=True, text=True,
    )


SPINE = {
    "work_id": "w1", "type": "gated", "items": ["g1"],
    "origin": {"work_id": "w1", "worktree": None, "opened_by": "init_work_area"},
    "tasks": {"g1": {
        "id": "g1", "title": "g1", "imperative": "do g1",
        "preconditions": [], "postconditions": [],
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
        worktree, foreign, nogit = base / "wt", base / "elsewhere", base / "nogit"
        (worktree / ".agent-work" / "w1").mkdir(parents=True)
        foreign.mkdir()
        nogit.mkdir()
        _git_in(worktree, "init", "-q")
        _git_in(foreign, "init", "-q")
        spine_path = worktree / ".agent-work" / "w1" / "spine.json"

        real_run = subprocess.run
        for label, cwd in (("the spine's own worktree", worktree),
                           ("a foreign git worktree", foreign),
                           ("a non-git directory", nogit)):
            payload = json.loads(json.dumps(SPINE))
            payload["origin"]["worktree"] = worktree.as_posix()
            spine_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            journal = spine_path.parent / "spine.json.journal"
            if journal.exists():
                journal.unlink()

            spawned: list[tuple[list[str], str]] = []

            def spy(args, *a, **kw):
                if isinstance(args, (list, tuple)):
                    # Attribute the spawn to the first frame outside this probe
                    # and outside subprocess itself: `engine.subprocess` IS the
                    # shared stdlib module, so this spy sees every spawn in the
                    # process, not only the engine's.
                    import traceback

                    site = "?"
                    for frame in reversed(traceback.extract_stack()[:-1]):
                        if Path(frame.filename).name not in (Path(__file__).name, "subprocess.py"):
                            site = f"{Path(frame.filename).name}:{frame.lineno}"
                            break
                    spawned.append((list(args), site))
                return real_run(args, *a, **kw)

            engine.subprocess.run = spy
            os.chdir(cwd)
            err = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    code = engine.main(["--file", str(spine_path), "start", "g1"])
            finally:
                os.chdir(here)
                engine.subprocess.run = real_run

            state = json.loads(spine_path.read_text(encoding="utf-8"))
            print(f"--- start g1, cwd = {label}")
            print(f"    exit code        : {code}")
            print(f"    stderr REFUSED   : {'REFUSED:' in err.getvalue()}")
            print(f"    gate status after: {state['tasks']['g1']['status']}")
            print(f"    origin.worktree  : {state['origin']['worktree'] == worktree.as_posix()}"
                  " (unchanged)")
            print(f"    git subprocesses : {len(spawned)}")
            for argv, site in spawned:
                print(f"      {site:<24} {' '.join(str(x) for x in argv)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
