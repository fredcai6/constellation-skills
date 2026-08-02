# Distilled investigation findings (commander notes; full crew output in investigation-output.txt)

## Load-bearing facts for plan + G1

1. **4 module pi fields** available at fusion intercept (`sampled_runtime._run_stage`, end, before
   `fuse_module_fields_ordered`). Order [constructor_recent, driver_recent, constructor_weekend,
   driver_weekend]. Constructor pi projected to driver space via `project_constructor_field_to_drivers`.
   In OFFLINE replay: metalearner `_event_pi_matrix` already builds this M[n,4]; `X_delta = pi_i - pi_j`.

2. **Prior-stage order IS derivable in BOTH paths:**
   - Production inference: `quali_pos` (race_start), `race_start_target_lap_positions` (race) on
     RaceFeatures, via `module_start_order_features.resolve_driver_module_start_positions`.
   - OFFLINE replay: the scorecard's `_preprocess_events` ALREADY opens the DB per event
     (`_get_constructor_by_driver` -> `DatabaseManager.get_race_driver_teams`). So grid/quali order and
     lap-3 order are fetchable from `session_classifications` at replay time keyed on year:round.
     => G1 persistence baseline (grid-order persistence) IS buildable offline.

3. **Race-pace deviation from prior order: NOT available pre-race.** `integrated_pace_gap` is a
   post-event label. So the #377 "prior-order x pace-deviation" ordering term is largely unavailable as
   an INFERENCE feature. Available proxy = practice-pace evidence ALREADY inside the 4 module pi +
   prior-stage order position. SCOPE REALITY: a deployable ordering net conditions on
   [4 module Delta-pi, prior-stage order position]; richer pace-deviation is offline-only / blocked.

4. **s_e / disagreement_rate NOT loaded at runtime.** Uncertainty-head (#408 component) production
   wiring would need new artifact plumbing (loader + RuntimeStageConfig slot + CLI). For OFFLINE
   measurement, target_mu / actual_positions are in records; s_e spread target is offline artifacts.

5. **Clean intercept, no anchor conflict.** Quali anchor attaches in the QUALI stage pre-fusion;
   race_start/race fusion is a separate `_run_stage` call. A race-day net replacing/augmenting the
   race_start/race fused field does NOT touch the anchor attach.

6. **No conditioned net exists.** OddMLP in metalearner is the prototype. New module ->
   `src/evo_predictor/fusion_conditioned_net.py`. latent_power boundary: net lives in evo, not
   latent_power.

7. **fusion.py surface:** `fuse_module_fields_ordered` (production), `fuse_module_fields_correlated`
   (#373 opt-in calibration), `project_constructor_field_to_drivers`, `_build_aligned_obs` (alignment
   helper, currently offline-only). FusionLayerConfig / FusionStepConfig dataclasses.

## Implication for gate structure
- G1 (offline) can run on regenerated records + DB prior-stage lookups. Stop-gate fully evaluable.
- The net's HONEST conditioning feature set (for both offline gate AND any production net) =
  [4 module Delta-pi] + [prior-stage-order position encoding]. This is narrower than #377's wishlist
  but it is what is derivable. State this in the plan success bar.
- Uncertainty head (#408): offline target = s_e spread target; ZERO ordering leverage (proven no-op),
  kept distinct from ordering head. Production wiring of the uncertainty head is heavier (new plumbing)
  -> if offline-justified, may be deferred to a follow-up rather than wired now.
