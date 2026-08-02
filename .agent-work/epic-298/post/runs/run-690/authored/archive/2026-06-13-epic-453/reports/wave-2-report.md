# Epic #453 — Wave 2 Report (2026-06-11)

All three Wave-2 issues dispositioned: **1 shipped, 2 measured negatives** — exactly the epic's accumulate-honestly design. Main carries every Wave-1+2 change; nothing has been gold-regenerated yet. #440 is next and is the single measured checkpoint.

## Results by issue

### #425 — allfp_best_raw feature (SHIPPED, PR #466)
First-class all-FP min-sector practice-pace feature on `DriverFeatures`, populated by the practice preprocessor, with an explicit missingness companion; the #420 anchor migrated off the `min(qs_best_raw, lr_best_raw)` idiom onto it. §7.6.4 acceptance: **all deltas positive** vs the §7.6.3 reference (α=0.5 HEADLINE 0.7757 vs 0.7452; OOS-2025 0.7572 vs 0.7097). The acceptance script's `PARTIAL_REPRODUCTION` label is a stale-reference artifact (its baseline predates the #335 regen — α=0 itself improved 0.6153→0.6754); values are functionally identical to the prior idiom. 96 focused + 37 regression tests green.

**Why it matters beyond cleanliness:** per #451's Wave-1 verdict, this feature is the canonical substrate for the future race_weekend head-input repair (the ~19pp lever). That wiring is deliberately NOT done here — it's the prime post-#440 follow-up (triage T2).

### #394 — race form re-encoding (NO-GO / DEFER, PR #464)
Design note delivered (`docs/evo/race_form_reencoding_design.md`): do not extend `quali_pace_gap` encoding to race recent-history now. The #369 quali A/B regressed pairwise NLL skill in both modules (driver 0.453→0.343, constructor 0.519→0.390); the promoted #335 Brier win is anchor+retrain compounded, not encoding-attributable; race pace is noisier; no controlled race A/B exists. Door stays open on data grounds (`integrated_pace_gap` fully computable, 0% track_status nulls); go-conditions and a measurement plan are documented.

### #395 — race-start form enrichment (DROP, PR #463)
All five candidates dropped with named reasons. Standouts: the variance signal the issue wanted (`std_grid_to_target_lap_gain`) **already exists in the feature vector**; launch-delta has zero race telemetry rows in the DB and is physics-limited (parked under #443 / #445 Phase 3). Bonus project lesson: main `f1_data.db` has 0 rows — all data lives in the per-year DBs (now in the playbook).

## Process
- Wave-1's shared-file fence worked: no playbook/feedback collisions this wave; deltas applied centrally (PR #465; playbook 16 active / 1 dormant, run-tick 4).
- cmdr-425 needed two continuation relaunches (stall-shaped early stops — once after init, once at a pre-answered triage question). No work lost; engine/worktree state carried each time. Lesson candidate for closeout: pre-confirmations help but turn-discipline drift in Sonnet commanders remains the top incident class (4 of 4 incidents this epic).
- cmdr-394's proposed lesson "satisfy engine null-checks via direct JSON edit" was NOT applied (contradicts engine attest doctrine) — routed to the closeout lessons audit instead.

## Parked triage candidates (added this wave)
9. **Wire `allfp_best_raw` into the race_weekend quali head** — the principled #451 repair, now substrate-ready; the prime post-#440 follow-up (HIGH).
10. Update `accept_quali_anchor_420.py` reference bounds to post-regen baselines (cosmetic).
11. Engine null-check attest friction claim (likely verb misuse — root-cause at lessons audit, do not codify).

## Wave 3 — #440 capstone (next)
Full gold refresh + walk-forward backtest, runbook-driven (`docs/evo/analysis_refresh.md` FIRST), Opus commander. Banks: pooled β artifacts (#410), skew guard (#413), allfp_best_raw + anchor migration (#425). **Hard stop before bundle promotion** — the new bundle and walk-forward score come to the user for sign-off; nothing in this epic counts as better until that comparison says so.
