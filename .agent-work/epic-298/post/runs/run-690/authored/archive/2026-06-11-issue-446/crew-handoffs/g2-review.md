# Reviewer Handoff

## Gate
g2 — Offline loaders + strawman candidate + runner (review)

## What Was Implemented
Four new modules in `src/preprocessing/trajectory_grading/`: `offline_loader.py` (raw cache
streams), `db_truth_loader.py` (read-only sqlite URI for sector splits), `strawman_candidate.py`
(wraps merged get_telemetry — the deliberate artifact under study, naive flat covariance),
`runner.py` (ties candidate+truth → g1 primitives → JSON report). Integration test
`tests/integration/test_trajectory_grading_runner.py` (19 tests, 2023 Belgium Q). Commit 3aa7c14.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-446
git show 3aa7c14 -- src/ tests/
```
Implementer report: `.agent-work/issue-446/crew-handoffs/g2-implement-RESULT.md`.

## Task Statement
Add the IO + wiring layer: offline raw-stream loader, DB truth loader, strawman candidate, and a
runner that produces a g1 JSON report. Offline, no re-pull, raw streams only (strawman excepted),
truth from DB read-only. Full task: `.agent-work/issue-446/crew-handoffs/g2-implement.md`.

## Close Criteria (each a review check)
- `grep -rn get_telemetry src/preprocessing/trajectory_grading/` shows it ONLY in
  `strawman_candidate.py`, and that module's docstring justifies it.
- Offline loader reads `session.car_data`/`session.pos_data` only; raises a clear error (no fetch)
  if a session is uncached; uses `fastf1.Cache.enable_cache(<absolute cache path>)`.
- DB truth loader is genuinely READ-ONLY against the canonical DBs (verify the `file:...?mode=ro`
  URI is actually used and DatabaseManager's schema-write path is bypassed) — confirm no write to
  the canonical DB occurs.
- **Arc-length scaling correctness:** the implementer found FastF1 `pos_data` X/Y are in DECIMETRES
  and applied `_XY_TO_METRES=0.1`. VERIFY this is right (e.g. sanity-check that a derived lap
  arc-length is plausible for the circuit — Spa is ~7004 m; a lap's position-derived arc length
  should land in that ballpark, NOT ~70 km or ~700 m). A wrong scale would silently corrupt every
  downstream number. This is the highest-value check.
- Strawman derives s(t) from the merged product and carries a deliberately-naive (not honest)
  covariance; its docstring states it is the artifact under study.
- Runner produces a schema-valid g1 `GradingReport` and writes JSON; all three primitives produce
  output (two gates with verdicts, diagnostic with fitted offsets).
- `py -m pytest tests/integration/test_trajectory_grading_runner.py -q` GREEN.
- `py -m src.utils.simplification_limits` PASS on touched paths.
- No imports from `src/evo_predictor`, `src/latent_power`, `src/compound_prior`.

## Allowed Scope
`src/preprocessing/trajectory_grading/` (new modules), `tests/integration/`.

## Specific Exclusions
No re-pull/network; no get_telemetry outside strawman; no canonical-DB writes; no evo imports; no
touch to windowed_estimator/physics; no estimator logic. Flag if any were touched.

## Constraints the Implementation Must Respect
- Raw streams only (strawman excepted). Offline cache only. Truth from DB read-only.
- Physics-region isolation. Absolute paths for cache + DBs.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing.trajectory_grading`; `struct:fastf1_api` (offline cache);
  `struct:sqlite_db` (lap_times truth); `struct:data` (DatabaseManager).
- **Capability:** trajectory grading — end-to-end wiring + strawman.
- **Constraints/assumptions:** DB-only (Phase-0 cache exception); physics-region-isolation;
  pre-ruling 2 (raw only; strawman exception).
- **Evidence expectations:** read-only/no-repull (offline load logs "Using cached data", no DB
  writes); end-to-end run on a real cached session.

## Evidence Produced
- `py -m pytest tests/integration/test_trajectory_grading_runner.py -q` → 19 passed.
- `py -m src.utils.simplification_limits ...` → PASS (11 files).
- `grep get_telemetry` → confined to strawman_candidate.py.
Re-run all three; spot-check the arc-length scaling sanity yourself.

## Suggested Model Tier
stronger — reason: the decimetre scaling, read-only-DB correctness, and raw-vs-merged discipline
are silent-corruption traps.

## Stop Conditions
Return BLOCK if: the diff can't be accessed; get_telemetry leaks outside the strawman; the loader
re-pulls or the DB loader writes the canonical DB; the arc-length scale is wrong/unjustified;
evidence is unverifiable. Otherwise APPROVE.

## Return Format
Return REVIEW_RESULT to `.agent-work/issue-446/crew-handoffs/g2-review-RESULT.md`: VERDICT (exactly
APPROVE or BLOCK), per-check findings (especially the arc-length scaling sanity outcome), blockers,
out-of-scope observations, workflow feedback.
