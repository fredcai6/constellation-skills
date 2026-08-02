# Converged Gate Plan — #513 Phase 4 FP-fits (A′ = A + B-sequencing + C-structural-honesty)

## Convergence rationale
- From C (decisive scientific insight): the grip/apex channel (`capability.apex_pace`, `LateralView`) mass-CANCELS
  → the held-out test is STRUCTURALLY non-circular there (no fp_mass smuggled). BUT grip is exactly the channel
  where the quali-mass fuel bias is ABSENT, so grip-only would be a toy w.r.t. the longitudinal product feeding #628.
- Resolution: test the SAME learned weighting on BOTH channels. GRIP = clean PRIMARY gate (airtight, structural
  non-circularity). LONGITUDINAL power-to-weight = caveated SECONDARY (where fuel-proximity earns its keep and
  fp_mass matters); reported with honest σ + the non-circularity chain proven, not the sole pass/fail.
- From B (decisive sequencing insight): FREEZE fp_mass before any heavy compute (a later mass correction forces a
  full re-pop redo — the most expensive reap-trap). FREEZE the gate protocol before any number (decouple ship-path
  from the falsifiable claim so integration momentum cannot coerce a PASS). Separate refit-gating from post-fit reads.
- Compute posture (heaviest phase + reap-trap): BOUNDED demonstration batch here; full multi-season #646 re-pop
  handed back with a measured ETA + resume command (B's "quantified resumable remainder"), NOT executed blind.

## Gates
**G1 (reasoning) — FREEZE the gate protocol (zero compute, before any number).**
Commit `GATE_PROTOCOL.md`: frozen train/held-out weekend split; PRIMARY target = per-car Q grip capability
(apex_pace / LateralView — mass-free) + SECONDARY target = longitudinal power-to-weight; the two weighting arms
(learned observation-property vs clock-distance-to-Q); metric (held-out Spearman + centred RMSE); named sandbagging
weekend + expected discount direction; honest-null rule (learned ≤ clock is complete, no kill switch); the
non-circularity obligation. Close: manifest committed + dated + split hashed. Reasoning gate (doc), crew-waived.

**G2 (crew) — fp_mass + per-lap latent state (mass FROZEN here).**
`mass_model.fp_mass(season, *, fuel_kg=None, team=None)` (base + estimated FP fuel, NOT the 10 kg quali reserve;
named constants). New `src/physics/layer2/fp_lap_latent.py`: from season-DB `lap_times` (compound OBSERVED, tyre_life,
stint_id, lap_number, lap_time, valid_lap, track_status) + burn model → per-lap `(fuel_mass_est, compound, tyre_life,
run_purpose)` + per-lap mass. run_purpose EMERGENT (out/push/in/long-run from lap-time-vs-session-best + stint pos).
Non-circular: no fit output feeds fp_mass. Close: base<fp_mass<quali+full-fuel; monotone fuel over stint;
run_purpose classification; tests green.

**G3 (crew) — representativeness weighting.**
New `src/physics/layer2/fp_representativeness.py`: `observation_weight(latent, track_evolution) -> w in [0,1]`,
continuous, EMERGENT from the observation's own properties (fuel-proximity-to-quali-fuel [inert on grip, load-bearing
on longitudinal], compound softness, run_purpose=push, track rubbered-in via #626 `weekend_state` evolution).
Nothing binary-dropped (thin runs → low weight, not excluded). Close: w in [0,1]; a low-fuel soft push lap in FP2
outweighs a high-fuel hard long-run in FP3; NO session appears as a hardcoded constant; tests green.

**G4 (crew) — estimate_session FP parameterization + explicit-unknown + #560.**
Parameterize `estimate_session(session_type="Q", mass_kg=None, ...)`: flip `:115` load literal + `:125` quali_mass;
FP mass from fp_mass/per-car representative latent. Grip-anchor FIRST (mass-cancel), power-to-weight SECOND. FP axis
status via #627 `_axis_statuses`/`effective_axis_sigma`; sandbagging/detuned → WIDER σ never bias. Extend #560
`_support_trust_profile` (already non-Q aware) — no new hard floor. Thread session_type through estimate_batch call.
Close: real 2023 FP fit runs; est.mass_kg ≠ quali_mass, lands in mass_kg_assumed; unresolved FP power axis reserves
high σ (nothing dropped); tests green + region suite green.

**G5 (crew) — per-car cumulative_track_laps unlock into session_estimates.**
Add `cumulative_track_laps INTEGER` to `EstimateRecord` (self-heal migration); populate per (year,gp,session,
constructor) via a session analogue of `compute_cumulative_track_laps`. Unblocks #626. Coordinate ShipE-626.
Close: column persists + migration self-heals on a store copy; value matches definition; tests green.

**G6 (crew) — held-out gate harness (both channels, tests on fixture).**
`scripts/fp_representativeness_gate.py`: clock-distance-to-Q baseline arm + learned observation-property arm; fit w on
TRAIN weekends only; predict per-car Q grip capability (PRIMARY) and longitudinal p/w (SECONDARY) from weighted FP
observations; evaluate on HELD-OUT. Encodes the G1-frozen protocol. Close: runs on a small fixture green; leakage-free
(train/held-out disjoint); tests green. NO real compute yet (that's G7).

**G7 (reasoning, my context) — EXECUTE bounded held-out compute + verdict.**
Detached headless (Start-Process hidden, OPENBLAS/OMP=4, liveness-checked), bounded to the frozen split. Produce:
held-out learned-vs-clock numbers (PRIMARY grip + SECONDARY longitudinal); sandbagging-discount demo; FP×regime
coverage + σ-vs-Q map; non-circularity audit (mass-cancel proof for grip; explicit chain for longitudinal); #646
disposition (bounded demo done + full re-pop handback ETA); parc-fermé/process-noise disposition. Honest-null reported
plainly. Verdict → wave8-513-verdict.md.

## Surfaced decisions (to Admiral)
- Single cold-critic (not full panel): the two design-it-twice alternative authors already served as an adversarial
  panel (attacked A's dispositions, surfaced the toy-risk). Bias-to-yes; panel skipped-with-reason.
- #646 full re-pop handed back (bounded demo here) — reap-trap prudence on the heaviest phase.
- Parc-fermé full per-team×season fitted distribution bounded-deferred; the weekend process-noise chain framing is
  carried in G3's weighting + G7's report.
- Gate framing (grip-primary / longitudinal-secondary) — the load-bearing scientific choice; surfaced for redirect.

## Untaken roads (named)
- Candidate B (integration-first, execute #646): rejected as primary for reap-trap prudence; its freeze-mass-first and
  freeze-protocol-first sequencing ADOPTED.
- Candidate C (grip-only minimal): rejected as sole gate for toy-risk; its structural-non-circularity grip anchor
  ADOPTED as the clean PRIMARY.
