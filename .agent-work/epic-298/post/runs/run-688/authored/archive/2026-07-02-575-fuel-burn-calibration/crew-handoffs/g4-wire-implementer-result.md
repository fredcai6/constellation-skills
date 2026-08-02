# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-wire` (work-id `575-fuel-burn-calibration`) — DB-stored per-session burn rate + resolver + wiring.

## Completed slice
Stores the calibrated per-(season, circuit) dry burn rate per race session in a
new `session_fuel_features` DB table, adds a populator + a runtime resolver in a
NEW module `src/physics/fuel_features.py`, and wires
`src/physics/layer2/session_race.load_race_stints` to inject the resolved rate
into `race_mass` via the g3 `burn_per_lap_kg` seam. The resolver returns
`mass_model.DEFAULT_BURN_PER_LAP_KG` (1.8) on any unpopulated DB, so the wiring
is a byte-identical no-op on synthetic test DBs and only changes numerics
against the real populated season DBs. All 8 season DBs (2019-2026) populated
(167 race sessions); one real dry before/after delta captured.

## Scope
**Files changed:**
- `src/data/schema.sql` — new `session_fuel_features` table (after `session_surface_features`)
- `src/data/database/_core.py` — mirrored the table via new module-level helper `_ensure_session_fuel_features(conn)`, called from `_apply_schema_upgrades` (helper extraction keeps `_apply_schema_upgrades` under the 100-line function cap and matches the `_ensure_session_surface_features` convention)
- `src/data/database/_ingest.py` — new `upsert_session_fuel_features(...)` (INSERT..ON CONFLICT(session_id) DO UPDATE) + `get_session_fuel_features(session_id=None) -> DataFrame`
- `src/physics/fuel_features.py` — NEW module: `resolve_race_burn_rate(year, gp, *, db_path) -> (float, str)` + `populate_fuel_features_for_db(year, *, db_path, store_path=None, wet_threshold=WET_EXCLUDE_THRESHOLD, verbose=True)`
- `scripts/populate_fuel_features.py` — NEW CLI (2019-2026 sweep / `--year` / `--years`, `--quiet`); prints coverage + resolved reference-circuit rates
- `src/physics/layer2/session_race.py` — imported `resolve_race_burn_rate`; resolve once per (year, gp); passed `burn_per_lap_kg=<resolved>` into the single real `race_mass` call; updated the `mass_kg` docstring
- `tests/unit/physics/test_fuel_features.py` — NEW (12 tests: resolver fallback chain + populator)
- `tests/unit/data/test_fuel_features_db.py` — NEW (5 tests: accessor round-trip + non-clobbering ON CONFLICT)
- `data/f1_data_{2019..2026}.db` — populated the `session_fuel_features` rows (167 sessions)

**Specific exclusions touched:** No. `mass_model.py`, `burn_rate_calibration.py`, and the untracked scratch scripts were NOT modified (confirmed via `git status`). No estimate/stint batch populator was re-run.

## Behavior changed
Yes. On a POPULATED season DB, `load_race_stints` now computes `mass_kg` with
the calibrated per-circuit dry burn rate instead of the flat 1.8 default (the
intended live W3 tyre-age-path change). On an UNPOPULATED DB (no table / no
measured rows) the resolver returns 1.8, making the change a byte-identical
no-op — the existing `test_session_race.py` suite (incl.
`test_mass_kg_values_match_race_mass`) passes UNCHANGED.

