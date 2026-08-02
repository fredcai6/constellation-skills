# Reviewer Handoff — g4-scorecard-review

## Gate
g4-scorecard-review (#668 instrument panel). Worktree `C:/Programs/f1brainz-wt/epic659-668`,
branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Survey State Location
`.agent-work/668-instrument-panel/g4-scorecard-review/review.json`.

## What Was Implemented
Instrument 4 — `src/physics/instrument_panel/sector_scorecard.py` + 11 tests. Position-sum
exactness + Student-t distribution-calibration coverage + gross-miscalib gate consuming the
frozen SECTOR_CALIB_* triple. Result:
`.agent-work/668-instrument-panel/crew-results/g4-scorecard-implement-result.md` (READ its
honesty notes: test-after collapse on m2/m3, and the `min(member n_eff)` Build-1 default).

## How to Inspect the Diff
UNCOMMITTED working tree. `git status --porcelain` then `git diff`. New files in `git status`,
not `git diff` until staged. Not `git diff main...HEAD`.

## Close Criteria (each a check — reproduce)
- **Position-sum EXACTNESS**: per-segment predictions sum EXACTLY to the composed sector (fp
  tolerance); confirm a misassigned segment would BREAK it (read the falsifier).
- **Distribution calibration is Student-t** (via `predictive_t`, heavy-tail), NOT ±1.96σ:
  well-calibrated synthetic → coverage ≈ nominal; understated-σ → coverage materially below.
- **Consume-not-remint**: `SECTOR_CALIB_COVERAGE_NOMINAL/OBSERVED_MIN/GROSS_MISCALIB_BOUND` are
  IMPORTED from `src/physics/layer2/frozen_constants.py` — show the import; confirm NO literal
  0.90/0.85/0.50 re-minted in the module.
- **Gate only on gross-miscalib**: the hard fail fires ONLY when observed coverage <
  `SECTOR_CALIB_GROSS_MISCALIB_BOUND`; a coverage of 0.7 does NOT gate, 0.3 does. Reproduce.
- **No leakback**: official sector time is used only as the comparison target, never fed into a
  predicted central value. Confirm by reading the compose path.
- **n_eff combination**: the implementer used `min(member n_eff)` (a Build-1 default the handoff
  did not pin). Judge it reasonable/conservative (least-supported segment dominates the tail) —
  APPROVE if sound + honestly documented; flag only if it materially distorts coverage.
- pyright-0 on the new module; 11 tests green on the pinned interpreter (reproduce).

## Allowed Scope
`src/physics/instrument_panel/sector_scorecard.py`, `tests/unit/physics/instrument_panel/`. No
producer edits, no real DB, no `data/` change.

## Specific Exclusions
No re-minted SECTOR_CALIB_* literals; no leakback; no #667 join; no `f1_data_*.db`.

## Constraints the Implementation Must Respect
Two separated claims; Student-t coverage; consume frozen bound; gate only on gross-miscalib;
no-frame-kill uncomposable branch.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/frozen_constants.py` SECTOR_CALIB_* (consume); `src/common/student_t.py`; `src/physics/segment_map/derivation/sector_nesting.py`; `src/physics/instrument_panel/`.
- **Decision anchors:** decision:consume-frozen-scorecard-triple — #660 already froze it.
  `@grade: settled/inherited · leans g4`
- **Evidence:** claim:position-sum-construction; claim:no-leakback; claim:coverage-is-distribution-not-gaussian.

## Evidence Produced
11 tests + pyright-0. Reproduce:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_sector_scorecard.py -q`.
Your APPROVE feeds `g4-scorecard-integrate.c1` (tests) + `.c2` (verdict).

## Suggested Model Tier
simple-bounded — main risks are a re-minted literal and leakback, both checkable directly.

## Stop Conditions
BLOCK if: position-sum not exact; Gaussian coverage; a SECTOR_CALIB_* literal re-minted; gate
fires on something other than the gross-miscalib bound; leakback present; numbers don't reproduce.

## Return Format
Return REVIEW_RESULT (APPROVE/BLOCK + findings + workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g4-scorecard-review-result.md` before ending your turn.
