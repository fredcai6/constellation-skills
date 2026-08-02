# cmdr-470 — walk-forward 2025 backtest (inherit-gold-fusion flow)

Issue #470, epic #453. Commander OPUS. Branch: `issue-470-walkforward` (MAIN checkout).
Work-id (engine spine): `cmdr-470`. Findings/state note (this file) is the recovery surface.

## Mission (one line)
Leakage-free walk-forward 2025 fantasy score vs prior baseline via the CHEAP inherit-gold-fusion
flow: per-period train 12 base modules only (`emit_fusion_train_rows="none"`), INHERIT live gold
fusion (`params/gold/fusion/fusion.json`) + calibration, assemble per-period trained manifest with
anchor PRESERVED. Add inherit-fusion mode as a flag-gated, tested pipeline change (default = existing
behavior). Single-path scoring. A WASH is the expected, honest result.

Live gold: `gold_cycle_260612_054059_2018thru2024` (promoted 2026-06-13).

## Key facts established (context read)
- Harness divergence: `src/evo_predictor/walkforward/pipeline.py`
  - `render_period_config` hardcodes `emit_fusion_train_rows="leave_one_season_out"` (line 159)
  - `_run_downstream` trains per-period fusion (`run_static_hierarchical_fusion_training.py`, lines 323-345)
- Inherit mode plan: per-period config `emit_fusion_train_rows="none"`; `_run_downstream` SKIPS fusion
  training and instead assembles period trained manifest from period gold details +
  LIVE gold `params/gold/fusion/fusion.json` via `assemble_trained_sampled_runtime_manifest.py`.
- Anchor: gold fusion has quali_pace_anchor alpha 0.5 — assembled manifest MUST preserve it.
- P0 prereq: `params/gold/per_race_predictions/` is ABSENT. Need clean per-race export from live gold,
  OR pick a single path that doesn't need it (decide & state).
