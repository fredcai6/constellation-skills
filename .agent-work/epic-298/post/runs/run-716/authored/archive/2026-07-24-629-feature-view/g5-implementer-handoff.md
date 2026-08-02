# Implementer Handoff — G5 (final gate)

## Gate
`g5`

## Task
Build the last two pieces of the Phase-5 contract:

1. `src/physics/feature_view/build_feature_view.py` — composes real `FeatureViewRow`s (per
   event, car) from G2's `weekend_state_records` + G3's `car_basis_posteriors`, as-of stamped.
2. `src/physics/feature_view/read.py` — `read_feature_view(store, year, gp_name, constructor,
   as_of_session, model_version)`, **the ONLY function evo may ever call into this package**.

Plus: an import-boundary test, a sole-public-read-surface test, and an end-to-end integration
test re-running G1's two protected-gate PROPERTIES against REAL composed data (not just G1's
synthetic fixtures).

## Composition design (already decided — carry exactly, do not re-design)

`build_feature_view.py`'s composer (e.g. `build_feature_view_row(store: FeatureViewStore, year:
int, gp_name: str, constructor: str, *, as_of_session: str, model_version: int) ->
FeatureViewRow`):

1. Call `store.load_as_of(year, gp_name, constructor, as_of_session)` (G1, already builds a
   `{"weekend_state": df, "car_basis_posterior": df}` dict, ALREADY restricted to sessions
   at-or-before the cutoff via `session_type IN (...)` — this IS the by-construction leakage
   guard; **do not re-implement session filtering in this new file, reuse `load_as_of` for every
   read** so there is exactly ONE place that guard lives).
2. **Primary source — `car_basis_posterior`:** among the rows returned (there is one row per
   session_type at-or-before the cutoff for this constructor), pick the one with the highest
   `session_ordinal(session_type)` — i.e. the most RECENT car-basis posterior as-of the cutoff
   (e.g. as-of `"FP3"`, prefer the FP3 row over FP1/FP2 if present; a constructor missing its own
   FP3 row falls back to its most recent PRESENT session). Its `axis_values`/`axis_sigma` seed
   `weekend_relative_basis`/`axis_sigma`.
3. **Refinement — `weekend_state`:** if the `weekend_state` DataFrame ALSO has a row at-or-before
   the cutoff (today this only happens when `as_of_session == "Q"`, since G2's Phase-2 model
   currently only processes Q — see `build_weekend_state.py`'s own `_DEFAULT_SESSION_TYPE`
   docstring), OVERRIDE each axis in `weekend_relative_basis`/`axis_sigma` with the
   `weekend_state` row's value+sigma **only where that row's own `axis_status[axis] ==
   "resolved"`** (never let an unresolved weekend_state axis clobber a resolved car_basis
   value — the weekend_state Phase-2 decomposition is the MORE REFINED signal when it has a
   real answer, but a reserved/degraded axis there must not regress a genuinely-resolved
   car_basis reading). Document this precedence rule explicitly in the module docstring — it
   is a real design decision, not incidental.
4. `circuit_conditional_composite`: **RESERVED — always `None`** in this gate. Nothing in
   Phases 2-4 computes a circuit-conditional composite yet (the closest existing artifact,
   `#512`'s regime-capability vector, was found to be "circuit-conditional + fine-margin, NOT a
   clean car axis" per `docs/architecture/index.md`'s C3 entry — not a ready composite to fold
   in here). State this explicitly in the docstring — do not fabricate a value, do not attempt
   to derive one from the axis data.
5. `written_at`: an ISO-8601 timestamp (`datetime.now(timezone.utc).isoformat()` or equivalent)
   recording when this row was composed.
6. Write the produced `FeatureViewRow` via `store.insert_feature_view_row` (append-only,
   already built in G1 — a repeat call for the SAME `(year, gp_name, constructor, model_version,
   as_of_session)` key correctly raises `sqlite3.IntegrityError`, which is CORRECT behavior, not
   a bug to route around).

**Constructor-grain (state explicitly in the docstring, do not silently assume away):** this
row is per-CONSTRUCTOR, not per-car/per-entry — a named round-1 approximation. Two-car
divergence within a constructor is banked as a follow-up, not solved here.

**2026 rows:** this gate gates on nothing 2026-specific — any row this composer is asked to
build, it builds, whatever year is passed. Note in the docstring (do not implement a gate) that
DESIGN_SPEC names the Phase-3 aero mini-gate as the real admission control for 2026 rows in
production; this composer has no opinion on when it's called.

## `read.py` — the sole evo-facing surface

`read_feature_view(store: FeatureViewStore, year: int, gp_name: str, constructor: str,
as_of_session: str, model_version: int) -> Optional[FeatureViewRow]` — a DIRECT KEY LOOKUP
against the ALREADY-WRITTEN `feature_view_rows` table (use
`store.load_feature_view_rows(year=year, gp_name=gp_name)` — G1, already built — then filter in
Python to the exact `(constructor, model_version, as_of_session)` triple, since
`load_feature_view_rows` doesn't take those as query params; this is fine because the row was
ALREADY as-of-restricted at WRITE time by `build_feature_view_row`, so no further session
filtering happens here — reading an already-written, already-scoped row is not the same failure
mode `load_as_of` guards against). Returns `None` (never raises) when no row matches — a caller
asking for an as-of cutoff that was never built simply gets nothing, not a fabricated value.
Set `__all__ = ["read_feature_view"]` in this module — the explicit, sole public surface.

