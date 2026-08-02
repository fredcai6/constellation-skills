# Implementation Result

## Assigned gate
`g1-implement` — Readiness core module + tests (issue #512, C3 regime-capability readiness)

## Completed slice
`src/physics/layer2/regime_readiness.py` (new) — pure-over-DataFrame readiness core computing
all 4 metrics (coverage, separability, stability, covariance honesty) per axis of the six
regime-vector components, returning typed `ComponentReadiness` / `AxisReadiness` objects
with per-axis pass/fail flags against injectable `DEFAULT_THRESHOLDS`.

`tests/unit/physics/layer2/test_regime_readiness.py` (new) — 34 TDD tests, all green.

### Rework round 2 (commander-directed): leave-one-out tau_resid (stability detrend)
Same out-of-sample bug class as round 1, now in the **stability** metric. Running the dashboard
over the real 2023-Q store surfaced `tau_resid == 0.0000` for **every** axis → `stable` flag
trivially True everywhere (useless). Root cause: `_ctor_tau` detrended with an **in-sample**
self-weighted drift (`drift.predict` at the observed clocks); the random-walk's d=0 term pins
μ to each row's own value → `vals − μ ≈ 0` → `pool_random_effects(...).tau = 0` for ANY series,
even an erratic one. Fix:
- Factored a shared `_loo_drift_preds(vals, sigs, clocks) -> (mu_loo, sigma_pred_loo)` helper out
  of `_loo_z_scores` — one LOO drift implementation now used by BOTH the honesty z and the
  stability detrend.
- `_ctor_tau` now computes `tau_resid = pool_random_effects(vals − mu_loo, sigs).tau` from the
  **leave-one-out** predictions. Raw `tau` is unchanged. Edge handling matches the honesty metric:
  n≥3 LOO drift; n==2 predict-from-the-other-row; n==1 → can't detrend → `tau_resid = tau`
  (conservative: counts all spread as instability rather than fabricating stability).
- `stable` flag unchanged (`tau_resid ≤ within_σ`) — it's meaningful now.
- The degenerate `tau_resid ≈ 0` is gone: on an erratic series `tau_resid ≈ 0.71 (≫ σ)`, and on a
  clean development trend it correctly stays ≤ σ (development is not read as instability).

### Rework round 1 (commander-directed): leave-one-out covariance honesty
The covariance-honesty metric (4) was rebuilt from a **self-inclusive** drift prediction to a
**leave-one-out (out-of-sample)** one. The old form pinned μ to each row's own value when its σ
was tiny, so it structurally could not detect **over-claiming** (σ too small) — exactly the
metric's primary job. New formula, per constructor series, per row i:
- Fit drift on the OTHER rows (`fit_drift(vals_without_i, clock_without_i, sigmas_without_i)`),
  then `predict(round_idx_i)` → `(mu_loo_i, sigma_pred_loo_i)`.
- `z_i = (x_i − mu_loo_i) / sqrt(σ_i² + sigma_pred_loo_i²)`. The drift's own predictive sigma
  already carries the random-walk/development spread, so `+τ²` is **dropped** (no double-count).
  `tau` / `tau_resid` remain separate stability metrics (metric 3), unchanged.
- Edge handling: n≥3 → LOO drift; n==2 → predict from the single other point (degenerate
  `fit_drift` returns that point's value & sigma — still out-of-sample); n==1 → skipped, no z.
- New interpretation (documented in docstrings): `zstd ≈ 1` calibrated, `zstd > 1` over-claiming,
  `zstd < 1` under-confident. The `calibrated` flag is `zstd ≤ zstd_go (1.3)`.

Implemented as `_loo_z_scores(...)` (now sharing `_loo_drift_preds`). `_axis_readiness` was
refactored (helpers `_separability`, `_ctor_tau`, `_aggregate_z`, `_stability_and_honesty`) to
stay under the project's simplification-limits complexity/length caps after the change.

## Scope
**Files changed:**
- `src/physics/layer2/regime_readiness.py` (new, 522 lines)
- `tests/unit/physics/layer2/test_regime_readiness.py` (new, 610 lines)
- `.agent-work/512/g1-implementer-plan.json` (new, engine checklist)

**Specific exclusions touched:** No. `pooling.py`, `pool_driver.py`, `estimate_store.py` were
read but not modified. No evo, no I/O, no plotting, no GO/NO-GO verdict.

## Behavior changed
Yes — new module adds:
- `compute_readiness(df, *, thresholds=DEFAULT_THRESHOLDS) -> dict[str, ComponentReadiness]`
  composing `fit_two_way`, `pool_random_effects`, `fit_drift`, `_cov_list` into one callable
  readiness readout over the five-view estimate store.
- `DEFAULT_THRESHOLDS` named injectable constant; `ReadinessThresholds` dataclass.
- `AxisReadiness` and `ComponentReadiness` typed return dataclasses.

## Map Impact

- **Structural anchors touched:** `struct:physics.layer2` — new `src/physics/layer2/regime_readiness.py` added. Imports (read-only) from `pooling.py` (`fit_two_way`, `pool_random_effects`, `fit_drift`) and `estimate_store.py` (`_cov_list`).
- **Capabilities added:** New readiness readout over the five-view estimate store (the C3 characterization gate). Composes pooling seams; adds coverage / param-pair separability / covariance honesty that were not previously surfaced in one callable.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored; grep confirmed zero evo imports in the new file. Honest covariance: param_pair_corr reads the real 2×2 blob off-diagonal, never diagonal σ alone.
- **Decision candidates / resolved decisions:** `DEFAULT_THRESHOLDS` thresholds are named, injectable constants (not buried magic numbers) as the handoff specified. The threshold values themselves (`frac_team_go=0.15`, etc.) are implementer-authority defaults from the handoff; rubric tuning is a future decision for the G3 gate.
- **Claims/evidence produced:** `frac_team` per axis is the headline output; tests verify recovery matches `fit_two_way` directly. Can re-measure the #492-era "constructors not separable, frac_team ≤ 3%" claim.
- **Trust limitations / drift found:** BOTH out-of-sample metrics are now leave-one-out. (1) The covariance-honesty z is leave-one-out, so over-claiming (σ too small) is detectable — the C3 calibration check's primary job; the drift's predictive sigma slightly over-covers at small n, so calibrated data lands at `zstd ≈ 0.7` not exactly 1 (the `zstd_go=1.3` threshold accommodates this). (2) **(Round 2)** `tau_resid` is now leave-one-out detrended; the prior in-sample detrend produced `tau_resid ≈ 0` for every axis on the real 2023-Q store (trivially "stable"). Both share one `_loo_drift_preds` implementation. For G3 rubric tuning: the `stable` flag is `tau_resid ≤ within_σ`, now a real discriminator.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes — red phase confirmed (ImportError) before implementation was written; green phase achieved in one pass (2 test fixes needed after initial run; see Workflow Feedback).

## Evidence

```bash
py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q
```

**Result:** pass — 34 passed in 2.87s (after rework round 2)

Also ran the project simplification-limits gate (CREW_CONTEXT review blocker):
```bash
py -m src.utils.simplification_limits --paths src/physics/layer2/regime_readiness.py tests/unit/physics/layer2/test_regime_readiness.py
```
**Result:** PASS (2 files checked).

Planted-value recovery note:
- `frac_team` recovery: balanced 2×6 grid, RBR=3.0 / Ferrari=2.0, no noise.
  `fit_two_way` direct call on same valid rows returns frac_team ≈ 1.0.
  `compute_readiness` returns same to within abs≤0.02. Test: `test_frac_team_recovery_matches_fit_two_way_directly` — PASSED.
- `τ` recovery: single-constructor fixture, vals=[3.0, 3.0, 3.5, 3.5], sigma=0.05.
  `pool_random_effects` direct call returns τ ≈ 0.569 (DL formula, analytically verified).
  `compute_readiness` returns same to within abs≤0.05. Test: `test_stability_tau_recovery_matches_pool_random_effects` — PASSED.
- `param_pair_corr` recovery: planted blob [[0.0025, 0.001], [0.001, 0.0009]].
  Expected corr = 0.001 / sqrt(0.0025 × 0.0009) ≈ 0.6667 (exact formula).
  `compute_readiness` returns same to within abs≤1e-6. Test: `test_param_pair_corr_matches_analytical_formula` — PASSED.
- z-std (LOO, bidirectional — the rework's point): single-constructor n=8, seed=7, magnitudes
  verified empirically and locked into deterministic tests.
  - **Over-claim DETECTED (the key new test):** scatter≈0.3, σ planted 0.02 → `zstd ≈ 1.98 > 1.5`.
    Regression-guard confirmed: the OLD self-inclusive formula on the same data gives
    `zstd ≈ 0.026` (would *fail* the `>1.5` guard). Test: `test_zstd_high_when_overclaiming_REGRESSION_GUARD`.
  - **Calibrated ≈ 1:** σ matched to scatter (both 0.3) → `zstd ≈ 0.74` (in band [0.5, 1.6]).
    Test: `test_zstd_near_one_when_calibrated`.
  - **Under-confident:** σ=10 ≫ scatter → `zstd ≈ 0.022 < 0.5`. Test: `test_zstd_low_when_sigma_underconfident`.
  - n==2 degenerate out-of-sample and n==1 skip both green.
- tau_resid (LOO detrend — round-2 fix) discriminates real instability:
  - **Unstable DETECTED (the key new test):** erratic series `[3.0,3.6,2.5,3.5,2.4,3.55,2.55,3.5]`,
    σ=0.05 → `tau_resid ≈ 0.711 ≫ within_σ=0.050` → `stable=False`. Regression-guard confirmed:
    the OLD in-sample formula gives `tau_resid = 0.0000` → `stable=True` (the bug seen on the real
    2023-Q store). Test: `test_tau_resid_large_and_unstable_for_erratic_series_REGRESSION_GUARD`.
  - **Stable development:** clean linear trend + noise within σ (slope 0.05/round, noise 0.02,
    σ=0.15, seed=11) → `tau_resid ≤ within_σ` → `stable=True` (development not read as instability).
    Test: `test_tau_resid_small_and_stable_for_clean_development_trend`.
  - n==1 → `tau_resid == tau` fallback. Test: `test_tau_resid_n1_falls_back_to_tau`.

### What tau_resid / stable now look like on the two fixtures (as requested)
| fixture | tau | tau_resid (LOO) | within_σ | stable | (old in-sample tau_resid) |
|---|---|---|---|---|---|
| over-claim (scatter 0.3, σ 0.02) | 0.221 | 0.238 | 0.020 | **False** | — |
| genuinely unstable (erratic, σ 0.05) | 0.523 | 0.711 | 0.050 | **False** | **0.0000 → stable=True (bug)** |

The over-claim fixture is *both* over-claiming (zstd 2.12) and genuinely unstable (its real scatter
≫ its tiny σ), so `stable=False` there is correct, not a false alarm. The degenerate `tau_resid ≈ 0`
is gone.

## TDD evidence, if required

- Failing test observed: `ImportError while importing test module` — 0 items collected, exit 255
- Passing test observed: 34 passed in 2.87s (after rework round 2)
- Refactor while green: yes — extracted `_separability` / `_ctor_tau` / `_aggregate_z` /
  `_stability_and_honesty` helpers (round 1) and `_loo_drift_preds` (round 2, shared by the
  honesty z and the stability detrend), plus a `_ok_measurements` test helper, to satisfy the
  simplification-limits caps, with tests staying green throughout.
- Rework regression guards (TDD discipline), each confirmed to FAIL the old code and PASS the fix:
  - round 1 over-claim z-std: old self-inclusive `zstd ≈ 0.026` → new LOO `zstd ≈ 1.98`.
  - round 2 unstable tau_resid: old in-sample `tau_resid = 0.0000` → new LOO `tau_resid ≈ 0.71`.

## Docs/contracts touched
- None — new module, no existing contract changed.

## Assumptions

1. **Covariance blobs in DataFrame are already-parsed Python nested lists**, not JSON strings.
   This matches `estimate_store.load()` which applies `json.loads` before returning. `_cov_list`
   is called on them to normalise (it's idempotent on Python lists since it does
   `np.asarray(cov).tolist()`). No re-parsing needed.

2. **`round_idx` may be None.** Handled by falling back to row position index for clock ordering
   (does not affect correctness; drift just uses row order).

3. **frac_team is computed once per axis, not per component.** The handoff describes it as
   "per scalar sub-axis" which is what the implementation does. slow_corner_grip and
   fast_corner_grip each get their own frac_team from fit_two_way on their respective value column.

4. **param_pair_corr is shared across slow/fast_corner_grip.** Both components reference
   `lateral_covariance` (the handoff says "param-pair for the two lateral axes ↔ blob
   lateral_covariance"). The same off-diagonal correlation is returned for both component entries.

5. **(Superseded by rework round 1.)** The z-std denominator no longer uses `τ` at all. After
   the LOO rebuild it uses the drift prediction's own out-of-sample sigma:
   `sqrt(σ_i² + sigma_pred_loo_i²)`. `τ` and `τ_resid` remain reported as separate stability
   metrics (metric 3) and are not mixed into the calibration z.

## Stop conditions hit
- None.

## Out-of-scope observations

1. **(RESOLVED in rework round 1.)** The original self-inclusive z-std could not detect
   over-claiming (σ too small). The commander escalated this from a triage item to a must-fix;
   it is now fixed via the leave-one-out formula (`_loo_z_scores`), with a dedicated regression
   guard test proving over-claiming is now detectable. No longer an open observation.

1b. **(RESOLVED in rework round 2.)** The same in-sample overfit trap was present in the stability
   metric's `tau_resid` (in-sample detrend → `tau_resid ≈ 0` for every axis on the real 2023-Q
   store → `stable` trivially True). Fixed via leave-one-out detrending (shared `_loo_drift_preds`),
   with a regression-guard test proving an erratic series is now flagged unstable. No longer open.

2. **`frac_team ≤ 3%` claim re-verification:** The module is wired to do this — compute_readiness
   on the 2023-Q store will surface frac_team per component. This is G2 work (dashboard run),
   not wired here.

3. **`coast` component is diagnostic:** The handoff marks coast as "minor/diagnostic". The module
   treats it identically to other components; a flag/marker distinguishing diagnostic from primary
   components may be useful in the G3 synthesis gate.

## Workflow Feedback

- **Handoff gaps:** The original handoff prescribed **self-inclusive** drift predictions in BOTH the
  covariance-honesty z (`μ_pred_i = DriftFit.predict(round_idx_i)`, `sqrt(σ_i² + τ²)`) AND, implicitly,
  the stability `tau_resid` detrend ("remove the fitted trend, recompute residual spread"). Both forms
  structurally fail for the same reason: `DriftFit.predict` includes the target session and (with small
  σ) pins μ to its own value, so the residual collapses to ≈0 — masking over-claiming (round 1) and
  fabricating stability (round 2). These surfaced as two separate rework rounds. **The single durable
  lesson worth baking into the handoff template: any residual-based diagnostic over a self-weighted
  smoother MUST be leave-one-out (out-of-sample); in-sample residuals look good by construction.** Had
  the round-1 fix message flagged that the same trap applied to `tau_resid`, round 2 would have been
  avoided. Both corrected specs were precise and directly implementable.

- **Context rediscovered:** `DriftFit.predict` semantics (self-inclusive; `d=0` term dominates when σ
  is tiny; `predict` returns the MEAN's sigma, not a new-observation predictive sigma) had to be read
  from `pooling.py`. The last point matters: because `sigma_pred_loo` is the mean's uncertainty, the LOO
  denominator slightly over-covers at small n, so calibrated data sits at `zstd ≈ 0.7`, not 1.0. Captured
  in the result so G3 rubric tuning inherits it rather than rediscovering it.

- **Instructions improvised around:** The IMPLEMENTER_PLAN template has no explicit "rework round" gate.
  I drove the rework by `reopen`-ing the engine's `m2-implement` and `m3-verify` gates (rework 1/3 each),
  which is the engine-sanctioned mechanism and worked cleanly. The simplification-limits check is a
  CREW_CONTEXT review blocker but was not a postcondition in my plan; I ran it manually after the change
  and refactored to pass it. A future implementer plan for this repo should bake the simplification-limits
  command into a postcondition so the engine enforces it.

- **What would have made this easier:** (1) The handoff naming the honesty check as explicitly
  out-of-sample from the start would have avoided a rework round. (2) A note in CREW_CONTEXT-aware plan
  templates wiring `simplification_limits --paths` as a gate postcondition.
