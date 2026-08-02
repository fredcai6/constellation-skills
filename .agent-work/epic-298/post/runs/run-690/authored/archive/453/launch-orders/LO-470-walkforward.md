# Launch Order: cmdr-470 — walk-forward 2025 backtest, cheap inherit-gold-fusion flow

## Mission
GitHub issue **#470** (the epic #453 done-bar item the user pulled back into scope from the #440 split): produce the leakage-free **walk-forward 2025 backtest** — in-season total fantasy score vs the prior baseline — using the **cheap inherit-gold-fusion flow**, NOT the canonical per-period-LOSO harness. Deliverable: a committed walk-forward report (`reports/walkforward/walkforward_2025.summary.{json,md}`) with a single-path-scored comparison vs the prior baseline, plus the small pipeline change that enables the cheap flow (test-led), and a runbook update. This is the LAST measured deliverable of epic #453 — nothing closes until it lands.

## Prior-Wave Verdicts / recovered measurement (pasted — READ FIRST)
From the 2026-06-10 #439 session (archive `.agent-work/archive/2026-06-10-issue-439-walkforward-backtest/post-run-investigations.md`, also posted on #440):
- **In-season retraining is a WASH on 2025 fantasy.** Clean like-for-like (both sampled-runtime, R7-24 where the model differs; P0 R1-6 identical reuse): P1 gold 174 vs wf 199 (+25); P2 250 vs 227 (-23); P3 248 vs 252 (+4); R7-24 total gold 672 vs wf 678 (+6) ≈ +0.3/race. So a near-zero or slightly-negative walk-forward delta is the EXPECTED, honest result — do not chase a win.
- **Walk-forward must NOT re-derive per-period fusion.** Inheriting the gold fusion is ~9x cheaper AND more leakage-safe (gold fusion = 2018-2024 LOSO only, zero 2025; per-period fusion risks a 2025-partial fold bleeding in). Per period: train the 12 base modules only, inherit gold fusion + calibration.
- **Path consistency is mandatory.** The 2026-06-10 committed summary MIXED scales (P0 full-evidence 707-scale + P1-3 sampled-runtime 849-scale) and was not comparable. Score ALL periods on ONE path. Prior baselines: full-evidence model 707 / human 711 (the readout-consistent comparison); sampled-runtime 849. The multi-season prior baseline file is `reports/walkforward/multiseason_fantasy.{json,md}` (model 3478 / human 2697 across seasons — different artifact, don't overwrite it).

## The harness divergence (cmdr-440 confirmed)
`scripts/run_walkforward_backtest.py` + `src/evo_predictor/walkforward/pipeline.py` HARDCODE the forbidden path: the per-period config template sets `emit_fusion_train_rows = "leave_one_season_out"` (pipeline.py ~line 159) and `_run_downstream` trains per-period fusion (~line 296+). Your code change: add an **inherit-gold-fusion mode** — per-period config `emit_fusion_train_rows = "none"` (base modules only), and `_run_downstream` assembles the period's trained manifest from the **live gold fusion config + calibration** (finish_step3b-style; the live gold's own `params/gold/sampled_runtime_manifest.json` and `params/gold/fusion/fusion.json` are the inherited artifacts) instead of training new fusion. Make it a flag (default preserves the existing harness behavior; the walk-forward run opts into inherit mode). Test-led: the existing walkforward tests must stay green; add a test for the inherit-fusion path.

