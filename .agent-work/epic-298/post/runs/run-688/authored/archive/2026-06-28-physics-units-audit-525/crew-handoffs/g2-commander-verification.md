# Commander verification note — #525 G2 rework (attempt-2)

The crew (attempt-2, Opus) **idled mid-step** ("waiting for m8 advance") and wrote a **STALE
result file** (`g2-implement-result.md` describes only the FIRST pass — it wrongly says
"field names unchanged" and omits the rename + migration). I ground-truthed the actual tree
state. **Do not rely on the result-file prose; verify against the diff + this note.**

## Actual state (commander-verified 2026-06-27)

1. **The full semantic rename DID land** across src + tests (81 files, +1393/−1300). Confirmed
   the store dataclasses renamed: `EstimateRecord` now has `lateral_mech_grip_g`,
   `lateral_aero_grip_g`, `max_power_w`, `brake_decel_ms2`, `traction_accel_ms2`,
   `drag_area_closed_m2` (+ `_sigma` companions); new names span 18 src/physics files.
2. **Full suite GREEN — I re-ran it myself:** `639 passed, 6 skipped` over
   `tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py`.
3. **The store migration was BUILT but NOT RUN by the crew** (the strand). The 3 real on-disk
   stores still had OLD columns. **I ran it** (`scripts/migrate_physics_store_columns_525.py`,
   after backing the DBs up to `*.pre525bak`):
   - Run 1: **61 columns renamed** across `physics_estimates.db` (24), `physics_estimates_g3wired.db`
     (24), `physics_fits.db` (13).
   - Run 2: clean **idempotent no-op** (61 already-migrated).
4. **C1 read+pool path verified on the migrated store:** raw read = 220 rows, all new columns
   present, zero old columns, data intact (216/220 non-null `lateral_mech_grip_g` — matches the
   known 2023-Q store). `EstimateStore('data/physics_estimates.db').load()` → 216 rows with new
   columns; `pool_driver.pool_store(df, year=2023, session_type='Q')` → `StorePooling` OK.
5. **theta_D unit reconciled:** crew used `spec_drag_m2_kg` (m²/kg) — the correct derived unit.

## Remaining old-name tokens in src/physics (~166)
Spot-checked: predominantly **docstring/formula-explanation references** (`mu = A0 + A2·v²`,
`p_max/MASS_KG`) and **return-dict string keys** (`{"a_b": ..., "A0": ...}`). The green suite
indicates no half-renamed *code* seam, but the reviewer should confirm the dict-key keys aren't
a missed internal contract (consumed-by-name elsewhere) and that all survivors are legit.

## Caveats for review
- The implementer **result file is stale** — review the DIFF, the suite, and the migration, not
  the result prose.
- The migration **mutated the untracked on-disk DBs** (expected — the renamed code needs the
  renamed columns); backups at `data/*.pre525bak` (untracked; removed at archive).
- Re-confirm `simplification_limits` on touched paths (crew reported 10 pre-existing violations).
