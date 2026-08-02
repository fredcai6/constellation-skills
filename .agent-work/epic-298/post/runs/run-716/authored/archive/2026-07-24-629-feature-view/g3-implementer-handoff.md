# Implementer Handoff — G3

## Gate
`g3`

## Task
Build `src/physics/feature_view/build_car_basis.py` — composes real `CarBasisPosteriorRecord`
rows (G1's dataclass) from `src.physics.layer2.estimate_store.EstimateStore` rows, and writes
them via `FeatureViewStore.insert_car_basis_posterior` (G1, closed/frozen this run).

## Key seams (verified from source — cite exactly, do not re-derive from memory)

- `EstimateStore.load(year=None, session_type="Q", status="ok") -> pd.DataFrame`
  (`src/physics/layer2/estimate_store.py:435-460`) — reads `session_estimates`. **Important:**
  its default `session_type="Q"` only returns Q rows; to build the full FP1->FP2->FP3->Q chain
  for a weekend you must call it once per session type (or pass `session_type=None` to get all,
  then group by `session_type` yourself — `session_type=None` removes that WHERE clause
  entirely per the method's own `if session_type is not None` guard, verified). Either approach
  is fine; state which you chose.
- The 11 physical axis columns on an `EstimateRecord` row (`estimate_store.py:101-239`) are
  IDENTICAL to `weekend_state.frame.AXES` (G2 already uses this list) — `drag_area_closed_m2`,
  `brake_decel_ms2`, `brake_aero_decel_per_m`, `traction_accel_ms2`, `traction_aero_accel_per_m`,
  `max_power_w`, `power_drag_area_m2`, `lateral_mech_grip_g`, `lateral_aero_grip_g`,
  `coast_rolling_decel_ms2`, `coast_drag_area_m2` — each has a `{axis}_sigma` sibling column.
- **The per-axis STATUS columns use a DIFFERENT, shorter 9-name set**
  (`AXIS_STATUS_NAMES = ("cda", "p_max", "a_b", "b_b", "a_t", "b_t", "A0", "A2", "theta_R")`,
  columns `{name}_status`) that each govern ONE OR TWO of the 11 physical axis columns. You
  MUST build a per-physical-axis `axis_status` dict (matching G2's `WeekendStateRecord`
  convention: keyed by the 11 physical axis names) by mapping through this table (verified
  against `estimate_store_fields._axis_statuses`'s own construction):
  - `cda_status` -> governs `drag_area_closed_m2` AND `power_drag_area_m2`
  - `p_max_status` -> governs `max_power_w`
  - `a_b_status` -> governs `brake_decel_ms2`
  - `b_b_status` -> governs `brake_aero_decel_per_m`
  - `a_t_status` -> governs `traction_accel_ms2`
  - `b_t_status` -> governs `traction_aero_accel_per_m`
  - `A0_status` -> governs `lateral_mech_grip_g`
  - `A2_status` -> governs `lateral_aero_grip_g`
  - `theta_R_status` -> governs `coast_rolling_decel_ms2` AND `coast_drag_area_m2`
  Use `normalize_axis_status` (`estimate_store_fields.py`, already imported in `store.py`) on
  each raw `{name}_status` value before applying this mapping (a legacy row's `None` status
  normalizes to `"unresolved"`, per that function's own contract) — do not read the raw column
  value directly.
- **`cross_view_covariance` is ALREADY COMPUTED, not something this gate re-derives.**
  `EstimateRecord.cross_view_covariance` (a dict or `None`, produced at fit-time by
  `_cross_view_covariance_fields`, which itself calls `cross_view.fuse_dual_cda` internally)
  is already present on every loaded row via `EstimateStore.load()`'s JSON-column
  deserialization. **Do NOT call `cross_view.fuse_dual_cda` yourself** — this gate is a
  passthrough: copy `row["cross_view_covariance"]` straight into
  `CarBasisPosteriorRecord.cross_view_covariance`. (The commander confirmed this by reading
  `estimate_store.py`'s `record_from_estimate` before writing this handoff — an earlier draft
  of this handoff would have had you re-fuse CdA from scratch, which is wrong: it's already
  done upstream.)
- `effective_axis_sigma`/`normalize_axis_status` — same import path `store.py` already uses
  (`src.physics.layer2.estimate_store_fields`). Apply `effective_axis_sigma(value, sigma,
  normalized_status)` per physical axis to populate `CarBasisPosteriorRecord.axis_sigma` (same
  discipline as G2: `"resolved"` passes sigma through, `"unresolved"` widens).
- `src/physics/feature_view/records.py`'s `CarBasisPosteriorRecord(year, gp_name, constructor,
  session_type, model_version, chain_position, prior_session, axis_values, axis_sigma,
  axis_status, cross_view_covariance, process_noise_link=None,
  process_noise_link_status="unresolved", parc_ferme_step=None,
  parc_ferme_step_status="unresolved")` — a `__post_init__` guard RAISES `ValueError` if you
  pass a non-`None` value for either reserved field. **Do not attempt to compute either
  reserved field — leave them at their defaults.** `SESSION_ORDER = ("FP1", "FP2", "FP3", "Q")`
  and `session_ordinal()` are in the same `records.py` module — use them to set
  `chain_position` (= the row's own `session_type`) and `prior_session` (the SESSION_ORDER
  entry immediately before this row's session, or `None` for `"FP1"` — the chain's first link;
  a constructor missing an earlier session in the DB simply has no row for that link, this
  gate does not synthesize placeholder rows for missing sessions).

## Protected Intent
Both `process_noise_link` and `parc_ferme_step` MUST remain `None` (the `__post_init__` guard
already enforces this — you cannot bypass it without editing G1's closed `records.py`, which
you must not do). `cross_view_covariance` must be a faithful passthrough, not a re-derivation —
do not import or call `cross_view.fuse_dual_cda` in this gate's code at all (a grep for
`fuse_dual_cda` in your new file should return nothing).

## Test Mode
TDD required — synthetic `EstimateStore` rows (build a small in-memory `EstimateStore` via
`tmp_path`, insert 2-3 synthetic `EstimateRecord`s covering FP1/FP2/Q for one constructor, plus
a second constructor, using `estimate_store.record_from_estimate` or direct
`EstimateRecord(...)` construction — either is fine, whichever is less brittle for your test
fixture). No live `physics_estimates.db` read required.

## Close Criteria
- `src/physics/feature_view/build_car_basis.py` exists with a composer function (e.g.
  `build_car_basis_posterior_records(store: EstimateStore, year: int, gp_name: str, *,
  model_version: int) -> list[CarBasisPosteriorRecord]`) that loads the relevant
  `session_estimates` rows and produces one `CarBasisPosteriorRecord` per (constructor,
  session_type) pair found.
- The 9-name-to-11-axis status mapping above is applied correctly — test explicitly: a row
  with `cda_status="unresolved"` produces `axis_status["drag_area_closed_m2"] ==
  "unresolved"` AND `axis_status["power_drag_area_m2"] == "unresolved"` (both, from the one
  status column).
- `chain_position`/`prior_session` correctly reflect `SESSION_ORDER` — test a full FP1/FP2/Q
  chain (FP3 legitimately missing from the DB) and confirm `prior_session` for the `"Q"` row is
  `"FP2"` (the nearest PRESENT prior session — or `"FP3"` if your design instead names the
  chain-adjacent slot regardless of presence; PICK ONE interpretation, state it explicitly in
  the docstring, and test it — do not leave this ambiguous). Prefer nearest-PRESENT (simpler,
  matches "this is what we actually observed") unless you find a strong reason otherwise; if
  you pick differently, say why in your IMPLEMENTER_RESULT.
- `cross_view_covariance` passthrough verified byte-for-byte (dict equality) against the
  source `EstimateRecord`'s value; `fuse_dual_cda`/`cross_view` NOT imported in this new file
  (grep-verifiable).
- Both reserved fields stay `None` on every produced record (trivially true since the composer
  never sets them, but add one explicit assertion test for it).
- No `src.evo_predictor` import.
- `py -m pytest tests/unit/physics/feature_view -q` green (all prior + new tests).
- `simplification_limits --paths src/physics/feature_view` clean.

## Allowed Scope
New file `src/physics/feature_view/build_car_basis.py`; new test file(s) under
`tests/unit/physics/feature_view/` (e.g. `test_build_car_basis.py`).

## Specific Exclusions
Do NOT modify `records.py`/`store.py` (G1) or `build_weekend_state.py` (G2) — closed/reviewed.
Do NOT modify `src/physics/layer2/estimate_store.py`, `estimate_store_fields.py`, or
`cross_view.py` (read-only consumers). Do NOT call `cross_view.fuse_dual_cda` (see Protected
Intent). Do NOT read a live/committed DB in tests.

## Constraints
- `constraint:physics_region_no_evo_import`.
- Reuse `effective_axis_sigma`/`normalize_axis_status` (import, don't reimplement).
- Both reserved fields stay `None` — enforced by G1's `__post_init__`, do not work around it.
- DB hygiene: tests use `tmp_path`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (read-only: `estimate_store`, `estimate_store_fields`,
  `cross_view` — read/cite only, `fuse_dual_cda` NOT called), `struct:physics.feature_view`.
- **Capability:** `EstimateStore.load`, `effective_axis_sigma`, `normalize_axis_status`.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** decision pressure 2 (session-chain framing) — RESOLVED as reserved
  slots per MISSION_FRAME.md; a related decision (float sent to Admiral, response pending) may
  arrive mid-gate — if it does, it changes FUTURE work only, not this closed gate; do not
  reopen this gate for it.
- **Evidence expectations:** `cross_view_covariance` full-covariance passthrough claim; the
  9-to-11 axis-status mapping.

## Deliverable Path Check
- **Committed** — `src/physics/feature_view/build_car_basis.py`; `git check-ignore` exit 1.
- **Committed** — new test file(s).

## Required Evidence
- Full pytest output.
- A concrete example of one produced `CarBasisPosteriorRecord` showing `axis_status` correctly
  fanned out from a single `cda_status`/`theta_R_status` source column to both of its governed
  physical axes.
- The `cross_view_covariance` passthrough example (source dict vs. produced record's dict,
  showing equality).
- `simplification_limits` output; `grep -rn "fuse_dual_cda" src/physics/feature_view/
  build_car_basis.py` (expect empty).

## Verification Commands

```bash
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view -q
py -m src.utils.simplification_limits --paths src/physics/feature_view
grep -rn "evo_predictor\|fuse_dual_cda" src/physics/feature_view/build_car_basis.py || echo clean
git check-ignore src/physics/feature_view/build_car_basis.py; echo "exit=$?"
```

## Suggested Model Tier
Stronger (Sonnet) — the 9-to-11 axis-status mapping and the chain-position/prior-session
semantics with a missing-session gap are genuine judgment points worth care.

## Authority
The reserved-slot decisions (process_noise_link, parc_ferme_step) are already made — carry
them exactly as specified; do not re-decide. The nearest-PRESENT vs. chain-adjacent-regardless
`prior_session` interpretation is yours to pick (see Close Criteria) as long as you state and
test your choice explicitly.

## Stop Conditions
Stop and return if: `EstimateRecord.cross_view_covariance`'s actual shape doesn't match what
this handoff describes; a decision outside this handoff's authority is needed; allowed scope
must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
