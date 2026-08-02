# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement` (Implementer Handoff — G2 Robustness fix)

## Completed slice
Convert the Saudi Arabia 2023 Q DEV empty-speed-stream crash into a clean typed
`no_speed_stream` skip. Implemented two guard sites, one typed-raise defense-in-depth,
a stale comment fix, and test updates. TDD: red tests written first, then guards.

## Scope
**Files changed:**
- `src/physics/session_fit.py` — early guard + ValueError mapping refactor
- `src/preprocessing/trajectory/calibration.py` — typed guard in `if windows:` block
- `src/physics/fit_store.py` — stale `fit_status` comment updated
- `tests/unit/physics/test_calibration_robustness.py` — new `TestNoSpeedStream` class (2 tests) + `import pandas as pd`
- `tests/unit/physics/test_475_validation_breadth.py` — `no_speed_stream` added to 3 `valid_statuses` sets

**Specific exclusions touched:** no — no_accel_samples semantics untouched; no successful-fit numeric path changed; no new statuses beyond no_speed_stream; fit store not rebuilt.

## Behavior changed
**yes** — `fit_driver(session, "DEV", ...)` on Saudi Arabia 2023 Q now returns
`FitRecord(fit_status="no_speed_stream")` instead of propagating
`ValueError: zero-size array to reduction operation minimum which has no identity`.

## Map Impact

- **Structural anchors touched:**
  - `session_fit.py fit_driver` (~line 237): primary early guard added after `driver_streams()` call — `if len(spd_d["t"]) == 0: return _err("no_speed_stream")`
  - `session_fit.py fit_driver` (except ValueError block): ValueError mapping updated from single-prefix to tuple-startswith `msg.startswith(("no_accel_samples", "no_speed_stream"))` + `msg.split(":")[0]` for status extraction; maintains complexity at 19 (baseline 18 + 1 new guard branch, net neutral on mapping branch by using tuple form)
  - `calibration.py calibrate_session_hp` (`if windows:` block, line ~877): typed guard added before `tc.min()` call — `if len(tc) < 1: raise ValueError("no_speed_stream: ...")` patterned after existing `no_accel_samples` raise at line 899
  - `fit_store.py FitRecord.fit_status` (line 34): comment now lists full set `# "ok" | "error" | "no_laps" | "no_accel_samples" | "no_speed_stream"`
- **Capabilities added/changed/affected:** per-session physics fit now handles empty-speed-stream drivers cleanly; typed-skip taxonomy extended with `no_speed_stream` reason; the 421 previously-ok fits' numeric paths unaffected (guard fires before any computation)
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honored (no evo imports added); `simplification_limits` — no new violations introduced (3 pre-existing violations unchanged: `fit_driver function_lines`, `fit_session_full function_lines`, `calibration.py file_lines`); cyclomatic complexity held at 19 (within `<20` limit) via tuple-startswith pattern
- **Decision candidates / resolved decisions:** typed-skip taxonomy ratified at decide-fix (2026-06-28); `msg.split(":")[0]` for status extraction from ValueError message is a local convention matching the `"prefix: detail"` message format — not a new decision
- **Claims/evidence produced:** Saudi Arabia 2023 Q DEV repro prints `no_speed_stream`; `test_calibration_robustness.py::TestNoSpeedStream` (2 tests) green; full unit suite 755 passed, 52 skipped, 0 failed

## Test mode
**Required:** test-first (TDD required per handoff)
**Satisfied:** yes — both new tests written RED and confirmed failing before any implementation change; then guards added to turn them GREEN; all 13 `test_calibration_robustness.py` tests pass; full unit suite green

## Evidence

```bash
py -m pytest tests/unit/physics tests/unit/preprocessing -q
```

**Result:** 755 passed, 52 skipped, 9 warnings in 1254.56s (0:20:54) — GREEN

```bash
py -m src.utils.simplification_limits --paths src/physics/session_fit.py src/preprocessing/trajectory/calibration.py
```

**Result:** FAIL (3 violations, 2 files checked) — all 3 are pre-existing (same as baseline):
- `src/physics/session_fit.py fit_driver: function_lines=120 (limit: <100)` (pre-existing)
- `src/physics/session_fit.py fit_session_full: function_lines=134 (limit: <100)` (pre-existing)
- `src/preprocessing/trajectory/calibration.py: file_lines=1203 (limit: <1000)` (pre-existing)
No new violations introduced. Cyclomatic complexity: baseline 18, final 19 (< 20 limit).

```bash
py -c "from src.physics.session_fit import load_quali_session, fit_driver; s,rho,_=load_quali_session(2023,'Saudi Arabia','Q'); r=fit_driver(s,'DEV',year=2023,gp_name='Saudi Arabia',round_idx=2,session_type='Q',constructor='AlphaTauri',rho=rho); print(r.fit_status)"
```

**Result:** `no_speed_stream` — PASS

## TDD evidence, if required

