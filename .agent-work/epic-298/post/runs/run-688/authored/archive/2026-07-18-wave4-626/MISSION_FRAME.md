# Mission frame — #626 Phase 2 four-layer weekend-state model

## Intent
Build a four-layer weekend-state model on qualifying that decomposes the raw per-session physics Q
estimates into (1) explained physics, (2) within-session evolution, (3) field-car common-mode, (4) car
signal — each with honest σ — and prove via a HELD-OUT F6 gate that it beats x4's weekend-relative floor
on ≥7/11 axes by a margin outside noise. Honest-null is an accepted outcome.

## Affected capabilities
- NEW: `src/physics/` weekend-state decomposition (no existing module; greenfield). Consumes the
  fit-output axis store; produces a decomposed per-car-weekend state + σ.
- Does NOT change: the estimator fitting (layer2 views), evo, gold bundle, production defaults.

## Structural anchors (verified by read this run)
- `data/physics_estimates.db:session_estimates` — 11 axes each + `_sigma`, plus `rho`, `rho_is_fallback`,
  `altitude_assumed_flat`, `mass_kg_assumed`, per-view covariance blobs, `round_idx`, `final_rel_delta`,
  `fit_status`, `support_trust`. PK (year, gp_name, session_type, constructor). Absolute path into MAIN
  checkout (worktree lacks it): `C:/Programs/f1Brainz/data/physics_estimates.db`.
- `src/utils/environment.moist_air_density_from_pressure(pressure_pa, air_temp_c, humidity_pct)` — the
  measured-pressure density fn (Pa not mbar: ×100; raises if <10000). Altitude path is `estimate_air_density_kg_m3` (buggy per memory — avoid).
- `src/physics/layer2/pooling.py` — `PooledParameter` + random-effects DerSimonian–Laird τ² pool +
  `weighted_trend`. REUSE SEAM for Layer 3 field-car trajectory / re-anchor + Layer 4 shrinkage. Handoff
  MUST cite exact signatures (lesson:handoff-cite-exact-seam-signature).
- `data/damage_integrals.db:grip_bin_obs` (per-lap `mu_lat_p90`/`mu_comb_p90`, `tyre_life`, `mass_kg`,
  `rho`) + `damage_lap_integrals` (`cumulative_track_laps`) — finest within-session grip-evolution proxy
  for Layer 2. Absolute path `C:/Programs/f1Brainz/data/damage_integrals.db`. NOTE: race-session weighted.
- Per-year measured Pressure/weather: `C:/Programs/f1Brainz/data/f1_data_<year>.db`.
- Frozen floor + methodology: `docs/physics/624-phase0-baseline-lock.md` (x4 table) +
  `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x4-analysis/normalization_stability.py`
  (the exact reproducible metric to re-run on model output).

## Governing constraints / assumptions
- `constraint:physics_region_no_evo_import` (new modules import no evo).
- F6 held-out mandatory; freeze split + methodology BEFORE looking at held-out. LOO/out-of-sample
  discipline (lesson:loo-residual-diagnostic) — self-weighted smoother is blind to σ-over-claim.
- No `data/*.db` commit (#632); no production-default/gold change; commander runs no multi-hour compute.
- Every layer carries explicit σ (feeds Phase-3 σ-honesty).

## Decision anchors / decision pressure (surfaced to Admiral)
- **DC1 (Layer-2 identifiability):** store granularity is one Q row/car-weekend; true within-session
  rubbering is below it. Build from grip_bin_obs proxy / season-time analog; test honest; report+float if
  it cannot earn its keep. Pre-dispositioned by Pre-Ruling 2 — not a blocker.
- **DC2 (observability router scope):** Phase 2 decomposes the 11 ALREADY-FIT axis outputs, not Phase-1
  segments; the observability router (regime→view evidence routing) is an estimator-fitting concern
  upstream of these outputs, so it is NOT a runtime dependency of this model. Mild deviation from the
  launch order's "use the router" suggestion — recorded, noted in verdict. Overridable.
- **DC3 (held-out split rule):** deterministic weekend holdout (e.g. every Nth round by a frozen rule),
  ≥ a few held-out weekends per car-season so x4's within-car-season SD is computable on held-out. Frozen
  in g1 before any layer is fit.

## Claims / evidence surfaces
- x4 floor table (11 axes, rel/abs noise + weekends-to-resolve) — regression-locked in g1.
- Mexico(low-ρ) vs Monaco(sea-level) density explanation — density secondary check.

## Map confidence / staleness
- High confidence: store schema, environment fn, pooling seam (all read this run). No stale-map risk on
  the greenfield module. No docs/architecture packet covers this new area yet → reconcile records it.

## Out of scope
- Phase 3 unification / cross-view covariance (F5), Phase 3b driver utility, Phase 4 FP, evo injection,
  2026 aero two-state. Layers here carry honest σ but do not close the x7 fractures.
