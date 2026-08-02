# Implementer Handoff — G1 ANCHOR FIX (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`. Read `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`.

This is a SMALL, targeted correction to the already-approved G1 work. The blend
function, config plumbing, and the pre-fusion attach point are all CORRECT and
must be kept. ONE thing changes: the anchor FIELD.

## Why (measured)
The current production anchor is `DriverFeatures.qs_best_raw` (short-stint
quali-sim laps only). A Commander acceptance probe proved this is too narrow: its
pure-anchor ceiling is ~0.69, vs the §7.6.3 target ceiling ~0.81. Using
`min(qs_best_raw, lr_best_raw)` — the min-sector pace across BOTH practice buckets
(short-stint + long-stint) — recovers the full §7.6.3 improvement (probe: α=0.5
overall 0.757 / EASY 0.882, ceiling 0.816 — matches the prototype's
`best_across_fp`). This is what admiral ruling 1 actually requires ("the same
best_across_fp min-sector pace source through the real practice-evidence
machinery"): the two buckets ARE the machinery's split of the all-FP laps, so the
min across them reconstructs the all-laps min-sector ordering signal.

## The change

### 1. `src/evo_predictor/sampled_runtime.py` — `_anchor_quali_field`
Currently builds the anchor from `qs_best_raw` only:
```python
driver_raw: dict[str, float] = {d.driver_id: d.qs_best_raw for d in features.drivers}
```
Change it to the NaN-safe min across `qs_best_raw` and `lr_best_raw` per driver:
- For each driver, take the minimum of `qs_best_raw` and `lr_best_raw`, treating
  None/NaN/non-finite as missing.
- If BOTH are missing -> NaN (the blend function already handles NaN: that driver
  gets no anchor term).
- If exactly ONE is present -> use it.
- If both present -> the smaller (faster) value.

Implement the per-driver min as a small pure helper (e.g. a module-level function
`_best_across_practice_buckets(driver) -> float` returning the min or nan), so it
is unit-testable. Keep `lr_best_raw` and `qs_best_raw` both read from
`DriverFeatures` (both are existing fields:
`src/evo_predictor/models/_features.py` `qs_best_raw` ~line 59, `lr_best_raw`
~line 56). Both are raw seconds, lower=faster, NaN when missing.

Update the inline comment to say the anchor is the min-sector practice pace across
BOTH the quali-sim (short-stint) and long-run (long-stint) buckets = the
production reconstruction of the §7.6.3 `best_across_fp` all-FP min-sector signal.

### 2. `src/evo_predictor/quali_pace_anchor.py` — docstring only
The blend function itself does NOT change (it takes a generic `anchor` array). But
update its module docstring / the `anchor` param doc: the production anchor is now
"min-sector practice pace across both practice buckets (qs + lr), raw seconds,
lower=faster" rather than naming `qs_best_raw` specifically. Keep the math, sign,
and missingness exactly as-is.

### 3. Tests
- Add a unit test for the new `_best_across_practice_buckets` helper (or wherever
  you put the per-driver min): both present -> min; one missing -> the other; both
  missing -> nan; None handled as missing. Synthetic `DriverFeatures` or a minimal
  stand-in.
- Update the existing `sampled_runtime` attach-point test
  (`test_anchor_attach_point_inside_run_stage_pre_fusion`) if it hard-codes
  `qs_best_raw` expectations: it should now reflect the min-of-two-buckets anchor.
  Keep its core assertion (anchor applied to the race_weekend per-module pi
  pre-fusion; gating correct; race_start untouched).
- Do NOT weaken any existing `quali_pace_anchor.py` blend-function tests.

## Close Criteria
- `_anchor_quali_field` builds the anchor as the NaN-safe per-driver min of
  `qs_best_raw` and `lr_best_raw`.
- The per-driver min is a tested pure helper.
- Attach point UNCHANGED (still per-module race_weekend pi inside `_run_stage`,
  pre-fusion, gated on the same module+task+enabled). sigma_pi still unchanged.
- All existing tests still green; new/updated tests green.
- `py -m src.utils.simplification_limits` clean on touched paths (except the
  pre-existing `predict_from_features` 153-line violation, unrelated).

## Allowed Scope
`src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/quali_pace_anchor.py`
(docstring only), test files.

## Specific Exclusions
Do NOT change: the blend math, the attach point, the config keys/threading, the
default OFF. Do NOT touch fusion files, `prediction_ceiling_and_priorities.md`,
`scope_quali_anchor_414.py`, race/race_start behavior, or
`scripts/accept_quali_anchor_420.py` (the Commander re-runs G2).

## Constraints
DB-only (both fields already on DriverFeatures; no new DB read). Missingness
explicit (None/NaN handled, no impute). Pure tested helper for the min.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_quali_pace_anchor.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_pipeline_manifest_v4.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits src/evo_predictor/sampled_runtime.py src/evo_predictor/quali_pace_anchor.py
```

## Suggested Model Tier
Simple bounded — a focused, well-specified field change with a tested helper.

## Authority
Decided by Commander (logged in DECISION_anchor_field.md): anchor =
min(qs_best_raw, lr_best_raw), NaN-safe. Everything else frozen.

## Stop Conditions
Stop if `lr_best_raw` is not present on `DriverFeatures` (it is — confirm) or if
changing the anchor breaks the attach-point invariant.

## Return Format
IMPLEMENTER_RESULT: the change, the helper + its test, files changed, full test +
simplification evidence, confirmation the attach point + blend math + config are
unchanged.
