# Step 1 (BLOCKING) — Evidence-model verdict

**Question:** Does `sampled-backtest --mode sampled_state` feed the model ACTUAL qualifying
results, or predict quali/start order from PRACTICE only (pre-quali)?

## VERDICT: `sampled_state` is PRE-QUALI (practice-only). Use it directly.

`sampled_state` predicts the quali order, then the race-start order, then the race order, each
stage seeded by the model's OWN sampled prior-stage order — never by observed qualifying
positions. Observed qualifying is read only to fix the driver ROSTER (who is in the field), not
their order. The actual-grid injection happens only in the `oracle_grid` / `oracle_all_states`
modes.

## Proof (file:line)

1. **Oracle injection is mode-gated to oracle modes only.**
   `src/evo_predictor/sampled_backtest.py:638-639`
   ```
   if mode in ("oracle_grid", "oracle_all_states"):
       grid = dict(db.get_session_classification(int(year), int(round_num), "Q") or {})
   ```
   Actual qualifying (`session_type="Q"`) is fetched and injected ONLY for the two oracle modes.
   `sampled_state` is not in that set, so no actual grid is injected (state stays `None`).

2. **In the runtime, `sampled_state` does not use the oracle path.**
   `src/evo_predictor/sampled_runtime.py:214-215`
   ```
   uses_oracle_grid = mode in ("oracle_grid", "oracle_all_states")
   uses_oracle_lap_n = mode in ("oracle_lap_n", "oracle_all_states")
   ```
   For `mode="sampled_state"`, both are False.

3. **With oracle off, the next stage is seeded by the model's SAMPLED prior order.**
   `src/evo_predictor/sampled_runtime.py:362-373` (`_resolve_handoff_clones`)
   ```
   if uses_oracle:
       position_maps = _oracle_position_maps_for_samples(...)   # actual Q / lap-N
       state_source = oracle_state_source                       # "oracle_grid" / "oracle_lap_n"
   else:
       position_maps = order_sample_to_position_maps(prior_orders)  # model's sampled order
       state_source = sampled_state_source                          # "sampled_quali_order" / "sampled_race_start_order"
   ```
   Race-start grid is seeded from `quali_orders` (sampled); race is seeded from `race_start_orders`
   (sampled). State-source labels: `sampled_runtime.py:234` (`sampled_quali_order`) and `:256`
   (`sampled_race_start_order`).

4. **The grid clone deliberately keeps observed quali distinct from runtime grid.**
   `src/evo_predictor/sample_state_adapter.py:60-63` (`clone_race_features_with_sampled_positions`)
   > `source='quali_order'` writes sampled grid/start positions to `race_start_grid_positions` and
   > each cloned driver's `race_start_grid_pos`. It deliberately leaves `quali_pos` untouched so
   > observed qualifying and sampled runtime grid state remain distinct.

5. **Observed Q is read only for the ROSTER, not the order.**
   `src/evo_predictor/data_adapter/_helpers.py:226-229`
   ```
   elif task in ("race_start", "quali"):
       quali_cls = db.get_session_classification(int(year), round_num, "Q") or {}
       if quali_cls:
           eligible_drivers = set(quali_cls.keys())
   ```
   The Q classification is converted to a SET of driver IDs (`eligible_drivers`) and passed to
   `build_race_features(..., eligible_drivers=...)`. Only the membership is used; positions are not.

6. **The quali-stage predictive module uses practice-only features — no `quali_pos`.**
   `src/evo_predictor/quali_power_adapter.py:39-66` — `DRIVER_QUALI_POWER_FEATURE_NAMES` is entirely
   `qs_*` (quali-sim from practice) and `short_run_*` (practice short-run pace) features plus their
   missingness indicators. `quali_pos` / `race_start_grid_pos` (observed-Q fields on `DriverFeatures`,
   populated at `data_adapter/_assemble.py:171-172`) are NOT in the quali module's feature vector.
   The recent-history quali module explicitly excludes the current event's quali:
   `src/evo_predictor/quali_recent_history_adapter.py:158` -> `"current_event_q_excluded": True`,
   using only `quali_history_full` (prior events).

## Roster caveat (mild, disclosed)
`sampled_state` uses the actual-Q *roster* (the set of drivers who qualified) to define the field.
This is a weak form of after-the-fact knowledge (it knows who started, not where). It is NOT
positional quali leakage. The predictive ordering signal is 100% practice-derived. This is the
project's established pre-quali design point; documented here for completeness.

## Empirical cross-check (recorded in Step 2/3)
The per-race diagnostics emit `runtime.backtest_mode="sampled_state"`,
`runtime.oracle_grid_used=False`, `runtime.oracle_lap_n_used=False`, and
`quali.grid_state_source="sampled_quali_order"` — confirming no oracle/actual-grid path at runtime.
