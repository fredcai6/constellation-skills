# D2 — SegmentMap interface, designed from its two hottest callers

**Constraint honored:** the interface below is derived by asking, concretely, what
utilization scoring and the race simulator's Monte-Carlo loop would need to stop doing the
expensive/unstable things they do today, then generalizing only as far as that requires.
Warm and cold consumers get whatever falls out of that for free; where it doesn't fall out
for free, the cost is named explicitly (final section).

No implementation beyond signatures. Types are shown as dataclasses/protocols for
readability; the actual storage layout is flat parallel arrays (see Persistence).

---

## 0. The one design decision that drives everything else

Read against the two hot callers, `src/physics/utilization/regime_utilization.py` and the
(not-yet-built) race-level MC simulator, the current state of the world has a specific,
nameable defect: **boundary computation and boundary consumption happen in the same call.**
`_build_regime_masks` re-derives braking/corner boundaries from one driver's own `dv/ds` and
curvature on every single invocation — which is also *why* they're unstable (P1 spike,
`.agent-work/explore-ref-utilization/excursions/P1-RESULT.md`: 9.9–16.4% of track distance
flips regime driver-to-driver on the same circuit, because each driver's own braking
kinematics and each corner's proximity to the 25 m/s² fast/slow split line are being
re-litigated per call).

SegmentMap's entire job, from the caller's point of view, is to **move boundary computation
out of the hot path and make it happen exactly once, driver-invariantly, per weekend** — so
that both hot callers are left with nothing but array indexing. Everything below is that
one idea worked through: what has to be true at build time so that both hot paths become
O(lookup), not O(recompute).

---

## 1. Core types

```python
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Literal, Optional, Protocol
import numpy as np

class SegType(IntEnum):
    """Int-coded, not string-coded, because both hot callers compare/branch on this
    inside per-point (caller 1) or per-draw (caller 2) vectorized code — string
    comparison in a tight numpy loop is the kind of thing that shows up in a profile."""
    STRAIGHT = 0
    BRAKING_ZONE = 1
    CORNER = 2

SEG_TYPE_LABELS: tuple[str, str, str] = ("straight", "braking_zone", "corner")


class SeverityMixture(Protocol):
    """Opaque per-rules-era severity classifier SegmentMap queries but does not own or
    fit. Deliberately a Protocol, not a concrete import of
    layer2.property_mixture.MixtureFit: the owner spec calls for a Student-t mixture
    per rules-era, and property_mixture.py's current GaussianMixture is Gate 2's
    seed, not a promise this stays Gaussian. SegmentMap must not need to change when
    that swap happens."""
    k: int
    version: str  # stable id for the fitted mixture instance, e.g. "2022-2025:v3"

    def posterior_membership(self, descriptors: np.ndarray) -> np.ndarray:
        """(N, 2) raw [radius_m, lateral_g] -> (N, k) rows summing to 1."""
        ...


@dataclass(frozen=True)
class MapVersion:
    """Identity + provenance. Every consumer stores/cites this, never just the four
    natural-key fields alone — reproducibility requires knowing WHICH build produced
    a given utilization score or MC run, not just which circuit/weekend it was."""
    gp_name: str
    year: int
    version: int                      # monotonic per (gp_name, year), starts at 1
    built_at: str                     # ISO8601
    build_basis: str                  # e.g. "FP1+FP2 seed, 6 drivers, 41 laps"
    mixture_version: str              # SeverityMixture.version cited at build time
    superseded_by: Optional[int] = None   # version number, or None if this is latest


@dataclass(frozen=True)
class SegmentMap:
    """One (gp_name, year, version)'s complete track tiling. Parallel flat arrays,
    index i means the same physical segment in every array — this is the layout both
    hot callers are designed against (Section 2/3). No list[Segment]-of-objects
    representation exists; that shape is exactly what the hot paths must not pay for.

    Ordering invariant: strictly increasing distance order, 0-indexed, wrapping
    (segment n-1's successor is segment 0 — every current circuit is a closed loop).
    Tiling invariant (checked at construction, not just documented):
        boundaries_m[0] == 0.0
        boundaries_m[-1] == lap_length_m
        np.all(np.diff(boundaries_m) > 0)   # strictly increasing, no zero-width segments
    Sector invariant (checked at construction): every one of the 2 internal sector cut
    points (S1/S2, S2/S3) is present verbatim in boundaries_m — i.e. no segment straddles
    a sector line. This is the "split not snap" rule: cut points are inserted exactly,
    never rounded onto the nearest natural boundary.
    """
    map_id: MapVersion
    n_segments: int
    lap_length_m: float

    # --- hot arrays: read by both hot callers, built once, never mutated ---
    boundaries_m: np.ndarray          # (n_segments+1,) float64, see invariant above
    length_m: np.ndarray              # (n_segments,) float64 == np.diff(boundaries_m), precomputed
    seg_type_code: np.ndarray         # (n_segments,) int8, values from SegType

    # --- warm/cold arrays: near-zero marginal cost to add alongside the above,
    # so they ride along even though neither hot caller strictly needs them ---
    sector: np.ndarray                # (n_segments,) int8 in {1, 2, 3} — free: falls out of
                                       # the sector invariant above by construction
    turn_direction: np.ndarray        # (n_segments,) int8 in {-1, 0, +1} = {right, n/a, left};
                                       # sign of mean curvature over the segment span, computed
                                       # once alongside seg_type_code from the same curvature pass
    segment_ids: np.ndarray           # (n_segments,) dtype=object[str], stable within-layout
                                       # (Section 5)

    # --- severity: geometry-derived descriptor is permanent; membership is a cheap
    # derived view against whichever mixture_version is current (Section 4) ---
    corner_descriptor: np.ndarray     # (n_segments, 2) float64 [radius_m, lateral_g];
                                       # NaN row where seg_type_code != CORNER
    severity_membership: np.ndarray   # (n_segments, k) float64; EXACTLY 0 (not NaN) on
                                       # non-corner rows — see Section 3 for why zero-fill

    is_closed_loop: bool = True

    # --- dormant, sparse, NOT a parallel array (Section 6) ---
    _sub_phase_marks: dict = field(default_factory=dict, repr=False)
```

