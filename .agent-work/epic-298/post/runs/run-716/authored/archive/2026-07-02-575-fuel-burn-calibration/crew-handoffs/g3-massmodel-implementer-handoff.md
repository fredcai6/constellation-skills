# Implementer Handoff — mass_model per-season max-fuel + burn-rate override (g3)

## Gate
`g3-massmodel` (work-id `575-fuel-burn-calibration`). The pure, DB-free
contract change to `src/physics/mass_model.py` that lets the calibrated
per-(season, circuit) burn rate (stored in the DB by the follow-on gate g4)
be injected, and makes the max-fuel ceiling per-season. This gate does NOT
touch the DB or wire any consumer — it only extends the mass_model API.

## Task
Extend `src/physics/mass_model.py` so that:
1. The regulated **max race-start fuel** is per-season (110 kg for 2019-2025,
   70 kg for 2026), instead of a single flat `MAX_FUEL_KG = 110.0`.
2. `fuel_at_lap` and `race_mass` accept **optional** `burn_per_lap_kg` (and
   `fuel_at_lap` also an optional `max_fuel_kg`) override so a caller that has
   a circuit-calibrated burn rate can inject it. **Defaults must reproduce the
   current behavior exactly** so all existing tests stay green.

`mass_model.py` stays pure arithmetic and DB-free — no imports from the data
region, no DB access. The calibrated values live in the DB and are passed IN by
callers (that wiring is gate g4, out of scope here).

## Protected Intent
- All 50 existing tests in `tests/unit/physics/test_mass_model.py` must stay
  green with their assertions UNCHANGED (you may ADD tests, not weaken existing
  ones). A call to `fuel_at_lap`/`race_mass` WITHOUT the new params must behave
  byte-identically to today for seasons 2019-2025.
- `mass_model.py` remains free of evo-region imports, `fastf1`, and any DB/IO.
- Do not change `DEFAULT_BURN_PER_LAP_KG` (1.8), `SC_BURN_FRACTION` (0.5),
  `NOMINAL_QUALI_FUEL_KG`, `SEASON_BASE_KG`, or `TEAM_OFFSETS` values.

## Test Mode
Test-first for the new behavior (per-season max fuel; override params) — write
the failing test, then implement. Physics-model change → truth-anchored where
applicable (the max-fuel values are cited regulation; the override arithmetic
is analytic/L1).

