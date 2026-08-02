# Implementer Handoff — G3 FIA sector-line derivation + nesting

## Gate
g3 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Task
Derive the 2 interior FIA sector LINES for a weekend and NEST them into the G2 base tiling. New files:
- `src/physics/segment_map/derivation/sector_nesting.py`
- `tests/unit/physics/segment_map/derivation/test_sector_nesting.py`

Split the work into a PURE nesting function (rigorously unit-tested) + a data-plumbing derivation
(smoke-tested):

1. `class SectorLineUnavailableError(Exception)` — raised to FAIL CLOSED (see below).
2. `nest_sectors(boundaries_m, seg_type_code, sector_lines_m, lap_length_m) -> (boundaries_m',
   seg_type_code', sector)` — PURE, no I/O. Takes the G2 base tiling (boundaries + seg_type_code from
   `tiling.tile_reference_lap`) and the interior sector-line distances; returns the nested tiling plus a
   per-segment `sector` int8 array (1/2/3). This carries all the subtle-correctness rules (below).
3. `derive_sector_lines(year, gp_name, session_type="Q", ...) -> list[float]` — data plumbing: read the
   per-lap FIA sector DURATIONS from the per-year DB `lap_times` table and map cumulative sector time to
   distance via each lap's telemetry time↔distance profile, pooled to a MEDIAN sub-meter boundary.

## Protected Intent
FIA sector lines are MANDATORY structural cut points. A segment straddling a line must SPLIT into
same-class pieces — snapping the boundary to a nearby existing cut would distort physical boundaries.
The map must never silently omit a sector line.

## Test Mode
TDD-lean. `nest_sectors` is pure → write its tests FIRST on hand-built synthetic tilings (deterministic).
`derive_sector_lines` gets a real-data smoke guarded on DB/store availability (skip cleanly if absent).

## Close Criteria (nest_sectors — the subtle-correctness heart; MUST TEST each)
1. **Every sector line is a segment boundary** in the output (exactness).
2. **Split-not-snap:** a segment straddling a sector line is SPLIT into TWO pieces of the SAME seg_type
   (a straddled CORNER → two CORNER pieces; a straddled STRAIGHT → two STRAIGHT pieces). The line becomes
   the new boundary at its EXACT distance — never snapped to a pre-existing nearby boundary.
3. **Sliver-merge EXEMPTS sector cuts:** merge any segment shorter than `MIN_SEGMENT_LENGTH_M` (IMPORT
   from `src.physics.layer2.frozen_constants`) into a neighbor — BUT a boundary that IS a sector line is
   NEVER removed by sliver-merging (a tiny piece adjacent to a sector cut is not merged ACROSS the cut).
   Test: a <5 m sliver away from any sector line merges; a <5 m sliver whose boundary is a sector cut is
   preserved (the sector line survives).
4. **Fail CLOSED:** raise `SectorLineUnavailableError` rather than return a tiling missing a sector-line
   invariant (e.g. a sector line outside [0, lap_length], NaN, or unplaceable). Do NOT emit a
   partial/degraded map.
5. **Completeness preserved:** after nesting the partition is still complete (boundaries strictly
   increasing 0→lap_length, no gaps/overlaps).
6. **sector int8 assignment:** each output segment gets sector ∈ {1,2,3} by which sector interval its
   midpoint falls in (line1 splits S1|S2, line2 splits S2|S3).

## Close Criteria (derive_sector_lines — data plumbing; smoke-test)
- Read per-lap FIA sector durations from the per-year DB (`data/f1_data_2023.db`) `lap_times` table
  columns `sector1_time`, `sector2_time` (durations, seconds). Prefer reusing `src/data/database.py`
  (`DatabaseManager`) if it exposes a lap_times accessor; else a documented read-only sqlite query
  (`mode=ro`). Cumulative time at line1 = sector1_time; at line2 = sector1_time + sector2_time.
