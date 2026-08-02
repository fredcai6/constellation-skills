# Problem Statement — issue #470 (walk-forward 2025 backtest, inherit-gold-fusion flow)

## Consolidated problem statement
Produce the **leakage-free walk-forward 2025 fantasy score vs the prior baseline**, scored on a
**single path**, using the **cheap inherit-gold-fusion flow** — NOT the canonical per-period
LOSO+fusion harness. This is the LAST measured deliverable of epic #453.

### What "cheap inherit-gold-fusion flow" means (the code change)
The current harness (`src/evo_predictor/walkforward/pipeline.py`) hardcodes the forbidden path:
- `render_period_config` sets `emit_fusion_train_rows = "leave_one_season_out"` (line 159) — per-period
  trains LOSO fusion rows.
- `_run_downstream` trains a fresh per-period fusion via `run_static_hierarchical_fusion_training.py`.

Add a **flag-gated inherit-fusion mode** (default preserves the existing harness behavior):
- Per-period config: `emit_fusion_train_rows = "none"` — train the **12 base modules only**.
- `_run_downstream` in inherit mode: SKIP fusion training; assemble the period's trained manifest from
  the period's own gold-cycle details + the **LIVE gold fusion config** (`params/gold/fusion/fusion.json`)
  and calibration (`params/gold/uncertainty_calibration/`), via the canonical anchor-preserving
  `assemble_trained_sampled_runtime_manifest.py`. The **quali_pace_anchor (alpha 0.5) MUST be preserved**
  in every assembled per-period manifest.

This is ~9x cheaper AND more leakage-safe (gold fusion = 2018-2024 LOSO only, zero 2025; per-period
fusion risks a 2025-partial fold bleeding in).

### Scoring path discipline (non-negotiable)
Score ALL periods on ONE path. Never mix full-evidence (707/711) with sampled-runtime (849) scales in
the headline comparison. The prior baseline file `reports/walkforward/multiseason_fantasy.{json,md}`
(model 3411 / human 2697; 2025 = model 829 / human 711) must NOT be overwritten. Output contract:
`reports/walkforward/walkforward_2025.summary.{json,md}`.

### P0 prerequisite
`params/gold/per_race_predictions/` is ABSENT. P0 (R1-6, reuse promoted gold) fails loud without it.
Either regenerate a CLEAN per-race export from the NEW live gold (`gold_cycle_260612_054059`), or pick a
single path where P0 does not need it — decide and state. (The March committed set was removed as leaked;
do not resurrect it.)

### Expected outcome (honest-null clause)
A **WASH** or slightly-negative walk-forward delta is the EXPECTED, complete, successful result
(2026-06-10 measured in-season retrain ≈ +0.3/race). Do NOT tune to manufacture a win.

### Constraints / invariants
- DB-only; per-year DBs at `data/f1_data_YYYY.db`; as-of cutoffs strictly enforced (no eval-round leak).
- Test-led code change; `py -m src.utils.simplification_limits` on touched paths; pyright spot-check
  touched src before PR (CI runs pyright over all of src).
- MAIN checkout, branch `issue-470-walkforward`; never commit CREW_CONTEXT/ORCHESTRATOR_CONTEXT working
  mods, LESSONS.md, AGENT_FEEDBACK.md. PR wording "Part of #453, addresses #470"; push, do NOT merge.
- Live gold: `gold_cycle_260612_054059_2018thru2024`.

## Protected intent
The deliverable is a HONEST, leakage-free, single-path measurement plus a tested, flag-gated pipeline
capability — not a performance win. The flag default must not change existing harness behavior.

## Map-first framing
Affected structural anchors: `src/evo_predictor/walkforward/` (pipeline/orchestrator/periods/run script),
`struct:evo.fusion`, `struct:evo.sampled_runtime`. No low-confidence/stale/disputed map area blocks this;
the harness divergence is confirmed in code (read at context). Governing constraints: DB-only canonical
input, as-of cutoff contract, one-canonical-path doctrine (the flag is a tracked dual path whose default
is unchanged — acceptable because the inherit mode is the leakage-safe one the run opts into).

## Confirmation status
This problem statement MATCHES the launch order LO-470-walkforward.md. Per the Admiral PRE-CONFIRMATION
clause in the dispatch ("if your problem statement matches the launch order, the Admiral pre-confirms —
record this paragraph as user-decision evidence and proceed"), this is confirmed. Recorded as
user-decision evidence; proceeding without ending the turn to re-ask (per lesson
cmdr-turn-premature-on-pre-answered).
