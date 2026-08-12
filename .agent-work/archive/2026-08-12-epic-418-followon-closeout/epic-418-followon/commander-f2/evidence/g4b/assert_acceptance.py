#!/usr/bin/env python3
"""g4b acceptance: did a real dispatched agent drive a real role spine to DONE
THROUGH THE DOOR ALONE?

TWO-SIDED BY CONSTRUCTION, and that is the whole point. `reached_done` alone is
one-sided: an agent that hit a wall on a door tool, dropped to
`python scripts/checklist_engine.py advance` in a Bash call and finished still
scores `reached_done: true`. The cold plan critic caught exactly that in the
first version of this gate's plan, and noted that F's own scorer ALREADY counts
CLI engine invocations (`ENGINE_HINT`) -- the gate was simply declining to read
the one field that would let the measure lose.

So this refuses unless BOTH hold:
  1. the driving agent reached DONE, and
  2. it made ZERO CLI engine invocations.

Counted from the DRIVING AGENT'S OWN record (`--output-format stream-json`),
never from the server log -- `decision:count-from-the-call-record`. A
client-side schema rejection never arrives at the server, so a server-side
numerator structurally hides exactly the fumbles the typed door is credited with
avoiding. A measure that cannot lose is not a measure.

Usage: python assert_acceptance.py <arm-dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from score_arm import score  # noqa: E402


def main() -> int:
    arm = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "arm-mcp"
    record = arm / "record.jsonl"
    if not record.is_file():
        print(f"REFUSED: no driving-agent record at {record}")
        print("This is an UNMEASURED condition, not a measured negative.")
        return 2

    s = score(arm)
    cli = s["invocation_attempts"] if s.get("cli_arm") else None

    # The scorer counts an MCP tool call as 1 invocation and a Bash
    # checklist_engine.py invocation as 1 too, so recover the CLI half by
    # re-walking the detail rows: any row whose tool is Bash carried CLI
    # engine invocations.
    cli_invocations = sum(d.get("invocations", 0) for d in s["detail"]
                          if d.get("tool") == "Bash")
    mcp_invocations = sum(d.get("invocations", 0) for d in s["detail"]
                          if str(d.get("tool", "")).startswith("mcp__spine__"))

    print(json.dumps({
        "arm_dir": s["arm_dir"],
        "reached_done": s["reached_done"],
        "invocation_attempts": s["invocation_attempts"],
        "mcp_invocations": mcp_invocations,
        "cli_engine_invocations": cli_invocations,
        "shape_errors": s["shape_errors"],
        "usage_reads": s["usage_reads"],
        "far_side_recoveries": s["far_side_recoveries"],
        "absorbable_fumbles": s["absorbable_fumbles"],
        "total_tool_calls": s["total_tool_calls"],
    }, indent=2))

    failures = []
    if not s["reached_done"]:
        failures.append("the driving agent never reached DONE")
    if cli_invocations:
        failures.append(
            f"{cli_invocations} CLI engine invocation(s) -- it did NOT drive through "
            "the door ALONE; this is the half `reached_done` cannot see")
    if mcp_invocations == 0:
        failures.append("zero MCP tool calls -- the door was never used at all")

    if failures:
        for f in failures:
            print(f"REFUSED: {f}")
        return 1

    print("\nACCEPTED: reached DONE, through the door alone, "
          f"{mcp_invocations} door calls, 0 CLI engine invocations.")
    print(f"Door-own friction observed on this run: {s['shape_errors']} shape error(s). "
          "Zero is a result: report it as measured, never as proof the capture works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
