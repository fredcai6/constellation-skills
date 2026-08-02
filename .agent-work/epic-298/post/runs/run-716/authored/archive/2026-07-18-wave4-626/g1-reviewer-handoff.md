# Reviewer Handoff

## Gate
`g1` — Frozen metric harness (frame / floor / holdout / gate_spec).

## Survey State Location
Create your review survey at `.agent-work/wave4-626/g1-review/review.json` (under the workbench, not the worktree root).

## What Was Implemented
New package `src/physics/weekend_state/`: `frame.py` (loads Q `session_estimates` from the ABSOLUTE main path), `floor.py` (column-parameterizable reimplementation of x4's convergence metric + `weekend_relative`), `holdout.py` (frozen deterministic split `round_idx % 3 == 0`), `gate_spec.py` (frozen F6 rule: F1 signal-preservation guard, F2 paired held-out floor, F3 >=7/11 car-season-bootstrap). 25 unit tests. Implementer result: `.agent-work/wave4-626/g1-implementer-result.md`.

## How to Inspect the Diff
This is an UNCOMMITTED working tree in a linked worktree. Inspect with `git status --porcelain` then `git diff` (files are untracked — `git diff --name-only` hides them; read the new files directly under `src/physics/weekend_state/` and `tests/unit/physics/weekend_state/`).

## Task Statement
Build the frozen metric foundation the four-layer model is judged on: reproduce x4's floor faithfully, freeze the held-out split + F6 decision rule BEFORE any layer exists, and make the gate un-gameable by over-shrinkage. Full task: `.agent-work/wave4-626/g1-implementer-handoff.md`.

## Close Criteria (each a review check)
- floor.py reproduces the 624-phase0-baseline-lock x4 table on ALL 11 axes (rel & abs noise_sd + N_weekends) within a tight tolerance — RE-RUN `test_floor_reproduction.py` and confirm; spot-check 2-3 axes against `docs/physics/624-phase0-baseline-lock.md` yourself.
- floor.py's metric logic MATCHES x4's `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x4-analysis/normalization_stability.py` (MIN_FIELD=6, MIN_WEEKENDS=4, field_sigma=median cross-constructor SD, noise_sd=median within-car-season SD, N=(noise/field)^2). Read both and confirm equivalence — this is the load-bearing fidelity check.
- holdout.py split is deterministic across runs, documented, and leaves computable held-out car-seasons (>=2 held-out weekends per trusted car-season).
- gate_spec.py encodes F1/F2/F3 HONESTLY: (F1) an over-shrinker (constant-per-car-season) must FAIL the signal-preservation guard — verify the test proves this, and that the guard scores OUT-OF-SAMPLE residual around a train-fit trajectory, NOT self-dispersion; (F2) floor recomputed on the SAME held-out weekends paired per car-season, not vs the full-sample 624 table; (F3) >=7/11, car-season bootstrap resampling unit, fixed seed, tie = not-a-beat.
- frame.py loads faithfully from the absolute path; no evo import in the package; no data/*.db staged.

## Allowed Scope
`src/physics/weekend_state/*.py`, `tests/unit/physics/weekend_state/*.py`.

## Specific Exclusions
No model layers built here (g2-g5). Estimator/evo/config untouched.

## Constraints (each a review check)
- `constraint:physics_region_no_evo_import` — confirm via import grep, not substring.
- DB read from absolute main path (worktree lacks it); no `data/*.db` staged/committed.
- Python is `py`.

## Map Anchors (inbound)
- Structural: `src/physics/weekend_state/` (NEW); `data/physics_estimates.db:session_estimates`.
- Capability: x4 floor reproduced as reusable column-parameterizable harness.
- Constraints: no evo import; no DB commit.
- Decision: DC3 — split frozen before any layer.
- Evidence: 624 table reproduced within tolerance; over-shrinker fails F1 guard.

## Evidence Produced
`py -m pytest tests/unit/physics/weekend_state/test_floor_reproduction.py tests/unit/physics/weekend_state/test_holdout_split.py tests/unit/physics/weekend_state/test_gate_spec.py -q` → 25 passed (commander re-ran: 25 passed). Reproduced-vs-624 table in the implementer result.

## Suggested Model Tier
Stronger — the metric fidelity + un-gameable gate spec are the whole run's validity foundation; a rubber-stamp here poisons every later gate.

## Stop Conditions
BLOCK if: floor.py diverges from x4's logic (not just numerically close by luck), the F1 guard does not actually punish over-shrinkage, the split is non-deterministic, an evo import exists, or a data/*.db is staged.

## Return Format
Return REVIEW_RESULT to `.agent-work/wave4-626/g1-reviewer-result.md`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
