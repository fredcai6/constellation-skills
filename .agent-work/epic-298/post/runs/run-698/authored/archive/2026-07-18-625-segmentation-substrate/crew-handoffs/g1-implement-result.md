# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1 (execute.json: g1-implement)` — Straight-arc grouping + descriptor axis

## Completed slice
Generalized `_contiguous_runs` in `src/physics/layer2/arcs.py` to accept a `regimes: set[str]`
parameter, added `StraightArc`/`identify_straight_arcs` mirroring the existing
`BrakingArc`/`identify_braking_arcs` pattern, and added a new
`src/physics/layer2/corner_descriptors.py` module computing a lateral-g/radius descriptor axis
from `grip_bin_obs`-shaped rows (`bin_row_to_descriptor`, `descriptors_from_frame`). All four
close criteria in the handoff are met.

## Scope
**Files changed:**
- `src/physics/layer2/arcs.py` (edit)
- `src/physics/layer2/corner_descriptors.py` (new)
- `tests/unit/physics/layer2/test_arcs.py` (edit — added `TestIdentifyStraightArcs`, 4 new cases)
- `tests/unit/physics/layer2/test_corner_descriptors.py` (new — 9 cases)

**Specific exclusions touched:** no — `segment_classifier.py`, DB files, `circuits.yaml`,
production defaults untouched; no imports from `evo_predictor`/`latent_power`/`compound_prior`
anywhere in the new/changed code (verified by reading the diff — the only new import is
`src.physics.physics_data_models._VALID_REGIMES`, within the physics region).

## Behavior changed
Yes, additively only. `identify_braking_arcs`'s public call signature
(`identify_braking_arcs(samples, min_len=3, frontier_decel_quantile=0.6)`) is unchanged; its
body now calls the generalized `_contiguous_runs(samples, min_len, {_BRAKE_REGIME})` instead of
the old two-argument form, which is behaviorally identical (a single-element regime set reduces
to the old hardcoded `==` check). All 3 pre-existing `test_arcs.py` tests pass unmodified,
confirming byte-identical behavior for the real caller (`braking_report.py::plot_arcs`, called
positionally with defaults — see Workflow Feedback on the handoff's file citation).

`_contiguous_runs` before/after signature:
```diff
-def _contiguous_runs(samples: Sequence, min_len: int) -> list[list[int]]:
+def _contiguous_runs(samples: Sequence, min_len: int, regimes: set[str]) -> list[list[int]]:
     runs: list[list[int]] = []
     cur: list[int] = []
     for i, s in enumerate(samples):
-        if s.regime == _BRAKE_REGIME:
+        if s.regime in regimes:
             cur.append(i)
```
`identify_braking_arcs` internally updated: `runs = _contiguous_runs(samples, min_len, {_BRAKE_REGIME})`
(was `_contiguous_runs(samples, min_len)`). `identify_straight_arcs` reuses the same generalized
function with `_STRAIGHT_REGIMES` (derived from `physics_data_models._VALID_REGIMES - {"corner"}`,
not a second hand-maintained literal set) — confirms `_contiguous_runs` was generalized, not
duplicated: it is the single grouping implementation both `identify_braking_arcs` and
`identify_straight_arcs` call.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — `src/physics/layer2/arcs.py`
  (generalized `_contiguous_runs`, added `StraightArc`/`identify_straight_arcs`, both public);
  `src/physics/layer2/corner_descriptors.py` (new module, `struct:physics.layer2` member) —
  `bin_row_to_descriptor`/`descriptors_from_frame` public pure functions.
- **Capabilities added/changed/affected:** straight-as-first-class-segment grouping (new,
  `identify_straight_arcs`) — one non-frontier-filtered `StraightArc` per contiguous
  non-corner run; lateral-g/radius descriptor axis (new, `corner_descriptors.py`) — per-row
  `(radius_m, lateral_g)` from a `grip_bin_obs` row via the circular-motion relation
  `a_lat = v^2/R`. Both are the named Phase-1 deliverables of this gate; both are pure
  functions with no DB I/O, consumed by later Phase 2/4 work (not yet wired to a caller).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored
  (only `src.physics.*` imports added). `mu_lat_p90` g-units assumption from
  `grip_bin_obs.py`'s docstring — honored, no re-division by `G`/`GRAVITY_MS2` in
  `corner_descriptors.py`.
- **Claims/evidence produced:** `_contiguous_runs` generalization is non-duplicating (single
  grouping implementation, verified by diff + both callers reading it); `identify_braking_arcs`
  external signature/behavior is byte-identical (verified by unmodified pre-existing tests still
  passing verbatim); `bin_row_to_descriptor`'s formula verified against 2 independent
  hand-computed values (L1 analytical reference per project physics-test convention).
- **Trust limitations / drift found:** the handoff's "verify... from `session_braking.py`'s call
  site" instruction pointed at the wrong file — see Workflow Feedback below. Low-stakes (the
  actual signature/behavior requirement was still correctly inferred and verified), but the map
  anchor citing `session_braking.py` as a caller of `identify_braking_arcs` should be corrected
  to `braking_report.py::plot_arcs` if/when Cartographer reconciles this area.
