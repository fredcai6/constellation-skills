# D2 — SegmentMap interface, max-flexibility variant

Excursion: design-it-twice, MAX FLEXIBILITY branch. Interface only — no bodies beyond
signatures/docstrings. Owner-ruled job description (fixed, not redesigned here) and the six
named escalation layers are treated as constraints; everything below is the seam that absorbs
them without a breaking change.

Grounding read before writing this: `src/physics/segment_classifier.py` (existing driver-level
regime classifier — untouched, sits upstream of SegmentMap as one geometry input),
`src/physics/layer2/{property_mixture,corner_descriptors,regime_rollup}.py` (the mixture
machinery this design wraps, not replaces), `src/physics/ribbon.py` (the distance axis this
tiles), `src/physics/utilization/regime_utilization.py` (an existing 4-regime tiler this
generalizes), `docs/agents/ORCHESTRATOR_CONTEXT.md` (physics/evo import boundary — SegmentMap
lives in `src/physics`, no evo imports), and the `explore-ref-utilization` IDEAS_BOARD.md
owner rulings (cycle-3 q1–q4: canonical gate, seed-then-supersede lifecycle, mixture-per-era
severity ladder, sector nesting by split).

## 0. The one design decision everything else follows from

**Every escalation layer the owner named is a new *label*, never a new *position*.**
Concretely: nothing in this interface is ever indexed by an integer that means "the i-th
thing" where i's meaning depends on how many things currently exist. Severity classes are
addressed by a `class_id` string, not a mixture-component index 0..k-1. Segments are addressed
by a `segment_id` string, not an array offset. Vocabularies are addressed by a `vocabulary_id`
string, not "the current taxonomy". Sub-phases are addressed by a `phase` string, not "the
n-th split of this corner". This one rule is *why* k changing, eras re-fitting, and phases
turning on can all be additive: a caller that hardcodes a label keeps reading exactly what it
read before; a caller that discovers labels dynamically sees new ones appear next to old ones,
never old ones renumbered out from under it.

The existing `property_mixture.py` machinery returns `posterior_membership` as a positional
`(N, k)` array — that is exactly correct for that module's job (a pure statistical core, fit
per call). SegmentMap's job is different: it is the thing that *persists* classification
results across weekends, eras, and re-fits, so it is the layer responsible for converting
positional GMM output into labeled, versioned, durable identifiers before anything gets
written down. That conversion happens once, at write time (see §4), and nothing downstream
ever sees a bare array again.

## 1. Core types

