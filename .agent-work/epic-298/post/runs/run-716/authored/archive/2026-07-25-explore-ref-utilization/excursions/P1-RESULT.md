# P1 — Complete track-tiling prototype: does it fall out of existing artifacts?

**Question asked:** does a coherent COMPLETE track tiling — every meter typed as exactly
one of {corner-severity-class segment, braking zone, straight} — fall out of existing
artifacts on 2-3 circuits, and where do the repo's three segmentation taxonomies disagree?

**Bottom line:** No single existing artifact gives you that tiling today. One of the three
named taxonomies — (b), the utilization 4-regime split — IS complete by construction (every
track point lands in exactly one of braking/slow_corner/fast_corner/straight, asserted in
code). The other two are not: (a) the corner-severity mixture only has evidence where a
kinematic gate fires (`a_lat > 3.0 m/s²`), leaving a real, data-dependent hole over straights;
(c) the ephemeris named segments exist for exactly one circuit/session in the whole store
(Bahrain 2023 R) and only distinguish corner-arc vs. untyped gap — no braking/straight split
at all. Composing (a)'s severity labels onto (b)'s corner points to get one complete
{severity-class, braking, straight} tiling is technically straightforward (the code pieces
exist) but **nobody has built it** — the closest thing to it in the repo is a fourth,
previously-unlisted taxonomy (`SegmentClassifier`, see below) that already tiles completely
and already has an (unwired) bridge to (a)'s mixture, but disagrees with (b) on both what
counts as a corner and what counts as braking.

Prototype code: `C:\Programs\f1Brainz\.agent-work\explore-ref-utilization\excursions\scratch\P1\tiling_prototype.py`
(read-only on all DBs and `src/`; run with the pinned interpreter). Full console output was
captured for all 4 circuits below.

## Circuits used and why

Checked coverage first rather than assuming it (task instruction). Chose 4, not 2-3, because
Bahrain is the only ephemeris circuit and the team-lead asked for contrast circuits:

| Circuit (2023) | grip_bin_obs (a) | telemetry_store pos/car (b) | ephemeris corner_json (c) |
|---|---|---|---|
| Bahrain | yes (2023, 2024) | yes (Q session_id 193) | **yes — only circuit in the store** (2023 R, 3 runs) |
| Great Britain (Silverstone) | yes (2023 only) | yes (Q session_id 237) | no |
| Japan (Suzuka) | yes (2023, 2024) | yes (Q session_id 267) | no |
| Monaco | **no 2023 rows** — used 2024 grip_bin_obs | yes (Q session_id 218, 2023) | no |

`data/f1_data_*.db::circuit_info` is empty (0 rows) in every DB checked (2018, 2023, 2024,
2025, merged `f1_data.db`) — see the FIA sector section below.

`data/telemetry_store.db`'s `tele_pos`/`tele_car` SQLite tables are **empty** (0 rows total) —
the real per-sample position/car channels live out-of-line in
`data/telemetry_store_parquet/<session_id>/{pos,car}.parquet` (per #541, confirmed via
`src/data/telemetry_store.py`'s `TelemetryStore.read_session`, which is what the prototype
uses). A raw SQL read against `tele_pos`/`tele_car` silently returns nothing — worth flagging
since it's an easy trap for the next person who reaches for those tables directly.

## Method (what was actually built, reusing existing code)

1. **Ribbon (curvature geometry):** for each circuit, pulled each driver's single fastest Q
   lap's raw (X, Y) trace from the Parquet store and fed 8 laps into
   `src.physics.ribbon.build_ribbon` (median-pooled path → κ(s), unmodified). Resulting lap
   lengths (5311 m Bahrain, 5801 m Silverstone, 5740 m Suzuka, 3250 m Monaco) are all within
   ~1-3% of the real circuit lengths — the ribbon build is sane.
2. **Taxonomy (b):** called `src.physics.utilization.regime_utilization._build_regime_masks`
   directly on the ribbon's curvature + one driver's real speed (resampled onto the ribbon
   grid via `sim_evaluator.resample_by_progress`). Note: **building the 4-way tiling does not
   require the car-ceiling simulator at all** — `v_ideal` is only needed to turn the masks into
   utilization ratios, not to build the masks themselves, so this prototype skipped
   `PhysicsSimulator`/`CarCeilingResult` entirely and stayed cheap.
