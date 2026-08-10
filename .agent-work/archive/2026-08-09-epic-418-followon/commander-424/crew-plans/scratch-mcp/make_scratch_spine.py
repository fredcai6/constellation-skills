#!/usr/bin/env python3
"""Generate a fresh throwaway gated spine (proving ground for the MCP door,
issue #424) plus a tiny throwaway survey fixture. Never touches the live
worktree spine.json/execute.json.

Usage: python make_scratch_spine.py <arm-dir> [nonce]

Optional NONCE is stamped into g1's imperative text -- a per-run unguessable
marker so a later proof (e.g. a headless dispatch) can show its final answer
could only contain that text by genuinely round-tripping through the engine,
not by a model guessing plausible-sounding output.

Four gates, deliberately covering every condition shape the 7-tool surface
must exercise:
  g1 -- mixed: one command-checked postcondition, one attested (check: null)
  g2 -- an `artifact`/`user-decision` postcondition, satisfied via `attach`
  g3 -- a command-checked postcondition that starts FALSE and carries
        override_policy.allowed=true, satisfied via `waive` (never made true)
  g4 -- close-out: command-checked + attested, plus a `block`/`resume` cycle
        exercised on it before it is actually driven to completion

Command-check paths are ABSOLUTE (the engine runs `command` checks with no
`cwd`).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

arm = Path(sys.argv[1]).resolve()
nonce = sys.argv[2] if len(sys.argv) > 2 else None
if arm.exists():
    shutil.rmtree(arm)
ws = arm / "workspace"
ws.mkdir(parents=True)

W = str(ws)
nonce_clause = f" NONCE:{nonce}" if nonce else ""

spine = {
    "work_id": "scratch-mcp-424",
    "type": "gated",
    "config": {"rework_cap": 99},
    "items": ["g1", "g2", "g3", "g4"],
    "consolidation": None,
    "triage_candidates": [],
    "blockers": [],
    "tasks": {
        "g1": {
            "id": "g1", "title": "Set up the work area",
            "imperative": f"Create {W}/notes.txt with one line, then confirm you understand this scratch spine's four gates.{nonce_clause}",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "notes.txt exists",
                 "check": {"kind": "command", "command": f"test -f {W}/notes.txt"},
                 "satisfied": False},
                {"id": "c2", "statement": "gates understood", "check": None, "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "g2": {
            "id": "g2", "title": "A human-decision checkpoint",
            "imperative": "Record the principal's decision on whether to proceed, as a user-decision artifact.",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "a user-decision artifact is attached",
                 "check": {"kind": "artifact", "evidence_type": "user-decision"},
                 "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "g3": {
            "id": "g3", "title": "A check the principal accepts as non-blocking",
            "imperative": f"Normally requires {W}/optional_report.txt to exist; the principal has decided this check is non-blocking for this run.",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "optional_report.txt exists",
                 "check": {"kind": "command", "command": f"test -f {W}/optional_report.txt"},
                 "override_policy": {"allowed": True, "authority": "human", "reason_required": True},
                 "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "g4": {
            "id": "g4", "title": "Close out the run",
            "imperative": f"Write {W}/SUMMARY.md summarizing the run in two or three sentences.",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "SUMMARY.md exists",
                 "check": {"kind": "command", "command": f"test -f {W}/SUMMARY.md"},
                 "satisfied": False},
                {"id": "c2", "statement": "summary honestly describes the run", "check": None, "satisfied": False},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
    },
}

(arm / "spine.json").write_text(json.dumps(spine, indent=2), encoding="utf-8")

# A tiny throwaway survey fixture, purely to exercise spine_survey_result
# (record + consolidate), which does not apply to the gated spine above.
survey = {
    "work_id": "scratch-mcp-survey-424",
    "type": "survey",
    "config": {"rework_cap": 99},
    "items": ["r1", "r2"],
    "consolidation": None,
    "triage_candidates": [],
    "blockers": [],
    "tasks": {
        "r1": {
            "id": "r1", "title": "check one",
            "imperative": "Check one thing.",
            "preconditions": [], "postconditions": [],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
        "r2": {
            "id": "r2", "title": "check two",
            "imperative": "Check another thing.",
            "preconditions": [], "postconditions": [],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
    },
}
(arm / "survey.json").write_text(json.dumps(survey, indent=2), encoding="utf-8")

print(str(arm / "spine.json"))
print(str(arm / "survey.json"))
