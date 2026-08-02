# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g1-review` — Readiness core module + tests (issue #512, C3 regime-capability vector readiness)

## Survey State Location
`.agent-work/512/g1-review/review.json` (under the issue workbench, never the worktree root).

## What Was Implemented
New pure-over-DataFrame readiness core `src/physics/layer2/regime_readiness.py`:
`compute_readiness(df, *, thresholds=DEFAULT_THRESHOLDS) -> dict[str, ComponentReadiness]`,
computing 4 metrics per regime-vector component axis — coverage, car-vs-car separability
(`fit_two_way.frac_team`), cross-session stability (`pool_random_effects.tau` + drift-aware
`fit_drift` → `tau_resid`), and **leave-one-out** covariance honesty (`_loo_z_scores`:
`z_i=(x_i−μ_loo_i)/sqrt(σ_i²+σ_pred_loo_i²)`, drift fit excluding row i). Returns typed
`AxisReadiness`/`ComponentReadiness` with per-axis boolean flags vs `DEFAULT_THRESHOLDS`.
Tests: `tests/unit/physics/layer2/test_regime_readiness.py` (31, data/-independent synthetic).
A prior pass used a self-inclusive drift prediction that could not detect over-claiming; it was
reworked to leave-one-out (commit 431f6374).

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-512
git diff main...HEAD -- src/physics/layer2/regime_readiness.py tests/unit/physics/layer2/test_regime_readiness.py
git log --oneline main..HEAD
```

## Task Statement
Build the tested logic core for #512's characterization: the 4 readiness metrics per component,
composing existing pooling seams, honest covariance first-class (real 2×2 blobs for param-pair
separability), NO GO/CONTEXTUAL/NO-GO verdict (that's a later gate), measured-not-wired.
Full handoff: `.agent-work/512/crew-handoffs/g1-implementer-handoff.md`.

## Close Criteria (each → a review check)
- The **leave-one-out covariance-honesty** metric is genuinely out-of-sample: the drift
  prediction for row i excludes row i. **Critically: confirm the over-claim regression test
  actually guards** — it must assert `zstd` is large (>~1.5) when σ is planted too small, AND
  the prior self-inclusive formula would have failed it (implementer reports old≈0.026 vs new≈1.98).
  If you can, sanity-check this isn't a tautological test.
- Separability uses `pooling.fit_two_way().frac_team` on per-(constructor, round) values; the
  module can re-measure the #492-era "frac_team ≤ 3%" claim (frac_team surfaced per axis).
- Param-pair separability reads the **real 2×2 covariance blob** off-diagonal correlation
  (`cov01/sqrt(cov00·cov11)`), NOT diagonal σ.
- Stability reports both raw `tau` and drift-removed `tau_resid` (development not read as instability).
- Coverage = valid-row fraction per constructor (fit_status ok + finite value + finite/positive σ).
- Synthetic fixtures recover planted frac_team / τ / param-corr / z within tolerance (analytical L1) + degenerate cases (L3).
- `py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q` green.

## Allowed Scope
`src/physics/layer2/regime_readiness.py`, `tests/unit/physics/layer2/test_regime_readiness.py` (both new). Read-only consumers of `pooling.py` / `estimate_store._cov_list`.

## Specific Exclusions (flag if touched)
- No modification to `pooling.py` / `pool_driver.py` / `estimate_store.py`.
- No DB/file I/O, no matplotlib, no CLI (G2's job). No GO/CONTEXTUAL/NO-GO verdict (G3's job).
- No grip-evolution state (#511), no traction rebuild (#557), no evo wiring.

## Constraints the Implementation Must Respect (each → a check)
- `constraint:physics_region_no_evo_import` — verify zero `src.evo_predictor`/`latent_power`/`compound_prior` imports in the new file.
- Tests independent of `data/` (no real-DB read).
- Honest covariance first-class (real 2×2 blobs).
- Thresholds are a named injectable constant, not buried magic numbers.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — new `regime_readiness.py`; read-only `pooling.py`, `estimate_store._cov_list`.
- **Capability:** readiness readout over the five-view store.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; honest covariance.
- **Decision anchors:** `decision:c1_driver_utilization_design`. Decision pressure: rubric thresholds (named injectable constant — verify not buried).
- **Evidence expectations:** `frac_team` per component is the headline (re-measures the #492-era claim).
- **Map confidence flags:** `fit_evidence.py` is the OLD Layer-1 fit_store — confirm it was NOT imported (reuse idea only).

## Evidence Produced
`py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q` → 31 passed. Implementer's
bidirectional z evidence: over-claim zstd≈1.98 (>1.5 guard), old self-inclusive≈0.026, calibrated≈0.74, under-confident≈0.022. simplification-limits gate PASS. Full: `.agent-work/512/crew-handoffs/g1-implementer-result.md`.

## Suggested Model Tier
`simple bounded` (Sonnet) — precise close criteria; the one subtle check is the LOO honesty metric, called out explicitly above.

## Stop Conditions
BLOCK if: diff inaccessible, the over-claim guard test is tautological/ineffective, evidence
unverifiable, real covariance blobs not used, an evo import or data/ test dependency is present,
or a verdict was smuggled in.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
