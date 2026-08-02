# Reviewer Handoff

## Gate
`g1` — Split smoother.py: review

## Task Statement
Review a mechanical refactor that split `src/preprocessing/trajectory/smoother.py` from 1253 lines into 4 new private helper modules and reduced smoother.py to 999 lines. The refactor adds 3 internal private methods to fix function-level complexity metrics.

## How to Inspect the Diff

Files modified/created in `C:/Programs/f1Brainz-worktrees/509-504/src/preprocessing/trajectory/`:
- `smoother.py` — was 1253 lines, now 999 (MODIFIED)
- `_accel_obs.py` — NEW (AccelObs dataclass)
- `_roughness.py` — NEW (driver_series, build_roughness)
- `_gap_metric.py` — NEW (banded_gap, _banded_gap_bands)
- `_ns_smoother.py` — NEW (NSStintSmoother class)

Compare smoother.py against the branch base to see the diff. Run from `C:/Programs/f1Brainz-worktrees/509-504`:

```bash
git diff HEAD src/preprocessing/trajectory/smoother.py
git diff HEAD src/preprocessing/trajectory/
```

## Close Criteria
Verify all of the following:

1. **Public API preserved**: `AccelObs, StintSmoother, NSStintSmoother, build_roughness, driver_series, banded_gap` all importable from `src.preprocessing.trajectory.smoother` — no name missing, no import error
2. **No behavior change**: `_fit_frozen_frame` and `_fit_standard` contain the exact code from the original `if lin_vel_frozen is not None:` and `else:` branches respectively — no logic, no variable names, no numerical constants changed
3. **No src/physics touch**: confirm no file under `src/physics/` was modified
4. **No shims or dual paths**: only ONE execution path for each functionality — the new modules are canonical, smoother.py re-exports via imports
5. **Circular import handled correctly**: `from src.preprocessing.trajectory._ns_smoother import NSStintSmoother  # noqa: E402` is at the VERY END of smoother.py (after StintSmoother is fully defined), and `_ns_smoother.py` imports `StintSmoother` from smoother (confirmed the late-import pattern, not a `TYPE_CHECKING` guard)
6. **E4-nesting guarantee intact**: The `NSStintSmoother._precompute_steps` in `_ns_smoother.py` is byte-identical to the original — the `order==3` path using `_block6(Phi_x, Phi_x)` and `_block6(Q0_x, Q0_x)` is preserved exactly
7. **`_validate_smoother_params` is correct**: contains the same 9 validation ifs from the original `__init__`, in the same order, with the same error messages
8. **`fit` dispatch is correct**: refactored `fit` calls `_fit_frozen_frame` when `lin_vel_frozen is not None`, else `_fit_standard`; `_n_iter_done` and `_last_lin_dmax` are set inside the helpers (not in `fit` itself)
9. **No test file touched**: confirm no files under `tests/` were modified

## Constraints
- Byte-identical Gaussian path must be preserved (E4-nesting validation depends on it)
- `__init__.py` must NOT have been modified
- The 4 new helper modules must NOT import from each other (except `_ns_smoother.py` imports from `smoother.py`)
- `_roughness.py` and `_gap_metric.py` must have zero imports from smoother.py or other trajectory modules

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing — src/preprocessing/trajectory/smoother.py` is the only target; subpackage self-contained
- **Capability:** `StintSmoother` Kalman-RTS + `NSStintSmoother` non-stationary — behavior unchanged; E4-nesting (byte-identical Gaussian path) intact
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; public API frozen; no shims
- **Decision anchors:** Circular import via late-import at end of smoother.py — verify this pattern is implemented, not a different workaround

## Evidence Produced
The implementer produced:
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/smoother.py` → PASS (1 files checked)
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/_accel_obs.py _roughness.py _gap_metric.py _ns_smoother.py` → PASS (4 files checked)
- All 91 unit tests in `tests/unit/preprocessing/trajectory/` passed (run in 3 batches due to runtime; combined 91 passed)
- Public API import check: `from src.preprocessing.trajectory.smoother import AccelObs, StintSmoother, NSStintSmoother, build_roughness, driver_series, banded_gap` → OK

## Return Format
Return REVIEW_RESULT:

```
## Verdict
APPROVE | BLOCK

## Summary
[2-3 lines of what was checked and found]

## Findings
[Any issues found: CRITICAL (blocks), MINOR (doesn't block)]
[If APPROVE: "None" or only MINOR items]

## Out-of-Scope Observations
[Anything noticed outside review scope — log as triage candidates]

## Workflow Feedback
[What in this handoff or workflow made the review harder than needed]
```
