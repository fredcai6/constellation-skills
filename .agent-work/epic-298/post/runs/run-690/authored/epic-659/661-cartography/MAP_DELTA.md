# Map delta — struct:physics.segment_map (issue #661, epic #659)

Scope note: this is a delta for the Admiral to fold at epic #659 closeout. No file under
`docs/architecture/` was edited by this run.

## 1. New component section for `docs/architecture/packets/physics.md`

Insert as a new sibling component section, after the existing `feature_view` section
(after line 2367 `---`, i.e. between the `feature_view` section and the packet's
`## Dependencies` section that currently starts at line 2532).

```markdown
## Component: segment_map — track SegmentMap (#661, epic #659)

```yaml
id: struct:physics.segment_map
level: component
parent: struct:physics
path: src/physics/segment_map/
status: current
confidence: high
```

Build 1 of the physics-as-feature-engine epic's track SegmentMap spec (#659): a frozen,
versioned, labeled representation of one track layout as flat PARALLEL numpy arrays
(never a list of segment objects) — O(lookup) segment assignment for the eventual
Monte-Carlo race-sim consumer, and O(n_corner) severity reclassification decoupled from
geometry. Geometry and severity classification are deliberately split: the
geometry-DERIVATION logic that feeds `SegmentMap.build`'s boundaries (#662), the join
into a race-weekend product, and the Monte-Carlo race-sim consumer are FUTURE issues in
this same epic. **MEASURED-not-wired**: no `src/` importer outside this package's own
tests yet (40 unit tests, `tests/unit/physics/segment_map/`). No evo-region import
(`constraint:physics_region_no_evo_import` honored — verified: no
`src.evo_predictor`/`src.latent_power`/`src.compound_prior` import anywhere under
`src/physics/segment_map/`).

- **`protocols.py`** — `SeverityMixture`, an `@runtime_checkable` Protocol (`k: int`,
  `version: str`, `posterior_membership(descriptors: (N,2) raw [radius_m, lateral_g]) ->
  (N,k)` posterior rows). The seam SegmentMap depends on instead of a concrete mixture —
  a future mixture swap (e.g. a Student-t core replacing today's Gaussian Layer-2 fit)
  never touches `runtime.py`. Deliberately imports nothing from Layer-2.
- **`runtime.py`** — `SegType(IntEnum)` (`STRAIGHT`/`BRAKING_ZONE`/`CORNER`) +
  `SEG_TYPE_LABELS`; frozen `SegmentMap` dataclass of flat parallel numpy arrays
  (`boundaries_m`, `length_m`, `seg_type_code` int8, `sector` int8, `turn_direction`
  int8, `corner_descriptor` (n,2), `severity_membership` (n,k), `class_ids`, plus
  primitive identity fields — no store dependency, no import cycle). Hot path:
  `segment_of` (one `np.searchsorted` + `np.mod` wrap, never raises — a flying lap
  straddling start/finish is normal on a closed loop), `type_of`, `next_ordinal`/
  `prev_ordinal` (mod arithmetic, no stored adjacency array). `reclassify_severity(mixture)`
  is the geometry/severity decoupling point: O(n_corner) membership recompute against a
  `SeverityMixture`, geometry carried through byte-identical. `__post_init__`/`build()`
  validate every shape/finiteness/sign invariant (e.g. non-corner rows must be EXACTLY
  0.0 membership, corner `radius_m` must be `> 0`).
- **`identity.py`** — frozen `VocabularyRef` (a fitted severity taxonomy; `class_ids`
  minted ONCE, fully-qualified `f"{vocabulary_id}:c{i}"`, never re-derived from a
  positional index — the reason a later k-change/era re-fit is a pure INSERT that cannot
  corrupt an already-persisted map) and `MapVersion`/`MapStatus`
  (`"seeded"|"superseded"|"historical"` — per-weekend provenance; Build 1 always writes
  `"historical"`, the seeded/supersede lifecycle ships with Build 3, #664).
  `layout_content_hash` — a geometry-ONLY sha256 over rounded (mm) cut points; the
  caller MUST strip sector-forced splits before calling (a sector line is a timing
  artifact, not a structural track difference). `config_fingerprint` — sha256 over a
  canonicalized (dataclass/dict/sequence-recursed) build config.
- **`from_mixture.py`** — the ONLY module in the package that imports the concrete
  `src.physics.layer2.property_mixture` (`MixtureFit`, `posterior_membership`) — keeps
  `runtime.py` Protocol-only. `vocabulary_from_fit` mints a `VocabularyRef` from a fit;
  `MixtureFitAdapter` wraps a bare `MixtureFit` (which does not itself satisfy
  `SeverityMixture` — no `.version`, membership is a module function not a method)
  behind the Protocol; `memberships_from_posterior` is the single place a positional
  `(k,)` posterior row crosses into labeled `{class_id: weight}` space.
- **`store.py`** — `SegmentMapStore`: SQLite persistence mirroring
  `layer2/estimate_store.py` conventions (`sqlite3.Row` factory, create-on-construct
  unless `must_exist`, additive `_migrate_missing_columns`, `INSERT OR REPLACE`
  idempotency). Tidy, class_id-keyed `segment_class_memberships` table (never wide
  per-class columns, never a positional index) — column ORDER on load is rebuilt from
  the row's OWN stored `VocabularyRef.class_ids`, never a live mixture's order, in
  `_materialize_membership` (labeled->positional exactly once per load). Three reads:
  `get_current`/`get_by_version` raise `SegmentMapNotFound` on a miss (a named map MUST
  exist); `get_latest` returns `None` on a genuine cold start (not an error — the normal
  case the Build-3 seeded path must handle). `write` is **cold-only in Build 1**: the
  `prior_map` seeded/supersede branch validates its "supersede needs a
  contradiction_reason" contract at the signature but then raises `NotImplementedError`
  (ships with Build 3, #664). `FORMAT_VERSION = "1"`.

### Dependencies (segment_map sub-package)

- Reads `struct:physics.layer2` (own container, intra-container, read-only):
  `layer2.property_mixture.MixtureFit`/`posterior_membership`, imported ONLY by
  `from_mixture.py` (the sole adapter seam; `runtime.py`/`protocols.py` stay
  Layer-2-free by design).
- No evo-region imports anywhere in the package
  (`constraint:physics_region_no_evo_import` honored — verified: no
  `src.evo_predictor`/`src.latent_power`/`src.compound_prior` import anywhere under
  `src/physics/segment_map/`).
- **No `src/` consumer yet** — MEASURED-not-wired. The geometry-derivation logic that
  feeds `SegmentMap.build`'s boundaries (#662), the join into a race-weekend product,
  and the Monte-Carlo race-sim consumer are FUTURE issues in the same epic (#659); this
  Build 1 slice is runtime + identity + store only.
- Produces a standalone artifact database (not a `struct:` node, own SQLite file via
  `SegmentMapStore.db_path`, schema: `segment_maps`, `segment_map_current`, `segments`,
  `vocabularies`, `segment_class_memberships`).

---
```

