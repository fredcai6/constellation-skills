#!/usr/bin/env python3
"""Postcondition checker for the #467 acceptance round-trip spine.

Exit 0 = the gate's deliverable is on disk and correct; exit 1 = it is not.
Deliberately strict about exact content: a gate that passes on a file that
merely exists is a check that cannot fail.
"""
import re
import sys
from pathlib import Path

DOC = Path(__file__).resolve().parent / "roundtrip.md"

HEAD = ["# Round trip 467", "1. alpha", "2. bravo", "3. charlie"]
TAIL = ["4. delta", "5. echo"]
NONCE_RE = re.compile(r"^6\. NONCE: [0-9a-fA-F]{6}$")


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    gate = sys.argv[1] if len(sys.argv) > 1 else ""
    if not DOC.exists():
        return fail(f"{DOC} does not exist")
    lines = [ln.rstrip() for ln in DOC.read_text(encoding="utf-8").splitlines()]
    lines = [ln for ln in lines if ln.strip()]

    if lines[:4] != HEAD:
        return fail(f"first four lines are {lines[:4]!r}, expected {HEAD!r}")

    if gate == "a1":
        if len(lines) != 4:
            return fail(f"a1 must leave exactly 4 lines, found {len(lines)}: {lines!r}")
        print("OK a1: heading and items 1-3 present, nothing more")
        return 0

    if gate == "a2":
        if len(lines) != 7:
            return fail(f"a2 must leave exactly 7 lines, found {len(lines)}: {lines!r}")
        if lines[4:6] != TAIL:
            return fail(f"lines 5-6 are {lines[4:6]!r}, expected {TAIL!r}")
        if not NONCE_RE.match(lines[6]):
            return fail(f"last line {lines[6]!r} is not '6. NONCE: <6 hex chars>'")
        print(f"OK a2: items 1-6 present, nonce line is {lines[6]!r}")
        return 0

    return fail(f"unknown gate {gate!r}")


if __name__ == "__main__":
    sys.exit(main())
