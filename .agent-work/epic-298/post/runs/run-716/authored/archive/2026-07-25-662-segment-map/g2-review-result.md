# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
G2 — Canonical gate + base tiling (issue #662, epic #659)

## Result
`APPROVE`

## Handoff compliance
Full compliance. `tile_reference_lap` (`src/physics/segment_map/derivation/tiling.py`) types a G1
`ReferenceLap` into a complete contiguous partition exactly per the task statement: corner =
`abs(curvature) > CORNER_CURVATURE_THRESHOLD`; braking zone = the field ENVELOPE (p10) onset upstream
of each corner, from `brake_active_frac`; straight = remainder. Both frozen thresholds are imported
from `frozen_constants.py`, never literals. Scope respected: only `tiling.py` and
`tests/unit/physics/segment_map/derivation/test_tiling.py` added; no existing `segment_map` runtime
file, `frozen_constants.py`, or `docs/architecture/*` touched.

## Scope drift
None. `git status --porcelain` shows only the two new files relevant to this gate (plus untracked
`.agent-work/` workflow scaffolding, not production code). Sliver-merging and sector-cut enforcement
correctly deferred to later gates per the handoff's Specific Exclusions — not attempted here.

## Evidence verdict
All three Required Evidence commands reproduced independently on the pinned interpreter
(`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`):

1. `pytest tests/unit/physics/segment_map/derivation/test_tiling.py -q` → **9 passed in 0.37s**
   (matches implementer's claim; includes both LOAD-BEARING tests, `TestCompleteness` and
   `TestEnvelopeNotMean`).
2. `py -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/tiling.py` →
   **PASS (1 files checked)** (matches).
3. `grep -nE "0\.005|0\.10|0\.1[^0-9]" src/physics/segment_map/derivation/tiling.py` → **zero
   matches** (exit code 1; matches the implementer's claim of zero literal-threshold occurrences,
   not even in a comment).

Supplementary (beyond the handoff's named Required Evidence, following the region-verification
project rule): ran the full physics region suite, `py -m pytest tests/unit/physics/ -q`, as a
regression sweep. Independently confirmed via
`grep -rn "segment_map.derivation.tiling" src/ tests/` that `tiling.py` is imported **only** by its
own test file — it is not yet wired into any production consumer (g3 wires it in) — so this gate
structurally cannot regress any other physics test. Result (actually completed, waited out
in-foreground): **2232 passed, 54 skipped, 0 failed, 11 warnings in 894.44s (0:14:54)** — no
regression. The 11 warnings are pre-existing numpy `RuntimeWarning`s in unrelated
`test_calibration_robustness.py` degenerate-input tests, not new.

Evidence genuinely demonstrates the claimed behavior, not just a passing test count — see the #1
check under Map impact verdict / Blockers below for the load-bearing detail.

## Code/doc quality
Minimal, maintainable, matches surrounding conventions. `Tiling` is a small frozen dataclass with
`__post_init__` validation in the same style as `ReferenceLap`/`SegmentMap`. Exceptions name field,
expectation, and actual value per `CREW_CONTEXT.md`'s Interface rule. Docstrings explain the *why*
(envelope vs. mean/median semantics) precisely because that is the genuinely subtle part of this
gate — not comment-as-deodorant over messy code (see Fowler pass below).

**Fowler refactoring pass** (`.agent-work/662-segment-map/g2-review/fowler_pass.json`, verified by
`scripts/verify_fowler_pass.py` → `fowler pass ok ... smells=12, flagged=[],
overridden=[primitive-obsession]`):
- 11/12 baseline smells **absent** (long-method, large-class, duplicated-code, feature-envy,
  data-clumps, long-parameter-list, shotgun-surgery, divergent-change, message-chains,
  speculative-generality, comments-as-deodorant).
- 1 **overridden**: `seg_type_code` stored as raw `int8` rather than a `SegType`-typed array is
  primitive obsession on its face, but subordinated to `runtime.py:26`'s own documented standard
  ("Segment kind, int-coded because both hot callers branch on it inside vectorized code") —
  `tiling.py` is the direct upstream producer of that same convention `SegmentMap` already
  established; a richer wrapper here would only add a conversion step at the seam, not fix a real
  problem.

## Map impact verdict
- **Evidence supports claimed change:** Yes. `claim:tiling-complete` is backed by
  `TestCompleteness`'s independent per-grid-station coverage recomputation (not four scalars); the
  p10-envelope-earlier-than-mean claim is backed by `TestEnvelopeNotMean`'s bimodal fixture with a
  fixture-sanity guard against a vacuous pass.
- **Constraints not violated:** Yes. `decision:corner-gate-is-curvature` and
  `decision:braking-envelope-p10-not-mean` are implemented exactly as `frozen_constants.py`'s own
  docstrings state them verbatim (cross-checked directly: "the corner/straight gate in this epic is
  CURVATURE, not lateral-g"; `BRAKING_ONSET_QUANTILE` "Robust low quantile, never mean").
- **Notes match the diff:** Yes. Structural anchors, the new `segment_map_tiling` capability, and
  the "consumed but not edited" list (`frozen_constants.py`, `runtime.py`, `reference_lap.py`) all
  match `git status` exactly.
- **Decision candidates surfaced:** Yes, both within the implementer's granted latitude (not
  silently made): the boundary-midpoint-at-transition convention, and the non-wrapping
  corner/braking-zone grouping — both explicitly flagged forward for g3/g6.
- **Durable context routed:** Yes — flagged as forward context for g3's handoff (state the
  boundary-midpoint convention explicitly), not dropped.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation. This gate composes