## Map Impact
- **Structural anchors touched:** `struct:data` — `schema.sql` + `database/{_core,_ingest}.py` gained the `session_fuel_features` table + two accessors + the `_ensure_session_fuel_features` helper. `struct:physics` — new `fuel_features.py` (reads `burn_rate_calibration` + `mass_model`, writes via `DatabaseManager`). `struct:physics.layer2` — `session_race.py` is the wired live consumer.
- **Capabilities added/changed/affected:** physics mass/fuel accounting now injects the calibrated per-(season, circuit) burn rate into `race_mass` on the live W3 race-stint path (matches inbound Capability anchor).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honored (module imports only physics + data, no evo/fastf1). `mass_model` stays DB-free (the resolver, not mass_model, reads the DB). Data does not import physics (the populator's `DatabaseManager` import lives in the physics module). The backward-compat no-op property (Protected Intent) is honored and explicitly verified.
- **Decision candidates / resolved decisions:** `decision:burn_rate_calibration_design` realized — per-(season, circuit), DB-stored, injected via the g3 override seam; fallback chain session -> season_mean -> global default (1.8). Cross-year rescaled circuit fallback is deliberately NOT in this gate (season_mean is the wet-race fallback) — noted as a future refinement (see Out-of-scope).
- **Claims/evidence produced:** reference-circuit rates reproduce the handoff's expected shape (Bahrain ~1.72, Spain ~1.47, GB dry-year ~1.79, Monaco dry ~1.0); wet races (GB 2024/2025, Monaco 2020/2022/2023) resolve to season_mean, not their own wet value. Backed by the populate output + the before/after delta below.
- **Trust limitations / drift found:** none new in the map. `session_race.py` carries pre-existing plain-mode simplification violations (see Out-of-scope) untouched by this change.

## Test mode
**Required:** test-first for the resolver fallback chain + pure detection/aggregation; test-after acceptable for the populator plumbing; explicit no-op verification for session_race.
**Satisfied:** Yes. Resolver tests written first and observed RED (ImportError on the missing module) then GREEN. Populator tests use mocked `season_burn_rate_estimate`/`session_wet_fraction`. The session_race no-op is verified by the existing 31-test suite passing UNCHANGED (no test edited).

## Evidence

```bash
# 1. Combined suite (existing session_race green unchanged + new green)
py -m pytest tests/unit/physics/layer2/test_session_race.py tests/unit/physics/test_fuel_features.py tests/unit/data -q
# -> 157 passed  (31 session_race unchanged, 12 fuel_features, 5 fuel_features_db, + rest of data dir incl. wet_features/telemetry_store — no regressions)

# 2. Populate the real DBs (2019-2026) + resolved reference rates
py scripts/populate_fuel_features.py
# -> done -- 167 race session(s) populated across 8 season(s)

# 3. Canonical simplification gate (repo canonical = --baseline mode, per TESTING.md)
py -m src.utils.simplification_limits --baseline --paths src/data/database/_core.py src/data/database/_ingest.py src/physics/fuel_features.py scripts/populate_fuel_features.py src/physics/layer2/session_race.py tests/unit/physics/test_fuel_features.py tests/unit/data/test_fuel_features_db.py
# -> PASS (7 files checked)
# Plain-mode on the 6 g4-new/modified files (excluding pre-existing session_race debt):
py -m src.utils.simplification_limits --paths src/data/database/_core.py src/data/database/_ingest.py src/physics/fuel_features.py scripts/populate_fuel_features.py tests/unit/physics/test_fuel_features.py tests/unit/data/test_fuel_features_db.py
# -> PASS (6 files checked)
```

**Result:** pass (all three).

### Resolved reference-circuit rates (from populate output)
```
2019 Bahrain 1.751 session | Spain 1.489 session | Great Britain 1.846 session | Monaco 1.012 session
2020 Bahrain 1.719 session | Spain 1.465 session | Great Britain 1.817 session | Monaco 1.627 season_mean(wet)
2021 Bahrain 1.762 session | Spain 1.469 session | Great Britain 1.790 session | Monaco 1.032 session
2022 Bahrain 1.730 session | Spain 1.426 session | Great Britain 1.809 session | Monaco 1.621 season_mean(wet)
2023 Bahrain 1.724 session | Spain 1.474 session | Great Britain 1.791 session | Monaco 1.646 season_mean(wet)
2024 Bahrain 1.738 session | Spain 1.453 session | Great Britain 1.619 season_mean(wet) | Monaco 1.031 session
2025 Bahrain 1.709 session | Spain 1.436 session | Great Britain 1.568 season_mean(wet) | Monaco 1.008 session
2026 Bahrain 1.039 season_mean | Spain 1.039 season_mean | Great Britain 1.039 season_mean | Monaco 0.690 session
```
Matches the handoff's expected shape: dry circuits get their measured `session`
rate; wet races (GB 2024/2025, Monaco 2020/2022/2023) fall back to `season_mean`
(NOT their own wet value). 2026 Bahrain/Spain resolve to `season_mean` because
those rounds didn't run in 2026 (Bahrain/Saudi dropped) so there's no session
row; 2026 Monaco (0.690) reflects the lower 2026 energy-based flow cap (70 kg/h).

### Row-source breakdown (all seasons)
```
2019 total=21 measured=20 wet_skipped=1
2020 total=17 measured=16 wet_skipped=1
2021 total=22 measured=18 wet_skipped=4
2022 total=22 measured=18 wet_skipped=4
2023 total=22 measured=20 wet_skipped=2
2024 total=24 measured=21 wet_skipped=3
2025 total=24 measured=21 wet_skipped=3
2026 total=15 measured=7  no_telemetry=8   (2026 season telemetry partial)
```

### Before/after live delta (the intended live change)
```
case            : 2023 Bahrain VER
n_race_laps     : 57
first_clean_lap : 3
resolved rate   : 1.7236 kg/lap  (source=session)
default rate    : 1.8000 kg/lap
mass_kg[0] BEFORE (flat 1.8) : 897.0000 kg
mass_kg[0] AFTER  (resolved) : 892.7959 kg
delta           : -4.2041 kg
```
Confirms the wiring changes real output against a populated DB (helper script:
`.agent-work/575-fuel-burn-calibration/g4-implementer/before_after_delta.py`).

### No-op property (session_race)
`test_session_race.py` = 31 passed UNCHANGED (no test edited). The synthetic
fixture DBs have no `session_fuel_features` table, so the resolver returns 1.8
and `race_mass(..., burn_per_lap_kg=1.8)` is byte-identical to the prior default
— `test_mass_kg_values_match_race_mass` stays green.

## TDD evidence, if required
- Failing test observed: `py -m pytest tests/unit/physics/test_fuel_features.py -q -k resolve` -> `ImportError: cannot import name 'fuel_features'` (module not yet created) — RED.
- Passing test observed: after creating `src/physics/fuel_features.py` -> `7 passed, 5 deselected` (resolver subset), then `12 passed` (full file) — GREEN.
- Refactor while green: yes — extracted `_ensure_session_fuel_features` in `_core.py` to keep `_apply_schema_upgrades` under the function-line cap, tests stayed green.

## Docs/contracts touched
- `src/physics/layer2/session_race.py` `RaceStintData.mass_kg` docstring updated to note the burn rate is resolved via `fuel_features.resolve_race_burn_rate` (calibrated rate or the DEFAULT no-op fallback). No committed report-schema change (the new table is a derived internal feature, not a committed report schema).

## Assumptions
- A None / un-graded wet fraction is treated as DRY (the measured path) — the populator never fabricates a wet flag. (Documented in the populator docstring; covered by `test_wet_fraction_none_treated_as_dry`.)
- The "season mean" in fallback step 2 is the mean of ALL `source='measured'` rows in that DB (season-wide), not a per-region or per-compound subset — as the handoff specifies (`the mean of that DB's source='measured' est values`).
- Canonical simplification gate is `--baseline` mode (per TESTING.md / engine-config tenet "verify_simplification_limits is the canonical check"); plain `--paths` mode enforces function-level caps that session_race.py already violated on HEAD.

## Stop conditions hit
- None. The no-op property held on the first wiring attempt (31/31 session_race tests green unchanged); region layering held (physics imports data, data does not import physics); no batch re-run was required; no decision beyond the handoff was needed.

## Out-of-scope observations
- **Pre-existing `session_race.py` simplification debt (NOT introduced here):** plain-mode `simplification_limits` flags `_fit_driver_laps` (cyclomatic=20, 117 lines — untouched by g4) and `load_race_stints` (cyclomatic=23, function_lines grew 215->227 from the minimal wiring — but complexity unchanged and already over-cap on HEAD). Both violate on the pristine HEAD checkout; the canonical `--baseline` gate passes. Refactoring the 227-line `load_race_stints` to <100 lines would restructure the closed-W3 live path — out of g4's minimal-wiring scope. Candidate: a follow-up to split `load_race_stints` / `_fit_driver_laps`.
- **Cross-year rescaled circuit fallback** (a wet race borrowing a rescaled dry rate from an adjacent-year running of the same circuit) is a documented future refinement — this gate uses same-DB `season_mean` as the wet-race fallback, per the handoff's Authority note.
- **Stored-artifact re-batch** (`race_stint_estimates.db` etc.) is a separate deferred follow-up per the handoff; not done here.

## Workflow Feedback
- **Handoff gaps:** The handoff was thorough and self-contained. One under-specified point: the Verification-Commands note says "`simplification_limits` only checks `.py` files; drop `schema.sql`" but does not mention that plain `--paths` mode enforces function-level caps that `session_race.py` (the wiring target) ALREADY violates on HEAD. The required-evidence bullet "`simplification_limits ... PASS`" reads as achievable in plain mode, but the canonical repo gate is `--baseline` mode. Naming the intended mode (baseline vs plain) in the handoff would have removed the ambiguity of whether pre-existing session_race debt blocks the gate.
- **Context rediscovered:** I had to discover that the repo's canonical simplification gate is `--baseline` mode (from `src/utils/simplification_limits.py` internals: `--baseline` restricts `active_metrics` to `["file_lines"]`, skipping function-level checks) and that `session_race.py`'s function violations pre-date g4. The Map Anchors could have carried "session_race.py is a known-large legacy file already over the plain-mode function caps" so an implementer doesn't rediscover it.
- **Instructions improvised around:** (1) The IMPLEMENTER_PLAN template's artifact-postcondition example was thin — the engine's `artifact` check requires `evidence_type` (not `artifact_type`) in the check spec; my first plan used `artifact_type` and the engine threw `KeyError: 'evidence_type'`. I corrected the field. Worth documenting the exact artifact-check key in the checklist-engine reference. (2) A `git stash` I ran to measure the pristine baseline FAILED to reset the working tree (a `data/*.db` file was locked by a concurrently-running populate) yet still created a stash entry that silently removed my tracked-file edits while leaving untracked new files — I recovered by `git checkout stash@{0} -- <the 4 source files>` then `git stash drop`. Lesson (already in CREW_CONTEXT via "worktree not stash" memory, but worth reinforcing): do NOT `git stash` in this repo while a DB-touching job runs; measure baseline via `git show HEAD:<path>` into a temp path UNDER the repo (the tool ignores paths outside src/tests) instead.
- **What would have made this easier:** Add one line to the handoff's Verification section: "run `simplification_limits` in `--baseline` mode (the canonical gate); `session_race.py`'s plain-mode function-cap violations are pre-existing on HEAD and out of scope."

## Return status
`complete`
