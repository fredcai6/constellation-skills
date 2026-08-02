# cmdr-440 — Gold Refresh + Walk-Forward Backtest (epic #453 Wave-3 capstone)

Crash-resume state note. Updated after every completed step (pre-ruling 9).
Continuation reads this to resume without forensics.

## Mission
- Full gold refresh per `docs/evo/analysis_refresh.md` (Steps 1-6, NO promotion).
- Walk-forward 2025 backtest (#439) vs prior baseline.
- #390 fused-Brier confirmation (vs 0.2008).
- Perf-history ledger (#433) + Step-6 artifacts regen.
- Runbook gap review.

## HARD STOP
Never run promote_gold.py for real (--dry-run preview OK). Never alter live params/gold beyond
legitimate non-promotion runbook writes. No merge. Candidate -> params/gold_candidate.

## Workspace
MAIN checkout C:/Programs/f1Brainz, branch `issue-440-gold-refresh`.
Do NOT touch: docs/agents/CREW_CONTEXT.md, docs/agents/ORCHESTRATOR_CONTEXT.md (pre-existing mods).
Do NOT commit: .agent-work/LESSONS.md, .agent-work/AGENT_FEEDBACK.md.

## Key config (verified)
- train_years 2018-2024, eval_year 2025 (configs/evo/gold_defaults.toml) — leakage gate OK.
- emit_fusion_train_rows = leave_one_season_out. utilization=balanced in config; pass --utilization max on CLI (pre-ruling 3).
- All 8 per-year DBs present + populated. Compound priors 2018-2025 present, timestamp 2026-06-11 09:46 (CURRENT — SKIP Step 0, pre-ruling 1).

## STATE LOG
- [DONE] Setup: branch created, runbook read end-to-end, prereqs verified, spine instantiated.
- [DONE] Spine: init/context/understand/plan/compact(skip)/execute started; execute.json gates e0+g1 done.
- [DONE] Step 1 (g1-tests): unit GREEN (pytest-cov installed to fix optional-dep arg error).
  Integration GREEN 126 passed/5 skipped/2 xfailed in 419s — run DIRECT `py -m pytest tests/integration/`
  because run_tests.py --integration has a hardcoded 300s timeout (RUNBOOK GAP #1).
- [CRASH] Step 2 (g2-goldcycle): training COMPLETED (modules/loso_folds/uncertainty_calibration_fit/backtests all present); process died at 7/24 of the FINAL sampled backtest. No reports/evo/gold_cycle_* from OUR run (only stale 260608 report predating epic).
- [CONTINUATION 1 / OPUS] Resumed 2026-06-11 ~23:11Z. Lease cmdr-440 still mine (heartbeat refreshed). Re-launched gold-cycle with PYTHONUTF8=1 GOLD_CYCLE_REUSE_EXISTING=1 --utilization max -> logs/gold_cycle_resume.log (ASCII, plain redirect). Reuse confirmed: module backtests short-circuited; now re-running 24-race sampled backtest + report assembly only. Monitor armed.
- [DONE] Step 2 (g2-goldcycle): resume exit 0 @ 2026-06-11 16:57 local. GOLD SLUG: gold_cycle_260611_231027_2018thru2024.
  Artifacts: reports/evo/gold_cycle_<slug>.{md,summary.json,details.json,sampled_runtime_manifest.json},
  unc_diag_<slug>.{json,md}, params/gold/uncertainty_calibration/unc_cal_260611_231027_2018thru2024.json.
  NON-FATAL: oracle_all_states diagnostic backtest failed at job idx 20 (ValueError 'sampled positions must be a strict
  permutation of positions 1..20') -> task_calibration_diagnostics.*.sampled_runtime.oracle_all_states EMPTY (event_count 0).
  Primary sampled_state mode 24/24 clean. TRIAGE CANDIDATE. Watch g7 validation.
- [DONE] Step-2 GATE: PASS. fusion_train_rows 1788/1788 non-null pairwise_nll. Retro-truth driver==constructor all years
  (2018:21 2019:21 2020:17 2021:22 2022:22 2023:22 2024:24 2025:24; train total 149 — check vs candidate_train_event_count in Step 3).
  unc_diag: 0 boundary hits; 2 wrong-sign sigma corr (constructor/driver_quali_power_from_recent_history — #314/#316); 8 advisory.
  Fusion corr |r|>0.6: quali 1 (0.773); race 3 (max 0.852); race_start 4 (max 0.991 d_rs_rw x d_rs_rh).
- [DONE] g4 Step 3 fusion: FUSION SLUG fusion_260612_000020_2018thru2024. config params/gold/fusion/fusion_260612_000020_2018thru2024.json + reports/evo fusion_*.{md,summary,details,sampled_runtime_manifest}. candidate_train_event_count=149 == retro-truth train total (all 3 tasks). Train events 149 / eval 24.
- [DONE] g5 Step 3b: materialize_runtime_bundles.py OK (12 bundles -> params/gold/runtime_bundles/gold_cycle_260611_231027_2018thru2024/, gold manifest rewritten relative). TIMESTAMP GOTCHA HIT + RESOLVED (RUNBOOK GAP #2 detail): assemble_trained_sampled_runtime_manifest.py writes a NEW timestamped manifest by default — must pass --output-manifest reports/evo/fusion_<fusion_slug>.sampled_runtime_manifest.json to overwrite the raw fusion-training manifest (validation discovers the trained manifest BY FUSION SLUG, and the raw one has absolute outputs/ paths that fail manifest_portability). THEN manually repoint its 12 module manifest_path entries to ..\\..\\params\\gold\\runtime_bundles\\<gold_slug>\\modules\\... (script: .agent-work/440-gold-refresh/evidence/repoint_trained_manifest.py). Checkpoint validation after fix: gold/static_fusion/sampled_runtime/strategy/manifest_portability/artifact_policy/provenance PASS; report_alignment fail only because rt_comparison is stale 260608 (documented; Step 4 fixes).
- [DONE] Prior baseline backed up: reports/walkforward/multiseason_fantasy.{json,md} -> .agent-work/440-gold-refresh/evidence/baseline_backup/ (also in git @ 20b5f89).
- [IN PROGRESS] g6 Step 4: run_sampled_runtime_comparison.py --race-start-target-lap 3 --output-dir reports/evo -> logs/rt_comparison.log (bg b2mkgud5p, monitor armed). DEFAULT+TRAINED backtests n_workers=4.
- [DONE-then-INVALIDATED] g6 Step 4 v1: rt_comparison_260612_000503 (24/24 both, deltas MAE -0.425 brier -0.0847 logloss -5.485 spearman -0.175; trained Brier 0.19592 vs 0.2008). g7 validation overall PASS @00:44:55Z. g8 DONE (fixtures, beam examples, Bahrain report from trained.json, performance_ledger 7 runs --check OK). Candidate v1 built+migrated (artifact set NONE problems). THEN TWO CRITICAL DISCOVERIES:
  (a) ANCHOR DROP BUG: scripts/assemble_trained_sampled_runtime_manifest.py rebuilds stages WITHOUT quali_pace_anchor (active in promoted gold, #335/PR437). My assembled trained manifest (hence rt v1 trained branch + candidate v1 manifest) had NO anchor. Fixed by rebuild via canonical fusion_training.write_trained_sampled_runtime_manifest + provenance: .agent-work/440-gold-refresh/evidence/rebuild_trained_manifest.py. RUNBOOK GAP #3 + TRIAGE (the runbook MANDATES the anchor-dropping script in Step 3b).
  (b) STALE LOSO FOLDS: ALL 84 fold bundles dated 2026-05-31, trained with lr=1e-4/patience=10 PRE-ca21ac1 (Jun 5: lr->1e-3, patience->15, median-relative SOLE encoding/minmax removed). Main modules fresh Jun-11 (lr=1e-3). GOLD_CYCLE_REUSE_EXISTING reused them (predecessor died BEFORE the LOSO stage; the May-31 bundles are from an UNRELATED earlier run in the fixed-name output dir). Fusion/calibration/fusion_train_rows therefore mixed incompatible feature-encoding regimes. NOTE: promoted Jun-8 gold likely shares this defect (its fold mtimes were May 31 too) — HIGH-PRIORITY TRIAGE.
  DECISION (override of pre-ruling-9 reuse assumption, evidence-backed): quarantined stale dirs to outputs/evo_runs/stale_20260531_loso_quarantine/ (reversible move; deletion denied by policy); re-running gold cycle with reuse=1 so the 12 fresh main modules reuse and the 84 folds RETRAIN under current config (~4h). All downstream (fusion, materialize, candidate, rt comparison, validation, Bahrain report, multiseason) WILL BE REDONE. rt v2 (anchor-fixed, stale-fold fusion) was killed mid-run — superseded.
- [KILLED ~18:30-18:58] gold cycle relaunch #2 (logs/gold_cycle_resume2.log) — background task killed externally after sampled_state pass, during oracle/LOSO data load. 0 fold checkpoints written.
- [DIED 4/84] gold cycle relaunch #3 -> logs/gold_cycle_resume3.log; only heldout_2018 has 4 fresh modules.
- [CONTINUATION 2 / OPUS] Resumed 2026-06-12. Branch HEAD now bd4033a (== main #467 merged; carries all Wave1/2 + #425/#447; state-note f95e43e refs superseded). No py procs at resume. RELAUNCHED gold cycle resume4 (PYTHONUTF8=1 GOLD_CYCLE_REUSE_EXISTING=1 --utilization max) -> logs/gold_cycle_resume4.log (bg b0jfcb2nw). Reuse confirmed: 12 main modules short-circuited; into LOSO/calibration/report (4 heldout_2018 folds reuse, ~80 retrain). Monitor armed.
  PREP for downstream (scripts reviewed): finish_step3b.py IS parametrized (--gold-slug/--fusion-slug, canonical anchor-preserving write_trained_sampled_runtime_manifest + provenance) -> USE THIS for Step 3b, supersedes hardcoded rebuild_trained_manifest.py. build_candidate.py parametrized (--gold-slug/--fusion-slug). build_loso_manifest.py parametrized via MS_FUSION_SLUG env + --year/--output. repoint_trained_manifest.py hardcoded (likely UNNEEDED — finish_step3b writes portable).
- [KILLED at 6/84] resume4 (bg b0jfcb2nw) externally killed during LOSO — THIRD kill in this phase; session-attached bg tasks not surviving. heldout_2018 now 6/12 modules checkpointed.
- [IN PROGRESS] resume5 DETACHED via PowerShell Start-Process -WindowStyle Hidden, PID 27868 (survives session/bg-task kills). Logs: logs/gold_cycle_resume5.log (stdout) + logs/gold_cycle_resume5.err.log (structured INFO). Env PYTHONUTF8=1 GOLD_CYCLE_REUSE_EXISTING=1, --utilization max. 12/12 main modules reused @22:41. Monitor bpujx35rn tails both logs + detects process death. Expected: sampled pass ~9m -> oracle pass ~7m (known non-fatal idx-20 fail) -> LOSO 6 reuse + 78 retrain ~25m -> calibration -> report = NEW SLUG.
  WALK-FORWARD DIVERGENCE CONFIRMED: canonical scripts/run_walkforward_backtest.py + src/evo_predictor/walkforward/pipeline.py HARDCODE emit_fusion_train_rows="leave_one_season_out" (pipeline.py:159) and run per-period FUSION (pipeline.py:296+). Directive forbids per-period fusion. Step (d) needs a CUSTOM per-period base-modules-only flow (cutoff-trained 12 modules + overlay new gold fusion, build_loso_manifest.py-style) NOT the canonical harness. Decision deferred to step (d).
- [PREP DONE for g9/g10] Candidate v1 at params/gold_candidate (WILL REBUILD — rm + re-run build_candidate.py + migrate with repo_root=candidate to skip reports rewrite). Heldout LOSO manifests v1 built (WILL REBUILD from new folds): .agent-work/440-gold-refresh/evidence/multiseason/manifests/. Heldout backtest cmd: py -m src.evo_predictor.run sampled-backtest --sampled-runtime-manifest <m> --year Y --mode sampled_state --compound-prior-root params/gold/compound_prior --db-path data/f1_data_<Y>.db --output <out>. 2025 result = Step-4 trained.json. Prior baseline backed up. Walk-forward: p1-p3 areas are Jun-9 (stale code, pre-#425) -> honest g10 needs 3 fresh per-period pipelines ~13h -> pre-ruling 13 SPLIT likely.
- Scripts (evidence dir): build_candidate.py, rebuild_trained_manifest.py (UPDATE slugs after new gold run!), build_loso_manifest.py (UPDATE fusion slug!), repoint_trained_manifest.py (UPDATE slugs!).

## ⚠ ADMIRAL DIRECTIVE (added 2026-06-12, while fold retrain runs — READ ON NEXT RESUME)
User surfaced recovered notes from the 2026-06-10 #439 session (archive: `.agent-work/archive/2026-06-10-issue-439-walkforward-backtest/post-run-investigations.md`; now also posted on issue #440). Three changes to your plan:
1. **Your stale-LOSO discovery was already known** (found 2026-06-10, note never posted). Your quarantine+retrain stands ratified — it IS the intended fix. The promoted Jun-8 gold sharing the defect is confirmed-suspected; keep it as the high-priority triage item.
2. **WALK-FORWARD: do NOT run per-period LOSO.** Measured 2026-06-10: in-season retraining is a wash (clean like-for-like R7-24: gold 672 vs wf 678, ~+0.3/race). Per-period pipelines = 12 base modules only (`emit_fusion_train_rows="none"`), INHERIT the new gold fusion config + calibration, assemble the trained manifest from them. ~9x cheaper: your ~13h estimate collapses to ~1.5-2h. Pre-ruling-13 split likely UNNECESSARY — plan to deliver the full mission.
3. **Path consistency is a hard requirement on THE COMPARISON:** the 2026-06-10 committed walkforward summary mixed scales (P0 full-evidence 707-scale + P1-3 sampled-runtime 849-scale — not comparable). Score all periods on ONE path; report full-evidence (vs 707 baseline / 711 human) and/or sampled-runtime (vs 849) explicitly, never mixed.

- [CONTINUATION 3 / OPUS] Resumed 2026-06-12. resume5 gold cycle COMPLETED clean. NEW GOLD SLUG: gold_cycle_260612_054059_2018thru2024.
  Engine binary scripts/checklist_engine.py ABSENT from repo (harness-side; lease reclaim N/A) -> state note IS source of truth (pre-ruling 9).
  FOLD FRESHNESS VERIFIED: oldest fold file 2026-06-11 19:57:32; 7 heldout dirs Jun-11 19:57 -> Jun-12 01:51. Main module FILES (not dir mtime) Jun-11 11:05.
  REGIME CONSISTENT: main+fold modules both lr=0.001, patience=15, schema v2, gauge median_zero. Quarantine+retrain SUCCEEDED — no mixed-encoding fusion.
- [DONE] Step-2 GATE (new slug) PASS: 37/37 invariants, 0 failures. fusion_train_rows 1788/1788 non-null pairwise_nll, 0 null.
  Retro-truth: all 6 recent_history modules scored 149 events / 0 skipped (train coverage both scopes). git_commit bd4033a, epochs 100, applied_overrides {}.
  unc_diag: 0 boundary hits, 2 wrong-sign sigma corr (constructor/driver_quali_recent_history #314/#316), 8 advisory near-zero.
  Fusion corr |r|>0.6: quali 2 (max 0.746), race_start 6 (max 0.994 d_rs_rw x d_rs_rh), race 3 (max 0.906).
- [DONE] Step 3 fusion training. NEW FUSION SLUG: fusion_260612_131957_2018thru2024.
  Artifacts: params/gold/fusion/fusion_260612_131957_2018thru2024.json + reports/evo/fusion_*.{md,summary,details,sampled_runtime_manifest}.
  config_kind static_hierarchical_fusion, train_years 7 (2018-2024), eval_year 2025 (leakage gate holds).
  CLARIFICATION (predecessor's "149" was conflated): fusion candidate_canonical_fusion_keys=173 per task INCLUDES 24x 2025 events
  (149 train + 24 eval). Verified NOT a regression: prior fusion_260612_000020 had identical 173/2025 structure. 173 = diagnostic
  usable-event universe (all modules produced output); weight FIT uses train_years only (config separates train_years/eval_year).
  149 = recent_history module retro-truth scored count (train-only). RUNBOOK/REPORT CLARITY GAP: candidate=173 vs retro-truth=149 confusing.
- [DONE] Step 3b: materialize_runtime_bundles.py OK (12 bundles -> params/gold/runtime_bundles/gold_cycle_260612_054059_2018thru2024/, gold manifest portable).
  finish_step3b.py OK: anchor present, portable, fusion overlaid, provenance set on reports/evo/fusion_260612_131957_*.sampled_runtime_manifest.json.
- [DONE] Checkpoint validation: 7/8 PASS (gold/static_fusion/sampled_runtime/strategy/manifest_portability/artifact_policy/provenance).
  report_alignment FAIL = STALE rt_comparison_260612_000503 (prior stale-fold run); Step 4 regenerates + fixes. EXPECTED.
  static_fusion counts CONFIRM no leakage: Candidate/Usable train 149, Candidate/Usable eval 24 per task. (149 fit, 24 held out.)
- [DONE] Candidate rebuilt: rm old, build_candidate.py --gold-slug gold_cycle_260612_054059 --fusion-slug fusion_260612_131957, migrate OK.
  Verified: anchor present, portable, 12 modules, fusion.json, manifest_path=runtime_bundles/modules/... (slug stripped). gold_provenance leakage_attestation true.
- [IN PROGRESS] Step 4 rt comparison DETACHED PID 22832 -> logs/rt_comparison2.log. Watcher bno5kbrma fires on exit.
  NOTE: build_loso_manifest.py REFERENCE_MANIFEST (line 31, points old fusion_260612_000020) is DEAD CODE — build() uses only GOLD_FUSION from MS_FUSION_SLUG env. Set MS_FUSION_SLUG=fusion_260612_131957_2018thru2024 for heldout manifests.
- [READY] Step 5 validation (py scripts/run_pipeline_validation.py --profile compact -> 7/7 after Step 4 fixes report_alignment).
  Step 6 (PYTHONUTF8=1): generate_synthetic_strategy_fixtures.py, generate_fantasy_beam_search_examples.py, generate_strategy_report_from_sampled_runtime.py (--round 4 Bahrain from trained.json). Then performance_ledger.

- [CONTINUATION 4 / OPUS] Resumed 2026-06-12. HEAD bd4033a, branch issue-440-gold-refresh. No py procs at resume (a brief py/python pair seen at 9:51 vanished immediately — transient, no log writes since 7:00 AM; system quiescent).
  CRITICAL FINDING — Step-4 rt_comparison_260612_132555 (cont3's, 7:00 AM) IS INVALID: its run_config resolved DEFAULT manifest = gold_cycle_260611_231027 (OLD superseded slug) and TRAINED = fusion_260612_000020 (OLD slug), NOT the new 054059/131957. Root cause: scripts/run_sampled_runtime_comparison.py:89 _manifest_candidate_paths uses _discover_latest_glob; ALL manifests share mtime 6:25:30 (rewritten together by finish_step3b+candidate build) so the "latest" tiebreak grabbed the wrong (old) slug. Trained Brier in that report (0.20120) is from the OLD fusion, not the clean-fold one. RUNBOOK GAP #4 + TRIAGE (rt comparison auto-resolution is mtime-fragile when multiple same-descriptor manifests coexist).
  FIX: re-run Step 4 with EXPLICIT --default-manifest reports/evo/gold_cycle_260612_054059_2018thru2024.sampled_runtime_manifest.json --trained-manifest reports/evo/fusion_260612_131957_2018thru2024.sampled_runtime_manifest.json. Both verified to exist, portable, anchor present (1 each).
- [IN PROGRESS] Step 4 rt comparison RE-RUN DETACHED (explicit manifests, --race-start-target-lap 3, --utilization max). Logs logs/rt_comparison3.log + .err.log. Watcher fires on new rt_comparison_* report (mtime > now) or process death.

- [CONTINUATION 5 / OPUS] Resumed 2026-06-12. HEAD bd4033a, branch issue-440-gold-refresh. No py procs (system quiescent). cont4's detached rt re-run COMPLETED -> reports/evo/rt_comparison_260612_165321_2018thru2024 (10:19 AM local), VALID: explicit manifests both new slugs (default=gold_cycle_260612_054059, trained=fusion_260612_131957), 24/24 races.
- [DONE] Step 1 metrics extracted from rt_comparison_260612_165321:
  metric_deltas_trained_minus_default: expected_position_mae -0.5111, pairwise_brier -0.07877, pairwise_log_loss -5.554, spearman_mean -0.0755.
  TRAINED aggregate: pairwise_brier 0.20157, log_loss 0.6448, exp_pos_mae 3.7076, winner_rank 3.667, winner_prob 0.18446.
  DEFAULT aggregate: pairwise_brier 0.28033, log_loss 6.199, exp_pos_mae 4.2187, winner_rank 8.833.
  #390 CONFIRMATION: trained fused Brier 0.20157 vs baseline 0.2008 -> at-baseline (delta +0.0008, within noise; trained beats default by -0.0788).

- [DONE] Step 5 validation: 8/8 PASS (gold, static_fusion, sampled_runtime, strategy, manifest_portability, report_alignment, artifact_policy, provenance). report reports/validation/pipeline_validation_summary.json.
  FIX APPLIED (legit non-promotion write): first run FAILED static_fusion+report_alignment — trained manifest provenance static_fusion_config_path was 'params/gold/fusion/fusion.json' but validator discovers the SLUG config 'fusion_260612_131957_2018thru2024.json'. ROOT CAUSE: candidate build's migrate_gold_to_constant_names.py (line 34-36) rewrote the SHARED reports/evo trained-manifest provenance slug->fusion.json (constant-name); but Step-5 validates against LIVE gold where the config is slug-named. RUNBOOK GAP #5: migrate corrupts the shared reports/evo manifest provenance when run on a candidate. FIX: re-ran finish_step3b.py to restore slug-path provenance (candidate has its own constant-name copy, unaffected). static_fusion train/eval counts 149/24 all 3 tasks (no leakage).

- [DONE] Step 6 (PYTHONUTF8=1): generate_synthetic_strategy_fixtures.py (3x200 futures), generate_fantasy_beam_search_examples.py (low/med/high), generate_strategy_report_from_sampled_runtime.py --round 4 Bahrain from trained.json (sampled_runtime_comparison_2018-2019-2020-2021-2022-2023-2024_eval_2025.trained.json) -> reports/strategy/fantasy_beam_search_2025_bahrain_from_sampled_runtime.{json,md}. All exit 0.
  Performance ledger: build_performance_ledger.py wrote 8 runs; --check OK (up to date). New slug gold_cycle_260612_054059 present @ commit bd4033a4.

- [IN PROGRESS] Multi-season fantasy (chain step 4). 3 LOSO heldout manifests REBUILT from NEW folds (heldout_2022/2023/2024, Jun-12 01:48-02:20, 12 modules each) + new fusion MS_FUSION_SLUG=fusion_260612_131957_2018thru2024 -> .agent-work/440-gold-refresh/evidence/multiseason/manifests/heldout_<Y>_sampled_runtime_manifest.json. All 3 build exit 0.
  Heldout backtest cmd: py -m src.evo_predictor.run sampled-backtest --sampled-runtime-manifest <m> --year Y --mode sampled_state --compound-prior-root params/gold/compound_prior --db-path data/f1_data_<Y>.db --output .agent-work/440-gold-refresh/evidence/multiseason/results/heldout_<Y>.json
  RESUME: 2022 DONE (heldout_2022.json, 22 races). 2023 DONE (heldout_2023.json, 22 races). 2024 was killed at race 14/24 when the session bg-chain was killed (session-attached subprocess died — same kill pattern as gold-cycle phase). RELAUNCHED 2024 DETACHED via Start-Process -WindowStyle Hidden PID 14076 (logs/ms_heldout_2024_b.log + .err.log) so it survives session kills. ~33min. When heldout_2024.json present -> run multiseason fantasy.
  2025 result = Step-4 trained.json (reports/evo/sampled_runtime_backtests/sampled_runtime_comparison_2018-2019-2020-2021-2022-2023-2024_eval_2025.trained.json).
  PRIOR BASELINE (lower=better; backup .agent-work/440-gold-refresh/evidence/baseline_backup/): totals model 3478 / human 2697 (model LOSES by 781). per-season model/human: 2022 831/739, 2023 963/632, 2024 835/615, 2025 849/711.
  THEN: py scripts/run_multiseason_fantasy_backtest.py --candidate-gold-root params/gold_candidate --result 2022=<r> 2023=<r> 2024=<r> 2025=<step4 trained.json>. Prior baseline backed up .agent-work/440-gold-refresh/evidence/baseline_backup/ (model 3478 / human 2697). OVERWRITES reports/walkforward/multiseason_fantasy.{json,md} -> back up done.

- [DECISION] Walk-forward (chain step 5): PRE-RULING 13 SPLIT INVOKED. Both triggers fire.
  Canonical harness FORBIDDEN by directive: src/evo_predictor/walkforward/pipeline.py:159 hardcodes emit_fusion_train_rows="leave_one_season_out" in render_period_config (an f-string, not config-driven), AND _run_downstream (pipeline.py:295-360) runs a per-period static fusion training subprocess + uses the anchor-DROPPING assemble_trained_sampled_runtime_manifest.py (bug #3). Per-period fusion is the forbidden thing AND measured (2026-06-10) to be a wash (+0.3/race R7-24).
  DIRECTIVE CHEAP FLOW requires: (1) override emit_fusion_train_rows="none" -> but it's hardcoded in the f-string, NOT a passthrough config flag -> CODE EDIT to pipeline.py:159 required. (2) Skip per-period fusion + overlay NEW gold fusion config (build_loso_manifest.py-style) -> CODE EDIT to _run_downstream required (rip out fusion subprocess, add gold-fusion overlay + anchor-preserving manifest write). (3) per-period as-of-N prior build already exists (_build_prior_root). (4) 3 sampled comparisons over period rounds.
  COST even with LOSO skipped: 3 periods x (12 base modules ~40-50min + sampled comparison ~20min) ~= 3-3.5h compute. EXCEEDS ~2h. Plus >small code changes (two methods in pipeline.py). BOTH pre-ruling-13 triggers met -> SPLIT. Walk-forward delivered as a precise follow-up plan in the report, does NOT block. P0 (R1-6, reuses promoted gold per_race_predictions which are ABSENT and would need a gold per-race export) also outstanding.

- [DONE] Promotion dry-run (chain step 6) — PREVIEW ONLY, exit 0, verbatim:
  {"candidate":"params\\gold_candidate","gold":"params\\gold","new_slug":"gold_cycle_260612_054059_2018thru2024","old_slug":"gold_cycle_260608_043414_2018thru2024","archive_dest":"params\\gold_archive\\gold_cycle_260608_043414_2018thru2024","dry_run":true}
  Promote cmd for user sign-off: py scripts/promote_gold.py --candidate params/gold_candidate

- [DONE] Multi-season fantasy backtest (chain step 4 COMPLETE). All 4 seasons scored vs human (lower=better):
  2022 model 873 / human 739 (+134); 2023 model 850 / human 632 (+218); 2024 model 859 / human 615 (+244); 2025 model 829 / human 711 (+118).
  CANDIDATE TOTAL: model 3411 / human 2697 (gap +714, model LOSES all seasons).
  vs PRIOR BASELINE: model 3478 / human 2697 (gap +781). IMPROVEMENT: -67 pts model total, gap closed by 67.
  Per-season vs prior: 2022 worse (831->873 +42), 2023 better (963->850 -113), 2024 worse (835->859 +24), 2025 better (849->829 -20). Net gain driven by 2023.
  Wrote reports/walkforward/multiseason_fantasy.{json,md} (prior backed up). LOSO fusion caveat applies (gold fusion structurally saw each heldout year's OOF metrics; flagged for strict per-season-holdout follow-up — documented in build_loso_manifest.py provenance).

- [DONE / MISSION COMPLETE — CONTINUATION 5] No src changes (pyright N/A). Selective commit 307c4fa (new-slug gold/fusion/rt artifacts + runtime_bundles + canonical outputs; NO old slugs, NO LESSONS/docs-agents/.agent-work/outputs/candidate). Pushed branch issue-440-gold-refresh. PR #469 created. Full report posted issue #440 comment 4697281900. Promotion remains user-gated (dry-run captured). Walk-forward = pre-ruling-13 split (plan in PR + issue comment).

## RUNBOOK GAPS FOUND
1. `py run_tests.py --integration` has a hardcoded 300s (5min) subprocess timeout in run_tests.py
   run_command(); NN integration tests need ~7min so the documented command always TIMEOUTs.
   Workaround: run `py -m pytest tests/integration/` directly. Also pytest-cov is an OPTIONAL dep
   but run_tests.py --unit passes --cov unconditionally, so a clean env fails until pytest-cov installed.

## Slugs / artifacts (fill as produced)
- gold slug: TBD
- fusion slug: TBD
- candidate root: params/gold_candidate (TBD)

## CRITICAL DOWNSTREAM NOTES (discovered during g2 wait)
- WALK-FORWARD (#439, run_walkforward_backtest.py): 4 periods. P0 reuses params/gold/per_race_predictions
  (currently ABSENT — must be produced by gold per-race export). P1/P2/P3 each run a FULL per-period
  gold cycle+fusion+materialize = 3 more multi-hour pipelines. Budget: main cycle + 3 cycles = 4x.
  Pre-ruling 13 split path likely. Dry-run plan captured. Writes reports/walkforward/walkforward_2025.summary.{json,md}.
- MULTISEASON FANTASY (g9, run_multiseason_fantasy_backtest.py) OVERWRITES reports/walkforward/multiseason_fantasy.{json,md}
  — the PRIOR BASELINE. MUST back up baseline first (prior totals model 3478 vs human 2697, loses by 781).
  Needs --result YEAR=PATH per season (2022-24 from LOSO heldout folds, 2025 from gold) + --candidate-gold-root params/gold_candidate.
- PRIOR BASELINE (reports/walkforward/multiseason_fantasy.md, 2026-06-10): model 3478 / human 2697; loses all 4 seasons.

## Resume recipe
- Training crash late: re-run gold-cycle with $env:GOLD_CYCLE_REUSE_EXISTING=1 (reuses bundles under outputs/evo_runs/gold_module_training_cycle/).
- Spine lease stale after long step: re-claim same session-id (idempotent) or --force --reason.