cleanly on top of G1's `ReferenceLap` and the epic's frozen-constants module; it introduces one new,
currently-unwired capability (`tile_reference_lap`) and touches nothing else.

## THE #1 check — braking onset is the ENVELOPE (p10), not mean/median
**CONFIRMED**, independently reproduced.

- Code (`_grid_type_array`, `tiling.py`): the onset search is a direct threshold-crossing —
  `for j in range(prev_corner_end, c_start): if ref.brake_active_frac[j] >= BRAKING_ONSET_QUANTILE:
  onset_idx = j; break` — first (most-upstream) qualifying index wins. `grep -n
  "np.mean|np.median|\.mean\(|\.median\("  tiling.py` → **zero matches**; no central-tendency
  statistic appears anywhere in the file.
- Test (`TestEnvelopeNotMean.test_p10_onset_is_earlier_than_mean_crossing`): fixture is bimodal —
  `brake_active_frac` = 0.15 (above p10=0.10, below 0.5) from index 60, rising to 0.6 (above 0.5)
  only from index 75. A fixture-sanity assertion first proves
  `expected_p10_onset_boundary < would_be_mean_onset_boundary` (rules out a vacuous pass on a
  degenerate fixture). The load-bearing assertions, quoted verbatim:

  ```python
  assert produced_onset == pytest.approx(expected_p10_onset_boundary), (
      f"braking-zone onset must equal the p10 envelope crossing "
      f"({expected_p10_onset_boundary}), got {produced_onset}"
  )
  assert produced_onset < would_be_mean_onset_boundary, (
      "the p10 envelope onset must be STRICTLY upstream (earlier, "
      "smaller distance) of the 0.5/mean crossing -- a mean onset "
      "would sit inside the real braking zone and miss the early "
      "brakers, which is exactly the failure the frozen quantile forbids"
  )
  ```

  Both assertions passed on independent reproduction (9/9 green). This genuinely proves
  `onset == p10-crossing` **and** `onset` is strictly upstream of the 0.5-crossing — not a
  coincidental pass on a fixture where the two thresholds happen to land on the same index.

## Other FOCUS points (all confirmed, see full detail in `g2-review/review.json`)
- **Thresholds imported, no literals:** confirmed by grep (zero matches) and by
  `TestThresholdIsImportedNotHardcoded`'s monkeypatch proof (a real dependency, not a shadow
  literal).
- **Complete partition:** `TestCompleteness` recomputes coverage per grid station via
  `np.searchsorted` against an independently-derived expected-type array — genuine coverage
  recomputation, confirmed.
- **Corner gate is curvature:** confirmed — `abs(ref.curvature) > CORNER_CURVATURE_THRESHOLD`, no
  lateral-g or speed term anywhere in the file; matches `frozen_constants.py`'s own
  `decision:corner-gate-is-curvature` framing verbatim.
- **`SegType` reused:** confirmed — imported from `runtime.py`, never redefined locally.
- **Wrap-handling:** ACCEPTABLE for Build 1, not a blocker. Explicitly within the handoff's granted
  latitude, does not corrupt completeness (`TestWrapHandlingSimplification` reproduced, passing —
  the straddling-corner case still yields a valid strict partition, just as two `CORNER` segments),
  and is properly surfaced as a decision candidate for g3/g6 rather than silently made or dropped.

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback
- **Handoff gaps:** none — the handoff pre-specified the exact grep pattern and both load-bearing
  test names, which made independent reproduction fast and unambiguous.
- **Context rediscovered:** none of real substance — `frozen_constants.py`'s own docstrings
  (`decision:corner-gate-is-curvature`, `BRAKING_ONSET_QUANTILE`'s "never mean" framing) matched the
  handoff's description verbatim on first read, giving a second independent confirmation source
  beyond the test file itself; worth citing directly in future handoffs for this epic since it is
  such a clean cross-check.
- **Instructions improvised around:** the reviewer skill's engine doctrine references a
  `refresh-request` / trip mechanism for mid-review course-correction; not needed here (no trip
  fired), so not exercised.
- **What would have made this easier:** none — this was an unusually precise handoff (exact grep
  pattern, named load-bearing tests, an explicit acceptable-simplification allowance for wrap
  handling) that left little ambiguity.

## Return status
`complete`
