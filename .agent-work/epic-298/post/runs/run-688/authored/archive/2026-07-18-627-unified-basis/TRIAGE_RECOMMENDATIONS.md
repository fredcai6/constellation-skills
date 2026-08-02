# #627 Triage recommendations

Delegated run. Filing latitude granted (LAUNCH_ORDER Inherited Latitude: "file triage"). Posture: fix-now the one
trivial diff-caused item; **recommend-and-defer** the research/decision/compute follow-ons for the Admiral to
batch-file at the epic boundary (matches the delegated posture + admiral-owns-long-batch-compute). No candidate
left unrouted.

| id | classification | disposition | detail |
|---|---|---|---|
| tc1 | research hardening | recommend-and-defer | The 3 back-solved systematic constants (THETA_SENS_CDA_REL, RHO_SENS_PMAX_REL, THETA_SENS_PMAX_REL) lack an independent closed-form check; validate against a live perturbation once the #644 headless-fit stall is resolved. Bounds the CdA/P_max shared/session **split** confidence (the TOTAL is validated; the split is not). Not bounded this wave (needs a live fit; hit #644). |
| tc2 | tooling | recommend-and-defer | `scripts/migrate_estimate_store_metadata.py` (standalone tooling migration) may not add the new cross_view_covariance/{axis}_status/{axis}_shared_sigma columns — reconcile it with the generic `_migrate_missing_columns` (which DOES, since it iterates EstimateRecord fields). Low risk (the store's own construction self-heals); matters only for tooling that opens the DB without constructing an EstimateStore. |
| tc3 | cleanup | recommend-and-defer | Pre-existing `simplification_limits` complexity violation in estimate_store.py (predates #627, not in a g2-touched function; confirmed via git-stash A/B). Separate cleanup, not this wave's. |
| tc4 | unresolved decision | **RESOLVED (reconcile)** | The honest-total-sigma fusion convention is now a recorded decision anchor `docs/architecture/decisions/dual-cda-fusion-honest-total-sigma.md`. No issue needed. |
| tc5 | cleanup | recommend-and-defer | Three out-of-scope observations in the G3 IMPLEMENTER_RESULT.md — review at a later cleanup pass; low priority. |
| tc6 | missing doc / doc-drift | **fixed-now** | weekend_state/layer1_physics.py comments (lines ~23,107) referenced the retired estimate_store.SYSTEMATIC_FLOOR; updated to point at systematic_budget (#627/#506). Comment-only, module imports OK, no behavior change. Commit: (this triage commit). |
| tc7 | tooling / doctrine | recommend-and-defer (→ feedback) | `simplification_limits` was not named in the g4 handoff/IMPLEMENTER_PLAN final-verify, so a 1000-line violation slipped to review. Add it as a standing final-verify postcondition for any gate touching src/tests. This is a CONSTELLATION workflow-doctrine improvement → carried to the feedback step (CONSTELLATION_FEEDBACK), not a project GitHub issue. |
| tc8 | research hardening / compute | recommend-and-defer (Admiral: file) | **Important:** main's `physics_estimates.db` has cross_view_covariance + {axis}_shared_sigma + {axis}_status UNPOPULATED on every row (fitted 2026-07-06, pre-G2/G3/G4). The new #627 store fields are empty until a store **re-fit** (`estimate_batch`) runs — a long batch compute (Admiral-owned). Downstream consumers can't USE the cross-view/σ-honesty data until then. Recommend the Admiral file + schedule this re-fit. |
| tc9 | dependency cleanup | recommend-and-defer (float) | Baseline discrepancy: launch order cites `active_aero_zones.py` + `active_aero_identification.py` as delivered deps, but they are ABSENT from base main 29315037 (only the state-agnostic `aero_axis_2026.py` exists). Reconcile the 2026 two-state dependency status before scheduling that build. Floated to the Admiral in the verdict + documented in docs/physics/627-tier3-2026-aero-defer.md. |

**Summary:** 1 fixed-now (tc6), 1 resolved-via-reconcile (tc4), 7 recommend-and-defer (tc1,tc2,tc3,tc5,tc7,tc8,tc9).
tc7 feeds the feedback step; tc8 + tc9 floated to the Admiral in the verdict.
