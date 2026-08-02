# Reviewer Handoff — G2 Canonical gate + base tiling

## Gate
g2 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## What was implemented
`src/physics/segment_map/derivation/tiling.py` — `tile_reference_lap(ref)` producing `boundaries_m` +
`seg_type_code` (SegType STRAIGHT/BRAKING_ZONE/CORNER). New tests
`tests/unit/physics/segment_map/derivation/test_tiling.py` (9 tests). Implementer result:
`.agent-work/662-segment-map/g2-impl-result.md`.

## How to inspect
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_tiling.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/tiling.py
```
Read `tiling.py`, `frozen_constants.py`, `reference_lap.py` (ReferenceLap fields), `runtime.py` (SegType).

## Task statement
Type the reference lap into a COMPLETE contiguous partition: corner = curvature > threshold; braking
zone = field ENVELOPE onset at p10; straight = remainder. Frozen thresholds imported, never literals.

## Reviewer FOCUS (subtle-correctness gate)
1. **Braking onset is the ENVELOPE (p10), NOT a mean/median.** Verify the pre-authored envelope-not-mean
   test genuinely proves the produced onset = the BRAKING_ONSET_QUANTILE (0.10) crossing and is strictly
   UPSTREAM of the 0.5 (mean/median) crossing. Confirm the code computes onset from the p10 crossing of
   brake_active_frac, not any central tendency. THIS IS THE #1 CHECK.
2. **Both thresholds IMPORTED from frozen_constants** — no literal 0.005 / 0.10 in tiling.py (re-run the
   grep `grep -nE "0\.005|0\.10|0\.1[^0-9]" tiling.py`).
3. **Complete partition:** boundaries strictly increasing, 0.0→lap_length, no gaps/overlaps; the
   completeness test must recompute coverage, not just check 4 scalars. Confirm.
4. **Corner gate is curvature** (abs(curvature) > threshold), not lateral-g.
5. **SegType reused** from runtime.py, not redefined.
6. **Wrap handling:** the implementer used a non-wrapping simplification (a start/finish-straddling corner
   → two segments). Judge whether this is acceptable for Build 1 (it is a documented simplification;
   most circuits have a start/finish straight so it rarely bites). Flag if you think it's wrong, but it
   is not necessarily a BLOCK — note it for the g6 corner-count check (which already merges split rows).
7. **No scope breach:** no edit to docs/architecture/*, existing segment_map runtime files, or
   frozen_constants.py.

## Close Criteria (verdict basis)
Tests green (9/9) incl. the two load-bearing tests (completeness + envelope-not-mean); simplification
clean; envelope-not-mean genuinely proven; thresholds imported; partition complete.

## Constraints
DB-only / pinned interpreter. Reviewer does not edit code.

## Map Anchors (inbound)
Inherits g2-implement anchors: decision:corner-gate-is-curvature (@grade settled/inherited),
decision:braking-envelope-p10-not-mean (@grade settled/human), constraint:frozen-constants.

## Required Evidence
Re-run both commands + the no-literal grep; a one-line confirmation that the envelope-not-mean test
proves onset==p10-crossing < mean-crossing (quote the assertion).

## Return Format
REVIEW_RESULT to `.agent-work/662-segment-map/g2-review-result.md`: verdict APPROVE/BLOCK, findings
(severity + file:line), evidence reproduced, workflow feedback. **Deliver a concise summary (verdict +
result path) to "cmdr-662" via SendMessage before ending your turn.**
