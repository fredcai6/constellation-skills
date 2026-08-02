# Problem Statement — #625 Phase 1 segmentation substrate

Reconciled against `LAUNCH_ORDER` (team-lead dispatch, epic #601, `LATITUDE_CONTRACT.md`,
confirmed `DESIGN_SPEC.md` Phase 1 section) plus source verification in this worktree
(`C:/Programs/f1-625`, `feat/625-segmentation-substrate`, base `main` 8a23b42c).

## What's being built

Three deliverables, per the launch order's Mission + Scope:

1. **Soft/fractional property-class membership** replacing `segment_classifier.py`'s hard
   4-tag regime (`straight_throttle`/`straight_coast`/`straight_brake`/`corner`,
   `physics_data_models.py:17` `_VALID_REGIMES`) — corners as mixtures over classes, class
   count support-driven, per-corner identity deferred.
2. **Straights as first-class segments** (length, duration, top speed) + a **lateral-g/radius
   axis**, sourced from `grip_bin_obs` (`data/damage_integrals.db`, 612,615 rows, 2019-2026,
   ~22 circuits) — NOT the corner-fingerprint CSVs (`data/corner_fingerprints_<year>.csv`,
   wear-sensor `label` tags, out of scope per pre-ruling #2).
3. **Per-circuit regime time-share rollup** — currently unbuilt (`segment_classifier` tags
   every sample, never aggregated per circuit, per x6 excursion).

## Source-verified facts that shape the design (not in the launch order verbatim)

- `grip_bin_obs` bins are **per-lap-normalized** (32 fixed bins, `N_BINS=32` in
  `src/physics/layer2/grip_bin_obs.py:21`), re-derived independently every lap from that
  lap's own cumulative distance — NOT a stable cross-lap/cross-session arc-length index.
  Aggregating at CIRCUIT granularity (many laps) averages this out for a coarse rollup; it
  is not usable for exact corner-identity registration (which per-corner identity is
  deferred anyway).
- `grip_bin_obs` is **corner-gated only** (`a_lat > 3 m/s²`, `CORNER_GATE_MS2`,
  `grip_bin_obs.py:22`) — it carries no straight-line rows. `mu_lat_p90` = p90(`a_lat/G`)
  per bin (lateral-g achieved); combined with `v_mean` per bin, radius is derivable as
  `R = v_mean**2 / (mu_lat_p90 * GRAVITY_MS2)` — this is the lateral-g/radius axis the
  pre-ruling names.
- No existing code computes top-speed/length/duration per straight, DRS-zone-level speed,
  or a stable per-circuit corner-vs-straight arc-length split. `arcs.py`'s
  `identify_braking_arcs`/`_contiguous_runs` is the only contiguous-run grouper in
  `src/physics`, and it is braking-only.
- `src/evo_predictor/circuits.yaml` `downforce` tags are hand-authored integers 1-5 with
  explicit "carried from 2025" comments on several 2026 rows — confirms the launch order's
  low-trust framing; this rules out using `downforce` as the F12 falsifiable-gate's
  independent proxy (would beg the question against the mission's own framing of that field
  as provisional).

## Scoping decision (within inherited latitude, not a scope cut)

The classifier's "straights as first-class segments" (length/duration/top-speed) and the
historical circuit rollup pull from **different data paths appropriate to their cost
profile**, both still fully built:

- **Live classifier capability** (new, tested): `segment_classifier.py` gains a
  straight-arc grouper (mirroring `arcs.BrakingArc`) computing length/duration/top-speed
  from classified `KinematicSample`s for any session run through it — this is the
  reusable substrate capability the spec names.
- **Historical rollup** (the per-circuit aggregate over 2019-2026): built from the
  already-computed `grip_bin_obs` store — corner-bin-share (fraction of a lap's 32 bins
  that clear the corner gate) approximates straight vs. corner distance-share without
  re-running the trajectory/telemetry pipeline over ~600 archived sessions (out of budget
  for one wave); corner property-class shares come from the soft-membership posterior over
  the same store's `(radius, lateral_g)` descriptors.

This is an engineering-breakdown call within "extend the classifier + add the rollup"
inherited latitude (LAUNCH_ORDER Inherited Latitude), not a deferral of either named
deliverable — both ship. Recorded here for visibility, not blocking.

## Falsifiable gate (F12, mandatory)

Held-out-circuit class-membership stability: fit the property-class mixture independently
on two non-overlapping circuit subsets (split at the circuit level, not the row level, so
no circuit leaks across the split) drawn from `grip_bin_obs`; compare the two independently
fit mixtures' component means (Hungarian-matched) for agreement. `circuits.yaml downforce`
is explicitly ruled out as the independent-proxy alternative (see above) — held-out
stability is the chosen check, per launch order's "EITHER/OR."

## Out of scope this wave (per launch order)

Round-2 affinity consumption, cross-year corner-identity mapping beyond the round-1
calendar, per-corner identity, `coast_frac` as a demand input, production-default /
`circuits.yaml` changes.

## Decision confirmed

This problem statement is ratified via `user-decision` citing `LAUNCH_ORDER:Mission` — the
Admiral is the ratifying authority for this delegated run (per Modes: delegated, in
`commander-core.md`); no reachable human this run.
