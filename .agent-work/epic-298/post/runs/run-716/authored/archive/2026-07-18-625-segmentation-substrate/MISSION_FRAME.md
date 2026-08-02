# Mission Frame — #625 Phase 1 segmentation substrate

## Intent
Extend `struct:physics`'s `segment_classifier.py` from hard per-sample regime tags to
soft/fractional corner property-class membership, add a straight-arc grouping capability
(length/duration/top-speed) and a lateral-g/radius descriptor axis, and produce a per-circuit
regime time-share rollup — with a mandatory falsifiable stability check — so Phase 2
(four-layer weekend-state model) and Phase 4 (FP extension) have a load-bearing, honestly
validated observability substrate to consume.

## Affected Capabilities
- `serves purpose:physics_estimation` (`struct:physics`, `parameter_estimator.py`) — the
  container `segment_classifier.py` feeds; this run extends the classifier's OUTPUT shape
  (adds soft membership + arc grouping), does not change the estimation orchestration itself.
- Per-session views (`struct:physics.layer2`: `braking_view.py`, `lateral_view.py`,
  `traction_view.py`, `power_drag_view.py`, `coast_view.py`) — each already consumes a
  specific regime slice; this run's "observability router" documents which
  segment/property-class carries evidence for which of these views' basis parameters. No
  view code changes.
- Wear pipeline `struct:physics.layer2` `grip_bin_obs.py` / `damage_batch.py` — read-only
  consumer this run (the `grip_bin_obs` table is the rollup's data source); not modified.

## Examples / Events
- `data/damage_integrals.db` `grip_bin_obs` table (612,615 rows, 2019-2026, ~22 circuits) —
  the concrete dataset the rollup and lateral-g/radius axis are built from.
- x6 excursion (`.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x6-circuit-demand-RESULT.md`)
  — prior finding that fingerprint CSVs are wear diagnostics, not a demand profile, and that
  `segment_classifier` tags every sample but nothing aggregates per circuit.

## Structural Anchors
- `struct:physics` — `src/physics/segment_classifier.py` (the file this run extends).
- `struct:physics` — `src/physics/physics_data_models.py` (`_VALID_REGIMES`, `SegmentedLap`,
  `KinematicSample` — the regime taxonomy and flat-sample container this run's new grouping
  sits alongside).
- `struct:physics.layer2` — `src/physics/layer2/arcs.py` (`_contiguous_runs`,
  `identify_braking_arcs`, `BrakingArc`) — the existing contiguous-run pattern the new
  straight-arc grouper mirrors.
- `struct:physics.layer2` — `src/physics/layer2/grip_bin_obs.py` (`N_BINS=32`,
  `CORNER_GATE_MS2`) — the rollup's data source; per-lap-normalized bins, corner-gated only.
- `src/evo_predictor/circuits.yaml` — read-only, low-trust `downforce` field (ruled out as
  the F12 independent proxy — see Map Confidence below).

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — physics stays clean of `evo_predictor`/
  `latent_power`/`compound_prior` imports; the new modules must not import evo.
- `constraint:canonical_data_source` (ORCHESTRATOR_CONTEXT.md) — DB is the only authoritative
  analysis source; the rollup reads `data/damage_integrals.db` (SQLite), never FastF1 direct.
- Pre-ruling #1 (soft/fractional, NOT hard one-corner-one-property; class count
  support-driven). Pre-ruling #2 (lateral axis from `grip_bin_obs`, NOT fingerprint CSVs).
  Pre-ruling #3 (drop `coast_frac` from demand inputs). Pre-ruling #4 (falsifiable gate
  mandatory). Pre-ruling #6 (no `circuits.yaml`/production-default writes).

## Decision Anchors & Decision Pressure
- `decision:two_cycle_external_anchor_design`, `decision:decoupled_1d_longitudinal` — govern
  the trajectory/longitudinal estimation this run does NOT touch (segment_classifier reads
  `curvature`/`a_lateral` already computed upstream).
- `decision:regime_readiness_rubric` — the C3 finding (car-vs-car separability is
  circuit-dominated, `frac_team` 0-4%) that motivates WHY a per-circuit rollup matters:
  circuit conditioning is where the real structure lives.
- Decision pressure (floated in PROBLEM_STATEMENT.md, not blocking): live-classifier
  straight-arc enrichment (length/duration/top-speed) vs. the historical rollup's
  bin-coverage-ratio approximation are two different data paths for the two different named
  deliverables — an engineering-breakdown call within inherited latitude, recorded not
  floated as a blocking decision.

## Claims / Evidence Surfaces
- Claim: "the soft-membership substrate is not overfitting circuit-specific noise" — checked
  by the F12 falsifiable gate (held-out-circuit stability, Hungarian-matched cluster-mean
  agreement between two independently-fit mixtures on non-overlapping circuit subsets).
- Claim: "the rollup reproduces known circuit character" — checked by the Monza/Monaco
  sanity read (necessary, not sufficient per the gate).

## Map Confidence / Staleness / Disputes
- `src/evo_predictor/circuits.yaml` `downforce` — LOW CONFIDENCE / provisional (2026 rows
  carry explicit "carried from 2025" comments, e.g. lines 349/442/540). Alters the plan: this
  run does NOT use it as the F12 independent-circuit-character proxy (would validate the
  substrate against a hand-tag the mission itself frames as low-trust); the held-out-circuit
  stability check is used instead.
- `grip_bin_obs.bin` stability — MEDIUM CONFIDENCE. Source-verified (this run's own research,
  not a pre-existing map claim) as per-lap-normalized, not a stable cross-session arc-length
  index. Alters the plan: no per-corner-identity claim is made from bin position; the rollup
  and mixture both operate on POOLED per-circuit statistics (bin-coverage-ratio, descriptor
  distributions), never on "bin N is always corner X."
- No existing map node describes a straight-line top-speed/length data source. Verified
  absent by this run's research (not merely unread) — the straight-arc grouper is new
  capability with no existing seam to reuse beyond `arcs.py`'s pattern.

## Out of Scope
Round-2 affinity consumption; per-corner identity; cross-year corner-identity mapping beyond
round-1 circuits; `coast_frac` as a demand input; `circuits.yaml`/production-default changes;
re-running the trajectory/telemetry pipeline over the full historical session set (the rollup
uses the already-computed `grip_bin_obs` store instead — see PROBLEM_STATEMENT.md scoping
decision).
