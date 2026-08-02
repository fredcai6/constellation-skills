# IMPLEMENTER_RESULT — g2-implement (issue #663, module G fit logic)

## Assigned gate
`g2-implement` — the grip-baseline FIT function.

## Completed slice
Created `src/physics/layer2/grip_baseline.py` (the fit logic that populates g1's
frozen `GripEstimateRecord`) and `tests/unit/physics/layer2/test_grip_baseline.py`.
Delivers, per session `(year, gp_name, session_type)`:
(a) a vectorized single-SQL cumulative-track-laps helper matching
`session_race.compute_cumulative_track_laps` exactly; (b) a session_type-generalized
clean-lap reader feeding `tyre_supplant.race_degradation_slopes` UNCHANGED for the
wear correction; (c) a saturating intra-session curve + free offset with all
`GripEstimateRecord` fields and `predictive_t` Student-t sigmas; (d) the frozen
thin-session wide-sigma fallback; (e) the frozen rain-flag sigma re-estimation.

## Scope
**Files changed (only these two):**
- `src/physics/layer2/grip_baseline.py` (new)
- `tests/unit/physics/layer2/test_grip_baseline.py` (new)

**Specific exclusions touched:** No. `tyre_supplant.py` was NOT modified (task (b)
local-reader path taken — see below). `grip_store.py` not modified. No g3/g4/g5 work.
`git status --porcelain` shows only my two new files (plus g1's still-uncommitted
grip_store.py/test_grip_store.py which I only READ, and my own `.agent-work/` plan).

## Behavior changed
Yes — new capability: module G's per-session grip-baseline fit (was g1 storage-only).

## Task (b) path taken — LOCAL generalized reader (confirmatory)
I added a local `_read_clean_session_laps(db_path, year, gp_name, session_type)` inside
`grip_baseline.py` and did NOT touch `tyre_supplant.py` at all. It mirrors
`_read_clean_race_laps`'s exact clean-lap filter and column set but parameterizes
`session_type` (that reader hardcodes `'R'`) and pins one `(year, gp_name)`. Its rows
feed `race_degradation_slopes` unchanged — imported and called directly, its OLS
regression body never reimplemented. The handoff preferred not touching `tyre_supplant.py`;
the local reader achieves full reuse with zero risk to existing `session_type='R'`
callers, so no additive edit there was needed.

## Functional-form / constant / method choices + reasoning
- **Curve form:** `grip(x) = session_offset + curve_asymptote*(1 - exp(-curve_rate*x))`,
  x = per-lap cumulative_track_laps, response = wear-corrected lap time (s). Fit with
  `scipy.optimize.curve_fit`, `curve_rate > 0` bound; x internally scaled by its max for
  conditioning then `curve_rate` rescaled back to raw cumulative-lap units. As the track
  rubbers in, times fall → `curve_asymptote` comes out negative (total pace gain);
  `session_offset` is the green-track (x→0) baseline consumers subtract.
- **`curve_offset_correlation` = corr(curve_asymptote, session_offset)** from the
  least-squares covariance (off-diagonal, normalized). This is the T2 separability
  diagnostic g5 tests: high |corr| ⇒ the fit can't separate curve magnitude from the
  free baseline level. (Correlation is x-scale-invariant, so the internal scaling doesn't
  perturb it.)
- **Student-t sigmas via `predictive_t`** — exact call:
  `predictive_t(mu=param, sigma=param_se_from_pcov, n_eff=n_stints, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule()).scale`
  for each of offset/asymptote/rate. `n_eff = n_stints` because laps within a stint are
  strongly autocorrelated, so a driver-stint (not a lap) is the effective independent
  observation. Stored `*_sigma` is that predictive scale (epistemically inflated by
  `sqrt(1 + 1/n_eff)` with the DEFAULT_NU_LOSS heavy tail).
- **THIN_SESSION_SIGMA_INFLATION = 3.0** — a thin offset is a DIFFERENT session's curve
  extrapolated to this session's rubber state; the neighbour's own sigma understates the
  cross-session transfer error, so 3× (~0.3s→~0.9s) reads "this is a guess" without going
  uninformative.
- **RAIN_SIGMA_INFLATION = 4.0** (separate named constant, > thin) — rain changes the
  grip-EVOLUTION regime entirely; the dry saturating-rubber model doesn't describe a
  wet/drying track, so its offset is even less trustworthy than a thin dry extrapolation.
  4 > 3 encodes "rain is a bigger unknown than a thin dry session."
