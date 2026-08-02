# Triage recommendation — tc1 (NOT filed; routed to Admiral)

**Labels:** cleanup, architecture weakness
**Anchor:** `src/evo_predictor/practice_preprocessor/_compute.py`
**Lane:** sibling **#379** (practice preprocessor / evidence aggregation) — NOT filed to
avoid collision with active sibling work; Admiral to route.

## What
Two functions exceed the strict per-function simplification limits (<20 cyclomatic
complexity, <100 lines):
- `compute_practice_features` — complexity 21, 290 lines
- `compute_constructor_race_features_from_laps` — complexity 36, 214 lines

Consider decomposing each (e.g. extract the per-bucket feature-assembly and the
`PracticeFeatures`/`ConstructorFeatures` construction into helpers).

## Importance
Low/medium. Maintainability only — both functions are correct and well-tested.
The two functions assemble many per-driver feature tuples inline, which is the
bulk of the complexity.

## Evidence
- **Pre-existing on main:** before #380 the values were complexity 20 / 277 lines and
  35 / 202 lines respectively. #380 added +1 complexity and +12–13 lines each via the
  `qs_normalizer` resolution + the new `quali_sim_compound_normalizer` routing.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/practice_preprocessor/_compute.py`
  reports the four violations.
- **Not a CI failure:** the canonical `py -m src.utils.simplification_limits --baseline`
  check enforces `file_lines` only; `_compute.py` (618 lines) passes it. CI is green.

## Acceptance criteria (if picked up)
- Both functions under the strict per-function limits (or explicitly baseline-allowlisted
  with rationale).
- `compute_practice_features` / `compute_constructor_race_features_from_laps` behaviour
  unchanged (existing tests green); no new feature-value differences.

## Out of scope
- Any change to the qs_*/lr_* compound-normalization regime behaviour (that is #380,
  shipped).
- This is a refactor in the #379 practice-preprocessor lane; #380 deliberately made the
  smallest additive change rather than decompose mid-flight.
