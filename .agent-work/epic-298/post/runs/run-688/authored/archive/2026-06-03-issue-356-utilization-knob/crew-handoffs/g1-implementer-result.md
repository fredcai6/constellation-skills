# IMPLEMENTER_RESULT — g1 (shared utilization core)

Status: complete. Commander-confirmed the cores=1 clamp decision (invariant wins; no effect at cores>=2).

## Files changed
- `src/utils/utilization.py` (new) — UTILIZATION_LEVELS, frozen ResourcePlan, resolve_resource_plan
  (per-level mapping, RAM auto-cap logged when binding, invalid-level ValueError, n_workers*threads<=cores
  invariant with a threads clamp only at the degenerate cores=1 balanced case), module-level init_worker
  (4 thread env vars + guarded torch.set_num_threads + best-effort psutil OS priority), run_jobs
  (n_workers==1 in-process short-circuit; multi-worker ProcessPoolExecutor with future->index reassembly to
  INPUT order; on_complete in completion order; fail_fast wraps first error as JobExecutionError with job
  index+truncated repr after pool teardown).
- `tests/unit/test_utilization.py` (new) — 25 tests.
- `pyproject.toml` — added `psutil>=5.9.0` to runtime dependencies (line 68).

## Test mode: TDD satisfied
- RED: suite written first; failed with ImportError (module absent) — failed for the right reason.
- GREEN: `25 passed in 5.62s`.
- Refactor while green: helper extraction (_run_in_pool/_run_in_process/_apply_ram_cap/_set_os_priority).

## Evidence
- `py -m pytest tests/unit/test_utilization.py -q` → 25 passed.
- `py -m src.utils.simplification_limits --paths src/utils/utilization.py tests/unit/test_utilization.py` → PASS (2 files).
- Imports cleanly with torch forced absent (init_worker OK without torch).

## Surfaced decision (Commander-confirmed)
- cores=1 balanced: mapping (1,2) would violate workers*threads<=cores; clamped threads to 1 to preserve the
  invariant. No effect at cores>=2 (cores=8: background 1x1, balanced 4x2, max 7x1 unchanged). CONFIRMED.

## Assumptions
- psutil>=5.9.0 minimum (modern API used). logger kwarg reserved; module logs via getLogger(__name__).
- fail_fast=False re-raises the original error unwrapped, pool drains via `with`.

## Out-of-scope observations
- None beyond tc1 (resolved/confirmed above).
