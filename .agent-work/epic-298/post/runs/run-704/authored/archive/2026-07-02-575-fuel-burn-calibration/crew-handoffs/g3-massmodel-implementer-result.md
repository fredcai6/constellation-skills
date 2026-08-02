# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-massmodel` (work-id `575-fuel-burn-calibration`) — pure, DB-free mass_model
contract change: per-season max-fuel table + optional burn/max-fuel overrides.

## Completed slice
`src/physics/mass_model.py` gained a per-season max race-start fuel table
(`MAX_FUEL_KG_BY_SEASON` = 110 kg for 2019-2025, 70 kg for 2026), a
`max_fuel_for_season(season)` helper (graceful fallback to `MAX_FUEL_KG`), and
optional `burn_per_lap_kg` / `max_fuel_kg` overrides on `fuel_at_lap` plus
`burn_per_lap_kg` on `race_mass`. `race_mass` now resolves the season ceiling
via `max_fuel_for_season` and forwards it. Defaults reproduce prior behavior
exactly. All close criteria met; no stop conditions hit.

## Scope
**Files changed:**
- `src/physics/mass_model.py`
- `tests/unit/physics/test_mass_model.py`

**Specific exclusions touched:** `no` — DB, `burn_rate_calibration.py`,
`session_race.py`, consumers, and untracked scratch scripts were all left
untouched. `burn_rate_calibration.py` was read only (for the citation) and not
imported or modified.

## Behavior changed
`yes` — (1) new optional override seam on `fuel_at_lap`/`race_mass`; (2)
per-season max-fuel: a 2026 `race_mass` now uses the 70 kg ceiling where the cap
binds. 2019-2025 default-arg calls are byte-identical to before (their
per-season max is still 110 kg and the default burn/max constants are unchanged).

## Map Impact
- **Structural anchors touched:** `struct:physics` — `src/physics/mass_model.py`:
  added constant `MAX_FUEL_KG_BY_SEASON`, function `max_fuel_for_season`, and two
  optional keyword params each on `fuel_at_lap`/`race_mass`. No new module, no
  new import edges. Packet `docs/architecture/packets/physics.md` describes the
  existing symbols; the new symbols extend the same surface (not updated here —
  Cartographer reconcile).
- **Capabilities added/changed/affected:** physics mass/fuel accounting now
  carries a per-season max-fuel ceiling and an injectable per-circuit burn seam
  (injection itself is g4). Observable per "Behavior changed" above.
- **Constraints/assumptions touched:**
  `constraint:physics_region_no_evo_import` and mass_model's "pure arithmetic,
  DB-free" intent — both HONORED. The 70-kg 2026 literal restates
  `FUEL_REGULATIONS.max_race_start_fuel_kg` by copy + citation, not import.
- **Decision candidates / resolved decisions:**
  `decision:burn_rate_calibration_design` — mass_model now exposes the override
  seam; the DB stays the source of calibrated values (wired in g4). No new
  decision forced.
- **Claims/evidence produced:** cited max-fuel values (110/70) match
  `FUEL_REGULATIONS`; 50 existing tests unchanged + green; identical-value check
  passes (below).
- **Triage candidates:** none.

## Test mode
**Required:** `test-first` (per handoff: write failing test, then implement;
truth-anchored — max-fuel values are cited regulation, override arithmetic is
analytic/L1).
**Satisfied:** `yes` — new test classes written and observed failing (ImportError
collection error) before implementation; then implemented to green. Existing 50
assertions untouched.

## Evidence

```bash
py -m pytest tests/unit/physics/test_mass_model.py -q
```
**Result:** `pass` — `69 passed in 0.18s` (50 existing unchanged + 19 new).

```bash
py -m src.utils.simplification_limits --paths src/physics/mass_model.py tests/unit/physics/test_mass_model.py
```
**Result:** `pass` — `PASS (2 files checked)`.

Identical-value check (2023 default-arg call, pre vs post change):

| call | pre-change | post-change |
|---|---|---|
| `fuel_at_lap('Spa', 20, 44)` | `43.20000000000006` | `43.20000000000006` |
| `race_mass(2023, 'Spa', 20, 44)` | `841.2` | `841.2` |

Identical. Purity check: no `fastf1` / `database` / `DatabaseManager` /
`evo_predictor` / `burn_rate_calibration` / `sqlite` imports in mass_model.py
(only docstring mentions).

## TDD evidence, if required
- Failing test observed:
  `py -m pytest tests/unit/physics/test_mass_model.py -q -k 'PerSeasonMaxFuel or Override'`
  → `ImportError: cannot import name 'MAX_FUEL_KG_BY_SEASON'` → 1 error during
  collection (RED).
- Passing test observed: full file `69 passed` after implementing the table,
  helper, and override params (GREEN).
- Refactor while green: `no` (minimal change; nothing to refactor).

## Docs/contracts touched
- Module docstring + `MAX_FUEL_KG` / `MAX_FUEL_KG_BY_SEASON` /
  `max_fuel_for_season` / `fuel_at_lap` / `race_mass` docstrings updated in-file.
- No external docs (`docs/architecture/packets/physics.md`) edited — out of this
  gate's scope; flagged in Map Impact for Cartographer reconcile.

## Assumptions
- Chose the cap-binding demonstration circuit as a generic 70-lap race
  ("Monza"/"Spa" as opaque circuit-name strings; `circuit` is unused in the
  arithmetic). 2026 base mass is absent from `SEASON_BASE_KG`, so `race_mass`
  falls back to the 2024 base (798.0) per the existing graceful-fallback posture
  — the 2026 tests assert against `SEASON_BASE_KG[2024]`, so they stay correct if
  a 2026 base is added later (the fuel-ceiling behavior under test is
  independent of the base).
- Interpreted "SC laps still burn at SC_BURN_FRACTION * burn" as
  `SC_BURN_FRACTION * resolved_burn` (the overridden rate), and added a test
  pinning that.

## Stop conditions hit
- `none` — no existing assertion needed changing; no DB access or purity break
  required; no decision beyond the handoff surfaced.

## Out-of-scope observations
- Consumer wiring (passing a DB-calibrated per-circuit burn rate and the
  per-season ceiling into `race_mass`/`fuel_at_lap`) is gate g4 as stated — not
  done here.
- `docs/architecture/packets/physics.md` will want the two new public symbols
  (`MAX_FUEL_KG_BY_SEASON`, `max_fuel_for_season`) recorded at Cartographer
  reconcile.

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** minor — the RED-gate assertion (that the new tests fail
  before implementation) is satisfied by a collection-level `ImportError` rather
  than per-test failures, because the new class shares the module's single
  top-of-file import block. That's the honest red signal for an added-symbol
  change, but a handoff that expected per-test red would have been slightly
  mismatched. Not blocking.
- **Context rediscovered:** the exact `FUEL_REGULATIONS` citation wording (70 kg
  = energy-based limit / Advanced Sustainable Fuel) had to be read from
  `burn_rate_calibration.py`; the handoff pointed at it correctly but did not
  quote it, so a read was needed to restate-not-import faithfully. A one-line
  quote in the handoff would have saved the lookup.
- **Instructions improvised around:** the engine `attest` verb defaults to
  `--which preconditions`; satisfying a `check: null` **postcondition** on the
  context step required `--which postconditions`, which the skill text mentions
  but the plan template does not flag. Handled per the workbench memory note.
- **What would have made this easier:** nothing material — the handoff was
  self-contained, close criteria were unambiguous, and the hand-computed
  expected values matched on first run.

## Return status
`complete`
