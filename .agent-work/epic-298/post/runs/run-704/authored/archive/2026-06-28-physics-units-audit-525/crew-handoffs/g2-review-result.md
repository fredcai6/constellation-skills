# Review Result — #525 G2 RE-REVIEW (rework: full semantic rename + store-column migration)

APPROVE

## Assigned Gate
`g2-review` (re-review after rework 1/3) — issue #525, branch `feat/physics-units-audit-525`

## Result
`APPROVE`

> This OVERWRITES the stale attempt-1 result (which predated the rework and wrongly
> said "field names unchanged"). The full semantic rename + migration IS present and
> was reviewed against the diff/source/suite/migration, not the stale implementer prose.

---

## Important note on how the rework is delivered (verify-command correction)
The handoff's inspect command `git diff main...feat/physics-units-audit-525` shows **nothing**,
because the rework is **uncommitted in the working tree**, and `main == merge-base == HEAD`
(branch tip `897b33bc` is only a docs commit; the #525 rename/migration is NOT committed).
I reviewed via **`git diff HEAD`**: 73 changed `src/`+`tests/` files (1360 insertions / 1274
deletions), plus two new untracked files — `scripts/migrate_physics_store_columns_525.py` and
`src/physics/constants.py`. All changes are physics-region. This is a workflow note (the work
should be committed before integrate), not a code blocker.

---

## Per-check findings (the 7 close criteria)

### Check 1 — Rename consistency (no half-renamed seam) — PASS
Consistent producer → store → consumer → tests:
- **Producers:** all 5 view-result classes expose the new attrs — `lateral_view.lateral_mech_grip_g`/`lateral_aero_grip_g` (L69-70), `power_drag_view.max_power_w`/`drag_area_closed_m2` (L42-43), `braking_view.brake_decel_ms2`/`brake_aero_decel_per_m` (L33-34), `traction_view.traction_accel_ms2`/`traction_aero_accel_per_m` (L41-42), `coast_view.coast_rolling_decel_ms2`/`coast_drag_area_m2` (L37-38). `record_from_estimate` reads them.
- **Stores:** `EstimateRecord` (45 fields) + `FitRecord` (46 fields) carry the new names incl. every `_sigma` companion; CREATE TABLE columns auto-derive from them.
- **Consumer:** `car_prior` reads the new store columns and emits `LateralParameters(lateral_mech_grip_ms2=…, lateral_aero_grip_ms2=…)`; consumer dataclasses (`physics_data_models.py`) all renamed with formulas using the new fields.
- **Imports:** every renamed physics module imports clean; suite green — no broken code seam.

**Surviving old-name tokens (~298 in `src/physics`, all legit):**
- (a) **fit-local working variables** (`theta_D`/`theta_R`/`A0` inside `parameter_estimator`/fit functions) — the NAMING_TABLE marks fit-locals a *soft* "should", behaviour-preserving; not done, acceptable.
- (b) **docstring/formula text** (`mu = A0 + A2·v²`, `decel = theta_R + theta_D·ρ·v²`).
- (c) **diagnostic LABEL tuples/keys** — `covariance_summary(("A0","A2"))`, `("theta_D","theta_R")`.
- (d) **`PhysicsEstimatorConfig` default field names** (`default_A0`, `default_A2`, `default_theta_D/P/R`, `fallback_lateral_A0_std`, `fallback_lateral_A2_std`) — an **internally consistent** contract: defined in `physics_config.py`, read as `cfg.default_A0` in `parameter_estimator.py` (L308-331) and `car_prior.py` (L514-515). NOT in the store/migration rename scope; nothing reads a renamed version of them → not a broken seam, just out of the rename's chosen scope.

**Dict-key scrutiny (the specifically-flagged risk):** `as_of_means` returns string keys `{"a_b","b_b","a_t","b_t","A0","A2","CdA","P_max","theta_R"}` (`car_prior` L405/421/524/595). I grepped **all** readers: the ONLY reader is `tests/unit/physics/test_car_prior.py:252` → `as_of_means.get("CdA")`, which the producer emits (L595). **No production consumer anywhere.** The dataclass docstring (L123) declares `as_of_means` diagnostics/tests-only. Producer-key == reader-key, so it is internally consistent. **Verdict: acceptable-diagnostic, NOT a missed consumed-by-name contract** — does not block.

### Check 2 — No-regression / convention B preserved — PASS
Behaviour preserved; verified the diff **line-by-line**:
- Consumer m/s² math unchanged — every formula keeps ρ: `aero = lateral_aero_grip_ms2·rho·speed²`; `drag = spec_drag·rho·speed²`; coast `theta_R + cda·rho·v²/(2m)`; power `max_power_w/(m·v) − cda·rho·v²/(2m)`. Only identifiers renamed. **No ρ removal, no refit, no formula edit.**
- The **`_g` (producer/store) vs `_ms2` (consumer) split is PRESERVED, not collapsed:** store columns are `lateral_mech_grip_g`/`lateral_aero_grip_g`; FitStore + consumer are `lateral_mech_grip_ms2`/`lateral_aero_grip_ms2`. The single conversion seam at `car_prior._assemble_lateral` keeps `s0 = GRAVITY_MS2`, `s2 = GRAVITY_MS2/air_density`, Jacobian `J = diag(G, G/ρ)` — identical math to the pre-rework `G_MS2` version (constant renamed only).
- `_build_longitudinal` keeps `p_max/MASS_KG` (watts→W/kg) and `cda/(2·MASS_KG)`.
- C1 numbers can't move: store reads 216 rows; the guard asserts the unchanged `3.2·G_MS2` conversion.

### Check 3 — Migration correctness — PASS
`scripts/migrate_physics_store_columns_525.py` old→new maps match the renamed dataclass fields exactly:
- `_SESSION_ESTIMATES_RENAMES` (24) == `EstimateRecord` renamed fields incl. all `_sigma` companions and the `*_cold` fields.
- `_SESSION_FITS_RENAMES` (13) == `FitRecord` renamed fields.
- Table names `session_estimates`/`session_fits` match `estimate_store.py:337` / `fit_store.py:104`.
- **Idempotent** (L115 guard: `old in cols AND new not in cols`) and **transactional** (L136-142 single connection + `commit()`; partial failure rolls back).
- **Re-ran it:** idempotent no-op — `0 column(s) renamed, 61 already-migrated` (24+24+13 across the 3 DBs), matching the commander's run.
- **Store read:** `EstimateStore('data/physics_estimates.db').load()` → **216 rows** with the renamed columns.

### Check 4 — Suite green — PASS
Re-ran myself: `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q` → **639 passed, 6 skipped in 308.03s, exit 0.** Matches the handoff/commander (639/6).

### Check 5 — Guard intact + docstring fixed — PASS
`TestTruthAnchorTunnelCornerCap` (`test_car_prior.py:261`) exercises the **real output path** (`PhysicsSimulator._compute_speed_caps`, L301), not a stub. `test_tunnel_corner_cap_is_realistic` asserts `63.0 <= cap <= 66.0` (L307) and the docstring band text says "~63–66 m/s" (L295) — **band text matches the assert.** It bites on a units break: the L308-310 failure message explicitly diagnoses the "~17 m/s ⇒ g-units not converted" case. `test_converted_A0_is_mechanical_ms2` (L313) + `test_lateral_A0_A2` (L223) assert `lateral_mech_grip_ms2 == 3.2·G_MS2` and `> 25.0` — the A0-boundary teeth, referencing the renamed field.

### Check 6 — simplification_limits, no NEW violations — PASS (with non-blocking observation)
- Canonical repo gate `py -m src.utils.simplification_limits --baseline` → 6 violations, all `file_lines`, **none in `src/physics/`**.
- Function-level delta (working-tree vs HEAD via `git archive` baseline): HEAD = **19** function violations in `src/physics/`; working-tree = **21**.
- The 2 newly-crossing are **length-only and purely rename-induced**, with **zero** new cyclomatic complexity, on functions already at/over the limit:
  - `car_prior._assemble_lateral` 100 → 101 lines (the `LateralParameters(A0=…, A2=…)` one-liner became a 3-line call because `lateral_mech_grip_ms2` ≫ `A0`, plus the bridge docstring grew).
  - `layer2/session_estimator.estimate_session` → exactly 100 lines.
- A direct, behaviour-preserving consequence of the **user-approved longer names**, not new structural debt → non-blocking. Filed as triage candidate `tc1`.

### Check 7 — Scope (physics-region only) — PASS
- The one allowed shim is the deprecated **`G_MS2` alias**: `braking_fit.py:42` `G_MS2 = GRAVITY_MS2  # deprecated alias — import GRAVITY_MS2 from constants instead` — **import-only** (a constant assignment used by tests; not a dual-name field re-export).
- **No `k_tire` value change:** `tyre_grip_decay_per_lap` is still sourced from `config.grip_decay_prior_k` (pure rename), the car_prior neutral default stays `0.0`, and `exp(-k·tire_laps)` is identical.
- **No banking change:** grep of added lines for bank re-application is empty; only pre-existing `bank_rad`/`banking_at` reads remain.
- `friction_coupling.py` deleted (first-pass item retained) with **zero** dangling import survivors.

---

## Map impact verdict
- **Evidence supports claimed change:** Yes — suite (639/6), idempotent migration (61 cols), 216-row store read, and a line-by-line behaviour-preservation pass back the "rename-only, behaviour-preserving" claim.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored (no evo imports; all edits physics-region). `_g`/`_ms2` split kept; behaviour-preserving renames.
- **Notes match the diff:** The inbound Map Anchors (`struct:physics`, `struct:physics.layer2`, `struct:physics.utilization`, the new migration script; `decision:ideal_lap_sim_two_sided_evaluator`; `claim:lateral_car_prior_boundary_conversion`) match the touched surface. The implementer **result file is stale** (first-pass only) — a process gap, surfaced below, not a code issue.
- **Decision candidates surfaced:** None requiring authority beyond the already-approved NAMING_TABLE.
- **Durable context routed:** Cartographer should refresh the physics packet's parameter-name references (the old `A0`/`A2`/`theta_*`/`a_b` vocabulary → the new `<what>_<unit>` names) so the map text matches code. Routed as durable context, not a blocker.

## Reconciliation check
No structural/contract divergence requiring Commander reconciliation beyond the doc refresh above. The rename is a vocabulary refresh over existing seams; the migration keeps the on-disk stores readable without recompute.

## Blockers
- None.

## Out-of-scope observations
- **`PhysicsEstimatorConfig` default field names unrenamed** (`default_A0`, `default_A2`, `default_theta_D/P/R`, `fallback_lateral_A0_std`, `fallback_lateral_A2_std`). Internally consistent (defined + consumed by the same old names), so not a broken seam, but the cryptic-name kill is incomplete here. Worth a follow-up to extend the rename to the config defaults for full consistency.
- **`as_of_means` diagnostic dict keys** retain old physics labels (`"A0"`, `"a_b"`, `"theta_R"`, …). Diagnostics-only, single test reader on `"CdA"`. Optional tidy.
- **`FitRecord.theta_D_source`** (provenance string field) kept un-renamed — it is a `_source` metadata tag, not a value-carrying physics parameter; acceptable, but note for consistency if a future pass renames provenance tags.
- **Triage candidate `tc1`** (filed): two length-only `simplification_limits` crossings from the longer names — `car_prior._assemble_lateral` and `session_estimator.estimate_session`. Optional helper-extraction follow-up.
- **The rework is uncommitted** (working tree). It must be committed before the integrate step; reviewing branches that diff clean against `main` is a footgun — see Workflow Feedback.

## Workflow Feedback
- **Handoff gaps:** The "How to Inspect" command (`git diff main...feat/physics-units-audit-525`) returns **empty** — the rework is uncommitted and `main == merge-base == HEAD` (a docs-only commit). Anyone following the handoff literally would conclude "renames not delivered" (exactly the stale attempt-1 trap). The handoff should have said: *the rework is uncommitted; review via `git diff HEAD`*. The commander-verification note saved the review by pointing at the diff + suite + migration directly.
- **Context rediscovered:** Had to discover the work was uncommitted (not on the branch tip) by checking merge-base/HEAD/main myself. Also had to compute the `simplification_limits` baseline at HEAD via `git archive` because the handoff's "10 pre-existing" figure (a) used a different scope than `--paths src/physics/` (which shows 19/21) and (b) wasn't reproducible from the stated command — the real, reproducible numbers are 19 (HEAD) → 21 (working tree).
- **Instructions improvised around:** The skill template ships generic survey items `r0–r5`; the 7 close-criteria were already appended as `c1–c7` in the pre-seeded `review.json`, so I drove the existing survey rather than re-instantiating from template. Recorded each criterion as its own check, plus mapped them onto `r1–r5`. No deviation from the engine mechanism.
- **What would have made this easier:** State the review base explicitly in the handoff (commit the rework, or say "uncommitted — diff against HEAD"), and cite the exact `simplification_limits` command + expected baseline count so "no NEW violations" is mechanically checkable rather than requiring a HEAD-baseline reconstruction.

## Return status
`complete`
