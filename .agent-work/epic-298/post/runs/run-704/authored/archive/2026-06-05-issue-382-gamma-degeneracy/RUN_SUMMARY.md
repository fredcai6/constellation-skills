# Run Summary — Issue #382 (γ / compound_prior degeneracy)

Commander run, driven through the constellation engine (spine → understand → plan → execute G1/G2/G3 → reconcile → triage → review → archive). Exploratory/research; off the critical path.

## Verdicts (the three deliverables, with numbers)

### 1. β degeneracy root cause — IDENTIFICATION / DATA-POOLING limited (NOT ridge, NOT a solver bug)
The issue's premise ("why is the production solver degenerate on β when a cruder pooled fit isn't?") resolves to: **the gold artifacts are fit per-season, and a single season cannot identify the β ladder.** Measured (`scripts/diagnose_compound_beta_degeneracy.py`, 8 seasons, 139k laps):
- **§1.3 ridge-dominance hypothesis REFUTED:** raising ridge α from 0 to the production 1.0 changes pooled β-spread by **0.2%** (max β shrinkage fraction α/(diag+α) = 0.0008). The pooled β ladder stays ordered at every α. The §1.3 precedent does not transfer to β.
- **Decisive cause:** **8/8 individual seasons (2018–2025) yield a non-monotone β ladder even at ridge=0** on the clean fixed-effects design; the ordered ~0.7%/step ladder **only emerges when all 8 seasons are pooled** (pooled spread 0.00726, monotone). The cruder gate fit "recovers β" precisely because it pools 8 seasons; the per-season gold fit cannot, by construction.
- **γ plateau (C1–C4 identical in gold) is a separate mechanism:** the post-solve isotonic (PAVA) monotone-γ projection pooling a non-monotone unconstrained γ (confirmed by replaying the production projection: distinct 6→1).
- **Fix or by-design:** by-design on the data axis (per-season selection is the time-safe runtime rule). Fixable on the modelling axis: **feed the solver pooled multi-season observations** (the `build_rolling_compound_priors.py` direction). Lowering ridge does almost nothing.

### 2. γ identifiability — measured: NOT recovered, and the limit is CONFOUNDING, not poor identifiability
Measured (`scripts/diagnose_compound_gamma_identifiability.py`, full pool):
- Collinearity is **moderate, not severe**: max VIF of each γ regressor (`tyre_life × compound`) vs the absorbed fuel/evolution term φ = **2.5** (severe bar 10); corr(γ-reg, φ) in +0.31..−0.02.
- γ is **statistically well-resolved**: **4/5** adjacent pairs separable at >2 SE; worst-γ (C6) 95% profile-likelihood CI [8.4e-5, 1.7e-4] **excludes zero**.
- **But the recovered ordering is the WRONG SIGN:** γ is monotone-DOWN in softness (C1 hardest 4.2e-4 → C6 softest 1.3e-4); all 4 statistically-resolved adjacent pairs go DOWN, 0 go UP. Physics expects γ-UP.
- A well-resolved signal pointing *against* the theory ⇒ **residual confounding** (harder tyres run stable late-race phases → little measured falloff; softs run short → under-sampled high-age falloff; the §7.1 entanglement), not noise or weak identification. The γ-up crossover is **not identifiable from race-lap data with this design, and a better fit of the same data cannot rescue it.** This sharpens the gate's qualitative "non-monotone, spec-sensitive" into a quantified confounding verdict.

### 3. Gate note (§7.4/§7.5) — Piece 3: PARKED → effectively CLOSED on physics grounds
Appended §7.7 to `docs/evo/prediction_ceiling_and_priorities.md`. §7.4's strict gate is not met; §7.5's "a better deg identification could revisit" escape clause is **measured to NOT apply** (γ is well-resolved-but-wrong-signed ⇒ confounding, which more data/a tighter estimator cannot fix). **Recommendation: close Piece 3 (structured vector latent, #336) as a physics-validated direction; reopen ONLY with a de-confounding lever** (per-compound φ / non-linear evolution / stint-phase controls / exogenous deg) — gated on de-confounding, not pooling or a fancier solver. **β / Piece 1 and Piece 2 unchanged.**

## Decisions taken (cheap+reversible, logged; see decisions-log.md)
- **D0 — no nested-subagent tool available:** the environment exposes no agent-spawn tool (verified). Per the engine's documented degenerate mode, ran implementer + reviewer roles in-context with full role discipline (separate handoffs + independent re-derivation for review). `model: sonnet` recorded in each handoff as intended tier (not enforceable without dispatch). Reversible.
- **D1 — §7 was not on main at branch time → became available mid-run:** §7 / gate findings / gate script lived only on `claude/compound-regime-feasibility`. **During the run, origin/main advanced 13 commits and merged that branch (commit 316f6c9).** I merged origin/main into my branch; the §7.7 note now appends to the real §7 (append-shaped, §7.1–§7.6 untouched). Vendored the pooled-FE method into my diagnosis script anyway so it stands alone. Reversible.
- **D2 — did NOT flip any production default** (ridge_alpha, monotone-γ, β-upper-bound). Identified + measured + recommended only; a fix needs its own gold-cycle Brier evidence. Reversible.
- **D3 — reproduced degeneracy from committed gold artifacts + solver ablation** rather than re-running the full iterative fit (the gold artifacts ARE the production output; cheaper and faithful). DB-only throughout.
- Triage issues **NOT auto-filed** — 3 issue-ready recommendations prepared, deferred to Admiral (filing is the Admiral's call).

## Flagged seam items for #380
- **No #380 seam touched.** The β root cause (per-season vs pooled) and the γ verdict concern WHAT OBSERVATIONS the fitter is fed and the identifiability of the data — NOT the emitted artifact schema or the `CompoundNormalizer` interface. #380's injection-at-interface consumption is unaffected.
- **Flag:** #380's plan to inject the gate-recovered (pooled) β is **consistent** with my β finding — the pooled β is the right artifact. If the team later adopts a pooled/rolling gold β fit (triage tc1), the emitted β *numbers* change (not the schema) → co-validate with #380 since they share the β artifact. **I did not change the consumption side.**

## Triage candidates (issue-ready, not filed — Admiral approves)
- **tc1 (medium):** adopt a pooled/rolling multi-season gold compound β fit (the β fix), co-validated with #380.
- **tc2 (low):** de-confounded γ identification — the gated reopen condition for Piece 3.
- **tc3 (low):** bisect the iterative production fit's secondary per-season β distortions (incl. the β-upper-bound −1e-6 sign interaction).

## Evidence & artifacts
- Scripts (committed): `scripts/diagnose_compound_beta_degeneracy.py`, `scripts/diagnose_compound_gamma_identifiability.py` — DB-only, self-contained, simplification PASS, pyright 0/0, `--smoke` fast path.
- Doc: `docs/evo/prediction_ceiling_and_priorities.md` §7.7; `docs/architecture/packets/compound_prior.md` (Scripts + Known-Limits entries).
- Evidence JSONs (run package, regenerate via the scripts): `evidence/beta_degeneracy.json`, `evidence/gamma_identifiability.json`.

## Verification
- Both scripts smoke exit 0; full runs exit 0; numbers independently re-derived in review (exact match for β ladder, ridge collapse, per-season 8/8, γ values/SE/VIF; profile-likelihood validated vs 1.96·SE).
- `py -m src.utils.simplification_limits` PASS (2 files); `py -m pyright` 0/0 (scripts not in CI pyright scope, but clean).
- 5 commits on branch; clean tree.