Why `seg_type_code`/`turn_direction`/`sector` are `int8` and not, say, `int64` or an
`object` array of enums: `n_segments` is O(15–25 corners) → roughly 50–100 segments once
braking zones, straights, and sector splits are counted, so the absolute bytes saved don't
matter — what matters is that these arrays get gathered by ordinal (`arr[ordinals]`) inside
both hot paths, and a narrow dtype keeps that gather cache-friendly at the 500k-point scale
of caller 1. `SEG_TYPE_LABELS[code]` (or `np.array(SEG_TYPE_LABELS)[seg_type_code]` for a
vectorized batch) recovers the readable string for anyone who wants it (mainly warm
consumer 2) at effectively zero cost, computed on demand, never stored.

---

## 2. Hot caller 1 — utilization scoring: vectorized point-in-segment masking

Today, `regime_utilization.regime_utilization()` takes a driver's own `distance`,
`curvature`, `v_real` and rebuilds four regime masks from scratch every call
(`_build_regime_masks`, `src/physics/utilization/regime_utilization.py:223`). What that
caller actually wants, once boundaries are computed once and driver-invariantly, is: *given
my own arbitrary telemetry distance samples, tell me which segment each one lands in.*

```python
def segment_of(self, distance_m: np.ndarray) -> np.ndarray:
    """distance_m: (N,) float64, arbitrary progress-axis samples from ANY driver's own
    lap (not required to be pre-registered onto boundaries_m or any fixed grid — this
    is the ergonomic difference from today's regime_utilization, which requires a
    shared grid via resample_by_progress before it can do anything).

    Returns (N,) int32 segment ordinals in [0, n_segments).

    One np.searchsorted call, O(N log n_segments). For N ~ 500k telemetry points and
    n_segments ~ 100, this is the entire cost — no per-point Python, no re-derivation
    of curvature or dv/ds, because those were already baked into boundaries_m at build
    time (Section 5).

    Out-of-range values wrap modulo lap_length_m and NEVER raise: a flying lap's
    telemetry can straddle the start/finish line, and that is a normal case, not an
    error, for a closed-loop track (is_closed_loop=True).
    """
    wrapped = np.mod(distance_m, self.lap_length_m)
    return np.searchsorted(self.boundaries_m, wrapped, side="right").astype(np.int32) - 1

def type_of(self, ordinals: np.ndarray) -> np.ndarray:
    """(N,) int32 ordinals -> (N,) int8 SegType codes. One gather: self.seg_type_code[ordinals]."""
    return self.seg_type_code[ordinals]
```