- Prior baseline: `reports/walkforward/multiseason_fantasy.{json,md}` (model 3411 vs human 2697, 2025=829 model/711 human). DO NOT overwrite this file. Output contract = `reports/walkforward/walkforward_2025.summary.{json,md}`.
- Tests: tests/unit/evo_predictor/walkforward/* (test_pipeline_downstream.py mocks subprocess).

## SINGLE-PATH DECISION (stated, Admiral pre-confirmed)
Single path = SAMPLED-RUNTIME for all 4 periods INCLUDING P0 at cutoff=0 (P0 routes through the cutoff
pipeline; NO per_race_predictions export needed). Prior baseline = **829** (no-in-season-retrain 2025
model fantasy from reports/walkforward/multiseason_fantasy.json: model 829 / human 711, 24 races).
Walk-forward (in-season retrain) total vs 829 is the headline. Wash expected (~+0.3/race).

## STATE / PROGRESS
- [x] context read (LO, runbook, pipeline.py, orchestrator.py, periods.py, run script, assemble script, tests, attestation)
- [x] init engine spine (work-id cmdr-470) + claim lease (cmdr-470-opus)
- [x] understand (problem statement + Admiral pre-confirm recorded as user-decision)
- [x] plan (mission frame + execute.json: G1 inherit-fusion code, G2 run+report) — approved
- [x] compact skipped (lesson)
- [~] execute G1: implementer DONE items 1/2/3/5 (116 walkforward tests green, simpl+pyright clean).
      P0-at-cutoff-0 BLOCKED (gold_cycle/config.py requires eval_year_train_through_round>=1).
      RESOLUTION (commander decision): Option B — under inherit mode P0 = score the LIVE GOLD manifest
      (params/gold/sampled_runtime_manifest.json) over R1-6 directly (NO gold cycle for P0). P0 is the
      no-retrain promoted gold by definition; cheaper, no config relaxation, same sampled-runtime scale.
      Sent implementer back for rework (SendMessage). NOT modifying gold_cycle/config.py.
- [ ] execute G2 (run walk-forward DETACHED + report)
- [ ] reconcile / triage / review / feedback / archive

## Engine paths
- spine: .agent-work/cmdr-470/spine.json ; execute: .agent-work/cmdr-470/execute.json
- session-id: cmdr-470-opus ; engine: C:/Users/fredc/.claude/skills/constellation-workbench/scripts/checklist_engine.py

## Detached-run discipline
Long compute launched via `Start-Process -WindowStyle Hidden`; record PID + expected artifact HERE
FIRST, then check on resume. NEVER arm a per-progress watcher and sleep. Bounded foreground polling only.

## G1 STATUS: DONE + COMMITTED (a71ef6b)
Inherit-fusion mode landed, 153 walkforward tests green, reviewer APPROVE, simpl+pyright clean.
10 files committed. Triage candidate tc1: dry-run plan cosmetic (build_dry_run_plan uses build_periods()
in inherit mode — real run unaffected; verified routing programmatically: inherit P0 live_gold_p0=True).

## G2 BLOCKER FOUND (pre-run): CLI pred_dir guard fires in inherit mode
The detached launch (PID 28156) exited instantly: run_walkforward_backtest.py main() guards
`if not pred_dir.is_dir(): return 2` (lines 157-160) BEFORE running — but in inherit mode P0 scores the
live gold, NOT per_race_predictions, so the guard is spurious and blocks the run. Also the --inherit-fusion
help text is stale ("P0 still reuses the promoted gold per-race predictions" — wrong after P0 rework).
FIX (focused, in inherit-fusion scope): skip the pred_dir guard when --inherit-fusion; correct help text;
add a test. Dispatching a micro implementer+review, then relaunch.

## G2 DETACHED RUN — RELAUNCHED & ALIVE (after guard fix committed 472ee89)
- PID: 29076 (started 11:17:48). Guard passed; P0 RT comparison running (n_workers=4).
- Command: py scripts/run_walkforward_backtest.py --inherit-fusion --utilization balanced
- Logs: logs/walkforward_inherit.out.log (stdout), logs/walkforward_inherit.err.log (progress/INFO)
- EXPECTED ARTIFACT: reports/walkforward/walkforward_2025.summary.json + .md
  Console (out.log) prints "Walk-forward season total: <X> (baseline <B>); attestation_all_pass=<bool>"
- BASELINE for verdict = 829 (multiseason_fantasy.json 2025 model). Script baseline_total likely null
  (walkforward_2025_baseline.json absent) — compute delta vs 829 manually in report.
- ON RESUME: (1) check Get-Process -Id 29076; (2) Test-Path reports/walkforward/walkforward_2025.summary.json;
  (3) tail logs. If summary exists -> proceed to report+verdict. If still running -> bounded poll, NO watcher-sleep.
- Commits so far: a71ef6b (inherit mode), 472ee89 (guard fix).
- Command: `py scripts/run_walkforward_backtest.py --inherit-fusion --utilization balanced`
  (PYTHONUTF8=1; stdout+stderr -> logs/walkforward_inherit.log)
- PID: see below (recorded at launch)
- EXPECTED OUTPUT ARTIFACT: reports/walkforward/walkforward_2025.summary.json (+ .md)
  Console prints "Walk-forward season total: <X> (baseline <B>); attestation_all_pass=<bool>"
- Single path: sampled-runtime, all 4 periods. P0 = live gold over R1-6. Baseline to compare = 829
  (from reports/walkforward/multiseason_fantasy.json; the script's baseline_total may be null since
  walkforward_2025_baseline.json is absent — I compute vs 829 manually in the report).
- ON RESUME: check if log shows completion + summary.json exists. If running, bounded poll. NO watcher-sleep.
- Est ~1.5-2h (P1-P3 each train 12 base modules, no LOSO; P0 is just a comparison).

## CONTINUATION 1 (OPUS) — RECOVERY FROM CRASH (2026-06-14)
Predecessor's PID 29076 CRASHED: stale June-9 gold summary collided with fresh June-13 in
p1/reports -> _only found 2 -> RuntimeError. outputs/walkforward_2025/{p0..p3} had mixed stale+fresh.

RECOVERY DONE:
- [x] Confirmed outputs/walkforward_2025 is gitignored + untracked; removed it entirely (clean slate).
- [x] ROOT-CAUSE FIX committed 1b3d556: run_cutoff_period now clears each period's isolated root up
      front (_clear_period_root) -> idempotent re-run, no stale collision. +4 tests
      (test_pipeline_clear_period_root.py). 159 walkforward tests green; simpl+pyright clean.
      Runbook (analysis_refresh.md) updated with idempotent-rerun note.

## G2 DETACHED RE-RUN (continuation 1) — RECORD PID BELOW
- Command: py scripts/run_walkforward_backtest.py --inherit-fusion --utilization balanced
  (PYTHONUTF8=1; stdout -> logs/walkforward_inherit.out.log, stderr -> logs/walkforward_inherit.err.log)
- EXPECTED ARTIFACT: reports/walkforward/walkforward_2025.summary.json + .md
  Console prints "Walk-forward season total: <X> (baseline <B>); attestation_all_pass=<bool>"
- BASELINE for verdict = 829 (multiseason_fantasy.json 2025 model). Compute delta vs 829 manually.
- PID: 32880 (started 2026-06-14 07:25:21). Logs: logs/walkforward_inherit.{out,err}.log
- ON RESUME: (1) Get-Process -Id 32880; (2) Test-Path reports/walkforward/walkforward_2025.summary.json;
  (3) tail logs. If summary exists -> report+verdict. If running -> bounded poll. NO watcher-sleep.
