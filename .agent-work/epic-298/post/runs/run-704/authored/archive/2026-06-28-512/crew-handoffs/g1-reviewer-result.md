# Review Result

## Assigned Gate
`g1-review` — Readiness core module + tests (issue #512, C3 regime-capability readiness)

## Result
`APPROVE`

Verdict: APPROVE

---

## Delta Re-review (rework 2, commit `0116ec93`) — 2026-06-28

**Verdict: APPROVE**

The **stability** metric carried the same in-sample-overfit bug class previously fixed on the honesty metric: `_ctor_tau` detrended `tau_resid` with an in-sample self-weighted drift, so `vals − μ ≈ 0` for any series (the `d=0` term pins μ to each row's own value) → `tau_resid=0.0000` everywhere on the real 2023-Q store → `stable` flag trivially True. Reworked to leave-one-out. All delta checks pass:

- **Shared LOO helper, no divergent logic:** `_loo_drift_preds(vals, sigs, clocks) -> (mu_loo, sigma_pred_loo)` was factored out of `_loo_z_scores` and now backs BOTH the covariance-honesty z AND `_ctor_tau`'s `tau_resid`. Confirmed genuinely leave-one-out: `keep = idx != i`, fit on the other rows, predict row i. One implementation, no duplication.
- **Stability regression-guard is non-tautological (independently verified):** REPL spot-check on the erratic fixture `[3.0, 3.6, 2.5, 3.5, 2.4, 3.55, 2.55, 3.5]`, σ=0.05 → NEW LOO `tau_resid=0.7106` > within_σ 0.05 → `stable=False`; OLD in-sample `tau_resid=0.0000` ≤ 0.05 → would false-pass `stable=True`. Matches the implementer's claimed ≈0.71 / 0.0000 exactly. The guard genuinely fails the old code and passes the fix.
- **Development not read as instability:** dev-trend fixture (seed=11, slope 0.05, noise within σ=0.15) → `tau_resid=0.0000` ≤ 0.15 → `stable=True`. A clean trend is perfectly predictable out-of-sample, so LOO residuals stay small. The metric discriminates erratic (0.71) from clean development (0.00).
- **Edge handling:** n==1 → `_ctor_tau` returns `(tau, tau)` (conservative fallback, no crash); `test_tau_resid_n1_falls_back_to_tau` passes. n==2 predict-from-other preserved.
- **Raw `tau` unchanged** (diff confirms only the `tau_resid` branch changed).
- **No regressions on prior constraints:** re-grepped — no evo/latent/compound import, no `src.data` dependency, no GO/CONTEXTUAL/NO-GO verdict string. Tests still 100% synthetic.
- **Tests:** `py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q` → 34 passed (was 31), run independently.

**Delta scope note (out of g1-review scope):** A G2 dashboard commit (`5f9985b1`, `regime-capability dashboard + 2023-Q readiness run`) landed on the branch interleaved between the two g1 rework commits. It did NOT touch the g1 in-scope files (`regime_readiness.py`, `test_regime_readiness.py`) — confirmed by `git show --stat`. It is a separate gate's work and was not re-reviewed here.

**Delta workflow feedback:** The coordinator message described the delta crisply and its numbers (LOO ≈0.71, in-sample ≈0.0000, tests 34) all reproduced exactly — a clean, verifiable delta handoff. One note: the docstring in the original code asserted "self-inclusive prediction is correct here" for `tau_resid`; that claim was wrong (same overfit trap as the honesty metric). Worth a durable lesson: any in-sample detrend/residual against a self-weighted drift collapses to ≈0 and must be leave-one-out — this bug class has now appeared twice in this module.

---

## Handoff compliance
The handoff specified: `compute_readiness(df, *, thresholds=DEFAULT_THRESHOLDS) -> dict[str, ComponentReadiness]` computing 4 metrics per axis (coverage, separability, stability, LOO covariance honesty), typed `AxisReadiness`/`ComponentReadiness` return objects, no I/O, no plotting, no GO/CONTEXTUAL/NO-GO verdict. Implementation satisfies all of this exactly. One rework round (LOO rebuild, commander-directed) was completed. 31 TDD tests pass. All close criteria verified.

## Scope drift
Scope is clean. Changed files: `src/physics/layer2/regime_readiness.py` (new), `tests/unit/physics/layer2/test_regime_readiness.py` (new), `.agent-work/512/*` (workbench, expected). Excluded files confirmed untouched (git diff main...HEAD on `pooling.py`, `estimate_store.py`, `pool_driver.py` returned empty). `fit_evidence.py` not imported. No DB/file I/O, no matplotlib, no CLI, no grip-evolution (#511) or traction (#557) work, no evo wiring.

## Evidence verdict
31 tests run independently and pass (`py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q → 31 passed in 1.38s`). Tests include L1 analytical recovery (frac_team matches `fit_two_way` directly, tau matches `pool_random_effects` directly, param_pair_corr matches formula analytically, LOO zstd bidirectional) and L3 degenerate cases (all-error, single session, zero variance, missing blobs, partial blobs). Behavior-change evidence is sufficient.

## Code/doc quality
Minimal, maintainable, project-rule compliant. Docstrings document the LOO formula and design rationale (including the deliberate choice to use self-inclusive drift for stability vs LOO for calibration honesty). Helper extraction (`_separability`, `_ctor_tau`, `_aggregate_z`, `_stability_and_honesty`) satisfies the project's simplification-limits cap. Naming conventions consistent with surrounding codebase. No magic numbers. Implementer reports simplification-limits gate PASS; consistent with the refactor.

## Map impact verdict

- **Evidence supports claimed change:** Yes. frac_team per component is surfaced; param_pair_corr reads the real 2×2 off-diagonal blob; tau + tau_resid are both reported; LOO honesty is genuinely out-of-sample.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored (confirmed by grep). Honest covariance first-class (real 2×2 blobs, not diagonal σ). Thresholds injectable as named constant.
- **Notes match the diff:** Yes. Structural: `struct:physics.layer2` receives `regime_readiness.py`. Read-only imports from `pooling.py` and `estimate_store._cov_list` match the diff. Capability: new readiness readout over five-view store — accurate.
- **Decision candidates surfaced:** `DEFAULT_THRESHOLDS` values are implementer-authority defaults; rubric tuning noted as a future decision for G3. Appropriately surfaced.
- **Durable context routed:** Implementer notes that calibrated data lands at `zstd ≈ 0.7` (not 1.0) due to mean-uncertainty in small-n LOO sigma, and that the `zstd_go=1.3` threshold accommodates this. This is durable context G3 rubric tuning needs. Routed via the implementer result.

## Reconciliation check
No architecture drift needing Commander reconciliation. The change is additive (new module, read-only consumers of existing seams). Cartographer may want to record `regime_readiness.py` in the structural map at G3 closeout.

## Blockers
None.

## Out-of-scope observations

1. **Self-inclusive zstd number discrepancy:** The implementer reported self-inclusive zstd ≈ 0.026 for the regression-guard scenario. Independent spot-check gives 0.20 (same data, same code path, seed=7). The guard threshold is 1.5, so 0.20 still clearly fails — the guard is genuine. The discrepancy is likely from a prior code state or different DriftFit behavior. Not a blocker; flagged for Commander awareness.

2. **`_cov_list` is a private seam (`_` prefix in `estimate_store`):** The implementation imports `from src.physics.layer2.estimate_store import _cov_list`. This is intentional (the handoff lists it as a named seam) but Cartographer may want to promote `_cov_list` to a non-private export or document it as a stable internal seam.

3. **`coast` component diagnostic status:** The module treats `coast` identically to primary components. The implementer notes a marker distinguishing diagnostic from primary components may be useful in G3. Triage candidate for G3 or a follow-on issue.

## Workflow Feedback

- **Handoff gaps:** The handoff was precise and complete. One minor gap: the LOO vs self-inclusive distinction in the close criteria says "the prior self-inclusive formula would have failed it (implementer reports old≈0.026 vs new≈1.98)." My independent spot-check gives 0.20 (self-inclusive) and 2.12 (LOO) — different numbers, same direction. The handoff could say "would fail the guard" without pinning specific numbers, since the exact value depends on the code state at measurement time.

- **Context rediscovered:** Had to read `DriftFit.predict()` source in `pooling.py` to confirm the self-inclusive formula pins mu close to each point (weight 1/sigma_i^2 dominates at d=0). This confirmed the old formula structurally cannot detect over-claiming. The handoff could carry a one-liner on this: "DriftFit.predict is a weighted mean; at d=0, tiny sigma pins the weight to the row's own value."

- **Instructions improvised around:** The engine `append` verb added r6-r14 checks from the close criteria to the base survey template's 6 items. This is the documented mechanism for per-rule checks in the reviewer skill and worked cleanly.

- **What would have made this easier:** Carrying the self-inclusive behavioral description (mu ≈ x_i when sigma is tiny and d=0) in the handoff would have saved reading pooling.py internals. Otherwise the handoff was very well structured — the specific called-out items (LOO guard, 2×2 blobs, frac_team, tau+tau_resid, verdict check) mapped directly to checkable assertions.

## Return status
`complete`
