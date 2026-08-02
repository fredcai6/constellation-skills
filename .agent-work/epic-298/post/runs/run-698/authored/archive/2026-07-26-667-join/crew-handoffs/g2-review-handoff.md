# Reviewer Handoff — g2 (season-capable bounded-validation harness)

## Gate
`g2` (issue #667 — "the join", validation harness)

## What was implemented
- NEW `scripts/join_bounded_validation_667.py` — season-capable offline harness.
- NEW `tests/unit/physics/fingerprint/test_join_bounded_validation.py` — synthetic smoke (always-run)
  + real-slice skip-if-absent (claimed 2 passed).
- IMPLEMENTER_RESULT: `.agent-work/667-join/crew-results/g2-implement-result.md`.

## How to inspect
Read both files in the worktree `C:/Programs/f1brainz-wt/epic659-667` (untracked — `git status`).
Re-run yourself with the PINNED interpreter:
```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join_bounded_validation.py -q
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" src/utils/simplification_limits.py --paths scripts/join_bounded_validation_667.py tests/unit/physics/fingerprint/test_join_bounded_validation.py
```

## Task statement
An offline, season-capable harness that runs the g1 join on a real bounded slice — reading #664
`reference_laps` composition × #666-fit fingerprint cells — and emits an honest-σ summary. A measured
thin/unresolved result is a COMPLETE outcome, reported with real numbers.

## Close Criteria (verify independently — do not trust the implementer's claim)
- The harness composes the seams CORRECTLY: fits cells via `fit_driver_fingerprints` into a TEMP
  store; reads composition via `ReferenceUtilizationStore.get(...).fingerprint`; reads cells via
  `store.get_fingerprint(driver, era, vocabulary, channel, "deficit")`; runs `join_weekend_prior`
  for BOTH channels; records corner_share, prior mean/scale/nu, thin_classes, weight_on_thin,
  resolved_mask.
- **Vocabulary alignment:** the SAME `ClassVocabulary` object drives both the fit and the join (so
  `vocabulary_version` matches and the join does not refuse). class_ids are DERIVED from the DB
  (severity classes from `reference_laps.class_ids_json`), not hardcoded.
- **Composition passthrough:** the WHOLE field-reference `.fingerprint` dict is passed as
  `composition` (the join selects the severity classes itself); it is NOT pre-filtered or
  renormalized before the join.
- **Season-capable + partial-tolerant:** circuit list is a `build_summary(...)` argument (defaults to
  the launch-order slice); an absent circuit is skipped with a printed note, never a crash. CONFIRM
  this — the real DB has only Great Britain, so the harness MUST run on a partial slice.
- **Tests:** the synthetic smoke test ALWAYS runs (builds a temp own-DB, no real-DB dependency) and
  asserts both channels produce a prior + thin surfacing populated; the real-slice test skips cleanly
  when the DB path is absent (mirror `test_bounded_validation.py`'s skipif).
- **No committed data/*.db;** temp DBs only; editable-.pth sys.path insert present at the top of the
  script; join module UNTOUCHED.
- `simplification_limits` passes on both files.

## Specific scrutiny
- The implementer reports a structural finding: `map_version` is per-circuit on disk
  (`2023-Great Britain-Q:v1`), so the fit runs season-wide (`map_version=None`, pooling all circuits
  up to `as_of_round`) and only the composition is per-circuit. CONFIRM this is what the code does and
  that it is a sound reading (the join re-weights season-pooled cells by each circuit's corner-severity
  mix — that is the intended per-weekend prior). If you disagree, BLOCK with specifics.
- Confirm the emitted JSON summary is written UNDER `.agent-work/` and is NOT staged/committed (the
  implementer notes `.agent-work/` is not broadly gitignored here — verify the harness does not add it
  to a committed path).

## Constraints
- Offline/DB-only (no FastF1 online call). Reuse #664/#666 seams as-is. Map fence.

## Required Evidence
Reproduce the pytest run + simplification yourself (paste output). Confirm the synthetic smoke runs
(does not skip). If the real slice DB is present, optionally smoke the real path and sanity-check that
a thin cell (c1) surfaces.

## Suggested Model Tier
`stronger — multi-seam offline harness; the vocabulary/composition alignment is subtle`

## Authority
Verdict is yours (APPROVE / BLOCK). The seam-consumption design is DECIDED — verify the implementation
matches it and the tests are honest (synthetic always-runs, real skips cleanly).

## Stop Conditions
BLOCK with specifics if: the seams are miscomposed, the vocabulary mismatches fit vs join, the synthetic
smoke does not actually run, a data/*.db is committed, or the join module was edited.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/667-join/crew-results/g2-review-result.md`): verdict
(APPROVE/BLOCK), what you verified + reproduced (paste output), each close-criterion pass/fail, the
map_version structural finding adjudication, out-of-scope observations, workflow feedback.
