# G3 Implementer Rework 1

Use `constellation-implementer` to resolve every P1 in `.agent-work/issue-418-iterative-planning/g3-review/REVIEW_RESULT.md` without redesigning the checklist engine or changing G1/G2 schemas.

## TDD First

Before production edits, replace/extend `tests/test_iterative_planning_doctrine.py` with adversarial executable tests that fail causally when:

- any cross-skill path fails in the installed `constellation-*` naming layout;
- an Explorer confirm can complete without verifying the run's exact shaped-brief artifact;
- a Commander execute can complete without a named, verified run `REPLAN_INPUT` artifact;
- an Admiral can launch the next wave without exactly one verified/audit-recorded transition, or without repair preservation and both rendered output artifacts.

Use the same frozen red/green command:

```bash
uv run python -m pytest -q tests/test_explorer_templates.py tests/test_iterative_planning_doctrine.py
```

## Required Correction

- Use one install-safe cross-skill resolution method. Prefer canonical installed sibling names if that is compatible with current installer/runtime conventions; do not invent an alias or duplicate G1/G2 validators.
- Give Explorer an explicit run artifact path and command postcondition invoking the public G1 shaped-brief verifier on that actual artifact.
- Give Commander an explicit run `REPLAN_INPUT` output path and command postcondition invoking the public G2 input verifier on that actual artifact. Discrepancies remain evidence and are not auto-filed.
- Give Admiral explicit per-boundary input/result/audit/render paths and an operative command check, using existing engine/check mechanisms, that refuses next launch until exactly one transition verifies, is audit-recorded, honors repair hold, and produces both current-truth and wave-review Markdown. Material exceptions use the same boundary.
- Tests must simulate installed layout and real run artifacts/launch refusal; literal directive dictionaries plus unrelated checked-in fixtures are insufficient.
- Preserve existing human latitude, independent review, engine, recovery, audit, and authorized tracker-port boundaries.

## Scope and Exclusions

The live Explorer/Commander/Admiral doctrine and spines, `tests/test_iterative_planning_doctrine.py`, and narrowly necessary pure/bundled verification helpers/tests are in scope. No engine redesign, tracker/network implementation, direct `gh`, schema change, compatibility alias, archive/history/external provenance, or G4 demo work. Preserve unrelated dirty changes.

Run the reviewer's installed-path probe (or a stricter equivalent), all focused/confirmatory suites, JSON parse, no-network, wiring, and diff checks. Refresh the exact ordinal inventory/digest and `IMPLEMENTER_RESULT.md` with rework RED/GREEN and scope evidence. Drive the checklist terminal, release its lease, and report to `/root`.
