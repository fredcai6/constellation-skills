"""Admiral-authored check: no zero-collect fault on spines this epic drove.

Not the crew's to edit; block against it instead.

Population is enumerated by each file's own `type` field (gated | survey), NOT by
a filename substring. The filename filter this script used first was wrong twice:
once over-broad (all of .agent-work/, which swept archived epics whose selectors
point at since-deleted tests -- true positives, not false ones), and once
under-broad (a "PLAN"/"SPINE" filename match, which silently dropped 11 of 25
real checklists including every REVIEW_SURVEY). The crew's own resweep had
already identified filename filtering as unreliable and avoided it; this script
now uses the method the crew used.

Asserts both halves: what it examined, and that what it examined is the
population it claims to model.
"""
import json, sys, pathlib
sys.path.insert(0, "scripts")
import validate_spine as v

ROOTS = [pathlib.Path(".agent-work/epic-559"), pathlib.Path(".agent-work/epic-418-followon")]
MIN_EXPECTED = 20  # measured population at authoring time was 25; a large drop means discovery broke

population, bad = [], []
for root in ROOTS:
    for f in sorted(root.rglob("*.json")):
        try:
            doc = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(doc, dict) or doc.get("type") not in ("gated", "survey"):
            continue
        population.append(f)
        try:
            faults = v.validate_file(str(f))
        except Exception as exc:
            bad.append((str(f), "validate raised", repr(exc)[:80]))
            continue
        for flt in faults:
            if "zero" in flt.code:
                bad.append((str(f), flt.where, flt.message[:90]))

print(f"examined {len(population)} checklists, discovered by type field")
if len(population) < MIN_EXPECTED:
    print(f"REFUSED: discovery found {len(population)} < {MIN_EXPECTED}; the population, not the corpus, changed")
    sys.exit(1)
for b in bad:
    print("FALSE POSITIVE:", *b)
sys.exit(1 if bad else 0)
