# Implementer Handoff — g4-scorecard-implement

## Gate
g4-scorecard-implement (#668 instrument panel, epic #659). Worktree
`C:/Programs/f1brainz-wt/epic659-668`, branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
Build **Instrument 4 — the composed-sector scorecard** in
`src/physics/instrument_panel/sector_scorecard.py` (+ tests). Segment predictions sum into
composed FIA sectors, validated against official sector times. PURE module, synthetic-tested,
F12-INDEPENDENT. It CONSUMES the already-frozen scorecard triple from #660 (mint nothing).

## Protected Intent
A DIAGNOSTIC that SIZES calibration; it gates ONLY on the frozen gross-miscalibration sanity
bound. Predicted sectors are built from strictly-pre inputs; official sector times enter ONLY
as the post-hoc comparison target — NO leakback of a sector outcome into the prediction.

## The two SEPARATED claims (per review T11 — do not conflate)
- **(a) Position-sum EXACTNESS = a construction check.** Per driver, the per-segment predicted
  times, grouped into their FIA sector (segment→sector by distance, via
  `src/physics/segment_map/derivation/sector_nesting.py`), MUST sum EXACTLY to the composed
  sector-time prediction. This is a construction identity (how the composed prediction is
  defined), asserted exactly (fp tolerance).
- **(b) Distribution calibration = the genuine external anchor.** The composed sector-time
  prediction (central value AND coverage, with a propagated Student-t σ) vs the OFFICIAL sector
  time. Central: bias of predicted vs official. Coverage: fraction of official sector times
  falling within the predicted interval, across drivers/laps — computed with `predictive_t`
  from `src/common/student_t.py` (`.interval(level)` / `.cdf` PIT), NON-Gaussian (owner ruling
  5). DIAGNOSTIC for size.

## Gating (consume the frozen bound — mint nothing)
Import the frozen triple from `src/physics/layer2/frozen_constants.py`:
`SECTOR_CALIB_COVERAGE_NOMINAL` (0.90), `SECTOR_CALIB_COVERAGE_OBSERVED_MIN` (0.85, DIAGNOSTIC),
`SECTOR_CALIB_GROSS_MISCALIB_BOUND` (0.50, GATING). The scorecard reports coverage vs the
nominal/observed-min for SIZING, and GATES (a hard fail) ONLY when observed coverage for the
nominal interval falls below `SECTOR_CALIB_GROSS_MISCALIB_BOUND` (a mechanically-broken
calibration). Do NOT re-mint any of these literals.

## σ propagation (Build-1 simplification — state it honestly)
The composed sector σ from its segments: treat segments as INDEPENDENT
(`σ_sector = sqrt(Σ σ_seg²)`) as a deliberate Build-1 simplification (mirrors the #667 join's
own honest independent-cell assumption; segments share a driver/session and are likely
correlated — say so in the docstring, do not claim it as measured). A correlation-aware upgrade
is #700, out of scope.

## no-frame-kill
If a driver/sector has insufficient segment coverage to compose a prediction, report it as an
explicit "uncomposable" result, never a fabricated sector time.

## Synthetic tests (falsifiable)
- Position-sum identity holds EXACTLY on synthetic segment predictions (and FAILS if a segment
  is misassigned to the wrong sector — spot-check the falsifier).
- Coverage path exercises the Student-t heavy tail (nu finite), not ±1.96σ: a well-calibrated
  synthetic (official drawn from the predicted distribution) → observed coverage ≈ nominal; an
  understated-σ synthetic → coverage materially below.
- The gross-miscalib GATE fires ONLY when observed coverage < `SECTOR_CALIB_GROSS_MISCALIB_BOUND`
  (a synthetic at coverage 0.7 does NOT gate; at 0.3 it DOES).
- No-leakback: a test/inspection confirming the official sector time is used only as the
  comparison target, never fed into the predicted central value.

## Allowed Scope
CREATE `src/physics/instrument_panel/sector_scorecard.py`,
`tests/unit/physics/instrument_panel/test_sector_scorecard.py`. READ-ONLY reuse:
`src/physics/layer2/frozen_constants.py` (consume triple), `src/common/student_t.py`,
`src/physics/segment_map/derivation/sector_nesting.py` (segment→sector mapping — inspect its API
first; if it needs a real DB to map, keep the UNIT tests on a synthetic mapping and leave the
real wiring for the g7 real-data run).

## Specific Exclusions
- Do NOT read a real DB in the unit tests (synthetic-only; F12-independent). Do NOT re-mint the
  SECTOR_CALIB_* literals. Do NOT let an official sector outcome enter a prediction (leakback).
- Do NOT touch #660/#664/#666/#667 producers or any `f1_data_*.db`. No #667 join.

## Constraints
- Pure/deterministic. Student-t coverage (no Gaussian). Consume frozen bound. Position-sum exact.
- If `sector_nesting.py` cannot be used purely (needs a DB), abstract the segment→sector mapping
  as an injected param so the unit tests stay synthetic; note it for the g7 wiring.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/frozen_constants.py` SECTOR_CALIB_* (consume); `src/physics/segment_map/derivation/sector_nesting.py`; `src/common/student_t.py`; `src/physics/instrument_panel/`.
- **Capability:** composed-sector validation.
- **Constraints:** constraint:strictly-pre (no leakback); constraint:no-baked-normality; constraint:no-inline-literals (consume frozen bound).
- **Decision anchors:** decision:consume-frozen-scorecard-triple — #660 already froze it.
  `@grade: settled/inherited · leans g4`
- **Evidence:** claim:position-sum-construction (exact); claim:no-leakback; claim:coverage-is-distribution-not-gaussian.

## Deliverable Path Check
- **Committed** — `src/physics/instrument_panel/sector_scorecard.py`,
  `tests/unit/physics/instrument_panel/test_sector_scorecard.py`; `git check-ignore` exits 1.
  New files show in `git status`, not `git diff` until staged.

## Required Evidence
- LOAD-BEARING: pytest output — position-sum identity, coverage-calibration (well-calibrated vs
  understated), gross-miscalib gate fires only below the frozen bound.
- LOAD-BEARING: pyright-0 on the new module.
- Confirmatory: the frozen triple is imported (not re-minted) — show the import line.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_sector_scorecard.py -q
```

## Suggested Model Tier
simple-bounded — well-specified; the risks are (i) re-minting the frozen bound and (ii) leakback,
both explicitly fenced above.

## Authority
The two-separated-claims split, consume-not-remint of the frozen triple, gate-only-on-gross-
miscalib, and no-leakback are DECIDED (commander, from the launch order). Do not merge the two
claims or re-mint constants. STOP and return if a real DB read seems required for the unit tests.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, `sector_nesting.py` forces a real DB read
into the unit tests, or the frozen triple cannot be consumed cleanly.

## Return Format
Return IMPLEMENTER_RESULT (slice, files, evidence, assumptions, stops, out-of-scope, workflow
feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g4-scorecard-implement-result.md` before ending
your turn — that file IS the deliverable.
