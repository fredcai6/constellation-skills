# Mission Frame — issue #470 walk-forward 2025 (inherit-gold-fusion)

## Intent
Add a flag-gated **inherit-gold-fusion mode** to the walk-forward pipeline (default = existing
per-period-LOSO behavior unchanged), then run the cheap leakage-free walk-forward 2025 backtest on a
SINGLE sampled-runtime path and report the in-season-retrain fantasy total vs the no-retrain baseline
(829). The map is relevant (the walkforward subsystem + fusion/sampled_runtime structures); frame is
full, not skipped.

## Affected Capabilities
- Walk-forward backtest (`src/evo_predictor/walkforward/`): per-period as-of-cutoff training + fantasy
  scoring of 2025. This run adds an alternate downstream that inherits the live gold fusion instead of
  retraining per-period fusion.
- Sampled-runtime prediction/comparison (`struct:evo.sampled_runtime`): the single scoring path; each
  period's trained manifest is consumed by `run_sampled_runtime_comparison.py`.
- Fusion (`struct:evo.fusion`): the inherited artifact — the live gold `params/gold/fusion/fusion.json`
  (2018-2024 LOSO, anchor alpha 0.5) replaces per-period fusion training.

## Structural Anchors
- `src/evo_predictor/walkforward/pipeline.py` (module, ~387 lines) — `render_period_config` (line 159
  hardcodes `emit_fusion_train_rows="leave_one_season_out"`), `_run_downstream` (lines 295-365 trains
  per-period fusion). THE edit site.
- `src/evo_predictor/walkforward/orchestrator.py` — routes P0 (reuse_promoted_gold) vs P1-P3 (cutoff
  pipeline); P0 needs to flow through the cutoff pipeline at cutoff=0 under the single sampled-runtime path.
- `src/evo_predictor/walkforward/periods.py` — `build_periods()`; P0 has `cutoff=None`, blocks the
  cutoff pipeline. Inherit mode needs a P0-at-cutoff-0 variant.
- `scripts/run_walkforward_backtest.py` — CLI entrypoint; threads the new flag.
- `scripts/assemble_trained_sampled_runtime_manifest.py` — the canonical anchor-preserving writer that
  assembles a trained manifest from gold details + a fusion config (inherit mode points it at live gold fusion).
- `struct:evo.fusion` (`src/evo_predictor/fusion.py`), `struct:evo.sampled_runtime`.

## Governing Constraints / Assumptions
- DB-only canonical input; per-year DBs `data/f1_data_YYYY.db`; as-of cutoff strictly enforced
  (attestation.py raises LeakageError on `train_max_round >= R` or `prior_through_round >= R`).
- One-canonical-path doctrine: the flag is a tracked dual path; default behavior unchanged; the inherit
  path is the leakage-safer one the walk-forward run opts into. Acceptable as a named, tested capability.
- Quali pace anchor (alpha 0.5) MUST be preserved in every assembled per-period manifest.
- Single-path scoring: never mix full-evidence (707/711) and sampled-runtime (829/849) scales.
- Test-led; simplification_limits on touched paths; pyright over touched src (CI runs pyright over all src).

## Decision Anchors & Decision Pressure
- decision (pre-confirmed by Admiral + LO): single path = sampled-runtime for ALL 4 periods incl P0 at
  cutoff=0; prior baseline = 829 (no-in-season-retrain 2025 model fantasy, multiseason_fantasy.json);
  P0 per_race_predictions export NOT needed. RECORDED as user-decision at understand.
- decision pressure -> reconcile candidate: the inherit-fusion mode is a durable new pipeline capability
  (dual downstream path) — Cartographer should record it as a decision anchor on the walkforward node.

## Claims / Evidence Surfaces
- claim: inherit mode trains base modules only (`emit_fusion_train_rows="none"`) and does NOT invoke
  `run_static_hierarchical_fusion_training.py` — re-confirmed by a new unit test on `_run_downstream`.
- claim: default (flag off) preserves existing harness behavior — re-confirmed by the existing
  walkforward unit suite staying green (test_pipeline_downstream.py etc.).
- claim: assembled per-period manifest preserves the anchor — re-confirmed by inspecting the trained
  manifest / a test asserting the anchor passes through.
- claim: walk-forward delta vs 829 is a wash/slightly-negative — the headline measured result.

## Map Confidence / Staleness / Disputes
- No low-confidence/stale/disputed map area blocks this. The harness divergence is confirmed directly in
  code (read at context), not from the map. multiseason_fantasy.json baseline confirmed by file read.

## Out of Scope
- Touching live `params/gold/` beyond reading the fusion/calibration to inherit (float to Admiral if needed).
- Regenerating the per_race_predictions export (sidestepped by the single sampled-runtime path).
- The canonical gold-cycle/full-refresh harness (`pipeline_validation`, multiseason backtest) — unchanged.
- Any tuning to chase a win (honest-null clause).