### Usage sketch — replacing `_build_regime_masks`

```python
seg_map = SegmentMapStore.load(gp_name, year)        # once per session, NOT per lap/call
ordinals = seg_map.segment_of(driver_distance_m)       # (500_000,) int32 — the ONE hot call
seg_type = seg_map.type_of(ordinals)                    # (500_000,) int8, one gather
severity = seg_map.severity_membership[ordinals]        # (500_000, k) float64, one gather

mask_braking  = seg_type == SegType.BRAKING_ZONE
is_corner     = seg_type == SegType.CORNER
mask_straight = seg_type == SegType.STRAIGHT
# today's slow/fast split becomes a severity threshold WITHIN corner segments, not a
# separate a_lat >= 25 m/s² recomputation per point:
mask_slow = is_corner & (severity[:, SLOW_CLASS_IDX] >= 0.5)
mask_fast = is_corner & (severity[:, FAST_CLASS_IDX] >= 0.5)
```

Everything to the right of `seg_map.segment_of(...)` is array indexing. The driver's own
`v_real`/`curvature` never enter a boundary computation again — they only enter the
utilization RATIO computation (`v_real / v_ideal`), which is unaffected by this module and
stays the caller's job.

**Invariant this depends on:** `severity_membership` rows are **exactly 0.0**, never NaN,
on non-corner segments (stated in Section 1). This lets `mask_slow`/`mask_fast` above be
computed without an `is_corner` guard on the comparison itself (only needed for the `&`,
which the caller already wants for semantic clarity) — no `isnan` branch anywhere in the
hot path.

---

## 3. Hot caller 4 — race simulator: per-segment draw loops

This consumer doesn't exist as production code yet (the current `PhysicsSimulator` in
`src/physics/physics_simulator.py` integrates a continuous point-mass forward/backward
sweep over the full distance grid, not a segment-level draw — the segment-level MC race
sim is the direction named in `project_arch_refactor.md`'s "MC race sim" vision). Designing
"the interface it wishes existed" here means: what would make a loop that runs **millions**
of correlated per-segment draws not re-pay any per-draw cost that SegmentMap could have
paid once.

The two things a per-draw MC loop cannot tolerate: (a) any Python-level iteration over
segments inside the draw loop, (b) any allocation inside the draw loop that SegmentMap
could have handed over pre-built. SegmentMap's contribution is therefore just three
read-only arrays, fetched once outside the loop, and cheap ordinal arithmetic for
lap-wrap:

```python
def next_ordinal(self, i: int) -> int:
    """(i + 1) % n_segments. Not stored — storing an explicit adjacency array would
    duplicate what one mod operation already gives for free, and the race sim needs
    this at most once per segment per draw, not per telemetry point."""
    return (i + 1) % self.n_segments

def prev_ordinal(self, i: int) -> int:
    return (i - 1) % self.n_segments
```

### Usage sketch

```python
seg_map = SegmentMapStore.load(gp_name, year)             # once, outside all MC draws
lengths     = seg_map.length_m                              # (n,) float64, reused every draw
type_codes  = seg_map.seg_type_code                         # (n,) int8, reused every draw
severity    = seg_map.severity_membership                    # (n, k), reused every draw

# Correlation structure is the SIMULATOR's concern, not SegmentMap's — SegmentMap
# supplies stable ordering/identity to key it against, once, outside the loop:
corr_chol = build_segment_correlation_cholesky(seg_map.segment_ids, seg_map.sector)

for draw in range(n_mc_draws):                                # millions of iterations
    z = corr_chol @ rng.standard_normal(seg_map.n_segments)     # correlated noise, one draw
    seg_time = per_segment_time_model(type_codes, lengths, severity, params) * (1.0 + z)
    lap_time = seg_time.sum()                                    # no per-segment Python loop
```

**Performance envelope statement:** for `n_segments` in the O(50–100) range typical of an
F1 circuit (15–25 corners → 15–25 corner segments + a comparable number of braking zones +
straights, plus at most 2 extra splits from mandatory sector cuts), every quantity the draw
loop touches is a flat array of ~100 float64/int8 elements, fetched once before the loop.
SegmentMap contributes **zero allocation and zero recomputation per draw** — the entire
marginal cost of a draw is the caller's own `n_segments`-length vector ops. The expensive
work (deriving driver-invariant boundaries from pooled sessions, sector-line
time-to-distance interpolation) happens exactly once, in `build()`/`supersede()`
(Section 5), and is amortized over however many MC draws and however many
utilization-scoring calls a session sees afterward.

