# Implementer Handoff

## Gate
g6 — Determinism acceptance test + usage doc

## Task
Add the headline determinism acceptance test (byte-identity at a fixed thread count regardless of worker count,
exercising REAL gold-cycle training through run_jobs) and a concise usage doc for the `--utilization` knob.

## Protected Intent
This test is the guarantee the whole feature rests on: parallel output MUST equal sequential output at a fixed
`threads_per_worker`. It must fail meaningfully if that ever breaks (not pass vacuously).

## Test Mode
TDD-mindset: author the test so it would FAIL if results diverged across worker counts (e.g. sanity-check it
catches a deliberate perturbation during development), before relying on green.

## Close Criteria — the determinism test
- A test whose name contains `utilization_determinism` (so `pytest -k utilization_determinism` selects it).
  Place it in `tests/integration/` (real-data smoke), e.g. `tests/integration/test_utilization_determinism.py`.
- Exercises REAL training+backtest through `run_jobs` (the actual `run_train_backtest` worker), NOT mocks.
- Keep it BOUNDED: restrict to 1-2 trainable modules, 2 train years, `max_rounds_per_year=1`. (Build a small set
  of real `TrainBacktestJob`s via the G3 builders or directly; you do NOT need the full 12-module cycle.)
- Run the SAME jobs twice into SEPARATE output dirs:
  - Run A: background plan (`n_workers=1`, `threads_per_worker=1`) → in-process.
  - Run B: a forced multi-worker plan (`n_workers=2`, `threads_per_worker=1`).
- ASSERT byte-identity at fixed threads: the trained bundle artifacts (weights) are byte-identical between A and B
  (hash the bundle files), AND the returned results/rows/manifests match. Normalize any embedded timestamps/paths
  before comparing JSON.
- Guard with `pytest.mark.skipif` when the required `data/f1_data_<year>.db` files are absent (this project is
  local-first; the test runs locally where data exists, skips cleanly in data-less CI — state the skip reason).
- OPTIONAL secondary check (only if cheap/non-flaky): background (1×1) vs balanced-style (1 worker, `threads=2`)
  → metrics within a tight tolerance (the cross-thread-count guarantee). If torch threading makes this flaky,
  omit it and note why — the PRIMARY fixed-threads byte-identity assertion is what gates the feature.

## Close Criteria — usage doc
- Add a concise `--utilization` usage entry. Consult `docs/DOCUMENTATION.md` for where commands/usage belong; put it
  in the existing command/usage doc home (or the gold-cycle usage doc). Do NOT create a sprawling new doc.
- Cover: the three levels (background/balanced/max), the `workers × threads ≈ cores` mapping with the RAM auto-cap,
  that it is allowed in gold mode as a NON-POLICY hint (not recorded in applied_overrides / report), and the
  determinism guarantee (byte-identical at fixed threads; tolerance across thread counts).
- The `gold_defaults.toml` already has a comment and the CLI has `--help`; this doc ties it together for users.

## Allowed Scope
- New `tests/integration/test_utilization_determinism.py` (or similarly named).
- The chosen usage doc file (one doc).
- A tiny config/fixture helper if needed for the test (keep minimal; reuse existing patterns from
  `tests/integration/test_retro_delta_smoke.py` / `test_f1_data_test_db_smoke.py` if helpful).

## Specific Exclusions
- Do NOT modify the gold cycle / scripts / utilization.py production code (G1-G5 are done & committed). If the test
  reveals a real determinism defect, STOP and report it as a blocker (do not silently patch production here).
- Do NOT add `utilization` to the gold report schema.
- Do NOT update the architecture map (the Commander's reconcile step / Cartographer handles parallel_jobs.py +
  sampled_backtest_scoring.py map entries).

## Constraints
- Use `py`, not `python`.
- Deterministic seeds; bounded runtime; the test must be a real signal, not vacuous.
- `py -m src.utils.simplification_limits --paths <test + doc>` clean (no new violation).

## Required Evidence
- The determinism test PASSES locally (data present): paste the `pytest -k utilization_determinism` tail showing it
  RAN (not just skipped) and passed. If it can only skip in your environment, say so — but local data IS present.
- A note that you confirmed the test catches divergence (e.g. a temporary perturbation made it fail).
- `py -m src.utils.simplification_limits --paths <touched>` → clean.

## Verification Commands
```bash
py -m pytest -q -k utilization_determinism
py -m src.utils.simplification_limits --paths tests/integration/test_utilization_determinism.py
```

## Suggested Model Tier
stronger — reason: designing a faithful-yet-bounded real-training determinism test (separate output dirs, bundle
byte-comparison, timestamp normalization, skip guard) is subtle; a vacuous test would give false confidence.

## Authority
Decided (do not re-litigate): the test asserts fixed-threads byte-identity on the REAL pipeline, bounded to 1-2
modules/2 years/max_rounds=1, skipif data absent; primary assertion is byte-identity (cross-thread tolerance is
optional); one usage doc; no production code changes; no schema/map change here. You choose the exact fixture/config
construction and doc location.

## Stop Conditions
Stop and return (as a BLOCKER) if: the determinism test reveals a REAL divergence between worker counts at fixed
threads (that's a production defect for the Commander to route, not something to patch here); scope must be exceeded;
or evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied (incl. that the test catches
divergence), evidence (command tails showing the test RAN and passed), assumptions, stop conditions hit,
out-of-scope observations.
