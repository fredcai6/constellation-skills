# IMPLEMENTER_RESULT — g4 held-out-weekend diagnostic (#670, epic #659)

## Assigned gate
`g4` — the leakage-critical strictly-pre held-out diagnostic that SIZES the weekend-utilization join's value (3 arms: fingerprint×composition, driver-overall-only T7-1 baseline, golf null).

## Return status
`complete`

## Slice
Consolidated 2023 season slice `.agent-work/670-season-run/artifacts/scratch/refutil_season_2023.db` (`driver_class_observables` + `reference_laps`), covered rounds 3–22 from `season_results.json` (rounds 1–2 parked). Read-only, offline, pinned interpreter `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Files changed (NEW only; no frozen/landed module edited)
- `scripts/run_heldout_diagnostic_670.py` (tracked-new; `git check-ignore` exit 1 = committable)
- `tests/unit/physics/fingerprint/test_heldout_diagnostic.py` (tracked-new)
- Local-only artifacts (folded into G5): `.agent-work/670-season-run/artifacts/heldout_diagnostic_670_report.{md,json}`

**Specific exclusions touched:** none. Did NOT edit `join.py`/`fit.py`/`store.py`/frozen sets/`docs/architecture/*`; built NO new statistical model (composed `join_weekend_prior` + `fit_driver_fingerprints` via `run_stage_g` + `derive_pilot_vocabulary` + `ReferenceUtilizationStore` + a field-mean pool); no FastF1/online.

## Composition-source confirmation (Admiral D1)
`load_field_composition` returns `ReferenceUtilizationStore.get(...).fingerprint`, which the store rebuilds from the `reference_id="__field__"` field row's `time_shares` ALONE (constructor rows carry their own `time_shares` and never populate `.fingerprint`). Read IDENTICALLY across all 3 arms. Test **(v) `test_composition_read_is_field_row`** asserts the composition equals the `__field__` field row and is NOT a constructor's own shares → PASS. It is the field-median track geometry, never a driver's own R-laps.

## The three arms (all driver-performance inputs strictly-pre)
1. **fingerprint × composition** = `join_weekend_prior(field_composition, cells_d@as_of=R-1)`.
2. **driver-overall-only baseline (T7-1)** = `join_weekend_prior(UNIFORM_composition, the SAME cells_d@R-1)` — the join's uniform-composition form (equal shares → resolved-weighted mean reduces to the unweighted driver mean). THE ONE DOCUMENTED BASELINE (#667 TC-1); same code path, same cells, composition flattened.
3. **golf null** = per-class FIELD mean pooled over rounds `< R` (NO driver term), composed with the SAME field composition, carried as an honest Student-t from the field cross-observation dispersion (`predictive_t`, heavy tail via `nu_loss` — no baked normality).

## Exact scoring formula
Per scored `(round R, driver d, channel ch)`: weights `w_i = comp_i / Σ_present(comp)` over the field composition's severity classes present for d at R; `truth = Σ_i w_i · actual_value(d, class_i, R)` (utilization=`time_deficit_s`, energy=`deployment_share`). Each arm yields a Student-t `PredictiveT(loc=m, scale=s, df=ν)`.
- **PRIMARY:** mean predictive log-score `L = mean over scored triples of scipy.stats.t.logpdf(truth; df=ν, loc=m, scale=s)` (higher better; no normal approximation).
- **SECONDARY:** `mean|resid| = mean|truth − m|`; `coverage = fraction of truths inside each arm's two-sided 90% predictive interval`.

Loop: for each covered held-out round R (as_of=R-1): derive vocab from the field row's severity class_ids, load field composition, fit strictly-pre cells (`fit_cells_as_of` derives as_of=R-1 internally so a caller cannot pass a leaking cutoff), build golf pools `< R`, then for every driver×channel score the 3 arms against truth.

## Two leakage-guard tests — evidence
Both guards are asserted in code AND covered by a dedicated test; both verified DISCRIMINATING via a leaking-cutoff counterfactual (not vacuous):

- **(i) fingerprint fit `test_fingerprint_fit_excludes_round_R`** — a round-R poison row (±1e6) yields byte-identical cells vs the clean fit at as_of=R-1 → PASS. Counterfactual: at a LEAKING as_of=R the poison DOES move the cells (identical=False, c0 mean 0.5→200000), so the equality assertion genuinely bites; at as_of=R-1 identical=True.
- **(ii) golf-null pool `test_golf_null_pool_excludes_round_R`** — round-R poison is a no-op on `per_class`; `max(rounds_used) < R`, `R ∉ rounds_used` → PASS. Counterfactual: at a leaking `held_out=R+1` the round-R poison enters (per_class identical=False, c0 mean 0.5→200000); `golf_null_field_pool` also raises `AssertionError` if `max(rounds_used) >= held_out_round`.

## Other tests
- **(iii) `test_baseline_t7_1_uniform_equals_unweighted_mean`** — uniform-composition join `prior.mean == unweighted resolved-cell mean`, Student-t preserved → PASS (genuine TDD red first: `AttributeError` before `arm_baseline`).
- **(iv) `test_golf_null_is_a_floor`** — for an off-field driver, golf-null point error > driver-arm point error → PASS.

```
python.exe -m pytest tests/unit/physics/fingerprint/test_heldout_diagnostic.py -q
  -> 5 passed in 0.68s
python.exe -m pytest tests/unit/physics/fingerprint -q
  -> 108 passed, 13 skipped in 1.46s
pyright scripts/run_heldout_diagnostic_670.py tests/.../test_heldout_diagnostic.py
  -> 0 errors, 0 warnings, 0 informations
```

## Per-arm aggregate (real run over the actual slice)
| arm | n | mean log-score ↑ | mean \|resid\| ↓ | coverage@90% |
|---|---:|---:|---:|---:|
| fingerprint × composition (arm 1) | 718 | −19.6252 | 0.8541 | 1.000 |
| driver-overall-only / T7-1 (arm 2) | 718 | −19.5294 | 1.1425 | 1.000 |
| golf null — field, no driver (arm 3) | 722 | −0.4594 | 0.8300 | 0.911 |

**Rounds resolved vs thin (as predicted by the handoff):**
- **unresolvable:** round 3 (as_of=2 has no covered strictly-prior severity round) — reported, not forced.
- **thin:** rounds 4, 5 (1–2 prior severity rounds → honest thin-cell fingerprints).
- **resolved:** rounds 6–22 (≥3 prior severity rounds).

## KEY FINDING (surface to commander) — log-score is σ-dominated; read the point metric
Arms 1/2 carry the LANDED #666 fit's predictive σ, which folds in the channel-independent one-sided grip term `g_sigma_onesided`. On this slice that term is pathological: **p90 ≈ 8e9, max ≈ 9.6e9, mean ≈ 1.1e9** across severity rows, versus a `time_deficit_s` scale of ~0.1 s. ~20% of severity rows (>1e6) inflate the fingerprint/baseline cell σ to ~1e9, so their predictive intervals are VACUOUSLY WIDE (coverage 1.000) and their mean log-score is catastrophically negative — a σ-calibration artifact of the landed fit, NOT a point-prediction failure. The golf null uses honest empirical field dispersion (well-scaled σ), so its log-score is not on equal footing with arms 1/2.

**Sigma-robust reading (mean |resid|, the point metric):**
- arm1 0.854 < arm2 1.14 → **composition-weighting HELPS the point prediction** (the join's composition step earns its keep on point error).
- golf null 0.830 ≈ arm1 0.854 → **the whole driver term does NOT beat the field null on point error on this bounded 2023 slice** — an honest thin/near-null result for the driver term (scoped to: 2023-only slice, Q, severity vocabulary v1, ~718 scored driver-weekends over resolved rounds 6–22).

The report leads with a prominent ⚠ σ-interpretation caveat and reports both readings. This is a real diagnostic output; changing the fit's σ is out of scope (do-not-edit `fit.py`).

## Map Impact
- **Structural anchors touched:** none edited. New composition-only consumer `scripts/run_heldout_diagnostic_670.py` over `join.py::join_weekend_prior`, `fit.py::fit_driver_fingerprints` (via `pipeline.py::run_stage_g`), `reference_utilization_store.py` `__field__` row, `pipeline.py::derive_pilot_vocabulary`.
- **Capabilities:** sizes the join value — composition-weighting vs driver-overall vs golf null, strictly-pre.
- **Constraints honored:** zero-leakage (as_of=R-1 fingerprint fit + golf pool `< R`, both asserted + tested); Student-t σ preserved on all arms; one documented baseline; composition = field-reference track geometry.
- **Decision candidates / claims:** `decision:diagnostic-baseline` settled as join T7-1 uniform-composition (stated + justified). New CLAIM/finding: the landed #666 fit's `g_sigma_onesided` term makes the join's predictive interval σ vacuously wide on this slice (p90 ~8e9) — a σ-calibration triage candidate for #666, distinct from this diagnostic.
- **Triage candidates:** (1) #666 fit σ calibration — grip `g_sigma_onesided` (p90 ~8e9) dominates the utilization/energy predictive σ; consider a cap/units audit. (2) The driver-term point value is near-null on the 2023-only slice — a multi-season / different-vocabulary variant is the natural next test (scoped null, not a class-spanning claim).

## Assumptions
- `derive_pilot_vocabulary` yields an UNVERIFIED vocabulary (bounded slice); fit runs `allow_unverified=True` as the docstring sanctions for a diagnostic.
- Golf-null per-class σ = population std of pooled per-observation values (rounds < R), composed with the join's independent-class quadrature (the join's own Build-1 assumption, kept identical for a fair arm comparison); `n_eff = min` per-class pooled count.
- Truth renormalizes composition weights over the classes the driver actually has at R (a missing class does not bias the target).

## Stop conditions hit
- none — zero-leakage did not require editing `join.py`/`fit.py`; the slice carried a field row + both per-class observables for every computation.

## Workflow Feedback
- **Handoff gaps:** The handoff mandates "mean predictive log-score (primary)" but the landed fit's σ (grip-dominated, ~1e9) makes log-score a σ-calibration diagnostic rather than a skill comparison across arm1/2 vs golf null. The handoff did not anticipate that the arms' σ come from DIFFERENT constructions (fit vs empirical dispersion), so a naive reading of the mandated primary metric would report "the driver term is worthless" — the opposite of what the sigma-robust point metric shows. A future handoff should name which σ-basis the arms share, or mandate |resid| as co-primary when arm σ-bases differ.
- **Handoff wording:** the "per-class breakdown" ask (Truth+scoring section) does not apply cleanly — the scored target is a single composition-WEIGHTED scalar per driver-weekend-channel, so there is no per-class scored quantity; I provided per-channel + per-round breakdowns instead and note this. Recommend the handoff say "per-channel + per-round" explicitly.
- **Context rediscovered:** that `run_stage_g`/`run_stage_h` (pipeline.py) already wrap fit+join with the field composition — the map anchors named `join`/`fit`/`derive_pilot_vocabulary` but not these ready-made composition wrappers, which are the cleanest reuse surface. Worth adding to the anchors.
- **What would have made this easier:** a one-line note in the handoff that `g_sigma_onesided` in the slice spans to ~1e9 would have pre-empted the σ investigation.
```
```
