# REVIEW_RESULT — g1 (shared utilization core)

Verdict: **APPROVE**

## Independent verification
- Re-ran `py -m pytest tests/unit/test_utilization.py -q` → 25 passed.
- Re-ran `py -m src.utils.simplification_limits --paths ...` → PASS (2 files); checker enforces real metrics (non-vacuous).
- Scope confirmed: only `src/utils/utilization.py`, `tests/unit/test_utilization.py`, `pyproject.toml` (1 line).

## Contracts verified non-vacuous
- Mapping exact at cores=8 (1,1 / 4,2 / 7,1); invariant workers*threads<=cores re-derived for cores 1..16.
- cores=1 clamp implemented correctly (utilization.py:146-157), provably inert at cores>=2.
- RAM cap binds + logs once with before/after (only when binding); floors to 1.
- physical_cores=None fallback chain correct.
- Invalid level + mem<=0 ValueErrors name field/expected/actual.
- Input-order reassembly proven via inverted completion order test.
- n_workers==1 in-process path proven via exploding-pool sentinel monkeypatch.
- fail_fast wraps first error as JobExecutionError(index+repr), pool closed; live probe ~4.5s no deadlock.
- Imports without torch; init_worker module-level/picklable; no F1 specifics; no module-level mutable state; logging not print.

## Out-of-scope observations (non-blocking, not filed)
- fail_fast docstring says "aborts" but in-flight siblings finish (shutdown waits) — wording nuance, behavior correct/orphan-free.
- os.cpu_count() or 1 final fallback rung not directly unit-tested (trivially correct; first two rungs covered).
