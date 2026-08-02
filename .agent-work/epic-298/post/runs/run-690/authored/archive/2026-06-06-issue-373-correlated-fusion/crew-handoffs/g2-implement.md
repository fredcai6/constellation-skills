# Implementer Handoff — G2: Correlated-covariance fusion (variant A) + cheap-B + R estimation

You are a fresh implementer crew. Work ONLY from this handoff. Repo: f1Brainz (Windows; `py`
not `python`). Branch `constellation/issue-373-correlated-fusion`; cwd = worktree root. Set
`PYTHONIOENCODING=utf-8` before any python command.

G1 already built a trusted numpy harness at `scripts/fusion_replay/` (records.py, baseline.py
with `_fuse_baseline_numpy`, scoring.py) and `tests/unit/evo_predictor/test_fusion_replay_harness.py`.
READ those first — you build on them.

## Gate
g2

## Task
Add an OPT-IN correlated-covariance fusion variant (A), a cross-module correlation-matrix (R)
estimator, the constructor<->driver cheap-B special case, and ablation hooks (R=I, shrinkage
sweep). Production `fuse_module_fields_ordered` must stay source-compatible AND behaviorally
UNCHANGED (no call-site flips to A in this issue). The decisive correctness anchor: **at R=I,
variant A must reproduce its baseline reference to <=1e-9** (unit-tested on a synthetic fixture).

## The math (read carefully — the R=I identity is load-bearing)

The production baseline (`fuse_module_fields_ordered`) does a SEQUENTIAL Gaussian precision
update over the task's 4 aligned driver-space observations of the latent driver pi vector:
  P_post = P_prior + sum_m inv(obs_cov_m)        (order-invariant)
  mean   = inv(P_post) @ (P_prior@m_prior + sum_m inv(obs_cov_m)@obs_mean_m)
where obs_cov_m is the FULL n x n covariance (covariance_scale*sigma_pi + jitter*I + tension*I),
prior is m_prior=0, P_prior=inv(I*prior_sigma^2).

Variant A treats R as a 4x4 CROSS-MODULE error correlation and combines PER ENTITY i:
each module m gives a scalar observation y_mi = obs_mean_m[i] of that entity's latent pi_i,
with per-entity std sigma_mi = sqrt(obs_cov_m[i,i]). The 4 observations of entity i have joint
covariance Sigma_i = D_i R D_i, D_i = diag(sigma_1i..sigma_4i). GLS combine per entity:
  prec_i  = 1^T Sigma_i^{-1} 1            (scalar precision from the 4 modules)
  ybar_i  = (1^T Sigma_i^{-1} y_i) / prec_i
then fold with the scalar prior (prior precision 1/prior_sigma^2, prior mean 0):
  post_prec_i = 1/prior_sigma^2 + prec_i
  post_mean_i = (prec_i*ybar_i) / post_prec_i
  post_var_i  = 1/post_prec_i
Posterior pi = [post_mean_i], posterior sigma_pi = diag([post_var_i]).

IMPORTANT IDENTITY FACTS (you must respect these):
- At R=I, Sigma_i is DIAGONAL, so prec_i = sum_m 1/sigma_mi^2 = sum_m 1/obs_cov_m[i,i].
  This equals the baseline's accumulated precision ONLY on the DIAGONAL — because the baseline
  uses the FULL n x n obs_cov, its per-entity posterior is coupled across entities, whereas
  variant A is per-entity-diagonal by construction (R is cross-module, not cross-entity).
- THEREFORE the correct R=I reference for variant A is the DIAGONALIZED baseline: the same
  precision update but with each obs_cov_m replaced by diag(diag(obs_cov_m)) and the prior
  kept as I*prior_sigma^2 (already diagonal). Implement a helper
  `_fuse_baseline_diagonal_numpy(...)` (in the harness) that does the sequential update using
  ONLY the diagonals; variant A at R=I MUST match THIS to <=1e-9. Document this clearly: A is a
  per-entity model; its identity anchor is the diagonalized baseline, not the full-matrix one.