```python
# src/physics/segment_map/types.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional, Tuple

RoundId = str
"""Weekend identity, consistent with the rest of the codebase's
(year, round_num, gp_name)-keyed session_classifications convention — callers
pass whatever string already keys a weekend elsewhere (e.g. f"{round_num}:{gp_name}"),
SegmentMap does not mint a competing identifier scheme."""


@dataclass(frozen=True)
class SegmentMapId:
    """Identity of one persisted tiling. Four fields, three independent axes:

    circuit_id / year / round_id together pick the WEEKEND (the owner's stated
    keying grain). map_version is a fourth axis, orthogonal to the weekend key:
    it enumerates the seed-then-supersede chain FOR that weekend (see
    lifecycle_status on SegmentMap). It is not a global counter and not a
    content hash — plain monotonic per-(circuit_id, year, round_id) integer,
    starting at 1 for the first seed.
    """
    circuit_id: str          # stable circuit identity, NOT venue/display name (venue renames,
                              # e.g. Madrid entering the calendar, must not mint a new circuit_id
                              # for what is geometrically the same ribbon)
    year: int
    round_id: RoundId
    map_version: int


@dataclass(frozen=True)
class VocabularyRef:
    """One classification taxonomy, as it applies to one SegmentMap.

    A SegmentMap's `vocabularies` mapping (see SegmentMap below) holds zero or
    more of these, keyed by `taxonomy_name` ("severity", "transition", ...).
    Absence of a taxonomy_name key means that vocabulary has not been fit for
    this map yet — not an error, see §3 read semantics.
    """
    vocabulary_id: str       # globally unique: f"{taxonomy_name}:{rules_era}:v{fit_version}"
    taxonomy_name: str       # "severity" | "transition" | future taxonomy names
    rules_era: str           # technical-rules era key the fit pools over (cycle-3 q3 ruling)
    k: int                   # component count AT THIS fit — informational; never used as an index
    fit_version: int         # monotonic per (taxonomy_name, rules_era); bumps on re-fit
    class_ids: Tuple[str, ...]   # the full label set this vocabulary defines, stable membership
    fit_provenance: str      # free-text: what data/method produced this fit


@dataclass(frozen=True)
class SectorLine:
    sector_index: int         # 1-based; sector_index N starts at this line, N-1 ends here
    distance_m: float         # position on THIS weekend's ribbon distance axis
    derivation: str           # e.g. "time_to_distance_interpolation:pooled_median" (cycle-3 q4)


@dataclass(frozen=True)
class SubPhaseMark:
    """A dormant or promoted sub-region within a corner segment (escalation layer 1).

    Marks are arc-length breakpoints, not separate tiling rows, by default —
    see §5.1 for why, and for what "promoted" means.
    """
    phase: str                # "entry" | "apex" | "exit" — open string, not a fixed enum, so a
                               # finer phase vocabulary (e.g. "entry_early"/"entry_late") is a
                               # new string, never a schema change
    start_m: float
    end_m: float
    is_addressable: bool = False   # False = informational mark only (default, current state).
                                    # True = this phase also exists as its own row in the
                                    # subphase-resolution tiling (see SegmentMap.get_tiling).


@dataclass(frozen=True)
class SegmentAdjacency:
    """Neighbor context for one segment (escalation layer 2's raw material).

    COMPUTED, never persisted — see §5.2 for why. Always available (not
    optional/dormant) because it costs nothing: every field here is derivable
    from the segment list itself plus whichever vocabularies happen to be
    populated. What CAN be genuinely absent is class-derived fields when the
    referenced vocabulary isn't fit yet (see field docs below).
    """
    prev_segment_id: Optional[str]
    next_segment_id: Optional[str]
    following_straight_length_m: Optional[float]   # None only at a lap-boundary edge case
    direction_flip: Optional[bool]     # True if this corner's turn_direction differs from the
                                        # previous corner's; None for non-corner segments
    def prev_class(self, vocabulary_name: str = "severity") -> Optional[str]:
        """Argmax class_id of the previous segment under `vocabulary_name`, or
        None if there is no previous segment OR that vocabulary isn't populated
        on it. Lazy — resolved against the owning SegmentMap, not stored."""
        ...
    def next_class(self, vocabulary_name: str = "severity") -> Optional[str]:
        ...


@dataclass(frozen=True)
class Segment:
    segment_id: str            # see §5.3 for the stability contract — read it before using this
                                # for anything beyond "one row in one SegmentMap"
    parent_id: Optional[str]   # None for a macro-resolution segment; set for a promoted
                                # subphase segment, pointing back to its macro segment_id
    ordinal: int                # 0-based position in THIS map_version's segment order.
                                # POSITION, NOT IDENTITY — do not persist ordinal anywhere as a
                                # cross-map-version key; it can and will shift.
    start_m: float               # ribbon distance, inclusive
    end_m: float                 # ribbon distance, exclusive
    segment_type: str            # "corner" | "braking_zone" | "straight" — open string (see §5.4
                                  # for why this is not a closed enum)
    turn_direction: Optional[str]    # "left" | "right"; None for straight/braking_zone
    sector: int                  # 1-based FIA sector this segment nests inside, exactly one
                                  # (sector lines are mandatory cuts — see SegmentMap invariant)
    class_memberships: Mapping[str, Mapping[str, float]]
        # vocabulary_id -> {class_id: weight}. Missing vocabulary_id key == not yet classified
        # under that taxonomy (soft-missing, not an error — see §3). Present entries sum to 1.0
        # (mixture posterior) or are a singleton {class_id: 1.0} for non-probabilistic
        # taxonomies. Keyed by vocabulary_id (not taxonomy_name) so a re-fit's old and new
        # vocabulary can coexist on historical rows without collision (see §5.6).
    subphases: Tuple[SubPhaseMark, ...]   # empty by default (escalation layer 1, dormant)
    attrs: Mapping[str, Any]              # namespaced escape hatch, see §5.7 — staging only

    def adjacency(self, segment_map: "SegmentMap") -> SegmentAdjacency:
        """Computed accessor — see SegmentAdjacency docstring and §5.2."""
        ...


@dataclass(frozen=True)
class MapProvenance:
    method: str                 # "seed_from_prior_year" | "seed_from_fia_docs" |
                                 # "live_reclassification" | "historical_post_hoc"
    source_map: Optional[SegmentMapId]   # the map this was seeded/superseded from, if any
    source_laps: Tuple[str, ...]         # lap identifiers backing geometry/sector-line derivation
    created_at: datetime
    contradiction_reason: Optional[str]  # populated on the map_version that SUPERSEDES a prior
                                          # one: what evidence contradicted it (owner: "seed...
                                          # superseded on contradiction")


@dataclass(frozen=True)
class SegmentMap:
    id: SegmentMapId
    schema_version: str          # format/shape version of THIS dataclass tree, e.g. "segmap/1".
                                  # Bumped only when the Segment/SegmentMap SHAPE changes (a new
                                  # typed field added) — orthogonal to map_version (content) and
                                  # to vocabulary fit_version (classification content within a
                                  # fixed shape). A consumer can check this once at import time
                                  # and assert a minimum without caring about map_version at all.
    layout_version: str          # physical-layout identity, e.g. "silverstone:v3" — changes ONLY
                                  # on a real track-geometry change (escalation layer 5), bumped by
                                  # whoever curates the map on FIA/observed evidence. Independent
                                  # of rules_era: a layout can outlive several rules eras, and a
                                  # rules era can outlive several layouts at other circuits.
    lifecycle_status: str         # "seed" | "confirmed" | "superseded" | "historical"
    superseded_by: Optional[SegmentMapId]
    provenance: MapProvenance
    sector_lines: Tuple[SectorLine, ...]     # len == number of sectors (3 for current-era F1,
                                              # not hardcoded — read len(), don't assume 3)
    segments: Tuple[Segment, ...]            # macro resolution, ordinal-ordered, see get_tiling
    vocabularies: Mapping[str, VocabularyRef]   # keyed by vocabulary_id (§5.6)

    def get_tiling(self, resolution: str = "segment") -> Tuple[Segment, ...]:
        """The one read path every consumer should use instead of touching
        `.segments` directly (kept public for iteration/debugging, but
        `get_tiling` is the contract). `resolution="segment"` (default) returns
        exactly `self.segments` — macro rows only, subphases collapsed into
        their `subphases` marks. `resolution="subphase"` returns the finer
        tiling where any `is_addressable=True` SubPhaseMark has been promoted
        to its own Segment row (parent_id set); segments with no promoted
        subphases pass through unchanged. Raises `ResolutionNotAvailable` if
        `"subphase"` is requested and this map has no addressable subphases at
        all (distinguishes "not escalated yet" from "silently returns the same
        thing", so callers who explicitly opted into subphase resolution find
        out they got nothing, rather than mistaking macro rows for subphase
        rows).
        """
        ...

    def segment_at(self, distance_m: float, *, resolution: str = "segment") -> Segment:
        """Binary search over start_m/end_m in the requested resolution's
        tiling. Raises `ValueError` if distance_m is outside [0, lap_length_m).
        """
        ...

    @property
    def lap_length_m(self) -> float: ...

    def validate(self) -> None:
        """Raises `IncompleteTilingError` unless `segments` (macro resolution)
        partitions [0, lap_length_m) exactly once with no gap or overlap, is
        ordinal-sorted and contiguous, and every segment's `sector` matches a
        `sector_lines` bracket. Called at write time by the store; exposed
        publicly so tests and reprocessing jobs can call it directly."""
        ...
```

