# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
G3 — FIA sector-line derivation + nesting (issue #662, epic #659).

## Completed slice
Built the PURE sector-nesting heart (`nest_sectors`) that splits a G2 base tiling on the 2 interior FIA
sector lines — split-not-snap (a straddling segment splits into two same-class pieces at the exact line
distance), sliver-merge that EXEMPTS sector-cut boundaries from removal, fail-closed
`SectorLineUnavailableError` for unplaceable/non-finite/out-of-range lines, completeness preservation, and
per-segment int8 sector (1/2/3) assignment — plus the data-plumbing derivation (`derive_sector_lines`) that
reads per-lap FIA sector durations from the per-year DB and maps them to distance via each lap's own
telemetry time↔distance profile, pooled to a MEDIAN boundary.

## Scope
**Files changed:**
- `src/physics/segment_map/derivation/sector_nesting.py` (new)
- `tests/unit/physics/segment_map/derivation/test_sector_nesting.py` (new)
- `.agent-work/662-segment-map/crew-handoffs/g3-impl-plan.json` (new — this run's engine-driven plan)

**Specific exclusions touched:** no. Did not compute corner descriptors/severity (g4) or assemble/store
(g5). Did not edit `docs/architecture/*`, any existing `src/physics/segment_map/*.py` runtime file
(`tiling.py`, `runtime.py`, `store.py`, `identity.py`, `from_mixture.py`, `protocols.py`, `__init__.py`,
`reference_lap.py`), or `frozen_constants.py`. Did not call FastF1 directly. Did not wire OpenF1/live-timing
segment data or official corner-number markers.

## Map Impact
- **Structural anchors touched:** NEW `src/physics/segment_map/derivation/sector_nesting.py`
  (`SectorLineUnavailableError`, `nest_sectors`, `derive_sector_lines`, plus private helpers
  `_split_at_lines`/`_merge_slivers`/`_assign_sectors`/`_load_valid_sector_laps`/
  `_abbreviation_to_driver_num`/`_lap_sector_distances`). Consumed but not edited: `frozen_constants.py`
  (`MIN_SEGMENT_LENGTH_M`), `runtime.py` (`SegType`, referenced only in the test file), `src/data/database`
  (`DatabaseManager.get_sessions`/`get_lap_times`), `src/physics/session_fit.load_quali_session`,
  `src/preprocessing/trajectory/loaders.driver_streams`.
- **Capabilities added/changed/affected:** `segment_map_sector_nesting` (NEW) — a G2 base tiling can now be
  nested with the 2 interior FIA sector lines into a sector-tagged tiling, and a real weekend's sector
  lines can be derived end-to-end from the per-year DB + telemetry store.
- **Constraints/assumptions touched:** `constraint:db-only-analysis` honored — `derive_sector_lines` never
  imports `fastf1`; all telemetry comes through `session_fit.load_quali_session`'s store-first shim, and all
  sector durations come through `DatabaseManager`. `decision:sector-split-not-snap` implemented exactly as
  specified (split-not-snap, sliver-exempt-cuts, fail-closed) — see Evidence below.
- **Decision candidates / resolved decisions:**
  - `decision:sector-split-not-snap` — resolved/implemented, not just a candidate: straddling segments
    split at the exact line distance and duplicate their own type; sliver-merge never removes a sector-cut
    boundary; unplaceable/non-finite/out-of-range lines raise `SectorLineUnavailableError`.
  - New candidate (not yet graded): **sliver-merge direction preference** — when a sub-threshold segment
    has both a removable left and removable right boundary, this implementation prefers merging FORWARD
    (absorbing the sliver into the NEXT segment's type) before trying backward. The handoff didn't pin an
    exact direction/type-inheritance rule for sliver merging (only that sector cuts are exempt); this is a
    within-latitude implementation choice, flagged for g4/g5 in case corner-descriptor computation cares
    which side a merged segment's type came from.
  - New candidate: **DB-existence guard before instantiating `DatabaseManager`** — `derive_sector_lines`
    checks `os.path.exists(db_path)` and raises `SectorLineUnavailableError` before ever constructing
    `DatabaseManager`, specifically to avoid `DatabaseManager.__init__`'s own side effect of creating an
    empty DB file (via `_init_database`'s `mkdir`+`executescript`) at a missing path. This is a defensive
    choice on my part, not something the handoff asked for — flagging since it changes the fail-closed
    entry point slightly from "let DatabaseManager fail" to "check first."
- **Claims/evidence produced:** `claim:sector-nesting-exact` — proven by `TestExactness` (every line is a
  boundary), `TestSplitNotSnap` (3 tests: straddled-corner, straddled-straight, exact-boundary-no-dup),
  `TestSliverMergeExemptsSectorCuts` (2 tests: away-from-cut merges, at-cut preserved). Real-weekend
  reproduction (2023 Bahrain Q): 161/161 usable `lap_times` rows, zero skipped, pooled median
  line1=1748.9001128850223 m, line2=3920.0948806410674 m.
- **Trust limitations / drift found:** none found in the reused seams (`tiling.py`'s boundary/seg_type
  shape, `frozen_constants.MIN_SEGMENT_LENGTH_M`, `DatabaseManager.get_sessions`/`get_lap_times`,
  `session_fit.load_quali_session`, `driver_streams` all matched their documented contracts on first read —
  `lap_times.driver_id` being the FIA abbreviation was already flagged by G1's result and confirmed again
  directly against the real DB here).
- **Triage candidates:** the sliver-merge direction/type-inheritance choice above should be stated
  explicitly if g4 (corner descriptors/severity) or g5 (assembly) ever need to reason about which original
  segment a merged segment's classification came from.

## Test mode
**Required:** TDD-lean for `nest_sectors` (pure, tested first on synthetic tilings); smoke test guarded on
DB/store availability for `derive_sector_lines`.
**Satisfied:** yes. `test_sector_nesting.py` was written and run BEFORE `sector_nesting.py` existed (RED:
`ModuleNotFoundError`), then `nest_sectors` + `SectorLineUnavailableError` were implemented and all 15
`nest_sectors` tests passed on the FIRST attempt (no rework). `derive_sector_lines` was written in the same
pass (data-plumbing, not TDD-first per the handoff) and its guarded smoke test passed against the real
2023 Bahrain Q data present in this environment.

## Evidence

### Required Evidence 1 — pytest (LOAD-BEARING: exactness, split-not-snap, sliver-exempt, fail-closed)

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_sector_nesting.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-662
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 17 items

tests\unit\physics\segment_map\derivation\test_sector_nesting.py ....... [ 41%]
..........                                                               [100%]

============================== 17 passed in 0.79s ==============================
```
**Result:** pass. 17/17, including all six LOAD-BEARING rule classes:
- `TestExactness::test_both_sector_lines_appear_as_exact_boundaries`
- `TestSplitNotSnap` (3 tests: straddled-corner, straddled-straight, exact-boundary-no-dup)
- `TestSliverMergeExemptsSectorCuts` (2 tests: away-from-cut merges, at-cut preserved)
- `TestFailClosed` (5 tests: out-of-range, NaN, non-increasing, wrong-count, zero)
- `TestCompletenessPreserved` (2 tests)
- `TestSectorAssignment` (2 tests)
- `TestDeriveSectorLinesSmoke` (guarded real-weekend smoke + missing-DB fail-closed)

### Required Evidence 2 — simplification_limits

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/sector_nesting.py
```
```
PASS (1 files checked)
```
**Result:** pass. (First pass FAILED — `derive_sector_lines` at 156 lines / cyclomatic complexity 23 exceeded
the <100 line / <20 complexity limits. Refactored by extracting `_load_valid_sector_laps`,
`_abbreviation_to_driver_num`, and `_lap_sector_distances` as named helpers; re-ran clean with no test
regressions — 17/17 still green after the refactor.)

### Required Evidence 3 — MIN_SEGMENT_LENGTH_M import / no-literal-threshold grep

```bash
cd C:/Programs/f1brainz-wt/epic659-662
grep -n "MIN_SEGMENT_LENGTH_M" src/physics/segment_map/derivation/sector_nesting.py
grep -nE "\b5\.0\b" src/physics/segment_map/derivation/sector_nesting.py
```
```
11:* Sliver-merge EXEMPTS sector cuts -- ``MIN_SEGMENT_LENGTH_M`` sliver-merging
32:from src.physics.layer2.frozen_constants import MIN_SEGMENT_LENGTH_M
94:    boundaries, types = _merge_slivers(boundaries, types, cut_set, MIN_SEGMENT_LENGTH_M)

(second grep: no output — zero matches for a literal 5.0 anywhere in the file)
```
**Result:** `MIN_SEGMENT_LENGTH_M` is imported from `frozen_constants` and used at its one call site
(`_merge_slivers`'s `min_len` argument); no literal `5.0` appears anywhere in the file.

## TDD evidence

- Failing test observed: ran `test_sector_nesting.py` before `sector_nesting.py` existed — collection
  ERROR, `ModuleNotFoundError: No module named 'src.physics.segment_map.derivation.sector_nesting'`.
- Passing test observed: all 15 `nest_sectors` tests passed on the FIRST attempt after writing
  `sector_nesting.py` (no rework cycle for correctness); `derive_sector_lines`'s smoke test also passed on
  first attempt against real data.
- Refactor while green: yes — after the initial green pass, `simplification_limits` flagged
  `derive_sector_lines` (156 lines, complexity 23). Extracted three named helpers
  (`_load_valid_sector_laps`, `_abbreviation_to_driver_num`, `_lap_sector_distances`); re-ran the full test
  file immediately after and confirmed all 17 tests still green (no behavior change, pure extraction).

## lap_times read path + driver join (confirmatory, per Required Evidence)

**Read path:** `src.data.database.DatabaseManager(db_path).get_sessions(year=year,
session_type=session_type, gp_name=gp_name)` → `id` column gives `session_id`; then
`DatabaseManager.get_lap_times(session_id=session_id, valid_only=True)`, filtered further to
`sector1_time.notna() & sector2_time.notna()`. `db_path` defaults to the canonical tracked
`data/f1_data_<year>.db` (confirmed **git-tracked** via `git ls-files` and `git check-ignore` exit 1 — this
is NOT the "untracked data" category `docs/agents/CREW_CONTEXT.md` warns off a writing `DatabaseManager`
for; that rule targets the FastF1 cache / `telemetry_store.db` / model artifacts, which are untracked and
absent from this worktree). A `os.path.exists(db_path)` guard runs BEFORE constructing `DatabaseManager`,
specifically to avoid its `_init_database` side effect (creates an empty DB file at a missing path) —
`derive_sector_lines` raises `SectorLineUnavailableError` immediately instead.

**Driver join:** `lap_times.driver_id` is the **3-letter FIA abbreviation** (e.g. `'VER'`), confirmed by
direct sqlite inspection of `data/f1_data_2023.db` (matches G1's earlier finding for the same column
family). The telemetry session (`session.drivers`, a list of driver **numbers** — `car_data`/`pos_data`
keys) is reverse-mapped via `session.get_driver(num)["Abbreviation"]` into an `abbr_to_num` dict; each
`lap_times` row's `driver_id` looks up its telemetry driver-number key through that map, then
`session.laps.pick_drivers(driver_num)` (falling back to `pick_drivers(driver_id)` directly, since
`DBSession`'s `_ShimLaps.pick_drivers` is itself keyed by the `Driver` abbreviation column — the same
number→abbreviation fallback pattern G1 established) is filtered to `LapNumber == row["lap_number"]` to
get that exact lap's `LapStartTime`/`Time`.

**Time→distance mapping:** for the matched lap, position samples come from
`src.preprocessing.trajectory.loaders.driver_streams(session, driver_num)` (cached per driver across
rows), windowed to `[LapStartTime, Time]` in session-time seconds. `time_from_start = t - LapStartTime`;
`dist_from_start = cumsum(hypot(diff(X), diff(Y)))` prepended with `0.0` — the lap's own cumulative
arc-length from its XY samples. Cumulative sector time (`sector1_time` for line1, `sector1_time +
sector2_time` for line2) is `np.interp`-ed onto `(time_from_start, dist_from_start)`, guarded so a lap
whose cumulative sector time falls outside its own recorded telemetry span is skipped (not
extrapolated/fabricated) rather than silently accepted. Per-line samples are pooled across the whole
field's usable laps to a **MEDIAN** distance, with a `min_laps` floor (default 3) that raises
`SectorLineUnavailableError` if too few laps survive the join+guard chain.

## Pooled median result on a real weekend (store present)

2023 Bahrain Q (`data/f1_data_2023.db` + the durable telemetry store, both present in this environment):

```
n candidate lap_times rows (both sectors present): 161
n usable after join+telemetry-window guard: 161 (zero skipped)
line1 (S1|S2) median: 1748.9001128850223 m   (IQR 1741.46 - 1754.43, ~13 m spread)
line2 (S2|S3) median: 3920.0948806410674 m   (IQR 3913.48 - 3926.25, ~13 m spread)
```
Bahrain's nominal lap length is ~5412 m; the derived split (S1≈1749 m / S2≈2171 m / S3≈1492 m, roughly
32%/40%/28% of the lap) is a plausible real-world FIA sector proportion for that circuit. The ~13 m per-lap
IQR reflects individual-lap telemetry/interpolation noise; pooling 161 laps to the median is what delivers
the sub-meter-precision target the handoff asks for (the median itself, not any single lap's estimate).

## Assumptions

- **Sliver-merge direction preference:** when a sub-threshold segment has both a removable left and
  removable right flanking boundary, this implementation merges FORWARD first (absorbs into the next
  segment's type), falling back to backward only if the forward boundary is unremovable. Not pinned by the
  handoff (only the sector-cut exemption was); a within-latitude choice, noted for g4/g5.
- **`_EPS_M = 1e-9`** float64 exact-match tolerance for "this distance already IS a boundary" (used both to
  detect a sector line that coincides with an existing boundary, and to detect a sector-cut boundary during
  sliver-merge). Not a physical threshold — just float64 comparison tolerance at metre-scale distances.
- **`min_laps` default of 3** for `derive_sector_lines`, mirroring G1's `build_reference_lap`'s own
  `min_laps` default/convention (a judgment call, not a frozen constant — the handoff didn't specify a
  number for this gate).
- **DB-existence pre-check** before instantiating `DatabaseManager` (see Map Impact) — a defensive choice to
  avoid a side-effecting empty-DB-file creation on a missing path, not something the handoff asked for.
- **`nest_sectors` requires exactly 2 sector lines** (not a general N-line nester) — matches the handoff's
  "3 FIA sectors → 2 interior sector lines" framing; a wrong count fails closed rather than being
  generalized past what's asked.

## Stop conditions hit
None. Sector durations were readable from the per-year DB without editing any runtime file or calling
FastF1 directly (`DatabaseManager` + `session_fit.load_quali_session`, both existing untouched seams); the
time→distance join was unambiguous once `lap_times.driver_id`'s abbreviation convention was confirmed
against the real schema (matching G1's prior finding, not a fresh ambiguity); no frozen threshold looked
wrong (`MIN_SEGMENT_LENGTH_M=5.0` used as-is, unmodified).

## Out-of-scope observations
- None found as defects. See "Decision candidates" above (sliver-merge direction preference, DB-existence
  guard) — both surfaced as context for g4/g5, not bugs.

## Workflow Feedback

- **Handoff gaps:** the handoff pins the sector-cut EXEMPTION precisely but doesn't specify a sliver-merge
  *direction*/type-inheritance rule for the ordinary (non-exempt) case — I chose "prefer merging forward,
  absorb into the neighbor's type" as the most defensible reading of "merge into a neighbor," but a
  reviewer could reasonably expect a different tie-break (e.g. merge into the LARGER neighbor by length).
  Worth pinning explicitly if a later gate's tests depend on which side's type a merged sliver inherits.
- **Context rediscovered:** `docs/agents/CREW_CONTEXT.md`'s "untracked data needs absolute main-checkout
  paths... not by instantiating a writing DatabaseManager" rule reads at first glance like it might forbid
  using `DatabaseManager` against the per-year DB — I verified `data/f1_data_2023.db` is actually
  git-TRACKED and present in this worktree (not the untracked FastF1-cache/telemetry_store.db category the
  rule targets) before proceeding, per the same file's own "verify a cited seam before you reuse it"
  advice. Worth a one-line clarification in CREW_CONTEXT.md distinguishing "per-year `f1_data_*.db`
  (tracked, safe)" from "`telemetry_store.db`/FastF1 cache (untracked, main-checkout-path only)" so a future
  agent doesn't have to re-derive this from `git ls-files`.
- **Instructions improvised around:** `simplification_limits` failed on the FIRST draft of
  `derive_sector_lines` (156 lines / complexity 23, over the <100/<20 limits) — not an instruction gap, just
  the normal red-flag-then-refactor loop; extracted three helpers and re-verified. Noting it here per the
  handoff's own evidence requirement (paste the check, including the fact that it initially failed).
- **What would have made this easier:** the handoff's data-plumbing Close Criteria were precise enough that
  I could prototype the exact join+interpolation logic standalone (outside any module) against real 2023
  Bahrain Q data BEFORE writing any code, and it worked cleanly first try (161/161, zero skipped) — that
  prototyping step is what let `derive_sector_lines` pass its smoke test on the first attempt. Nothing to
  change; flagging the workflow as a good pattern for future data-plumbing gates.

## Return status
`complete`

## Rework (attempt 2)

**Trigger:** reviewer BLOCK, relayed by cmdr-662 — a real bug in `_merge_slivers`'s backward-merge branch,
plus a missing test that would have caught it.

**Bug (confirmed independently before fixing):** the forward-merge branch (`right_removable`) correctly
discards the sliver's OWN type and keeps the real neighbor's type — `del types[i]` removes the sliver's
type entry, leaving the next segment's type to occupy the merged slot. The backward-merge branch
(`left_removable`) did the OPPOSITE: `del types[i - 1]` removed the REAL NEIGHBOR's type entry, leaving the
SLIVER's own (noise) type to occupy the merged slot. Traced through a concrete 3-segment example
(`types=['A','B','C']`, sliver at index 1 merging backward into segment 0): the buggy code left
`types=['B','C']` (segment 0's real type `'A'` silently overwritten by the sliver's `'B'`) instead of the
correct `['A','C']`. All 17 original tests passed only because the one fixture that happened to exercise
the backward-merge branch (`test_sliver_whose_boundary_is_a_sector_cut_is_preserved`) had an accidentally
identical type on both sides of the merge, masking the bug — it asserted the sector line survived, not
which type the merged segment carried.

**Fix:** `src/physics/segment_map/derivation/sector_nesting.py`, `_merge_slivers`'s `left_removable` branch
changed from `del types[i - 1]` to `del types[i]` — now symmetric with the forward branch: in both
directions, the segment being deleted from `types` is always the SLIVER's own entry, never the real
neighbor's.

**New regression test:** `TestSliverMergeExemptsSectorCuts::test_backward_merge_keeps_the_real_neighbors_type_not_the_slivers`
in `tests/unit/physics/segment_map/derivation/test_sector_nesting.py`. Fixture: pre-nesting
`segment0=CORNER [0, 297.5)`, `segment1=STRAIGHT [297.5, 400)`; sector line `300.0` splits `segment1` into
a STRAIGHT sliver `[297.5, 300)` (2.5 m `< MIN_SEGMENT_LENGTH_M`) and a STRAIGHT piece `[300, 400)`. The
sliver's right boundary (`300.0`) is the sector cut, blocking forward-merge, forcing a backward merge into
`segment0` — which is a genuinely DIFFERENT type (CORNER) than the sliver (STRAIGHT), unlike the
split-duplicate sibling on the sliver's other side (always same-typed by construction, so it can never
expose this class of bug). Asserts the merged segment spanning `[0, 300)` is CORNER, not STRAIGHT.

**Verified the test actually catches the bug (not just decorative):** temporarily reverted the fix
(`del types[i - 1]`), ran only the new test — it FAILED:
```
AssertionError: backward-merged segment must inherit the real neighbor's type, not the sliver's own noise type
assert np.int8(0) == 2
```
(`0`=STRAIGHT was produced instead of the expected `2`=CORNER — exactly the bug). Restored the fix,
reran — passed. This confirms the test is a genuine regression guard, not a fixture that would pass either
way.

### Fresh evidence (post-fix, full re-run)

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_sector_nesting.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-662
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 18 items

tests\unit\physics\segment_map\derivation\test_sector_nesting.py ....... [ 38%]
...........                                                              [100%]

============================= 18 passed in 0.86s ==============================
```
**Result:** pass. 18/18 (was 17; +1 new regression test). All original rule-tests unaffected — the bug and
fix were isolated to the backward-merge branch only.

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/sector_nesting.py
```
```
PASS (1 files checked)
```
**Result:** pass.

```bash
grep -n "MIN_SEGMENT_LENGTH_M" src/physics/segment_map/derivation/sector_nesting.py
grep -nE "\b5\.0\b" src/physics/segment_map/derivation/sector_nesting.py
```
```
11:* Sliver-merge EXEMPTS sector cuts -- ``MIN_SEGMENT_LENGTH_M`` sliver-merging
32:from src.physics.layer2.frozen_constants import MIN_SEGMENT_LENGTH_M
94:    boundaries, types = _merge_slivers(boundaries, types, cut_set, MIN_SEGMENT_LENGTH_M)

(second grep: no output — still zero literal-5.0 matches after the fix)
```
**Result:** unchanged — `MIN_SEGMENT_LENGTH_M` import/usage and the no-literal guarantee both still hold.

**Files touched in this rework:**
- `src/physics/segment_map/derivation/sector_nesting.py` — one-line fix in `_merge_slivers`
- `tests/unit/physics/segment_map/derivation/test_sector_nesting.py` — one new test added
- `.agent-work/662-segment-map/crew-handoffs/g3-impl-plan.json` — `m2-green` reopened (rework 1/3),
  cascaded `m3-derive`/`m4-evidence-result` back to pending, then all three re-driven to `complete`
  through the engine with fresh evidence (not hand-edited)

**Decision candidate superseded:** the earlier "sliver-merge direction preference" candidate (Map Impact,
attempt 1) claimed the forward-first preference was the only under-specified choice; this rework shows the
type-inheritance rule itself needed to be *symmetric* regardless of direction, which is now fixed and
tested in both directions.

## Return status (final)
`complete`