## Close Criteria
1. **Per-season max fuel.** Add `MAX_FUEL_KG_BY_SEASON: dict[int, float]` =
   `{2019..2025: 110.0, 2026: 70.0}` with a docstring citing the same source
   already recorded in `src/physics/burn_rate_calibration.py`'s
   `FUEL_REGULATIONS` (do NOT import from burn_rate_calibration — keep
   mass_model self-contained; restate the literal + cite). Keep the existing
   `MAX_FUEL_KG = 110.0` as the documented fallback constant for unknown
   seasons. Add `max_fuel_for_season(season: int) -> float` returning
   `MAX_FUEL_KG_BY_SEASON.get(season, MAX_FUEL_KG)` (graceful fallback,
   matching race_mass's existing 2024-base-mass fallback posture).
2. **`fuel_at_lap` overrides.** Add two optional keyword params:
   `burn_per_lap_kg: float | None = None` and
   `max_fuel_kg: float | None = None`. Internally resolve
   `burn = burn_per_lap_kg if burn_per_lap_kg is not None else DEFAULT_BURN_PER_LAP_KG`
   and `max_fuel = max_fuel_kg if max_fuel_kg is not None else MAX_FUEL_KG`,
   and use those in place of the current constants (fuel_start cap AND the
   per-lap green/ SC burn). SC laps still burn at `SC_BURN_FRACTION * burn`.
   Validate the new params: if provided and negative, raise ValueError naming
   the field and value (matches the module's validation posture).
3. **`race_mass` override + per-season max fuel.** Add optional
   `burn_per_lap_kg: float | None = None`. Resolve the season's max fuel via
   `max_fuel_for_season(season)` and pass BOTH `burn_per_lap_kg=burn_per_lap_kg`
   and `max_fuel_kg=<resolved>` through to `fuel_at_lap`. This means a 2026
   `race_mass(...)` now uses the 70 kg ceiling (behavior change for 2026 only;
   2019-2025 unchanged since their per-season max is still 110).
4. **Docstrings** updated for both functions (params, the per-season max-fuel
   behavior, that the override defaults reproduce prior behavior).
5. **New tests** in `tests/unit/physics/test_mass_model.py` (add a class):
   - `max_fuel_for_season`: 2023 -> 110, 2026 -> 70, unknown (2099) -> 110.
   - `fuel_at_lap` with `burn_per_lap_kg`/`max_fuel_kg` overrides gives the
     hand-computed value; without them equals the current default result.
   - `race_mass` for 2026 uses the 70 kg fuel_start cap (hand-computed at a
     high-lap-count circuit where the cap binds); 2019-2025 unchanged.
   - override negative-value ValueErrors.
6. `py -m pytest tests/unit/physics/test_mass_model.py -q` — all green
   (50 existing + new). `py -m src.utils.simplification_limits --paths
   src/physics/mass_model.py tests/unit/physics/test_mass_model.py` — PASS.

## Allowed Scope
- `src/physics/mass_model.py`
- `tests/unit/physics/test_mass_model.py`

## Specific Exclusions
- Do NOT touch the DB, `burn_rate_calibration.py`, `session_race.py`, any
  layer2/utilization module, or any script. Consumer wiring is gate g4.
- Do NOT modify the pre-existing untracked scratch scripts.
- Do NOT change existing constant values or weaken existing test assertions.

## Constraints
- `py` (not python). DB-free, pure arithmetic. No evo/fastf1 imports.
- Backward compatibility: default-arg calls behave exactly as before for
  2019-2025.
- `simplification_limits --paths` must pass (mind the module's line count —
  if adding pushes it over, factor cohesively rather than deleting docs).

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `src/physics/mass_model.py` (the
  per-context car-mass model; existing `SEASON_BASE_KG`/`MAX_FUEL_KG`/
  `fuel_at_lap`/`race_mass`). Documented in
  `docs/architecture/packets/physics.md`.
- **Capability:** physics mass/fuel accounting — gains per-season max fuel and
  an injectable per-circuit burn rate (injection wired in g4).
- **Constraints:** `constraint:physics_region_no_evo_import`; mass_model's
  "pure arithmetic, nothing fitted, DB-free" design intent — preserved (the
  calibrated values are injected by callers, not read here).
- **Decision anchors:** decision pressure `decision:burn_rate_calibration_design`
  — mass_model exposes the override seam; the DB is the source of the calibrated
  values (g4).
- **Evidence expectations:** 50 existing mass_model tests unchanged + green;
  new per-season/override tests; cited max-fuel values match FUEL_REGULATIONS.

## Required Evidence
- `py -m pytest tests/unit/physics/test_mass_model.py -q` output (count green).
- `py -m src.utils.simplification_limits --paths <files>` PASS.
- A short note confirming a default-arg `fuel_at_lap`/`race_mass` call for a
  2023 case returns the identical value pre- and post-change (paste the two
  numbers).

## Verification Commands
```bash
py -m pytest tests/unit/physics/test_mass_model.py -q
py -m src.utils.simplification_limits --paths src/physics/mass_model.py tests/unit/physics/test_mass_model.py
```

## Suggested Model Tier
Stronger — a core physics-contract change consumed widely; backward-compat and
the per-season max-fuel behavior change (2026) must be exactly right.

## Authority
Settled: per-season max fuel (110/70) as cited literals; optional override
params with defaults reproducing current behavior; mass_model stays DB-free
(calibrated values injected by callers in g4); keep `MAX_FUEL_KG` as the
unknown-season fallback. If keeping 50 tests green conflicts with any close
criterion, STOP and report rather than editing existing assertions.

## Stop Conditions
Stop and return if: an existing test can't stay green without changing its
assertion; a criterion would require DB access or breaking mass_model's
purity; a decision beyond this handoff is needed.

## Return Format
IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied,
evidence (test counts + the pre/post identical-value check), assumptions,
stop conditions, out-of-scope observations, workflow feedback.
