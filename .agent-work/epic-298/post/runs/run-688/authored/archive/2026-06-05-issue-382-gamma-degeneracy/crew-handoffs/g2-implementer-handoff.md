# Implementer Handoff — G2

## Gate
`g2-implement` (issue #382, MEASURED γ identifiability verdict)

## Task
Build `scripts/diagnose_compound_gamma_identifiability.py` (DB-only) that returns a MEASURED γ identifiability verdict — recovered, or a QUANTIFIED identification limit — using the same pooled fixed-effects design as G1. Required metrics:
1. **Collinearity** of each γ regressor (`tyre_life × compound`, after within-(driver,race) demeaning) vs the absorbed fuel/track-evolution term φ (`lap_number`, demeaned): Pearson r AND VIF per compound. This is the issue's "collinearity with the fuel-evolution term."
2. **Profile likelihood / SE**: per-γ_c standard error from the OLS covariance (σ²·(XᵀX)⁻¹), and the implied identifiable range. Quantify: are adjacent γ's separable (γ-up ladder) vs a plateau, and at how many SE? Optionally a 1-D profile-likelihood sweep of one γ holding others at the optimum.
3. **Design condition number**, and the per-γ data information diag(XᵀX).
4. A measured `verdict` string: "γ recovered" or "identification-limited: <numbers>".

## Protected Intent / Exclusions / Constraints
Same as G1: DB-only (no FastF1); `py`; do NOT modify src/compound_prior (esp. the #380 normalizer/artifact seam); scripts/ harness, test-after; simplification_limits + pyright clean; deterministic; `--smoke` fast path. Reuse the G1 script's loaders by import (`from diagnose_compound_beta_degeneracy import load_clean_laps, build_groups, build_design`) — they are now committed.

## Close Criteria
- `py scripts/diagnose_compound_gamma_identifiability.py --smoke` exit 0; full run emits `.agent-work/issue-382-gamma-degeneracy/evidence/gamma_identifiability.json`.
- The verdict is backed by numbers (r/VIF, SE per γ_c, condition number, adjacent-γ separation in SE).
- Cross-references the gate's qualitative "non-monotone, spec-sensitive" finding and turns it into a measured limit.

## Verification Commands
```bash
py scripts/diagnose_compound_gamma_identifiability.py --smoke
py scripts/diagnose_compound_gamma_identifiability.py
py -m src.utils.simplification_limits --paths scripts/diagnose_compound_gamma_identifiability.py
py -m pyright scripts/diagnose_compound_gamma_identifiability.py
```

## Suggested Model Tier
sonnet.

## Authority / Stop Conditions / Return Format
Same as G1. Stop if src must change or the seam is implicated. Return IMPLEMENTER_RESULT with key numbers.
