# tests.test_diagnose
tests/test_diagnose.py, 281 lines, 27 holes

Tests for the constellation-diagnose skill's rail (scripts/verify_diagnosis.py).

The rail is reproduce-before-you-claim. These tests exercise the three cases the
DESIGN_SPEC (Section B, "Testing pathways") names, plus the exception path and
the structural refusals:

  * SeededRuntimeBugTests -- one loop over a seeded runtime bug: the oracle (a
                             test) reproduces it, the finding records the observed
                             mechanism, and the rail confirms it.
  * SeededDisconnectTests -- the SAME loop over a seeded intent/execution
                             disconnect, reached via the map-as-oracle probe.
  * RailBlocksTests       -- a 'confirmed' claim with no falsifier / no observed
                             result is BLOCKED; the reviewer-cosigned exception
                             passes; a self-asserted exception does NOT.
  * StructureTests        -- the shape + route-out-don't-fix refusals + CLI codes.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
_STATE = {'writes': 0}
MAP_CLAIM_PURE = True
```

- [load](load.md) function: HOLE: no docstring
- [seeded_add](seeded_add.md) function: Seeded bug: multiplies instead of adds.
- [reproduce_runtime_bug](reproduce_runtime_bug.md) function: The oracle: a test that fails on the seeded bug. Returns the observed
- [seeded_touch](seeded_touch.md) function: Execution drifted from the map: the map says pure, this mutates _STATE.
- [probe_disconnect](probe_disconnect.md) function: The oracle: probe the map's purity claim against actual behavior. Returns
- [SeededRuntimeBugTests](SeededRuntimeBugTests.md) class: HOLE: no docstring
  - [SeededRuntimeBugTests.setUp](SeededRuntimeBugTests.setUp.md) method: HOLE: no docstring
  - [SeededRuntimeBugTests.test_loop_reproduces_and_rail_confirms](SeededRuntimeBugTests.test_loop_reproduces_and_rail_confirms.md) method: HOLE: no docstring
- [SeededDisconnectTests](SeededDisconnectTests.md) class: HOLE: no docstring
  - [SeededDisconnectTests.setUp](SeededDisconnectTests.setUp.md) method: HOLE: no docstring
  - [SeededDisconnectTests.test_same_loop_reaches_disconnect_via_map_oracle](SeededDisconnectTests.test_same_loop_reaches_disconnect_via_map_oracle.md) method: HOLE: no docstring
  - [SeededDisconnectTests.test_disconnect_without_caveat_refused](SeededDisconnectTests.test_disconnect_without_caveat_refused.md) method: HOLE: no docstring
- [RailBlocksTests](RailBlocksTests.md) class: The reproduce-before-you-claim rail and its cosigned exception.
  - [RailBlocksTests.setUp](RailBlocksTests.setUp.md) method: HOLE: no docstring
  - [RailBlocksTests._confirmed](RailBlocksTests._confirmed.md) method: HOLE: no docstring
  - [RailBlocksTests.test_confirmed_without_falsifier_blocked](RailBlocksTests.test_confirmed_without_falsifier_blocked.md) method: HOLE: no docstring
  - [RailBlocksTests.test_confirmed_without_observed_result_blocked](RailBlocksTests.test_confirmed_without_observed_result_blocked.md) method: HOLE: no docstring
  - [RailBlocksTests.test_confirmed_with_empty_evidence_blocked](RailBlocksTests.test_confirmed_with_empty_evidence_blocked.md) method: HOLE: no docstring
  - [RailBlocksTests.test_reviewer_cosigned_exception_passes](RailBlocksTests.test_reviewer_cosigned_exception_passes.md) method: HOLE: no docstring
  - [RailBlocksTests.test_self_asserted_exception_blocked](RailBlocksTests.test_self_asserted_exception_blocked.md) method: HOLE: no docstring
  - [RailBlocksTests.test_suspected_needs_no_reproduce_evidence](RailBlocksTests.test_suspected_needs_no_reproduce_evidence.md) method: HOLE: no docstring
- [StructureTests](StructureTests.md) class: HOLE: no docstring
  - [StructureTests.setUp](StructureTests.setUp.md) method: HOLE: no docstring
  - [StructureTests.test_empty_symptom_refused](StructureTests.test_empty_symptom_refused.md) method: HOLE: no docstring
  - [StructureTests.test_bad_altitude_refused](StructureTests.test_bad_altitude_refused.md) method: HOLE: no docstring
  - [StructureTests.test_empty_oracle_refused](StructureTests.test_empty_oracle_refused.md) method: HOLE: no docstring
  - [StructureTests.test_bad_status_refused](StructureTests.test_bad_status_refused.md) method: HOLE: no docstring
  - [StructureTests.test_confirmed_fault_must_route_out_not_note](StructureTests.test_confirmed_fault_must_route_out_not_note.md) method: HOLE: no docstring
  - [StructureTests.test_explained_by_design_is_a_note](StructureTests.test_explained_by_design_is_a_note.md) method: HOLE: no docstring
  - [StructureTests.test_explained_by_design_cannot_route_to_triage](StructureTests.test_explained_by_design_cannot_route_to_triage.md) method: HOLE: no docstring
  - [StructureTests.test_cli_refuses_unreproduced_nonzero](StructureTests.test_cli_refuses_unreproduced_nonzero.md) method: HOLE: no docstring
  - [StructureTests.test_cli_accepts_reproduced_zero](StructureTests.test_cli_accepts_reproduced_zero.md) method: HOLE: no docstring
