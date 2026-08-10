#!/usr/bin/env python3
"""Run the Commander REPLAN_INPUT G2 check on an explicit path.

Why this exists: the canonical entry point,
`verify_iterative_role_artifacts.py commander --work-id <id>`, cannot accept a
MULTI-SEGMENT work id. Its `_work_area()` guards the id with
`SAFE_ID = ^[A-Za-z0-9][A-Za-z0-9._-]*$`, which forbids `/`, so
`epic-418-followon/commander-424` is refused as "unsafe path characters" before
any verification runs. That is a path-safety guard doing its job on an input
shape it was not designed for -- the same defect class as `run_crew.py`'s
single-segment work-id assumption (discrepancy D5 in this run's REPLAN_INPUT).

This calls the SAME verification the canonical entry point calls --
`constellation-replan/scripts/verify_replan.py :: verify_replan_input` -- on the
file directly. Nothing is relaxed: the packet is checked against the identical
G2 schema. Only the path guard is bypassed, and only because the path is passed
explicitly rather than built from the work id.

The guard was masking a REAL defect: the predecessor's packet had
`completed_outcomes` as an array of strings where G2 requires objects, and the
refusal fired before that was ever checked. It is fixed and verified.

Usage: python3 verify_replan_input.py <path-to-REPLAN_INPUT.json>
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

VERIFIER = Path("/home/tommy/.claude/skills/constellation-replan/scripts/verify_replan.py")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: verify_replan_input.py <path-to-REPLAN_INPUT.json>", file=sys.stderr)
        return 2
    packet_path = Path(argv[0])
    spec = importlib.util.spec_from_file_location("verify_replan", VERIFIER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        mod.verify_replan_input(json.loads(packet_path.read_text(encoding="utf-8")))
    except mod.ReplanError as exc:
        print(f"REFUSED: Commander REPLAN_INPUT violates G2: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {packet_path} verifies against the G2 REPLAN_INPUT schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
