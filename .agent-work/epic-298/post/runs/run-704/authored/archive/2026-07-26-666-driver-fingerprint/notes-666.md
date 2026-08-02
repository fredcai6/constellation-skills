# notes-666 — DriverFingerprint working notes

## Bounded slice provenance + commander audit (input for G1 + G4)
- **DB (uncommitted, gitignored):** `.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db`
- **Generated:** 2026-07-26, offline, via `scripts/build_class_utilization_observables.py` (#664 pipeline),
  pinned interpreter, `PYTHONPATH=.`. Reads MAIN-checkout data (physics_estimates.db full 2023-Q coverage,
  telemetry_store.db, damage_integrals.db, f1_data_2023.db). No online FastF1 calls.
- **Slice:** 2023 **Q**, 4 circuits — Monaco R6 (**street**), Spain R7, Great Britain R10, Belgium R12
  (permanents + 1 street) × 4 drivers **VER, PER, LEC, SAI** × 6 classes = **96 rows**.
- **Audit (offline / no contamination):** all `g_sigma_onesided`=0 (grip store empty — expected soft-degrade);
  `time_deficit_s` 96/96, `deployment_share` 96/96 populated; `sigma_lapsampling` 0/96 (dormant-NULL, expected);
  rounds present are exactly {6,7,10,12} (no round>cutoff contamination); session_type=Q only.
- **Severity-cell support (real imbalance — good for exercising invariants):** per severity class there are
  16 driver×circuit cells; avg n_points c0=340.4, **c1=1.3 (THIN — near the 1.0 unresolved floor)**, c2=191.3,
  c3=22.6. The class-across-drivers parent has 4 drivers × 4 circuits per class of real signal.
- **k=4 corner-severity cells** = `severity:2023:v1:c0..c3`. `straight` + `braking_zone` present in the store
  but EXCLUDED from the fingerprint cells (straight = confounded negative control; braking_zone = seg-type
  label, not a severity class).

## Honest support-size + shrinkage statement (G4 bounded validation, real 2023-Q slice)
Measured, NOT asserted. Slice = 4 circuits (Monaco/Spain/GB/Belgium), 4 drivers, k=4 severity classes.
Real per-cell raw support (n_points, per driver×circuit): c0≈340, **c1≈1.3**, c2≈191, c3≈22.6 → a genuine
imbalance that exercises the thin-cell path. Behaviour on the real fit:
- **c1 is a measured-null at `as_of_round=6/7`** (recency-effective support 0 → `unresolved` for all 4 drivers;
  an `unresolved` row is written, never a missing row — k=4 always).
- **c1 becomes resolved at `as_of_round=10/12`** (recency-weighted support ~3.8–4.9 clears the 1.0 floor once
  GB/Belgium enter the cutoff). At resolution, its unfloored σ (0.094) widens ~22× to 2.066 via the class-level
  `shared_floor = sqrt(var_circuit)` (#675), and its point shrinks much closer to the class-across-drivers parent
  (Δ≈0.067) than to the driver's own overall level (Δ≈1.16) — the intended hierarchical shrinkage under thin
  support. This IS the "cells shrink to the parent" measured-null-adjacent outcome the ruling anticipated: a
  COMPLETE, successful deliverable, honestly small.
- Well-supported cells (c0/c2, support ~190–340) carry the class `shared_floor` too (priced once) but shrink far
  less — their driver-vs-class signal survives.
- Both channels (time_deficit, energy deployment) fit and populated. G σ⁺=0 throughout (grip store empty) →
  point values byte-identical to the no-G fit (invariant preserved).

## #560 reconciliation (thin-fit acceptance floor — prose only, non-blocking; #560 not solved here)
#560 asks whether a thin fit should be ACCEPTED AT ALL (a hard sample floor below which the fit is rejected).
#666 answers a DIFFERENT, complementary question one layer up: a thin CELL is always ACCEPTED into the fingerprint
(k-cells-always-populated is a structural invariant — no cell is ever dropped), and its thinness is PRICED ONCE at
fit time via σ-widening (the class `shared_floor` + the count-driven `predictive_t` epistemic term) and, below
`FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` (1.0), marked `unresolved` rather than carrying a false point. So the two
layers do NOT contradict: #560's "reject the fit" is an UPSTREAM (observable-production) gate on whether a session's
estimate is trustworthy enough to emit; #666's "price and mark, never drop" is a DOWNSTREAM (fingerprint-assembly)
policy that a consumer needs exactly-k addressable cells and an honest σ/`unresolved` flag rather than a hole. If
#560 later imposes an upstream floor, #666's `unresolved` status is the natural sink for a cell whose observables
#560 declined to emit — they compose, they don't fight. Recommendation: keep #666's price-and-mark policy; let
#560 decide the upstream emit floor independently.

## Map impact (staged prose for the epic CLOSEOUT cartographer reconcile — do NOT edit docs/architecture)
See `.agent-work/666-driver-fingerprint/666-cartography/map-impact.md`.

## #675 verdict (G1-integrate — commander adjudication, delegated: cites LAUNCH_ORDER §BINDING PRE-RULING)
**VERDICT: class-axis `predictive_t` under-coverage GENERALIZES to the real driver×class fit → APPLY a
class-level `shared_floor` in G3 (per the ruling).** Evidence (`coverage_675_verdict.json`, N_REPS=200 over
the real bounded-slice support structure, level 0.80):
- TIME channel: class coverage 0.281 [0.250, 0.314] — CI upper 0.314 < 0.60 bound → generalizes.
- ENERGY channel: class coverage 0.335 [0.302, 0.369] — CI upper 0.369 < 0.60 bound → generalizes.
- Driver axis: 0.349 (time) / 0.309 (energy) — ALSO under-covers here.

**Adjudication of the driver-axis caveat (within latitude; not a float):** The class axis has EXACTLY k=4
classes ALWAYS (structural), so its few-groups under-coverage is DURABLE — this is the #665/#675 phenomenon
and the ruling's condition is squarely met. The driver-axis under-coverage is a BOUNDED-SLICE artifact (only 4
drivers here); #665's many-driver synthetic showed the driver axis calibrates ~0.90–0.96 at production driver
counts, so it resolves at full-season scale. Therefore: floor the CLASS level only in this build (in #675
scope); do NOT floor the driver-overall level (out of #675 scope, premature). The driver-axis question is
carried as triage candidate tc1 for #560 (thin-fit floor) / #670 (full season). #675 CLOSED with this PR.

**G3 derivation instruction (refinement over the synthetic recommendation):** the verdict's
`shared_floor=0.30` (time) / `0.0156` (energy) are the SYNTHETIC injected class-effect sigmas used to
demonstrate the harness. In the PRODUCTION fit the class-level `shared_floor` MUST be DERIVED FROM THE REAL
FIT's own class-effect variance component — `sqrt(fit_two_way.var_circuit)` (the between-class spread), per
channel — applied ONCE via `pool_random_effects(shared_floor=...)`, mirroring `_shared_floor_for_param`'s
data-derived median pattern. NOT a frozen literal. Byte-identical-point invariant preserved (floor only
widens σ).

## #560 reconciliation (to be filled at G4-integrate)
