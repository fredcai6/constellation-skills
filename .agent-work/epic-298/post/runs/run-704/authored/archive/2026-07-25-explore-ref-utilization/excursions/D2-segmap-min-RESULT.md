# D2 — SegmentMap interface, MINIMAL variant

Design-it-twice excursion. Constraint: smallest surface that serves all six named
consumers; every method earns its place; one deep entry point over many shallow ones.
Interface only — no implementation bodies beyond signatures/dataclass fields. The module's
job (tiling contents, boundary rules, lifecycle) is owner-ruled and reproduced verbatim in
the brief; this document does not re-litigate it, only shapes the API surface around it.

Grounded against real code before designing (not from memory): `src/physics/ribbon.py`
(the ribbon geometry SegmentMap consumes, not rebuilds), `src/physics/layer2/{corner_descriptors,
property_mixture,regime_rollup,arcs}.py` (existing severity-mixture and regime-tiling
precedent — and where this design deliberately departs from it), `src/physics/segment_classifier.py`
(a fourth, currently-unwired tiling taxonomy — see "Why not reuse X" below), and three prior
excursions in this same directory: P1 (four disagreeing taxonomies exist today, none is the
tiling this job describes), P4 (FIA sector boundaries are NOT stored anywhere on disk — must
be derived from `lap_times.sectorN_time` durations by walking a speed trace, exactly as the
brief specifies), and x1/x2/x3 (the per-rules-era severity mixture, reference-lap, and
per-driver-observable machinery this module sits between).

---

## Why the existing taxonomies don't just become this

