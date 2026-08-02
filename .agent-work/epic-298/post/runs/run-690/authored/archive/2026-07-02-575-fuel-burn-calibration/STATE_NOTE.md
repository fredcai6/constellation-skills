# Crash-resume state note — 575-fuel-burn-calibration

- **step:** WIRING mass_model (the culminating change). Committed so far on branch: g1 e97ba638, map 8e52e0bf, nonlinear b016c281, ceiling 423cb171, wet-flag code 938608af + data f801b8f4. g3-massmodel DONE+committed (mass_model per-season MAX_FUEL + overrides; 69 tests; reviewed inline). NOW: g4-wire implementer dispatched (agentId a080243c226c431d8) = new session_fuel_features DB table + populator + resolver (new module src/physics/fuel_features.py) + wire session_race to inject calibrated burn_per_lap_kg. Critical property: resolver falls back to DEFAULT_BURN_PER_LAP_KG on unpopulated DB → session_race tests stay green (no-op), real numerics change only vs populated DBs. After g4: review, then resume/finish spine closeout + decide PR strategy for the sprawling branch.
- **design (user-ratified):** per-(season, circuit) granularity, stored in DB, override approach (mass_model stays pure; callers resolve+pass). User acknowledged downstream live numerics change (layer2/W3/utilization); stored-artifact re-batch already deferred to follow-up.
- **spine status:** #575 spine paused mid-`review` (pre-wiring closeout deferred until user done iterating). Prior spine steps done through reconcile + triage(partial, issue #576 filed).
- **slug:** work-id 575-fuel-burn-calibration, branch feat/575-fuel-burn-calibration, worktree C:/Programs/f1Brainz (no separate worktree — main checkout)
- **next command:** check for agent completion notification (agentId a8a9bbe06c5d02915); once done, attest spine reconcile.c1, advance reconcile, then proceed to triage (load constellation-triage in this context) → review → feedback → archive
- **pid:** none — external dispatch (Agent tool subagent)
- **expected artifact:** Cartographer's summary of docs/architecture/ changes (no fixed file path — subagent reports back in its result message)

_Updated: 2026-07-01T18:31:51Z (G1 gate closed + committed; reconcile dispatched, awaiting subagent completion)_
