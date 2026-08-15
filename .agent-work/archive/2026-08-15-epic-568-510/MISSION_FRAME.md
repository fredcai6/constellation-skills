# Mission Frame

## Intent

Correct the pending-HARD advisory so an agent is told the legal refresh sequence that already exists: attach a refresh request, start the guarded task, then advance with `--why`; the refresh digest must survive into the successor `current` output.

## Affected Capabilities

- `pending-HARD trip advisory` — text emitted by `_trip_advisory` when the HARD guard blocks a new task.
- `refresh lifecycle` — existing attach → start → advance behavior exercised by the direct regression test.

## Examples / Events

- A pending HARD trip blocks `start`; the advisory must name the ordered legal recovery path.
- After attach, start, and advance, successor `current` exposes the preserved digest.

## Structural Anchors

- `scripts/checklist_engine.py:_trip_advisory` — advisory rendering seam.
- `tests/test_checklist_engine.py:TripHardGuardsBeginNotClose` — direct behavior regression seam.

## Governing Constraints / Assumptions

- `LAUNCH_ORDER:Pre-rulings` — advisory-only; no trip guards, defaults, verbs, state, or schema changes.
- `LAUNCH_ORDER:File ownership` — only the engine file and focused test may change.

## Decision Anchors & Decision Pressure

- The frozen launch order's **advisory-only** ruling permits only status-aware pending-HARD advice and direct regression coverage.
  @grade: settled/measured · leans g1-implement
- Its **legal-sequence** ruling orders attach refresh-request, start, then advance with why, and requires the test to prove digest continuity.
  @grade: settled/human · leans g1-implement,g1-review
- Its **no-runtime-expansion** ruling keeps runtime behavior, defaults, verbs, and schema untouched.
  @grade: settled/human · leans g1-implement,g1-review

## Claims / Evidence Surfaces

- Existing direct regression test is red before the advisory correction and green after it.
- The focused test executes the legal sequence and asserts successor current retains the digest.

## Map Confidence / Staleness / Disputes

- The repository map is degraded/unparseable for this surface; `README.md` is the hash-pinned substitute in `map-orientation.json`. The launch order supplies the bounded code and test anchors, so no architecture inference is required.

## Out of Scope

- Trip runtime semantics, guard/default/state/schema changes, spine rail/lifecycle work, crew launcher work, and Windows-only failures.
