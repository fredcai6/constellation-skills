# Reviewer Handoff — G2

## Gate
`g2`

## Survey State Location
`.agent-work/629-feature-view/g2-review/review.json`.

## What Was Implemented
`src/physics/feature_view/build_weekend_state.py` — `build_weekend_state_records(model,
transformed_df, *, model_version)` composes real `WeekendStateRecord` rows from a fitted
`WeekendStateModel`'s `.transform()` output. Plus `tests/unit/physics/feature_view/
test_build_weekend_state.py` (6 new tests).

## How to Inspect the Diff
Uncommitted working tree, `C:/Programs/f1-629`, branch `feat/629-feature-view`. Read
`src/physics/feature_view/build_weekend_state.py` and the new test file directly (untracked
additions — `git status --porcelain` then read files, not `git diff --name-only`).

## Task Statement
Compose `WeekendStateRecord` rows from `WeekendStateModel`'s L1-L4 output, citing exact column
names from `model.model_cols()`/`model.layer_sigma_cols()` (never hand-guessed), applying a
real per-row/per-axis resolved-vs-unresolved rule reusing `effective_axis_sigma`
(`src.physics.layer2.estimate_store_fields`, same import G1's `store.py` already uses — not
reimplemented). Full detail: `.agent-work/629-feature-view/g2-implementer-handoff.md`. Full
evidence: `.agent-work/629-feature-view/g2-implementer-result.md`.

## Close Criteria
- Column names are read from `model.model_cols()`/`.layer_sigma_cols()` at runtime, not
  hardcoded string-built guesses — verify by reading the source.
- The resolved/unresolved rule is genuinely per-row AND per-axis: construct (or confirm the
  implementer's own tests construct) (a) a row where one axis is fully resolved (value+sigma
  present) and another axis on the SAME row is unresolved (NaN value or sigma) — confirm both
  are labeled independently and correctly; (b) confirm an unresolved axis's sigma is actually
  WIDENED via `effective_axis_sigma`, not just copied through or dropped.
- `effective_axis_sigma` is imported from `estimate_store_fields`, not reimplemented (read the
  import statement).
- No `src.evo_predictor` import in the new file.
- Full suite `py -m pytest tests/unit/physics/feature_view -q` green — reproduce the count
  (33 expected: 27 from G1 + 6 new).
- `round_idx` omission from the stored record is documented with real reasoning (not silently
  dropped) — confirm the docstring's claim (`gp_name` disambiguates within a year since only
  Q-session rows are the current input) is actually sound, or flag if you can construct a
  counterexample (e.g. a calendar year with a repeated `gp_name`).
- `simplification_limits --paths src/physics/feature_view` clean.

## Allowed Scope
`src/physics/feature_view/build_weekend_state.py` (new); `tests/unit/physics/feature_view/
test_build_weekend_state.py` (new). Nothing else.

## Specific Exclusions
G1's `records.py`/`store.py` are CLOSED/frozen this run — confirm they were not modified. Do
not flag a G1 file as in-scope for this review; if you spot a genuine G1 defect, note it as an
out-of-scope observation, not a G2 blocker.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`.
- Reuse (not reimplement) `effective_axis_sigma`.
- Tests use `tmp_path`, never a committed DB path.

## Map Anchors (inbound)
- **Structural:** `struct:physics.weekend_state` (read-only consumer), `struct:physics.feature_view`.
- **Capability:** `WeekendStateModel.fit/transform/model_cols/layer_sigma_cols`.
- **Constraints:** `constraint:physics_region_no_evo_import`.
- **Evidence expectations:** explicit-unknown contract applied genuinely per-row/per-axis.

## Evidence Produced
See `.agent-work/629-feature-view/g2-implementer-result.md`. Commander independently re-ran
the suite (33 passed) and read `build_weekend_state.py` source directly.

## Suggested Model Tier
Simple bounded — straightforward composition; the per-row rule is the one thing worth
adversarial attention.

## Stop Conditions
Stop and return BLOCK if: column names are hardcoded rather than read from the model's own
accessors; the resolved/unresolved rule is a blanket constant rather than genuinely per-row;
`round_idx`'s omission is unsound (a real counterexample exists); evidence is unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
