#!/usr/bin/env python
"""Verify the captured PRE arm (#299) — the g1-capture engine postcondition.

Exits non-zero on any of: a missing run, an uncaptured transcript, a forbidden operation
against f1Brainz, or a run whose worktree did not end at the pin with nothing landed.

Deliberately strict about the one thing the launch order calls a stop condition: if any
measured run pushed, opened a PR, commented on an issue, or committed in f1Brainz, this
fails and says which run and which call.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
PIN = "3541d2929b19de37107ae13e56776b7162d07255"
EXPECTED = ["690", "688", "698", "716", "704"]


def main() -> int:
    problems: list[str] = []
    if not RUNS.is_dir():
        print(f"FAIL: no runs directory at {RUNS}")
        return 1

    for issue in EXPECTED:
        d = RUNS / f"run-{issue}"
        if not d.is_dir():
            problems.append(f"#{issue}: run directory missing")
            continue

        meta_p, order_p = d / "meta.json", d / "ordering.json"
        if not meta_p.is_file():
            problems.append(f"#{issue}: meta.json missing")
            continue
        if not order_p.is_file():
            problems.append(f"#{issue}: ordering.json missing (extractor not run)")
            continue

        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        order = json.loads(order_p.read_text(encoding="utf-8"))

        if meta.get("pin") != PIN:
            problems.append(f"#{issue}: pin mismatch {meta.get('pin')}")
        if meta.get("git_after", {}).get("head") != PIN:
            problems.append(f"#{issue}: worktree did not end at the pin")
        if not meta.get("git_unchanged"):
            problems.append(f"#{issue}: worktree changed during the run — something landed")
        if not order.get("captured"):
            problems.append(f"#{issue}: transcript NOT-CAPTURED")
        if order.get("tool_call_count", 0) == 0:
            problems.append(f"#{issue}: zero tool calls captured")

        for op in order.get("forbidden_operations", []):
            problems.append(
                f"#{issue}: FORBIDDEN OPERATION at call {op['index']} "
                f"({op['tool']}): {op['target'][:120]}"
            )

    if problems:
        print("CAPTURE VERIFICATION FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"CAPTURE VERIFIED: {len(EXPECTED)} runs at pin {PIN[:8]}, "
          f"no forbidden operations, nothing landed in f1Brainz.")
    for issue in EXPECTED:
        o = json.loads((RUNS / f"run-{issue}" / "ordering.json").read_text(encoding="utf-8"))
        print(f"  #{issue}: calls={o['tool_call_count']:>3} "
              f"first_map={o['first_map_read_index']} "
              f"first_src={o['first_src_read_index']} "
              f"map_before_src={o['map_before_src']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
