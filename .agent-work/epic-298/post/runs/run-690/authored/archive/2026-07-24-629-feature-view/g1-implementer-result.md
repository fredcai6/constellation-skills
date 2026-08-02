# Implementation Result

## Assigned gate
`g1` (execute.json: g1-implement) -- #629 feature-view Phase-5 store foundation

## Completed slice
Built `src/physics/feature_view/` (new component, sibling to `src/physics/weekend_state/` and
`src/physics/layer2/`): four frozen record dataclasses (`records.py`) + an append-only,
as-of-scoped SQLite store (`store.py`) against SYNTHETIC fixture data only. Both protected gate
tests (`test_append_only_contract.py`, `test_as_of_leakage.py`) are written and green, per the
handoff's TDD-first requirement (red observed before the corresponding source file existed for
`records.py`/`store.py`; the two protected gate tests were verified real -- including a working
negative control -- against the store already built for m2/m3, per the handoff's explicit
allowance for that case).

## Scope
**Files changed:**
- `src/physics/feature_view/__init__.py` (new)
- `src/physics/feature_view/records.py` (new)
- `src/physics/feature_view/store.py` (new)
- `tests/unit/physics/feature_view/__init__.py` (new)
- `tests/unit/physics/feature_view/test_records.py` (new)
- `tests/unit/physics/feature_view/test_store.py` (new)
- `tests/unit/physics/feature_view/test_append_only_contract.py` (new)
- `tests/unit/physics/feature_view/test_as_of_leakage.py` (new)
- `.agent-work/629-feature-view/g1-implementer-plan.json` (new -- this run's own driven engine plan)

**Specific exclusions touched:** no. Did not touch `src/physics/layer2/`, `src/physics/weekend_state/`,
`data/physics_estimates.db`, or wire any real Phase 2-4 data. All tests use `tmp_path`; no
committed/shared DB file was created or touched.

## Map Impact
- **Structural anchors touched:** `struct:physics.feature_view` -- new component created exactly
  as scoped: `src/physics/feature_view/{__init__,records,store}.py`.
- **Capabilities added/changed/affected:** new -- the Phase-5 feature-view store foundation now
  exists: 4 record shapes + an append-only SQLite store with an as-of-scoped read path
  (`FeatureViewStore.load_as_of`). No real Phase 2-4 wiring yet (G2-G5's job).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` -- honored;
  verified by grep (no literal prediction-runtime import or reference anywhere in the package;
  docstrings phrase the boundary the same way `src.physics.weekend_state.model` does, to avoid a
  docstring-only substring false-triggering a naive grep check -- see Workflow Feedback).
- **Decision candidates / resolved decisions:** the two reserved-slot decisions
  (`process_noise_link`/`parc_ferme_step` on `CarBasisPosteriorRecord`; `unit_class_residuals` on
  `LapEvidenceRecord`) were carried exactly as specified in the handoff's Authority section --
  not re-decided. I added one small extension beyond the literal handoff text: each RESERVED field
  is now enforced at construction time via a `__post_init__` guard that raises `ValueError` if a
  caller passes a non-`None` value -- this was not explicitly requested, but follows directly from
  "never compute a value for either field in this gate" and the project's fail-visibly doctrine
  (`global-everyone.md`: "Fail visibly rather than emit plausible wrong output"). Flagging as a
  decision candidate in case a later gate (G2+) intentionally wants to populate one of these and
  finds the guard too strict -- it is a one-line removal at that point, not a redesign.
- **Claims/evidence produced:** the append-only contract-freeze claim and the as-of
  leakage-prevention-by-construction claim (including a working negative control) are both backed
  by the pasted evidence below -- see the Evidence section.
- **Trust limitations / drift found:** none found. This is a from-scratch new component; no
  existing map area was touched.
- **Triage candidates:** none raised beyond what the handoff already scoped to G2-G5.

## Test mode
**Required:** `test-first` (TDD red -> green, explicitly mandated by the handoff for both gate
tests)
**Satisfied:** yes. `test_records.py` and `test_store.py` were each written before their
corresponding source module existed and observed to fail on `ModuleNotFoundError` (real RED, not
simulated). `test_append_only_contract.py` and `test_as_of_leakage.py` were written per the
handoff's Close Criteria and verified against the by-then-existing store (built out fully during
the `records.py`/`store.py` slices) -- both passed immediately, but every assertion was verified
to be REAL: the `sqlite3.IntegrityError` is a genuine constraint violation (traceback pasted
below, not mocked), and the as-of leakage test's negative control was proven capable of actually
FAILING the WHERE-clause-structure check (see its own dedicated test,
`test_negative_control_broken_query_path_is_correctly_flagged_as_not_session_scoped`) -- so the
Stop Condition ("if the negative control cannot be made to fail as designed") was never triggered.

## Evidence

### Full suite (verbatim, verbose)

```bash
$ py -m pytest tests/unit/physics/feature_view -v
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collecting ... collected 27 items

tests/unit/physics/feature_view/test_append_only_contract.py::test_older_model_version_row_survives_a_newer_version_write_byte_identical PASSED [  3%]
tests/unit/physics/feature_view/test_append_only_contract.py::test_duplicate_natural_key_and_model_version_raises_real_integrity_error PASSED [  7%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_fp1_returns_only_the_fp1_sentinel_per_entity_no_cross_entity_leak PASSED [ 11%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_fp3_includes_fp1_through_fp3_but_excludes_q PASSED [ 14%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_negative_control_broken_query_path_is_correctly_flagged_as_not_session_scoped PASSED [ 18%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_session_is_a_required_parameter_not_optional PASSED [ 22%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_unknown_session_fails_visibly PASSED [ 25%]
tests/unit/physics/feature_view/test_records.py::test_session_order_is_fp1_fp2_fp3_q PASSED [ 29%]
tests/unit/physics/feature_view/test_records.py::test_session_ordinal_orders_practice_before_quali PASSED [ 33%]
tests/unit/physics/feature_view/test_records.py::test_session_ordinal_matches_index_in_session_order PASSED [ 37%]
tests/unit/physics/feature_view/test_records.py::test_session_ordinal_raises_value_error_naming_unknown_and_known_set PASSED [ 40%]
tests/unit/physics/feature_view/test_records.py::test_weekend_state_record_is_frozen_and_constructible PASSED [ 44%]
tests/unit/physics/feature_view/test_records.py::test_car_basis_posterior_record_reserved_fields_default_none_unresolved PASSED [ 48%]
tests/unit/physics/feature_view/test_records.py::test_car_basis_posterior_record_rejects_a_populated_reserved_field PASSED [ 51%]
tests/unit/physics/feature_view/test_records.py::test_lap_evidence_record_reserved_field_default_none_unresolved PASSED [ 55%]
tests/unit/physics/feature_view/test_records.py::test_lap_evidence_record_rejects_a_populated_reserved_field PASSED [ 59%]
tests/unit/physics/feature_view/test_records.py::test_feature_view_row_is_frozen_and_constructible PASSED [ 62%]
tests/unit/physics/feature_view/test_store.py::test_must_exist_raises_before_any_connect_or_schema_work PASSED [ 66%]
tests/unit/physics/feature_view/test_store.py::test_default_db_path_is_a_standalone_feature_view_file PASSED [ 70%]
tests/unit/physics/feature_view/test_store.py::test_fresh_store_creates_all_four_tables PASSED [ 74%]
tests/unit/physics/feature_view/test_store.py::test_weekend_state_insert_and_load_roundtrip PASSED [ 77%]
tests/unit/physics/feature_view/test_store.py::test_car_basis_posterior_insert_and_load_roundtrip_reserved_fields_stay_none PASSED [ 81%]
tests/unit/physics/feature_view/test_store.py::test_lap_evidence_insert_and_load_roundtrip PASSED [ 85%]
tests/unit/physics/feature_view/test_store.py::test_feature_view_row_insert_and_load_roundtrip PASSED [ 88%]
tests/unit/physics/feature_view/test_store.py::test_migrate_missing_columns_is_idempotent PASSED [ 92%]
tests/unit/physics/feature_view/test_store.py::test_effective_axis_sigma_for_row_reuses_layer2_helper_not_reimplemented PASSED [ 96%]
tests/unit/physics/feature_view/test_store.py::test_normalize_axis_status_is_the_real_layer2_function PASSED [100%]

============================= 27 passed in 0.86s ==============================
```

**Result:** pass (27/27).

### The real `sqlite3.IntegrityError` traceback (append-only contract test, verbatim)

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collecting ... collected 2 items

tests/unit/physics/feature_view/test_append_only_contract.py::test_older_model_version_row_survives_a_newer_version_write_byte_identical PASSED
tests/unit/physics/feature_view/test_append_only_contract.py::test_duplicate_natural_key_and_model_version_raises_real_integrity_error CAPTURED sqlite3.IntegrityError traceback:
Traceback (most recent call last):
  File "C:\Programs\f1-629\tests\unit\physics\feature_view\test_append_only_contract.py", line 72, in test_duplicate_natural_key_and_model_version_raises_real_integrity_error
    store.insert_feature_view_row(v1)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^
  File "C:\Programs\f1-629\src\physics\feature_view\store.py", line 248, in insert_feature_view_row
    self._insert("feature_view_rows", record)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Programs\f1-629\src\physics\feature_view\store.py", line 185, in _insert
    con.execute(
    ~~~~~~~~~~~^
        f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders})',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        [d[c] for c in cols],
        ^^^^^^^^^^^^^^^^^^^^^
    )
    ^
