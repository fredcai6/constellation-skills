# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4 (issue #662)` — Corner descriptors + turn direction + severity membership; the HIGHEST-RISK gate (#639 a_lateral unit boundary).

## Completed slice
Full G4 scope delivered in one module: per-corner `(radius_m, lateral_g)` descriptor computed at the corner apex from the reference lap's own geometry+speed (the #639 unit boundary), signed `turn_direction`, soft `severity_membership` against a re-fit k=4 mixture pooled across all of 2023, plus the `fit_era_severity_mixture` entry point that produces the `MixtureFitAdapter`/`VocabularyRef` pair for g5 to persist.

## Scope
**Files changed:**
- `src/physics/segment_map/derivation/corner_attributes.py` (new)
- `tests/unit/physics/segment_map/derivation/test_corner_attributes.py` (new)

**Specific exclusions touched:** no — did not assemble `SegmentMap`, did not write the store, did not populate sub-phase marks, did not edit `docs/architecture/*` or any existing `segment_map` runtime/`layer2`/`frozen_constants.py` file, did not join official corner-number markers.

## Behavior changed
Yes — new capability. Two new public value objects/functions surface: `compute_corner_descriptor` / `compute_turn_direction` / `compute_severity_membership` (pure, deterministic, no I/O) and `fit_era_severity_mixture` (data-plumbing: reads `grip_bin_obs`, fits, mints a `VocabularyRef`). `derive_corner_attributes` is a convenience wrapper combining the first three for g5.

## Map Impact
- **Structural anchors touched:** `src/physics/segment_map/derivation/corner_attributes.py` (NEW module); reuses `src.physics.segment_classifier.SegmentClassifier.soft_class_membership`'s convention (radius=1/|kappa|, lateral_g=a_lateral/GRAVITY_MS2 at one call site) without importing it (the two call sites operate on different input shapes — `KinematicSample` vs `ReferenceLap` — so the convention is mirrored, not shared code); imports `src.physics.layer2.corner_descriptors.descriptors_from_frame`, `src.physics.layer2.property_mixture.fit_property_mixture`, `src.physics.segment_map.from_mixture.{MixtureFitAdapter, vocabulary_from_fit}`, `src.physics.layer2.grip_bin_obs.GripBinStore`, `src.physics.constants.GRAVITY_MS2`.
- **Capabilities added:** corner-attribute derivation (descriptor + direction + severity) for a segment-map weekend, ready for g5 assembly.
- **Constraints/assumptions touched:** `decision:a-lateral-g-boundary` (honored: exactly one call site, verified by a monkeypatch test — see Evidence); `decision:severity-refit-consume-k4` (honored: re-fit on pooled 2023, k_range=(2,4), Student-t/fresh-F12 explicitly deferred, stated in the module docstring); `decision:dormant-subphase` (honored: no sub-phase store touched).
- **Claims/evidence produced:** `claim:unit-boundary-fires-once` — proven by `test_monkeypatched_gravity_scales_lateral_g_by_exactly_one_over_g` (see Evidence). `claim:membership-invariants` — proven by `test_noncorner_zero_corner_sums_to_one_shape`.
- **Trust limitations / drift found:** `DEFAULT_GRIP_BIN_DB_PATH` is a hardcoded absolute path into the MAIN checkout (`C:/Programs/f1Brainz/data/damage_integrals.db`), following the exact precedent already set by `src/physics/weekend_state/layer2_evolution.py`'s `DB_PATH` and a dozen `scripts/*.py` files — `grip_bin_obs` is NOT present in this worktree's per-year DBs (`data/f1_data_2023.db` has no such table); it lives only in the separate `damage_integrals.db` store, which this worktree does not track. This is a repo-wide pattern, not new debt introduced here, but it is worth Cartographer noting if it hasn't already (cross-worktree data dependency).
- **Triage candidates:** none new. The g5 assembler will need to decide whether `fit_era_severity_mixture`'s default year/db_path are appropriate to call as-is or whether it wants to pass its own weekend's year explicitly (it always should — see Assumptions).

## Test mode
**Required:** `test-first (TDD-lean per the handoff)`
**Satisfied:** yes, with one honest caveat (see Workflow Feedback: "Instructions improvised around") — the three functional slices (unit-boundary, direction+membership, era-fit) were each observed RED against the not-yet-existing module/functions, but because the three groups of functions are tightly coupled in one small module, the GREEN implementation was written as one pass rather than three strictly separate coding passes. Each slice's own green-check command was still run and passed independently before advancing to the next (see the engine's own `why` trail in `g4-impl-plan.json`).

## Evidence

