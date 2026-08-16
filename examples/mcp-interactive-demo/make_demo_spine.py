#!/usr/bin/env python3
"""Generate this directory's throwaway demo spine.

Usage:
    python examples/mcp-interactive-demo/make_demo_spine.py          # rewrite spine.json here
    python examples/mcp-interactive-demo/make_demo_spine.py <dir>    # write a copy elsewhere

Four gates, deliberately covering every condition shape the 7-tool MCP surface
must exercise:

  g1 -- mixed: one command-checked postcondition, one attested (check: null)
  g2 -- an `artifact`/`user-decision` postcondition, satisfied via `attach`
  g3 -- a command-checked postcondition that starts FALSE and carries
        override_policy.allowed=true, satisfied via `waive` (never made true)
  g4 -- close-out: command-checked + attested, plus a `block`/`resume` cycle
        exercised on it before it is actually driven to completion

How this spine addresses its own files, and why it is not relative
------------------------------------------------------------------
`checklist_engine.py:883` runs a `command` check as::

    subprocess.run([shell, "-c", command], capture_output=True, text=True)

with **no `cwd`**. The check inherits whatever directory the driving process
happens to stand in -- through the MCP door that is the bound spine's git
toplevel; from the CLI it is the user's own shell. So a path written relative
to this directory resolves correctly from essentially nowhere, and that is why
the paths here were absolute in the first place (issue #605).

The fix is not to make them relative. It is to make them *not need a working
directory at all*: every path is written as a shell expansion that resolves to
the same absolute location on any machine, from any cwd, with no setup --

    ${SPINE_DEMO_WORKSPACE:-${TMPDIR:-/tmp}/constellation-mcp-demo-$(id -u)}

The `$(id -u)` suffix keeps two users on one host out of each other's demo
directory. `SPINE_DEMO_WORKSPACE` is the override seam for anyone who wants the
demo to write somewhere specific. Nothing machine-specific is committed, and
the workspace lands outside the repository, so driving the demo never dirties a
tracked directory.

`tests/test_shipped_examples_are_portable.py` asserts that the committed
`spine.json` is exactly what this generator produces, so the paths cannot be
hand-edited back to something machine-specific without failing the suite.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent

# Expanded by the POSIX shell that runs each command check, and by whatever
# shell the reader uses to follow an imperative. Both sides expand it the same
# way, which is what makes the demo drivable without instructions.
WORKSPACE = "${SPINE_DEMO_WORKSPACE:-${TMPDIR:-/tmp}/constellation-mcp-demo-$(id -u)}/workspace"

SETUP_HINT = (
    'Run `WS="' + WORKSPACE + '"; mkdir -p "$WS"` first, from any directory -- '
    "the demo workspace resolves the same way from all of them."
)


def build_spine() -> dict:
    """The demo spine, as data. Deterministic: same output on every machine."""
    return {
        "work_id": "mcp-interactive-demo",
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
                    f'Create notes.txt with one line in the demo workspace: `echo "hello" > "{WORKSPACE}/notes.txt"`. '
                    f"{SETUP_HINT} Then confirm you understand this demo spine's four gates."
                ),
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "notes.txt exists in the demo workspace",
                     "check": {"kind": "command", "command": f'test -f "{WORKSPACE}/notes.txt"'},
                     "satisfied": False},
                    {"id": "c2", "statement": "gates understood", "check": None, "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
            "g2": {
                "id": "g2",
                "title": "A human-decision checkpoint",
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
                "id": "g3",
                "title": "A check the principal accepts as non-blocking",
                "imperative": (
                    f'Normally requires "{WORKSPACE}/optional_report.txt" to exist; '
                    "the principal has decided this check is non-blocking for this run, so waive it rather than "
                    "making it true."
                ),
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "optional_report.txt exists in the demo workspace",
                     "check": {"kind": "command", "command": f'test -f "{WORKSPACE}/optional_report.txt"'},
                     "override_policy": {"allowed": True, "authority": "human", "reason_required": True},
                     "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
            "g4": {
                "id": "g4",
                "title": "Close out the run",
                "imperative": (
                    f'Write "{WORKSPACE}/SUMMARY.md" summarizing the run in two or three sentences.'
                ),
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "SUMMARY.md exists in the demo workspace",
                     "check": {"kind": "command", "command": f'test -f "{WORKSPACE}/SUMMARY.md"'},
                     "satisfied": False},
                    {"id": "c2", "statement": "summary honestly describes the run", "check": None, "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
        },
    }


def spine_text() -> str:
    """The exact bytes the committed `spine.json` must contain."""
    return json.dumps(build_spine(), indent=2) + "\n"


def write_spine(target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / "spine.json"
    path.write_text(spine_text(), encoding="utf-8")
    return path


def main(argv: list[str]) -> int:
    target = Path(argv[1]).resolve() if len(argv) > 1 else HERE
    print(write_spine(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
