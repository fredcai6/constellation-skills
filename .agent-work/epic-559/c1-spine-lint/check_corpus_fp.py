"""Admiral-authored check: no zero-collect fault on spines known to be sound.

Every spine this epic drove to a terminal state ran its checks for real, so a
zero-collect fault on one of them is a false positive by construction. Asserts
what it examined, so a broken discovery step cannot read as a clean pass.
"""
import sys, pathlib
sys.path.insert(0, "scripts")
import validate_spine as v

# Scope: spines THIS epic drove to a terminal state, whose checks demonstrably ran.
# A zero-collect fault on one of those is a false positive by construction.
# Archived spines from earlier epics are deliberately excluded: their selectors
# point at tests that have since been renamed or deleted, so a zero-collect fault
# there is a TRUE positive and evidence the lint works. The c1 crew found exactly
# one such case (epic-298 PLAN-rework1.json, -k 'live_spine') and blocked rather
# than waiving -- correctly, against this script's earlier over-broad scope.
roots = [pathlib.Path(".agent-work/epic-559"), pathlib.Path(".agent-work/epic-418-followon")]
seen, bad = 0, []
for root in roots:
    for f in sorted(root.rglob("*.json")):
        if "PLAN" not in f.name.upper() and "SPINE" not in f.name.upper():
            continue
        try:
            faults = v.validate_file(str(f))
        except Exception:
            continue
        seen += 1
        for flt in faults:
            if "zero" in flt.code:
                bad.append((str(f), flt.where, flt.message[:90]))

print(f"examined {seen} spine files")
if seen < 3:
    print("REFUSED: discovery found too few spines to be meaningful")
    sys.exit(1)
for b in bad:
    print("FALSE POSITIVE:", *b)
sys.exit(1 if bad else 0)
