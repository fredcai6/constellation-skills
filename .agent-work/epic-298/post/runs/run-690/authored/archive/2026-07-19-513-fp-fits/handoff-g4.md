# Implementer Handoff — G4 (representativeness weighting)

## Gate
`g4` (execute.json)

## Task
New `src/physics/layer2/fp_representativeness.py`: a continuous per-observation representativeness weight
`w in [0,1]` computed from the OBSERVATION's OWN properties (never a session label), for weighting FP
observations toward qualifying-representative capability. This is the module the held-out gate (G6) and
the #628 product consume.

## Protected Intent
The weighting must be EMERGENT: "FP3 usually matters most" must fall out of FP3 happening to hold the most
Q-representative observations, NEVER a hardcoded session weight. If a team quali-sims in FP2, THAT
observation earns the weight. A weighting that collapses to a monotone function of session-mean
track-evolution has smuggled the calendar and is WRONG (see the emergence test).

## Test Mode
TDD required (pure feature functions + weighting form).

## Close Criteria
- `observation_features(latent: FpLapLatent, *, quali_fuel_kg, track_evolution: Optional[int],
  session_max_track_evolution: Optional[int]=None) -> ObservationFeatures` — a small frozen dataclass /
  named-array of per-observation features:
  - `fuel_proximity`: closeness of `latent.fuel_kg_est` to `quali_fuel_kg` (low fuel → high; e.g.
    `exp(-((fuel_est - quali_fuel)/FUEL_SCALE_KG)^2)` or a monotone decay). INERT on grip, load-bearing
    on longitudinal — keep it a distinct feature so the gate can see its per-channel value.
  - `compound_softness`: monotone score from `latent.compound` (SOFT > MEDIUM > HARD; C-number aware if
    present). Quali runs on softs → softer = more representative.
  - `run_purpose_score`: push/quali-sim → high; long_run → low; out/in → ~0. From `latent.run_purpose`.
  - `track_evolution_score`: rubbered-in → higher (monotone in `track_evolution`). CARRIED but it must NOT
    be able to dominate — see the within-session-orthogonal requirement below.
- `observation_weight(features: ObservationFeatures, *, params: WeightParams=DEFAULT_WEIGHT_PARAMS)
  -> float in [0,1]` — a TRANSPARENT parametric combination (e.g. logistic over a linear score, or a
  weighted geometric mean), with `WeightParams` a named dataclass of coefficients. DEFAULT params are
  reasonable hand-set values (flag tunable); the gate (G6) FITS `params` on train weekends. The form must
  be inspectable (not a black box) so emergence is auditable.
- EMERGENCE (load-bearing, critic F3): the weight MUST respond to WITHIN-SESSION variation independent of
  session-mean track-evolution. Provide + test: within a single session (same track_evolution band), a
  lap-3 low-fuel soft push observation outweighs a lap-18 high-fuel hard long-run observation. And a
  low-fuel soft push observation in FP2 outweighs a high-fuel hard long-run in FP3 (later session, but
  less representative). NO session-type string anywhere in the module.
- NOTHING BINARY-DROPPED: every observation gets a weight in [0,1]; thin/unrepresentative runs get LOW
  weight, never excluded/None.
- Process-noise/parc-fermé framing (document in the module docstring, no separate fit here): car-state
  drifts FP1→FP2→FP3→[parc-fermé]→Q; the weighting down-weights earlier-session observations ONLY through
  their emergent OBSERVATION properties (green track, high fuel), not a session label — the process-noise
  chain is REPRESENTED by the track_evolution + fuel features, not hardcoded.

## Allowed Scope
- New `src/physics/layer2/fp_representativeness.py`.
- New `tests/unit/physics/layer2/test_fp_representativeness.py`.
- May import `fp_lap_latent` (FpLapLatent) and read `session_cumulative_track_laps` /
  `compute_cumulative_track_laps` from session_race for the track-evolution feature (do NOT change them).

## Specific Exclusions
- Do NOT fit weighting coefficients on real data here (that is G6 on train weekends). DEFAULT params only.
- Do NOT touch session_estimator.py (G5), the views, or estimate_store.
- Do NOT read/modify/commit any data/*.db (#632) — unit tests use synthetic FpLapLatent instances.
- Do NOT wire into #628 driver_utility here (named follow-on).

## Constraints
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- weekend_state/track-evolution feature MUST consume NO qualifying-session input (leakage guard, F6) —
  track_evolution is computed from FP/session lap counts only.
- All coefficients/scales named at module scope, flagged tunable (no hidden inline tuning).
- Keep the file well under 1000 lines (simplification_limits); split the test file if it approaches it.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — new `fp_representativeness.py`; consumes `fp_lap_latent.FpLapLatent`.
- Capability: continuous per-observation weight feeding held-out gate + #628 product.
- Constraints: emergence (no session label), leakage (no Q input), nothing binary-dropped.
- Decision pressure: the weighting FORM + feature set (surface as a decision-candidate in your result).

## Deliverable Path Check
- Committed — `src/physics/layer2/fp_representativeness.py`,
  `tests/unit/physics/layer2/test_fp_representativeness.py`. Tracked; new files appear in `git status`.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q` green (paste summary).
- The emergence tests explicitly (within-session reweighting + FP2-push-beats-FP3-longrun).
- `py -m src.utils.simplification_limits` on the new paths (PASS, under 1000).
- `git status --short data/` clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q && py -m src.utils.simplification_limits src/physics/layer2/fp_representativeness.py
```

## Suggested Model Tier
`stronger` — the emergence property + transparent weighting form carry real design judgment; get it right.

## Authority
The feature set (fuel_proximity, compound_softness, run_purpose_score, track_evolution_score), the
emergent-no-session-label rule, and the fit-params-in-G6 split are DECIDED (Ship I, per GATE_PROTOCOL.md
F3/F6). You choose the concrete transparent weighting form + default coefficients (name + flag tunable).
Do not add a session-type feature; do not fit on real data.

## Stop Conditions
Stop and return if scope must be exceeded, the emergence tests cannot pass with a session-label-free form,
or a Q-session input would be needed for the track-evolution feature.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence (incl. the two emergence
tests), assumptions, stop conditions, out-of-scope observations, workflow feedback.