sqlite3.IntegrityError: UNIQUE constraint failed: feature_view_rows.year, feature_view_rows.gp_name, feature_view_rows.constructor, feature_view_rows.model_version, feature_view_rows.as_of_session

PASSED

============================== 2 passed in 0.47s ==============================
```

(Line numbers in the traceback are from the `store.py` version at the moment the test was first
run against it during the m3 gate; the file has since gained a few comment-line edits during m5's
docstring fix for the evo-import grep check, so the exact line numbers may shift by 1-2 lines on
re-run, but the same real `sqlite3.IntegrityError` fires identically.)

### Captured SQL statement list (as-of leakage test, verbatim reproduction)

```
RESULT weekend_state axis_values: [{'drag_area_closed_m2': 101.0}]

CAPTURED SQL statements during load_as_of(as_of_session="FP1"):
1. SELECT * FROM "weekend_state_records" WHERE year=2024 AND gp_name='Belgium' AND constructor='Red Bull' AND session_type IN ('FP1')
2. SELECT * FROM "car_basis_posteriors" WHERE year=2024 AND gp_name='Belgium' AND constructor='Red Bull' AND session_type IN ('FP1')
```

Both statements carry an explicit `session_type IN (...)` restriction in their own WHERE-clause
text -- this is what `test_as_of_leakage.py`'s `_all_statements_session_scoped` checker asserts
programmatically (via `sqlite3.connect` wrapped with `set_trace_callback`, since the store opens a
new connection per call rather than one long-lived connection the test could grab ahead of time).
The negative-control test in the same file
(`test_negative_control_broken_query_path_is_correctly_flagged_as_not_session_scoped`) proves the
checker correctly FAILS a deliberately-broken query with no session predicate in its SQL (fetch-all
+ Python-side post-filter) -- confirming the check can actually catch what it claims to catch.

### `git check-ignore` exit codes (new committed files)

```bash
$ git check-ignore src/physics/feature_view/__init__.py src/physics/feature_view/records.py src/physics/feature_view/store.py
exit=1
$ git check-ignore tests/unit/physics/feature_view/test_append_only_contract.py
exit=1
$ git check-ignore tests/unit/physics/feature_view/test_as_of_leakage.py
exit=1
```

Exit 1 on every path == not ignored == will be committed normally.

### `evo_predictor` / prediction-runtime import grep (clean)

```bash
$ grep -rn "evo_predictor" src/physics/feature_view/
clean: no evo_predictor import
```

(No import statement anywhere. Docstrings that originally named the literal `src.evo_predictor`
path in prose were reworded during this gate to phrase the boundary the way
`src.physics.weekend_state.model` already does -- "No prediction-runtime (``evo``) import" --
since a docstring-only prose mention of the literal module path would (harmlessly, but
misleadingly) trip a naive substring grep even with zero real imports. See Workflow Feedback.)

### `simplification_limits` (verbatim)

```bash
$ py -m src.utils.simplification_limits --paths src/physics/feature_view
PASS (3 files checked)
```

Note: the handoff's literal verification command (`py -m src.utils.simplification_limits
src/physics/feature_view`, no `--paths`) does not match the script's actual CLI (positional args
are not accepted -- `--paths` is required). Ran the equivalent `--paths src/physics/feature_view`
form instead; flagged below in Workflow Feedback.

## TDD evidence, if required

- Failing test observed:
  - `test_records.py` against a not-yet-existing `records.py`:
    `ModuleNotFoundError: No module named 'src.physics.feature_view'`.
  - `test_store.py` against a not-yet-existing `store.py`:
    `ModuleNotFoundError: No module named 'src.physics.feature_view.store'`.
  - `test_append_only_contract.py` / `test_as_of_leakage.py`: per the handoff's explicit
    allowance ("if store.py already satisfies it because m2 over-built, that is fine, but ...
    verified for real"), these were written against the ALREADY-BUILT store (built out fully
    while implementing `store.py`'s insert/load/as-of mechanics in the m2 slice) and passed
    immediately -- every assertion was still verified for REAL sqlite3 behavior (see the pasted
    IntegrityError traceback and the working negative control above), not a docstring claim.
- Passing test observed: full suite above, 27/27.
- Refactor while green: no refactor pass was needed; the two docstring edits during close-out
  (removing the literal `evo_predictor` substring from prose) were made and the full suite was
  re-run green afterward (27/27, same result).

## Docs/contracts touched
- None outside the new package's own module/class docstrings (this gate creates the contract; it
  does not modify an existing one).

## Assumptions
- "car" in the handoff's `WeekendStateRecord (per event, session, car)` means **constructor**, not
  an individual driver/chassis -- confirmed against `src/physics/weekend_state/model.py`'s
  `DEFAULT_SEASON_KEY = ("year", "constructor")` (the existing L1-L4 weekend-state model's own
  season key), which is the model whose output this record type carries.
- `SESSION_ORDER` is deliberately `(FP1, FP2, FP3, Q)` only (no Race) -- the handoff states this
  exactly, and it matches the pre-race prediction-chain framing (`chain_position`/`prior_session`
  on `CarBasisPosteriorRecord`) the rest of the handoff describes.
- The as-of-scoped required-restriction query method is implemented as `FeatureViewStore.load_as_of`
  (one method covering both `weekend_state_records` and `car_basis_posteriors`, since the handoff's
  leakage test seeds both tables and queries "as of" a session for one entity) rather than two
  separate per-table methods -- reduces duplication for what the handoff frames as one leakage
  surface.

## Stop conditions hit
- None. In particular, the as-of leakage test's negative control was verified to actually fail
  the WHERE-clause-structure check (see the dedicated test for this), so the "cannot be made to
  fail" stop condition was never triggered.

## Out-of-scope observations
- None beyond what the handoff already names as G2-G5's job (real Phase 2-4 wiring, real
  process-noise-link fit, real parc-ferme distribution fit, real per-lap unit-class-residual
  extractor).

## Workflow Feedback

- **Handoff gaps:** the handoff's own `py -m src.utils.simplification_limits src/physics/feature_view`
  verification command does not match the script's actual CLI -- `main()` in
  `src/utils/simplification_limits.py` only accepts `--paths [PATHS ...]`, not a bare positional
  path; running the handoff's literal command raises an argparse error (unrecognized argument).
  Ran `--paths src/physics/feature_view` instead, which is almost certainly the intended form.
- **Context rediscovered:** the correct Python interpreter on this box is NOT the bare `py` that
  resolves first on `PATH` in this environment's POSIX shell (`/c/Users/fredc/.local/bin/py`,
  which resolves to a `codex-runtimes` Python 3.12 with no `pytest` installed) -- the one with
  `pytest`/the project's dependencies is
  `/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe` (Python 3.14.3, matches
  `C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64` from CLAUDE.md's Python Invocation
  note). This also broke the engine's own `command`-kind postconditions the first time (they run
  under the same POSIX shell and inherited the same wrong-`py`-first `PATH`, so the very first
  `advance m1-records` failed on `ModuleNotFoundError: No module named 'pytest'` even though the
  test genuinely passed under the correct interpreter) -- fixed by prepending the WindowsApps
  directory to `PATH` in every shell invocation that runs `checklist_engine.py` or `pytest` for
  the rest of the run. Worth carrying forward as a standing note for this box/session specifically
  (not necessarily a global CLAUDE.md fact, since it may be an artifact of this particular
  sandboxed shell's PATH setup) so the next agent doesn't lose a step rediscovering it.
- **Instructions improvised around:** the handoff's grep check ("no `src.evo_predictor` import
  anywhere in the package (grep-verifiable)") is written as a literal substring check, but my own
  module docstrings legitimately needed to NAME the constraint in prose to explain it to the next
  reader -- which, taken literally, would make a naive `grep -rn evo_predictor` "fail" even with
  zero real imports. Resolved by rewording the docstrings to state the boundary the way
  `src.physics.weekend_state.model` already does (mentioning "evo" without the literal dotted
  `src.evo_predictor` path) rather than weakening the grep check itself -- the check stays a
  genuine substring grep, and it is now actually clean.
- **What would have made this easier:** naming the correct interpreter path explicitly in the
  handoff (or in `CREW_CONTEXT.md`) would have saved the PATH-resolution rediscovery above; and
  phrasing the grep-verifiable constraint as "no `import ... evo_predictor` / `from ...
  evo_predictor` statement" (rather than a bare substring) would have avoided the
  docstring-vs-grep tension entirely, without requiring any rewording.

## Return status
`complete`
