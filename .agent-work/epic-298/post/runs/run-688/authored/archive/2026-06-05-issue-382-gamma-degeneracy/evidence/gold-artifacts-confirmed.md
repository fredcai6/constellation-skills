# Gold compound_prior artifacts — degeneracy CONFIRMED (read directly, no refit)

Source: `params/gold/compound_prior/{2018..2025}/compound_prior_summary.json` (committed production outputs).

## Production config (identical across seasons)
- `ridge_alpha = 1.0`  ← identical to RetroTruthConfig.lambda_ridge=1.0 (§1.3 ridge-dominance precedent)
- `sparse_prior_mode = support_aware_zero_shrinkage`, `sparse_prior_strength = 1.0`
- `reference_compound = C3` (gate used C3 too — so reference is NOT the difference)
- `accepted_compounds = [C1,C2,C3,C4,C5]` (no C6 in gold)
- `race_delta_gamma_mode = additive`
- `effect_space = normalized_fractional`
- `condition_number ≈ 6.1e4 (2022) / 7.1e4 (2024) / 9.9e3 (2025)` — well-posed, NOT rank-deficient (matches gate's 6.3e4)
- `solver_status = warning`

## β degeneracy — CONFIRMED
| yr | β_C1 | β_C2 | β_C3 | β_C4 | β_C5 | monotone-down? |
|----|------|------|------|------|------|----------------|
| 2022 | +0.000071 | +0.000588 | -0.000025 | -0.000732 | -0.004159 | NO (C1<C2) |
| 2024 | -0.001376 | +0.000306 | +0.000106 | +0.000282 | -0.008107 | NO (wrong-signed C1, C3<C4) |
| 2025 | -0.000428 | +0.000698 | -0.000166 | +0.000248 | -0.001042 | NO (jagged) |

Gate's clean ladder (2018-2025 pooled, single φ): C1 +0.0030 → C2 +0.0012 → C3 0 → C4 -0.0024 → C5 -0.0055. **Production β middle (C1..C4) is flat/jagged and ~5-10x smaller in spread than the gate's ladder, with wrong-signed C1.** Only C5 carries a clear (large) value.

## γ plateau — CONFIRMED and LOCALIZED to the isotonic projection
| yr | γ_C1 | γ_C2 | γ_C3 | γ_C4 | γ_C5 |
|----|------|------|------|------|------|
| 2022 | 0.00020829 | 0.00020955 | 0.00020955 | 0.00020955 | 0.00046422 |
| 2024 | 0.00010358 | 0.00010358 | 0.00010358 | 0.00010358 | 0.00037234 |
| 2025 | 0.00008424 | 0.00008424 | 0.00008424 | 0.00008425 | 0.00009898 |

**γ_C1=γ_C2=γ_C3=γ_C4 identical to ~8 decimals**, then C5 breaks free. This is the EXACT signature of `_isotonic_non_decreasing` (PAVA) pooling: when the unconstrained γ ladder is non-monotone (which the gate proved it is), the monotone projection merges the offending adjacent values into a single pooled block → a flat plateau across C1-C4. H2 is essentially confirmed by inspection; the diagnosis script will quantify it.

## Implication for G1/G2
- The β root-cause is NOT ill-conditioning (cond ~6e4, same as the well-posed gate). It is the penalty/constraint stack on a near-collinear design: ridge α=1.0 (§1.3 mirror) + sparse-prior strength 1.0 + (for γ) the monotone isotonic projection.
- I can reproduce the production fit from the committed gold config and ablate each lever. The implementer's job: turn this inspection into MEASURED ablation numbers (ridge shrinkage factor per param, β-spread vs α, plateau-vs-isotonic, collinearity r/VIF for γ).