## 2. Persistence shape

The single highest-leverage decision for the "k changing" and "era re-fit" escalation layers:
**class memberships are stored tidy (long/EAV), never as wide per-class columns.**

```
segment_maps(circuit_id, year, round_id, map_version,        -- PK
             schema_version, layout_version, rules_era_default,
             lifecycle_status, superseded_by_version,
             provenance_json, created_at)

sector_lines(circuit_id, year, round_id, map_version,         -- FK
             sector_index, distance_m, derivation)

segments(circuit_id, year, round_id, map_version,             -- FK
         segment_id, parent_id, ordinal, start_m, end_m,
         segment_type, turn_direction, sector)

segment_subphase_marks(segment_id (+ map FK), phase, start_m, end_m, is_addressable)

segment_class_memberships(segment_id (+ map FK), vocabulary_id, class_id, weight)
    -- tidy: one row per (segment, vocabulary, class). Adding a vocabulary, or a
    -- fit_version with a different k, is a pure INSERT. No migration, no NULL
    -- column sprawl, no "class_5" appearing on rows from before k=5 existed.

vocabularies(vocabulary_id,                                    -- PK
             taxonomy_name, rules_era, k, fit_version,
             class_ids_json, fit_provenance)
```

`SegmentAdjacency` and the subphase-*promotion* (as opposed to the marks table above) are
intentionally absent from persistence — see §5.1 and §5.2 for why they're computed, not stored.

