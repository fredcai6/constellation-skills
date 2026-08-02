# Implementer Handoff — G3 (held-out gate harness)

## Gate
`g3-implement` (#628 Phase 3b — the LOAD-BEARING falsifiable gate). Worktree **C:/Programs/f1-628** ONLY.
Bespoke scripts need `PYTHONPATH=C:/Programs/f1-628`. G1 (observable) + G2 (latent estimator) are merged on
this branch.

## Task
Build `src/physics/utilization/driver_utility_gate.py`: the **held-out gate harness** that, given
per-(driver,session,axis) observable deficit rows (G1 schema) and a train/held-out round split, fits the
driver-utility latent on TRAIN (via G2) and evaluates BOTH gate limbs OUT-OF-SAMPLE on HELD-OUT, plus a
leakage self-test and a non-gating reputational read.

## Protected Intent (anti-circularity, F4)
The gate is falsifiable ONLY because (a) δ is fit on TRAIN sessions and evaluated on HELD-OUT sessions
(out-of-sample — never self-inclusive), and (b) the deficit uses a strictly_pre causal ceiling. The harness
must never predict a held-out point using that point's own value. A negative result (utility does NOT
replicate) is a COMPLETE, reportable outcome — do not tune toward a pass.

## Test Mode
TDD required — SYNTHETIC data only (do NOT run the real batch; that is G5). Construct deficit-row fixtures
with KNOWN driver utilities and verify the harness recovers/falsifies them out-of-sample.

## Close Criteria — the harness computes, per axis in {braking, slow_corner, fast_corner, straight}:
1. **RECOMPOSITION (limb 1), out-of-sample:** with `delta_driver,axis` from TRAIN, for each held-out
   (driver,session): `err_model = g_obs - delta_driver`, `err_baseline = g_obs - 0` (δ=0 = car-only). Report
   per-axis held-out RMSE_model vs RMSE_baseline and the improvement. **Falsifiable weight is on the CORNER
   axes** (braking/slow_corner/fast_corner).
2. **PER-AXIS STRUCTURE (limb 2), out-of-sample:** cross-driver variance of the **per-axis-CENTERED** utility
   `delta_centered = delta_driver - mean_over_drivers(delta_.,axis)` (subtracting the axis mean removes the
   car/calibration offset; the VARIANCE of the centered δ is the driver signal). Report centered cross-driver
   variance per axis; the PREDICTION under test is corner axes >> straight axis.
3. **STRAIGHT/POWER = CALIBRATION-CONFOUNDED NEGATIVE CONTROL** (critic SERIOUS-1): the measured probe showed
   the causal ceiling under-predicts straight speed (deficit can be negative / driven by DRS-slipstream, not
   driver skill). The harness MUST label the straight axis a confounded negative control in its output — a
   near-zero centered variance there is CONSISTENT WITH (not a validation of) "power≈0 driver utility", and
   limb-1 improvement on the straight axis is NOT evidence of driver access (δ_straight absorbs a ceiling
   bias). Do not let a straight-axis pass count toward the verdict.
4. **δ is teammate-relative** (critic MINOR-2): within-constructor δ are mutually anchored; note this and,
   where practical, report cross-constructor variance alongside all-driver variance in limb 2.

## Leakage self-test (critic SERIOUS-3 — must be genuinely powered)
A unit test proving the harness's OOS replication metric is SENSITIVE to ceiling leakage:
- Construct two synthetic held-out scenarios differing ONLY in whether the held-out session's deficit was
  computed against a CAUSAL (strictly_pre) ceiling vs a NON-CAUSAL (through-W, contaminated by the held-out
  lap) ceiling — the non-causal case shrinks the held-out deficit toward the driver's own lap.
- Assert the harness's held-out replication is **visibly INFLATED** in the non-causal case by a PRE-COMMITTED
  magnitude, on a HIGH-LEVERAGE (few-prior-sessions, e.g. early-season) configuration where one session moves
  the pool materially.
