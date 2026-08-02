# G3 generation notes (Commander-prepared while G2 ran)

## Verified backtest recipe (probe, 4s, year 2025)
```
py -m src.evo_predictor.run backtest-latent-power-module \
  --module <MODULE> \
  --bundle "C:/Programs/f1Brainz/outputs/evo_runs/gold_module_training_cycle/modules/<MODULE>/latent_power_manifest.json" \
  --year 2025 \
  --output "<workdir>/records/<MODULE>.json" \
  --retro-root "C:/Programs/f1Brainz/params/retro_truth" \
  --compound-prior-root "C:/Programs/f1Brainz/params/gold/compound_prior" \
  --db-root "C:/Programs/f1Brainz/data" \
  --emit-module-record
```
- Probe (driver_quali_recent, year 2025): 24 events, 20 entities, target_mu + actual_positions BOTH present. ~4s.
- All 12 backtests => well under 5 min total. Budget non-issue.
- compound-prior-root needed for constructor + weekend modules; harmless for recent driver (probe omitted it and still worked). Pass it for all to be safe.

## The 12 modules (4 per task), canonical order per module_names_for_task:
quali:      constructor_quali_power_from_recent_history, driver_quali_power_from_recent_history, constructor_quali_power_from_race_weekend, driver_quali_power_from_race_weekend
race_start: constructor_race_start_power_from_recent_history, driver_race_start_power_from_recent_history, constructor_race_start_power_from_race_weekend, driver_race_start_power_from_race_weekend
race:       constructor_race_power_from_recent_history, driver_race_power_from_recent_history, constructor_race_power_from_race_weekend, driver_race_power_from_race_weekend

## CRITICAL integration detail (found via probe):
Module event_ids carry FAMILY-SPECIFIC SUFFIXES that DIVERGE across the 4 modules of a task:
  driver recent  -> "2025:1:Australia:quali_history"
  (constructor / weekend will differ, e.g. ":constructors:quali", ":quali_weekend")
The G1 harness `load_task_records` inner-joins on RAW event_id, which will NOT match across modules.
=> G3 MUST canonicalize event_ids to FusionEventKey "year:round:gp" before joining the 4 modules.
   Reference: src/evo_predictor/fusion_training/_types.py FusionEventKey.from_module_event_id(event_id, task)
   (splits on ':', takes year:round_num:gp_name). Build the task's joined events on that canonical key.

## constructor_by_driver mapping
align_event needs {driver_id -> constructor_id} per event. The records do NOT carry it.
Source options (pick the leakage-free one in G3):
  - Derive per-event from session_classifications / DB driver->team for that (year, round).
  - Since this is OFFLINE replay scoring (not prediction), using the actual race-weekend team
    assignment per event is acceptable (it is not a predictive feature; it only maps which
    constructor latent projects onto which driver). Document the source.

## Scoring truth
- pairwise log-loss / rank MAE / spearman vs actual_positions.
- coverage vs target_mu.
- Both present in 2025 records (probe confirmed).
