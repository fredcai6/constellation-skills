# Reviewer Handoff — G2 Robustness fix

## Gate
g2 (execute.json `g2-review`)

## Survey State Location
`.agent-work/issue-495-fit-robustness/g2-review/review.json`.

## What Was Implemented
A `no_speed_stream` typed-skip for the one remaining live fit crash (Saudi Arabia
2023 Q DEV, empty session-wide speed stream). Five files:
- `src/physics/session_fit.py` — early guard after `driver_streams`
  (`if len(spd_d["t"]) == 0: return _err("no_speed_stream")`); `except ValueError`
  mapping refactored to `msg.startswith(("no_accel_samples","no_speed_stream"))` →
  `_err(msg.split(":")[0], msg)`; plus a `flying_windows or None` simplification in
  two `calibrate_session_hp(...)` call sites (fit_driver + fit_session_full).
- `src/preprocessing/trajectory/calibration.py` — typed guard in the `if windows:`
  block before `tc.min()`: raises `ValueError("no_speed_stream: ...")` when
  `len(tc) < 1` (and `len(tp) < 1`).
- `src/physics/fit_store.py:34` — stale `fit_status` comment updated.
- `tests/unit/physics/test_calibration_robustness.py` — new `TestNoSpeedStream` (2 tests).
- `tests/unit/physics/test_475_validation_breadth.py` — `no_speed_stream` added to 3 valid_statuses sets.

## How to Inspect the Diff
```bash
git diff src/physics/session_fit.py src/preprocessing/trajectory/calibration.py src/physics/fit_store.py
git diff tests/unit/physics/test_calibration_robustness.py tests/unit/physics/test_475_validation_breadth.py
```

## Task Statement
Convert the Saudi-DEV empty-speed-stream crash into a clean typed `no_speed_stream`
skip, guarded at two sites, plus the stale-comment fix — per the human-ratified
decide-fix design. Crash→typed-skip only; NO fit-quality floor.

## REWORK 1 (re-review — added since attempt-1)
The human extended scope to fold the same protection into the sibling
`fit_session_full`. New since the first review:
- `src/physics/session_fit.py` `fit_session_full` (~line 400): early guard
  `if len(spd_d["t"]) == 0: logger.debug(...); return None` — note it returns
  **None** (fit_session_full returns `Optional[SessionFitFull]`, not a FitRecord),
  NOT `_err("no_speed_stream")`. Confirm this is correct and that an empty-speed
  session now returns None cleanly (not via the caught broad Exception).
- New test `test_fit_session_full_empty_speed_stream_returns_none`
  (`test_calibration_robustness.py`). Confirm it passes and asserts None-not-raise.
- Re-verify the WHOLE updated diff, not just the increment.

## Close Criteria (each a review check)
- **`no_accel_samples` path NOT regressed** by the `msg.split(":")[0]` refactor:
  confirm a `ValueError("no_accel_samples: ...")` still maps to
  `fit_status="no_accel_samples"` (run `test_calibration_robustness.py`).
- **`no_speed_stream` path works:** independently reproduce Saudi Arabia 2023 Q DEV
  → `fit_driver` returns `fit_status="no_speed_stream"` (no raised exception).
- **No regression:** independently run `py -m pytest tests/unit/physics
  tests/unit/preprocessing -q` and confirm green.
- **421 ok fits unaffected:** spot-check ≥1 previously-ok case (e.g. Bahrain ALO or
  Japan PIA) still returns `ok` with unchanged params (no numeric drift).
- **`flying_windows or None` is behavior-equivalent** to the prior
  `flying_windows if flying_windows else None` (empty list → None either way) — confirm.
- **calibration.py guard naming:** the `len(tp) < 1` branch raises a `no_speed_stream`
  message that says "empty position stream" — judge whether the shared
  `no_speed_stream` bucket for a position-empty case is acceptable (defense-in-depth,
  position-empty is not reachable via the speed-only early guard) or a naming nit to flag.
- **simplification_limits:** confirm `py -m src.utils.simplification_limits
  src/physics/session_fit.py src/preprocessing/trajectory/calibration.py` introduces
  NO new violation (implementer reports complexity 18→19, still under the <20 limit).
- **Scope:** no new status beyond `no_speed_stream`; no min-flying-laps/sample floor;
  no_accel_samples semantics untouched.

## Allowed Scope (what implementation could touch)
`src/physics/session_fit.py`, `src/preprocessing/trajectory/calibration.py`,
`src/physics/fit_store.py`, `tests/unit/physics/`. Flag anything else.

## Specific Exclusions
Fit-quality floor; new statuses; successful-fit numeric changes; store rebuild.

## Constraints the Implementation Must Respect
- `py` launcher; `constraint:physics_region_no_evo_import`; test-led; no fabricated
  overlap / no second-class fits; inputs validated with named conditions.

## Map Anchors (inbound)
- **Structural:** `session_fit.fit_driver` (early guard @ ~236; mapping @ 308-314);
  `calibrate_session_hp` `windows=` branch (@ ~877); `fit_store.FitRecord.fit_status`
  (@ 34); test sentinel sets (`test_475_validation_breadth.py:87/261/573`).
- **Capability:** per-session physics fit; HP calibration / held-out split.
- **Constraints:** physics_region_no_evo_import; test-led; no second-class fits.
- **Decision anchors:** `no_speed_stream` typed-skip ratified at decide-fix.
- **Evidence expectations:** `test_calibration_robustness.py` stays green; 421 ok fits unaffected.

## Evidence Produced
Implementer reports: 755 passed / 52 skipped; Saudi DEV repro prints
`no_speed_stream`; simplification_limits 3 pre-existing violations (complexity 18→19,
under limit). Result: `.agent-work/issue-495-fit-robustness/g2_implementer_result.md`.

## Suggested Model Tier
simple bounded — small, well-scoped diff; verify by independent re-run.

## Stop Conditions
Return BLOCK if: the `no_accel_samples` mapping regressed; Saudi DEV does not return
`no_speed_stream`; the region suite is not green; a previously-ok fit's params drift;
or scope was exceeded.

## Return Format
Return REVIEW_RESULT (write to
`.agent-work/issue-495-fit-robustness/g2_review_result.md`): verdict (APPROVE/BLOCK),
per-check findings WITH your independent re-run outputs, blockers, out-of-scope
observations, workflow feedback.
