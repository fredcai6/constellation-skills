# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g4-review` — Static-latent separability at manageable uncertainty (issue #512, C3)

## Survey State Location
`.agent-work/512/g4-review/review.json` (under the issue workbench, never the worktree root).

## What Was Implemented (commit `c05b8ec5`)
Extension to `src/physics/layer2/regime_readiness.py`: a static-latent separability readout — per
constructor per axis, RE-pool the per-session values into a static `mu_c ± sigma_mu_c` (dev
separated via `fit_drift`), then measure car separability **relative to that static estimate's own
uncertainty**: `separation_ratio = stdev({mu_c}) / median({sigma_mu_c})`, `sep_F`, a `manageable`
flag vs `DEFAULT_THRESHOLDS.separation_ratio_manageable` (=2.0), per-car `(mu_c, sigma_mu_c, n_c)`,
and a per-axis `setup_conflated` flag (power clean; drag/aero conflated). Dashboard renders a new
"Static-latent separability" section + re-run over the real store. Tests 42 core + 26 dashboard.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-512
git show c05b8ec5 --stat
git diff main...HEAD -- src/physics/layer2/regime_readiness.py tests/unit/physics/layer2/test_regime_readiness.py scripts/regime_capability_dashboard.py tests/unit/physics/layer2/test_regime_capability_dashboard.py
sed -n '/Static-latent/,/##/p' reports/physics/regime_capability_2023Q.md
```

## Task Statement
Test the pooling thesis the additive `frac_team` under-tested: does pooling a car's track-viewpoints
recover a STATIC car latent separable at a *manageable* uncertainty (not full recovery)?
Full handoff: `.agent-work/512/crew-handoffs/g4-implementer-handoff.md`.

## Close Criteria (each → a check)
- **The separation metric is vs the static estimate's OWN uncertainty**, NOT vs circuit variance
  (this is the whole point — distinct from `frac_team`). Verify `separation_ratio = stdev(mu_c) /
  median(sigma_mu_c)` and `sigma_mu_c` is the RE pooled-mean uncertainty (`pool_random_effects`).
- **Synthetic fixtures genuinely discriminate:** a planted separable static latent (distinct mu_c,
  small sigma) → high ratio; a non-separable one (same mu, OR huge per-session sigma) → low ratio.
  Spot-check the planted-vs-recovered numbers (impl reports separable≈31, same-mu≈0.40, huge-σ≈0.78).
- **Development handled:** a developing-car fixture detrends (tau_post < tau_pre on that fixture).
- **Degenerate guard:** the real-store `braking/brake_aero_decel` ratio 9.24σ is correctly
  attributable to a degenerate tau≈0 (near-zero sigma_mu) — confirm it's flagged/explained, not a
  real separation (a tiny denominator inflates the ratio).
- **setup_conflated** is per-AXIS (power False, drag/aero True) and documented.
- Backward-compatible: existing G1/G2 metrics, flags, and tests unchanged.
- No evo import; tests data/-independent; dashboard renders the section from the core; no GO/NO-GO verdict.
- `py -m pytest tests/unit/physics/layer2/test_regime_readiness.py tests/unit/physics/layer2/test_regime_capability_dashboard.py -q` green (68).

## Allowed Scope / Exclusions
Scope: `regime_readiness.py`, its test, the dashboard + its test, the refreshed `.md`. No changes to
`pooling.py`/`estimate_store.py`; no evo import; no verdict; no #511/#557 work.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/regime_readiness.py` (extend); `pooling.pool_random_effects`/`fit_drift`; dashboard.
- **Capability:** static-latent recovery test (distinct from additive frac_team).
- **Constraints:** `constraint:physics_region_no_evo_import`; manageable-uncertainty bar.
- **Evidence:** power separation_ratio 1.16σ (NOT manageable); only coast-rolling (diagnostic) + degenerate braking_aero clear 2σ; static-power ordering within overlapping σ → don't over-read.

## Evidence Produced
68 tests green; real-store static-separability section in `.agent-work/512/crew-handoffs/g4-implementer-result.md`.

## Suggested Model Tier
`simple bounded` (Sonnet) — verify the metric is vs own-uncertainty + the fixtures discriminate + the degenerate guard.

## Stop Conditions
BLOCK if: separation is measured vs circuit variance (not own uncertainty), fixtures are tautological,
the degenerate 9.24σ is presented as a real separation, evo import / data-test dependency, or a verdict smuggled in.

## Return Format
REVIEW_RESULT: `Verdict: APPROVE`/`Verdict: BLOCK` (exact), per-check findings, blockers, out-of-scope observations, workflow feedback.
