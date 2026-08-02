# Plan Candidate A — "falsifiable-core-first" (Ship I's primary draft)

Constraint: the frozen held-out gate is the deliverable; build the minimum real machinery to run
it honestly on real FP physics fits, wire the smallest production seam, treat store re-pop and
parc-fermé-distribution as bounded dispositions. Honest-null is complete.

## Gate plan
**G1 — fp_mass + per-lap latent state (crew gate).**
- `mass_model.fp_mass(season, *, fuel_kg=None, team=None)`: season base + estimated FP fuel (NOT the
  10 kg quali reserve). Named constants, no hidden tuning.
- New `src/physics/layer2/fp_lap_latent.py`: from season-DB `lap_times` rows (compound OBSERVED,
  tyre_life, stint_id, lap_number, lap_time, valid_lap, track_status) + burn model, emit per-lap latent:
  `(fuel_mass_est, compound, tyre_life, run_purpose)` and per-lap mass. run_purpose classified from
  lap pattern (out / push / in / long-run) via lap_time-vs-session-best + stint position — EMERGENT,
  never a session label. Fuel est = decreasing over stint via burn model (heaviest at stint start).
- Reuse the season-DB join (physics→data allowed direction, like fuel_features.py).
- Tests: fp_mass < quali+full-fuel and > base; run_purpose classification; monotone fuel over stint.

**G2 — representativeness weighting (crew gate).**
- New `src/physics/layer2/fp_representativeness.py`: `observation_weight(latent, track_evolution) -> w in [0,1]`,
  a continuous weight from the OBSERVATION's own properties (fuel proximity to quali-fuel, compound
  softness, run_purpose=push, track rubbered-in via #626 evolution). Emergent session ordering.
- Uses #626 `weekend_state` evolution for track-state so a green-track FP1 push lap isn't scored as
  car-slow. Nothing binary-dropped — every lap gets a weight (thin runs → low weight, not excluded).
- Tests: a low-fuel soft push lap in FP2 outweighs a high-fuel hard long-run lap in FP3; weights in [0,1];
  no session appears as a hardcoded constant anywhere.

**G3 — FP fit wiring + explicit-unknown (crew gate).**
- Parameterize `estimate_session(session_type="Q", mass_kg=None, ...)`: flip `:115` literal + `:125`
  quali_mass. When session_type startswith FP, mass from fp_mass/latent (per-car representative lap),
  NOT quali_mass. Grip-anchor FIRST (apex/lateral mass-cancel), power-to-weight from straights SECOND.
- FP axis status via #627 machinery (`_axis_statuses`/`effective_axis_sigma`); sandbagging/detuned →
  WIDER σ never bias. Extend #560 `_support_trust_profile` (already non-Q aware) — no new hard floor.
- Tests: FP fit runs on a real 2023 FP session; mass ≠ quali_mass; unresolved FP power axis reserves high σ.

**G4 — the frozen held-out gate + evidence (reasoning gate; compute-heavy sub-batch).**
- Freeze split (train/held-out weekends) + rubric BEFORE any number.
- `scripts/fp_representativeness_gate.py`: predict per-car Q grip capability (the trustworthy #627 Q basis)
  from weighted FP observations under LEARNED weighting vs CLOCK-DISTANCE-to-Q baseline; held-out error.
- Sandbagging weekend must visibly discount. FP×regime coverage+σ-vs-Q map.
- Compute: bounded (one season's apex extraction), detached headless (Start-Process hidden, OMP=4).
- Deliverable = verdict numbers into the verdict doc. Honest-null reported plainly if learned ≤ clock.

**G5 — per-car cumulative_track_laps unlock (crew gate; aim to land, bounded-defer if balloons).**
- Add `cumulative_track_laps INTEGER` to `session_estimates`; populate per (year,gp,session,constructor)
  via a per-session analogue of `compute_cumulative_track_laps`. Unblocks #626.
- Tests: column persists + self-heal migration; value matches the count definition.

## Dispositions (surfaced, not silently dropped)
- #646 full multi-season re-pop = HEAVIEST compute → bounded demo batch in G4; full re-pop handed back
  as clean follow-on (surface to Admiral).
- Parc-fermé reaction / weekend process-noise chain: G2's weighting carries the chain/process-noise
  framing; a full per-team×season fitted parc-fermé distribution is bounded-deferred with quantified reason.