## 3. Store / service API

```python
# src/physics/segment_map/store.py

class SegmentMapNotFound(Exception): ...
class ResolutionNotAvailable(Exception): ...
class IncompleteTilingError(Exception): ...
class LayoutVersionConflict(Exception): ...


class SegmentMapStore:
    """SQLite-backed (per §2), read/write. Concrete class, not a Protocol —
    consistent with estimate_store.py / grip_bin_obs.py / race_stint_store.py's
    existing pattern in this package (no injectable-seam need identified yet;
    add one the day a second backend is real, not preemptively)."""

    def __init__(self, db_path: str) -> None: ...

    # --- reads ---
    def get(
        self,
        circuit_id: str,
        year: int,
        round_id: RoundId,
        *,
        map_version: Optional[int] = None,   # None = latest non-superseded
        as_of: Optional[datetime] = None,    # pins to whatever was live at this instant
                                              # (reprocessing determinism for backtests —
                                              # mutually exclusive with map_version)
    ) -> SegmentMap:
        """Raises SegmentMapNotFound if no map exists for this weekend key at
        all. Never raises for an unpopulated vocabulary — that's soft-missing
        (§0), read it off `.vocabularies` / `.class_memberships` instead."""
        ...

    def get_by_id(self, map_id: SegmentMapId) -> SegmentMap: ...

    def history(self, circuit_id: str, year: int, round_id: RoundId) -> Tuple[SegmentMapId, ...]:
        """Full seed-then-supersede chain, oldest first."""
        ...

    def vocabulary(self, vocabulary_id: str) -> VocabularyRef:
        """Standalone lookup — lets a consumer resolve a vocabulary_id it found
        on a segment without loading the whole map again."""
        ...

    # --- writes (reprocess-over-change-detection: owner ruling, no partial patch API) ---
    def write_seed(self, segment_map: SegmentMap) -> None:
        """Inserts a new map_version with lifecycle_status='seed'. Calls
        segment_map.validate() first. Raises ValueError if a seed already
        exists and is not superseded for this weekend key (supersede
        explicitly, don't silently overwrite)."""
        ...

    def supersede(self, new_segment_map: SegmentMap, *, contradiction_reason: str) -> None:
        """Writes new_segment_map as the next map_version, flips the previous
        live version's lifecycle_status to 'superseded' with superseded_by set.
        new_segment_map.provenance.contradiction_reason must be set (or is
        filled from the contradiction_reason arg) — a supersession with no
        recorded reason is a write-time error, not a debugging exercise later."""
        ...

    def write_historical(self, segment_map: SegmentMap) -> None:
        """For post-hoc-built (never-live) maps — no supersede chain
        requirement, lifecycle_status='historical'."""
        ...
```

