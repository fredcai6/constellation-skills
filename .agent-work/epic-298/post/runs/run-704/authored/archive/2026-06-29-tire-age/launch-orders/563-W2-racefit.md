# Launch Order: `cmdr-563 — W2 race-session five-view fit path`

Commanders start cold. Paste, don't point.

## Mission
Issue **#563** (epic #509, tire-age wave W2). Generalize the physics five-view estimator from **quali-only** (`load_quali_session`, per-`(driver, quali)`) to **race-session stints**, producing per-stint grip-vs-tyre-age observations that W3 (#511) will pool to separate tyre from track. **This wave runs in two phases** (see Phase Structure) — a diagnose-first evidence gate that you FLOAT to the Admiral, then the build. Deliverable: per-`(driver, race, stint)` grip-decay observations in a new store table + the session-agnostic fit path + tests, as a merge-ready PR.

## Phase Structure (IMPORTANT — this wave floats mid-run)
- **Phase 1 — diagnose-first, EVIDENCE ONLY (no production code freeze).** Establish on 2023: (1) coverage counts — races × drivers × clean stint-laps, stints per compound; (2) per-stint five-view fit viability — does a single race stint yield a stable fit with usable covariance? (3) identifiability map — the pit-staggered-fleet levers (`same_progress_tire_age_spread` / `same_age_progress_spread` / `distinct_stint_start_bins`, à la `src/compound_prior/identifiability.py`) — are the conditions present to separate tyre vs track in 2023? Then **STOP and FLOAT to the Admiral**: return your findings + a recommended fit-shape — **(A)** per-stint independent fits, or **(B)** joint-hierarchical fallback if per-stint covariance is hopeless. Do NOT freeze the build plan yourself; the Admiral adjudicates the fit-shape (this is the contract's self-adjudicated W2→W3 shaping) and continues you.
- **Phase 2 — build** the adjudicated fit shape: produce the per-stint grip-vs-age observations with covariance, the session-agnostic fit path, and the new store table; tests; readiness.

## Fit shape (the design — Admiral confirms A vs B after Phase 1)
**Per-stint decay fit (B-style default):** fit each view over a stint with tyre-age as a covariate — `frontier = g0·exp(−k·age)` — recovering fresh `g0` + decay `k` per `(driver, race, stint)` **with covariance**, **mass-corrected via W1**. Single managed laps are too thin alone → the unit is the stint (W3 pools many). Layering: **W2 produces** per-stint observations; **W3 separates**.

## W1 dependency — pasted API (verify from source before use)
W1 (#562) is **merged to main** (`5db55d02`). Use `src/physics/mass_model.py`:
- `quali_mass(season: int, team: str | None = None) -> float` — returns season base + nominal quali fuel; `quali_mass(2023) == 808.0`.
- `race_mass(season: int, circuit: str, lap_num: int, n_race_laps: int, track_statuses: Sequence[str|None]|None = None, team: str|None = None) -> float` — **this is what you feed each race lap's mass.**
- `fuel_at_lap(circuit, lap_num, n_race_laps, track_statuses=None) -> float`; `fuel_at_lap_has_status(...)` coverage helper.
- Constants: `SEASON_BASE_KG: dict[int,float]`, `DEFAULT_BURN_PER_LAP_KG=1.8`, `SC_BURN_FRACTION=0.5`, `MAX_FUEL_KG` (110), `TEAM_OFFSETS={}`. Status `"4"` = Safety Car (reduced burn).
- Note: `longitudinal_fit.py:44 MASS_KG=808.0` is the spec_drag unit-convention anchor — leave it; consumers now resolve mass via `quali_mass`/`race_mass`.

## HARD GATE — TrackStatus (Admiral ruling, non-negotiable)
`race_mass`/`fuel_at_lap` accept `track_statuses` but default to `None` (→ silent pure-linear fallback). **You must (a) verify the lap store actually carries per-lap track status (FastF1 `TrackStatus`; "4"=SC, "6"/"7"=VSC), and (b) pass the REAL `track_statuses` into `race_mass` — never silently pass `None`.** If the store lacks `TrackStatus`, the smallest honest fix is to ingest it; if that's infeasible, **STOP and FLOAT** to the Admiral with the evidence (do not ship a silent linear approximation).

## Views / lap selection / output (the design)
- **Views:** lateral-lead (clean instrument), traction-second (vector axis), braking + power-drag characterized (power-drag also = mass/fuel cross-ref), coast diagnostic-only. Produce all five so reliability is visible.
- **Lap selection:** reuse cleanliness filters — green-flag committed laps; exclude in/out/lap-1/SC/VSC/red-flag/invalid; configurable gap-ahead threshold (~1.5 s) for dirty air. Per-channel (aero-sensitive stricter) only if Phase-1 shows it matters.
- **Output:** **new `race_stint_estimates` table** in the same store DB (per-stint grain: stint_id, compound, tyre-age range, fuel/mass, `session_type`, `cumulative_track_laps`, g0+k per view, covariance blobs). Reuse `EstimateStore` plumbing (cov-blob encoding, `_cov_list`, read API); the quali `session_estimates` table (`estimate_store.py:335`) is **untouched**. **Build the interface session-agnostic** (fits race now; schema/interface carry `session_type` + `cumulative_track_laps` so FP/quali plug in later — FP *fitting* stays #513).
- **`cumulative_track_laps`** (field-wide laps run on the circuit up to each lap) is the track-evolution axis W3 needs — compute and store it now.

## Prior art (template, NOT a dependency)
`src/compound_prior` "Unified Tire-Wear Pipeline" already attempted pooled multi-race degradation fits; its `identifiability.py` encodes the exact pit-staggered levers (reuse the *idea*, run them as diagnostics). Its confounds (race_progress fuel-proxy, absolute-C#, lap-time response) are what W1 + the physics grip frontier fix. **Do NOT import `compound_prior`** (evo region) — physics has its own `pooling.py`.

## Prior-Wave Verdicts (pasted)
**W1 / #562 (MERGED, main 5db55d02):** per-context mass model shipped. `mass_model.py` with per-season `SEASON_BASE_KG` (2019–2025), `quali_mass` (2023→808.0, quali pool preserved), SC/VSC-aware `fuel_at_lap`/`race_mass`, empty `TEAM_OFFSETS`. 9 consumers rewired across 7 layer2/utilization files. 50 tests; pyright/arch/docs green. TrackStatus interface built but data-sourcing deferred to you (this wave).

## Pre-Rulings (overridable; say so if overriding)
- New code under `src/physics/` (+ the new store table); reuse `EstimateStore`/`pooling.py`; do NOT import evo (`compound_prior`, `evo_predictor`).
- 2023 first (matches the 2023-Q pool); structure for multi-season.
- Per-stint decay (B-style) is the default unit; the A-vs-B fit-shape is the Admiral's Phase-1 ruling.
- Phase-1 is evidence-only — float before freezing the build.
- TrackStatus hard gate above.
- Honest-null is success: if 2023 can't separate / per-stint fits are hopeless even jointly, that's a complete, documented finding — report it, don't thrash.

## Honest-Null Clause
A measured negative is a complete, successful deliverable — full rigor. **Posture: solid, EXPANDABLE baseline; first build is not the final answer; take nulls in stride, stay confident.**

## Inherited Latitude
- **Delegated to you:** module placement under `src/physics/`, the `race_stint_estimates` schema details, test layout, lap-filter thresholds, fit hyperparameters.
- **Float to the Admiral:** the Phase-1 fit-shape (A vs B) — ALWAYS; TrackStatus unavailable; any need to import evo or touch the quali path destructively; any architecture/boundary change; scope beyond `src/physics/` + the store + tests + docs.

## File Ownership
Sole writer for: the new race-fit module(s), the `race_stint_estimates` store code, their tests, touched docs. cmdr-443 (running in parallel) owns the **evo region** + a neutral metric harness (possibly under `src/common/`) — do NOT touch evo or that harness; you are physics-region. Do NOT commit `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md`/your own `.agent-work/<id>/` on the mission branch.

## Workspace
Worktree **`C:/Programs/f1Brainz-563`**, branch **`feat/563-race-fit-path`**, base **`origin/main` `5db55d02`** (includes W1). Before any git op: `git -C C:/Programs/f1Brainz-563 rev-parse --show-toplevel` must be `C:/Programs/f1Brainz-563` (NOT shared `C:/Programs/f1Brainz`); `git worktree list`. Paste output in your return. *(verify_worktree_isolation.py not vendored — use this rev-parse check; sanctioned by the Admiral.)*

## Inherited Context (lessons + invariants)
- Python is `py`, never `python`. Crew dispatch via the **Agent tool** (no `claude` CLI binary); `run_crew.py` registry + `recover_crews.py` before each dispatch. Engine artifact postconditions **attached, not attested** (review-result to BOTH gN-review and gN-integrate). Compact step: skip with reason. State-note before any detach. **Diagnose-first** (this wave's whole Phase 1). Cite exact seams from source. `loo`-style out-of-sample for any residual/calibration/stability diagnostic over a self-weighted/smoothing predictor (lesson:loo-residual-diagnostic).
- Evidence (physics): `py -m src.utils.simplification_limits` on touched paths; region suite green; honest covariance; units/bounds/invariants explicit. **DB/telemetry-store is the ONLY data source.**
- **CI: pyright baseline-diff gate** — self-verify with `py scripts/pyright_baseline_diff.py` (must show `new=0`) before pushing; local pyright ≠ CI pyright.

## Data Locations (absolute — worktrees lack untracked inputs)
- Telemetry store (race telemetry, all sessions 2018–2026): `C:/Programs/f1Brainz/data/telemetry_store.db` (+ sibling parquet; `DEFAULT_STORE_PATH` is this absolute path).
- Per-year DBs (laps, `compound`, `tyre_life`, lap_number, sector times, **`TrackStatus`** if present, weather): `C:/Programs/f1Brainz/data/f1_data_<year>.db`.
- Quali estimate/fit stores: `C:/Programs/f1Brainz/data/physics_estimates.db`, `physics_fits.db`.
- Read-only; do not delete/mutate anything under `data/`.

## Budget
Sonnet (commander + crews). Phase 1 should be quick (evidence). Verify crew completion from artifacts, not liveness.

## Stop Conditions
Stop and return (float to the Admiral) when: **Phase 1 is complete** (always — float the fit-shape); TrackStatus is unavailable; you'd need to import evo or change the quali path; scope exceeds physics + the store + tests; or you need context not covered. Asking up is always sanctioned.

## Return Shape
**Phase-1 float:** coverage counts + per-stint fit viability + identifiability map + recommended A/B + the TrackStatus availability finding → return to the Admiral.
**Final (Phase 2):** readiness statement + evidence (the per-stint observations produced, covariance honesty, the store table, tests) + PR URL + map-impact + triage candidates + workflow feedback + rev-parse isolation confirmation. Post verdict in your return + a comment on #563. On Windows open the PR via `gh pr create -F <file>`.
