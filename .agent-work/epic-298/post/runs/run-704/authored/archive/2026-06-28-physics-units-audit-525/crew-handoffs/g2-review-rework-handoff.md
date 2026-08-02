# Reviewer Handoff — #525 G2 RE-REVIEW (rework: full semantic rename + store migration)

## Gate
g2-review (re-review after rework 1/3) — issue #525, branch `feat/physics-units-audit-525`

## Critical context — the implementer result file is STALE
The rework crew idled and wrote a **stale result file** (`g2-implement-result.md` describes only
the first pass; it wrongly says "field names unchanged"). **Read
`.agent-work/525/crew-handoffs/g2-commander-verification.md` for the TRUE state, and verify
against the DIFF + the suite + the migration — NOT the result-file prose.** The binding spec is
`.agent-work/525/NAMING_TABLE.md`; seam map is `.agent-work/525/AUDIT_MAP.md`.

## What Was Implemented (rework)
A **full semantic rename** of the physics parameter vocabulary (`A0`→`lateral_mech_grip_g`/`_ms2`,
`A2`→`lateral_aero_grip_*`, `p_max`→`max_power_w`, `theta_P*`→`specific_power_w_kg`,
`theta_D`→`spec_drag_m2_kg`, `cda*`→`drag_area_*_m2`, `a_b/b_b`→`brake_decel_ms2`/`brake_aero_decel_per_m`,
`a_t/b_t`→`traction_accel_ms2`/`traction_aero_accel_per_m`, terrain, + `_sigma` companions)
across producers, both store dataclasses, consumers, fit locals, and ALL tests — plus an
idempotent SQLite column migration (`scripts/migrate_physics_store_columns_525.py`) for the 3
on-disk stores. The first-pass work (GRAVITY_MS2/MASS_KG dedup, density 1.225, friction_coupling
removal, OT-6 comment-fix, headers, the output-level guard) is retained underneath.

## How to Inspect
```bash
git diff main...feat/physics-units-audit-525 -- src/ tests/ scripts/
git log --oneline main..feat/physics-units-audit-525
```

## Commander pre-verification (re-confirm independently)
- Full suite GREEN: `639 passed, 6 skipped` (I re-ran it).
- Migration ran: 61 columns across the 3 DBs; second run idempotent no-op.
- C1 read+pool verified: `EstimateStore('data/physics_estimates.db').load()` → 216 rows new cols;
  `pool_driver.pool_store(df, year=2023, session_type='Q')` → `StorePooling` OK.

## Close Criteria (each a review check)
1. **Rename consistency — no half-renamed seam.** Every NAMING_TABLE field renamed consistently
   producer→store→consumer→tests. **The ~166 remaining old-name tokens in `src/physics` must all
   be legit** (docstring/formula text like `mu = A0 + A2·v²`, or explained survivors). **Specifically
   scrutinize the return-dict string keys** (`car_prior` returns `{"a_b": ..., "A0": ...}` ~L395-429):
   confirm those keys aren't consumed-by-name as a missed internal contract (grep their readers) —
   if they're an unrenamed internal contract, decide whether that's acceptable (diagnostic-only) or
   a BLOCK (inconsistent with the rename intent).
2. **No-regression / convention B.** Consumer m/s² **math unchanged** (renames are behaviour-
   preserving, NOT formula edits); no ρ removal; no refit; the `_g` (producer/store, density-agnostic)
   vs `_ms2` (consumer) split is **preserved, not collapsed**. The C1 numbers must not move.
3. **Migration correctness.** Read `scripts/migrate_physics_store_columns_525.py`: the old→new map
   matches the renamed dataclass fields exactly (both `session_estimates`/EstimateRecord and
   `session_fits`/FitRecord, incl. `_sigma`); it's idempotent (old-present & new-absent guard) and
   transactional. Re-run it (must be a no-op) and re-confirm a store read via `EstimateStore.load()`.
4. **Suite green.** Re-run `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q` → GREEN.
5. **Guard intact + docstring fixed.** The output-level guard still exercises the real path and
   bites on a units break; its docstring band text now matches the actual asserts.
6. **simplification_limits** on touched paths — no NEW violations (10 pre-existing reported).
7. **Scope.** Physics-region only; no shim/alias/dual-name back-compat (a deprecated `G_MS2` alias
   in braking_fit is the one allowed survivor — confirm it's import-only); no `k_tire` value change;
   no banking change.

## Constraints
`constraint:physics_region_no_evo_import`; behaviour-preserving renames; `_g`/`_ms2` split kept.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (all *Parameters + fits + session_fit/fit_store),
  `struct:physics.layer2` (views, estimate_store, producers), `struct:physics.utilization` (car_prior),
  `scripts/migrate_physics_store_columns_525.py` (new). 
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (Review Trigger fires);
  `claim:lateral_car_prior_boundary_conversion` (sanctioned seam, renamed fields).

## Suggested Model Tier
stronger (Opus) — rename-consistency across ~80 files + the migration correctness + the dict-key
contract question are judgment calls a green suite alone won't settle.

## Stop Conditions
BLOCK if: a consumer-formula/ρ/refit change slipped in; a genuine half-renamed *code* seam exists
(not just docstrings); the dict-key keys are a missed consumed-by-name contract left inconsistent
without justification; the migration map mismatches the dataclass fields or isn't idempotent; the
`_g`/`_ms2` split was collapsed; or the suite/guard isn't green.

## Return Format
REVIEW_RESULT: verdict (APPROVE or BLOCK) on its own line; per-check findings (1–7, each citing the
diff/source/command output you verified); blockers; out-of-scope observations; Workflow Feedback.
