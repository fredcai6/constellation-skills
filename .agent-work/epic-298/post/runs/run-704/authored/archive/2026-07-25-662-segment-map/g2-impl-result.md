# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
G2 — Canonical gate + base tiling (issue #662, epic #659).

## Completed slice
Turned a G1 `ReferenceLap` into a complete contiguous tiling of the lap into typed segments
(`tile_reference_lap` in `src/physics/segment_map/derivation/tiling.py`): the curvature-based
corner gate, the ENVELOPE (p10, never mean/median) braking-zone onset upstream of each corner,
straight-as-remainder, and grouping into a strict `boundaries_m`/`seg_type_code` partition.

## Scope
**Files changed:**
- `src/physics/segment_map/derivation/tiling.py` (new)
- `tests/unit/physics/segment_map/derivation/test_tiling.py` (new)
- `.agent-work/662-segment-map/crew-handoffs/g2-impl-plan.json` (new — this run's engine-driven plan)

**Specific exclusions touched:** no. Did not do sector nesting (g3), corner descriptors/severity
(g4), or assembly/store (g5). Did not edit `docs/architecture/*`, any existing
`src/physics/segment_map/*.py` runtime file, or `frozen_constants.py`. Did not retune
`CORNER_CURVATURE_THRESHOLD`.

## Map Impact
- **Structural anchors touched:** NEW `src/physics/segment_map/derivation/tiling.py`
  (`Tiling`, `tile_reference_lap`, `_grid_type_array`, `_group_into_segments`). Consumed but not
  edited: `frozen_constants.py` (`CORNER_CURVATURE_THRESHOLD`, `BRAKING_ONSET_QUANTILE`),
  `runtime.py` (`SegType`), `reference_lap.py` (`ReferenceLap`).
- **Capabilities added/changed/affected:** `segment_map_tiling` (NEW) — a `ReferenceLap` is now
  tileable into a complete straight/braking-zone/corner partition.
- **Constraints/assumptions touched:** `decision:corner-gate-is-curvature` and
  `decision:braking-envelope-p10-not-mean` both implemented exactly as specified (see Evidence).
- **Decision candidates / resolved decisions:**
  - New candidate (not yet graded, surfacing for Cartographer/Commander/g3): **boundary placement
    at the type-change midpoint distance** (`0.5 * (distance_m[i-1] + distance_m[i])`) is my own
    design choice — the handoff didn't pin an exact boundary-placement rule, only that boundaries
    must be strictly increasing and span `[0, lap_length_m]`. g3 (sector nesting) needs to know
    this convention since it will insert FIA sector cuts as MANDATORY split points into this same
    `boundaries_m` array.
  - New candidate: **non-wrapping corner/braking-zone grouping** (see "Wrap-handling choice"
    below) — a straddling corner/braking region comes out as two same-type segments rather than
    one merged wrapped segment. This is a within-latitude implementation choice per the handoff's
    explicit allowance, not a settled epic decision; flagging for g3+ in case sector nesting near
    the start/finish line needs to reason about it.
- **Claims/evidence produced:** `claim:tiling-complete` — proven by the completeness test's
  independent grid-coverage recomputation (not just the four scalar invariants). The p10-envelope-
  earlier-than-mean-crossing claim — proven by `TestEnvelopeNotMean` with a fixture where the two
  crossings are demonstrably different indices.
- **Trust limitations / drift found:** none found in the reused seams (`ReferenceLap`, `SegType`,
  `frozen_constants` all matched the handoff's description exactly, no rediscovery needed).
- **Triage candidates:** the boundary-midpoint convention (above) should be stated explicitly in
  g3's handoff so sector-cut insertion composes with it predictably.

## Test mode
**Required:** TDD-lean (per handoff).
**Satisfied:** yes. `test_tiling.py` was written and run BEFORE `tiling.py` existed (RED: 9 failed,
`ModuleNotFoundError`), then the implementation was added and the same 9 tests went green on the
first attempt (no rework cycle needed).

## Evidence

### Required Evidence 1 — pytest (LOAD-BEARING: completeness + envelope-not-mean)

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_tiling.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-662
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 9 items

tests\unit\physics\segment_map\derivation\test_tiling.py .........       [100%]

============================== 9 passed in 0.36s ==============================
```
**Result:** pass. 9/9, including `TestCompleteness::test_partition_invariants_and_coverage` and
`TestEnvelopeNotMean::test_p10_onset_is_earlier_than_mean_crossing` (both LOAD-BEARING).

### Required Evidence 2 — simplification_limits

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/tiling.py
```
```
PASS (1 files checked)
```
**Result:** pass.

### Required Evidence 3 — no-literal-threshold grep

```bash
cd C:/Programs/f1brainz-wt/epic659-662
grep -nE "0\.005|0\.10|0\.1[^0-9]" src/physics/segment_map/derivation/tiling.py
```
```
(no output — zero matches)
```
**Result:** zero matches at all, not even in a comment — stronger than "only imports/comments";
the file contains no `0.005`/`0.10`/bare-`0.1` literal anywhere. The only numeric-looking neighbor
is the unrelated `0.5 * (distance_m[i - 1] + distance_m[i])` midpoint-boundary formula in
`_group_into_segments`, which the pattern correctly does not match (`0.5` ≠ `0.1x`/`0.005`).

## TDD evidence

- Failing test observed: ran `test_tiling.py` before `tiling.py` existed — all 9 tests failed with
  `ModuleNotFoundError: No module named 'src.physics.segment_map.derivation.tiling'`.
- Passing test observed: same 9 tests passed on the FIRST attempt after writing `tiling.py` (no
  rework cycle needed).
- Refactor while green: no refactor pass was needed; the implementation was accepted as
  first-written.

## Imported constants (confirmatory, per Required Evidence)

`tiling.py` imports exactly two names from `src.physics.layer2.frozen_constants`:
`CORNER_CURVATURE_THRESHOLD` (0.005 1/m, re-exported from `PhysicsEstimatorConfig`) and
`BRAKING_ONSET_QUANTILE` (0.10, p10). `SegType` is imported from
`src.physics.segment_map.runtime` and never redefined. Both frozen constants are referenced by
their bare imported names at every call site (`_grid_type_array`'s `abs(ref.curvature) >
CORNER_CURVATURE_THRESHOLD` and `ref.brake_active_frac[j] >= BRAKING_ONSET_QUANTILE`) — no literal
threshold appears anywhere in the file (see grep above). `TestThresholdIsImportedNotHardcoded`
additionally proves this is a REAL dependency (not a shadow literal elsewhere): monkeypatching the
module-bound `tiling_mod.CORNER_CURVATURE_THRESHOLD` to `0.5` changes a previously-CORNER
classification (curvature `0.02`) to STRAIGHT.

## ReferenceLap fields consumed

`distance_m` (arc-length station, m, strictly increasing, `[0] == 0.0`), `curvature` (signed, 1/m —
gated on `abs()`), `brake_active_frac` (pooled fraction in `[0, 1]` per grid point — thresholded
directly, never smoothed/re-derived), `lap_length_m` (float, closes the last boundary). `v_ref`,
`px`, `py`, `n_laps_pooled` are NOT consumed by this gate (confirmed by reading `reference_lap.py`
before writing any code) — the tiling algorithm needs only geometry (curvature) and brake state,
not speed or raw XY.

## Wrap-handling choice

Corner-run grouping and each corner's braking-zone search window are computed on the **linear
(non-wrapping) grid index space** (`0` to `n-1`), never wrapping across the array boundary:

- Corner runs are contiguous-index runs of `is_corner`, found by a single linear scan of the index
  array — a corner region occupying indices `[0, k)` and one occupying `[n-m, n)` are two SEPARATE
  runs, never merged into one "wrapped" corner even if they are physically the same corner
  straddling the start/finish line.
- Each corner's braking-zone search window is bounded below by the end of the **previous** corner
  run in index order (or index `0` for the very first corner) — the first corner's window never
  wraps around to search the tail of the array for a "previous" corner.

Consequence: a corner/braking region that physically straddles the start/finish line comes out as
two same-type segments (one ending at `lap_length_m`, one starting at `0.0`) rather than one merged
wrapped segment. This is explicitly within my latitude per the handoff ("If wrap handling is
non-trivial, keep it simple and note the choice") — I judged full wraparound merging (rotating the
grid to find a non-straddling start point, or a doubly-linked circular scan) to add real complexity
for a case that occurs only when a real track's start/finish line happens to sit inside a corner or
its braking zone, which is uncommon and not required by any Close Criterion. Proven by
`TestWrapHandlingSimplification`.

## Assumptions

- **Boundary placement at type-change midpoint:** the exact arc-length position of a boundary
  between two differently-typed adjacent grid stations is placed at their midpoint distance
  (`0.5 * (distance_m[i-1] + distance_m[i])`) — the true transition is only known to lie somewhere
  between the two sampled stations, and the midpoint is the most neutral estimate (doesn't bias to
  either neighbor). The handoff's Close Criteria specify WHICH grid points are which type, but not
  an exact sub-grid boundary placement rule; this was a judgment call within "you MAY decide the
  tiling result's dataclass shape... and grouping details."
- **Tiling result dataclass shape:** `Tiling(boundaries_m, seg_type_code)`, a minimal frozen
  dataclass carrying exactly the two fields the handoff requires "at minimum," with `__post_init__`
  validating shape consistency and strict monotonicity (mirroring `ReferenceLap`'s and
  `SegmentMap`'s own validation style per project convention). No extra fields added — sector/
  severity/identity fields are explicitly later-gate territory.
- **Sliver-merging deferred:** `MIN_SEGMENT_LENGTH_M` (the sliver-merge floor in
  `frozen_constants.py`) is NOT applied here — the handoff's Close Criteria for this gate never
  mention it, and the handoff's own Map Anchors note "sliver-merge exempts sector cuts" as
  characteristic of a LATER gate (g3, which owns sector-cut insertion). A pathological input could
  in principle produce very thin flip-flopping segments; not exercised here since no Close
  Criterion asks for it, and it's explicitly the kind of thing g3/later gates handle.
- **"First reaches" reading of the p10 onset:** implemented as the most-upstream (smallest index)
  grid point in the search window where `brake_active_frac >= BRAKING_ONSET_QUANTILE`, i.e. a
  single forward linear scan taking the FIRST qualifying point — not "the point after which it
  stays above threshold continuously to the corner." If the fraction dipped below 0.10 and rose
  again before the corner, this reading would still report the earliest crossing, matching the
  handoff's literal wording ("FIRST reaches"). Not exercised by a dedicated test (the handoff's
  fixtures are monotonic/step-wise, not oscillating) — flagging as a reading choice, not a proven
  edge case.

## Stop conditions hit
None. The ENVELOPE onset was computable directly from `ref.brake_active_frac` (present, as
documented); no frozen threshold looked wrong (both were used as-is, unmodified); completeness was
guaranteed by construction (the grouping algorithm always closes with `lap_length_m` and starts
with `0.0`, proven by the completeness test).

## Out-of-scope observations
None found as defects. See "Decision candidates" above for the boundary-midpoint convention and the
non-wrapping simplification, both surfaced as context g3 will need, not as bugs.

## Workflow Feedback

- **Handoff gaps:** the handoff specifies exactly which grid points are which SegType but not an
  exact sub-grid boundary-placement rule (I chose the midpoint between adjacent differently-typed
  stations) — this is explicitly left to my latitude ("you MAY decide... grouping details"), so not
  really a gap, but worth naming in g3's handoff since sector-cut insertion will compose with
  whatever convention g2 picked.
- **Context rediscovered:** none — `ReferenceLap`'s field names, `SegType`'s values, and both frozen
  constants' names/values all matched the handoff's description exactly on first read; no seam
  surprises like G1's abbreviation-vs-number keying discovery.
- **Instructions improvised around:** none — the handoff's "you MAY decide the tiling result's
  dataclass shape, wrap handling, and grouping details (note them)" latitude covered everything I
  needed to decide, and I noted each choice above.
- **What would have made this easier:** none — this handoff was unusually precise (it even
  pre-specified the exact required grep pattern and both load-bearing test names), which made the
  TDD-lean write-tests-first step fast and unambiguous. The only thing I'd flag for the NEXT
  handoff (g3) is to explicitly state the boundary-midpoint convention this gate settled on, since
  g3 needs to insert sector cuts into the same `boundaries_m` array.

## Return status
`complete`
