# IMPLEMENTER_RESULT — G2 (measured γ identifiability)

## Completed slice
`scripts/diagnose_compound_gamma_identifiability.py` — DB-only, imports the G1 loaders. Measures γ identifiability on the pooled fixed-effects design: collinearity (corr + VIF vs φ), per-γ SE, adjacent-γ separation in SE, 1-D profile likelihood, condition number. Emits `evidence/gamma_identifiability.json` with a measured verdict.

## Files changed
- ADDED `scripts/diagnose_compound_gamma_identifiability.py`
- WROTE `evidence/gamma_identifiability.json`
- No src/ change. #380 seam untouched.

## Test mode satisfied
test-after. smoke exit 0; full exit 0; simplification_limits PASS; pyright 0 errors/0 warnings.

## Evidence produced — MEASURED γ VERDICT
**γ NOT RECOVERED, and the limit is CONFOUNDING, not poor identifiability.**

Full 8-season pooled fit (139k laps), γ per compound (×10⁻⁴), SE, corr vs φ:
| C# | γ | SE | corr(γ-reg, φ) | VIF |
|----|-----|-----|------|-----|
| C1 | 4.170 | 0.109 | +0.226 | 2.16 |
| C2 | 3.813 | 0.053 | +0.311 | 2.30 |
| C3 | 3.921 | 0.050 | +0.163 | 2.36 |
| C4 | 3.470 | 0.066 | +0.081 | 2.28 |
| C5 | 2.760 | 0.107 | +0.022 | 2.30 |
| C6 | 1.277 | 0.229 | −0.015 | 2.55 |

- **Collinearity is moderate, NOT severe:** max VIF (γ regressor vs φ + all other cols) = **2.5** (textbook severe bar is 10). corr(γ-regressor, φ) ranges +0.31..−0.02. So γ is NOT crippled by raw collinearity with the fuel/evolution term.
- **γ is statistically well-resolved:** **4/5** adjacent pairs separable at >2 SE; the worst-identified γ (C6) has a 95% profile-likelihood CI [8.42e-5, 1.71e-4] that **excludes zero**.
- **BUT the recovered ordering is the WRONG SIGN:** among the 4 statistically-resolved adjacent pairs, **4 go DOWN and 0 go UP** in softness — γ is predominantly monotone-DOWN (hardest C1 highest deg 4.17e-4, softest C6 lowest 1.28e-4). Physics expects γ-UP (softer degrades faster).
- **Interpretation (measured):** the γ-up crossover is not merely noisy/under-identified — the clean pooled signal points the *opposite* way, which is the signature of **residual confounding** (harder tyres run stable late-race phases → little measured falloff; softs run short → high-age falloff under-sampled — the §7.1 entanglement), not sampling noise. The γ-up ladder is **not identifiable from this design**: confounded with the absorbed fuel/track-evolution + stint-phase structure.

This sharpens the gate's qualitative "non-monotone, spec-sensitive" into a quantified verdict: identifiable-but-wrong-signed ⇒ confounding-limited.

## Profile likelihood
Implemented a real 1-D profile likelihood (fix γ_j on a ±6 SE grid, re-optimize the rest, chi²(1)=3.84 threshold on 2(RSS−RSS_min)/σ²). For C6: 95% CI [8.42e-5, 1.71e-4], half-width 4.35e-5 vs MLE 1.28e-4 — finite and excludes zero (γ is identified; it is just wrong-signed for the ladder).

## Assumptions used
- Same pooled FE design + eligibility as G1 (imported). The φ term is the single global lap_number slope (the gate's primary spec). Per-race φ (the gate's robustness variant) would only worsen γ identifiability; not re-run here (timebox; the gate already showed per-race φ degrades it).
- VIF computed with an intercept on the demeaned columns (standard).

## Stop conditions hit
None.

## Out-of-scope / seam
- #380 seam untouched; γ identifiability implies no artifact/normalizer change. It informs the Piece-3 gate (γ-dependent vector latent), not #380's β injection.