- Per lap, build a monotone time→distance curve from the same telemetry the reference lap uses
  (distance = cumsum of consecutive position deltas; time = session_time − lap_start). Interpolate the
  cumulative sector time onto distance. Pool across the field's clean laps → **median** boundary distance
  (sub-meter target). Reuse the store-first session from `session_fit.load_quali_session` for telemetry
  (as G1 did) — do NOT call FastF1 directly.
- Join lap_times (per-year DB) to telemetry laps by (driver, lap_number). Cite exactly how you join
  (driver keying: abbreviation vs number — see G1's result note) in IMPLEMENTER_RESULT.
- If sector durations or the time→distance map are unavailable, raise `SectorLineUnavailableError`
  (fail closed) — do NOT fabricate lines.

## Allowed Scope
`src/physics/segment_map/derivation/sector_nesting.py`; its test file. Read (not edit): `tiling.py`,
`reference_lap.py`, `frozen_constants.py`, `src/data/database.py`, `src/physics/session_fit.py`,
`data/f1_data_2023.db` schema.

## Specific Exclusions
- Do NOT compute corner descriptors/severity (g4) or assemble/store (g5).
- Do NOT edit `docs/architecture/*`, existing `segment_map/*.py` runtime files, or `frozen_constants.py`.
- Official corner-number markers are OUT (cosmetic, later/skip). Do NOT wire OpenF1/live-timing segment data.

## Constraints
- frozen-constants: import MIN_SEGMENT_LENGTH_M (never literal 5.0).
- DB-only analysis: telemetry via store-first session; sector times from the per-year DB. No FastF1.
- 3 FIA sectors → 2 INTERIOR sector lines (S3 ends at start/finish = lap_length).

## Map Anchors (inbound)
- **Structural:** sector_nesting.py (NEW); lap_times.sector{1,2}_time (per-year DB); frozen_constants
  MIN_SEGMENT_LENGTH_M; tiling.py (base tiling input).
- **Decision anchors:**
  - decision:sector-split-not-snap — straddlers split into same-class pieces; sliver-merge exempts sector
    cuts; nesting fails CLOSED. @grade: settled/human (launch order, spec §1) · leans g3
- **Evidence expectations:** claim:sector-nesting-exact (every line a boundary; straddlers split; slivers
  merged except at cuts).
- **Map confidence flags:** no prior sector-line derivation — time→distance interpolation is the novel step.

## Deliverable Path Check
- **Committed:** `sector_nesting.py`, `test_sector_nesting.py` — `git check-ignore` exits 1. New in
  `git status` until staged.

## Required Evidence
- pytest `test_sector_nesting.py` green (LOAD-BEARING: the exactness, split-not-snap, sliver-exempt, and
  fail-closed tests each prove a distinct rule).
- `simplification_limits --paths src/physics/segment_map/derivation/sector_nesting.py` clean.
- Confirm MIN_SEGMENT_LENGTH_M imported (grep, no literal 5.0). In IMPLEMENTER_RESULT: the lap_times
  read path + the driver join used.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_sector_nesting.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/sector_nesting.py
```

## Suggested Model Tier
Stronger — split-not-snap + sliver-exempt-cuts + fail-closed are the subtle rules; the join is fiddly.

## Authority
Split-not-snap, sliver-exempt-cuts, fail-closed, and the frozen threshold are DECIDED. You MAY decide the
result shape, the exact join, and interpolation details (cite them).

## Stop Conditions
Stop and return if: sector durations can't be read without editing a runtime file or calling FastF1; the
time→distance join is ambiguous enough to risk mis-placed lines; a frozen threshold looks wrong.

## Return Format
IMPLEMENTER_RESULT to `.agent-work/662-segment-map/g3-impl-result.md`: slice, files, test mode, evidence
(pytest incl. the four rule-tests + simplification + grep), lap_times read path + driver join, pooled
median sub-meter result on a real weekend (if store present), assumptions, stop conditions, out-of-scope,
workflow feedback. **Deliver a concise summary to "cmdr-662" via SendMessage before ending your turn.**
