# IMPLEMENTER_RESULT — G1 (β degeneracy root-cause)

## Completed slice
`scripts/diagnose_compound_beta_degeneracy.py` — self-contained, DB-only diagnosis harness. Reads committed gold artifacts, rebuilds the gate's pooled fixed-effects design from the 8 per-season DBs, runs a ridge-α sweep, a per-season-vs-pooled identification test, and an isotonic gamma-plateau replay. Emits `.agent-work/issue-382-gamma-degeneracy/evidence/beta_degeneracy.json`.

## Files changed
- ADDED `scripts/diagnose_compound_beta_degeneracy.py` (~430 lines)
- WROTE `.agent-work/.../evidence/beta_degeneracy.json` (evidence)
- No src/ change. No #380 seam touched.

## Test mode satisfied
test-after. `py scripts/diagnose_compound_beta_degeneracy.py --smoke` exit 0; full run exit 0. `py -m src.utils.simplification_limits --paths scripts/diagnose_compound_beta_degeneracy.py` PASS. `py -m pyright scripts/diagnose_compound_beta_degeneracy.py` 0 errors/0 warnings.

## Evidence produced (KEY NUMBERS — measured)
**β root cause = identification / data-pooling limited. NOT ridge, NOT a solver bug. (H1 ridge-dominance pre-registered and REFUTED.)**

1. **Ridge REFUTED:** On the well-identified pooled design (139,006 demeaned laps, 8 seasons, 2861 groups), production ridge α=1.0 changes β-spread by only **0.2%** (α=0 spread 0.007259 → α=1.0 spread 0.007245). Max β shrinkage fraction α/(diag+α) = **0.0008** — the data information on β directions dwarfs α=1.0. §1.3 ridge-dominance does NOT transfer to β. The pooled β ladder stays ordered (`increasing`) at every α including 1.0.
2. **Decisive cause — per-season vs pooled:** the gold artifacts are fit PER SEASON. **8/8 individual seasons (2018-2025) yield a NON-MONOTONE β ladder even at ridge=0** with the clean FE design (per-season spreads 0.0035-0.0135, all non-monotone). The ordered ~0.7%/step ladder **only emerges when all 8 seasons are POOLED** (pooled monotone_kind=`increasing`, spread 0.00726). So the cruder pooled fit "recovers β" precisely because it pools 8 seasons; the production per-season gold fit cannot, by construction. This matches the gate findings ("per-season uniformly NOT RECOVERED; β signal only emerges after pooling all eight seasons").
3. **γ plateau = the isotonic monotone projection (separate mechanism):** replaying `_isotonic_non_decreasing` (PAVA, copied identically from `src/compound_prior/solver/_ridge.py`) on the unconstrained pooled γ: non_monotone_before=True, distinct values 6→1 (full run), plateau_created=True. This is exactly the gold γ_C1..C4-identical signature.

**Gold config confirmed** (read from artifacts): ridge_alpha=1.0, sparse_prior_mode=support_aware_zero_shrinkage(strength 1.0), reference C3, race_delta_gamma_mode=additive, effect_space normalized_fractional, condition_number ~6e4-7e4 (well-posed, NOT rank-deficient).

## Fix or by-design
BY-DESIGN on the data axis (per-season fit is required by time-safe prior selection in `runtime_normalization.py`, and a single season genuinely cannot identify the ladder — a data-pooling limit, not a coding defect). FIXABLE on the modelling axis: feed the solver POOLED multi-season observations (a rolling/pooled compound prior). Lowering ridge_alpha does almost nothing (refuted). Changing production is out of scope (gold + #380 depend on it) — measured recommendation only.

## Assumptions used
- Reproduced the production degenerate output by reading committed gold artifacts (the actual production output) rather than re-running the full iterative `fit_tire_wear_model` — the gold artifacts ARE the production output, so this is faithful and cheaper. The ablation uses the gate's clean pooled-FE design (the well-identified reference where the ladder is known to exist) to isolate the ridge effect; this is the right controlled comparison.
- β-ladder monotonicity uses an orientation-agnostic, tie-tolerant check (tol 5e-5) — the gate's C2/C3 land within ~5e-6 and the sign convention differs between the gate's reference-omitted β and my recentered β. The economically meaningful question (does β order by compound) is what's tested.

## Stop conditions hit
None.

## Out-of-scope observations / seam flag
- **#380 seam:** untouched. The root cause (per-season vs pooled identification) concerns WHAT OBSERVATIONS the fitter is fed, NOT the emitted artifact shape or the `CompoundNormalizer` interface — so #380's injection-at-interface consumption is unaffected. Flag for #380: if the team later adopts a pooled compound-prior fit, the emitted β *numbers* change (not the schema); co-validate since they share the β artifact. #380's plan to inject the gate-recovered (pooled) β is consistent with this finding — the pooled β is the right artifact.
- The production fit also carries a `--beta-upper-bound` default of −1e-6 (β constrained ≤ −1e-6) and an iterative baseline+SOR solve; these add to the per-season degeneracy but the decisive lever is pooling. A full component-by-component bisection of the iterative production fit was timeboxed out (off critical path) — recorded as a triage candidate.