- **Failing tests observed:**
  ```
  FAILED test_calibration_robustness.py::TestNoSpeedStream::test_calibrate_session_hp_empty_tc_raises_no_speed_stream
  AssertionError: Expected ValueError starting with 'no_speed_stream', got: 'zero-size array to reduction operation minimum which has no identity'

  FAILED test_calibration_robustness.py::TestNoSpeedStream::test_fit_driver_empty_speed_stream_returns_no_speed_stream
  AssertionError: Expected fit_status='no_speed_stream', got 'error' (error='zero-size array...')
  ```
- **Passing tests observed:** both pass after implementation; full `test_calibration_robustness.py` (13 tests) green
- **Refactor while green:** yes — ValueError mapping refactored from two separate `if` blocks to tuple-startswith to reduce cyclomatic complexity; tests remained green throughout

## Docs/contracts touched
- `src/physics/fit_store.py` line 34 comment (inline doc) — updated to list full status set

## Assumptions
- `msg.split(":")[0]` correctly extracts the status prefix because all typed-skip ValueError messages follow the `"prefix: detail"` convention (verified in both `no_accel_samples` at calibration.py:899 and the new `no_speed_stream` raise)
- The `driver_streams` import inside `fit_driver` is from `src.preprocessing.trajectory.loaders`; patching at the source module level works for the mock test because the local `from ... import` in the function body looks up the name in the module at call time
- Pre-existing `simplification_limits` violations are a baseline condition not introduced by this change; the project rule "clean on touched paths" is interpreted as "no new violations introduced"

## Stop conditions hit
- None — implementation matched the ratified design exactly

## Out-of-scope observations
- `fit_session_full` at line ~386 has a symmetric `driver_streams` call and also processes speed data; it does NOT have an early no_speed_stream guard. The handoff scope is `fit_driver` only, so this is left as-is. If `fit_session_full` were called on Saudi Arabia 2023 Q DEV it would likely crash similarly — triage candidate for a follow-up.
- `simplification_limits` reports 3 pre-existing violations; the `function_lines` violations in `fit_driver` and `fit_session_full` suggest both functions are candidates for eventual decomposition (outside scope).

## Workflow Feedback

- **Handoff gaps:** The Map Anchors stated `calibration.py:877-879` for the guard location but the actual `if windows:` block starts at line 877 with `tp_min,tp_max = tp.min(),tp.max()` and `tc_min,tc_max = tc.min(),tc.max()` at lines 878-879. The instruction said to add the guard "BEFORE line 878" — this was unambiguous once I read the source. The position-stream guard for `len(tp) < 1` was mentioned as "a sensible typed raise" in the Map Anchors but not listed as a required change in Close Criteria. I added it (matching the tc guard pattern) as the logical complement; it's a trivial safe addition.
- **Context rediscovered:** The `driver_num` and `driver_streams` functions are imported locally inside `fit_driver` (not at module top level), so `mock.patch("src.physics.session_fit.driver_num")` fails with AttributeError. Needed to patch at `src.preprocessing.trajectory.loaders.driver_num`. This wasn't mentioned in the handoff. Took one failed run to discover.
- **Cyclomatic complexity wall:** The handoff didn't flag that adding the early guard would push `fit_driver` from complexity 18 to 19, and that the naive two-separate-if ValueError mapping would push it to 20 (hitting the `< 20` limit). Required an iterative refactor of the ValueError mapping to use `startswith(tuple)` which counts as 1 branch instead of 2. Worth noting the project's cyclomatic complexity limit is strict.
- **Instructions improvised around:** The engine checklist reference (`checklist-engine.md`) was not found at the skill path — drove the plan directly from the template JSON and skill prose. The plan JSON was written but the engine script was not available; drove steps manually as instructed.
- **What would have made this easier:** Include the baseline cyclomatic complexity of key functions in the Map Anchors when the change touches a function already near a limit. A note like "fit_driver baseline complexity=18, limit=<20, budget=1 new branch" would have prevented the iteration.

## Return status
`complete`

---

## COMMANDER ADDENDUM — Rework 1 verified (fit_session_full guard, 2026-06-28)

Scope was extended by human decision: fold the same empty-speed-stream protection
into the sibling `fit_session_full`. The crew applied the code change but did NOT
update the body of this result file (the "Out-of-scope: fit_session_full left as-is"
note and the "13 tests" count above are now STALE). Commander ground-truthed the
actual tree (verify-claimed-side-effects):

- `src/physics/session_fit.py` `fit_session_full` now has, right after
  `driver_streams`: `if len(spd_d["t"]) == 0: logger.debug(...); return None`
  (returns None — correct: fit_session_full returns `Optional[SessionFitFull]`, not
  a FitRecord). VERIFIED present at lines 400-402.
- New test `test_fit_session_full_empty_speed_stream_returns_none` added to
  `tests/unit/physics/test_calibration_robustness.py` (line 348). VERIFIED present.
- `py -m pytest tests/unit/physics/test_calibration_robustness.py -q` →
  **14 passed** (was 13; +1 for the new fit_session_full test). VERIFIED by commander.

The CODE is the ground truth; this addendum reconciles the stale body. Re-review
(g2 reviewer attempt-2) covers the full updated diff.
