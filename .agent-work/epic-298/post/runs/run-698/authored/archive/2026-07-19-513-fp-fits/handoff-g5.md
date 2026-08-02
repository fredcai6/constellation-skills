# Implementer Handoff — G5 (estimate_session FP wiring + explicit-unknown + #560)

## Gate
`g5` (execute.json)

## Task
Wire FP-session support into the estimator so FP fits run UNBIASED (fp_mass, not quali_mass), with the
grip-anchor-first / power-to-weight-second discipline and the #627 explicit-unknown contract for FP axes.

## Protected Intent
Today `session_estimator.estimate_session` applies `m = quali_mass(year)` at line ~125 REGARDLESS of
session type, and `estimate_batch` loads the FP session + records `session_type` but never tells
`estimate_session` it's FP — so FP fits are silently fuel-biased. Fix the bias at its source. The FP
per-run starting fuel is UNOBSERVABLE (fp_mass carries intercept σ) — that σ MUST propagate into the
longitudinal (power-to-weight / CdA) axes as widened uncertainty, NEVER as bias. Sandbagging/detuned
engines → WIDER σ, never a shifted mean.

## Test Mode
TDD required for the wiring logic; a real-session smoke fit is inspection evidence.

## Close Criteria
- `estimate_session(..., session_type: str = "Q", mass_kg: Optional[float] = None,
  mass_sigma_kg: Optional[float] = None, ...)`:
  - Flip the `:115` load literal `"Q"` → `session_type` (the session=None standalone path).
  - Replace the unconditional `m = quali_mass(year)` (~:125): when `mass_kg` is injected, use it; else when
    `session_type` starts with "FP", resolve mass from `fp_mass` at the constructor's REPRESENTATIVE
    (fastest clean) lap via `fp_lap_latent` (single per-session assumed mass + its σ — document this as the
    same single-mass approximation quali used; per-observation mass is a named future refinement); else
    `quali_mass(year)` (byte-identical for Q — default-arg Q calls MUST be unchanged).
  - Carry the resolved mass σ on `SessionEstimate` (e.g. `mass_sigma_kg`) so the store + longitudinal axis
    status can use it.
- `estimate_batch.run_estimate_batch` passes `session_type=session_type` into the `estimate_fn(...)` call
  (it currently omits it — the session is loaded with the right type but estimate_session isn't told).
- Grip-anchor FIRST: confirm the lateral/apex (mass-cancelling) path is unaffected by the mass change;
  power-to-weight/CdA (mass-consuming) axes SECOND, carrying the fp_mass σ.
- FP axis explicit-unknown (#627): for FP fits, the longitudinal axes (`cda`, `p_max`, `b_b`, `b_t`) whose
  uncertainty is inflated by the unobservable fuel intercept carry widened `effective_axis_sigma` via the
  existing `_axis_statuses`/`effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC` machinery — reuse it,
  do NOT invent a parallel path. Nothing dropped; a poorly-supported FP axis reserves a high-σ slot.
- #560: `_support_trust_profile` already degrades non-Q rows (reason `practice_session_quali_mass_assumption`).
  Update/extend that reason wording now that FP uses fp_mass (it is no longer a quali-mass assumption) — but
  do NOT add a new hard flying-lap floor (that was #560's explicit finding).
- A real 2023 FP session smoke fit runs end-to-end: `est.mass_kg != quali_mass(2023)` and lands in the
  store's `mass_kg_assumed`; the longitudinal axis σ is visibly wider than the Q-fit equivalent.

## Allowed Scope
- `src/physics/layer2/session_estimator.py`, `src/physics/layer2/estimate_batch.py`,
  `src/physics/layer2/estimate_store_fields.py` (the `_support_trust_profile` reason + any FP axis-σ wiring),
  and `estimate_store.py`/`record_from_estimate` only if a new mass_sigma field is needed.
- Tests under `tests/unit/physics/layer2/` (keep each test file < 1000 lines; run
  `py -m src.utils.simplification_limits --baseline` on touched paths — this IS required per CREW_CONTEXT,
  even though a prior handoff omitted it).

## Specific Exclusions
- Do NOT run a real backfill / re-pop over real data (#646). A single-session smoke fit is fine (read-only
  telemetry); do NOT write any `data/*.db`.
- Do NOT thread per-OBSERVATION mass into the views (named future refinement — single representative mass now).
- Do NOT change the grip/lateral mass-cancelling math.
- Do NOT wire #628 driver_utility here.

## Constraints
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- Q default-arg behavior BYTE-IDENTICAL (regression pins must stay green).
- fp_mass σ propagation must WIDEN longitudinal σ, never shift the mean (explicit-unknown discipline).
- Reuse #627 machinery verbatim; reuse fp_mass/fp_lap_latent from G2.
- DB hygiene #632; simplification --baseline on touched paths.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — `session_estimator.py::estimate_session`,
  `estimate_batch.py::run_estimate_batch`, `estimate_store_fields.py::_support_trust_profile`/`_axis_statuses`.
- Capability: FP fits run unbiased; grip-first/power-second.
- Constraints: explicit-unknown (#627), #560 soft-trust (no new hard floor), Q byte-identical.
- Decision: `decision:cross_view_covariance_sparse_representation` — reuse not fight.

## Deliverable Path Check
- Committed — the touched src files + new/extended tests under `tests/unit/physics/layer2/`. Tracked.

## Required Evidence
- Put the new FP-wiring unit tests in `tests/unit/physics/layer2/test_session_estimator_fp.py` (this exact
  path is the gate's own check). `py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py -q`
  green (paste summary).
- Q-regression: run the EXISTING session_estimator tests to prove Q byte-identical
  (`py -m pytest tests/unit/physics/layer2/test_session_estimator*.py -q` or the specific existing file) —
  paste summary. (The full `tests/unit/physics` region suite EXCEEDS the harness sync timeout — do NOT
  block on running it synchronously; run targeted files, and if you want the broader sweep run it detached.)
- `py -m src.utils.simplification_limits --baseline --paths <touched>` PASS.
- The real 2023 FP smoke-fit output showing `mass_kg != quali_mass` + wider longitudinal σ vs a Q fit.
- `git status --short data/` clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py -q && py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/session_estimator.py && git status --short data/
```

## Suggested Model Tier
`stronger` — the mass-σ→longitudinal-σ propagation and the byte-identical-Q constraint carry real risk.

## Authority
The wiring shape (session_type param + representative-lap fp_mass + σ propagation via #627 machinery, Q
byte-identical, single-representative-mass approximation) is DECIDED (Ship I, per GATE_PROTOCOL.md F2/F10 +
launch order). You choose implementation details; do not run a real backfill or change grip math.

## Stop Conditions
Stop and return if Q byte-identical cannot be preserved, per-observation mass proves necessary for a
passing fit, or the fp_mass σ cannot be propagated through the existing #627 machinery.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence (incl. the FP smoke fit +
Q-regression-green), assumptions, stop conditions, out-of-scope observations, workflow feedback.
