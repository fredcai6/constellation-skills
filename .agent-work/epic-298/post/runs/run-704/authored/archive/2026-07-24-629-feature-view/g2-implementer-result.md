# Implementation Result

## Assigned gate
`g2` -- #629 feature-view Phase-5, build `src/physics/feature_view/build_weekend_state.py`

## Completed slice
Built `src/physics/feature_view/build_weekend_state.py`: a pure composer function
`build_weekend_state_records(model, transformed_df, *, model_version) -> list[WeekendStateRecord]`
that turns each row of an already-fitted `WeekendStateModel`'s `.transform()` output into one G1
`WeekendStateRecord`, enumerating axes via BOTH `model.model_cols()` and `model.layer_sigma_cols()`
(never hand-guessed), applying a real per-row/per-axis resolved/unresolved rule (axis's
`{axis}_car_signal` value AND its `{axis}_car_signal_sigma` both present -> `"resolved"`, sigma
passed through unchanged; otherwise `"unresolved"`, sigma widened via the SAME
`estimate_store_fields.effective_axis_sigma` `store.py` already imports), and never fabricating a
value (NaN normalized to an honest `None`, never zero-filled or dropped).

## Scope
**Files changed:**
- `src/physics/feature_view/build_weekend_state.py` (new)
- `tests/unit/physics/feature_view/test_build_weekend_state.py` (new)
- `.agent-work/629-feature-view/g2-implementer-plan.json` (new -- this run's own driven engine plan)
- `.agent-work/629-feature-view/g2-implementer-result.md` (this file)

**Specific exclusions touched:** no. Did not modify `src/physics/feature_view/records.py` or
`store.py` (G1, frozen/closed -- no defect found, nothing patched), did not modify
`src/physics/weekend_state/` (read-only consumer only -- `WeekendStateModel`, `holdout.split` used
exactly as documented, never edited), and did not read the real `data/physics_estimates.db`
(synthetic frame only, per Test Mode).

## Map Impact
- **Structural anchors touched:** `struct:physics.feature_view` -- added
  `build_weekend_state.py` as a new composer module inside the existing G1-built package.
- **Capabilities added/changed/affected:** new -- `build_weekend_state_records` is the first real
  populator of `WeekendStateRecord` (G1 built only the shape; this gate feeds it real L1-L4 physics
  decomposition output for the first time). Feeds forward into G3-G5 (`CarBasisPosteriorRecord`,
  `LapEvidenceRecord`, `FeatureViewRow` composers, not yet built).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` -- honored,
  grep-verified clean (see Evidence). `WeekendStateModel.fit/transform`'s no-leakage contract is
  read-only consumed, not touched.
- **Decision candidates / resolved decisions:** the resolved/unresolved axis-status rule (value +
  sigma both present -> "resolved") is a NEW convention this gate introduces, exactly as
  pre-authorized in the handoff -- documented explicitly in the module docstring, not re-decided
  beyond that authorization. `round_idx` omission from the stored record is the handoff's
  pre-authorized schema-fit observation, applied as stated (no duplicate `gp_name`-within-year case
  was found in the synthetic test frame or in `frame.py`'s real key columns -- one GP per weekend
  holds).
- **Claims/evidence produced:** the resolved-vs-unresolved contrast (both branches, including the
  "value present but sigma missing -> widen, don't drop" sub-case) is backed by real
  `WeekendStateModel.fit/transform` output on the synthetic frame -- see Evidence below, pasted
  verbatim, not summarized.
- **Trust limitations / drift found:** none found.
- **Triage candidates:** none beyond what the handoff already scopes to G3-G5 (car-basis posterior
  composer, lap-evidence composer, feature-view-row composer, real process-noise-link/parc-ferme
  fits -- all explicitly out of this gate's scope).

## Test mode
**Required:** `test-first` (TDD red -> green, per the handoff's Test Mode section)
**Satisfied:** yes. `test_build_weekend_state.py` was written before `build_weekend_state.py`
existed and observed to fail with a real `ModuleNotFoundError` (pasted below), then the module was
implemented until all 6 new tests passed.

## Evidence

### TDD RED (verbatim, module did not yet exist)

```bash
$ py -m pytest tests/unit/physics/feature_view/test_build_weekend_state.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 0 items / 1 error

=================================== ERRORS ====================================
_ ERROR collecting tests/unit/physics/feature_view/test_build_weekend_state.py _
ImportError while importing test module 'C:\Programs\f1-629\tests\unit\physics\feature_view\test_build_weekend_state.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\unit\physics\feature_view\test_build_weekend_state.py:24: in <module>
    from src.physics.feature_view.build_weekend_state import build_weekend_state_records
E   ModuleNotFoundError: No module named 'src.physics.feature_view.build_weekend_state'
=========================== short test summary info ===========================
ERROR tests/unit/physics/feature_view/test_build_weekend_state.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 0.47s ===============================
```

### TDD GREEN -- full region suite, verbatim (`-v`, G1's 27 + G2's new 6 = 33)

```bash
$ py -m pytest tests/unit/physics/feature_view -v
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collecting ... collected 33 items

tests/unit/physics/feature_view/test_append_only_contract.py::test_older_model_version_row_survives_a_newer_version_write_byte_identical PASSED [  3%]
tests/unit/physics/feature_view/test_append_only_contract.py::test_duplicate_natural_key_and_model_version_raises_real_integrity_error PASSED [  6%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_fp1_returns_only_the_fp1_sentinel_per_entity_no_cross_entity_leak PASSED [  9%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_fp3_includes_fp1_through_fp3_but_excludes_q PASSED [ 12%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_negative_control_broken_query_path_is_correctly_flagged_as_not_session_scoped PASSED [ 15%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_session_is_a_required_parameter_not_optional PASSED [ 18%]
tests/unit/physics/feature_view/test_as_of_leakage.py::test_as_of_unknown_session_fails_visibly PASSED [ 21%]
tests/unit/physics/feature_view/test_build_weekend_state.py::test_one_record_per_input_row PASSED [ 24%]
tests/unit/physics/feature_view/test_build_weekend_state.py::test_resolved_axis_passes_sigma_through_unchanged PASSED [ 27%]
tests/unit/physics/feature_view/test_build_weekend_state.py::test_unresolved_axis_widens_sigma_via_effective_axis_sigma PASSED [ 30%]
tests/unit/physics/feature_view/test_build_weekend_state.py::test_unresolved_with_present_value_widens_not_drops PASSED [ 33%]
tests/unit/physics/feature_view/test_build_weekend_state.py::test_records_write_successfully_via_feature_view_store PASSED [ 36%]
tests/unit/physics/feature_view/test_build_weekend_state.py::test_no_evo_import PASSED [ 39%]
tests/unit/physics/feature_view/test_records.py::test_session_order_is_fp1_fp2_fp3_q PASSED [ 42%]
tests/unit/physics/feature_view/test_records.py::test_session_ordinal_orders_practice_before_quali PASSED [ 45%]
tests/unit/physics/feature_view/test_records.py::test_session_ordinal_matches_index_in_session_order PASSED [ 48%]
tests/unit/physics/feature_view/test_records.py::test_session_ordinal_raises_value_error_naming_unknown_and_known_set PASSED [ 51%]
tests/unit/physics/feature_view/test_records.py::test_weekend_state_record_is_frozen_and_constructible PASSED [ 54%]
tests/unit/physics/feature_view/test_records.py::test_car_basis_posterior_record_reserved_fields_default_none_unresolved PASSED [ 57%]
tests/unit/physics/feature_view/test_records.py::test_car_basis_posterior_record_rejects_a_populated_reserved_field PASSED [ 60%]
tests/unit/physics/feature_view/test_records.py::test_lap_evidence_record_reserved_field_default_none_unresolved PASSED [ 63%]
tests/unit/physics/feature_view/test_records.py::test_lap_evidence_record_rejects_a_populated_reserved_field PASSED [ 66%]
tests/unit/physics/feature_view/test_records.py::test_feature_view_row_is_frozen_and_constructible PASSED [ 69%]
tests/unit/physics/feature_view/test_store.py::test_must_exist_raises_before_any_connect_or_schema_work PASSED [ 72%]
tests/unit/physics/feature_view/test_store.py::test_default_db_path_is_a_standalone_feature_view_file PASSED [ 75%]
tests/unit/physics/feature_view/test_store.py::test_fresh_store_creates_all_four_tables PASSED [ 78%]
tests/unit/physics/feature_view/test_store.py::test_weekend_state_insert_and_load_roundtrip PASSED [ 81%]
tests/unit/physics/feature_view/test_store.py::test_car_basis_posterior_insert_and_load_roundtrip_reserved_fields_stay_none PASSED [ 84%]
tests/unit/physics/feature_view/test_store.py::test_lap_evidence_insert_and_load_roundtrip PASSED [ 87%]
tests/unit/physics/feature_view/test_store.py::test_feature_view_row_insert_and_load_roundtrip PASSED [ 90%]
tests/unit/physics/feature_view/test_store.py::test_migrate_missing_columns_is_idempotent PASSED [ 93%]
tests/unit/physics/feature_view/test_store.py::test_effective_axis_sigma_for_row_reuses_layer2_helper_not_reimplemented PASSED [ 96%]
tests/unit/physics/feature_view/test_store.py::test_normalize_axis_status_is_the_real_layer2_function PASSED [100%]

============================= 33 passed in 0.70s ==============================
```

**Result:** pass (33/33; 27 G1 + 6 new G2).

### Concrete resolved-vs-unresolved `WeekendStateRecord` examples (verbatim, real run against
`WeekendStateModel.fit/transform` on the synthetic frame -- not hand-constructed)

**Fully resolved row** (all three synthetic axes have a real car_signal + sigma):

```
RESOLVED example row (transformed): {'year': 2022, 'gp_name': 'gp3', 'constructor': 'c0',
  'drag_area_closed_m2_car_signal': -0.010788585483154966,
  'drag_area_closed_m2_car_signal_sigma': 0.004741957879677459}

RESOLVED WeekendStateRecord:
WeekendStateRecord(year=2022, gp_name='gp3', session_type='Q', constructor='c0', model_version=1,
  axis_values={'drag_area_closed_m2': -0.010788585483154966, 'max_power_w': -6916.117908843856,
               'brake_decel_ms2': -0.40376796600081954},
  axis_sigma={'drag_area_closed_m2': 0.004741957879677459, 'max_power_w': 2755.6141444859845,
              'brake_decel_ms2': 0.16494690126628353},
  axis_status={'drag_area_closed_m2': 'resolved', 'max_power_w': 'resolved',
               'brake_decel_ms2': 'resolved'})
```

Sigma (`0.004741957879677459`) is passed through UNCHANGED from the model's own
`drag_area_closed_m2_car_signal_sigma` -- exactly the "resolved" branch's contract.

**Same row, `drag_area_closed_m2` axis forced fully unresolved** (both car_signal value AND sigma
NaN -- e.g. a car-season absent from the L4 train pool, per
`layer4_car.test_layer4_missing_pool_or_relative_is_nan_not_fabricated`):

```
UNRESOLVED example row (transformed, forced NaN): {'year': 2022, 'gp_name': 'gp3',
  'constructor': 'c0', 'drag_area_closed_m2_car_signal': nan,
  'drag_area_closed_m2_car_signal_sigma': nan}

UNRESOLVED WeekendStateRecord:
WeekendStateRecord(year=2022, gp_name='gp3', session_type='Q', constructor='c0', model_version=1,
  axis_values={'drag_area_closed_m2': None, 'max_power_w': -6916.117908843856,
               'brake_decel_ms2': -0.40376796600081954},
  axis_sigma={'drag_area_closed_m2': None, 'max_power_w': 2755.6141444859845,
              'brake_decel_ms2': 0.16494690126628353},
  axis_status={'drag_area_closed_m2': 'unresolved', 'max_power_w': 'resolved',
               'brake_decel_ms2': 'resolved'})
```

`drag_area_closed_m2`'s value is honestly `None` (never fabricated) and its sigma is also `None` --
this is `effective_axis_sigma`'s documented "no value, no reference_value -> nothing to synthesize
from" case (this composer passes no `reference_value`, so a fully-absent axis stays fully excluded,
matching the Protected Intent's "never silently drop... but never fabricate either").

**The "value present, only sigma missing" sub-case** (a genuine widen-don't-drop test, same row,
only `drag_area_closed_m2_car_signal_sigma` forced to NaN, value left intact):

```
value-present-sigma-missing row: {'drag_area_closed_m2_car_signal': -0.010788585483154966,
  'drag_area_closed_m2_car_signal_sigma': nan}

WeekendStateRecord:
WeekendStateRecord(year=2022, gp_name='gp3', session_type='Q', constructor='c0', model_version=1,
  axis_values={'drag_area_closed_m2': -0.010788585483154966, 'max_power_w': -6916.117908843856,
               'brake_decel_ms2': -0.40376796600081954},
  axis_sigma={'drag_area_closed_m2': 0.010788585483154966, 'max_power_w': 2755.6141444859845,
              'brake_decel_ms2': 0.16494690126628353},
  axis_status={'drag_area_closed_m2': 'unresolved', 'max_power_w': 'resolved',
               'brake_decel_ms2': 'resolved'})

expected widened sigma (UNRESOLVED_AXIS_SIGMA_FRAC * |value|) = 0.010788585483154966
```

The widened sigma (`0.010788585483154966`) exactly equals `UNRESOLVED_AXIS_SIGMA_FRAC * |value|`
(`1.0 * 0.010788585483154966`) -- the value is carried through (never dropped), and the sigma is
widened (never left fake-precise), per `effective_axis_sigma`'s "present value, absent sigma ->
reserve at least the sentinel fraction" branch.

### `simplification_limits` (verbatim)

```bash
$ py -m src.utils.simplification_limits --paths src/physics/feature_view
PASS (4 files checked)
```

### `evo_predictor` import grep (verbatim, clean)

```bash
$ grep -rn "evo_predictor" src/physics/feature_view/build_weekend_state.py || echo "clean"
clean
```

### `git check-ignore` (verbatim, committed path confirmed)

```bash
$ git check-ignore src/physics/feature_view/build_weekend_state.py; echo "exit=$?"
exit=1
```

Exit 1 == not ignored == will be committed normally.

## TDD evidence, if required
- Failing test observed: `ModuleNotFoundError: No module named 'src.physics.feature_view.build_weekend_state'` (pasted above, full traceback).
- Passing test observed: full region suite above, 33/33 (6 new + 27 G1).
- Refactor while green: no separate refactor pass was needed; the module was written directly to
  its final documented shape (axis enumeration via both `model_cols()`/`layer_sigma_cols()`,
  `_none_if_nan` normalization helper, per-row/per-axis resolved rule) and passed on the first
  full-suite run after implementation.

## Docs/contracts touched
- None outside the new module's own docstring (a new composer contract, not a modification of an
  existing one). `records.py`/`store.py` docstrings (G1) were not touched.

## Assumptions
- `session_type` defaults to `"Q"` when the input `transformed_df` does not carry that column
  (documented explicitly in the module docstring) -- `WeekendStateModel.transform()`'s bare output
  does not itself add a `session_type` column (it isn't one of the four layers' outputs), while the
  real `frame.load_frame()` pathway's frame already carries a constant `session_type='Q'` from its
  own WHERE clause. A caller feeding a real Q-sourced frame gets that column read through unchanged;
  a caller feeding a bare synthetic/test frame (as this gate's own tests do for most cases) gets the
  documented default. This matches the handoff's framing that `session_type` is always `"Q"` for
  this model's current input.
- The car_signal sigma column for each axis is `model.layer_sigma_cols()[axis][-1]` (the LAST entry
  in that ordered list) -- confirmed against `model.py`'s own `layer_sigma_cols()` implementation,
  which always appends `f"{axis}_car_signal_sigma"` last; not hand-guessed.
- No `reference_value` is passed to `effective_axis_sigma` for a fully-absent axis (no value, no
  sigma) -- this composer has no per-axis reference/typical-magnitude table of its own, so a fully
  unresolved axis stays honestly `None` (fully excluded) rather than synthesizing a reference scale
  that doesn't exist anywhere in this gate's inputs. Flagging as a decision candidate: a future gate
  wiring a real reference-magnitude table (e.g. from `frame.AXES`' typical ranges) could tighten
  this, but doing so here would be inventing a number not in scope.

## Stop conditions hit
- None. `round_idx` was not found to be genuinely required (no duplicate `gp_name` within a year in
  either the synthetic test frame or `frame.py`'s real key columns); `WeekendStateModel`'s actual
  output columns matched `model_cols()`/`layer_sigma_cols()`'s stated shape exactly (verified by
  reading `model.py` source directly, not from memory); no decision outside the handoff's stated
  authority was needed.

## Out-of-scope observations
- None beyond what the handoff already names as future gates' job (G3: `CarBasisPosteriorRecord`
  composer; G4: `LapEvidenceRecord` composer; G5: `FeatureViewRow` composer; real
  process-noise-link/parc-ferme fits, both still bounded-deferred per G1's own docstring).

## Workflow Feedback
- **Handoff gaps:** none found -- the handoff's `--paths` correction (flagged by the G1 reviewer)
  was already folded in; the verification commands ran exactly as written once the PATH prepend was
  applied.
- **Context rediscovered:** the same PATH-resolution note from the G1 result carried forward
  identically in this session (bare `py` on `PATH` first resolves a pytest-less interpreter;
  prepending `/c/Users/fredc/AppData/Local/Microsoft/WindowsApps` fixes it) -- the handoff already
  named this explicitly this time, so it cost no rediscovery time; noting it held.
- **Instructions improvised around:** none. The handoff's seam citations (`model_cols()`,
  `layer_sigma_cols()`, the resolved/unresolved rule, the `round_idx` omission rationale) all
  matched source exactly on verification, so no improvisation was needed.
- **What would have made this easier:** nothing concrete to add -- this handoff was unusually
  precise (exact line ranges, exact function names, the pre-authorized `round_idx` decision spelled
  out) and needed no deviation.

## Return status
`complete`
