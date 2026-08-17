"""C1 + C2 — the deleted symbol has no live reference, and the constant is gone.

C1 as the handoff words it ("`grep -rn worktree_from_spine_path --include=*.py
scripts/` returns ZERO lines") cannot be satisfied as written, and the handoff
says so itself two sections later: its own Wiring Grep expects the two fenced g3
files to still name the symbol in prose, and Specific Exclusions forbids
touching them. `scripts/hooks/spine_rail.py` is under `scripts/`, so the literal
grep can only reach zero by editing a file this gate may not edit.

This check applies C1's intent and states every count out loud:

  * ZERO references anywhere under `scripts/` outside the fenced g3 file --
    definition, call, import or prose;
  * the fenced file's remaining hits are PROSE only (no `def` and no call), so
    nothing resolves the deleted name at runtime;
  * `AGENT_WORK_DIR` is gone from the repo (not just from the engine).

Exit 0 = C1 and C2 hold. Exit 1 = a live reference or a stray constant survives.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FENCED_G3 = "scripts/hooks/spine_rail.py"   # #609 g3's, repaired there, not here
SYMBOL = "worktree_from_spine_path"


def grep(pattern: str, *paths: str) -> list[str]:
    out = subprocess.run(["grep", "-rn", pattern, "--include=*.py", *paths],
                         cwd=ROOT, capture_output=True, text=True)
    return [line for line in out.stdout.split("\n") if line.strip()]


def main() -> int:
    failures: list[str] = []

    hits = grep(SYMBOL, "scripts/")
    fenced = [h for h in hits if h.startswith(FENCED_G3 + ":")]
    live = [h for h in hits if not h.startswith(FENCED_G3 + ":")]
    print(f"C1: `{SYMBOL}` under scripts/ -- {len(hits)} line(s) total: "
          f"{len(live)} outside the fenced g3 file, {len(fenced)} inside it")
    for line in hits:
        print(f"    | {line}")
    if live:
        failures.append(f"C1: {len(live)} reference(s) to {SYMBOL} survive outside {FENCED_G3}")

    # The fenced hits must be prose. A definition or a call would mean something
    # still resolves the name at runtime, which no exclusion can excuse.
    executable = [h for h in fenced
                  if re.search(rf"def\s+{SYMBOL}\s*\(", h) or re.search(rf"{SYMBOL}\s*\(", h)]
    print(f"C1: of the {len(fenced)} fenced hit(s), {len(executable)} are a definition or a call")
    if executable:
        failures.append(f"C1: {FENCED_G3} still DEFINES or CALLS {SYMBOL}: {executable}")

    const = grep("AGENT_WORK_DIR", "scripts/", "tests/", "docs/", "skills/")
    print(f"C2: `AGENT_WORK_DIR` across scripts/ tests/ docs/ skills/ -- {len(const)} line(s)")
    for line in const:
        print(f"    | {line}")
    if const:
        failures.append(f"C2: AGENT_WORK_DIR still referenced: {const}")

    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("\nOK: no live reference to the deleted derivation, and the constant is gone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