- **Triage candidates:** none raised by this gate's work.

## Test mode
**Required:** `test-after` (project norm for physics fitting code; both new pieces are pure
functions, tests written alongside implementation per handoff's Test Mode section)
**Satisfied:** yes — every new function/dataclass has tests written in the same step it was
implemented, no separate after-the-fact pass.

## Evidence

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_arcs.py tests/unit/physics/layer2/test_corner_descriptors.py -v
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- ...\python.exe
collecting ... collected 16 items

tests/unit/physics/layer2/test_arcs.py::test_contiguous_brake_runs_become_arcs PASSED [  6%]
tests/unit/physics/layer2/test_arcs.py::test_frontier_filter_drops_gentle_arcs PASSED [ 12%]
tests/unit/physics/layer2/test_arcs.py::test_short_runs_are_ignored PASSED [ 18%]
tests/unit/physics/layer2/test_arcs.py::TestIdentifyStraightArcs::test_contiguous_run_across_all_three_straight_regimes_becomes_one_arc PASSED [ 25%]
tests/unit/physics/layer2/test_arcs.py::TestIdentifyStraightArcs::test_corner_sample_breaks_a_run_into_two_arcs PASSED [ 31%]
tests/unit/physics/layer2/test_arcs.py::TestIdentifyStraightArcs::test_min_len_filtering_drops_short_runs PASSED [ 37%]
tests/unit/physics/layer2/test_arcs.py::TestIdentifyStraightArcs::test_field_computations PASSED [ 43%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestBinRowToDescriptor::test_hand_computed_values PASSED [ 50%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestBinRowToDescriptor::test_hand_computed_values_second_case PASSED [ 56%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestBinRowToDescriptor::test_zero_mu_raises_value_error PASSED [ 62%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestBinRowToDescriptor::test_negative_mu_raises_value_error PASSED [ 68%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestBinRowToDescriptor::test_nan_mu_raises_value_error PASSED [ 75%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestBinRowToDescriptor::test_nan_v_mean_raises_value_error PASSED [ 81%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestDescriptorsFromFrame::test_all_good_frame_returns_full_n_rows_in_order PASSED [ 87%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestDescriptorsFromFrame::test_drops_zero_and_negative_and_nan_rows PASSED [ 88%]
tests/unit/physics/layer2/test_corner_descriptors.py::TestDescriptorsFromFrame::test_empty_frame_returns_empty_array PASSED [100%]

============================= 16 passed in 0.71s ==============================
```

**Result:** `pass` — count-before-after: 3 pre-existing `test_arcs.py` tests before this gate
started (verified by running the file before editing, at the m1 step); 3 pre-existing +
4 new = 7 in `test_arcs.py` after, plus 9 new in `test_corner_descriptors.py` = 16 total.
No pre-existing case removed or weakened.

Additional evidence — `simplification_limits` on touched files (project norm,
`docs/agents/CREW_CONTEXT.md`):
```bash
py -m src.utils.simplification_limits --paths src/physics/layer2/arcs.py src/physics/layer2/corner_descriptors.py tests/unit/physics/layer2/test_arcs.py tests/unit/physics/layer2/test_corner_descriptors.py
```
```
PASS (4 files checked)
```

## TDD evidence, if required
Not required (test-after mode per handoff). Tests were written alongside each implementation
step, not after a separate pass, and were green on first correct implementation attempt (one
self-caught arithmetic slip in a hand-computed test literal, fixed before reporting — see below).

## Docs/contracts touched
- none — both new pieces are additive pure-function code with docstrings; no committed
  contract/schema doc governs this module.

## Assumptions
- `_STRAIGHT_REGIMES` is derived as `_VALID_REGIMES - {"corner"}` (import + set-subtract) rather
  than a second literal `{"straight_throttle","straight_coast","straight_brake"}` — the handoff
  offered either as acceptable; deriving it removes any chance of the two sets silently
  drifting apart.
- `StraightArc.length_m` sums Euclidean distance between consecutive samples' full 3D
  `position` vectors (`KinematicSample.position` is shape `(3,)` per
  `physics_data_models.py`), not a 2D px/py-only distance — chosen because it is the real
  attribute available on the actual `KinematicSample` samples this will run on in production
  (the handoff's own unit tests use a minimal fake carrying only the fields read, so this
  choice was made from reading `physics_data_models.KinematicSample` directly, not guessed).
- `bin_row_to_descriptor`'s NaN/non-positive guard raises `ValueError` (the handoff's other
  offered option, returning `(nan, nan)`, was not used) — chosen to match the project's
  "no hidden fallback; fail visibly" doctrine and the CREW_CONTEXT rule that non-finite/
  impossible physics states are defects, not silently-propagated values.

## Stop conditions hit
None — no contradiction blocked progress; the one factual discrepancy found (handoff citing
`session_braking.py` instead of the real caller `braking_report.py`) did not change what the
frozen-signature requirement actually meant, so it was resolved by direct verification rather
than treated as a stop condition.

## Out-of-scope observations
None beyond the Workflow Feedback item below.

## Workflow Feedback
- **Handoff gaps:** the "Constraints" section says "verify [`identify_braking_arcs`'s frozen
  signature] by reading `src/physics/layer2/session_braking.py`'s call site" — `grep`-ing the
  whole repo shows `session_braking.py` does NOT call `identify_braking_arcs` at all; the real
  (and only) caller is `src/physics/layer2/braking_report.py::plot_arcs` (`identify_braking_arcs(samples)`,
  positional, using both defaults). This did not block the gate — the actual signature was
  trivially confirmed by reading `arcs.py` itself plus the real caller — but a reviewer/future
  reader chasing the handoff's specific file citation would waste time on a dead end.
- **Context rediscovered:** `KinematicSample.position`'s real shape/semantics (a 3-vector,
  `physics_data_models.py`) had to be looked up to decide how `StraightArc.length_m` should
  accumulate distance, since neither the handoff nor the map anchors mention the sample's
  position field shape at all (only `arcs.py`'s and `grip_bin_obs.py`'s existing fields were
  anchored). Not a blocker, just extra source-reading before the close criterion could be
  implemented precisely.
- **Instructions improvised around:** none — the handoff's two explicitly-offered choice points
  (regimes-set import-vs-literal; ValueError-vs-NaN guard) both had a "your choice, document it"
  clause, so picking and documenting was in-scope, not an improvisation.
- **What would have made this easier:** correcting the `session_braking.py` -> `braking_report.py`
  citation in this handoff template/anchor set, and adding one line noting
  `KinematicSample.position` is a 3-vector (since `StraightArc.length_m`'s exact accumulation
  method depends on knowing that shape).

## Return status
`complete`
