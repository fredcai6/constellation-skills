# IMPLEMENTER_RESULT — G3 (gate note + verdicts)

## Completed slice
Appended **§7.7 "Exploratory follow-up — γ / `compound_prior` degeneracy root-cause (#382, resolved)"** to `docs/evo/prediction_ceiling_and_priorities.md` (after §7.6, append-shaped, self-contained). It synthesizes the three deliverables with measured numbers and gives the Piece-3 recommendation.

## Files changed
- EDITED `docs/evo/prediction_ceiling_and_priorities.md` — added §7.7 only (no other section touched).

## The three deliverables in the note
1. **β root cause:** identification/data-pooling (per-season vs pooled), NOT ridge (refuted, 0.2% effect), NOT a solver bug. 8/8 seasons non-monotone at ridge=0; pooled ladder ordered. γ plateau = isotonic projection. Refines §7.5's "provably mis-fit" to its mechanism. Fix (if pursued): feed pooled multi-season observations.
2. **Measured γ verdict:** NOT recovered, limit is CONFOUNDING not poor identifiability — max VIF 2.5 (moderate), 4/5 pairs separable >2 SE, profile CI excludes zero (well-resolved), but all resolved pairs point DOWN (wrong sign). Revises §7.5's "most collinear with φ" (collinearity is only moderate); the real obstacle is confounding (§7.1).
3. **Piece-3 gate recommendation:** move from PARKED to effectively **CLOSED on physics-identification grounds**. §7.5's "a better deg identification could revisit" escape clause is measured to NOT apply (well-resolved-but-wrong-signed ⇒ a better fit can't help). Reopen ONLY with a new lever that breaks the confound (fuel-corrected/stint-phase-controlled design, exogenous deg measurement) — gated on de-confounding, not more pooling/solver. β/Piece 1 and Piece 2 unchanged; #380's pooled-β injection is consistent.

## Test mode satisfied
inspection-only (docs). Postcondition check passes: doc contains "#382" and "Piece 3" (engine command check). All references resolve (both scripts exist, runtime_normalization.py exists, §1.3/§7.1/§7.4/§7.5/§7.6 exist, `_isotonic_non_decreasing` matches production code). §7 headings intact (7.1-7.7).

## Assumptions used
- Append-shaped per standing order (§7 now on main after the feasibility branch merged mid-run — D1 updated). New §7.7 subsection, no rewrite of §7.1-§7.6.
- Scripts documented inline in §7.7 + their module docstrings; no separate scripts/README created (matches the repo convention where scripts are documented in findings docs).

## Stop conditions hit
None.

## Out-of-scope / seam
- The note explicitly states no artifact-schema / normalizer change and that #380's β injection is consistent — the standing-order seam flag is captured in the durable doc, not just the run package.
