# Review Result

## Assigned Gate
`g2-review` — Issue #495 fit-robustness: no_speed_stream typed-skip

## Result
`APPROVE`

---

## Handoff compliance

All eight close criteria independently verified and passed. The change does exactly what the handoff asked: converts the Saudi Arabia 2023 Q DEV empty-speed-stream crash into a clean typed `no_speed_stream` skip, with two guard sites (fit_driver early guard + calibrate_session_hp defense-in-depth), a ValueError mapping refactor, stale comment update, and test updates. No close criterion is unmet.

---

## Scope drift

None. Changed files confirmed by `git diff --name-only`:
- `src/physics/session_fit.py`
- `src/preprocessing/trajectory/calibration.py`
- `src/physics/fit_store.py`
- `tests/unit/physics/test_calibration_robustness.py`
- `tests/unit/physics/test_475_validation_breadth.py`

All five are within the allowed scope. No evo imports added. No fit-quality floor. No store rebuild. No successful-fit numeric paths changed.

---

## Evidence verdict

All evidence independently reproduced:

**Check r4a — no_accel_samples path not regressed:**
Independent Python invocation confirmed `ValueError("no_accel_samples: ...")` message, `msg.split(":")[0]` yields `'no_accel_samples'`, `msg.startswith(("no_accel_samples","no_speed_stream"))` is `True`. The refactor from two separate `if` blocks to tuple-startswith preserves the existing mapping. PASS.

```
ValueError message: 'no_accel_samples: fit_stint_hp could not find valid HPs (too few samples or degenerate window)'
Split prefix: 'no_accel_samples'
Starts with no_accel_samples: True
PASS: no_accel_samples path still works
```

**Check r4b — Saudi DEV live repro:**
```
fit_status='no_speed_stream'
error=None
PASS: Saudi DEV returns no_speed_stream
```
`load_quali_session(2023, 'Saudi Arabia', 'Q')` + `fit_driver(s, 'DEV', ...)` returns `fit_status='no_speed_stream'` with no exception raised.

**Check r4c — full unit suite green:**
```
755 passed, 52 skipped, 9 warnings in 1106.47s (0:18:26)
```
Independent run of `py -m pytest tests/unit/physics tests/unit/preprocessing -q`. Zero failures. Matches implementer-reported result.

Physics-only subset also confirmed:
```
664 passed, 52 skipped, 9 warnings in 368.45s (0:06:08)
```

**Check r4d — spot-check previously-ok fits:**
Two cases independently verified via live `fit_driver` calls:
- Bahrain 2023 Q ALO: `fit_status='ok'`, `best_lap_s=90.336`, `n_flying_laps=5`
- Japan 2023 Q PIA: `fit_status='ok'`, `best_lap_s=89.458`, `n_flying_laps=4`

Both return `ok` with realistic numeric values. No drift.

**Check r4e — `flying_windows or None` behavior-equivalent:**
```
empty list: old=None, new=None, equal=True
non-empty: old=[(10.0, 80.0)], new=[(10.0, 80.0)], equal=True
None: old=None, new=None, equal=True
```
All three cases match. The simplification is strictly equivalent.

**Check r4f — calibration.py guard naming:**
The `len(tp) < 1` branch raising `"no_speed_stream: empty position stream"` is a naming nit only. Position-empty is not reachable via the Saudi DEV path (the primary guard in `fit_driver` fires on empty `spd_d["t"]` before `calibrate_session_hp` is called). The shared `no_speed_stream` bucket routes to the same clean-null handling path. Acceptable defense-in-depth per handoff sanction. Flagged as out-of-scope triage candidate (see below).

**Check r4g — simplification_limits:**
```
FAIL (3 violations, 2 files checked)
src/physics/session_fit.py fit_driver: function_lines=120 (limit: <100)
src/physics/session_fit.py fit_session_full: function_lines=134 (limit: <100)
src/preprocessing/trajectory/calibration.py: file_lines=1203 (limit: <1000)
```
All 3 are pre-existing. No new violations introduced. Cyclomatic complexity held at 19 (< 20 limit) by the tuple-startswith refactor.

