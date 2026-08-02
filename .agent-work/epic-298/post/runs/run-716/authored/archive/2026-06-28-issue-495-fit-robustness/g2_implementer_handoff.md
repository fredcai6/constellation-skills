# Implementer Handoff — G2 Robustness fix

## Gate
g2 (execute.json `g2-implement`)

## Task
Convert the one remaining live fit crash (Saudi Arabia 2023 Q, driver DEV — empty
session-wide speed stream → `ValueError: zero-size array...` at `calibration.py:879`)
into a **clean typed-skip** with a new `no_speed_stream` reason, guarded at two
sites, plus fix the stale `fit_store.py:34` comment. Test-led.

## Protected Intent
A batch fit must never crash on one driver, and an unfittable session must record an
**honest typed reason**, not a generic `error` and not a fabricated fit. Physics
doctrine: fail visibly, no hidden fallback, no plausible-wrong output. Do NOT
manufacture a speed stream or relax any fit-quality path.

## Test Mode
TDD required — there is a test surface (`tests/unit/physics/test_calibration_robustness.py`,
`tests/unit/preprocessing/`). Write the failing test for the empty-speed-stream skip
first, then the guard.

## Ratified design (human, decide-fix 2026-06-28 — do NOT re-decide)
1. **Distinct `no_speed_stream` typed-skip reason** (NOT reuse `no_accel_samples`).
2. **Both guard sites:** (a) primary early guard in `session_fit.fit_driver`,
   (b) defense-in-depth typed raise in `calibrate_session_hp`'s `windows=` branch.
3. Thin-fit minimum-lap/sample floor is OUT of scope (follow-up triage) — do not add
   any min-flying-laps/min-sample gate.

## Close Criteria (each proven)
- `session_fit.fit_driver` returns `FitRecord(fit_status="no_speed_stream")` (no
  raised exception, not `error`) when the driver's speed stream is empty —
  reproduced on Saudi Arabia 2023 Q DEV.
- `calibrate_session_hp(..., windows=...)` raises a **typed** `ValueError`
  (message prefix `no_speed_stream`) instead of the raw `zero-size array` ValueError
  when its speed (`tc`) input is empty — and `fit_driver` maps that prefix to
  `_err("no_speed_stream", msg)`.
- `fit_store.py:34` comment lists the full current set:
  `# "ok" | "error" | "no_laps" | "no_accel_samples" | "no_speed_stream"`.
- All three `valid_statuses` sets in `tests/unit/physics/test_475_validation_breadth.py`
  (lines 87, 261, 573) include `"no_speed_stream"`.
- New unit test(s) cover: (i) the early `fit_driver` guard returns
  `no_speed_stream`; (ii) `calibrate_session_hp` empty-`tc` → typed
  `ValueError("no_speed_stream: ...")`. Keep `test_calibration_robustness.py`
  (`no_accel_samples` path) green — do not regress it.
- `py -m pytest tests/unit/physics tests/unit/preprocessing -q` green.

## Allowed Scope
- `src/physics/session_fit.py` (early guard + ValueError mapping).
- `src/preprocessing/trajectory/calibration.py` (`calibrate_session_hp` `windows=`
  branch empty-input guard only).
- `src/physics/fit_store.py` (line-34 comment only).
- `tests/unit/physics/`, `tests/unit/preprocessing/` (new + updated tests).

## Specific Exclusions
- No new status beyond `no_speed_stream`. No min-flying-laps/sample floor. No change
  to any successful-fit numeric path (the 421 ok fits must stay byte-identical).
- Do NOT touch the `no_accel_samples` semantics — that path stays for the
  HP-search-failed case; `no_speed_stream` is specifically "speed channel empty".
- Do not rebuild the fit store (that's G3 validation).

## Constraints
- `py` launcher (never `python`).
- `constraint:physics_region_no_evo_import`.
- `src/utils/simplification_limits` clean on touched paths (project rule).
- Validate inputs with messages naming the condition (project rule).

## Map Anchors (inbound)
- **Structural — exact seams (verify from source before editing):**
  - `session_fit.py:237` `pos_d, spd_d = driver_streams(session, num)` — place the
    primary guard right after, mirroring `:240-241` `if valid.empty: return
    _err("no_laps")`: `if len(spd_d["t"]) == 0: return _err("no_speed_stream")`.
    (`spd_d`/`pos_d` are dict-likes with numpy arrays under keys `t,V` / `t,X,Y`.)
  - `session_fit.py:308-314` — the `except ValueError` mapping. Add a
    `no_speed_stream` branch alongside the existing `no_accel_samples` branch
    (`if msg.startswith("no_speed_stream"): return _err("no_speed_stream", msg)`).
  - `calibration.py:877-879` — the `if windows:` block computes
    `tp_min,tp_max = tp.min(),tp.max()` / `tc_min,tc_max = tc.min(),tc.max()` on
    possibly-empty arrays. Add a guard BEFORE line 878 that raises
    `ValueError("no_speed_stream: empty speed stream in calibration windows")` when
    `len(tc) < 1` (and a sensible typed raise if `len(tp) < 1`). Pattern-match the
    existing typed raise at `calibration.py:899-902`.
  - `fit_store.py:34` — the stale `fit_status` comment.
- **Capability:** per-session physics fit; HP calibration / held-out split.
- **Constraints:** physics_region_no_evo_import; test-led; no fabricated overlap /
  no second-class fits; py launcher.
- **Decision anchors:** typed-skip taxonomy ratified at decide-fix (no_speed_stream).
- **Evidence expectations:** `tests/unit/physics/test_calibration_robustness.py`
  stays green; the 421 previously-ok fits unaffected.
- **Map confidence flags:** none — diagnosis resolved the area.

## Required Evidence
- The new/updated test output (red→green for the no_speed_stream path).
- `py -m pytest tests/unit/physics tests/unit/preprocessing -q` full result.
- A one-line repro showing Saudi Arabia 2023 Q DEV now returns
  `fit_status="no_speed_stream"` (via `load_quali_session` + `fit_driver`).

## Verification Commands
```bash
py -m pytest tests/unit/physics tests/unit/preprocessing -q
py -m src.utils.simplification_limits src/physics/session_fit.py src/preprocessing/trajectory/calibration.py
py -c "from src.physics.session_fit import load_quali_session, fit_driver; s,rho,_=load_quali_session(2023,'Saudi Arabia','Q'); r=fit_driver(s,'DEV',year=2023,gp_name='Saudi Arabia',round_idx=2,session_type='Q',constructor='AlphaTauri',rho=rho); print(r.fit_status)"
```

## Suggested Model Tier
simple bounded — well-scoped, ratified design, two small guards + a comment + tests.

## Authority
Design ratified by the human (decide-fix). You implement exactly that; you do not
add new statuses, floors, or change successful-fit numerics. If the ratified plan
cannot be implemented as written, STOP and return rather than improvising.

## Stop Conditions
Stop and return if: a successful-fit numeric path would change; the empty-stream
condition turns out to need a different reason than ratified; scope must be exceeded;
a test cannot be made to pass without altering the ratified design.

## Return Format
Return IMPLEMENTER_RESULT (write to
`.agent-work/issue-495-fit-robustness/g2_implementer_result.md`): completed slice,
files changed, test mode satisfied, evidence (test output + the Saudi DEV repro),
assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