### Full test file (14/14 green, including the real-data smoke test — genuinely ran, not skipped)
```
$ C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_corner_attributes.py -v
collected 14 items

tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary::test_known_value_hand_computed PASSED [  7%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary::test_monkeypatched_gravity_scales_lateral_g_by_exactly_one_over_g PASSED [ 14%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary::test_gravity_ms2_is_imported_not_a_local_literal PASSED [ 21%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestDescriptorValidity::test_corner_rows_finite_and_radius_positive PASSED [ 28%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestDescriptorValidity::test_noncorner_rows_are_nan_sentinel PASSED [ 35%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestApexSelection::test_apex_is_max_abs_curvature_point_within_segment PASSED [ 42%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestDegenerateApexGuard::test_degenerate_curvature_apex_is_sentineled_not_fabricated PASSED [ 50%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestTurnDirection::test_signed_curvature_produces_expected_codes PASSED [ 57%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestTurnDirection::test_noncorner_rows_are_straight_code_zero PASSED [ 64%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestMembershipInvariants::test_noncorner_zero_corner_sums_to_one_shape PASSED [ 71%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestSectorSplitCorners::test_split_corner_pieces_get_independent_descriptors PASSED [ 78%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestEraFitFailClosed::test_raises_file_not_found_when_store_absent PASSED [ 85%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestEraFitFailClosed::test_raises_value_error_when_year_has_no_rows PASSED [ 92%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestRealDataSmoke::test_pooled_2023_fit_smoke PASSED [100%]

============================= 14 passed in 5.11s ==============================
```

### The two LOAD-BEARING tests, isolated
```
$ C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestMembershipInvariants -v
collected 4 items

tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary::test_known_value_hand_computed PASSED [ 25%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary::test_monkeypatched_gravity_scales_lateral_g_by_exactly_one_over_g PASSED [ 50%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestUnitBoundary::test_gravity_ms2_is_imported_not_a_local_literal PASSED [ 75%]
tests/unit/physics/segment_map/derivation/test_corner_attributes.py::TestMembershipInvariants::test_noncorner_zero_corner_sums_to_one_shape PASSED [100%]

============================== 4 passed in 0.70s ==============================
```

`test_monkeypatched_gravity_scales_lateral_g_by_exactly_one_over_g` is the direct proof the conversion fires EXACTLY ONCE: it computes `lateral_g` once with the real `GRAVITY_MS2`, monkeypatches the module-bound `GRAVITY_MS2` to `2x`, recomputes, and asserts the new value equals exactly `old / 2`. A double-conversion would produce `old / 4`; a missing conversion would leave it unchanged at `old`. Both alternates are ruled out by the single assertion.

### simplification_limits (verification command #2 from the handoff)
```
$ C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/corner_attributes.py
PASS (1 files checked)
```

### No-literal-9.81 grep + GRAVITY_MS2 import confirmation
```
$ grep -n "GRAVITY_MS2" src/physics/segment_map/derivation/corner_attributes.py
89:from src.physics.constants import GRAVITY_MS2
185:        lateral_g = a_lateral_ms2 / GRAVITY_MS2
(+ 4 docstring mentions of the name, not the literal)

$ grep -n "9\.81" src/physics/segment_map/derivation/corner_attributes.py
(no output; exit code 1 -- no literal 9.81 anywhere in the file)
```

### Deliverable path check (git check-ignore exits 1 -- not ignored; both untracked/new)
```
$ git check-ignore -v src/physics/segment_map/derivation/corner_attributes.py tests/unit/physics/segment_map/derivation/test_corner_attributes.py
(no output; exit code 1)

$ git status --short src/physics/segment_map/derivation/corner_attributes.py tests/unit/physics/segment_map/derivation/test_corner_attributes.py
?? src/physics/segment_map/derivation/corner_attributes.py
?? tests/unit/physics/segment_map/derivation/test_corner_attributes.py
```

**Result:** pass — all four required evidence commands green.

## TDD evidence, if required

- Failing test observed: slice 1 (`-k "UnitBoundary or DescriptorValidity"`) failed with `ModuleNotFoundError: No module named 'src.physics.segment_map.derivation.corner_attributes'` before the module existed (5 failed, 9 deselected). Slices 2/3 were driven through the same module once it existed (see Workflow Feedback for the honest caveat on strict per-slice red/green separation).
- Passing test observed: full file 14/14 green (above), and each slice's own scoped subset was independently green before its engine `advance` (`-k 'UnitBoundary or DescriptorValidity'` for m1; `-k 'not RealDataSmoke'` for m2; full file for m3).
- Refactor while green: no separate refactor pass was needed — one iteration fixed two initial test-authoring bugs (a docstring containing the literal "9.81" it was itself asserting against; a synthetic-tiling helper that merged two same-type CORNER ranges instead of forcing the sector-split shape) before the whole suite went green.

## Docs/contracts touched
- none (module docstring is the only "documentation," per the Allowed Scope — no `docs/architecture/*` edits, per the Specific Exclusions).

