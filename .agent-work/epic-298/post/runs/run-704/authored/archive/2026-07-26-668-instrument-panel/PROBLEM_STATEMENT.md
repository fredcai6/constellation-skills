# #668 Instrument Panel — Consolidated Problem Statement

**Mode:** delegated. Principal = the frozen `LAUNCH_ORDER-668.md` (Admiral = team-lead, `main`).
Reconciled against the actual worktree code (ef97d799), not just the order's framing.

## The ask (from the launch order)
Build **Build-1's exit instrument — a four-instrument panel that SIZES the driver-utilization
signal, never gates go/no-go.** Emit a written, versioned report on the Great Britain 2023-Q
on-disk slice with all four instruments + the frozen constants used. No output halts Build 2/3.

## The four instruments
1. **Variance decomposition** — split segment-time variance into **car-reference /
   driver-utilization / residual** shares. THE "set the size" instrument. Driver-utilization
   share reads as a **floor**. Car-reference ← #664 `reference_laps`; driver-utilization ←
   #666 fingerprint cells (un-aggregated, read directly).
2. **Residual split-half replication (golf-corrected — LOAD-BEARING)** — per-class fingerprint
   replication computed **AFTER removing overall skill**. Raw replication smuggles overall
   skill back in and flatters. Doubles as a **σ-honesty check** (do cells replicate within
   their stated Student-t uncertainty?). Thresholds + support-count-scaling formula = frozen
   set (F12 gate).
3. **Pre-registered channel comparison** — run the replication per class in BOTH channels
   (time-deficit `utilization` AND energy `deployment_share`). **Whichever channel replicates
   better in a class earns join weight there.** Protocol REGISTERED (frozen) before real-data
   run; winner decided empirically after.
4. **Composed-sector scorecard** — segment predictions sum into FIA sectors, validated against
   **official sector times on disk**. (a) position-sum exactness = construction check;
   (b) predicted sector-time **distribution calibration** (central + coverage) = the real
   anchor. DIAGNOSTIC for size; **GATING only on the frozen gross-miscalibration sanity bound**.

## Reconciliation of the order's assumed baseline against the code (VERIFIED)
- **#660 `src/physics/layer2/frozen_constants.py` explicitly DEFERS the `REPLICATION_*` set to
  THIS panel** (decision:replication-deferred): "added to THIS SAME MODULE... once the #668
  commander has produced a 1-page pre-registration proposal grounded in the actual 2023
  driver×class support distribution + a noise model, for Fred's signature BEFORE that panel's
  real-data run." → the F12 gate is precisely this proposal.
- **The scorecard triple is ALREADY FROZEN in #660**: `SECTOR_CALIB_COVERAGE_NOMINAL=0.90`,
  `SECTOR_CALIB_COVERAGE_OBSERVED_MIN=0.85` (diagnostic), `SECTOR_CALIB_GROSS_MISCALIB_BOUND=0.50`
  (GATING). → I **consume** these, mint nothing for the scorecard.
- **#666 `src/physics/fingerprint/frozen_constants.py`** freezes `FINGERPRINT_NOMINAL_COVERAGE_LEVEL=0.80`,
  `FINGERPRINT_UNDER_COVERAGE_BOUND=0.60`, `FINGERPRINT_RECENCY_HALFLIFE_ROUNDS=5.0`,
  `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR=1.0`. → consumed, not re-minted.
