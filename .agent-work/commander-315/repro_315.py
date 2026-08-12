#!/usr/bin/env python
"""Live repro for issue #315 — a command-kind check inherits the LAUNCHER's cwd.

Builds two directories:

  proj/            a real git repo, holding the spine at proj/.agent-work/w1/spine.json
    real_evidence.txt        <- exists in the project
  decoy/           an unrelated directory the launcher happens to stand in
    decoy_evidence.txt       <- exists ONLY here

The spine has two gates, both with repo-root-relative command postconditions:

  gA  `test -f decoy_evidence.txt`   -- must FAIL: no such file in the project
  gB  `test -f real_evidence.txt`    -- must PASS: it is right there in the project

The engine is invoked with an ABSOLUTE --file, from cwd=decoy/.

BEFORE the fix (no cwd= on subprocess.run):
  gA advances  -> FAIL-OPEN: a stranger's file satisfied a gate that should refuse
  gB refuses   -> FALSE-RED: the project's own file is invisible

AFTER the fix (cwd = repo root enclosing the spine):
  gA refuses   -> correct
  gB advances  -> correct

Exit 0 only when all four expectations hold.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[2] / "scripts" / "checklist_engine.py"


def build(tmp: Path) -> tuple[Path, Path, Path]:
    proj = tmp / "proj"
    decoy = tmp / "decoy"
    (proj / ".agent-work" / "w1").mkdir(parents=True)
    decoy.mkdir(parents=True)

    subprocess.run(["git", "init", "-q", str(proj)], check=True)

    (proj / "real_evidence.txt").write_text("in the project\n", encoding="utf-8")
    (decoy / "decoy_evidence.txt").write_text("in the launcher's cwd\n", encoding="utf-8")

    spine = {
        "work_id": "w1",
        "type": "gated",
        "items": ["gA", "gB"],
        "tasks": {
            "gA": {
                "id": "gA",
                "status": "pending",
                "imperative": "a check naming a file that exists ONLY in the launcher's cwd",
                "preconditions": [],
                "postconditions": [
                    {
                        "id": "c1",
                        "statement": "decoy_evidence.txt is present",
                        "check": {"kind": "command", "command": "test -f decoy_evidence.txt"},
                        "satisfied": False,
                    }
                ],
                "evidence": [],
            },
            "gB": {
                "id": "gB",
                "status": "pending",
                "imperative": "a check naming a file that exists in the PROJECT",
                "preconditions": [],
                "postconditions": [
                    {
                        "id": "c1",
                        "statement": "real_evidence.txt is present",
                        "check": {"kind": "command", "command": "test -f real_evidence.txt"},
                        "satisfied": False,
                    }
                ],
                "evidence": [],
            },
        },
        "triage_candidates": [],
        "blockers": [],
        "refusals": [],
    }
    spine_path = proj / ".agent-work" / "w1" / "spine.json"
    spine_path.write_text(json.dumps(spine, indent=1), encoding="utf-8")
    return proj, decoy, spine_path


def drive(spine_path: Path, gate: str, cwd: Path) -> tuple[int, str]:
    """start+advance one gate with the engine, running FROM `cwd`."""
    subprocess.run(
        [sys.executable, str(ENGINE), "--file", str(spine_path), "start", gate],
        cwd=str(cwd), capture_output=True, text=True,
    )
    proc = subprocess.run(
        [sys.executable, str(ENGINE), "--file", str(spine_path), "advance", gate, "--mechanical"],
        cwd=str(cwd), capture_output=True, text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="repro315-"))
    try:
        proj, decoy, spine_path = build(tmp)
        print(f"project root : {proj}")
        print(f"launcher cwd : {decoy}")
        print(f"spine        : {spine_path}")
        print()

        rc_a, out_a = drive(spine_path, "gA", decoy)
        advanced_a = "gA -> complete" in out_a
        print("--- gate gA: `test -f decoy_evidence.txt` (file exists ONLY in launcher cwd) ---")
        print(f"    advanced = {advanced_a}   (want False: the gate must REFUSE)")
        print(f"    {out_a.strip().splitlines()[-1] if out_a.strip() else '(no output)'}")
        print()

        rc_b, out_b = drive(spine_path, "gB", decoy)
        advanced_b = "gB -> complete" in out_b
        print("--- gate gB: `test -f real_evidence.txt` (file exists in the PROJECT) ---")
        print(f"    advanced = {advanced_b}   (want True: the gate must PASS)")
        print(f"    {out_b.strip().splitlines()[-1] if out_b.strip() else '(no output)'}")
        print()

        ok = (not advanced_a) and advanced_b
        if ok:
            print("REPRO RESULT: PASS -- checks resolve against the project, not the launcher")
            return 0
        print("REPRO RESULT: FAIL -- issue #315 reproduces")
        if advanced_a:
            print("  * FAIL-OPEN: a decoy file in the launcher's cwd satisfied gate gA")
        if not advanced_b:
            print("  * FALSE-RED: the project's own real_evidence.txt was invisible to gate gB")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
