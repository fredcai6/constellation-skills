# Reviewer Handoff — G3 FIA sector-line derivation + nesting

## Gate
g3 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## What was implemented
`src/physics/segment_map/derivation/sector_nesting.py` — `SectorLineUnavailableError`,
`nest_sectors(boundaries_m, seg_type_code, sector_lines_m, lap_length_m)` (PURE) and
`derive_sector_lines(year, gp, session)` (data plumbing). Tests
`tests/unit/physics/segment_map/derivation/test_sector_nesting.py` (17). Result:
`.agent-work/662-segment-map/g3-impl-result.md`.

## How to inspect
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_sector_nesting.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/sector_nesting.py
```
Read `sector_nesting.py`, `tiling.py` (base tiling shape), `frozen_constants.py`.

## Task statement
Derive the 2 interior FIA sector lines (time→distance, pooled median, sub-meter) and nest them: split
straddlers into same-class pieces, sliver-merge exempting sector cuts, fail CLOSED, assign sector int8.

## Reviewer FOCUS (subtle-correctness gate — verify each rule with its test)
1. **Split-not-snap:** a straddling segment SPLITS into TWO SAME-class pieces at the EXACT line distance —
   NOT snapped to a pre-existing boundary. Verify the test proves the new boundary equals the line and
   flanking pieces keep the original type, and that no existing boundary moved. THIS IS #1.
2. **Sliver-merge EXEMPTS sector cuts:** a <MIN_SEGMENT_LENGTH_M sliver away from a cut merges; a sliver
   whose boundary IS a sector line is preserved (the line survives). Verify both directions are tested.
3. **Fail CLOSED:** `SectorLineUnavailableError` raised for out-of-range / NaN / non-increasing / wrong
   count / unplaceable lines — never a partial map. Verify the fail-closed tests.
4. **MIN_SEGMENT_LENGTH_M IMPORTED** from frozen_constants, no literal 5.0 (re-run grep).
5. **Completeness preserved** after nesting (boundaries strictly increasing 0→lap_length); **sector int8**
   assignment correct (midpoint → 1/2/3).
6. **derive_sector_lines:** reads sector durations from the per-year DB lap_times; time→distance via
   store-first telemetry (NO FastF1); pooled median. Sanity-check the real-data result if store present
   (Bahrain 2023 Q line1≈1749m / line2≈3920m — plausible against ~5412m lap). Confirm no FastF1 import.
7. **No scope breach:** no edit to docs/architecture/*, existing segment_map runtime files, frozen_constants.

## Close Criteria (verdict basis)
Tests green (17/17) incl. the six rule classes; simplification clean; split-not-snap + sliver-exempt +
fail-closed genuinely proven; threshold imported; derive_sector_lines DB-only.

## Constraints / Map Anchors
DB-only / pinned interpreter. Inherits decision:sector-split-not-snap (@grade settled/human).

## Required Evidence
Re-run both commands + the no-literal grep; quote the split-not-snap assertion and one fail-closed
assertion you confirmed.

## Return Format
REVIEW_RESULT to `.agent-work/662-segment-map/g3-review-result.md`: verdict APPROVE/BLOCK, findings
(severity + file:line), evidence reproduced, workflow feedback. **Deliver a concise summary (verdict +
result path) to "cmdr-662" via SendMessage before ending your turn.**
