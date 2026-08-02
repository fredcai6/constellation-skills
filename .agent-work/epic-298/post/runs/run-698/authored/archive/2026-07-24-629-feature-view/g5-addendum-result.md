# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5` addendum (two Admiral-ruled additions on top of the already-built/passing G5 gate)

## Completed slice
Both additions landed and verified:
1. Reserved transition-sigma widening on `FeatureViewRow` (additive `transition_axis_status`
   field + flat widening logic in `build_feature_view_row`, reusing `effective_axis_sigma`
   verbatim per the handoff's specified snippet).
2. Forward-looking evo-side import-boundary test
   (`tests/unit/physics/feature_view/test_evo_import_boundary.py`), vacuously green today.

## Scope
**Files changed:**
- `src/physics/feature_view/records.py` — added `transition_axis_status: dict =
  field(default_factory=dict)` to `FeatureViewRow` (one additive field, no other change to
  this file).
- `src/physics/feature_view/store.py` — added `transition_axis_status` to
  `_FEATURE_VIEW_ROW_JSON_COLS` (one-line tuple addition, no other change to this file).
- `src/physics/feature_view/build_feature_view.py` — added the import of `SESSION_ORDER` and
  `effective_axis_sigma` (from `store.py`'s re-export), and the widening loop + population of
  `transition_axis_status` in `build_feature_view_row`, plus passing the new field into the
  constructed `FeatureViewRow`.
- `tests/unit/physics/feature_view/test_transition_sigma_widening.py` — new file, 6 tests for
  Addition 1.
- `tests/unit/physics/feature_view/test_evo_import_boundary.py` — new file, 2 tests for
  Addition 2.

**Specific Exclusions touched:** no. `build_weekend_state.py`, `build_car_basis.py`,
`build_lap_evidence.py`, `read.py`, and every other existing field on any record were left
untouched, as instructed.

## Behavior changed
Yes. `build_feature_view_row` now widens `axis_sigma` for every axis when `as_of_session !=
"Q"` (flat reserved-unresolved floor via `effective_axis_sigma(..., "unresolved")`, `max()`
against the source sigma so it never narrows), and stamps `transition_axis_status[axis]` as
`"unresolved"` in that case or `"resolved"` when `as_of_session == "Q"` (terminal, no forward
transition). `FeatureViewRow` gained one new defaulted field; all existing construction call
sites (tests + `build_feature_view.py`'s own prior construction) continue to work unchanged
because the field defaults to `{}`.

## Map Impact
- **Structural anchors touched:** `struct:src.physics.feature_view.records.FeatureViewRow` —
  additive field `transition_axis_status`; `struct:src.physics.feature_view.build_feature_view`
  — widening logic added to `build_feature_view_row`.
- **Capabilities added/changed/affected:** the feature-view composite now carries an honest,
  inspectable widened-sigma cost for not-yet-observed Q readings on non-terminal as-of reads —
  a new observable behavior a downstream consumer (e.g. #630) can branch on via
  `transition_axis_status`.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — reinforced
  with the new reverse-direction test guarding the evo->physics boundary shape; the reserved
  `CarBasisPosteriorRecord.process_noise_link` field's "reserved, no fit exists yet" status is
  unchanged (this widening only borrows its narrative justification, does not populate it).
- **Decision candidates:** none new — both additions were fully Admiral-ruled, no design choice
  made here.
- **Claims/evidence produced:** `84/84 tests/unit/physics/feature_view green` (see Evidence);
  `simplification_limits clean over src/physics/feature_view (8 files)`.
- **Trust limitations / drift found:** see Workflow Feedback below — `read.py`'s existing
  `read_feature_view` reconstructs `FeatureViewRow` via named kwargs (not a generic
  `**row_dict`), so a row read back through `read_feature_view` will get the *default* `{}` for
  `transition_axis_status` rather than the persisted value, until `read.py` is updated to pass
  it through. The handoff's exclusion says not to touch `read.py`, so this was left as-is per
  instruction, but it means the field does not yet round-trip end-to-end through the sanctioned
  evo-facing read surface.
- **Triage candidates:** wire `transition_axis_status` through `read.py`'s reconstruction (small
  follow-up, currently the field silently returns `{}` via `read_feature_view` even though it is
  correctly persisted/loaded at the store layer).

## Test mode
**Required:** test-after (mechanical, fully-specified addendum; not a TDD-red/green scenario per
the handoff's "Suggested Model Tier: Simple bounded — both additions are fully mechanical")
**Satisfied:** yes — new tests added and run green alongside the full existing suite.

## Evidence

```bash
cd /c/Programs/f1-629
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view -q
```

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 84 items

tests\unit\physics\feature_view\test_append_only_contract.py ..          [  2%]
tests\unit\physics\feature_view\test_as_of_leakage.py .....              [  8%]
tests\unit\physics\feature_view\test_build_car_basis.py ...............  [ 26%]
tests\unit\physics\feature_view\test_build_feature_view.py ..........    [ 38%]
tests\unit\physics\feature_view\test_build_lap_evidence.py .........     [ 48%]
tests\unit\physics\feature_view\test_build_weekend_state.py ......       [ 55%]
tests\unit\physics\feature_view\test_e2e_integration.py .                [ 57%]
tests\unit\physics\feature_view\test_evo_import_boundary.py ..           [ 59%]
tests\unit\physics\feature_view\test_import_boundary.py .                [ 60%]
tests\unit\physics\feature_view\test_read.py .......                     [ 69%]
tests\unit\physics\feature_view\test_records.py ..........               [ 80%]
tests\unit\physics\feature_view\test_store.py ..........                 [ 92%]
tests\unit\physics\feature_view\test_transition_sigma_widening.py ...... [100%]

============================= 84 passed in 2.38s ==============================
```

The four G1 tests named in the handoff (`test_records.py`, `test_store.py`,
`test_append_only_contract.py`, `test_as_of_leakage.py`) are all present in the above run and
pass unchanged (10, 10, 2, 5 tests respectively — none needed editing).

```bash
py -m src.utils.simplification_limits --paths src/physics/feature_view
```

```
PASS (8 files checked)
```

**Concrete before/after example (FP1 vs Q, same entity)** — from
`test_terminal_session_marks_resolved_and_does_not_widen` and
`test_non_terminal_session_widens_and_marks_unresolved`:
- Seeded car_basis at `"Q"`: `value=1.04, sigma=0.05` → `as_of_session="Q"` produces
  `transition_axis_status["drag_area_closed_m2"] == "resolved"`, `axis_sigma == 0.05`
  (unchanged).
- Seeded car_basis at `"FP1"`: `value=1.01, sigma=0.05` → `as_of_session="FP1"` produces
  `transition_axis_status["drag_area_closed_m2"] == "unresolved"`, `axis_sigma ==
  1.01` (widened: `UNRESOLVED_AXIS_SIGMA_FRAC(1.0) * abs(1.01) = 1.01 > 0.05`, so the reserved
  floor dominates via `max()`).

**Flat-widening proof (FP1 vs FP3, same source sigma)** — from
`test_flat_widening_fp1_and_fp3_give_same_magnitude_for_equal_source_sigma`: with only one
car_basis row seeded (`"FP1"`, `value=1.01, sigma=0.05`), both `as_of_session="FP1"` and
`as_of_session="FP3"` resolve to that SAME source row via `load_as_of`'s most-recent-present
rule, and both produce the identical widened `axis_sigma["drag_area_closed_m2"] ==
1.01` — proving the widening term does not scale with hop-count (FP1→Q spans 3 links, FP3→Q
spans 1) or clock distance.

**No-narrow proof** — from `test_max_never_narrows_an_already_wider_source_sigma`: source
sigma seeded at `5.0` (already above the reserved floor of `1.01`) stays `5.0` after widening —
`max()` never pulled it down.

**Evo-side import-boundary scan sanity output** (from the `-s` run,
`test_evo_import_boundary.py`):
```
scanned 118 src/evo_predictor .py files for feature_view/layer2 imports
```
118 >= the required 10-file vacuousness floor; zero offenders found (test passes, vacuously
true today — no `src/evo_predictor/` file currently imports this package or
`src.physics.layer2`).

## TDD evidence, if required
Not applicable — test-after mode per the handoff's own model-tier note (fully mechanical,
Admiral-specified changes; no red/green cycle required). Tests were written immediately
alongside the implementation and observed green on first run together with the rest of the
suite (no separate red capture taken).

## Docs/contracts touched
- None. `FeatureViewRow`'s own docstring (per Allowed Scope: "ONE additive field... No other
  change to this file") was intentionally left untouched — the field's semantics are documented
  in the new test file's module docstring and in `build_feature_view.py`'s inline comment at the
  widening site instead.

## Assumptions
- The "value" argument to `effective_axis_sigma(value, sigma, "unresolved")` in the widening
  call is the composed `weekend_relative_basis[axis]` (the axis's own composed value at that
  point in the function) — the handoff's snippet names it generically as `value`/`sigma` without
  pinning the source; this mirrors `store.py`'s own `effective_axis_sigma_for_row` wrapper
  pattern (`axis_values.get(axis)` paired with `axis_sigma.get(axis)`), so this reading is
  carried, not invented.
- `_seed_one_car_basis_row`'s helper in the new test file constructs `CarBasisPosteriorRecord`
  directly (mirrors `test_build_feature_view.py`'s own `_seed_car_basis` helper style) rather
  than reusing that file's helper directly, since the new tests needed single-axis,
  single-session control not offered by the existing two-axis fixture.

## Stop conditions hit
None. Neither addition forced an undocumented magnitude/scaling choice, and no existing
`FeatureViewRow` construction call site broke (the field is defaulted; all pre-existing call
sites — in `build_feature_view.py` itself, `read.py`, and every existing test — construct
without naming it and get `{}`).

## Out-of-scope observations
- `read.py`'s `read_feature_view` reconstructs `FeatureViewRow` via explicit named kwargs and
  does NOT pass `transition_axis_status` through, so a row round-tripped through the sanctioned
  evo-facing read surface currently loses this field back to its `{}` default even though the
  store correctly persists and loads it. The handoff states read.py "already passes
  transition_axis_status through generically via ... JSON deserialization" — that claim is true
  only at the `store.load_feature_view_rows` DataFrame layer (which is generic over
  `_FEATURE_VIEW_ROW_JSON_COLS`), not at `read.py`'s own explicit reconstruction step one layer
  up. Per the explicit exclusion ("do not modify read.py's existing behavior"), this was left
  untouched; flagging as a triage candidate for a follow-up one-line fix
  (`transition_axis_status=row["transition_axis_status"]`) in `read.py`'s constructor call.

## Workflow Feedback
- **Handoff gaps:** the claim that `read.py` "already passes `transition_axis_status` through
  generically" doesn't hold at `read.py`'s own explicit-kwarg reconstruction step (see Out-of-
  scope observations above) — worth a one-line handoff correction or a follow-up ticket rather
  than leaving the discrepancy implicit.
- **Context rediscovered:** none beyond normal source reading — the handoff's mechanical
  snippet and the surrounding module docstrings were sufficient to implement both additions
  without re-deriving any design.
- **Instructions improvised around:** none — both additions were implementable exactly as
  specified; the one edge case worth flagging (whether the outer `max(sigma, transition_widened)`
  could ever crash on a `None` source `sigma` combined with a non-`None` `transition_widened`) is
  a pre-existing shape in the Admiral's own specified snippet, not something this run had to
  improvise around, and did not manifest in any real fixture tested here.
- **What would have made this easier:** fixing the `read.py` claim above in the handoff before
  dispatch (or explicitly scoping it out with a stated reason) would have removed the one
  ambiguity this run had to resolve by judgment.

## Return status
`complete`
