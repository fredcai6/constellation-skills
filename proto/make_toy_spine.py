#!/usr/bin/env python3
"""Generate a fresh toy spine + arm workspace for one tracer arm.

Usage: python make_toy_spine.py <arm-dir>

Four gates, mixed condition kinds: two machine-checked `command` conditions and
three attested (`check: null`) ones. The WORK is deliberately trivial (write
three small files) so what the tracer measures is engine-driving friction, not
task difficulty.

Command-check paths are ABSOLUTE. The engine runs command checks with no `cwd`,
so a relative path would pass or fail depending on where the caller's shell
happened to be -- a real defect, but one that would swamp this measurement, so
it is neutralized here and reported separately.

The imperatives describe the WORK ONLY and name no door. Real shipped spines
carry CLI invocation strings inside their imperatives; that teaching burden is
part of what this prototype is testing, so the toy spine carries none.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

arm = Path(sys.argv[1]).resolve()
if arm.exists():
    shutil.rmtree(arm)
ws = arm / "workspace"
ws.mkdir(parents=True)

W = str(ws).replace("\\", "/")

spine = {
    "work_id": "toy-widget",
    "type": "gated",
    "config": {"rework_cap": 99},
    "items": ["g1", "g2", "g3", "g4"],
    "consolidation": None,
    "triage_candidates": [],
    "blockers": [],
    "tasks": {
        "g1": {
            "id": "g1",
            "title": "Set up the work area",
            "imperative": (
                f"Create the file {W}/notes.txt containing one line describing what "
                "you are about to build. Then confirm you have understood this "
                "spine's four gates."
            ),
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "notes.txt exists in the workspace",
                 "check": {"kind": "command", "command": f"test -f {W}/notes.txt"},
                 "satisfied": False},
                {"id": "c2", "statement": "you have understood the four gates of this spine",
                 "check": None, "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "g2": {
            "id": "g2",
            "title": "Build the widget",
            "imperative": (
                f"Create the file {W}/widget.txt. Its contents must include the word "
                "hello on some line."
            ),
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "widget.txt exists",
                 "check": {"kind": "command", "command": f"test -f {W}/widget.txt"},
                 "satisfied": False},
                {"id": "c2", "statement": "widget.txt contains the word hello",
                 "check": {"kind": "command", "command": f"grep -q hello {W}/widget.txt"},
                 "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "g3": {
            "id": "g3",
            "title": "Verify the widget",
            "imperative": (
                f"Read {W}/widget.txt back and satisfy yourself it is what gate g2 "
                "asked for. Record what you checked."
            ),
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "you have read widget.txt back and it matches what g2 required",
                 "check": None, "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "g4": {
            "id": "g4",
            "title": "Close out the run",
            "imperative": (
                f"Write {W}/SUMMARY.md summarizing in two or three sentences what you "
                "built and how you verified it."
            ),
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "SUMMARY.md exists",
                 "check": {"kind": "command", "command": f"test -f {W}/SUMMARY.md"},
                 "satisfied": False},
                {"id": "c2", "statement": "the summary honestly describes what was built",
                 "check": None, "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
    },
}

(arm / "spine.json").write_text(json.dumps(spine, indent=2), encoding="utf-8")
print(str(arm / "spine.json"))
