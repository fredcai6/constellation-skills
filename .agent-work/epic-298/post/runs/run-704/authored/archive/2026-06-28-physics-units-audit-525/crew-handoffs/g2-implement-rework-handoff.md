# Implementer Handoff — #525 G2 REWORK (full semantic rename + store migration)

## Gate
g2-implement (rework 1/3) — issue #525, branch `feat/physics-units-audit-525`

## Why a rework
The first G2 pass delivered unit **comments/headers** but **not the renamed field names**. The
human then **expanded** the scope: do a **full semantic rename** of the cryptic physics
parameter vocabulary (`A0`, `A2`, `theta_*`, `a_b`, `b_b`, `a_t`, `b_t`, and single-letter fit
locals) so every name says **what it is + what unit space it's in**.

## Authoritative inputs (READ FIRST, in order)
1. `.agent-work/525/NAMING_TABLE.md` — **the binding rename spec** (approved names, convention,
   the producer-`_g`/consumer-`_ms2` rationale, and the store-migration approach).
2. `.agent-work/525/AUDIT_MAP.md` — exact `file:symbol`+line for every parameter at every
   producer/consumer (use it to find all rename sites; verify unit tokens against it).
3. `.agent-work/525/crew-handoffs/g2-implement-result.md` — what the FIRST pass already landed.

## What already landed (KEEP IT — do not redo or revert)
GRAVITY_MS2/MASS_KG dedup, density fallback = 1.225, friction_coupling removal, OT-6 comment-fix
at `car_prior.py`, the unit headers, and the output-level guard in
`tests/known_answer/test_published_f1_data.py`. These are correct and reviewed-modulo-the-rename.

## Task (the rework additions, ON TOP of what landed)
1. **Full rename to the NAMING_TABLE targets.** Rename every physics parameter field
   (`A0`→`lateral_mech_grip_*`, `A2`→`lateral_aero_grip_*`, `theta_P*`→`specific_power_w_kg`,
   `p_max`→`max_power_w`, `cda_*`→`drag_area_*_m2`, `theta_D*`→`spec_drag*`,
   `theta_R`→`rolling_decel_ms2`, `a_b/b_b`→`brake_decel_ms2`/`brake_aero_decel_per_m`,
   `a_t/b_t`→`traction_accel_ms2`/`traction_aero_accel_per_m`, terrain `theta/z/bank`, etc. —
   full table in NAMING_TABLE.md) across: the producers, **both** stores' dataclasses
   (`EstimateRecord`, `FitRecord`), the consumers (`LateralParameters`, `LongitudinalParameters`,
   `BrakingParameters`, `TractionParameters` + every reader), the **fit-local variables** (the
   `a`/`b`/`A`/`B` inside the fit functions — the user explicitly dislikes these), and **ALL
   tests/fixtures**. Consistent producer→store→consumer; **no half-renamed seam**.
   Behaviour-preserving — a rename, never a formula change.
   - **Unit token = the source-verified unit** (esp. `spec_drag`/`theta_D` — reconcile the
     AUDIT_MAP unit vs the derived dimension and use the correct token; note it in the header).
   - **`_g` vs `_ms2` is intentional** (producer/store = density-agnostic g-coefficient for
     poolability; consumer = per-session m/s²). Keep both spaces; the conversion stays at the
     one `car_prior` seam. (See NAMING_TABLE rationale.)
2. **`_sigma`/`_std` companions rename in lockstep** with their base field
   (`A0_sigma`→`lateral_mech_grip_g_sigma`, etc.).
3. **SQLite store column migration.** The `session_estimates` / `fit_store` **column names
   auto-derive from the dataclass field names**, so renaming the fields renames the columns and
   the existing populated DBs stop being readable. Ship an **idempotent** migration at
   `scripts/migrate_physics_store_columns_525.py` that does `ALTER TABLE <t> RENAME COLUMN <old>
   TO <new>` for **every** renamed column (incl. `_sigma`) on the three on-disk stores
   (`data/physics_estimates.db`, `data/physics_estimates_g3wired.db`, `data/physics_fits.db`),
   **safe to re-run** (skip already-migrated columns), with a short docstring. Then **run it**
   and verify `pool_driver`/`car_prior` read the renamed columns and the C1 read path still
   loads (e.g. a quick `EstimateStore.to_dataframe()` / `pool_store` smoke).
4. **Convention B preserved:** the consumer m/s² **math is untouched** — these are
   behaviour-preserving renames, NOT formula changes. The full green suite is the proof.
