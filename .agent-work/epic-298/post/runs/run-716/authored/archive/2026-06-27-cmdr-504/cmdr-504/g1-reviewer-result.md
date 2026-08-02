## Verdict
APPROVE

## Summary
All 9 close criteria verified. The mechanical split of smoother.py (1253→999 lines) into 4 private helper modules is clean: public API is preserved, behavior is unchanged, the E4-nesting guarantee is intact (byte-identical `_precompute_steps`), circular import is handled correctly via the late import at line 999, and no physics or test files were touched.

## Findings
None.

Detailed evidence per criterion:

1. **Public API preserved** — `py -c "from src.preprocessing.trajectory.smoother import AccelObs, StintSmoother, NSStintSmoother, build_roughness, driver_series, banded_gap; print('API OK')"` → `API OK`

2. **No behavior change** — `_fit_frozen_frame` and `_fit_standard` contain the exact logic from the original `if lin_vel_frozen is not None:` / `else:` branches. The only structural difference is `lin_vel = np.asarray(lin_vel_frozen, float)` moved one line up into `fit()` before the dispatch call — semantically identical.

3. **No src/physics touch** — `git diff --name-only HEAD -- src/physics/` returns empty.

4. **No shims or dual paths** — new modules are canonical; smoother.py re-exports via top-level imports. No redundant code paths found.

5. **Circular import handled correctly** — `from src.preprocessing.trajectory._ns_smoother import NSStintSmoother  # noqa: E402` is at line 999 (verified last line of a 999-line file). `_ns_smoother.py` imports `StintSmoother` directly from `smoother` (not a TYPE_CHECKING guard).

6. **E4-nesting guarantee intact** — `_precompute_steps` in `_ns_smoother.py` (lines 69–127) is byte-identical to the removed block: `order==3` path uses `_block6(Phi_x, Phi_x)` and `_block6(r * Q0_x, r * Q0_x)` with `Qs_nominal.append(_block6(Q0_x, Q0_x))` as required.

7. **`_validate_smoother_params` is correct** — all 9 validation ifs present at top of smoother.py (lines 29–59), same order, same error messages as the original `__init__` block.

8. **`fit` dispatch correct** — dispatches to `_fit_frozen_frame` / `_fit_standard`; `_n_iter_done` and `_last_lin_dmax` are set inside each helper (not in `fit` itself); `self._n_iter_done = it + 1` removed from fit().

9. **No test files touched** — `git diff --name-only HEAD -- tests/` returns empty. `__init__.py` also unmodified.

Cross-import constraints all clean:
- `_accel_obs.py` — imports only `dataclasses`, `numpy`
- `_roughness.py` — imports only `numpy`
- `_gap_metric.py` — imports only `typing.Any`, `numpy`
- `_ns_smoother.py` — imports from `dynamics` and `smoother` only (no peer helper imports)

## Out-of-Scope Observations
None worth triaging.

## Workflow Feedback
Handoff was clear and complete. Criteria were specific and verifiable. The only minor friction: `git diff --name-only HEAD <path>` with a directory path requires the `--` separator on this platform (PowerShell/bash gave exit 128 otherwise) — the handoff could note `git diff --name-only HEAD -- src/physics/` form. Not a blocker.
