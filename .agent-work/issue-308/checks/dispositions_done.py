"""Guard: g4 disposed all lessons EXCEPT the one carved out for g6.

The cold plan critic found (BLOCKING 1) that g4's original postcondition -- zero
active entries -- is unreachable before g6. `lesson:verify-launch-order-claims-against-code`
states cluster A's own pattern, so disposing it *is* the routing decision:
graduating it to docs/agents/ is bin 2, which is Tommy's call, not the Commander's.

So this check pins the carve-out BY ID rather than by count. A bare `count == 1`
would be satisfied by any surviving lesson, including one simply forgotten -- which
is the same under-inclusive-predicate failure this issue exists to consolidate.

Exit 0 = exactly one lesson remains and it is the carved-out one.
Run from the repo root.
"""
import pathlib
import re
import sys

CARVED = "verify-launch-order-claims-against-code"
ROOT = pathlib.Path(__file__).resolve().parents[3]
LESSONS = ROOT / ".agent-work/LESSONS.md"


def main() -> int:
    if not LESSONS.exists():
        print(f"FAIL: {LESSONS} missing")
        return 1

    text = LESSONS.read_text(encoding="utf-8")
    if "## Active" not in text:
        print("FAIL: no '## Active' section — the file's shape changed; this check cannot speak to it")
        return 1

    active = text.split("## Active", 1)[1]
    ids = re.findall(r"^### lesson:(\S+)", active, re.M)

    print(f"active entries: {len(ids)} -> {ids}")

    if ids == [CARVED]:
        print(f"PASS: only the carved-out cluster-A lesson remains, deferred to g6")
        return 0

    if not ids:
        print(f"FAIL: ZERO active entries. The carved-out lesson '{CARVED}' was disposed here, "
              f"but disposing it IS the routing decision and that is Tommy's call (g6).")
        return 1

    extra = [i for i in ids if i != CARVED]
    if CARVED not in ids:
        print(f"FAIL: the carved-out lesson '{CARVED}' is gone and {len(extra)} others remain")
    else:
        print(f"FAIL: {len(extra)} lesson(s) besides the carve-out are still active: {extra}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