## Live gold to run against
gold_cycle_260612_054059_2018thru2024 (promoted 2026-06-13). Inherited fusion: `params/gold/fusion/fusion.json`; calibration: `params/gold/uncertainty_calibration/`; the anchor is ON (quali_pace_anchor alpha 0.5) — your assembled per-period manifests MUST preserve it (the assemble-script anchor-drop bug bit #440 — use the canonical anchor-preserving writer).

## P0 prerequisite
The orchestrator's P0 reuses `params/gold/per_race_predictions/` (full-evidence per-race export) and FAILS LOUD if absent (see WalkforwardOrchestrator docstring). That dir is currently absent. Generate a CLEAN per-race export from the NEW live gold first (the committed March set was removed as leaked — do not resurrect it; regenerate from gold_cycle_260612_054059). If you score everything on the sampled-runtime path instead, P0 may not need it — decide based on which single path you pick, and state it.

## Pre-Rulings (each overridable if evidence contradicts — say so)
- **Honest-null is the expected outcome.** A wash or slightly-negative walk-forward delta is a complete, successful deliverable. Report it with full rigor; do NOT tune to manufacture a win.
- Single-path scoring is non-negotiable; never mix full-evidence and sampled-runtime scales in the headline comparison.
- No per-period LOSO/fusion (the whole point). Inherit the live gold fusion + calibration.
- Preserve the quali pace anchor in every assembled per-period manifest.
- Runbook-first: read `docs/evo/analysis_refresh.md` walk-forward + gold-lifecycle sections before acting; update it with the cheap flow at the end.
- DB-only; per-year DBs at `C:/Programs/f1Brainz/data/f1_data_YYYY.db` (main f1_data.db has 0 rows); walk-forward as-of cutoffs strictly enforced (no eval-round leakage into a period's prior/modules).
- Code changes are test-led; run `py -m src.utils.simplification_limits` on touched paths; pyright spot-check touched src before PR (CI runs pyright over all of src — it bit #425).

## Honest-Null Clause
A measured wash/negative on the walk-forward question is a complete, successful deliverable.

## Inherited Latitude
You may: commit on your branch, push, open a PR (do NOT merge), comment on #470, run all pipelines. Float to the Admiral: any need to touch the live params/gold beyond generating the per-race export; scope beyond the inherit-fusion mode + the run + the report + runbook; a result that looks like a real regression worth surfacing before I merge.

## Workspace — MAIN CHECKOUT exception (same as #440)
Work in the MAIN checkout `C:/Programs/f1Brainz` on branch `issue-470-walkforward` (already created, off origin/main 3a7127a). Runbook mandates repo-root runs (worktree paths fail manifest portability). Hard fences: NEVER commit/revert/stash the pre-existing `docs/agents/CREW_CONTEXT.md` + `docs/agents/ORCHESTRATOR_CONTEXT.md` working-tree mods (another session's); NEVER commit `.agent-work/LESSONS.md` / `.agent-work/AGENT_FEEDBACK.md` (return delta ops + feedback entry in your report); leave other sessions' `.agent-work/` dirs alone; self-rebase if origin/main advances.

## File Ownership
Findings + crash-resume state note: `.agent-work/453/findings/cmdr-470.md` (sole writer). UPDATE IT AFTER EVERY COMPLETED STEP — this is the recovery surface.

## Inherited Context (lessons from THIS epic — read `.agent-work/LESSONS.md` Active, 20 lessons)
- `py` not `python`; Set-Location repo root before git/gh; utf-8 child env on every captured python subprocess; PYTHONUTF8=1 for unicode-printing scripts.
- **Long compute: launch DETACHED (PowerShell Start-Process -WindowStyle Hidden), write the state note FIRST with PID + expected output, then check on resume. NEVER arm a per-progress watcher and sleep on it — that pattern killed 3 continuations and burned tokens (banked lesson watcher-sleep-death). Bounded foreground polling otherwise.**
- Final message ONLY when DONE or BLOCKED — never end a turn waiting on a background shell or on a question the launch order already answers (banked lesson cmdr-turn-premature-on-pre-answered).
- Crews Sonnet, small fresh contexts; `$null | claude -p` if headless; crews never background long tasks.
- `run_tests.py --integration` has a hardcoded 300s timeout — use `py -m pytest tests/integration/` directly.

## Budget
Commander **Opus**. Crews Sonnet. The cheap flow is ~1.5-2h of compute (4 periods × 12 base modules, no LOSO) plus the code change. Detached + state-note discipline is your insurance against session-limit kills.

## Stop Conditions
Stop and return when: the inherit-fusion change needs more than a focused pipeline edit (float the design); the walk-forward shows a result you'd want me to see before proceeding; a path-consistency or leakage problem can't be resolved cleanly; budget blows past ~2x estimate.

## Return Shape
Final report (last message + summary comment on #470): the walk-forward total fantasy score vs the prior baseline, single-path, with the per-period breakdown and the plain-English verdict (wash / better / worse, by how much); the inherit-fusion code change + tests + simplification_limits + pyright evidence; PR number (pushed, NOT merged); runbook update; map impact; triage candidates; lessons-delta ops + feedback entry text (do not commit shared files); workflow feedback.