- ALSO compute and report (in the harness, for the measurement gate later) how much the
  full-matrix baseline differs from the diagonalized baseline on the synthetic fixture, so the
  modelling choice is transparent (a quick metric: max abs pi diff). This is evidence, not a gate.

## What to build (exact files)

1. `src/evo_predictor/fusion.py` — ADD a new pure function (production fuse_module_fields_ordered
   UNCHANGED — do not edit its body or signature):
   `fuse_module_fields_correlated(module_results, *, driver_ids, constructor_by_driver, config,
   correlation: np.ndarray)` returning a `FusedLatentField`. `correlation` is the 4x4 R indexed
   in `config.fusion_order` module order. It performs the per-entity GLS update above (align
   driver modules, project constructor modules exactly as the baseline does — reuse the existing
   `_align_driver_field_to_driver_ids` and `project_constructor_field_to_drivers`). Validate:
   R is (k,k) symmetric PSD with unit diagonal where k=len(enabled modules), R aligns to the
   enabled module order. At R=I it must reduce to the per-entity diagonal precision sum + prior.
   Keep it numpy. Add to `__all__`. Add a `diagnostics` dict noting fusion_mode="correlated_v1".
   NOTE: production default path is untouched; this function is exercised only by the harness.

2. `src/evo_predictor/fusion_training/_correlation.py` — NEW module: R estimation.
   - `estimate_cross_module_correlation(per_event_residuals, *, module_order, shrinkage) -> np.ndarray`
     where per_event_residuals is a list, one per event, of {module_name -> (residual vector,
     entity_ids)} with residual = module_pi - target_mu (caller computes; you standardize).
     Standardize residuals PER (event, module) (subtract mean, divide by std over that event's
     entities), then for each module PAIR accumulate standardized-residual products over their
     COMMON entities across all events, and form the kxk correlation R_hat. Shrink toward I:
     R = (1-shrinkage)*R_hat + shrinkage*I, clip to valid correlation (unit diagonal, symmetric).
     Handle: events with <2 entities (skip, count), modules missing target_mu (skip, count),
     disjoint entity sets (pairwise common-entity intersection). Return R plus a diagnostics dict
     (n_events_used, n_pairs_per_block, condition_number_before/after_shrinkage). NO torch, numpy
     (+ optional scipy) only. Represent skips EXPLICITLY in diagnostics; never impute.
   - `mask_correlation_to_block(R, *, module_order, keep_pairs) -> np.ndarray` — cheap-B helper:
     return a copy of R with all off-diagonal entries set to 0 EXCEPT the pairs in keep_pairs
     (each a frozenset/tuple of two module names). For cheap-B, keep_pairs = the two
     constructor<->driver same-evidence pairs (recent constructor<->recent driver, weekend
     constructor<->weekend driver). Diagonal stays 1.

3. `scripts/fusion_replay/variants.py` — NEW harness module wiring A + cheap-B + ablations:
   - `_fuse_baseline_diagonal_numpy(module_results, *, driver_ids, constructor_by_driver, config)`
     -> (pi, sigma_pi): the diagonalized-baseline reference described above.
   - `run_variant(module_results, *, driver_ids, constructor_by_driver, config, correlation)` ->
     FusedLatentField via `fuse_module_fields_correlated` (thin wrapper for the harness).
   - `cheapB_correlation(R, module_order, module_meta)` -> masked R using mask_correlation_to_block
     with the constructor<->driver same-evidence pairs derived from module_meta
     (entity_scope + evidence_source).
   - keep numpy-only.

