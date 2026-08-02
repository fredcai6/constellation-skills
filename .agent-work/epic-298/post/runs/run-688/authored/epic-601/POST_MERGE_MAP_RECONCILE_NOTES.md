# Post-#653-merge consolidated map reconcile — input notes

Do ONE coherent cartographer pass AFTER the #653 merge, covering both #628 (§9 driver_utility, deferred at its merge) and the Phase-4 FP modules. PR #653 already ships a `physics.md` reconcile for the FP modules (+241); verify it, then add the #628 §9 coverage below so the map lands in a single consistent state.

## #628 driver_utility findings (handed over by the stale #628 cartographer, verified by it against main `27b6eac9`)
- Three modules: `driver_utility_observable.py` (G1), `driver_utility.py` (G2), `driver_utility_gate.py` (G3).
- They reuse: `regime_utilization._build_regime_masks` + thresholds, `layer2.pooling.pool_random_effects`, `layer2.estimate_store_fields.effective_axis_sigma` / `UNRESOLVED_AXIS_SIGMA_FRAC`.
- **NO new cross-container edge** — just new evidence on the EXISTING `utilization → layer2` read-only edge.
- `car_prior.strictly_pre` mode **pre-dates #628** (already on main); #628 is its first load-bearing caller → decision-anchor for the strictly_pre causal-ceiling choice belongs on the utilization §9 with #628 as the making-it-load-bearing caller.
- Merge `27b6eac9` records held-out gate VERDICT=PASS (29/29), leakage-materiality 2.185 m/s vs 0.15 pre-committed bar.

## Phase-4 (#513) map surface (from Ship I verdict §cartographer)
New: `fp_lap_latent.py`, `fp_representativeness.py`, `fp_gate.py`, `fp_gate_real_extractor.py`, `scripts/fp_representativeness_gate.py`; `mass_model.fp_mass`/`FpMass`; `session_estimator` FP params; `estimate_store` cumulative_track_laps + mass_sigma_kg_assumed; `session_race.session_cumulative_track_laps`. Ship I ran a reconcile (commit 74bfc6aa) — verify it's still accurate post-merge; `check_arch_map.py` passed locally on the branch.
