# scripts.verify_cycles
scripts/verify_cycles.py, 71 lines, 3 holes

Verify a work area's exploration cycles are consolidated before explore closes.

Wired as the explorer spine's `explore` step command check: `explore` cannot
close having run zero cycles, or with any cycle left unconsolidated — the
mechanical teeth behind "premature convergence is the failure mode this skill
exists to prevent" (see DESIGN_SPEC.md, spine table, "explore").

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, sys
imported by: none found

- [CyclesVerificationError](CyclesVerificationError.md) class: Raised when the exploration-cycles invariant is broken.
- [cycles_dir](cycles_dir.md) function: HOLE: no docstring
- [verify_cycles](verify_cycles.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