3. **Taxonomy (a):** loaded `grip_bin_obs` per circuit, fit `property_mixture.fit_property_mixture`
   over `corner_descriptors.descriptors_from_frame`, took the posterior-argmax class per row,
   then majority-voted a class per one of the 32 progress-bins (or `None` if the bin never has
   a corner-gated row at all).
4. **Taxonomy (c):** read Bahrain 2023 R's `eph_residual.corner_json` (latest run, one driver's
   lap), typed `[start_m, end_m)` windows as `"corner"`, everything else `"gap"`.
5. Mapped all three onto the same 1500-point ribbon distance grid and cross-tabulated.

## Finding 1 — (b) is the only one that's actually complete

`_build_regime_masks` has an internal assert that the four masks tile every point exactly
once — verified true by construction, not just claimed. Distance-share by circuit (reference
driver ALB in all 4):

| Circuit | braking | slow_corner | fast_corner | straight |
|---|---|---|---|---|
| Bahrain | 20.3% | 40.9% | 9.3% | 29.5% |
| Great Britain | 17.1% | 58.5% | 13.9% | 10.5% |
| Japan | 18.7% | 47.8% | 16.4% | 17.1% |
| Monaco | 32.3% | 57.6% | 7.7% | 2.3% |

Sanity: Monaco's near-zero straight share (2.3%) and highest braking share (32.3%) are
directionally right for a street circuit; Silverstone's low straight share (10.5%) is
suspicious for a track famous for flowing high-speed corners — see the threshold-sensitivity
note in Finding 4, this is a real artifact of the fixed 25 m/s² fast/slow split, not a bug in
the prototype.

