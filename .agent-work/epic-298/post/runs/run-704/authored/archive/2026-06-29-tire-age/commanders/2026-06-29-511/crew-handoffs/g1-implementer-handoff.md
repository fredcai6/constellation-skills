# Implementer Handoff — G1 populate batch (module + CLI + smoke)

## Gate
g1 (epic #509, issue #511 W3 tyre-age capstone). Worktree `C:/Programs/f1Brainz-511`, branch `feat/511-tyre-age-evolution`. Use `py`, never `python`.

## Task
Build the race-stint population batch that fills the empty `race_stint_estimates` table by running the W2 fit path over 2023 race stints:
1. **New module `src/physics/layer2/race_stint_batch.py`** (evo-free): discovery + per-(gp,driver) population loop, resumable, loss-proof.
2. **Thin CLI `scripts/populate_race_stint_estimates.py`** wrapping the module.
3. **Unit test `tests/unit/physics/layer2/test_race_stint_batch.py`** over the PURE helpers using synthetic/fixture inputs (no heavy telemetry).
4. **SMOKE PROOF** on real data (2 races) — see Required Evidence.

## Protected Intent
Phase-C MEASURED-not-wired. The W2 modules (`session_race`, `stint_estimator`, `race_stint_store`) and the quali path (`session_estimator`/`EstimateStore`/`session_estimates`) are CONSUMED, not modified. No evo wiring.

## Test Mode
Test-after allowed for the I/O batch loop; the pure helpers (discovery, skip logic, record-from-estimate assembly, error handling) get focused unit tests with synthetic inputs. Real-data smoke is the integration evidence (telemetry/DBs are not in the worktree; use absolute main-checkout paths).

## Close Criteria
- `race_stint_batch.py` exposes a discovery helper (enumerate 2023 race `gp_name`s + their drivers from the per-year SQLite DB) and a population driver that, per (gp, driver): calls `load_race_stints` → `estimate_stint` → `record_from_stint_estimate` → `RaceStintStore.upsert`.
- **Resumable**: skip a (year, gp_name, driver, stint_num, compound) already present via `RaceStintStore.has(...)`.
- **Loss-proof**: on a per-(gp,driver) or per-stint exception, store an `error_record(...)` so the failure is recorded, not dropped; continue.
- **Timestamped progress logging** (HH:MM:SS) per (gp, driver): n stints, n ok, n error.
- Unit test green; `simplification_limits` clean on the new src module + test.
- Smoke writes real rows to `C:/Programs/f1Brainz/data/race_stint_estimates.db` with finite, non-degenerate lateral fits.
- evo-free: the module imports NO `src.evo_predictor`, `src.latent_power`, `src.compound_prior`.

## Allowed Scope
`src/physics/layer2/race_stint_batch.py` (new), `scripts/populate_race_stint_estimates.py` (new), `tests/unit/physics/layer2/test_race_stint_batch.py` (new). Read-only consumption of the W2 modules. Writing rows to `data/race_stint_estimates.db` (sanctioned).

## Specific Exclusions
- Do NOT modify `session_race.py`, `stint_estimator.py`, `race_stint_store.py`, or any quali-path module. If you find a defect in them, STOP and return it (do not patch — the commander floats it).
- Do NOT run the FULL 2023 batch — that is the commander's detached G2 job. Smoke = 2 races only.
- Do NOT commit the `.db` or any generated output.

## Constraints
- `constraint:physics_region_no_evo_import` — race_stint_batch.py imports no evo-region package.
- DB/telemetry-store is the only data source; `py` not `python`.
- `lesson:worktree-untracked-data` — DBs + telemetry store are NOT in the worktree; use the absolute main-checkout paths in Data Locations.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/race_stint_batch.py` (new component-leaf). Consumed seams in `src/physics/layer2/`.
- **Capability:** `purpose:physics_estimation` — race-stint per-driver decay population.
- **Constraints:** `constraint:physics_region_no_evo_import`; `lesson:worktree-untracked-data`.
- **Evidence:** W2 inherited 889 clean 2023 stints — smoke re-confirms per-stint (g0,k) usable on real data; covariance PSD/finite.

## Verified Seams (cite from source — already verified by the commander; re-verify before relying)
- `src/physics/layer2/session_race.py`:
  `load_race_stints(year: int, gp: str, driver: str, *, db_path: str, store_path: str | None = None, min_clean_laps: int = 1) -> list[RaceStintData]`. Returns one `RaceStintData` per stint (ordered by stint_num); returns `[]` for missing session/driver/no-clean-laps; `store_path` defaults to `DEFAULT_STORE_PATH` (the telemetry store). `RaceStintData` fields: `year, gp, driver, stint_num, compound, lap_nums, tyre_life, processed_df, mass_kg, cumulative_track_laps, rho, n_race_laps, n_clean_laps, tyre_life_start, tyre_life_end, sparse`.
- `src/physics/layer2/stint_estimator.py`:
  `estimate_stint(stint, *, k_prior_mu: float = 0.01, k_prior_sigma: float = 0.02, n_boot: int = 30, min_samples: int = 20) -> StintEstimate`. ALWAYS returns a `StintEstimate`; view fields are `None` when a view can't be fit. `.lateral_decay` (g0,k,b_aero, 3×3 covariance) PRIMARY; `.traction_decay` (a0,k,b_aero,3×3) SECONDARY.
- `src/physics/layer2/race_stint_store.py`:
  `RaceStintStore(db_path: str)` (NO default — pass an explicit path). `.upsert(record)`, `.has(year, gp_name, driver, stint_num, compound, session_type='R') -> bool`, `.load(year=None, session_type='R', status=None) -> pd.DataFrame`. Module funcs: `record_from_stint_estimate(est, *, session_type='R', fitted_at=None) -> RaceStintRecord` and `error_record(year, gp_name, driver, stint_num, compound, *, error, session_type='R', fitted_at=None) -> RaceStintRecord`. Table `race_stint_estimates`, PK (year, gp_name, session_type, driver, stint_num, compound).
- Discovery: per-year DB `sessions` table has columns incl. `(year, gp_name, session_type, id)`; `lap_times` has `(session_id, driver_id, lap_number, ...)`. Verify exact column names from `src/data/database.py` / schema before relying. Use read-only sqlite (`mode=ro` URI) for discovery — mirror the `_ro_uri` pattern already in `session_race.py`.

## Data Locations (absolute — worktrees lack untracked inputs)
- Per-year season DB (laps/sessions/compound/tyre_life/track_status): `C:/Programs/f1Brainz/data/f1_data_2023.db`
- Telemetry store (race telemetry): `C:/Programs/f1Brainz/data/telemetry_store.db` (this is `DEFAULT_STORE_PATH`; `load_race_stints` defaults to it — you may omit `store_path`).
- Output store (write here): `C:/Programs/f1Brainz/data/race_stint_estimates.db`

## Required Evidence
1. `py -m pytest tests/unit/physics/layer2/test_race_stint_batch.py -q` green.
2. `py -m src.utils.simplification_limits src/physics/layer2/race_stint_batch.py tests/unit/physics/layer2/test_race_stint_batch.py` clean.
3. evo-free assertion (paste output): `py -c "s=open('src/physics/layer2/race_stint_batch.py').read(); assert not any(x in s for x in ('evo_predictor','latent_power','compound_prior')); print('evo-free ok')"`
4. **Smoke**: run the CLI on Bahrain + one more 2023 race (verify the exact `gp_name` strings from the `sessions` table first), writing to `C:/Programs/f1Brainz/data/race_stint_estimates.db`. Then load the store and REPORT: number of stints fitted ok vs error; the per-stint lateral `g0` and `k` ranges (min/median/max); confirmation that lateral covariances are finite and PSD (eigenvalues ≥ 0) on the ok rows; how many stints hit each compound. Paste the loader output. Plausibility guide (not a gate): lateral g0 ≈ 1.0–1.6 (g-units), k ≥ 0 and small (~0–0.1 /lap).

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_race_stint_batch.py -q
py -m src.utils.simplification_limits src/physics/layer2/race_stint_batch.py tests/unit/physics/layer2/test_race_stint_batch.py
py scripts/populate_race_stint_estimates.py --year 2023 --races Bahrain <second-race> --db C:/Programs/f1Brainz/data/f1_data_2023.db --out C:/Programs/f1Brainz/data/race_stint_estimates.db
```
(Design the CLI args as you see fit; `--year`, a race selector, `--db`, `--out` are the minimum. A full-season run with NO race selector must be supported — the commander runs it in G2.)

## Suggested Model Tier
Simple-bounded → moderate (data plumbing + resumability + real-data smoke). No subtle math.

## Authority
The commander has decided: separate output DB `data/race_stint_estimates.db`; W2 modules are read-only; smoke = 2 races; full run is the commander's. You decide CLI shape, helper decomposition, and logging format. Do not decide to modify W2 modules or to widen scope.

## Stop Conditions
Stop and return if: a W2 module must be modified to make the batch work; the smoke fits are pervasively degenerate (all lateral fits None / non-finite / non-PSD) — that is a coverage-collapse signal the commander must float; required evidence cannot be produced; a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT to `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g1-implementer-result.md`: completed slice, files changed, test mode satisfied, evidence produced (paste the 4 evidence blocks), assumptions used, stop conditions hit, out-of-scope observations, and a **Workflow Feedback** section (what in this handoff/workflow made the work harder than it needed to be).
