# Reviewer Handoff — g2-variance-review

## Gate
g2-variance-review (#668 instrument panel). Worktree `C:/Programs/f1brainz-wt/epic659-668`,
branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Survey State Location
`.agent-work/668-instrument-panel/g2-variance-review/review.json`.

## What Was Implemented
Instrument 1 — the variance-decomposition instrument. New package
`src/physics/instrument_panel/` with `variance_decomposition.py`
(`decompose_segment_time_variance` + `VarianceShares`) built purely on `fit_two_way` from
`src/physics/layer2/pooling.py`, plus 7 synthetic-recovery TDD tests. Implementer result:
`.agent-work/668-instrument-panel/crew-results/g2-variance-implement-result.md`.

## How to Inspect the Diff
Review the UNCOMMITTED working tree (linked worktree). `git status --porcelain` then `git diff`
(untracked-safe). New files appear in `git status`, not `git diff` until staged. Do NOT use
`git diff main...HEAD`.

## Task Statement
Split segment-time variance into car-reference / driver-utilization / residual shares via the
additive TwoWayPool arithmetic, driver-utilization share flagged as a floor, synthetic-recovery
tested. (Full handoff: `.agent-work/668-instrument-panel/crew-handoffs/g2-variance-implement-handoff.md`.)

## Close Criteria (each a review check)
- Shares are in [0,1] and sum to ~1.0 (fp tolerance); driver-utilization share exposed as a FLOOR.
- Realized via `fit_two_way(teams=drivers, circuits=classes)`: frac_team=driver-utilization,
  frac_circuit=car-reference, frac_resid=residual. Verify the axis mapping is correct
  (drivers→team, classes→circuit) — a swapped mapping would invert the instrument's meaning.
- NO interaction term / NO bespoke model added (owner ruling 4); `pooling.py` unmodified.
- Synthetic-recovery tests genuinely falsify: pure-car → driver-util ≈ 0; pure-driver →
  car-ref ≈ 0; raising the driver coefficient raises driver-util share monotonically. Confirm
  the tests would FAIL if the mapping were swapped or a share hard-coded (spot-check by reading
  the test asserts, not just that they pass).
- pyright-0 on the new module; tests green on the pinned interpreter (reproduce yourself).

## Allowed Scope
`src/physics/instrument_panel/` (new), `tests/unit/physics/instrument_panel/` (new). No
producer modules touched; no real DB read; no `data/` change.

## Specific Exclusions
No #660/#664/#666/#667 producer edits; no `f1_data_*.db` write; no interaction term.

## Constraints the Implementation Must Respect
- Pure/deterministic; additive pool only; driver-utilization = floor; F12-independent (no real
  DB, no frozen REPLICATION_* needed).

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/pooling.py`; `src/physics/instrument_panel/` (new).
- **Capability:** driver-utilization measurement (variance sizing).
- **Constraints:** constraint:lowest-dimensionality (no interaction term); constraint:no-frame-kill (driver share=floor).
- **Evidence:** each share recovers its synthetic ground-truth coefficient.

## Evidence Produced
Implementer reports 7 tests passing + pyright-0. Reproduce:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_variance_decomposition.py -q`.
Your APPROVE feeds `g2-variance-integrate.c1` (tests) + `.c2` (verdict).

## Suggested Model Tier
simple-bounded — small pure module; the one real risk is a swapped axis mapping, so scrutinize that.

## Stop Conditions
BLOCK if: diff inaccessible, tests don't reproduce, axis mapping wrong, an interaction term was
added, or shares don't sum/bound correctly.

## Return Format
Return REVIEW_RESULT (verdict APPROVE/BLOCK + per-check findings + workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g2-variance-review-result.md` before ending your turn.
