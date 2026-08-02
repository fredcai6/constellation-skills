# Reviewer Handoff — G1 populate batch

## Gate
g1 (issue #511 W3 tyre-age capstone). Worktree `C:/Programs/f1Brainz-511`. Use `py`, never `python`.

## Survey State Location
Create your review survey at `.agent-work/511/g1-review/review.json` (NOT at the worktree root).

## What Was Implemented
New evo-free batch to populate `race_stint_estimates` from the W2 fit path:
- `src/physics/layer2/race_stint_batch.py` (discovery helpers + resumable, loss-proof population loop)
- `scripts/populate_race_stint_estimates.py` (thin CLI; supports a race subset AND a full-season run)
- `tests/unit/physics/layer2/test_race_stint_batch.py` (22 tests over pure helpers)
Smoke run (Bahrain + Australia 2023) wrote 106 ok rows to `C:/Programs/f1Brainz/data/race_stint_estimates.db`.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-511
git status
git diff --stat
git diff -- src/physics/layer2/race_stint_batch.py scripts/populate_race_stint_estimates.py tests/unit/physics/layer2/test_race_stint_batch.py
```
The IMPLEMENTER_RESULT is at `.agent-work/511/crew-handoffs/g1-implementer-result.md`.

## Task Statement
Build a resumable, loss-proof batch that, per (2023 race gp, driver), runs `load_race_stints` → `estimate_stint` → `record_from_stint_estimate` → `RaceStintStore.upsert`, skipping already-present PK rows via `RaceStintStore.has(...)` and storing `error_record(...)` on failures, with timestamped progress logging; plus a unit test over the pure helpers and a 2-race real-data smoke proof.

## Close Criteria (each a review check)
- `race_stint_batch.py` imports NO evo-region package (`evo_predictor`/`latent_power`/`compound_prior`) — confirm by reading imports, not just the implementer's assertion.
- Discovery enumerates 2023 race gp_names + drivers from the per-year DB via read-only sqlite.
- Resumability: a present PK is skipped via `RaceStintStore.has(...)` (verify the has()-args order matches the store seam: `has(year, gp_name, driver, stint_num, compound, session_type='R')`).
- Loss-proof: per-(gp,driver)/per-stint exceptions produce an `error_record(...)` (nothing dropped silently).
- Unit test exercises the pure helpers (discovery, skip, record assembly, error path) with synthetic inputs; 22/22 pass on your re-run.
- `simplification_limits` clean on the new src module + test (use `--paths`).
- No W2-module mutation (`session_race.py`/`stint_estimator.py`/`race_stint_store.py` and the quali path are untouched) — confirm via `git diff`.
- Smoke fits are non-degenerate: lateral fits present, finite, PSD covariance.

## Allowed Scope
The 3 new files only + writing `data/race_stint_estimates.db` rows.

## Specific Exclusions (flag if touched)
Any edit to `session_race.py`, `stint_estimator.py`, `race_stint_store.py`, quali-path modules, or any committed `.db`.

## Constraints the Implementation Must Respect (each a review check)
- `constraint:physics_region_no_evo_import`.
- DB/telemetry-store is the only data source; `py` not `python`.
- `lesson:worktree-untracked-data` — absolute main-checkout paths for DB access.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/race_stint_batch.py` (new component-leaf).
- **Capability:** `purpose:physics_estimation`.
- **Constraints:** `constraint:physics_region_no_evo_import`; `lesson:worktree-untracked-data`.
- **Evidence:** W2 inherited 889 clean 2023 stints — smoke re-confirms (g0,k) usable; covariance PSD/finite.

## Evidence Produced (re-verify; do not trust blind)
1. `py -m pytest tests/unit/physics/layer2/test_race_stint_batch.py -q` → 22 passed (re-run it).
2. `py -m src.utils.simplification_limits --paths src/physics/layer2/race_stint_batch.py tests/unit/physics/layer2/test_race_stint_batch.py` → PASS.
3. evo-free assertion → `evo-free ok`.
4. Smoke loader report: 106 rows, 106 ok / 0 error; lateral fit 102/106; lateral_g0 min 1.23 / median 2.03 / max 4.81; lateral_k min 0 / median 0.0015 / max 0.058; covariance finite 102/102, PSD 102/102; HARD 55 / SOFT 36 / MEDIUM 15.

## Reviewer note on the g0 plausibility guide
The handoff's "lateral g0 ≈ 1.0–1.6 g" guide was QUALIFYING-calibrated. Race stints sample low-speed corners where mechanical grip dominates and `b_aero·v²` is small, so g0 runs higher (median ~2.0, max ~4.8). This is EXPECTED and is NOT a defect — do NOT BLOCK on g0 exceeding 1.6. Block only on non-finite / non-PSD / pervasively-missing lateral fits, or on a real correctness/scope/constraint violation.

## Suggested Model Tier
Simple-bounded → moderate (plumbing correctness + import/scope discipline; re-run tests + read imports).

## Stop Conditions
Return BLOCK if: the diff is inaccessible, evidence cannot be reproduced, an evo-region import is present, a W2 module was mutated, or resumability/error-handling is broken.

## Return Format
Return REVIEW_RESULT to `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g1-reviewer-result.md`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, and a Workflow Feedback section.
