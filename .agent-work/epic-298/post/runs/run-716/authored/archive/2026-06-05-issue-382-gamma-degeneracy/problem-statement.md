# Issue #382 — Consolidated Problem Statement (post-interrogation)

## The bounded problem
Exploratory/research, off the critical path. Three measured deliverables:

1. **Root-cause the production `compound_prior` solver's β degeneracy** (β≈0, γ collapsed C1–C4 identical) when a cruder stdlib pooled fixed-effects fit recovered β decisively. Deliver a measured root-cause + a fix-OR-by-design explanation. **Diagnose-first; no production code fix required** (issue says "diagnosis script + doc update is a perfectly good PR shape").
2. **Measured γ identifiability verdict**: collinearity (Pearson r / VIF) of the γ regressor (`tyre_life×compound`) vs the absorbed fuel/track-evolution term; profile-likelihood width / SE per γ_c; design condition number. A NUMBER, not "non-monotone."
3. **Updated §7.4/§7.5 gate note**: does Piece 3 (structured vector latent, #336) revive / stay parked / close.

## Resolved understanding (the answers)

- **Q1 scope:** diagnose-first; measured root-cause + explanation suffices. Production solver fix is OUT of default scope (timebox + #380 seam).
- **Q2 γ-measured:** report (a) corr/VIF of γ-regressor vs fuel/evolution term, (b) profile-likelihood/SE per γ_c + identifiable range, (c) condition number.
- **Q3 §7 not on main [LOGGED DECISION, flag to Admiral]:** §7 / gate findings / gate script live ONLY on un-merged branch `claude/compound-regime-feasibility`. Default: append a NEW self-contained §7.5-followup note to the priorities doc on my branch (append-shaped, stands alone). Do not port whole §7; do not rewrite. Admiral reconciles at merge.
- **Q4 #380 seam:** seam = `CompoundNormalizer.normalize_lap_time` + artifact JSON schema (`parameter_means[beta/gamma_C*]`, `effect_space=normalized_fractional`, `_effect_fraction=beta+gamma*age`) in `src/compound_prior/runtime_normalization.py`. FLAG (don't change) any artifact-schema / key-convention / effect-formula / normalizer-signature change.
- **Q5 done-bar:** scripts+docs only → light bar (no src tests needed for a scripts/ harness; exploratory output is non-canonical). IF I touch src/compound_prior → focused region tests + simplification_limits + pyright. Timebox: partial verdict + "what it'd take," then close.
- **Q6 config-default flip [IRREVERSIBLE — needs Admiral if pursued]:** flipping a production default (ridge_alpha, monotone-γ) is a behavior change gold + #380 depend on → out of default scope; identify+measure+recommend the lever, do not flip.

## Root-cause hypotheses to TEST (measured, in execute)
From reading `src/compound_prior/solver/_ridge.py` + `_core.py` + `runtime_normalization.py`:

- **H1 (ridge dominance, §1.3 mirror):** `ridge_alpha` default = **1.0** — identical to RetroTruthConfig.lambda_ridge=1.0 that §1.3 proved "dominates the data likelihood and erases magnitude." The ridge block is `X'WX + α·I`. If the weighted data information `X'WX` on the β/γ directions is ≪ α, β/γ shrink toward 0. PRIME suspect for β≈0. Measure: diag(X'WX) per param vs α; ridge shrinkage factor; refit at α∈{0, 1e-3, …, 1} and watch the β ladder appear/vanish.
- **H2 (monotone-γ isotonic plateau):** γ has THREE constraints — lower bound γ≥0, inequality γ_softer≥γ_harder, AND post-hoc isotonic projection `_enforce_monotone_gamma_coefficients`. The gate found the *unconstrained* γ ordering is non-monotone; isotonic projection POOLS non-monotone adjacent values into equal blocks → exactly the "C1–C4 identical" plateau. STRONG candidate for γ collapse (and possibly the production "by-design" answer: the plateau is the monotone constraint doing its job on a non-identified axis).
- **H3 (target/design differences vs the gate):** production reference = C1 (gate used C3); production target = "stacked_baselined_observations" vs a baseline-model fit; weighting (precision 1/σ²) differs from the gate's OLS. Could explain why production β is *flat* where the gate's β is a ladder, beyond ridge.
- **H4 (sparse-prior / support drops):** default `sparse_prior_mode='none'`, strength 0 — so probably NOT active in gold, but verify the gold artifact's config. If thin compounds were pulled to 0 by support drops, that adds to apparent collapse.

## Cross-check asset
Vendored prior art in `.agent-work/issue-382-gamma-degeneracy/prior-art/`: the gate script (stdlib pooled FE fit) + findings doc. I will reproduce the gate's pooled β ladder as the "ground truth the production solver should approximately match," then bisect what in the production pipeline destroys it. My PR's diagnosis script will be self-contained against main (vendor the needed pooled-fit method; do not depend on the un-merged gate script).

## Protected intent
- Do not change production solver behavior (gold + #380 depend on it).
- Do not touch the #380 normalizer seam / artifact schema; flag if implicated.
- Keep priorities-doc edits append-shaped; Admiral merges.
- This is research: deliver measured verdicts; any code is a scripts/ diagnosis harness with targeted tests only if it touches src.
