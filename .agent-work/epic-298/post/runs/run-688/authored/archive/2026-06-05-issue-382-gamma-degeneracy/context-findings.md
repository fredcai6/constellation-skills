# Issue #382 — Context Findings (baseline read)

## What #382 asks (3 deliverables)
1. **Root-cause** of the production `compound_prior` solver's β degeneracy (β≈0, γ collapsed) when a cruder pooled fit recovered β. Fix OR clear "by-design" explanation.
2. **Measured γ identifiability verdict** — profile likelihood / collinearity vs the absorbed fuel/evolution term. Not "can't recover" by assumption; measured.
3. **Updated §7.4/§7.5 gate note** — does Piece 3 (structured vector latent, #336) revive, stay parked, or close.

## Prior art (CRITICAL — extracted to prior-art/)
- `scripts/fit_compound_crossover_gate.py` and `docs/evo/compound_crossover_gate_findings.md` and §7 of the priorities doc **live ONLY on branch `claude/compound-regime-feasibility`** (tip 581c617 / df57111). They are **NOT on main**, **NOT merged**, **no PR**. Branch is 8 ahead / 24 behind main.
- The gate already established (PARTIAL verdict):
  - **β axis RECOVERED** by stdlib pooled fixed-effects fit: monotone-down C1→C6 ~1%/step, every step ≫2 SE. Gold misses it (β≈0, non-monotone, wrong-signed C1).
  - **γ axis NOT recovered**: non-monotone, spec-sensitive (per-race φ breaks it, single-season fails), confound-suspect. Framed "identification-limited, not refuted" — but QUALITATIVELY, not measured.
  - Gold/production degeneracy reproduced independently (durable).
- **What the gate did NOT do** (= my net-new work):
  - It did not diagnose WHY the *production solver* is degenerate (it only re-derived that gold IS degenerate, with an independent fit). #382 Q1 wants the production solver's own machinery diagnosed.
  - It did not put a NUMBER on γ identifiability (profile likelihood / collinearity). #382 Q2 wants measured.

## §1.3 ridge-dominance precedent (on main, the analogue to mirror)
- Retro truth solve `RetroTruthConfig.lambda_ridge=1.0` → per-event π spread CV ≈ 0.0010 (essentially constant). "The ridge dominates the data likelihood and erases magnitude at the solve."
- This is the exact failure mode to check for in the production compound_prior fit: is `ridge_alpha` (and/or the centering constraint + monotone-gamma enforcement + sparse-prior precision) shrinking β/γ toward 0 / toward equality so hard that the data likelihood can't move them?

## Production solver machinery (src/compound_prior/solver/)
- `_solve.py::_fit_compound_linear_model` builds design matrix, then calls `_solve_constrained_weighted_ridge` (in `_ridge.py`) with:
  - `config.ridge_alpha` (the ridge penalty — PRIME suspect, mirror §1.3)
  - `constraint_mat` = `_centering_constraint_matrix` (weighted-mean-zero centering)
  - `penalty` = `_combined_penalty_rows` (ridge + sparse-prior precision per param)
  - `lower` = `_coefficient_lower_bounds`
  - `ineq_mat` = `_monotone_inequality_matrix` (monotone-gamma inequality constraints!)
  - then `_enforce_monotone_gamma_coefficients` post-hoc
- Suspects for β/γ degeneracy: (a) ridge_alpha too high vs data weight, (b) centering convention forcing weighted-mean-zero collapses level info, (c) monotone-gamma enforcement flattening γ to a plateau, (d) sparse-prior precision pulling thin compounds to 0, (e) the design/target space differs from the gate's (gate used fraction-of-(driver,race)-median; production uses normalized fractional vs a baseline model).
- `src/compound_prior/identifiability.py` already exists (`compute_compound_identifiability`) — reuse for the measured γ verdict.

## Region / rigor
- `src/compound_prior/` is in the **Evo** verification region. Solver/artifact contracts are rigorous. Physics-model-adjacent: L1-L4 truth norms apply if I touch physics, but this is a fit/identifiability diagnosis — evidence is measured numbers + targeted tests if I touch src.

## SEAM with #380 (standing order)
- #380 is wiring qs_* normalization to CONSUME the gate-recovered β via injection at the EXISTING normalizer interface. I own the FITTER (compound_prior solve). If my root-cause suggests changing the fitter's emitted artifact schema or the normalizer interface → FLAG, do not change consumption side.

## Decisions surfaced so far (cheap+reversible, logged)
- **D1: §7 not on main.** My deliverable #3 updates §7.4/§7.5 which don't exist on my branch (from main). Default plan: add an APPEND-shaped §7.5 gate-update note as a NEW addition; if §7 base text is needed for the note to make sense, I will add a compact self-contained note rather than porting the whole feasibility §7 (Admiral resolves doc conflicts at merge; several commanders touch this doc). Will NOT rewrite. Logged for Admiral.
- **D2: gate script not on main.** I will write my diagnosis as a NEW script under scripts/ rather than depending on the un-merged gate script; I may reuse the gate's pooled-fit approach as a methodological cross-check, vendored into my own diagnosis script so my PR is self-contained against main.