- **FIELD_PRIOR_SIGMA = 2.0s** — deliberately wide (~10× a typical intra-session pace
  spread) baseline for the degenerate all-thin weekend; the field-wide prior is honestly
  uninformative, never falsely confident.
- **Rain flag from `sessions.rainfall`:** the schema declares `rainfall REAL` but the
  collector actually stores an 8-byte little-endian int64 blob = the count of wet weather
  samples (see workflow feedback). Decoded via `int.from_bytes(..., 'little', signed=True)`;
  `rain_flag = count > 0`. Any wet sample ⇒ rain (conservative — errs toward wider sigma,
  the safe direction per Protected Intent).

## Test mode
**Required:** test-after (full test-after before gate close).
**Satisfied:** yes — 12 tests, all green; fit logic tested against synthetic fixtures
(normal/thin/rain) + real 2023 DB (cumulative regression + DB-wrapper smoke).

## Evidence (pasted command outputs)

### Cumulative-laps regression (load-bearing) — vectorized == source, real 2023 data
```
$ py.exe -m pytest tests/unit/physics/layer2/test_grip_baseline.py -q -k cumulative
collected 12 items / 10 deselected / 2 selected
tests\unit\physics\layer2\test_grip_baseline.py ..                       [100%]
2 passed, 10 deselected in 0.44s
```
(`test_cumulative_matches_source_on_real_2023_data` compares the vectorized helper to
`compute_cumulative_track_laps` on sampled real lap_numbers across 3 real 2023 R sessions;
they match exactly.)

### Full file (load-bearing)
```
$ py.exe -m pytest tests/unit/physics/layer2/test_grip_baseline.py -q
collected 12 items
tests\unit\physics\layer2\test_grip_baseline.py ............             [100%]
12 passed in 0.44s
```

### Rain-flag sigma comparison (load-bearing — the frozen Mission requirement's proof)
```
NORMAL FIT dry  session_offset_sigma = 0.029608
NORMAL FIT rain session_offset_sigma = 0.118433  (factor 4.000, RAIN_SIGMA_INFLATION=4.0)
  offset mean unchanged: dry=90.0878 rain=90.0878
  asymptote=-1.7969 rate=0.01396 corr=0.5029
THIN neighbor: offset=89.8417 sigma=0.9000 (=0.30*3.0) status=thin_fallback
```
Rain fit's `session_offset_sigma` is exactly 4.0× the dry fit's on identical data, with
the curve mean unchanged. The test `test_rain_flag_widens_session_offset_sigma_vs_dry`
asserts this numerically.

### simplification_limits (self-checked before returning — g1 reviewer BLOCK precedent)
```
$ py.exe -m src.utils.simplification_limits --paths src/physics/layer2/grip_baseline.py tests/unit/physics/layer2/test_grip_baseline.py
PASS (2 files checked)
```

### git check-ignore (both committable, exit 1)
```
$ git check-ignore src/physics/layer2/grip_baseline.py; echo exit=$?
exit=1
$ git check-ignore tests/unit/physics/layer2/test_grip_baseline.py; echo exit=$?
exit=1
$ git status --porcelain <both files>
?? src/physics/layer2/grip_baseline.py
?? tests/unit/physics/layer2/test_grip_baseline.py
```

## Close-criteria coverage
- Cumulative helper matches source exactly on real data — `test_cumulative_*` ✅
- Generalized session-type reader reuses `race_degradation_slopes` unchanged — ✅ (no reimpl)
- Curve+offset fit produces all required fields via `predictive_t` — `test_normal_fit_*` ✅
- Thin fallback on 2-lap-stint → `thin_fallback` + inflated sigma, never dropped/NULL —
  `test_thin_fallback_*` (neighbour + degenerate field-prior paths) ✅
- Rain fallback → demonstrably wider `session_offset_sigma` (direct numeric compare) —
  `test_rain_flag_widens_*` ✅
- Tests at the exact path `tests/unit/physics/layer2/test_grip_baseline.py` ✅

## Assumptions used
- **Fuel is NOT explicitly removed from the residual pace** (see out-of-scope). The wear
  correction subtracts only the per-compound tyre-age slope that `race_degradation_slopes`
  RETURNS; fuel (which it fits internally but does not return) stays in the residual and is
  absorbed by the curve+offset. `curve_offset_correlation` is exactly the diagnostic that
  surfaces the resulting confound. Explicit fuel de-biasing would require reimplementing
  `race_degradation_slopes`'s body (forbidden) — deferred.