**What SegmentMap deliberately does NOT own here:** the correlation matrix, the
per-segment capability/time model, and the RNG. Those stay simulator-owned because they
are physics/strategy decisions (how correlated is corner-to-corner tyre-limited grip,
which capability frontier applies per `SegType`) that have nothing to do with what a
track tiling *is*. SegmentMap's contract ends at "here is a stable, ordered, typed
partition of the lap distance axis with per-segment lengths and severity" — building a
correlated draw on top of that is caller-side composition, consistent with the module
staying a track-geometry authority, not a race-strategy or capability-model owner.

---

## 4. Severity classification is decoupled from geometry

The owner spec calls the severity mixture **per-rules-era**, not per-weekend. That has a
direct interface consequence: geometry (`boundaries_m`, `seg_type_code`, `sector`, all the
expensive driver-aggregated work) and severity (`severity_membership`, which just needs a
`SeverityMixture` to query) must be separable, because a rules-era mixture can get refit
independently of any one weekend's geometry, and a geometry rebuild (new FP sessions,
`supersede()`) shouldn't force a severity refit or vice versa.

```python
def reclassify_severity(self, mixture: SeverityMixture) -> "SegmentMap":
    """Returns a new SegmentMap with severity_membership recomputed against `mixture`
    (posterior_membership over the PERSISTED corner_descriptor rows) and mixture_version
    updated on map_id. Geometry (boundaries_m, seg_type_code, sector, segment_ids,
    corner_descriptor) is untouched — this is O(n_corner_segments) work, not a rebuild.
    Non-corner rows stay exactly 0.0 in the output, same as at construction.
    """
```

This is why `corner_descriptor` (the raw `[radius_m, lateral_g]` per corner segment) is a
permanent field on `SegmentMap` and not thrown away after the initial membership
computation: it's the thing `reclassify_severity` recomputes against. `SegType.CORNER` rows
always carry a valid descriptor (finite, `radius_m > 0` — the same validity contract
`corner_descriptors.bin_row_to_descriptor` already enforces); `corner_descriptor` is `NaN`
on non-corner rows for the same reason `bin_row_to_descriptor` raises on non-positive
lateral-g rather than fabricating a value — a straight or braking-zone segment has no
steady-state cornering radius to report.

---

## 5. Build, persistence, and the seed-then-supersede lifecycle

### Driver-invariant boundaries (the actual hard part)

Two owner-ruled rules, both aimed at killing the 9.9–16.4% cross-driver boundary
instability P1 measured:

- **Corner/straight split:** a single reference lap's lateral-accel gate on the pooled
  ribbon curvature (`ribbon.build_ribbon`'s κ(s), one geometry, not any one driver's own
  curvature-from-telemetry) — every driver sees the same corner/straight cut points because
  there is only ever one curvature signal being thresholded, computed once.
