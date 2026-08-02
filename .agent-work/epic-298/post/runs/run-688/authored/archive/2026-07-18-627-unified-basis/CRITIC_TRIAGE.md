# Cold-critic triage — #627 (authority: Commander citing LAUNCH_ORDER research-program standard)

Single cold critic (panel-vs-single: single, proportional — established component, frozen scope). Plan is still
being AUTHORED (pre-freeze), so accepted findings are folded into execute.json now.

| # | Finding | Disposition | Fix folded into |
|---|---|---|---|
| 1 | [BLOCKER] fused-CdA σ-tightening is a tautology (inverse-variance always tightens) | ACCEPT | G3 rewrite: the falsifiable content is the AGREEMENT z-score (a 5σ disagreement BLOCKS fusion as illegitimate) + MATERIAL magnitude + propagation THROUGH the persisted cross-cov into b_b/b_t — direction alone is not the claim |
| 2 | [BLOCKER] persisted cross-cov (a) and redundancy demo (b) are disjoint | ACCEPT | G3 rewrite: the demo MUST use the persisted cov(CdA,b_b/b_t) to propagate the fused (tighter) CdA into b_b/b_t and show THOSE tighten vs the single-view-pin baseline |
| 3 | [BLOCKER] PowerDrag-CdA & Coast-CdA share within-session mass/ρ → not independent → naive fusion understates σ | ACCEPT (honesty, pre-ruling #3) | G3: fuse with the within-session shared-nuisance correlation from G1's budget (honest σ_fused), NOT naive-independent |
| 4 | [SHOULD] reserved wide σ magnitude undefined | ACCEPT | G2: define reserved σ = documented wide sentinel (follow existing power_drag `_CDA_UNKNOWN_SIGMA=0.4`/`_PMAX_UNKNOWN_FRAC=0.15` pattern; ≥100% rel) so it down-weights to ~0 in any inverse-variance consumer, paired with status=unresolved |
| 5 | [SHOULD] shared_floor optional → silent unfloored regression | ACCEPT | G4: pool_store MUST always pass the floor; add a test that the floored path is the one wired + floor is non-None at the wiring point |
| 6 | [SHOULD] G5 integrate check is size-only | ACCEPT | G5 c1 check: grep the doc for all four fracture markers + a numeric token each, not just size |
| 7 | [SHOULD] grip-triplet cross-session Pearson conflates physical co-variation with measurement-error cov | ACCEPT | G5(a): partial correlation CONTROLLING for circuit (separate "grippy circuits" physical co-variation from shared measurement-error cov); bound the measurement-error component specifically |
| 8 | [SHOULD] weekend_state DECISIONS (not just tests) may shift as {axis}_sigma distribution changes | ACCEPT | G4: characterize weekend_state gate output before/after on a fixture; confirm no unintended decision flips OR document the expected shift |
| 9 | [SHOULD] no single-session end-to-end consistency check | ACCEPT | Pin canonical session = Italy (Monza) RBR 2023 Q across G1/G3/G4 demos |
| 10 | [CONSIDER] A2 has a status column but no G1/G4 treatment | ACCEPT | G1/G4: name A2 explicitly (aero grip slope; systematic bounded like A0; resolved/unresolved logic) |
| 11 | [CONSIDER] grep SYSTEMATIC_FLOOR usages before delete | ACCEPT | G4: grep-for-usages step before removing the symbol |
| 12 | [CONSIDER] G2 precond doesn't declare G1 dep | REJECT (correct as-is) | G2 schema is independent of G1's budget module; real dep is G4←G1+G2+G3, already declared. Engine serialization handles the shared-file edit order. |
| 13 | [CONSIDER] decision candidates have no reconcile gate | REJECT (wrong home) | Decision candidates are reconciled at the SPINE reconcile step (Cartographer) + recorded as candidates — not an execute.json gate. Working as designed. |
| 14 | [CONSIDER] shared_floor within-year vs cross-year scope | ACCEPT (clarify) | G4: floor is WITHIN-YEAR (matches pool_store's within-year `load(year=...)`); cross-year mass-model drift is a separate axis (fit_drift) — documented out-of-scope |

Non-finding confirmed: a_long bounded-defer is correctly scoped (no re-merge). No parallel-edit hazard (sequential gating).