## 2. Intro bullet-list addition (same file, container-level list ~line 41-59)

The container intro already lists each component as a sibling bullet
(`struct:physics.layer2`, `struct:physics.utilization`, `struct:physics.weekend_state`,
`struct:physics.feature_view`). Add a sibling bullet after the `feature_view` bullet
(after line 59):

```markdown
- **`struct:physics.segment_map`** — Build 1 of the track SegmentMap (#661, epic #659);
  see its node below.
```

## 3. `docs/architecture/index.md` — new struct catalog node

Insert after the existing `struct:physics.feature_view` block + its "See:" line
(after line 644, before the `---` / `## Relationships` divider at line 646):

```markdown
```yaml
id: struct:physics.segment_map
level: component
parent: struct:physics
path: src/physics/segment_map/
purpose: "Build 1 of the track SegmentMap (#661, epic #659, physics-as-feature-engine): frozen flat-numpy runtime (runtime.py, SegmentMap/SegType, O(lookup) segment_of + O(n_corner) reclassify_severity decoupled from geometry) behind a SeverityMixture Protocol (protocols.py) + identity/provenance value objects (identity.py: VocabularyRef minted-once labels, MapVersion/MapStatus, layout_content_hash geometry-only, config_fingerprint) + the sole Layer-2 adapter (from_mixture.py, wraps property_mixture.MixtureFit) + a labeled versioned SQLite store (store.py, cold-write-only in Build 1, seeded/supersede raises NotImplementedError pending Build 3 #664). MEASURED-not-wired: no src/ importer outside its own tests (40 unit tests). No evo-region import."
status: current
confidence: high
```

See: [packets/physics.md](packets/physics.md) (segment_map section)
```

## 4. `docs/architecture/overlays/constraints.yml` — relationship edge

Every existing physics sub-component (`layer2`, `utilization`, `weekend_state`,
`feature_view`) carries a `constrained-by` edge to `constraint:physics_region_no_evo_import`.
`segment_map` should get the same sibling edge for consistency (append to the
`relationships:` section):

```yaml
  - source: struct:physics.segment_map
    type: constrained-by
    target: constraint:physics_region_no_evo_import
    provenance: curated
    evidence: ["no import of src.evo_predictor / src.latent_power / src.compound_prior anywhere under src/physics/segment_map/ (verified 2026-07-25)"]
    confidence: high
```

## 5. No-evo-import boundary confirmation

Confirmed by direct grep of the package: no occurrence of `evo_predictor`, `latent_power`,
or `compound_prior` anywhere under `src/physics/segment_map/` (5 modules + `__init__.py`).
The package's only cross-component read is `from_mixture.py` importing
`src.physics.layer2.property_mixture` — intra-`struct:physics`, not a boundary crossing.
`constraint:physics_region_no_evo_import` holds.

## 6. Map-truth discrepancies found

None. The landed code matches the handoff description exactly (module names, dataclass
fields, Protocol shape, store table names, 40 tests split 24 `test_runtime.py` / 16
`test_store.py`). The only gap is an **expected omission, not a discrepancy**: the
physics.md container intro bullet list and index.md's physics-components catalog
naturally don't yet mention `segment_map` because it didn't exist before this issue —
items 2 and 3 above are exactly that fill-in, following the same pattern the prior
`weekend_state`/`feature_view` reconciles used when those components first landed.
Also confirmed: `src/physics/segment_map/` has no consumer anywhere else in `src/`
(grepped `segment_map` repo-wide under `src/`) — the MEASURED-not-wired characterization
in the handoff is accurate, not an over-claim.