- **Braking-zone onset:** a field-envelope quantile (a low, robust quantile — e.g. p10, NOT
  a mean, which today's `_build_regime_masks`-style per-driver `dv/ds < -threshold` test is
  effectively vulnerable to: one very-late, very-hard braker pulls a mean-based cut point
  into the middle of the field's actual braking zone) of braking-onset distance **pooled
  across the field**, not any one driver's own deceleration trace.

```python
@dataclass(frozen=True)
class SegmentMapConfig:
    reference_curvature_threshold: float      # 1/m; corner/straight gate on ribbon κ(s)
    brake_onset_quantile: float = 0.10          # robust low quantile, NEVER a mean
    min_lap_count_for_field_envelope: int = 5   # below this, build() raises (see errors)
    min_segment_length_m: float = 3.0           # degenerate-sliver merge floor (natural
                                                 # boundaries only — sector cuts are exempt,
                                                 # see below)
```

`min_segment_length_m` exists because inserting sector cut points as forced splits (next
paragraph) can leave a natural boundary and a sector line only centimeters apart. The rule:
segments narrower than the floor are merged into their trailing neighbor **unless the
narrow segment's boundary is a mandatory sector cut** — sector lines are never removed or
moved (the owner-ruled "split not snap"), so a genuinely tiny sector-adjacent segment is an
allowed exception to the floor, not a bug.

### Sector nesting

Sector cut points are derived per weekend by time-to-distance interpolation (walk a
reference lap's timestamped speed trace until cumulative time matches the FIA sector-1/
sector-2 boundary, read off distance — exactly the derivation P1's spike flagged as **not
currently implemented anywhere in the repo**: `f1_data_*.db::circuit_info.marshal_sectors_json`
is empty in every DB checked, and `lap_times.sector1_time`/`sector2_time` are durations, not
locations). `build()` depends on this derivation existing; until it does, `build()` must
fail closed (see Error modes) rather than emit a map that silently doesn't honor the
sector-nesting invariant consumer 3 depends on unconditionally.

### API

```python
class SegmentMapStore:
    @staticmethod
    def build(
        gp_name: str, year: int, sessions: list[SessionRef],
        mixture: SeverityMixture, config: SegmentMapConfig,
    ) -> SegmentMap:
        """Pure builder, does not persist. Pools `sessions` (e.g. FP1+FP2 for a seed
        build) for the reference curvature + field-envelope braking onset, derives
        sector cut points, tiles, classifies severity against `mixture`. Raises
        SegmentMapBuildError / SectorLineUnavailableError (below) rather than
        returning a partial/ungated map."""

    @staticmethod
    def load(gp_name: str, year: int, version: int | Literal["latest"] = "latest") -> SegmentMap:
        """O(1)-ish disk read (~100 rows) of an already-persisted map — this is what
        both hot callers call, exactly once per session, before their hot loops start.
        Raises SegmentMapNotFoundError if absent. Deliberately has NO fallback to
        building a map ad hoc on a cache miss: silently computing a driver-specific
        tiling on the spot is the exact per-call instability this module exists to
        eliminate, so a miss must surface, not degrade quietly."""

    @staticmethod
    def supersede(new_map: SegmentMap, reason: str) -> SegmentMap:
        """Persists new_map as version = current_latest + 1 (e.g. an FP1+FP2 seed
        superseded once Q data pools in more laps), stamps the prior version's
        superseded_by, returns the new map. Never mutates or deletes a prior version:
        every already-computed utilization score or MC run stays reproducible against
        the exact version its map_id cites."""
```

### Persistence shape

Flat, one row per segment, mirroring the `telemetry_store_parquet` pattern already in use
(`data/telemetry_store_parquet/<session_id>/{pos,car}.parquet`, `src/data/telemetry_store.py`):
a `segment_maps` table/parquet partitioned by `(gp_name, year, version)`, columns
`ordinal, segment_id, start_m, end_m, seg_type_code, sector, turn_direction, radius_m,
lateral_g` (the last two = `corner_descriptor`, NaN for non-corner rows) — plus a small
map-level metadata record (JSON sidecar or a `segment_map_meta` row) holding the
`MapVersion` fields and `lap_length_m`. On `load()`: `boundaries_m` is reconstructed as
`concatenate([start_m, [end_m[-1]]])`, `length_m` as `end_m - start_m`; `severity_membership`
is recomputed from `corner_descriptor` against whichever `SeverityMixture` resolves from
`mixture_version` (cheap — `O(n_corner_segments)`, paid once at load, never per-query).

### Error modes

- `SegmentMapNotFoundError` — `load()` with no persisted map for the key. No silent
  fallback (see above).
- `SegmentMapBuildError` — fewer than `min_lap_count_for_field_envelope` clean laps
  available across `sessions` to compute a robust braking-onset quantile.
- `SectorLineUnavailableError` — `sessions` lack the timing data to interpolate sector cut
  points. `build()` fails closed rather than emitting a map without the mandatory nesting
  invariant.

`segment_of()` (Section 2) is the one method in this whole surface that is guaranteed to
never raise — wrap-around on a closed loop is a normal case, not a boundary condition.

---

## 6. Cold consumer 5 (discriminativeness) and dormant fields

`segment_id` is built so a **future** consumer can track "the same corner" across seasons
without SegmentMap doing anything special for it today:

```python
segment_id = f"{gp_name}:{layout_key}:{ordinal_in_layout}:{SEG_TYPE_LABELS[seg_type_code]}"
```

`layout_key` is a content hash of the geometry-only cut points (the natural
corner/straight boundaries, rounded to a fixed precision — deliberately *excluding*
sector-forced splits, which can shift year to year even when the physical layout hasn't).
Two maps for the same circuit with the same `layout_key` are asserting "this is
structurally the same track," so ordinal-`N` corner segments are comparable across them; a
genuine layout change (the 2026 Madrid venue / year-aware Spain routing work already landed
in this repo per recent commits) produces a new `layout_key` and entirely new
`segment_id`s — no false continuity is ever claimed across a real layout change.

`turn_direction` and `_sub_phase_marks` are the two literally-dormant fields (owner spec:
"dormant attributes"):

- `turn_direction` rides along as a free int8 column (Section 1) — computed from the sign
  of mean curvature during the same pass that already derives `seg_type_code`, so its
  marginal build cost is one more array write, and its marginal hot-path cost is exactly
  zero (neither hot caller reads it).
- `_sub_phase_marks` (turn-in / apex / exit distances within a corner segment) is
  deliberately **not** a parallel array. It's a sparse `dict[segment_id, dict[str, float]]`
  side-table, populated lazily (only once some future corner-phase fitter runs, if ever) and
  entirely absent from the hot arrays' memory layout — adding a rarely-populated, variable-
  shape field to the parallel-array set would break the cache-locality property both hot
  paths depend on for no benefit to either of them.

---

## 7. What the hot-path bias cost the cold/warm consumers, and why that's acceptable

- **Consumer 2 (circuit fingerprint time-shares):** gets no built-in "distance-share by
  type/severity" rollup method (the `regime_rollup.circuit_distance_share` equivalent).
  They compute it themselves: `np.bincount`-style grouping of `length_m` by `seg_type_code`
  (and by `argmax(severity_membership)` within corner rows) — a few lines over fields that
  already exist. Cost: a small amount of caller-side code, every time. Acceptable because
  baking a rollup INTO the core type would mean SegmentMap owns an open-ended set of
  possible statistics over the tiling, which blurs its job (define the tiling) with a job
  it doesn't need to have (summarize the tiling) — and no hot caller needs that method to
  exist, so it would exist purely for consumer 2's convenience at the cost of surface area
  every other consumer has to understand.

- **Consumer 3 (composed-sector validation):** costs essentially nothing — `sector` is a
  required array anyway (it falls directly out of the mandatory sector-nesting invariant
  the owner spec fixes), so consumer 3 gets exactly the field it needs for free, gathered
  the same way either hot caller gathers anything else.

- **Consumer 6 (grip/practice-update lookups):** pays a real cost: SegmentMap does not
  carry any per-segment grip state, so consumer 6 must maintain its own
  `segment_id -> grip_estimate` side table and join against `SegmentMapStore.load(...)`'s
  `segment_ids` array rather than reading a ready-made field. This is deliberate, not an
  oversight: grip evolves session-by-session *within* a weekend, while the tiling is
  designed to change only via explicit `supersede()`. Folding a frequently-mutating
  quantity into the versioned map would force a new map version on every FP-session grip
  update, which defeats the entire "map_version cited by every consumer, reproducible"
  contract this module exists to provide to the hot callers. Consumer 6 pays one extra join
  so that consumers 1 and 4 never have to reason about a map that can mutate under them
  mid-session.

- **Consumer 5 (discriminativeness):** effectively free, as noted in Section 6 — the stable
  `segment_id` scheme exists because hot caller 4 already needed stable IDs (to key
  per-segment MC state across laps within a draw); consumer 5 reuses the same field at a
  coarser equality granularity (`layout_key` prefix instead of full `segment_id`). No
  separate cost was paid for it.

---

## Files read (unmodified)

`src/physics/segment_classifier.py`, `src/physics/layer2/{regime_rollup,property_mixture,
corner_descriptors,arcs}.py`, `src/physics/ribbon.py`,
`src/physics/utilization/regime_utilization.py`, `src/physics/physics_data_models.py`,
`src/physics/physics_simulator.py` (`simulate_lap`), `src/physics/sim_evaluator.py`
(`resample_by_progress`, `BRAKING_DECEL_THRESHOLD`), `src/data/telemetry_store.py`
(session natural-key convention), `docs/agents/ORCHESTRATOR_CONTEXT.md` (architecture
boundaries), and the sibling excursion
`.agent-work/explore-ref-utilization/excursions/P1-RESULT.md` (tiling-taxonomy spike —
source of the driver-instability numbers and the FIA-sector-data-gap finding cited above).