- The harness/test must document that **null inflation ⇒ EITHER the causal apparatus is immaterial here OR
  the test is underpowered — NEVER silently a pass.** Encode that as an explicit branch/assert message.

## Reputational smell-test (NON-GATING)
Provide a function that ranks drivers by resolved corner-axis δ and juxtaposes reputation — clearly labeled
`NON-GATING / smell-test only`. Never feeds the verdict.

## Allowed Scope
- NEW: `src/physics/utilization/driver_utility_gate.py`, `tests/unit/physics/test_driver_utility_gate.py`.
- READ-ONLY reuse: `driver_utility.estimate_driver_utility` (G2), the G1 row schema. Do NOT modify G1/G2.

## Specific Exclusions
- Do NOT run the real batch or produce real numbers (G5). No FastF1/telemetry here — synthetic rows only.
- Do NOT compute `observed/capability`. Work on the additive deficits.
- Do NOT build a kill switch — honest-null is a legitimate verdict the harness must be able to REPORT.

## Constraints
- `py` not `python`. Tests: `py -m pytest tests/unit/physics/test_driver_utility_gate.py -q`.
- `src.utils.simplification_limits --paths <file>` must PASS (keep functions small).
- Out-of-sample discipline: split by SESSION/round; a driver's held-out sessions never enter their own δ fit
  (LOO-clean — the `loo-residual-diagnostic` lesson: a self-inclusive metric is structurally blind to the
  over-claim it exists to detect).

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new driver_utility_gate.py; reuse G2 estimator.
- **Capability:** falsifiable held-out gate (recomposition + centered per-axis structure).
- **Constraints:** out-of-sample only; centered variance for limb 2; straight = confounded negative control;
  no observed/capability.
- **Decision:** strictly_pre causal ceiling breaks the within-session leak; cross-round leak only attenuated
  (named limit). `decision:c1_driver_utilization_design`.
- **Evidence:** δ recovered OOS on synthetic; centering removes the car offset; leakage self-test powered.
- **Confidence flag:** straight/power axis calibration-confounded (SERIOUS-1) → negative-control framing.

## Deliverable Path Check
- **Committed:** `src/physics/utilization/driver_utility_gate.py`,
  `tests/unit/physics/test_driver_utility_gate.py` — `git check-ignore` each, confirm exit 1.
- No data DB deliverable in this gate (synthetic-only).

## Required Evidence
- `py -m pytest tests/unit/physics/test_driver_utility_gate.py -q` full pass.
- Tests demonstrating: (a) known synthetic δ recovered out-of-sample (RMSE_model < RMSE_baseline on corner
  axes when a true driver signal exists; NO improvement when the true signal is zero — honest-null reachable);
  (b) centering removes a shared car offset (a pure car-offset with zero driver spread → ≈0 centered
  variance); (c) the powered leakage self-test (non-causal inflates vs causal by the pre-committed magnitude);
  (d) straight axis labeled confounded negative control in the output structure.
- `simplification_limits --paths` PASS.

## Verification Commands
```bash
cd /c/Programs/f1-628 && py -m pytest tests/unit/physics/test_driver_utility_gate.py -q
cd /c/Programs/f1-628 && py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility_gate.py
cd /c/Programs/f1-628 && grep -nE "/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_gate.py || echo NO-RATIO-OK
```

## Suggested Model Tier
stronger — the OOS discipline, centered-variance, confounded-axis framing, and the powered leakage self-test
carry real subtlety; correctness of the FALSIFIABILITY is the whole point of this gate.

## Authority
The gate design (two limbs OOS, centered variance, straight=negative-control, powered leakage self-test) is
DECIDED by the Commander (cold-critic-ratified). Do not re-open. If G2's `estimate_driver_utility` signature
differs from the G2 result doc, STOP and return.

## Stop Conditions
Stop and return if: allowed scope exceeded, out-of-sample discipline cannot be honored, the honest-null path
cannot be represented, or a cited seam mismatches source.

## Return Format
IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (pytest + simplification +
grep), assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