- **What I MINT** (new named set, appended to #660's layer2 module, F12-clean): `REPLICATION_THRESHOLD`,
  `REPLICATION_MIN_SUPPORT_N` + the `r_floor(n)` support-count-scaling formula, and the
  **channel-comparison registration** (decision rule + tie margin).

## Structural facts that shape the design (source-verified)
- **`TwoWayPool` (`pooling.py`) is purely ADDITIVE** — `y = grand_mean + team_effect +
  circuit_effect + resid`, **NO driver×class interaction**. Convention: teams=drivers,
  circuits=classes. Driver-overall skill = `grand_mean + team_effects[driver]`; the per-class
  deviation `circuit_effects[class]` is SHARED across drivers; any genuine driver×class
  interaction currently lives entirely in `var_resid`. → **The golf-correction is a
  per-driver demean across classes** (subtract the driver's own mean over its k classes);
  what remains is the per-class residual profile that replication must test. Model-light and
  robust.
- **Un-aggregated substrate** = `driver_class_observables` table (own DB
  `reference_utilization.db`, or the #675 slice `.agent-work/666-driver-fingerprint/artifacts/
  fp_slice_2023Q.db`). Per (driver, class, round): `time_deficit_s`, `deployment_share`,
  `n_points`, `g_sigma_onesided`, `sigma_lapsampling`. The #666 `DriverFingerprintStore` cells
  are the AGGREGATED form; the panel reads the un-aggregated cells directly (store read API /
  observables), **NOT the #667 join** (consumer boundary, ruled at #667).
- **Coverage seam** = `src/common/student_t.py` `predictive_t(mu, sigma, n_eff, nu_loss, rule)`
  → `PredictiveT.interval(level)` / `.cdf` (PIT). Non-Gaussian; heavy-tailed σ propagated
  honestly (owner ruling #5: no baked normality).
- **FIA sector times on disk**: `data/f1_data_2023.db` `lap_times.sector{1,2,3}_time` (REAL
  seconds), GB-Q = `session_id 559` / round 10, via `DatabaseManager.get_lap_times`.
  Distance→sector-line mapping already exists in `src/physics/segment_map/derivation/
  sector_nesting.py` (offline, never FastF1).
- **Composition / corner-share** for the scorecard's per-class weighting = #664
  `ReferenceUtilizationStore.get(...).fingerprint` (field-median per-class TIME-share). GB-2023-Q
  reference product lives in the #664 archive own-DB.
- Reusable precedents: `scripts/fingerprint_class_coverage_675.py` (Clopper-Pearson binomial
  CI + `predictive_t.interval(0.80)` coverage) and `scripts/pooling_imbalance_validation_665.py`
  (synthetic driver×class generative model, `draw_ground_truth`, `run_profile`) — directly
  reusable for synthetic instrument tests.

## GENUINE GAP surfaced to the Admiral (design decision inside my latitude, floated for awareness)
The golf-corrected **split-half** replication needs a per-observation substrate to split into
two halves. The GB-2023-Q bounded slice is a **SINGLE session** (16 drivers × 4 severity
classes = 64 aggregated cells; one round). **Cross-session / cross-round split-half is
unavailable on this slice.** → the split-half unit must be defined **within-session** (a
lap-level split of each driver's laps: e.g. odd/even laps or first/second half, recomputing the
per-class `time_deficit_s` profile on each half). This IS a pre-registration decision and goes
INTO the F12 replication-protocol registration; it is mine to design and register, then float
to the Admiral with the rest of the frozen set. Not a blocker — noted so the Admiral/owner
sees the bounded-slice consequence when signing off the replication protocol.

## Owner rulings (binding — carried into every gate)
1. No frame-kill — a small/zero size is a COMPLETE result; the panel sizes, never halts.
2. F12 frozen set pre-registered + Admiral/owner sign-off BEFORE the real-data run (HARD GATE).
3. Pre-quali — cells stay strictly-pre (`as_of_round` threaded); no sector-outcome leakback.
4. Lowest dimensionality — EXACTLY the four instruments; no bespoke model, no interaction terms.
5. No baked normality — Student-t coverage throughout.

## Scope
Build **season-capable**, validate **GB 2023-Q only** (only on-disk slice). Multi-circuit
breadth → #670 (HITL, not run here). Report the 1-circuit bounded-scope note explicitly.

## Out of scope
Any Build-2/3 halting gate; the full season run (#670); correlation-aware σ (#700); fit-cutoff
enforcement (#701); moving G's μ off zero (#678); 3-circuit regeneration (#670).
