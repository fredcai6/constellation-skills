# Reviewer Handoff

## Gate
g1 — Shared utilization core

## What Was Implemented
New generic resource-policy module `src/utils/utilization.py` (UTILIZATION_LEVELS, frozen ResourcePlan,
resolve_resource_plan, init_worker, run_jobs), 25-test `tests/unit/test_utilization.py`, and a `psutil>=5.9.0`
runtime dep in `pyproject.toml`. Built test-first (TDD).

## How to Inspect the Diff
Files are new/untracked in the worktree (branch claude/recursing-hofstadter-5c4e0d). Inspect by:
- Read `src/utils/utilization.py` and `tests/unit/test_utilization.py` in full.
- `git diff -- pyproject.toml` (the psutil dep line).
- `git status --porcelain` to confirm ONLY the three allowed files changed (the `.agent-work/` engine plan
  file is workflow state, not part of the change).

## Task Statement
Create an F1-agnostic core mapping a utilization level (background/balanced/max) to a
(n_workers, threads_per_worker, priority) plan and running jobs through a ProcessPoolExecutor — with an
in-process short-circuit at 1 worker and input-order result reassembly. Full handoff:
`.agent-work/issue-356-utilization-knob/crew-handoffs/g1-implementer-handoff.md`.

## Close Criteria (each a review check)
- Level→plan mapping correct on a stubbed core count: at cores=8 → background (1,1,below_normal), balanced (4,2,normal), max (7,1,normal).
- `n_workers * threads_per_worker <= cores` invariant holds for every level/core count (including the degenerate cores=1).
- RAM cap binds and logs once when it lowers n_workers (e.g. available_mem_gb=2, mem_per_worker_gb=1, max → 2 workers).
- `physical_cores=None` falls back to `psutil.cpu_count(logical=False) or os.cpu_count() or 1`.
- Invalid level → `ValueError` naming field, expected set, actual.
- `run_jobs` reassembles results in INPUT order (not completion order) under multi-worker execution.
- `n_workers==1` takes the in-process path — no ProcessPoolExecutor constructed.
- A raising job with `fail_fast=True` surfaces wrapped with the job's identity and the pool is closed (no deadlock/orphan).
- Module imports cleanly WITHOUT torch (torch import lazy/guarded).
- `init_worker` is module-level (picklable initializer).

## Allowed Scope
`src/utils/utilization.py`, `tests/unit/test_utilization.py`, `pyproject.toml` only.

## Specific Exclusions (flag if touched)
No `gold_cycle`, `sampled_backtest`, `run.py`, or `scripts/` changes. No new user-facing config/CLI knob.

## Constraints the Implementation Must Respect (each a review check)
- Nothing F1-specific in the module (no DB/calendar/evo imports).
- No mutable module-level runtime state; no impure caches.
- Library logging via `logging.getLogger(__name__)`; no `print()`.
- Validation messages name field, expectation, actual.
- COMMANDER-SANCTIONED DECISION (do not block on this, but verify it is implemented correctly): at the
  degenerate cores=1 balanced case the mapping (1,2) would violate the invariant, so threads_per_worker is
  clamped to keep `workers*threads<=cores`. This is the confirmed resolution; the invariant is the hard
  guarantee. Verify it has zero effect at cores>=2.

## Evidence Produced
- `py -m pytest tests/unit/test_utilization.py -q` → 25 passed (per IMPLEMENTER_RESULT).
- `py -m src.utils.simplification_limits --paths src/utils/utilization.py tests/unit/test_utilization.py` → PASS.
- Re-run both yourself to confirm; spot-check that tests genuinely assert the contracts (not vacuous).
Full result: `.agent-work/issue-356-utilization-knob/crew-handoffs/g1-implementer-result.md`.

## Suggested Model Tier
stronger — reason: concurrency correctness (spawn, ordering, fail-fast) is subtle and everything downstream depends on it; verify the tests actually exercise the ordering and in-process contracts rather than asserting trivially.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, evidence is absent/unverifiable, scope was exceeded, a
required contract is unmet, or the tests are vacuous.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