5. **Guard docstring fix:** make the guard's docstring band text match the actual asserts
   (the "300–360" vs `[250,500]` and "15–60" vs `[15,80]` inconsistencies the reviewer flagged).

## Protected Intent
**No behaviour regression.** Renames preserve behaviour; the C1 utilization numbers and the
sim outputs must not move. The store migration preserves data (no recompute).

## Test Mode
test-after for the renames (the suite is the safety net — it MUST stay green, proving
behaviour-preserving); the migration needs its own idempotency + read-back verification.

## Close Criteria
- Every NAMING_TABLE field renamed everywhere (producers, stores, consumers, fit locals, tests);
  no old name survives except where it is a real external token. Grep the old names to confirm:
  `git grep -nw "A0\|A2\|theta_P_values\|p_max\|a_b\|b_b\|a_t\|b_t" src/ tests/` → only
  intended/explained survivors.
- `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q` GREEN.
- `py -m src.utils.simplification_limits --paths <touched>` clean.
- `py scripts/migrate_physics_store_columns_525.py` runs idempotently (twice in a row, second is a no-op) on the 3 DBs; a post-migration read of the estimate store + the C1 read path works.
- The guard still demonstrably red-on-break, green-restored; its docstring matches its asserts.
- No `# TODO(#525)` in `src/`.

## Allowed Scope
`src/physics/**`, `tests/unit/physics/**`, `tests/known_answer/**`, `tests/property/**`,
`src/physics/__init__.py`, `src/physics/constants.py`, the test fixtures that hard-code param
names/values, and the new `scripts/migrate_physics_store_columns_525.py`.

## Specific Exclusions
- No consumer-formula/ρ/refit changes; no banking re-application (#527); no `k_tire` value change (#511).
- Do NOT collapse the `_g`/`_ms2` two-space split into one (it's correct — see NAMING_TABLE).
- No units library, no per-param band-test matrix, no shim/alias/dual-name back-compat.

## Constraints
- `constraint:physics_region_no_evo_import`; `py` not `python`.
- Renames consistent producer→store→consumer; `_sigma` in lockstep.
- The migration is the ONLY way the on-disk stores change — do not hand-edit DBs.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (all *Parameters dataclasses, the fits, session_fit,
  fit_store), `struct:physics.layer2` (the views, estimate_store, the producers),
  `struct:physics.utilization` (car_prior). New: `scripts/migrate_physics_store_columns_525.py`.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (Review Trigger fires);
  `claim:lateral_car_prior_boundary_conversion` (the sanctioned seam, now with renamed fields).

## Required Evidence
Full suite GREEN; the old-name grep showing only explained survivors; the rename map
(old→new per field); the migration idempotency + read-back evidence; the guard red-on-break;
simplification_limits output.

## Verification Commands
```bash
py scripts/migrate_physics_store_columns_525.py   # run it; then run AGAIN (must be no-op)
py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q
py -m src.utils.simplification_limits --paths <touched>
git grep -n "TODO(#525)" src/   # empty
```

## Suggested Model Tier
stronger (Opus) — breadth (rename across producers/stores/consumers/fits/tests with strict
consistency) + the store migration + the no-regression bar are exactly where a Sonnet pass
under-delivered. Opus.

## Authority
- The NAMING_TABLE names + convention + the migration approach are **user-approved** — do not
  relitigate them. You MAY choose constant-module/migration-script internals and final exact
  unit tokens (matching source). You may NOT change a ratified disposition, alter a consumer
  formula, or collapse the `_g`/`_ms2` split.

## Stop Conditions
Stop and report if: a rename forces a consumer-formula/refit change; the migration can't be made
idempotent/safe on a real DB; the suite can't be made green without a behaviour change (= a real
regression); or a NAMING_TABLE target conflicts with an external/persistence contract you can't
rename safely (report it — don't freelance a workaround).

## Operating Discipline
Your **result file IS the deliverable** — `.agent-work/525/crew-handoffs/g2-implement-result.md`
must exist with the rename map + all evidence before you rest. Poll any long suite to completion.

## Return Format
`IMPLEMENTER_RESULT`: the rename map (old→new), files changed, the migration (path + idempotency
+ read-back evidence), suite GREEN, simplification_limits, guard red-on-break, old-name grep
result, assumptions, stop conditions, out-of-scope finds, **Workflow Feedback** (`none` needs a
run-specific reason).
