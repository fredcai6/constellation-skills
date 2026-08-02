# Mission Frame — #440 gold refresh + walk-forward

## Intent
Operational pipeline run (NOT a structural code change). Execute the canonical gold-refresh
runbook end to end + walk-forward backtest, producing comparison numbers for a promotion decision
the user owns. The architecture map is frozen read-only context; no module boundaries change.
Mission frame is intentionally lightweight — the runbook `docs/evo/analysis_refresh.md` is the
authoritative procedure, not the map.

## Affected capabilities (touched, not modified)
- evo_predictor gold-cycle training (12 modules + 84 LOSO + 12 calibration)
- static hierarchical fusion training
- sampled runtime comparison (default=gold vs trained=fusion)
- pipeline validation (7 sections)
- multi-season fantasy backtest + walk-forward (#439)
- perf-history ledger (#433), Step-6 strategy/fantasy artifacts

## Structural anchors
- configs/evo/gold_defaults.toml (train 2018-2024, eval 2025)
- params/gold/ (LIVE — read-only except legitimate non-promotion writes); params/gold_candidate/ (candidate)
- reports/evo/, reports/validation/, reports/walkforward/, reports/strategy/

## Governing constraints / HARD STOP
- No promote_gold.py real run (dry-run preview OK). No live-gold promotion. No merge.
- Brier primary for gold comparison (orchestrator tenet).
- py launcher; utf-8 child env on captured subprocesses; PYTHONUTF8=1 for Step-6.
- --race-start-target-lap 3; --utilization max.

## Decision anchors / pressure
- Pre-ruling 1: SKIP Step 0 (priors current 2026-06-11 — clobbering would lose #410 pooled betas).
- Candidate flow: build into params/gold then migrate_gold_to_constant_names --gold-root params/gold_candidate.
- Honest-null: measured regression/flat is a complete deliverable.

## Map confidence
High for the runbook procedure (Last verified 2026-06-10). No stale/disputed map area gates this run.

## Out of scope
- allfp_best_raw head-input wiring (#451 — post-#440 follow-up).
- Step 0 prior rebuild. Any param/default change. Promotion. Merge.
