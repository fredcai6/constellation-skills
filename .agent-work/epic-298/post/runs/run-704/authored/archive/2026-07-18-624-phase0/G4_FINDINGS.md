# G4 — SQ coverage probe findings

## What ran

`scripts/g4_sq_probe.py` (committed, `git check-ignore` confirms exit 1 / not ignored): loads a real SQ session via `load_quali_session(2023, "Austria", "SQ", DEFAULT_CACHE)` (`src/physics/session_fit.py:168`), then feeds it into `estimate_session(year=2023, gp="Austria", drivers=("VER","PER"), session=<SQ session>, rho=..., rho_is_fallback=...)` — bypassing the internal hardcoded `"Q"` load (`session_estimator.py:113-115`) while `quali_mass(year)` still applies unconditionally (the known, documented gap; SQ has a genuinely different fuel/mass profile that this probe does NOT correct for).

Weekend chosen: 2023 Austria (round 9), Red Bull Racing — a sprint-format weekend where `session_estimates` already holds a Q-session estimate for the SAME constructor/SAME weekend (all 10 constructors, `fit_status='ok'`), giving a tighter same-weekend comparison than an adjacent round.

## Load outcome

**SUCCESS.** `load_quali_session(2023, "Austria", "SQ", ...)` loaded without error (`rho=1.1119`, not a fallback density). `estimate_session(..., session=<SQ session>)` also completed without raising. Note: `fit_status` on the returned `SessionEstimate` was `None` rather than `'ok'`/`'error'` — `SessionEstimate` does not carry a `fit_status` field at all (verified from `session_estimator.py:45-61`'s dataclass definition; this attribute simply doesn't exist on the object, `getattr(..., None)` silently returned `None`). Not a defect — the DB's `fit_status` column is written by the STORE layer (`estimate_store.py`), not the estimator itself, and this probe doesn't write to the store.

## Numeric plausibility check (not crash-only, per critic finding #4)

Compared each of the 11 axes' SQ estimate against the SAME constructor's SAME-weekend stored Q estimate (`data/physics_estimates.db`, `year=2023 gp_name='Austria' constructor='Red Bull Racing' session_type='Q'`), same-sign + within a 0.4x-2.5x band as the plausibility bar:

| axis | SQ | Q (stored) | ratio SQ/Q | verdict |
|---|---|---|---|---|
| drag_area_closed_m2 | 1.241 | 1.305 | 0.951 | PLAUSIBLE |
| brake_decel_ms2 | 26.70 | 32.74 | 0.816 | PLAUSIBLE |
| brake_aero_decel_per_m | 0.00364 | 0.00123 | 2.964 | **FLAG** |
| traction_accel_ms2 | 4.167 | 8.383 | 0.497 | PLAUSIBLE |
| traction_aero_accel_per_m | 0.01572 | 0.00841 | 1.871 | PLAUSIBLE |
| max_power_w | 610,703 | 621,545 | 0.983 | PLAUSIBLE |
| power_drag_area_m2 | 1.241 | 1.305 | 0.951 | PLAUSIBLE |
| lateral_mech_grip_g | 2.466 | 2.974 | 0.829 | PLAUSIBLE |
| lateral_aero_grip_g | 0.000831 | 0.000609 | 1.364 | PLAUSIBLE |
| coast_rolling_decel_ms2 | 1.160 | 0.838 | 1.384 | PLAUSIBLE |
| coast_drag_area_m2 | 1.241 | 1.305 | 0.951 | PLAUSIBLE |

**10/11 axes plausible.** The one flag (`brake_aero_decel_per_m`, ratio 2.96x) is the downforce-added braking-grip slope — a thin, historically noisy secondary parameter (per `x7-basis-map-RESULT.md`, braking-aero-slope was ALSO the axis that benefited LEAST from weekend-relative normalization in x4, "already the most locally-fit, least density/circuit-sensitive quantity" — consistent with it being the most fit-noise-sensitive axis, not necessarily an SQ-specific problem). Most axes (drag, power, lateral grip, traction) land within a plausible 0.5x-1.4x band despite the unconditional `quali_mass()` gap.

## Verdict

**Plausibly compatible.** The Q estimator runs on an SQ session without modification to the estimator itself (only bypassing the hardcoded session-type string via the existing `session=` override parameter), and produces numbers in the same ballpark as the same-weekend Q estimate for 10 of 11 axes — a genuinely informative result, not a load-bearing production claim (the mass mismatch is real and uncorrected; this is a Phase-0 compatibility read, not a validated SQ pipeline). The one flagged axis (`brake_aero_decel_per_m`) is worth a note for whoever eventually builds real SQ support, but is not disqualifying on its own (it's the noisiest axis by prior finding, not uniquely broken by SQ).

## Architecture boundary check

`grep -rn "evo_predictor" src/physics/ --include=*.py | grep -v test` returns 8 matches — all pre-existing docstring/comment mentions of the `constraint:physics_region_no_evo_import` rule itself, plus two pre-existing config-path STRING LITERALS (`src/physics/wear/panel.py:61`, `season_model.py:42`, `"C:/Programs/f1Brainz/src/evo_predictor/compounds.yaml"`) — none are Python `import` statements, and none were introduced or touched by this probe (`g4_sq_probe.py` is read-only against `src/physics/`, zero files under `src/physics/` were modified). **Zero evo_predictor imports introduced.**

## Correction note (self-caught, no crew review on this reasoning gate)

The first run of this script accessed `SessionEstimate` as if it carried flat attributes matching the DB column names (`est.lateral_mech_grip_g`, etc.) and produced an all-`n/a` table — a script bug, not a real finding. `SessionEstimate` actually nests results per view (`.braking.brake_decel_ms2`, `.traction.traction_accel_ms2`, `.power_drag.max_power_w`/`.drag_area_closed_m2`, `.lateral.lateral_mech_grip_g`/`.lateral_aero_grip_g`, `.coast.coast_rolling_decel_ms2`/`.coast_drag_area_m2` — verified from each view's dataclass definition in `src/physics/layer2/{braking,traction,power_drag,lateral,coast}_view.py`). Corrected and re-run; the table above is from the corrected run. Flagged here per this run's own doctrine (verify claimed side-effects against the world) rather than silently fixed.
