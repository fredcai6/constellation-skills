# #525 Triage Dispositions (user-ratified 2026-06-27)

| Candidate | Disposition |
|---|---|
| tc1 — OT-6 k_tire decay default mismatch | RESOLVED in-run: comment posted to #511 (grip-evolution); modelling decision, not units |
| tc2 — OT-7 two air densities (1.20 vs 1.225) | RESOLVED in-run: unified to 1.225 (ISA) in G2 |
| tc3 — friction_coupling superseded-but-live | RESOLVED in-run: removed in G2 (verified never invoked) |
| tc4 — residual cryptic config vocabulary (default_A0/A2 + as_of_means dict keys) | FIXED in-run (user: "just go ahead and fix"): expanded to the full config-default family (10 fields default_theta_*/A0/A2/g_track + fallback_*_std) + as_of_means keys; addendum commit 68a0de93 |
| tc5 — two length-only simplification_limits nudges | DROPPED (user: "no issue on the complexity limit, that's a bigger issue we'll deal with"); pre-existing oversized functions, length-only from longer names |
| tc6 — DOCUMENTATION.md missing the new ref doc | RESOLVED in-run: Cartographer added the row at reconcile |

**Issues filed during the run (user-directed, not at triage):**
- #527 — banking fit/apply asymmetry (lateral grip normalized at fit, not re-applied at apply)
- #511 comment — k_tire decay value unification (grip-evolution modelling)

**No new issues to file at the triage step.** All units-scope work landed; the two model
asymmetries are routed to #527/#511; the complexity pass is deferred per user.
