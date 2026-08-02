# G2 — Commander integrate-verification (re-review constrained by crew session limit)

**Context.** The g2 reviewer crew APPROVED attempt-1 (the core `no_speed_stream`
typed-skip fix in `fit_driver` + `calibrate_session_hp` + comment + tests) with 8
independent checks — a genuine independent crew verdict (see `g2_review_result.md`,
verdict APPROVE). The human then extended scope to fold the same guard into the
sibling `fit_session_full`. The crew re-review (attempt-2) of that increment could
NOT complete: the subagent hit a session limit (resets 12:10pm PT). The user
directed "keep going."

**Closest-compliant resolution (flagged for feedback).** Rather than impersonate the
reviewer, the verdict rests on: (a) the genuine attempt-1 crew APPROVE of the
substantive fix; (b) this commander integrate-verification of the trivial increment;
(c) the engine's own `g2-integrate` full-suite postcondition, which independently
exercises the new `fit_session_full` test. The increment is a 3-line mirror of an
existing pattern — low independent-review value.

**Increment verified by commander (ground truth, 2026-06-28):**
- `src/physics/session_fit.py` `fit_session_full` (lines 400-402), right after
  `pos_d, spd_d = driver_streams(session, num)`:
  ```python
  if len(spd_d["t"]) == 0:
      logger.debug("fit_session_full no speed stream %s %s %s", year, gp_name, driver)
      return None
  ```
  Correct shape: `fit_session_full` returns `Optional[SessionFitFull]` (NOT a
  FitRecord), so an early `return None` is the right clean signal — it makes the
  empty-speed case explicit instead of falling through to the broad `except
  Exception` as a silent None. Mirrors the existing `if not proc: return None`.
- New test `test_fit_session_full_empty_speed_stream_returns_none`
  (`tests/unit/physics/test_calibration_robustness.py:348`) asserts None-not-raise.
- `py -m pytest tests/unit/physics/test_calibration_robustness.py -q` → **14 passed**
  (the +1 over attempt-1's 13 is exactly this new test).
- Scope unchanged: no new status beyond `no_speed_stream`; no fit-quality floor;
  `no_accel_samples` semantics untouched; only allowed files changed;
  `physics_region_no_evo_import` honored.

**Stale-artifact note.** `g2_review_result.md` is the attempt-1 file; its Triage
candidate #1 ("fit_session_full has no guard… would crash… out of scope") is now
STALE — the guard exists. Triage candidate #2 (the `len(tp)<1` branch raising a
"no_speed_stream: empty position stream" message — a naming nit) still stands and is
carried to the triage step.

**Verdict carried into integrate:** APPROVE (attempt-1 crew APPROVE + commander
increment verification + engine full-suite gate). Misfit (truncated crew re-review
due to session limit) recorded for the feedback step.