## 4. How a mixture fit becomes a vocabulary + memberships (the label conversion from §0)

Not part of the public interface (it's the ONE write-time adapter, lives in
`src/physics/segment_map/from_mixture.py`), but worth stating so the "vocabulary_id, not k"
design isn't just assertion:

```python
def vocabulary_from_fit(fit: MixtureFit, taxonomy_name: str, rules_era: str, fit_version: int) -> VocabularyRef:
    """class_ids = tuple(f"{taxonomy_name}:{rules_era}:v{fit_version}:c{i}" for i in range(fit.k))
    — minted ONCE at fit time, then frozen into every persisted row. Nothing
    downstream ever re-derives a class_id from a component index again."""
    ...

def memberships_from_posterior(vocabulary: VocabularyRef, posterior_row: np.ndarray) -> dict[str, float]:
    """dict(zip(vocabulary.class_ids, posterior_row.tolist())) — the ONE place
    property_mixture.py's positional (N, k) array output crosses into labeled
    space."""
    ...
```

## 5. Escalation layers — mechanism + worked "what breaks" check

For each layer: what activating it means concretely, and a direct answer to "what does a
consumer who ignores it have to change" — the answer is always checked against a specific
existing/planned consumer from the six named.

### 5.1 Corner sub-phases (entry/apex/exit) activating later

**Now:** `Segment.subphases` is always `()`. **Activating:** the pipeline that derives
sub-phase boundaries (out of scope here) starts populating `SubPhaseMark` tuples with
`is_addressable=False` — informational only, e.g. utilization scoring could optionally report
"how much of this corner's braking happened before vs after the marked entry point" without
the tiling itself changing shape. **Escalating further** (phases becoming independently
classified, e.g. their own grip-relevant class memberships): flip `is_addressable=True` and the
subphase becomes a real row, but ONLY in the `resolution="subphase"` tiling.

*Check against consumer 1 (utilization scoring, `regime_utilization.py`'s eventual SegmentMap
consumer):* it calls `smap.get_tiling()` with the default `resolution="segment"`. That call
returns exactly the same 20-ish macro rows it returned before phases existed — literally
`self.segments`, untouched by whether any `subphases` tuple is populated or promoted. Nothing
changes. A consumer that wants phase detail opts in with `resolution="subphase"` and gets a
longer, `parent_id`-linked list; a consumer that doesn't ask, doesn't see it.

### 5.2 Transition/adjacency-based compound classes

Two distinct things hide under this name and the interface separates them:

- **Adjacency as raw material** (`SegmentAdjacency`) is COMPUTED, not persisted (§1). It costs
  nothing to have "on" day one because it's derived from `ordinal` + neighbor lookups + whatever
  vocabularies exist — there is no activation event for it at all, it's just always callable.
