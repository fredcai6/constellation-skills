# Implementer Handoff

## Gate
g3 — Wire the decoupled-estimator adapter into the production braking frontier, retire the
raw-speed read from the braking path, add the scoreboard terrain handle, repopulate the
EstimateStore, and verify the downforce-pinned braking ceiling. **This is the production wiring
gate** (G2's side-by-side ratified ADOPT-A — user decision Option 2).

## Task
1. **Wire** `decoupled_braking_input` (the G2 adapter) as the production braking-frontier input in
   `session_braking.prepare_braking_frontier`: feed the gravity-free `F_vehicle/m` (+ `theta=0` into
   `BrakingView.fit`) and the per-sample `sigma_a` (→ `sigma_kin`, replacing the broadcast scalar).
   Remove the by-hand `g*sin(theta)` from the braking de-conflation path (gravity is now counted
   once, inside the estimator via the z-map). Variant-A semantics from G2: `F_vehicle/m` + `theta=0`.
2. **Retire** `clean_longitudinal_from_raw` as the **direct braking-frontier input** — ONE canonical
   braking input (the adapter). NOTE: do NOT delete the function; it remains (a) the estimator's
   raw-anchor source *inside* the adapter and (b) the throttle/coast input until G6. "Retire" here =
   `prepare_braking_frontier` no longer calls it directly for the frontier `a_long`; the adapter does.
3. **Terrain handle on the scoreboard** (`scoreboard.CaseInputs`, comment item 4): add an OPTIONAL
   `theta`/`z` pool to `CaseInputs` so the scoreboard's self-test can exercise the total-energy path
   (currently FLAT-only on the scoreboard; real terrain only via the proof driver). Additive/optional —
   existing FLAT cases must stay byte-identical when no terrain is supplied.
4. **Repopulate the EstimateStore** with the wired braking input, into a **NEW store file**
   (preserve the existing one for before/after comparison). Scope: the C1-evaluated constructors
   **RBR, Ferrari, McLaren, Williams, Mercedes** across 2023-Q through the dashboard's max target
   round (confirm rounds from `scripts/driver_utilization_dashboard.py`) — enough for G4's re-eval to
   be apples-to-apples with the #510 CONTEXTUAL baseline. Report the runtime; if a full-season run is
   prohibitive, prioritize RBR (the primary) + report what was covered. estimate_batch is
   idempotent on (year,gp,session,constructor) — FORCE re-estimation (new store) so the OLD braking
   params don't survive.
5. **Verify the downforce-pinned ceiling** (the user's Option-2 condition): the production
   `session_estimator` outer loop pins `b_b` indirectly via the PowerDrag-measured CdA. After
   repopulating, report whether the wired braking ceiling (a_b, b_b + covariance) is physical and
   whether the cold-start ceiling gap from G2 collapsed toward the synthesis. A short comparison
   note suffices — NOT a full re-sweep. Surface to the Commander if the pinned ceiling unexpectedly
   under-calls high-speed braking.
6. **Flag (do NOT edit) the MEASURED→wired map updates** for reconcile: `decision:decoupled_1d_longitudinal`,
   `decision:smoother_rounds_braking_knee`, and the physics packet Known Limits all say
   "MEASURED-not-wired / 0 src importers" — now stale after this wiring. List them in your result's
   Map Impact; the Cartographer updates the architecture docs at the reconcile step (do not edit
   `docs/architecture/` yourself — the map is frozen read-only during execution).

## Protected Intent
The wired braking frontier must deliver the deep, knee-correct floor (the whole point) with honest
per-sample σ, ONE canonical braking input, gravity counted exactly once. The C1 re-eval (G4) depends
on the repopulated store, so the store must be reproducible and comparable to #510.

## Test Mode
Test-after. Update/extend the affected `tests/unit/physics/layer2/` tests for the wired
`prepare_braking_frontier` + the scoreboard terrain handle; keep existing tests green. Physics
evidence: confirm the wired path's braking knee is deep (matches the G2 synthesis a_b) on a spot
circuit; confirm the scoreboard FLAT path is unchanged when no terrain supplied.

## Close Criteria
- `prepare_braking_frontier` uses the adapter (one canonical braking input); `clean_longitudinal_from_raw`
  no longer the direct braking-frontier `a_long` (still present for the adapter's anchor + throttle/coast).
- Gravity counted once (F_vehicle/m + theta=0 into BrakingView for braking); no by-hand g*sinθ double-count.
- Per-sample `sigma_a` carried into `sigma_kin` (no scalar broadcast on the braking path).
- Scoreboard `CaseInputs` accepts optional terrain; FLAT path byte-identical without it.
- A NEW EstimateStore populated with the wired braking input at the C1 scope (old store preserved).
- Pinned-ceiling verification note (Option-2 condition).
- `py -m pytest tests/unit/physics/layer2/ tests/unit/physics/ -q` green; `py -m src.utils.simplification_limits` clean on touched paths.
- Map-impact items (MEASURED→wired) flagged for reconcile (not edited).

## Allowed Scope
- `src/physics/layer2/session_braking.py` (`prepare_braking_frontier`, `run_braking_view_on_session`).
- `src/physics/layer2/scoreboard.py` (`CaseInputs` optional terrain — additive).
- `src/physics/layer2/decoupled_braking_input.py` (adapter — extend if needed for the production seam).
- `src/physics/layer2/braking_view.py` ONLY if the braking de-conflation needs a theta=0 path — but
  prefer passing `theta=0` from the caller rather than changing `BrakingView.fit`'s signature.
- `src/physics/layer2/estimate_batch.py` / `estimate_store.py` / `session_estimator.py` ONLY as needed
  to point the braking view at the adapter and write a new store (prefer injection/parameters over edits).
- `tests/unit/physics/layer2/`, `scripts/` (a repopulation script), `reports/physics/` (gitignored).

## Specific Exclusions
- Do NOT touch `session_traction.py` / `session_coast.py` / their `clean_longitudinal_from_raw` use —
  the throttle/coast views are G5 (characterize) / G6 (productize).
- Do NOT delete `clean_longitudinal_from_raw`.
- Do NOT edit `docs/architecture/` (reconcile/Cartographer owns the map).
- Do NOT touch the utilization layer / `car_prior` / the dashboard (that's G4).

## Constraints
- `py` not `python`.
- ONE canonical path on the braking input (no dual/flagged input left behind).
- Gravity counted exactly once.
- `constraint:physics_region_no_evo_import`; `decision:two_cycle_external_anchor_design` (anchor = TV-denoised RAW a_long).
- Honest covariance first-class (per-sample σ).
- Physics model change → L1-L4 evidence.
- Store repopulation reproducible; preserve the old store.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `session_braking.py`, `braking_view.py`, `scoreboard.py`,
  `decoupled_braking_input.py`, `estimate_batch.py`, `estimate_store.py`, `session_estimator.py`;
  `struct:physics` — `capability_envelope.py` (the ceiling the store feeds).
- **Capability:** per-car capability ceiling — recalibrated via the repopulated store.
- **Constraints:** one canonical path; `decision:two_cycle_external_anchor_design`; `constraint:physics_region_no_evo_import`.
- **Decision anchors:** `decision:decoupled_1d_longitudinal` (→ wired), `decision:smoother_rounds_braking_knee` (retire caveat resolved).
- **Evidence:** scoreboard acceptance preserved on the wired path; store repopulation reproducible; pinned ceiling sensible.

## Exact seams (verified from source)
- Adapter (G2, READ IT): `src/physics/layer2/decoupled_braking_input.py` — `build_decoupled_braking_input`,
  `estimate_driver_braking`, `estimate_lap_longitudinal`, `split_samples_by_lap`, `DecoupledBrakingInput`.
  It already produces per-sample `a_long`/`f_vehicle`/`sigma_a` aligned to classified samples with terrain θ/z.
- `session_braking.prepare_braking_frontier(year, gp, drivers, cache, session, rho, refine, sample_cache) -> BrakingFrontierData(v, a_long, sigma_kin, theta, rho, drivers, samples, raw_p99_decel)`.
  Today it loops drivers, calls `clean_longitudinal_from_raw(spd_d["t"], spd_d["V"], t_s)` per braking sample
  and `gradient_at_positions` for θ. Replace the per-sample a_long/θ with the adapter's `F_vehicle/m` + σ_a;
  pass `theta=0` downstream so BrakingView does not re-subtract gravity.
- `BrakingView.fit(v, a_long, sigma_kin, theta, *, cda_closed, theta_R, mass_kg, rho, prior, ...)` — feed
  `a_long = F_vehicle/m`, `theta = zeros`. (Variant A from G2, gravity-once-verified.)
- `terrain.build_terrain_profile(all_xyz, min_laps=3) -> dict{...}`; `gradient_at_positions(px,py,profile)`;
  `altitude_at_positions(px,py,profile)` (G2-added) for z.
- `estimate_batch.run_estimate_batch(...)` — season driver; `estimate_store.EstimateStore` (standalone SQLite).
  Inspect for the store path + a force/overwrite or new-path option.
- `scripts/driver_utilization_dashboard.py` — confirm the exact circuits/rounds/constructors C1 evaluates.
- `MASS_KG` at `src.physics.longitudinal_fit.MASS_KG` (=808.0).

## Data Locations (absolute; main checkout)
- DB `C:/Programs/f1Brainz/data/f1_data_2023.db`; FastF1 cache `C:/Programs/f1Brainz/data/telemetry` (offline).
- Existing EstimateStore: find its path from `estimate_batch`/`estimate_store` defaults — PRESERVE it; write the new one beside it (e.g. a `_g3wired` suffix).
- Reports → `C:/Programs/f1Brainz/reports/physics/` (gitignored).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/ tests/unit/physics/ -q` (green) + `py -m src.utils.simplification_limits` (clean).
- Spot-circuit confirmation that the wired braking knee matches the G2 synthesis a_b (deep floor preserved).
- The repopulated store (new file) + a short manifest of what was populated + runtime.
- The pinned-ceiling verification note (did the cold ceiling gap collapse?).
- Map-impact list of MEASURED→wired updates for reconcile.

## Suggested Model Tier
Stronger (Opus) — production wiring with the gravity-de-conflation change, the one-canonical-path
requirement, store-repopulation mechanics, and a verification judgment; load-bearing for G4.

## Long-run discipline (store repopulation)
The store repopulation may be long. If you background it: write a state note, and STAY ACTIVE / poll
it to completion — do NOT come to rest while it runs and do NOT declare done until the new store +
all evidence exist. If it would exceed a reasonable wall-clock, narrow to RBR first, report, and
flag the remaining constructors as a continuation.

## Authority
- ADOPT-A and Option-2 (verify pinned ceiling at G3) are the user's decisions (made). You wire it.
- You decide the wiring mechanics + store mechanics within scope. You do NOT edit the architecture map.
- If the pinned ceiling unexpectedly under-calls high-speed braking, STOP and surface it (do not paper over).

## Stop Conditions
Stop and return if: a clean one-canonical-path wiring is impossible without touching excluded code;
the store cannot be repopulated reproducibly; the pinned ceiling reveals a real regression; required
evidence cannot be produced; allowed scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g3-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence (wired-knee spot check, store manifest +
runtime, pinned-ceiling note), assumptions, stop conditions hit, out-of-scope observations, the
MEASURED→wired map-impact list for reconcile, and **Workflow Feedback**.
