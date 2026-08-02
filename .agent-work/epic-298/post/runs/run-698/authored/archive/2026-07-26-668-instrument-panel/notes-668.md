# notes-668 — working notes + map-impact prose (for epic-659 closeout cartographer reconcile)

**Map fence honored:** this run did NOT touch `docs/architecture/*`. The structural delta below
is staged for the epic-closeout cartographer (with `668-cartography/MAP_DELTA.md`).

## What #668 added (structural delta)
- **NEW component `struct:physics.instrument_panel`** — `src/physics/instrument_panel/`
  (`__init__.py`, `variance_decomposition.py`, `replication.py`, `sector_scorecard.py`). A
  **read-only diagnostic panel** that SIZES the driver-utilization signal via four fixed
  instruments; it NEVER gates Build 2/3 (owner ruling). Pure modules with injected-seam synthetic
  tests; the one impure entry is the report script.
  - `variance_decomposition.decompose_segment_time_variance` — car-reference / driver-utilization
    (FLOOR) / residual shares via the additive `TwoWayPool` (no interaction term).
  - `replication.py` — golf-corrected (DOUBLE-CENTERING) cross-circuit split-half replication +
    out-of-sample Student-t σ-honesty (with main-effect-margin widening) + per-class channel
    comparison. `frozen_replication_thresholds()` consumes the signed frozen set.
  - `sector_scorecard.py` — composed-sector position-sum construction check + Student-t
    distribution-calibration, gating only on the frozen `SECTOR_CALIB_GROSS_MISCALIB_BOUND`.
- **Frozen-constant delta** — `src/physics/layer2/frozen_constants.py` gained the OWNER-SIGNED
  `REPLICATION_*` set (2026-07-26): `REPLICATION_MIN_SUPPORT_N=15.0`, `REPLICATION_THRESHOLD=0.5`,
  `REPLICATION_R_FLOOR_CAP=0.7`, `REPLICATION_R_FLOOR_SUPPORT_REF=100.0`,
  `REPLICATION_CHANNEL_TIE_MARGIN=0.1`. The DEFERRED note (`decision:replication-deferred`) is now
  resolved.
- **NEW report artifacts** — `scripts/instrument_panel_668_report.py` (the runnable generator) +
  `docs/physics/instrument_panel_668_gb2023q_report.md` (+ `.json`) — the versioned cross-circuit
  real-data report.
- **Consumer boundary (ruled at #667, honored here):** the panel reads UN-AGGREGATED cells
  directly (`DriverFingerprintStore.get_fingerprint` / `driver_class_observables`), NOT through
  the `#667` join. No #660/#664/#666/#667 producer was mutated.

## Decision anchors introduced (for the cartographer to record with @grade)
- `decision:golf-correction-is-double-centering` — remove BOTH driver and class main effects
  (a data transform, not a fitted interaction term); the interaction residual is what replicates.
  @grade: settled/measured (cold-critic-forced + independently re-derived: within-class
  double-center ≡ demean to 1e-16, so the interaction r must span classes; negative control
  r_double=0.0006 vs r_demean=0.685).
- `decision:split-half-unit-cross-circuit-2v2` — owner-ruled; the 4-circuit slice enables the
  statistically-correct repeated-measurement unit. @grade: settled/human.
- `decision:replication-frozen-set-signed` — the F12 REPLICATION_* set, owner-signed 2026-07-26.
  @grade: settled/human.

## Claims / evidence surfaces
- `claim:golf-correction-removes-skill` — verified by the 3-arm + negative-control synthetic
  falsifier (interaction-bearing generator).
- `claim:driver-utilization-floor-sized` — real result on the slice: driver-utilization variance
  share = 0.0 (genuine method-of-moments clip); ~2-3 severity classes replicate (c0/c3 on the
  utilization channel), c2 unresolved, c1 unmeasurable. Small signal, honestly sized (no-frame-kill).
- `claim:no-leakback` — strictly-pre `as_of_round` threaded; official sectors only as the post-hoc
  target (a real iteration bug was caught by the no-leakback test and fixed).

## Real-data headline (from the versioned report)
- Instrument 1: driver-utilization FLOOR = 0.0 (car-reference ~0.83–0.87 share).
- Instruments 2+3: cross-circuit 2v2 — c0 r≈0.84, c3 r≈0.81 replicate on utilization; c2 r≈0.46
  (< r_floor) unresolved; c1 unmeasurable (< MIN_SUPPORT_N). σ-honesty 144/144 covered (conservative).
- Instrument 4: position-sum construction PASSES; per-FIA-sector composition NOT constructible from
  the on-disk class grain (severity classes span sectors; no mapping on disk) → routed to #670;
  honest whole-lap substitute reported with the min-n_eff inflation caveat.

## Bounded scope
Cross-circuit on the 4-circuit on-disk slice (Belgium/GB/Monaco/Spain Q × LEC/PER/SAI/VER). Full
season / broader breadth → #670 (HITL). The per-FIA-sector segment-tiling gap also → #670.

## Open triage candidates (drained at the spine triage step)
- tc1: `tests/unit/physics/test_damage_tractability.py` stalls the physics region suite (pre-existing, unrelated).
- tc2: duplicated axis-grouping helper (`main_effect_margin_uncertainty` vs `_axis_means`) — simplify-pass candidate.