- **A "transition" vocabulary** (compound classes defined over adjacency, e.g. "fast-corner-into-
  hairpin") is a NEW `taxonomy_name` in `vocabularies`, e.g. `vocabulary_id =
  "transition:2026-current:v1"`, added to a segment's `class_memberships` dict alongside
  `"severity:..."`, never replacing it.

*Check against consumer 2 (circuit fingerprint):* existing code reads
`seg.class_memberships.get("severity:2026-current:v1", {})` (or resolves the current severity
vocabulary_id via `store.vocabulary(...)` lookup by `taxonomy_name`). When a transition
vocabulary is added, that dict gains a second key. Code that only ever indexed the severity key
sees an unchanged value at that key. Code that wants transition-aware fingerprints reads the
new key explicitly — an opt-in addition, not a migration.

### 5.3 Per-class grip curves

**Deliberately NOT a SegmentMap field.** A grip curve is fit/owned by the grip module (cycle-3
q6: "one canonical module... field-pooled fit"), keyed by `(rules_era, vocabulary_id,
class_id)`. SegmentMap supplies the `(rules_era, vocabulary_id, class_id)` triple on every
segment (via `vocabularies[vid].rules_era` + `class_memberships[vid]`'s keys); the grip module
looks its curve up by that same triple in its own store. This is a join at query time, not a
field SegmentMap carries.

*Check against consumer 6 (grip module + practice update lookups):* the grip module's read path
is `grip_store.curve_for(rules_era=vocab.rules_era, vocabulary_id=vid, class_id=cid)` for each
`(vid, cid)` a segment reports. If SegmentMap grows a new vocabulary tomorrow, the grip module's
existing lookups for the old vocabulary_ids are byte-identical; a curve for the new vocabulary
simply doesn't exist yet in the grip store until someone fits one — a `KeyError`/miss on a genuinely
absent curve, not a schema break.

### 5.4 Era changes re-fitting the class vocabulary

A re-fit for `rules_era="2026-current"` produces `fit_version=2` (`vocabulary_id =
"severity:2026-current:v2"`), a NEW `VocabularyRef`, entirely separate `class_ids` from `v1`.
Historical `SegmentMap` rows already written under `v1` are never rewritten — their
`class_memberships` keys stay `"severity:2026-current:v1"` forever (immutability of history,
matching the owner's "map version cited per observable row" ruling generalized to vocabularies).
A *live* weekend gets reprocessed (seed-then-supersede, §3 `supersede`) to pick up `v2` when the
grip/severity team decides the old fit is stale.

*Cross-era comparison* (e.g. a fingerprint spanning both eras) is explicitly NOT SegmentMap's
problem to solve silently — there is no automatic `v1`-to-`v2` translation, because none is
generally correct (component count and physical meaning can both shift). A `VocabularyRegistry`
helper (separate, optional module) can offer best-effort nearest-mean class translation for
consumers that want it; SegmentMap's job stops at making both vocabularies identifiable and
co-addressable, never at reconciling them.

*Check against consumer 2 again:* a fingerprint job written against `v1` and hardcoding that
`vocabulary_id` keeps computing the exact same thing on old weekends after `v2` exists elsewhere
in the store — it's reading a specific labeled key, not "whatever the current severity
vocabulary is." Only a fingerprint job that explicitly asks the store for "the vocabulary_id
whose `taxonomy_name == 'severity'` and `rules_era` matches this weekend" sees the new version,
and that's by its own choice of lookup, not a forced break.

### 5.5 Layout changes mid-era

`layout_version` is orthogonal to `rules_era` and to `map_version` (§1). A mid-era layout change
(track-geometry edit) triggers `write_seed` with a bumped `layout_version` string and a fresh
`map_version=1` for that weekend under the new geometry — it does NOT force a vocabulary re-fit
(severity classes fit on `(radius, lateral_g)` descriptors can carry over unchanged if the rules
era hasn't changed) and does NOT force a schema_version bump (shape is unaffected). Cross-year
`segment_id`-based joins (discriminativeness layer, §5.6) that span a layout change must check
`layout_version` equality first — `LayoutVersionConflict` is raised by that join helper, not
silently produced as garbage.

*Check against consumer 4 (race simulator, per-segment draws):* reads whichever `SegmentMap` the
weekend's `get(circuit_id, year, round_id)` call returns — always the current weekend's map, so
a layout change occurring between weekends is invisible to it beyond "this weekend's segment
list looks different," which is the correct, expected behavior (the track physically changed),
not a broken contract.

### 5.6 Possible future finer class ladders (k changing)

Exactly the §5.4 mechanism (`fit_version` bump), specialized: `k` moving from 4 to, say, 6 within
the same `taxonomy_name`/`rules_era` is a new `vocabulary_id` with `k=6` and 6 fresh `class_ids`
that share no positional relationship with the old 4 (§0 — labels, not positions, so there is no
"class 4 used to not exist, now it does" index-shift bug class at all). The tidy persistence
(§2) means this is a pure `INSERT`, not a migration.

## 6. Consumer usage sketches (all six named)

```python
# 1. Utilization scoring — mask lap telemetry into segments
smap = store.get(circuit_id, year, round_id)
for sample in lap_telemetry:
    seg = smap.segment_at(sample.distance_m)
    regime = seg.segment_type          # only field touched — immune to every escalation above

# 2. Circuit fingerprint — per-class time-shares via reference lap
smap = store.get(circuit_id, year, round_id)
severity_vid = next(v.vocabulary_id for v in smap.vocabularies.values()
                     if v.taxonomy_name == "severity")
for seg in smap.get_tiling():
    for class_id, weight in seg.class_memberships.get(severity_vid, {}).items():
        time_shares[class_id] += weight * reference_lap_time(seg)

# 3. Composed-sector validation
smap = store.get(circuit_id, year, round_id)
by_sector: dict[int, list[Segment]] = defaultdict(list)
for seg in smap.get_tiling():
    by_sector[seg.sector].append(seg)   # never straddles by construction (validate())
composed = {s: sum(reference_lap_time(seg) for seg in segs) for s, segs in by_sector.items()}
compare(composed, official_sector_times(year, round_id))

# 4. Race simulator — correlated per-segment draws
smap = store.get(circuit_id, year, round_id)
for seg in smap.get_tiling():
    adj = seg.adjacency(smap)
    prev_draw = draws.get(adj.prev_segment_id)   # None if unpopulated/edge -> falls back to an
    draws[seg.segment_id] = sample_correlated(seg, prev_draw)  # independent/default-kernel draw

# 5. Segment-discriminativeness layer (future) — stable within-layout ids
smap = store.get(circuit_id, year, round_id)
for seg in smap.get_tiling():
    # segment_id is arc-length-anchored WITHIN layout_version (owner ruling, cycle-3 q2) —
    # scoped to THIS use, not a general cross-weekend join key elsewhere in the interface.
    discriminativeness_table[(smap.layout_version, seg.segment_id)].append(observation)

# 6. Grip module + practice-update lookups
smap = store.get(circuit_id, year, round_id)
for seg in smap.get_tiling():
    for vid, memberships in seg.class_memberships.items():
        vocab = smap.vocabularies[vid]
        for class_id, weight in memberships.items():
            curve = grip_store.curve_for(vocab.rules_era, vid, class_id)  # separate store, §5.3
            apply_weighted(seg, curve, weight)
```

## 7. Error modes summary

| Condition | Behavior |
|---|---|
| No map exists for `(circuit_id, year, round_id)` | `SegmentMapNotFound` (get) |
| Requested vocabulary not fit on this map | Soft-missing: empty `{}` from `class_memberships.get(vid, {})`, no exception |
| `resolution="subphase"` with no addressable subphases anywhere in the map | `ResolutionNotAvailable` |
| Persisted/constructed tiling has a gap, overlap, or sector straddle | `IncompleteTilingError` (`validate()`, called at every write) |
| Cross-map join assumes `segment_id` comparability across differing `layout_version` | `LayoutVersionConflict` (raised by the join helper, not by SegmentMap itself) |
| `write_seed` called when a live (non-superseded) seed already exists | `ValueError` — supersede explicitly |
| `supersede` called without a contradiction reason | `ValueError` at write time |

## 8. Where flexibility costs complexity, and the calls made

- **Tidy `segment_class_memberships` table vs wide per-class columns.** Costs: extra join per
  read, less self-documenting in raw SQL, more rows. Verdict: **worth it** — this is the one
  decision the owner's stated escalations (k changing, era re-fits) directly stress-test, and a
  wide-column schema would need a migration on every single one of them.

- **String-keyed `class_id`/`vocabulary_id` vs int/positional.** Costs: an indirection through
  `VocabularyRef` to know what a `class_id` even means; slightly more verbose call sites.
  Verdict: **worth it** — the alternative (positional indices persisted across re-fits) is a
  silent-corruption risk the moment k changes, not just an inconvenience.

- **`resolution` parameter / dual macro-vs-subphase tiling.** Costs: two representations to keep
  consistent (`parent_id` bookkeeping), an API surface most callers never touch. Verdict:
  **defer the backing implementation, keep the signature now.** The owner has already deferred
  phase-level fingerprint axes once ("huge utility, great deal more complexity, save for later"
  — IDEAS_BOARD rejected/culled). Reserving `get_tiling(resolution=...)` today costs nothing
  (it's one parameter with one working value); building the promotion machinery behind it before
  anything needs `resolution="subphase"` would be paying the complexity bill early for no return.
  Recommendation: ship `SubPhaseMark`-only (informational, `is_addressable` always `False`) in
  the first cut; treat subphase promotion as its own follow-on issue when phase-level
  classification is actually designed.

- **`SegmentAdjacency` as a computed accessor vs a persisted denormalized field.** Costs: a
  method call instead of a field read, and it must be re-derivable purely from `ordinal` +
  neighbor `start_m/end_m/turn_direction` + whichever `class_memberships` happen to exist — it
  cannot depend on anything NOT already in the segment list. Verdict: **worth it, and cheaper
  than the alternative**: a persisted adjacency field would need write-time sync on every
  reprocess (§3 `supersede`) and would be one more place a stale value could survive a
  supersession by mistake. Computing it removes that failure mode entirely — there being no
  escalation "event" for adjacency at all (§5.2) is a direct consequence of this call.

- **`attrs: Mapping[str, Any]` escape hatch on `Segment`.** Costs: type safety, discoverability,
  a place bugs hide (a typo'd key silently returns nothing instead of failing). Verdict:
  **keep, but as a documented staging convention only** — anything that lives in `attrs` for
  more than one escalation cycle should be promoted to a typed field (bumping `schema_version`),
  not left there permanently. It exists for the layer the owner's six named ones don't cover:
  genuinely unanticipated future needs, where the alternative (no escape hatch at all) means a
  schema_version bump for even a single experimental field.

- **Open string `segment_type`/`turn_direction`/`phase` instead of closed enums.** Costs: no
  compile-time exhaustiveness checking, a typo produces a new silent "type" instead of a caught
  error. Verdict: **worth it for `segment_type`** (owner's three named types are stable, but a
  closed Python `Enum` would need a code change — not just a data insert — the day a fourth type
  is ever needed, e.g. a distinguished "pit_entry" segment) **and worth it for `phase`** (per
  §1's `SubPhaseMark` docstring — a finer phase vocabulary is plausible and should be a string
  change, not a schema change). Mitigated by `SegmentMap.validate()` maintaining an
  allow-list check against a small module-level constant (not a hard enum) so typos are still
  caught, without foreclosing deliberate new values.

## 9. Explicit non-goals

- No cross-vocabulary translation logic (a `VocabularyRegistry` best-effort mapper is sketched
  as a *possible* separate module in §5.4, not designed here).
- No opinion on how `SubPhaseMark` boundaries or transition-vocabulary fits are computed — this
  is the storage/serving contract for their output, not the fitting machinery (that's
  `property_mixture.py`'s and its future siblings' job, per §4's single adapter seam).
- No opinion on how `layout_version` bumps are *detected* (FIA docs, geometry diff, manual
  curation) — only that the field exists and is load-bearing for identity once a change is
  known.