4. `tests/unit/evo_predictor/test_fusion_correlated.py` — NEW tests:
   - **test_correlated_RI_equals_diagonal_baseline**: synthetic 4-module task (reuse the G1
     fixture style); build R=I (4x4); assert `fuse_module_fields_correlated` pi & sigma_pi match
     `_fuse_baseline_diagonal_numpy` to atol=1e-9.
   - **test_correlated_RnotI_differs**: with a non-trivial R (e.g. 0.8 on the constructor/driver
     block), assert the result DIFFERS materially from R=I (sanity: coupling changes the answer).
   - **test_estimate_correlation_recovers_planted**: generate residuals with a KNOWN cross-module
     correlation (e.g. simulate correlated standardized residuals), assert
     `estimate_cross_module_correlation` recovers it within tolerance (shrinkage=0) and that
     shrinkage moves R toward I (off-diagonals shrink) and improves conditioning.
   - **test_cheapB_masks_offblock**: assert mask_correlation_to_block zeros the recent<->weekend
     cross terms but keeps the constructor<->driver block.
   - **test_production_fusion_unchanged**: import fuse_module_fields_ordered and assert the
     existing G1 baseline test still holds (call it on the fixture; it must equal the real fn) —
     i.e. confirm you did not alter production behavior.
   - Seed all RNG. No real data/DB/network.

## Close Criteria (prove each)
- `py -m pytest tests/unit/evo_predictor/test_fusion_correlated.py tests/unit/evo_predictor/test_fusion_replay_harness.py -q` passes.
- `py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay" -q` passes (existing
  fusion suite stays green — production behavior unchanged).
- At R=I, variant A == diagonalized baseline to <=1e-9 (the test above).
- production `fuse_module_fields_ordered` body+signature unchanged (git diff shows only ADDED
  function(s) in fusion.py, no edits to the existing function).
- `py -m src.utils.simplification_limits --paths src/evo_predictor/fusion.py src/evo_predictor/fusion_training/_correlation.py scripts/fusion_replay tests/unit/evo_predictor/test_fusion_correlated.py` passes (fix/split if flagged).

## Allowed Scope
- EDIT (additively only): `src/evo_predictor/fusion.py` (ADD function + __all__ entry; do NOT
  change existing functions).
- CREATE: `src/evo_predictor/fusion_training/_correlation.py`, `scripts/fusion_replay/variants.py`,
  `tests/unit/evo_predictor/test_fusion_correlated.py`.
- READ: anything under src/evo_predictor/.

## Specific Exclusions
- Do NOT change the behavior or signature of `fuse_module_fields_ordered` or any existing
  production function. Do NOT flip any production/runtime call-site to the new variant.
- Do NOT touch quali-head / latent_power evidence-weighting code, `_correction.py`, or docs.
- Do NOT generate real records or run backtests (that is G3).

## Constraints
- numpy-only in harness + _correlation.py (scipy optional for linalg/stats); no torch.
- Missingness explicit (count skipped events/modules/entities); never impute target_mu.
- One canonical path; explicit input validation naming field/expectation/actual.
- R is a correlation matrix: symmetric, unit diagonal, PSD (after shrinkage). Validate.

## Verification Commands
```
py -m pytest tests/unit/evo_predictor/test_fusion_correlated.py tests/unit/evo_predictor/test_fusion_replay_harness.py -q
py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay" -q
py -m src.utils.simplification_limits --paths src/evo_predictor/fusion.py src/evo_predictor/fusion_training/_correlation.py scripts/fusion_replay tests/unit/evo_predictor/test_fusion_correlated.py
```

## Suggested Model Tier
sonnet (numerics-heavy; the R=I identity and correlation recovery need care).

## Authority
Commander decisions (do not re-litigate): variant A is per-entity GLS with Sigma_i=D_i R D_i;
its R=I identity anchor is the DIAGONALIZED baseline (documented), because R is cross-module not
cross-entity; production fusion default UNCHANGED; R estimated in standardized-residual space and
shrunk toward I; cheap-B = R masked to the constructor<->driver same-evidence block. If you find
a formulation where variant A reduces to the FULL-matrix baseline at R=I exactly, you MAY use it
instead — but you must prove the <=1e-9 identity and document the formulation either way.

## Stop Conditions
Stop and return if: you cannot achieve the R=I identity to 1e-9 against a clearly-documented
reference (report the residual and your formulation), achieving it requires changing production
behavior, or a close criterion cannot be met within scope.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed (full paths, noting fusion.py is
additive-only), test mode satisfied, exact verification command outputs (paste pytest +
simplification tails), the R=I identity residual achieved, the full-vs-diagonal baseline
difference observed on the fixture, assumptions, stop conditions hit, out-of-scope observations.