**Check r4h — scope exclusions:**
Confirmed by diff review: no new statuses beyond `no_speed_stream`, no sample-floor/min-lap guard, `no_accel_samples` semantics unchanged, `constraint:physics_region_no_evo_import` honored.

**test_calibration_robustness.py — both new tests pass:**
```
TestNoSpeedStream::test_calibrate_session_hp_empty_tc_raises_no_speed_stream PASSED
TestNoSpeedStream::test_fit_driver_empty_speed_stream_returns_no_speed_stream PASSED
```
All 13 tests in the file pass.

---

## Code/doc quality

Minimal, correct, well-scoped. The tuple-startswith + `msg.split(":")[0]` pattern is a clean generalization of the original single-prefix check and preserves cyclomatic budget. Tests are behavior-focused with clear docstrings. The `flying_windows or None` simplification is strictly equivalent and more idiomatic. The `fit_store.py` comment update is accurate and overdue. No doc artifacts created; no speculative code added.

---

## Map impact verdict

- **Evidence supports claimed change:** Yes. Saudi DEV live repro confirms the crash-to-typed-skip transition. Full suite green confirms no regression. TDD evidence (red→green) present in implementer result and reproducible.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored. `simplification_limits` complexity limit (< 20) maintained at 19 via the tuple-startswith refactor. Test-led requirement met.
- **Notes match the diff:** Yes. Structural anchor line numbers in Map Impact are accurate within a few lines (normal for line-number drift). Capability claim ("per-session physics fit now handles empty-speed-stream drivers cleanly") is demonstrated. Status taxonomy extension documented.
- **Decision candidates surfaced:** The `msg.split(":")[0]` convention for status extraction was correctly identified as a local pattern (not a new decision). Typed-skip taxonomy ratified at decide-fix. No outstanding decision candidates.
- **Durable context routed:** Two triage candidates identified (see below). Implementer surfaced `fit_session_full` gap as an out-of-scope observation.

---

## Reconciliation check

No divergence from recorded architecture. `fit_store.py` comment brought into sync with actual status taxonomy. The `no_speed_stream` status is an extension of the existing typed-skip taxonomy (alongside `no_accel_samples`), not a structural change. No structural map update required for this local robustness fix.

---

## Blockers

None.

---

## Out-of-scope observations

1. **`fit_session_full` has no no_speed_stream guard** (line ~386): symmetric `driver_streams` call processes speed data without an early empty-speed-stream guard. If called on Saudi Arabia 2023 Q DEV it would crash similarly. Out of scope for this fix but a latent crash risk. Triage candidate for follow-up.

2. **`len(tp) < 1` branch naming nit**: `calibration.py` raises `"no_speed_stream: empty position stream"` for a position-empty condition. Semantically imprecise — position-empty is distinct from speed-empty. Not a blocker (reachability is very low; routes to the same clean-null path). Triage candidate for future taxonomy cleanup if a `no_position_stream` status ever makes sense.

---

## Workflow Feedback

- **Handoff gaps:** `checklist-engine.md` referenced in the skill was not found at `C:/Users/fredc/.claude/skills/constellation-reviewer/references/checklist-engine.md` — drove the survey manually from the template JSON and skill prose. The engine script at `scripts/checklist_engine.py` exists but its reference doc is absent from the installed skill. This is a skill installation issue, not a handoff issue.

- **Context rediscovered:** The `simplification_limits` module requires `--paths` flag (not positional args as shown in the handoff's `py -m src.utils.simplification_limits src/physics/...`). This caused a one-call failure before switching to `--paths`. The handoff should use the correct flag syntax.

- **Instructions improvised around:** The survey template has a flat 6-item structure (r0–r5). The 8 close-criteria checks from the handoff were appended as r4a–r4h sub-items under r4-quality. This is the natural mapping but the template doesn't have a sub-item mechanism — treated them as top-level items in the JSON under the same naming convention.

- **What would have made this easier:** Include the correct `simplification_limits` invocation syntax in the handoff's "verification commands" section (use `--paths`). Also: confirm the checklist-engine.md reference file is present in the installed skill.

---

## Return status
`complete`
