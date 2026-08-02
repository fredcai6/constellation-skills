# GATE PROTOCOL — #513 Phase 4 FP-fits held-out falsifiable test (FROZEN before any number)

**Frozen:** 2026-07-19, before any held-out number is computed. **SPLIT_HASH:** `f1725bd81cd3eefa`
(sha256 of the weekend list + method). Any change to the split/method after this point is a
protocol break and must be recorded as such. Encodes all 12 cold-critic findings (CRITIC_TRIAGE.md).

## 0. The falsifiable claim
Weighting FP observations by their OWN properties (compound, estimated fuel, run-purpose,
track-evolution) predicts qualifying-representative car capability BETTER than weighting purely by
clock-distance-to-Q, on held-out weekends. Honest-null (learned ≤ clock) is a COMPLETE result.

## 1. Data / split (hashed)
- Season 2023; the 16 standard-format weekends with full FP1+FP2+FP3+Q telemetry:
  Abu Dhabi, Australia, Bahrain, Canada, Great Britain, Hungary, Italy, Japan, Las Vegas, Mexico,
  Miami, Monaco, Netherlands, Saudi Arabia, Singapore, Spain.
- **Split = LEAVE-ONE-WEEKEND-OUT (LOWO):** learned weighting is re-fit on the other 15 weekends,
  then predicts the held-out weekend. 16 folds → 16 paired per-weekend deltas. Chosen over a single
  train/held-out split to maximize N for the paired significance test (F7) and avoid an arbitrary split.
- Clock baseline requires no fitting (parameter-free, or a single decay constant fit per-fold on train).

## 2. Targets
- **PRIMARY (clean, mass-free):** per-car Q grip capability = per-car Q `apex_pace` (from
  `apex_extract.extract_apex_observations` → `capability.apex_pace`; mass CANCELS — structural
  non-circularity, F10). Read on the DIVERGENT cases (§6).
- **SECONDARY (caveated):** per-car Q longitudinal power-to-weight. Reported ONLY at a MATCHED
  fuel-uncertainty stratum (bin FP observations by fp_mass intercept σ; require learned to beat clock
  WITHIN matched-σ bins) OR explicitly labeled "confounded, not evidential" (F1). fp_mass intercept σ
  is propagated into all longitudinal predictions (F2/F10); the secondary is meaningful only if that σ
  is bounded, else it is structurally null and reported as such.

## 3. Two arms
- **CLOCK baseline:** each FP observation weighted by clock-distance-to-Q (session-start-time gap to
  Q; nearer = higher). Blind to compound/fuel/run-purpose. A REAL baseline (it captures track rubber-in,
  which genuinely helps grip), not a strawman — that is exactly why the primary is a hard test (F4).
- **LEARNED:** `w(compound, fuel_est, run_purpose, track_evolution) ∈ [0,1]`, fit on train weekends
  (per fold) to best predict the Q target from FP observations. No session identity as a feature.

## 4. Prediction + metric
- Per-car FP-derived capability = weighted aggregate of that car's FP observations under each arm.
- Per-weekend metric (across cars): Spearman rank correlation (predicted vs actual Q per-car capability)
  and centred RMSE.
- **Significance (F7):** N=16 LOWO folds; PAIRED BOOTSTRAP (10k resamples) over the 16 per-weekend
  (learned − clock) metric deltas. **PASS iff** the 95% CI of the mean paired delta favors learned
  (Spearman higher AND/OR centred-RMSE lower) AND the divergent-case read (§6) confirms it. Otherwise
  HONEST-NULL, reported plainly.

## 5. Emergence — the calendar-in-disguise guard (F3)
Track-evolution ≈ monotone with session identity (FP1<FP2<FP3). A learned weighting that collapses to a
monotone function of session-mean track-evolution has smuggled "later session = better" and FAILS.
**Test:** residualize track_evolution against session identity; the learned weight MUST still respond to
the within-session residual features (fuel/compound/run_purpose) — concretely, WITHIN a single session a
lap-3 low-fuel soft push must outweigh a lap-18 high-fuel hard long-run. If the learned weight is a
monotone function of session-mean track-evolution alone → emergence FAIL (calendar in disguise).

## 6. Divergent-case read — the discriminating test (F4)
The primary verdict is READ ON the observations where clock and learned DISAGREE most
(|w_learned − w_clock| in the top tercile) — early-session soft low-fuel push laps (FP1/FP2 quali-sims)
that clock under-weights but learned up-weights, and late-session high-fuel long-runs that clock
over-weights but learned down-weights. Pooling everywhere clock and learned coincide dilutes the test
(F4). If clock and learned agree nearly everywhere (thin divergent set), the test is INCONCLUSIVE and
reported as such — not a pass.

## 7. Leakage guard (F6)
All normalizers (compound-softness scale, burn/fuel calibration, feature z-scores) are fit WITHIN the
training fold only. `weekend_state`/track-evolution consumes NO Q-session input (audited in G4 + G7).
Held-out Q capability is the target only; it never enters the learned weights or features.

## 8. Sandbagging demonstration (F8)
Data-defined proxy (no cherry-pick): the car-weekend with the largest positive FP-best-pace → Q-pace
improvement is the sandbagging proxy. Falsifiable demo: **learned_weight < clock_weight** on that
car-weekend's FP observations (clock is BLIND to sandbagging → over-weights the sandbagged FP3; learned
down-weights it). Direction frozen here. A single-weekend ILLUSTRATION, not evidence.

## 9. Honest-null #628 ship contract (F12)
FP fits still LAND (unbiased fp_mass) regardless of the gate outcome. Under learned ≤ clock, the FP
product ships the BEST-PERFORMING arm's weighting (clock-distance if clock wins) — the
representativeness-weighting CLAIM is null while the FP-fit capability still ships downstream.

## 10. Driver-utility transfer (F11)
Car-capability representativeness is the TRACTABLE FALSIFIABLE PROXY for "does observation-property
weighting work at all." Transfer argument: the same observation properties (low-fuel, push, soft,
rubbered-in) that make a lap Q-representative for capability also make it the cleanest driver-utility
(v_ideal−v_real) demonstrator. A driver-utility-side held-out check is a NAMED FOLLOW-ON if primary passes.

## 11. Non-circularity contract
- fuel-accounting → fp_mass (independent of any fit; no fit output feeds fp_mass).
- Grip/apex mass-CANCELS → PRIMARY is structurally non-circular.
- Longitudinal CdA and p/w BOTH consume fp_mass (PowerDragView takes mass_kg, F10) → fp_mass intercept
  σ propagated; SECONDARY reported at matched-σ or labeled confounded. Documented in the G7 audit.

## 12. Compute (F9) — filled at G7
Demo weekend-N and pre-measured single-session apex-extraction wall-clock are recorded at G7 BEFORE the
batch. G7 runs the frozen LOWO or a DOCUMENTED reduced fold set if compute-bound (the split stays frozen;
any fold reduction is stated with its reason). cumulative_track_laps column population is DEMO-scoped
(NULL elsewhere self-heals; full backfill deferred to #646). Detached headless, OPENBLAS/OMP=4, liveness-checked.
