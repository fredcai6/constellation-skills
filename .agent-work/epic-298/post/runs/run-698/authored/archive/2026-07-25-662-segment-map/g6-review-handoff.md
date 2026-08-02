# Reviewer Handoff — G6 Acceptance: GATING checks + verdict

## Gate
g6 (issue #662) — the substantive gating verdict. Pinned interpreter:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## What was implemented
`scripts/validate_segment_map_662.py` (harness), `tests/unit/physics/segment_map/derivation/
test_segment_map_gating.py` (6 tests), `.agent-work/662-segment-map/VERDICT.md` (numbers, local-only),
plus a minimal pre-authorized `drivers=` filter on `reference_lap.py` (+ its test). Result:
`.agent-work/662-segment-map/g6-impl-result.md`. VERDICT: both GATING claims PASS.

## How to inspect
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths scripts/validate_segment_map_662.py
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/validate_segment_map_662.py
```
Read `VERDICT.md`, `validate_segment_map_662.py`, the reference_lap.py `drivers=` diff, `regime_rollup.py`,
`.agent-work/archive/2026-07-25-explore-ref-utilization/excursions/P4-RESULT.md`.

## Reviewer FOCUS (verify each)
1. **GATING-1 and GATING-2 are SEPARATELY named** so a failure distinguishes claim:map-stable from
   claim:typing-correct. Confirm.
2. **Scoped null is HONEST** (not silently green, not fabricated): the 2023 no-repeat fact is
   mechanically confirmed and recorded as a TYPED "not tested" result. Confirm.
3. **Split-half is a genuine disjoint-subset derivation** (even/odd drivers); median drift < imported
   MAP_STABILITY_DRIFT_M; the numbers REPRODUCE when you re-run the validate script. Verify the median
   (not max) is the asserted gate and the max-drift caveat is honestly reported, not hidden.
4. **PHYSICAL corner count MERGES sector-split rows** (contiguous CORNER collapse) — a sector-split
   corner is NOT double-counted. Verify the Bahrain count (12) and that the collapse logic is correct.
5. **Typing references are real:** P4 range [11,17] (Bahrain), Austria official 10 turns (cited). The
   regime_rollup comparison is a distance-SHARE cross-check (not a nonexistent discrete tally); the
   0.308-vs-0.523 divergence rationale (stricter curvature gate vs CORNER_GATE_MS2=3.0) is sound.
6. **MAP_STABILITY_DRIFT_M imported** (no literal 10.0). **No frozen-constant retune.**
7. **drivers= filter backward-compatible:** the default path (drivers=None) is byte-unchanged — the
   existing reference_lap tests still pass (8/8). No scope breach beyond the pre-authorized filter.
8. **No-frame-kill honored:** a scoped null / bounded caveat is reported as a complete deliverable.

## Close Criteria (verdict basis)
Tests green; validate script numbers reproduce; scoped-null honest; physical-corner merge correct;
typing references real; distance-share rationale sound; threshold imported; drivers= backward-compat.
APPROVE if the gating methodology is honest and the numbers reproduce; BLOCK only on a real methodology
error (e.g. double-counted corners, a fabricated number, a silently-greened null, a non-reproducing number).

## Constraints / Map Anchors
DB-only / pinned interpreter. Inherits decision:stability-scoped-null-split-half; constraint:no-frame-kill;
constraint:frozen-constants.

## Required Evidence
Re-run the gating tests + the reference_lap tests + the validate script yourself; confirm the headline
numbers (Bahrain median 2.18m, Austria 3.48m, Bahrain 12 corners, Austria 10==10) reproduce.

## Return Format
REVIEW_RESULT to `.agent-work/662-segment-map/g6-review-result.md`: verdict APPROVE/BLOCK, findings
(severity + file:line), evidence reproduced (the reproduced numbers), workflow feedback. **Deliver a
concise summary (verdict + result path + reproduced numbers) to "cmdr-662" via SendMessage before ending
your turn.**
