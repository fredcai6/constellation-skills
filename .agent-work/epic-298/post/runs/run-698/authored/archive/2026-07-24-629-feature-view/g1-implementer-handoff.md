# Implementer Handoff — G1

## Gate
`g1` (execute.json: g1-implement)

## Task
Build `src/physics/feature_view/` — a NEW component, sibling to `src/physics/weekend_state/`
and `src/physics/layer2/`. This gate builds the store foundation + the two load-bearing gate
tests using SYNTHETIC fixture data only (no real Phase 2-4 wiring — that's G2-G5). Files:

- `src/physics/feature_view/__init__.py`
- `src/physics/feature_view/records.py` — four frozen dataclasses, each carrying its own
  `model_version: int` field:
  - `WeekendStateRecord` (per event, session, car) — reserve fields for L1-L4 state + sigma
    per axis (G2 populates these for real; here just the shape, e.g. `axis_values: dict`,
    `axis_sigma: dict`, `axis_status: dict` — dicts keyed by axis name, since the 11 axes are
    a list not fixed columns at this layer).
  - `CarBasisPosteriorRecord` (per constructor, session) — `year: int`, `gp_name: str`,
    `constructor: str`, `session_type: str`, `chain_position: str`, `prior_session:
    Optional[str]`, `axis_values: dict`, `axis_sigma: dict`, `axis_status: dict`,
    `cross_view_covariance: Optional[dict]`, `process_noise_link: Optional[dict] = None`
    (RESERVED — always None, carries a `process_noise_link_status: str = "unresolved"`
    sibling field), `parc_ferme_step: Optional[dict] = None` (RESERVED — always None, carries
    `parc_ferme_step_status: str = "unresolved"`). Docstring must state explicitly WHY both
    are reserved (no process-noise-link fit exists anywhere in the codebase — verified:
    `pooling.fit_drift` is a season-clock trend, not an intra-weekend link; the parc-ferme
    distribution fit is bounded-deferred per #513) — never compute a value for either field
    in this gate.
  - `LapEvidenceRecord` (per driver, lap) — `year`, `gp_name`, `session_type`, `driver: str`,
    `lap_number: int`, `representativeness_weight: Optional[float]`, `mass_kg: Optional[float]`,
    `mass_sigma_kg: Optional[float]`, `run_purpose: Optional[str]`, `compound: Optional[str]`,
    `unit_class_residuals: Optional[dict] = None` (RESERVED, `unit_class_residual_status: str
    = "unresolved"` sibling — G7's real per-lap extractor is compute-deferred; never fabricate).
  - `FeatureViewRow` (per event, car) — `year`, `gp_name`, `constructor`, `model_version: int`,
    `as_of_session: str`, `weekend_relative_basis: dict`, `circuit_conditional_composite:
    Optional[dict]`, `axis_sigma: dict`, `written_at: str` (ISO timestamp).
  Also define `SESSION_ORDER = ("FP1", "FP2", "FP3", "Q")` and `def session_ordinal(session_type:
  str) -> int` (raises ValueError naming the unknown session_type + the known set — mirrors
  `fp_gate_real_extractor.nominal_hours_to_q`'s fail-visibly convention, do not silently
  return a sentinel).
- `src/physics/feature_view/store.py` — `FeatureViewStore` class. Constructor
  `__init__(self, db_path: str, *, must_exist: bool = False)` mirrors
  `src/physics/layer2/estimate_store.py`'s `EstimateStore.__init__` shape exactly (same
  `must_exist` semantics — `FileNotFoundError` before any connect/schema work). Default
  `db_path` for callers who don't specify one: `data/feature_view.db` (a NEW standalone
  SQLite file — do NOT add tables to the existing `physics_estimates.db`; this is a distinct
  product-contract store, not an extension of the internal `session_estimates` store — mirrors
  the `fit_store.py`/`wear/store.py` precedent of a standalone artifact store, NOT the season
  DB). Reuse the `_connect`/`_init_schema`/`_migrate_missing_columns` shape from
  `estimate_store.EstimateStore` (additive `ALTER TABLE ADD COLUMN` self-heal). **Deliberate
  divergence from `EstimateStore`:** every insert method (`insert_weekend_state`,
  `insert_car_basis_posterior`, `insert_lap_evidence`, `insert_feature_view_row`) uses plain
  `INSERT` (never `INSERT OR REPLACE`) — a duplicate natural-key+`model_version` (+
  `as_of_session` for the feature-view table) write must raise `sqlite3.IntegrityError` via a
  `UNIQUE`/`PRIMARY KEY` constraint on that exact column set. State this divergence explicitly
  in the module docstring (readers will reach for `EstimateStore`'s idiom by habit — head that
  off). Provide `load_*` query methods returning `pandas.DataFrame` (mirrors `EstimateStore.load`)
  for each table, and — critically for the leakage test below — a query method whose SQL WHERE
  clause takes an explicit `session_type IN (...)` or `session_ordinal <= ?` restriction as a
  REQUIRED parameter (never optional/defaulted to "all"), so a caller cannot accidentally omit
  the session bound.
- Reuse (import, do not reimplement) `src.physics.layer2.estimate_store_fields.
  effective_axis_sigma`, `.UNRESOLVED_AXIS_SIGMA_FRAC`, `.normalize_axis_status` wherever this
  gate needs axis-status logic.

## Protected Intent
The two gate tests below are THE load-bearing correctness properties for the entire epic's
Phase 5 (append-only contract-freeze; as-of leakage prevention by construction, not by
post-hoc filtering). A test that merely LOOKS like it enforces these, without actually being
unable to pass under a buggy implementation, defeats the entire point of freezing them before
wiring. Do not write a test that would pass against a `SELECT * ... WHERE constructor=?`
(no session predicate) query.

## Test Mode
TDD required — write both gate tests FIRST against the store/records shape, watch them go
RED against a stub/incomplete implementation, then complete the implementation to GREEN. This
is the "freeze the tests before wiring" directive from the governing launch order.

## Close Criteria
- `src/physics/feature_view/{__init__,records,store}.py` exist, no `src.evo_predictor` import
  anywhere in the package (grep-verifiable).
- `tests/unit/physics/feature_view/test_append_only_contract.py`: writes a `FeatureViewRow` at
  `model_version=1` for one natural key, writes a DIFFERENT row at `model_version=2` for the
  SAME natural key, re-reads the `model_version=1` row and asserts it is byte-identical to what
  was originally written (every field, not just a spot check); AND asserts that attempting to
  write a SECOND row with the identical natural key + `model_version` (no as_of/version bump)
  raises `sqlite3.IntegrityError`.
- `tests/unit/physics/feature_view/test_as_of_leakage.py`:
  - Seed `weekend_state_records`/`car_basis_posteriors` rows for FP1/FP2/FP3/Q sessions, with
    DISTINCT SENTINEL axis values per session (e.g. `drag_area_closed_m2` = 101.0/102.0/103.0/
    104.0), across TWO DIFFERENT `(year, gp_name, constructor)` tuples (cross-entity isolation).
  - Query "as of FP1" via the store's as-of-scoped read method; assert the returned data
    reflects ONLY the FP1 sentinel for each entity.
  - Capture every SQL statement executed against the store during that as-of query via
    `sqlite3.Connection.set_trace_callback` (or an equivalent hook on the connection the store
    opens); assert EVERY captured statement reading `weekend_state_records`/
    `car_basis_posteriors` contains an explicit session restriction in its WHERE-clause TEXT
    (e.g. `session_type IN (...)` or `session_ordinal <=`) — not merely that bound params don't
    echo a later sentinel. A statement of the shape `SELECT * FROM ... WHERE constructor=?`
    with no session predicate must FAIL this assertion.
  - NEGATIVE CONTROL: write a second, deliberately-broken query path in the test itself (e.g. a
    small helper that runs `SELECT * FROM weekend_state_records WHERE year=? AND gp_name=? AND
    constructor=?` with no session filter, then filters the returned rows in Python) and assert
    the WHERE-clause-structure check correctly FAILS this broken path — proving the assertion
    can actually catch what it claims to catch, not just pass on the happy-path fixture.
- Both test files pass: `py -m pytest tests/unit/physics/feature_view -q`.
- `py -m src.utils.simplification_limits src/physics/feature_view` clean.

## Allowed Scope
- New directory `src/physics/feature_view/` (all files).
- New directory `tests/unit/physics/feature_view/` (test files for this gate:
  `test_append_only_contract.py`, `test_as_of_leakage.py`; you may also add
  `test_records.py`/`test_store.py` for basic dataclass/store-mechanics coverage if useful).
- Read-only reads of `src/physics/layer2/estimate_store_fields.py` (import only).

## Specific Exclusions
- Do NOT touch `src/physics/layer2/`, `src/physics/weekend_state/`, or any existing file —
  this gate is 100% new files. (#629 owns this directory tree exclusively this run.)
- Do NOT wire real Phase 2/3/4 data into these tests — synthetic fixtures only (G2-G5 wire
  real composers).
- Do NOT create or touch `data/physics_estimates.db` — this gate's tests must use a temp
  SQLite path (e.g. `tmp_path` pytest fixture), never a committed/shared DB file.

## Constraints
- `constraint:physics_region_no_evo_import` — no `src.evo_predictor` import anywhere in
  `src/physics/feature_view/`.
- Append-only: plain `INSERT` only, verified via a real `sqlite3.IntegrityError`, not a
  docstring claim.
- Reuse `effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC`/`normalize_axis_status` from
  `src.physics.layer2.estimate_store_fields` by import — do not reimplement the explicit-unknown
  sigma-widening logic.
- DB hygiene: never write to a committed DB path; tests use `tmp_path`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.feature_view` (new component, `src/physics/feature_view/`).
- **Capability:** new — the Phase-5 feature-view store foundation.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** decision pressure (new component vs layer2 module-leaf) — RESOLVED new
  component; record as a decision candidate at reconcile, do not re-litigate here.
- **Evidence expectations:** the two gate tests ARE the evidence for "append-only
  contract-freeze" and "as-of leakage by construction" claims.

## Deliverable Path Check
- **Committed** — `src/physics/feature_view/__init__.py`, `records.py`, `store.py`; verify via
  `git check-ignore src/physics/feature_view/store.py` exiting 1 (not ignored) before your
  final commit-readiness check.
- **Committed** — `tests/unit/physics/feature_view/*.py`; same `git check-ignore` check.
- **Local-only** — none (this gate produces no `.agent-work` or DB artifacts that should be
  committed; any temp DB the tests create must use `tmp_path`, never landing in the working
  tree at all).

## Required Evidence
- Full pytest output for `py -m pytest tests/unit/physics/feature_view -q` (paste verbatim,
  not summarized).
- The exact `sqlite3.IntegrityError` traceback/message captured by the append-only test's
  duplicate-write assertion (paste it — proves it's real, not a mocked exception).
- The captured SQL statement list from the leakage test's trace callback (paste it) showing
  every WHERE clause the as-of query actually executed.
- `git check-ignore` exit codes for the new files (see Deliverable Path Check).
- `py -m src.utils.simplification_limits src/physics/feature_view` output.

## Verification Commands

```bash
py -m pytest tests/unit/physics/feature_view -q
py -m src.utils.simplification_limits src/physics/feature_view
git check-ignore src/physics/feature_view/store.py; echo "exit=$?"
grep -rn "evo_predictor" src/physics/feature_view/ || echo "clean: no evo_predictor import"
```

## Suggested Model Tier
Stronger (Sonnet) — the by-construction leakage test design has real subtlety (WHERE-clause
introspection + a negative control), and a shallow implementation would silently pass a weaker
test.

## Authority
Structural placement (new component) and the two reserved-slot decisions (process-noise-link +
parc-ferme in `CarBasisPosteriorRecord`; `unit_class_residuals` in `LapEvidenceRecord`) are
already made — do not re-decide them; carry them exactly as specified above.

## Stop Conditions
Stop and return if: the by-construction leakage test cannot be made to fail against the
negative-control broken query (this would mean the test design itself is unsound — escalate,
do not ship a weaker test); a decision outside this handoff's authority is needed; allowed
scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced (paste full pytest output + IntegrityError traceback + captured SQL list), assumptions
used, stop conditions hit, out-of-scope observations, workflow feedback.
