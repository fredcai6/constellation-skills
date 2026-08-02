# Ready-to-paste packet fragment — docs/architecture/packets/physics.md

Admiral: fold this into `docs/architecture/packets/physics.md` at epic-659 closeout (append after the
existing `### Segmentation substrate (#625 ...)` section, or under a new
`### Per-weekend segment-map derivation (#662, epic #659)` heading). Do NOT let a cmdr branch write it
(map fence). Verify `git status` in BOTH the worktree AND `C:/Programs/f1Brainz` if a cartographer is
dispatched (prior cartographer wrote to the wrong checkout git-invisibly).

---

### Per-weekend segment-map derivation (#662, epic #659)

`src/physics/segment_map/derivation/` — a new subpackage that DERIVES a per-weekend `SegmentMap`
(2023-first, quali-side) and POPULATES the merged #661 runtime + store. Purely additive (no edits to any
existing module); imports every threshold from #660 `frozen_constants.py`. **MEASURED-not-wired** — no
live-prediction consumer yet (a later Phase-2/4 consumes it, per the epic plan).

- **`reference_lap.py`** — `ReferenceLap` (frozen dataclass) + `build_reference_lap` (agnostic core:
  reuses `ribbon.build_ribbon` for median-pooled XY→κ geometry, adds pooled speed `v_ref` + brake-active
  fraction on the SAME progress grid) + `reference_lap_from_store` (store-first via
  `session_fit.load_quali_session`, DB-only; optional `drivers=` subset filter). The POOLED FIELD
  reference lap; per-lap gates are demoted to observation filters (`decision:reference-lap-pooled-not-per-lap`).
- **`tiling.py`** — `tile_reference_lap`: complete contiguous STRAIGHT/BRAKING_ZONE/CORNER partition.
  Corner gate = `|curvature| > CORNER_CURVATURE_THRESHOLD` (`decision:corner-gate-is-curvature`, owner
  ruling — curvature NOT lateral-g). Braking zone = field ENVELOPE onset at `BRAKING_ONSET_QUANTILE`
  (p10 crossing of the pooled brake fraction; a mean would sit inside the zone). Straight = remainder.
- **`sector_nesting.py`** — `derive_sector_lines` (FIA sector-line time→distance interpolation, pooled
  median sub-meter, off per-year DB `lap_times.sector{1,2}_time`) + `nest_sectors` (pure: split-not-snap,
  sliver-merge exempts sector cuts, fails CLOSED) + `SectorLineUnavailableError`.
- **`corner_attributes.py`** — `compute_corner_descriptor` ([radius_m, lateral_g] at apex; a_lateral
  m/s²→g via `GRAVITY_MS2` at ONE documented call site, mirroring `segment_classifier.soft_class_membership`
  — the #639 unit boundary), `compute_turn_direction` (int8 from signed curvature),
  `fit_era_severity_mixture` (re-fit #638 k=4 from POOLED grip_bin_obs across the era),
  `compute_severity_membership` (soft; non-corner rows exactly 0.0), `derive_corner_attributes`. Consumes
  `layer2.corner_descriptors.descriptors_from_frame` + `layer2.property_mixture.fit_property_mixture` +
  `from_mixture.{MixtureFitAdapter, vocabulary_from_fit}`. Median-vs-p90 lateral_g offset is a documented,
  DEFERRED secondary-axis approximation (radius/log-radius is the dominant, purely-geometric k=4 axis).
- **`derive.py`** — `derive_segment_map(year, gp_name, session_type)` orchestrator →
  `SegmentMap.build` → (SegmentMap, VocabularyRef, MapVersion); `write_segment_map` (`SegmentMapStore.write`
  cold/historical). `layout_content_hash` fed the G2 base-tiling geometry (sector-independent).
- CLI `scripts/derive_segment_maps.py` (batch 2023 quali, idempotent); GATING harness
  `scripts/validate_segment_map_662.py` (non-map nodes).

**Import edges:** `segment_map/derivation → segment_map/{runtime,store,identity,from_mixture,protocols}`,
`→ ribbon`, `→ session_fit` (store-first; `physics→data` allowed), `→ layer2/{frozen_constants,
corner_descriptors,property_mixture,grip_bin_obs}`, `→ constants.GRAVITY_MS2`,
`→ segment_classifier.soft_class_membership` (convention mirror). Reads per-year DB `lap_times`;
grip_bin_obs in main-checkout `damage_integrals.db`.

**Capability:** `serves purpose:segment_map_derivation` (NEW).

**Deferred (T10, stated not skipped):** the per-era Student-t mixture refit + a fresh F12 gate run at
backfill when multi-era circuit diversity makes the gate meaningful. Sub-phase marks stay a reserved
dormant signature (no backing store). Adjacency computed on demand (runtime mod-arithmetic), never persisted.