- When `<2` dry compounds are present (`race_degradation_slopes` returns `[]` via its own
  rank guard, e.g. a one-compound quali), the wear correction is skipped and raw lap time
  is used — tyre age is minimal in that regime.
- "Nearest" weekend neighbour = nearest by `|cumulative_track_laps_max diff|` (the
  rubber-level axis the neighbour's curve is a function of), among `fit_status='ok'`
  neighbours with usable curve params.
- Weekend neighbours are passed in as prior `GripEstimateRecord`s (g3/g4 supply them from
  the store); the fit function itself is pure/stateless w.r.t. cross-session ordering.

## Stop conditions hit
None. All three named stop conditions were checked and did not fire: (1)
`race_degradation_slopes` was reused without any `tyre_supplant.py` edit; (2) the 2023 DB
DOES carry the rain column (`sessions.rainfall`) — though stored as a blob, not REAL (see
feedback); (3) no decision outside the granted authority was needed.

## Out-of-scope observations (triage candidates for Commander)
1. **Fuel confound in the grip curve.** `race_degradation_slopes` computes a global fuel
   slope but only returns per-compound wear slopes, so g2's wear-corrected pace still
   contains fuel burn-off (~linear in lap_number). A future enhancement could expose the
   fuel coefficient from `race_degradation_slopes` (additive return field) to fully
   de-fuel the grip curve — would tighten `curve_offset_correlation` separability. Not
   fixable within g2's "don't reimplement / don't edit tyre_supplant" scope.
2. **`sessions.rainfall` schema/storage mismatch.** Schema declares `rainfall REAL` but the
   collector writes a raw 8-byte little-endian int64 blob (wet-sample count). A cleaner
   `session_surface_features.session_rain_flag` (INTEGER) IS populated in the 2023 DB and
   would avoid the blob-decode entirely — worth considering as the canonical rain source
   repo-wide. I used the handoff-directed `sessions.rainfall` (with robust decode) as
   specified.
3. **Rain threshold.** Current rule is any wet sample (count>0) ⇒ rain. A higher count
   threshold (ignore 1–2 sample sensor blips) could be tuned later.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new module `grip_baseline.py`
  (module G's fit logic), sibling to `grip_store.py` (g1) and `tyre_supplant.py`.
- **Capabilities added:** module-G grip-baseline fit — per-session field-pooled saturating
  grip curve + free offset with honest (thin/rain) wide-sigma fallbacks.
- **Constraints/assumptions relied on:** `assumption:student-t-residuals` — honored via
  `predictive_t` for every stored sigma.
- **Decisions implemented (not authored):** `decision:thin-session-explicit` (floor=2
  stints of 4 laps, wide-sigma fallback) and `decision:session-scope-uniform` (generalized
  `session_type` reader) — both implemented exactly as frozen.
- **Claims/evidence produced:** `claim:cumulative-track-laps-reuse` (regression test proves
  exact match to `compute_cumulative_track_laps`); `claim:tyre-supplant-correction-reused`
  (`race_degradation_slopes` imported + called unchanged; no reimplementation).
- **Triage candidates:** the three out-of-scope items above.

## Workflow Feedback
- **Handoff gaps:** Task (e) said "check `sessions.rainfall` or equivalent — read
  `schema.sql` to confirm the exact column name." The column NAME was confirmable from
  schema.sql, but the schema's declared TYPE (`REAL`) is wrong for the actual data — the
  value is a raw int64 blob (wet-sample count). The stop condition ("the real 2023 DB lacks
  the rain/weather column you expected") was satisfied (the column exists), so I proceeded,
  but a handoff note that `rainfall` is a blob wet-count (or a pointer to
  `session_surface_features.session_rain_flag`) would have saved a decode investigation.
- **Context rediscovered:** The exact semantics of "residual pace" / how much of the
  tyre_supplant correction to apply. `race_degradation_slopes` returns only per-compound
  wear slopes (not the fuel term), which forced the fuel-confound decision (out-of-scope
  #1). One line in the handoff on whether fuel removal was expected vs. deferred would have
  removed ambiguity.
- **Instructions improvised around:** None material. The plan template's TDD-red
  postcondition (`c1`) doesn't apply to a test-after run; per the template's own guidance I
  collapsed each slice to the single green command postcondition, which the engine accepted.
- **What would have made this easier:** A one-line note in the handoff that
  `sessions.rainfall` is a blob wet-count, and an explicit statement that fuel de-biasing is
  out of scope for g2 (both now captured as triage candidates).

## Return status
`complete`