## Import-boundary + sole-surface + end-to-end tests

- `tests/unit/physics/feature_view/test_import_boundary.py` (or fold into an existing file):
  `grep`-equivalent (a Python-level `ast`/text scan, or a plain substring check reading every
  `.py` file under `src/physics/feature_view/`) asserting zero occurrences of `evo_predictor`
  anywhere in the package — mirrors how `constraint:physics_region_no_evo_import` is verified
  elsewhere in this repo (a real, reusable check, not a one-off).
- A test asserting `read.py.__all__ == ["read_feature_view"]` (or equivalent) — the explicit
  sole-surface contract.
- `tests/unit/physics/feature_view/test_e2e_integration.py`: build a small synthetic
  `WeekendStateModel` (per G2's own test convention) + synthetic `EstimateRecord`s (per G3's own
  test convention) for one `(year, gp_name)` across FP1/FP2/FP3/Q, run them through
  `build_weekend_state_records`/`build_car_basis_posterior_records` (G2/G3, real composers, not
  hand-built records), write everything to a `FeatureViewStore`, build+write `FeatureViewRow`s
  at each as-of cutoff via THIS gate's composer, then read them back via `read_feature_view` and
  re-assert: (a) a `model_version` bump for the same natural key does not mutate the prior row
  (append-only, re-proven on REAL composed data); (b) the "as of FP1" row's `weekend_relative_
  basis` traces only to FP1-sourced values (as-of leakage, re-proven on REAL composed data, not
  just G1's synthetic sentinels).

## Test Mode
TDD required.

## Close Criteria
- Both new files exist; `__all__` on `read.py` is exactly `["read_feature_view"]`.
- The primary/refinement/override precedence rule (see step 2-3 above) is implemented exactly
  as specified and tested (construct a case where `weekend_state` has an unresolved axis and
  `car_basis_posterior` has a resolved one for that same axis — confirm the car_basis value
  survives, not clobbered).
- `circuit_conditional_composite` is always `None`, documented as reserved.
- The import-boundary test passes for the WHOLE `src/physics/feature_view/` package (not just
  this gate's new files).
- The end-to-end test's two re-proven properties (append-only + as-of leakage on real composed
  data) both pass.
- No `src.evo_predictor` import anywhere in the package.
- `py -m pytest tests/unit/physics/feature_view -q` green (all prior + new).
- `py -m pytest tests/unit/physics/layer2 tests/unit/physics/weekend_state -q` green (no
  regression in the two consumed regions — this gate's own required regression slice).
- `simplification_limits --paths src/physics/feature_view` clean.

## Allowed Scope
New files `src/physics/feature_view/build_feature_view.py`, `src/physics/feature_view/read.py`;
new test file(s) under `tests/unit/physics/feature_view/`.

## Specific Exclusions
G1/G2/G3 (`records.py`, `store.py`, `build_weekend_state.py`, `build_car_basis.py`) are
CLOSED — do not modify; report a genuine defect as a blocker rather than patching it.

## Constraints
- `constraint:physics_region_no_evo_import`.
- `read.py` is the ONLY public surface — no second read path anywhere in the package that a
  future evo caller could reach for instead.
- Reuse `store.load_as_of` for every as-of read — do not reimplement session filtering.
- DB hygiene: tests use `tmp_path`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.feature_view` (the whole component, closing out).
- **Capability:** the as-of-stamped feature view — THE evo-facing surface.
- **Constraints:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** decision candidate — `struct:physics.feature_view` as a new sibling
  component (mirrors `weekend_state` precedent) — record at reconcile, this gate's evidence is
  the final proof it holds together end-to-end.
- **Evidence expectations:** append-only + as-of leakage RE-VERIFIED on real composed data
  (not just G1's synthetic fixtures); DB-only / sole-read-surface.

## Deliverable Path Check
- **Committed** — both new files; `git check-ignore` exit 1 each.
- **Committed** — new test file(s).

## Required Evidence
- Full pytest output for the feature_view suite AND the layer2/weekend_state regression slice.
- The primary/refinement override example (paste the before/after axis_values showing a
  resolved car_basis value surviving an unresolved weekend_state axis).
- The end-to-end test's captured proof that append-only + as-of leakage hold on real composed
  data (paste the relevant assertions/output).
- `simplification_limits` output.

## Verification Commands

```bash
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view tests/unit/physics/layer2 tests/unit/physics/weekend_state -q
py -m src.utils.simplification_limits --paths src/physics/feature_view
grep -rln "evo_predictor" src/physics/feature_view/ || echo clean
git check-ignore src/physics/feature_view/read.py; echo "exit=$?"
```

## Suggested Model Tier
Stronger (Sonnet) — this is the culminating gate; the precedence rule and the end-to-end
re-verification of both protected properties on real data are genuinely load-bearing.

## Authority
The composition/precedence design (steps 1-6 above), the reserved `circuit_conditional_
composite`, and the constructor-grain approximation are already decided — carry them exactly;
do not re-design.

## Stop Conditions
Stop and return if: `load_as_of`'s actual return shape doesn't match what's described here;
a decision outside this handoff's authority is needed; the end-to-end test cannot be built
without duplicating G1's session-filtering logic (escalate rather than reimplementing it).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
