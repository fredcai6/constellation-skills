# Reviewer Handoff

## Gate
`g2` — Race session data loader

## Survey State Location
Create your review survey at `.agent-work/563/g2-review/review.json`.

## What Was Implemented

`src/physics/layer2/session_race.py` (NEW, 286 lines): pure data-loader for race stints. Provides `RaceStintData` frozen dataclass and `load_race_stints(year, gp, driver, *, db_path, store_path=None, min_clean_laps=1) -> list[RaceStintData]`. Also `compute_cumulative_track_laps(session_id, first_clean_lap_num, db_path) -> int`.

`tests/unit/physics/layer2/test_session_race.py` (NEW, 481 lines, 31 tests): mocked unit tests for all fields and constraints.

Commit: `1e21ca28` on branch `feat/563-race-fit-path`.

## How to Inspect the Diff

```bash
cd C:/Programs/f1Brainz-563
git show 1e21ca28 --stat
git diff HEAD~1 -- src/physics/layer2/session_race.py
git diff HEAD~1 -- tests/unit/physics/layer2/test_session_race.py
```

## Task Statement

Implement a pure data-loader `session_race.py` for race stints, producing `RaceStintData` objects with: absolute tyre_life (NOT normalized), per-lap mass computed via `race_mass` with real `track_statuses` from `lap_times.track_status` (NEVER None), `cumulative_track_laps` = count of all field driver-laps before this stint's first clean lap, smoother-fitted `processed_df` for each clean lap. No view fitting, no decay model. No changes to any existing file.

## Close Criteria

- `RaceStintData` dataclass has all required fields: `year`, `gp`, `driver`, `stint_num`, `compound`, `lap_nums`, `tyre_life`, `processed_df`, `mass_kg`, `cumulative_track_laps`, `rho`, `n_race_laps`, `n_clean_laps`, `tyre_life_start`, `tyre_life_end`, `sparse`
- `tyre_life` is ABSOLUTE (NOT normalized / NOT `tyre_life - min(tyre_life)`); code comments document that VER Bahrain 2023 R stint 1 starts at 4
- `mass_kg[i]` = `race_mass(year, gp, lap_nums[i], n_race_laps, track_statuses=all_ts)` where `all_ts` is the REAL track_status sequence from `lap_times`; `track_statuses` is NEVER passed as None
- `cumulative_track_laps` = COUNT of all (driver, lap_number) pairs in `lap_times` for that session where `lap_number < first_clean_lap_num`
- No existing file modified (zero diff on existing files)
- `py -m pytest tests/unit/physics/layer2/test_session_race.py -v` → 31 passed
- `from src.physics.layer2.session_race import load_race_stints, RaceStintData` imports cleanly
- No imports from `src/evo_predictor/`, `src/latent_power/`, `src/compound_prior/`

## Allowed Scope

- `src/physics/layer2/session_race.py` — NEW
- `tests/unit/physics/layer2/test_session_race.py` — NEW
- `src/physics/layer2/__init__.py` — only if `__all__` exists (may be untouched)

## Specific Exclusions

- `src/physics/session_fit.py` — must be untouched
- `src/physics/layer2/estimate_store.py` — must be untouched
- `src/physics/layer2/session_estimator.py` — must be untouched
- `src/physics/mass_model.py` — must be untouched
- Any other existing source or test file — must be untouched

## Constraints the Implementation Must Respect

- No imports from evo/latent_power/compound_prior regions
- No direct FastF1 calls — data via SQLite + TelemetryStore only
- `track_statuses` must be real (from `lap_times.track_status`), never None
- `tyre_life` is absolute — no per-stint normalization
- `n_race_laps` = `max(lap_number)` across all drivers (not hardcoded)
- `cumulative_track_laps` must count ALL driver-laps (not just clean ones) before the stint's first clean lap

## Map Anchors (inbound)

- **Structural:** `src/physics/layer2/session_race.py` (new); `src/data/telemetry_session.py`, `src/data/telemetry_store.py` (imported, not modified)
- **Capability:** `TelemetryStore.read_session(year, gp, 'R')` + `build_db_session(payload)` chain; `race_mass` from `mass_model.py`
- **Constraints/assumptions:** TrackStatus hard gate: `track_statuses` always real; ABSOLUTE tyre_life
- **Decision anchors:** tyre_life NOT normalized; n_race_laps from max(lap_number)
- **Evidence expectations:** test for `track_statuses_never_none`; test for `tyre_life_is_absolute`; test for `cumulative_track_laps_correct`

## Evidence Produced

From IMPLEMENTER_RESULT:
- `py -m pytest tests/unit/physics/layer2/test_session_race.py -v` → **31 passed in 0.57s**
- `py -c "from src.physics.layer2.session_race import load_race_stints, RaceStintData; print('ok')"` → `ok`
- Commit `1e21ca28` on `feat/563-race-fit-path`

## Suggested Model Tier

`sonnet` — bounded, well-specified new file review; verify the constraints, not redesign

## Stop Conditions

Return BLOCK if:
- The diff touches any existing source file
- `track_statuses=None` is ever passed to `race_mass`
- `tyre_life` is normalized (subtracted min or divided by range)
- Any test imports from the real DB or TelemetryStore without mocking
- Import from evo/latent_power/compound_prior detected

## Return Format

Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
