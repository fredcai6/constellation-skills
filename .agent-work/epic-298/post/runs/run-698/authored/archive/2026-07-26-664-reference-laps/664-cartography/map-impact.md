# Map impact — #664 (staged for epic #659 CLOSEOUT cartographer)

**MAP FENCE honored:** cmdr-664 did NOT edit `docs/architecture/*`. This prose is staged for
the epic's SINGLE closeout cartographer reconcile per the launch order. Verified against the
final branch state (all files committed on `epic659/664-reference-laps-utilization`).

## New structural nodes (all under `struct:physics.utilization`, `src/physics/utilization/`)
- **`class_ledger.py`** (g1) — PURE class-grain time-ledger + fingerprint core. Public:
  `build_weight_matrix(segment_map) -> (W, class_ids)` (the single `(n, 2+k)` attribution
  matrix `W = hstack([seg_type one-hot {STRAIGHT, BRAKING_ZONE}, severity_membership])`);
  `class_time_ledger` / `class_time_shares` (per-class TIME-shares summing to the lap);
  `class_deficits` (per-class ABSOLUTE speed-m/s + transit-time-s deficits, no ratio);
  `dominant_class_of(W)` (derived diagnostic argmax ONLY). Consumes
  `struct:physics.segment_map.runtime`. No I/O. `DEFAULT_MIN_SPEED_MS` inherited from
  `PhysicsEstimatorConfig.simulator_min_speed_ms` (no new literal).
- **`reference_lap_product.py`** (g2) — the reference lap as a FIRST-CLASS product.
  `ReferenceLapProduct` / `ConstructorLap` / `FieldBasis`; `field_median_fingerprint()` +
  `compose_reference_lap_product()`. Promotes `SimulatedLap.lap_time_s` (previously computed
  and discarded) to a stored scalar; the circuit fingerprint = per-class TIME-shares (retires
  the #625 `regime_rollup` DISTANCE-share). Consumes `car_prior.build_car_ceiling(strictly_pre=
  True)` → `PhysicsSimulator.simulate_lap` (single canonical path) + g1 `class_ledger`.
- **`reference_utilization_store.py`** (g2+g3) — OWN-DB SQLite store (default
  `data/reference_utilization.db`, gitignored; #632). Table `reference_laps`
  (PK `year, gp_name, session_type, reference_id, map_version`; `reference_id="__field__"`
  sentinel for the field-reference fingerprint row) + table `driver_class_observables` (mirrors
  `driver_utility_observables` schema + `class`, `map_version`, `time_deficit_s`,
  `g_sigma_onesided`, energy columns; escalation columns present-but-DORMANT). estimate_store
  conventions (Row factory, create-on-construct unless `must_exist`, INSERT OR REPLACE
  idempotency, additive migrate).
- **`class_utilization_observable.py`** (g3) — per-driver per-class observable: absolute
  deficit (via g1) + a ONE-SIDED grip-G σ⁺ band (`σ⁺ = hypot(mu, sigma)` from
  `grip_store.get_grip_at`; μ NEVER shifts the point; half/truncated Student-t via
  `src.common.student_t`; G consumed NOT re-fit) + a RELATIVE energy deployment channel.
- **`class_utilization_validation.py`** (g4) — pure jackknife math: delete-d/block schedule,
  boundary-drift vs `frozen_constants.MAP_STABILITY_DRIFT_M`, per-class stability, positive
  control.
- **`scripts/build_class_utilization_observables.py`** (g4, non-map CLI) — season-CAPABLE,
  resumable, idempotent build pipeline composing g1/g2/g3 + segment-map derivation; mirrors the
  #628 `build_driver_utility_observables.py` pattern; own-db; G soft-degrades when the grip
  store is absent.

## New decision anchors (to record)
- **`decision:class-attribution-membership-faithful`** — attribution is a single `(n, 2+k)`
  weight matrix `W = seg_type one-hot ⊕ severity_membership`; NO argmax collapse (argmax is a
  derived diagnostic only). `@grade: settled/measured` (design-it-twice; the decisive axis was
  jackknife-meaningfulness — argmax flips whole segments and makes the gate measure
  quantization noise). Leans g1, g4.
- **`decision:field-reference-fingerprint`** — the circuit fingerprint = the FIELD-MEDIAN
  across the weekend's present constructors of each constructor's simulated-lap per-class
  TIME-shares (renormalized); per-constructor scalar `lap_time_s` stored separately; the
  fingerprint is field-CONDITIONED (field-basis descriptor persisted), not a pure-circuit
  invariant. `@grade: guess · settle: g4 drop-a-constructor stability` (commander latitude).
- **`decision:g-one-sided-directed-uncertainty`** (epic-owner pre-ruling, recorded here as the
  consumer contract) — G is consumed as μ=0, σ⁺ half-Student-t; the utilization POINT deficit
  is unchanged; only σ gains a one-sided component. `@grade: settled/inherited`.
- **Energy FINDING (g3):** a single KINETIC-energy (½v²) channel suffices for the relative
  deployment observable; total-mechanical-energy (½v²+g·h) is NOT needed because the
  deployment proxy reads only KE CHANGES normalized to the car's own baseline, so `g·h` is
  common-mode on a fixed circuit and an absolute SOC/kW offset differentiates to zero.

## New claims / evidence surfaces
- **`claim:attribution-robust`** — verified-by the g4 delete-d/driver-block jackknife
  (2023 Q GB round 10, B=30): per-class deficit IQRs 0.0015-0.017 s / 0.009-0.057 m/s;
  boundary drift mean 0.74 m / max 1.15 m ≪ the frozen 10 m `MAP_STABILITY_DRIFT_M`; POSITIVE
  CONTROL FIRED (injected corner→straight leak 0.159 vs 0.0). Independently recomputed by the
  g4 reviewer to 6 decimal places. Reported as an INSTRUMENT (allocation-not-gating), not a
  pass/fail. Artifact: `.agent-work/664-reference-laps/artifacts/jackknife_attribution.json`.
- **`claim:deficits-sum-to-lap`** (CONSTRUCTION check) — per-class transit times sum to the
  lap; class time-shares sum to 1. Guarded by the `W`-row-sum-to-1 invariant.

## Packet-drift note for the closeout cartographer
The `docs/architecture/packets/physics.md` "utilization" section (C1 #510 / #628 era) predates
this epic. It should gain the six new nodes above under `struct:physics.utilization`, the three
decisions, and the two claims. The `#625 regime_rollup` DISTANCE-share caveat is now RETIRED by
the simulated-lap TIME-share fingerprint — update that note.

## Stale forward-reference finding (TRIAGE — the seeded/supersede rename)
`segment_map/store.py:24,148-163`, `identity.py:33-34,84-100`, and `derivation/derive.py:234`
forward-reference **"#664 = Build 3, the SegmentMap seeded/supersede write path"** — a
DIFFERENT deliverable than this issue's actual scope (reference laps + utilization). The
seeded/supersede `write` branch remains `NotImplementedError` (correctly OUT of #664 scope per
the launch order). These three comment references are STALE issue-numbering and should be
re-pointed to whatever issue now owns Build 3 (floated to the Admiral; a triage candidate).