## Assumptions
- **Apex choice:** the corner's representative point is the grid index of MAX `abs(curvature)` within the segment's own grid-point span (found via `searchsorted` against `tiling.boundaries_m`, mirroring `SegmentMap.segment_of`'s own convention) — the tightest point, the physical corner descriptor, per the handoff's explicit instruction.
- **Mixture pool scope:** `fit_era_severity_mixture` pools `GripBinStore(db_path).load(year=year)` with NO further `session_type`/`fit_status` filter (matching `scripts/f12_held_out_stability.py`'s own unfiltered pooling — `descriptors_from_frame` already drops NaN/non-positive rows), plus the `year=2023` filter this handoff explicitly requires ("all 2023", not every year the store happens to carry, which is currently 2023+2024). This is a deliberate divergence from F12's own script (which pools every year in the table) — stated explicitly in the module docstring and here.
- **Turn-direction convention:** `LEFT = +1` for positive curvature, `RIGHT = -1` for negative, `STRAIGHT = 0` for non-corner (and the degenerate-apex guard branch). Positive curvature follows directly from `build_ribbon`'s own sign convention (`kappa = dphi/ds`, a positive turn angle at a vertex = counter-clockwise in the pooled XY frame) — this LEFT/RIGHT naming is a within-authority choice (the handoff's Authority section permits it), not an independently re-verified physical left/right against real track orientation; it only needs internal consistency with the descriptor's own `radius_m = 1/abs(curvature)`, which it has.
- **`DEFAULT_GRIP_BIN_DB_PATH`** is a hardcoded absolute path into the MAIN checkout, following the exact precedent of `layer2_evolution.py`'s `DB_PATH` (data/*.db, including `damage_integrals.db`, is untracked in this worktree). `fit_era_severity_mixture` takes `db_path` as its first parameter so callers (tests, g5, scripts) can always override it; nothing calls the default silently in production code paths added here.
- **Degenerate-apex guard** (`abs(curvature) <= 1e-9`) is defensive and, given `CORNER_CURVATURE_THRESHOLD` (~0.005, far above 1e-9), unreachable through the real tiling pipeline — exercised directly against the pure functions in `TestDegenerateApexGuard`, not through a full pipeline run.

## Stop conditions hit
- none. The descriptor sits on the mixture's axis without a second conversion; the mixture fit succeeded on real pooled 2023 data (612,615 total rows in the store, 12 circuits present for 2023 in `grip_bin_obs`); no frozen value looked wrong.

## Out-of-scope observations
- `data/f1_data_2023.db` (the worktree's own per-year DB) has NO `grip_bin_obs` table — that table lives only in the separate, untracked `damage_integrals.db` store in the main checkout. This is pre-existing repo structure (not introduced by this gate), but future gates/g5 assembly should be aware the two "data" stores are not interchangeable.
- No new triage candidates beyond the above (already a known, repo-wide pattern).

## Workflow Feedback
- **Handoff gaps:** none load-bearing. One minor ambiguity: the handoff says "Use synthetic grip_bin_obs-shaped frames for the mixture fit in unit tests" but the membership-invariants test more naturally needed a small REAL `MixtureFitAdapter` fit on synthetic `(radius, lateral_g)` descriptors (not a synthetic `grip_bin_obs`-shaped DataFrame) to get a `posterior_membership`-capable object — I built a `_toy_mixture_adapter` helper that fits `fit_property_mixture` directly on synthetic descriptor arrays rather than routing through `descriptors_from_frame`/a fake DataFrame, which is the more direct and equally deterministic path. Worth a one-line handoff clarification next time ("synthetic descriptors, not necessarily a synthetic DataFrame, are fine for the membership tests").
- **Context rediscovered:** the fact that `grip_bin_obs` is NOT in this worktree's per-year DBs and instead lives in the main checkout's `damage_integrals.db` (found via grepping `scripts/populate_damage_integrals.py`'s `_DEF_STORE` and `layer2_evolution.py`'s `DB_PATH`) took real digging — the handoff's own text ("GripBinStore(db_path).load(...)") doesn't name where `db_path` should point in this worktree. A one-line pointer to `layer2_evolution.py`'s `DB_PATH` precedent in the handoff would have saved that search.
- **Instructions improvised around:** the skill's TDD doctrine (`references/global-crew.md`: "red→green→refactor when the handoff's test mode requires it") is written for a single-function slice. G4's three functional groups (descriptor, direction, membership, era-fit) are small and mutually referential enough that I wrote the whole module in one pass after observing slice-1's RED, then verified each subsequent slice's own scoped test subset independently before advancing that engine gate — rather than three fully separate red-then-write-code-then-green cycles. I judged this the closest-compliant reading (each gate's `c1`/`c2` postconditions were still genuinely satisfied in order, with real command evidence per slice) rather than artificially splitting one cohesive ~250-line module into three separately-committed partial states. Reporting it here per doctrine ("reporting misfit is compliance, not deviation").
- **What would have made this easier:** a one-line handoff pointer to the `layer2_evolution.py` `DB_PATH`/`pytest.mark.skipif` precedent for the grip_bin_obs store location, since g3's own handoff (sibling gate) already established a similar cross-worktree-DB precedent for `lap_times` but that one lives in the (in-worktree) per-year DB, not the (out-of-worktree) damage store — the two "which DB" answers are easy to conflate at gate start.

## Return status
`complete`
