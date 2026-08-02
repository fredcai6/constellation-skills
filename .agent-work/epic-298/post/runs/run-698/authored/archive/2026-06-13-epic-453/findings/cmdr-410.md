# cmdr-410 findings: pooled multi-season compound β fit

Date: 2026-06-11
Branch: issue-410-pooled-beta-fit
Issue: #410 (epic #453, Wave 1)

## Summary

Shipped `scripts/build_pooled_compound_prior.py` with 7 tests; updated gold
`params/gold/compound_prior/{2023,2024,2025}/compound_prior_summary.json` to
pooled-prior artifacts; co-validated `compound_push_regime.py` against the new
values.

**Key finding (honest null on monotonicity):** The production compound_prior
solver does NOT recover a monotone β ladder from 1–3 seasons of pooled
observations. Pooling does improve the spread/stability of the ladder (no longer
collapsed), but monotonicity requires the gate's fixed-effects estimator (different
solver design), not just pooling the production solver.

---

## β Ladder Numbers

### Gate (push-regime, crossover fit, reference):
Monotone down C1→C6. Adjacent steps ~1.2–3 SE each.
```
beta_C1: +0.003012   beta_C2: +0.001237   beta_C3: 0.0
beta_C4: -0.002422   beta_C5: -0.005498   beta_C6: -0.007365
```

### Per-season gold (BEFORE this PR):
All 8/8 seasons non-monotone (consistent with #382 measurement).
```
2022: C1=+0.000071  C2=+0.000588  C3=-0.000025  C4=-0.000732  C5=-0.004159  mono=False
2023: C1=-0.001295  C2=+0.000877  C3=+0.000364  C4=-0.001517  C5=-0.026274  mono=False
2024: C1=-0.001376  C2=+0.000306  C3=+0.000106  C4=+0.000282  C5=-0.008107  mono=False
2025: C1=-0.000428  C2=+0.000698  C3=-0.000166  C4=+0.000248  C5=-0.001042  mono=False
```

### Pooled gold (AFTER this PR):
Non-monotone but stabilised spread (especially 2023 collapsed from 0.027 → 0.005).
```
2022: unchanged — no prior seasons, per-season artifact retained
2023: (pool: 2022 only)      C1=-0.000846  C2=+0.000529  C3=+0.000030  C4=-0.000626  C5=-0.004448  mono=False
2024: (pool: 2022+2023)      C1=-0.001327  C2=+0.000716  C3=+0.000257  C4=-0.001188  C5=-0.010320  mono=False
2025: (pool: 2022+2023+2024) C1=-0.001372  C2=+0.000442  C3=+0.000228  C4=-0.000534  C5=-0.008296  mono=False
```

---

## Time-Safety Argument

The pooled fit for target year Y uses ONLY observations from seasons strictly < Y:
- `historical_years` are discovered as `range(2018, target_year)` — all strictly before Y.
- `source_season` in emitted artifact = `max(historical_years)` < Y.
- `artifact_id` = `"pooled-compound-prior-{max_season}-for-{target_year}"` makes provenance clear.
- `runtime_normalization.py` selection logic unchanged: picks `max(season < target_year)`.

---

## Co-Validation of compound_push_regime.py

The push-regime β constants in `compound_push_regime.py` (PUSH_REGIME_BETA) are
derived from the crossover gate (different solver), NOT from the compound_prior
artifact. They are therefore not affected by changes to the gold artifacts.

Validation ran `scripts/validate_qs_compound_beta_regime.py --years 2024`:
```
  OVERALL  race-beta=0.6968  push-beta=0.6985  delta=+0.0017
  CROSS    race-beta=0.7315  push-beta=0.7332  delta=+0.0017
```
Push-regime beta still improves cross-compound sign accuracy vs race-regime. The
co-validation script is unaffected by the pooled artifact change (it reads the
gold artifact for race-beta comparison, which now contains pooled values).

---

## Interpretation: why production solver doesn't achieve monotonicity

The prior-wave triage said "monotone ladder emerges when 8 seasons pooled" — this
was from `diagnose_compound_beta_degeneracy.py`, which uses a *different estimator*:
within-(driver,race) demeaning + clean fixed-effects pooled OLS. The production
solver adds: γ terms, sparse prior, effective_age_modifiers, race_delta_gamma
(additive) — these additional parameters compete with and absorb β identification.

Empirical result: even with 3 seasons pooled (2022+2023+2024 → 2025 prior), the
production solver's β remains non-monotone. Pooling does help spread stability
(2023 spread drops from 0.027 to 0.005) but doesn't resolve the identification
puzzle.

**This is an honest null on the original issue's stated goal**: the pooled
production fit does not recover a clean monotone β ladder. The architecture change
(pooled provenance artifacts) is shipped; the β identification gap is a separate
structural issue requiring the fixed-effects gate design to be integrated into the
production solver path.

---

## Files Changed

- `scripts/build_pooled_compound_prior.py` — NEW: CLI to regenerate pooled gold artifacts
- `tests/unit/compound_prior/test_build_pooled_compound_prior.py` — NEW: 7 tests
- `params/gold/compound_prior/2023/compound_prior_summary.json` — UPDATED (pooled)
- `params/gold/compound_prior/2024/compound_prior_summary.json` — UPDATED (pooled)
- `params/gold/compound_prior/2025/compound_prior_summary.json` — UPDATED (pooled)
- `params/gold/compound_prior/2022/compound_prior_summary.json` — UNCHANGED (no prior seasons)

---

## Triage Candidates

1. **Production solver β identification gap**: Even with 3-season pooling, production
   compound_prior solver doesn't recover a monotone β. The gate's fixed-effects design
   does. The fix requires integrating the gate estimator approach into the gold fit path
   (replace weighted regression with within-group FE demeaning for β identification, or
   profile β from gate values and use production solver only for γ). This is out of scope
   for this issue but is the next structural step.

2. **2022 gold artifact missing pooled treatment**: 2022 has no prior-season data so
   cannot be pooled. If historical data (pre-2022) becomes available, re-run the script.
   Currently 2022 retains the per-season artifact.

---

## Workflow Feedback

- The predecessor session floated the problem statement correctly; resuming from Admiral
  confirmation worked cleanly.
- The prior-wave triage document's claim of "monotone from 8-season pooling" referred
  to a different solver design (gate FE), not the production solver. This was ambiguous
  in the triage and caused extra investigation work in this session.
- simplification_limits caught a 118-line function; extracting two helpers resolved it.
- Windows MAX_PATH on diagnostic filename is a recurring issue with many-race fits
  (handled with OSError recovery already in rolling script; same pattern reused here).