**Boundary instability** (built masks from 5 different drivers' fastest laps per circuit, same
ribbon; measured the fraction of the 1500-point grid where at least one of the 5 disagrees
with the reference driver's regime label at that point):

| Circuit | % of track distance with driver disagreement |
|---|---|
| Bahrain | 9.9% |
| Great Britain | 11.1% |
| Japan | 14.2% |
| Monaco | 16.4% |

This is real instability, not just edge-pixel noise on a 1500-point grid — it's concentrated
where it should be (braking-zone start/end depends on each driver's own dv/ds, and the
slow/fast corner split depends on each driver's own speed through the corner via
`a_lat = v²·|κ|`), so the same geometric corner can flip between "slow" and "fast" driver to
driver near the 25 m/s² line.

## Finding 2 — (a) is structurally incomplete, and "coverage" is a bin-resolution artifact

`grip_bin_obs` only ever emits rows where `a_lat > CORNER_GATE_MS2 = 3.0 m/s²`
(`src/physics/layer2/grip_bin_obs.py`) — there is no straight-line row in the table, ever, by
construction. Bins-with-any-evidence out of the fixed 32 progress-bins:

| Circuit | bins with evidence | years pooled |
|---|---|---|
| Bahrain | 23/32 (72%) | 2023 only |
| Great Britain | 32/32 (100%) | 2023 only |
| Japan | 30/32 (94%) | 2023, 2024 |
| Monaco | 32/32 (100%) | 2024 only (no 2023 rows) |

Reading "100%" as "every meter is typed" would be wrong: a 32-bin grid is coarse enough
(~170 m/bin at Silverstone) that almost any bin will contain *some* corner-gated sample once
enough laps are pooled, even though the geometry only has 15-19 real corners. The real,
per-meter picture (visible once you cross-tab against (b)'s 1500-point grid, see below) is
that (a) has zero opinion on most of the literal straight-line meters; its "distance share"
statistic in `regime_rollup.py` is explicitly documented as a lower bound on true time-share,
and that same undercounting logic applies to spatial coverage.

## Finding 3 — (c) exists for exactly one circuit and only splits corner/gap

Bahrain 2023 R, latest ephemeris run (run_id 3), driver ALB lap 3: 15 named corner segments,
32.5% of track distance. Everything else is an undifferentiated `"gap"` — the ephemeris
`corner_json` has no braking or straight label at all, so on its own (c) cannot deliver the
3-way tiling the question asks about; it would need to be composed with something like (b) to
split the gap. No other circuit/session in `data/ephemeris.db` has `corner_json` populated
(`eph_state`/`eph_residual` both only ever have `(2023, Bahrain, R)` rows across all 3 runs).

## Finding 4 — the disagreement tables, and WHY they disagree

Cross-tabs are grid-point counts (of 1500) at Bahrain, Great Britain, Japan, Monaco — full
output captured from the prototype run, e.g. Bahrain (a) vs (b):

```
(b) regime          braking  fast_corner  slow_corner  straight
(a) severity class
corner_class_0.0        148           33          268       115
corner_class_1.0         45           84           58         1
corner_class_2.0         81           14           82        11
corner_class_3.0         30            8          101         3
corner_class_nan          0            0          105       313
```

and Bahrain (c) vs (b):

```
(c) ephemeris     braking  fast_corner  slow_corner  straight
gap                   158           18          420       417
corner                146          121          194        26
```

Two root causes explain essentially all of the disagreement mass, and they are structural
(different threshold philosophies), not noise:

1. **(a) gates on kinematic lateral load (`a_lat > 3.0 m/s²`); (b) gates on track geometry
   (`|κ| ≥ 1e-4`, i.e. radius < 10,000 m).** A trail-braking point has real lateral load before
   the geometric apex, so (a) tags it "corner" while (b) — whose braking mask takes priority
   over its corner test — tags the same point "braking". That is most of the
   `corner_class_*` × `braking` mass in the crosstab (148+45+81+30 = 304 points at Bahrain).
2. **(a)'s coarse 32-bin resolution vs (b)'s 1500-point resolution.** `corner_class_nan`
   (bins that never see a corner-gated sample) still lands on 105 `slow_corner` and 313
   `straight` points in (b) — consistent (no data where there's no corner) — but real
   `corner_class_*` bins also bleed into 115+1+11+3 = 130 `straight` points, because a 32-bin
   grid smears a genuine corner's bin edges ~170 m wide onto (b)'s much finer per-meter
   boundary.

For (c) vs (b): the named corner segments do **not** include the braking zone on the way in —
158 of Bahrain's `braking`-labelled points fall in ephemeris's `"gap"`, i.e. (c)'s corner
windows start at (something close to) the geometric turn-in, not the braking point, which is
consistent with `corner_json`'s docstring describing per-corner transit time, not a
capability-envelope braking zone.

## Finding 5 (unrequested but load-bearing) — a fourth taxonomy that's actually complete AND already bridges to (a)

Grepping for where `KinematicSample.regime` (the vocabulary `arcs.py` builds
`BrakingArc`/`StraightArc` on top of) actually gets assigned turned up
`src/physics/segment_classifier.py::SegmentClassifier._classify_regime` — production code,
not a prototype:

```python
def _classify_regime(self, curvature, control) -> str:
    if abs(curvature) >= self.config.straight_curvature_threshold:  # 0.005 1/m, i.e. radius < 200 m
        return "corner"
    if control.is_braking:      # brake_probability >= 0.5 (pedal-input model, NOT dv/ds)
        return "straight_brake"
    if control.is_coasting:     # throttle <= 0.1 AND brake_probability <= 0.2
        return "straight_coast"
    return "straight_throttle"
```

This if/elif/else exhausts every sample — it's complete by construction, same as (b). It also
already has a bridge method, `SegmentClassifier.soft_class_membership(sample, fit)`, that
queries a fitted `property_mixture.MixtureFit` (i.e. taxonomy (a)'s own mixture) for any
`"corner"`-regime sample — literally the composition the team-lead's question is asking
whether exists. Its own docstring is explicit about the catch: *"Standalone, additive,
post-hoc: NOT wired into `classify_samples`'s main loop... Callers invoke this after both a
`SegmentedLap` and a fitted `MixtureFit` exist."* So the plumbing exists, callable, but nothing
in the repo actually calls it to produce a materialized per-lap tiling — there's no store, no
script, no test fixture that runs it end-to-end today (I did not find one; see scoped nulls).

And it actively **disagrees with (b) on both axes it shares**:
- **Corner gate:** `SegmentClassifier` uses `straight_curvature_threshold = 0.005` (radius <
  200 m) vs (b)'s `CURVATURE_THRESHOLD = 1e-4` (radius < 10,000 m) — a **50x** difference in
  what geometry counts as "still a corner". (b) would call most of Silverstone's high-speed
  kinks "corner"; `SegmentClassifier` would call them "straight".
- **Braking definition:** `SegmentClassifier`'s `is_braking` is a brake-pedal-probability
  threshold (`brake_probability >= 0.5`, an input signal) — (b)'s braking mask is a kinematic
  derivative test (`dv_real/ds < -0.05`, an outcome signal). These are not the same thing: a
  driver can be off the brake but still decelerating (lift-and-coast, engine braking, or just
  running out of straight) — kinematic-braking without pedal-braking — and the reverse (light
  brake dab with negligible dv/ds) also happens. I did not quantify how often these two diverge
  on real data (would need `ControlState`/ processed_telemetry wired up — see scoped nulls),
  but the two definitions are drawing from structurally different signals, so material
  disagreement should be expected, not assumed away.

## FIA sector boundaries — not recoverable from any current store

- `f1_data_*.db::circuit_info` (columns `corners_json`, `marshal_sectors_json`) is the schema's
  obvious home for this and is **completely empty** — 0 rows — in every DB checked (2018, 2023,
  2024, 2025, and the merged `f1_data.db`). The collector code path that would populate it
  (`src/data/database/_metadata_circuit.py`, referenced by `src/data/collector.py`) exists but
  was apparently never run, or writes were never persisted.
- `f1_data_*.db::lap_times` has `sector1_time`/`sector2_time`/`sector3_time` — but these are
  **durations** (seconds), not locations. Recovering a sector boundary's track-distance
  location from them would require picking one lap, walking its timestamped speed trace
  (available via `telemetry`/`processed_telemetry` or the Parquet mirror) until cumulative
  elapsed time matches the sector-1 duration, and reading off the distance at that point — a
  genuinely new derivation script, not a read of any existing artifact. Nothing in `src/`
  currently does this (grepped for `sector1_time` usage — only the DB write path and
  `session_gap_weather`/scoring consumers touch it, none derive a location).
- **Verdict: sector-nesting needs new data engineering, honestly, not just a new query.**

## Scoped nulls — what this excursion did NOT test

- Did not run `SegmentClassifier.classify_samples` end-to-end on real telemetry (it needs a
  `processed_telemetry` DataFrame + a `control_states` iterable built from FastF1
  throttle/brake channels via whatever adapter feeds the windowed estimator — didn't chase that
  down within budget), so Finding 5's disagreement with (b) is argued from the two modules'
  threshold constants and docstrings, not measured point-by-point like Findings 1-4 were.
- Did not measure boundary instability for taxonomy (a) (bin-majority-class stability lap-to-lap)
  or taxonomy (c) (corner-segment edges lap-to-lap) — only (b)'s point masks got the
  cross-driver stability treatment.
- Did not attempt Suzuka/Silverstone/Monaco ephemeris runs (the store genuinely has none —
  confirmed by direct query, not inferred) — no partial (c) tiling was possible outside Bahrain.
- Did not test the FP/R sessions, only Q — plausible some circuits' R sessions have longer
  green-flag stretches that would shift (b)'s straight/braking shares; not checked.
- Did not attempt to actually build the composed {severity-class, braking, straight} tiling
  the question envisions (using (b)'s curvature+braking test as the master gate, then querying
  (a)'s mixture only within (b)'s corner points) — that's the natural next excursion once this
  spike is reviewed, not attempted here since the ask was to characterize the gap, not close it.
- `session_terrain_profile_samples` (bank angle, grade, altitude — potentially a 4th/5th
  geometric channel for a richer tiling) exists for all 4 circuits but was not touched.

## Files

- Prototype script (read-only, throwaway):
  `C:\Programs\f1Brainz\.agent-work\explore-ref-utilization\excursions\scratch\P1\tiling_prototype.py`
- Source modules read (unmodified): `src/physics/layer2/{corner_descriptors,property_mixture,
  regime_rollup,arcs,grip_bin_obs}.py`, `src/physics/utilization/{regime_utilization,
  characterize}.py`, `src/physics/ideal_lap/ephemeris_store.py`, `src/physics/ribbon.py`,
  `src/physics/sim_evaluator.py`, `src/physics/segment_classifier.py`,
  `src/physics/physics_data_models.py`, `src/physics/physics_config.py`,
  `src/data/telemetry_store.py`.
- DBs queried (read-only): `data/damage_integrals.db`, `data/ephemeris.db`,
  `data/telemetry_store.db` + `data/telemetry_store_parquet/`, `data/f1_data_2023.db`
  (+ spot checks on `f1_data.db`, `f1_data_2018.db`, `f1_data_2024.db`, `f1_data_2025.db`).