P1 found four separate corner/regime taxonomies in the repo today (severity mixture on
`grip_bin_obs`, the 4-regime utilization split, the Bahrain-only ephemeris corner windows,
and `SegmentClassifier`'s regime tags) and none of them (a) tiles the whole lap AND (b)
nests inside FIA sectors AND (c) is driver-invariant AND (d) has a version lifecycle. This
design does not try to unify those four — it defines a fifth, purpose-built artifact that
*consumes* two of them as inputs (a fitted severity mixture from the property-mixture
lineage; ribbon curvature from `ribbon.py`) rather than re-deriving corner/brake logic that
already exists elsewhere. `SegmentClassifier` in particular is NOT reused as the tiling
engine: P1 documents it uses a different, driver-dependent brake definition
(`brake_probability >= 0.5`, a pedal-input signal) than this job's driver-invariant
field-envelope requirement, and a different, uncalibrated curvature threshold. Building on
it would either violate driver-invariance or require silently overriding its thresholds —
cleaner to keep this module's own small set of named thresholds (see Config) and leave
`SegmentClassifier` as the separate per-sample regime tagger it already is.

---

## Types

```python
class SegmentClass(Enum):
    CORNER = "corner"
    BRAKING_ZONE = "braking_zone"
    STRAIGHT = "straight"


@dataclass(frozen=True)
class SubPhaseMark:
    """Dormant: an optional named point-of-interest within a segment (e.g. 'turn-in',
    'apex', 'exit-kerb'). No controlled vocabulary is enforced here — that is a future
    consumer's concern, not this module's; SegmentMap only carries the marks it's given."""
    name: str
    at_m: float          # absolute ribbon distance, must lie within the owning segment's [start_m, end_m)


@dataclass(frozen=True)
class SegmentAdjacency:
    """Dormant: neighbor context, computed once at build time from segment order (not a
    live query — see 'Excluded' for why no traversal method exists)."""
    prev_segment_id: Optional[str]
    next_segment_id: Optional[str]
    prev_class: Optional[SegmentClass]
    next_class: Optional[SegmentClass]
    following_straight_length_m: Optional[float]   # length of the NEXT straight segment, if any
    direction_flip: Optional[bool]   # corner-to-corner only: does turn_direction change vs. the previous corner? None when not corner-to-corner


@dataclass(frozen=True)
class Segment:
    segment_id: str        # f"{layout_id}:{ordinal:04d}" -- stable WITHIN a layout across
                            # reprocessing of the same weekend or a seeded-forward map; a
                            # layout change (new circuit_layout_id) invalidates it deliberately
    ordinal: int            # 0-based position in the tiling; segments[i].ordinal == i always
    start_m: float           # inclusive
    end_m: float              # exclusive; segments tile [0, lap_length_m) with no gaps/overlaps
    segment_type: SegmentClass
    sector_index: int         # 1, 2, or 3 (FIA sector this segment nests inside, exactly)
    turn_direction: Optional[Literal["left", "right"]]   # CORNER only; None otherwise
    severity_weights: Optional[dict[int, float]]          # CORNER only; None otherwise.
                            # Keys are class indices INTO map.rules_era's fitted mixture
                            # (meaningless without map.rules_era); values sum to 1.0 (tol 1e-6)
    subphase_marks: tuple[SubPhaseMark, ...]     # dormant; () when unpopulated, never None
    adjacency: SegmentAdjacency                   # dormant fields inside may be None; the
                            # wrapper itself is always present (every segment has *a* position
                            # in the order, even a first/last with one-sided neighbors)


@dataclass(frozen=True)
class SegmentMapProvenance:
    status: Literal["seeded", "superseded", "historical"]
    seeded_from_map_version: Optional[str]    # the prior_map this was seeded from, if any
    built_at: str                              # ISO-8601 UTC
    reason: str                                # e.g. "cold build, no prior map", "kept seed:
                            # no contradiction within tolerance", "supersede: corner_3 boundary
                            # diverged 41m > contradiction_tolerance_m=25m"
    source_event_docs: tuple[str, ...]         # FIA circulars/layout-change docs cited when seeding; () otherwise
    config_fingerprint: str                    # hash of the SegmentMapConfig used to build this version, for audit replay


@dataclass(frozen=True)
class SegmentMap:
    map_version: str            # globally unique, monotonically orderable within (layout_id,)
    circuit_id: str
    layout_id: str               # stable circuit-layout identity; changes only on a real track-layout change
    year: int
    weekend: str                 # event key, e.g. round identifier
    rules_era: str                # selects which severity mixture severity_weights indices refer to
    lap_length_m: float
    sector_boundaries_m: tuple[float, float]   # (b1, b2); the two interior FIA cut distances
    segments: tuple[Segment, ...]               # ordered by ordinal; the tiling itself
    provenance: SegmentMapProvenance

    def segment_ids_for_distances(self, distances_m: np.ndarray) -> np.ndarray:
        """The one query method. Vectorized nearest-below lookup (segments are sorted,
        non-overlapping [start_m, end_m) intervals) -- returns segment_id per input point.
        Points outside [0, lap_length_m) raise ValueError (no silent clamping: a caller
        feeding an unregistered/mis-scaled distance axis should fail loudly, not get a
        wrapped-around or edge-clamped answer that looks plausible)."""
```

`SegmentMap` and every nested dataclass are frozen — there is no in-place mutation anywhere
in this interface (see Invariants: version monotonicity / reprocess-over-change-detection).

### Config

```python
@dataclass(frozen=True)
class SegmentMapConfig:
    corner_lat_accel_threshold_ms2: float     # reference-lap a_lat threshold defining corner vs. straight
    braking_onset_quantile: float              # robust LOW quantile (e.g. 0.10) over the field's
                            # brake-onset distances-before-corner-entry; never a mean (owner-fixed)
    min_segment_length_m: float                 # floor to avoid degenerate slivers after sector-line splitting
    contradiction_tolerance_m: float             # max allowed boundary drift (in meters, any
                            # corner/braking-zone edge) between a seed and this weekend's own
                            # derivation before the seed is superseded rather than kept
```

No field resolves `rules_era` or fits the severity mixture — era resolution and mixture
fitting stay in `layer2/property_mixture.py` (or its per-rules-era Student-t successor);
`SegmentMap` only accepts an already-fitted mixture as a build input (see below). Coupling
tiling production to mixture-fitting internals would cross a module boundary this interface
doesn't need to cross to do its job.

---

## Functions — one deep write path, three narrow read paths

### The one deep entry point (build/reprocess)

```python
def derive_segment_map(
    circuit_id: str,
    layout_id: str,
    year: int,
    weekend: str,
    rules_era: str,
    reference_lap: ReferenceLapGeometry,       # distance_m, curvature, lateral_accel_ms2 --
                            # ribbon-shaped (see ribbon.build_ribbon/build_session_ribbon),
                            # SegmentMap does not build ribbons itself
    braking_envelope: BrakingEnvelopeObservations,   # per-corner-candidate set of field
                            # brake-onset distances (many drivers/laps), from which the low
                            # quantile is taken -- never a per-driver or mean value
    sector_time_splits: SectorTimeSplits,       # official sector1/2/3 DURATIONS (from
                            # lap_times) + the same reference lap's cumulative-time-vs-distance
                            # trace, so boundaries are located by time-to-distance interpolation
    severity_mixture: MixtureFit,                 # pre-fit, rules_era-tagged; SegmentMap
                            # validates the tag matches `rules_era`, does not fit it
    prior_map: Optional[SegmentMap],               # seed source; None for a genuine cold build
                            # (first time this layout is processed, or a historical post-hoc map)
    event_docs: tuple[str, ...] = (),
    config: SegmentMapConfig = ...,
) -> SegmentMap:
    """Cold build (prior_map is None): derive segments entirely from this weekend's own
    reference_lap + braking_envelope + sector_time_splits. status="historical" if this is
    a post-hoc backfill call, "seeded" otherwise (the two share one code path; the caller's
    intent is carried in `event_docs`/how the caller labels the call, not a separate branch
    of this function -- see Excluded).

    Seeded build (prior_map given): recompute this weekend's own boundaries the same way as
    a cold build, then compare against prior_map's boundaries. Within contradiction_tolerance_m
    on every boundary: return prior_map's segments verbatim, re-stamped with a fresh
    map_version and provenance.status="seeded". Any boundary exceeds tolerance: return the
    freshly-derived segments, provenance.status="superseded". Either way this call NEVER
    mutates prior_map -- it stays retrievable at its own map_version via get_by_version.

    Raises ValueError on: an unrecognized circuit_id/layout_id, a severity_mixture whose era
    tag != rules_era, non-monotonic or missing sector_time_splits data (no fabricated
    boundary -- see P4: sector lines are not literally recoverable without a real reference
    trace), or a cold build with no prior_map AND insufficient reference_lap/braking_envelope
    data to derive segments at all (there is no third option; a caller with neither a seed
    nor real data has nothing to build from).
    """
```

This single function carries the entire owner-specified lifecycle (seed vs. supersede vs.
cold/historical) rather than exposing `seed_from_prior` / `build_from_scratch` /
`check_contradiction` as separate public methods. All three are the same computation
(derive boundaries from this weekend's data) with a comparison-and-branch at the end; splitting
that branch across multiple public entry points would let a caller invoke half the lifecycle
(e.g. supersede without ever comparing to the seed) and produce a map with no defensible
provenance story.

### Read paths (serving)

```python
def get_current(circuit_id: str, year: int, weekend: str) -> SegmentMap:
    """The map a consumer should score THIS weekend against. Raises LookupError if none
    exists yet for this key -- never returns None or silently falls back to a different
    weekend's map (silent-wrong-prediction is a named project failure mode)."""

def get_by_version(map_version: str) -> SegmentMap:
    """Exact-version lookup for reproduction/audit -- the counterpart to every consumer
    recording which map_version it was scored against. Raises LookupError on a miss (a
    caller citing a map_version it believes exists should fail loudly if that belief is
    wrong, not silently get something else)."""

def get_latest(layout_id: str, before_year: Optional[int] = None) -> Optional[SegmentMap]:
    """Resolves the seed source for derive_segment_map's `prior_map` argument: the most
    recently built non-historical map for this layout (optionally restricted to before a
    given year, for reproducing what a live weekend would have seen at the time). Returns
    None (not an error) when this layout has never been mapped -- a genuine cold start is an
    expected, common state, not a broken lookup."""
```

`get_latest` is the one method in this design whose only caller is the orchestrator that
drives `derive_segment_map`, not one of the six named consumers directly -- included anyway
because without it, resolving `prior_map` has no seam at all and every caller would
reimplement "find the last map for this layout" against the persistence layer directly,
which is exactly the kind of shallow duplicate access the minimal-interface constraint is
meant to prevent.

---

## Invariants

- **Tiling completeness**: `segments[0].start_m == 0.0`, `segments[-1].end_m == lap_length_m`,
  and `segments[i].end_m == segments[i+1].start_m` for every consecutive pair. No gaps, no
  overlaps, checked as a build-time postcondition inside `derive_segment_map` (raises, does
  not return a malformed map).
- **Ordering**: `segments` is tuple-ordered by `ordinal`; `ordinal` is redundant with array
  position but persisted explicitly so a consumer holding one `Segment` out of context (e.g.
  after a DB round-trip) still knows its position without re-deriving it from `segment_id`.
- **Nesting exactness**: every value in `sector_boundaries_m` equals some segment's
  `start_m`/`end_m` exactly (segments never straddle a sector line — straddling segments are
  split into same-class pieces at build time, per the owner's fixed rule); `sector_index` is
  non-decreasing along `segments` order and takes exactly the values `{1, 2, 3}`.
- **Severity weights**: present (non-`None`) iff `segment_type == CORNER`; values sum to 1.0
  within `1e-6`; keys are only meaningful paired with the owning `SegmentMap.rules_era`.
- **Version monotonicity**: `map_version` values are orderable within a `layout_id` (e.g.
  timestamp-prefixed or a strictly increasing counter scoped per layout) so `get_latest` has
  an unambiguous "most recent" without needing wall-clock comparison of unrelated layouts.
- **Immutability / reprocess-over-change-detection**: no update/patch surface exists anywhere
  in this interface (see Excluded); a superseded map is retained, not deleted or rewritten —
  `get_by_version` must keep resolving it for as long as any recorded consumer might replay it.

## Error modes

| Condition | Behavior |
|---|---|
| Unrecognized `circuit_id`/`layout_id` | `ValueError`, no silent fallback (matches the project's existing no-silent-year-fallback convention in `circuits.yaml`) |
| `severity_mixture` era tag ≠ requested `rules_era` | `ValueError` |
| Sector time/distance data missing, non-finite, or non-monotonic | `ValueError` — no fabricated boundary (P4: a best-fit boundary search over incomplete data produces a *fit artifact*, not a real FIA line; this module refuses rather than repeats that mistake) |
| Cold build, no `prior_map`, insufficient reference/braking data | `ValueError` |
| `get_current` / `get_by_version` miss | `LookupError` |
| `get_latest` miss | Returns `None` (expected cold-start state, not an error) |
| Contradiction check inconclusive (evidence too thin to confirm OR refute the seed within tolerance) | Keep the seed (`status="seeded"`) — never guess a supersede off ambiguous evidence |

## Persistence shape

SQLite, following the repo's existing `EstimateStore`/`eph_residual` pattern (typed scalar
columns + a JSON blob for the ordered nested structure, opened `mode=ro` for every read
path):

- `segment_maps` (PK `map_version`): `circuit_id, layout_id, year, weekend, rules_era,
  lap_length_m, sector_boundaries_json, status, seeded_from_map_version, built_at, reason,
  source_event_docs_json, config_fingerprint, segments_json`. `segments_json` is the ordered
  list of full `Segment` records (mirrors the existing `corner_json` blob convention in
  `eph_residual` rather than inventing a new shape).
- `segment_map_current` (PK `circuit_id, year, weekend`): `map_version` — upserted by every
  successful `derive_segment_map` call, giving `get_current` an O(1) lookup instead of a scan.
- `get_latest` queries `segment_maps` filtered by `layout_id` (and `year < before_year` when
  given), ordered by the version-monotonicity key, `status != 'historical'`, limit 1.

## Consumer usage sketches

1. **Utilization scoring**: `smap = get_current(circuit, year, weekend)`; `seg_ids =
   smap.segment_ids_for_distances(lap.distance_m)`; group the lap's telemetry by `seg_ids`
   to compute per-segment observables. Records `smap.map_version` alongside the result.
2. **Circuit fingerprint**: `smap = get_current(...)`; iterate `smap.segments` directly,
   summing `end_m - start_m` (optionally weighted by `severity_weights`) per
   `segment_type`/severity class. No SegmentMap method needed — this is the consumer's own
   derived statistic over public fields (deliberately not built into the module; see Excluded).
3. **Composed-sector validation**: `smap = get_current(...)`; group `smap.segments` by
   `sector_index`, sum per-segment predicted times, compare to official sector times.
4. **Race simulator**: `smap = get_current(...)`; walks `smap.segments` in `ordinal` order,
   using `adjacency` (`following_straight_length_m`, `direction_flip`) to structure
   correlation between adjacent draws; `segment_id` is the stable key for a persisted
   per-segment time-distribution model across weekends of the same layout.
5. **Segment-discriminativeness layer**: reads `segment_id` off `smap.segments` across many
   `get_current`/`get_by_version` calls for the same `layout_id`; relies on the
   within-layout `segment_id` stability invariant, nothing else.
6. **Grip module / practice update**: `get_current(...)` (or `get_by_version` when replaying
   a specific prior scoring run) — pure read-only lookup, no write access needed or exposed.

## Excluded, and why (the minimal-interface constraint speaking)

- **No update/patch/delete methods.** Reprocess-over-change-detection is an owner-fixed
  rule; the only way to change a map is a fresh `derive_segment_map` call producing a new
  immutable version. A patch method would invite exactly the incremental-diff behavior the
  lifecycle rule forbids.
- **No `seed_from_prior` / `build_from_scratch` / `check_contradiction` as separate public
  methods.** Collapsed into `derive_segment_map`'s single branch so no caller can invoke a
  partial lifecycle step and produce a map with incoherent provenance (see above).
- **No fingerprint/aggregate-statistics methods** (time-share, class-share, sector-composition
  error, etc.) on `SegmentMap` itself. Every one of those is a consumer-side reduction over
  public fields (`segments`, `severity_weights`, `sector_index`) that already has a natural
  home in the calling module (e.g. `regime_rollup.py`-style math stays separate from a thin
  reader, matching that module's own established split between I/O and computation).
- **No severity-mixture fitting or era-resolution logic inside SegmentMap.** Takes a
  pre-fit `MixtureFit`-shaped object; fitting is `layer2/property_mixture.py`'s (or its
  Student-t successor's) job. Owning that here would pull mixture-model internals into a
  tiling-production module for no consumer-facing benefit, and none of the six consumers
  ever need to *fit* a mixture, only read the weights that resulted from one.
- **No streaming/incremental per-lap update API.** The lifecycle is weekend-cadence
  (FP-session-triggered rebuilds), not per-lap; a live-update surface would be unused
  surface for every named consumer today.
- **No cross-layout migration/diff helper** (mapping segment ids from an old layout to a
  new one after a real track change). Consumer 5 is explicitly scoped to *within-layout*
  stability — cross-layout continuity is a different, harder problem this interface
  deliberately does not promise, rather than promising it badly.
- **No controlled vocabulary for `SubPhaseMark.name`.** The owner calls sub-phase marks
  dormant; enforcing a taxonomy now would be speculative generality for a feature nothing
  yet consumes.
- **No per-point traversal method on `SegmentAdjacency`** (e.g. `next_segment() -> Segment`)
  beyond the plain `segment_id` reference. A consumer that already has the full `segments`
  tuple can index by `ordinal + 1` directly; a live traversal method would duplicate that
  for no new capability.
- **`get_latest`/`get_current`/`get_by_version` stayed three separate functions rather than
  one polymorphic `get(**kwargs)`.** Each has a different miss-behavior contract (`None` vs.
  `LookupError`) and a different key shape (layout+optional-year vs. weekend-key vs.
  version-key); collapsing them into one call with optional arguments would hide those two
  genuinely different contracts behind one signature instead of making each explicit.
