#!/usr/bin/env python3
"""DC1 as a MACHINE ASSERTION, not prose (gate g4's explicit requirement).

DC1: a cold agent reaches DONE on a real role spine through the door, with zero
malformed calls.

Both halves are read from the driving agent's own record via the shared scorer,
so this asserts the same numbers MEASUREMENT.md quotes rather than a retelling
of them. Exits non-zero if either half fails.

Usage: python3 assert_dc1.py <mcp-arm-dir> [<mcp-arm-dir> ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_arm import score  # noqa: E402

def main(argv: list[str]) -> int:
    if not argv:
        print("usage: assert_dc1.py <mcp-arm-dir> ...", file=sys.stderr)
        return 2
    failures = []
    for d in argv:
        s = score(Path(d).resolve())
        name = Path(d).name
        if not s["reached_done"]:
            failures.append(f"{name}: never reached DONE")
        if s["shape_errors"]:
            failures.append(f"{name}: {s['shape_errors']} malformed call(s)")
        print(f"{name}: reached_done={s['reached_done']} "
              f"malformed_calls={s['shape_errors']} "
              f"invocation_attempts={s['invocation_attempts']}")
    if failures:
        print("DC1 FAILED: " + "; ".join(failures), file=sys.stderr)
        return 1
    print(f"DC1 PASS: {len(argv)} cold agent(s) reached DONE through the door "
          f"with zero malformed calls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
