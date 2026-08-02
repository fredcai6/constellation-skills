# notes-662 — map delta for Admiral consolidation (issue #662, epic #659)

**Map fence honored:** this branch does NOT edit `docs/architecture/*`. The structural delta below is
staged for the Admiral to fold into `docs/architecture/packets/physics.md` at epic closeout. See
`662-cartography/physics-packet-delta.md` for the ready-to-paste packet fragment.

## What changed (purely additive — 15 new files, zero edits to existing modules)
A new subpackage **`src/physics/segment_map/derivation/`** that DERIVES a per-weekend `SegmentMap`
(2023, quali-side) and populates the merged #661 runtime + store. All thresholds imported from merged
#660 `frozen_constants.py`; nothing fit or literal at a call site.

### New modules (all under `src/physics/segment_map/derivation/`)
- `reference_lap.py` — `ReferenceLap`, `build_reference_lap` (agnostic core; reuses
  `physics.ribbon.build_ribbon` for median-pooled XY→κ geometry + adds pooled speed + brake-active
  fraction on one shared progress grid), `reference_lap_from_store` (store-first via
  `session_fit.load_quali_session`, DB-only; optional `drivers=` subset filter for split-half validation).
- `tiling.py` — `tile_reference_lap`: complete contiguous partition into STRAIGHT/BRAKING_ZONE/CORNER.
  Corner gate = `|curvature| > CORNER_CURVATURE_THRESHOLD` (owner ruling `decision:corner-gate-is-curvature`;
  a_lateral does NOT enter the gate). Braking zone = field ENVELOPE onset at `BRAKING_ONSET_QUANTILE`
  (p10 crossing of the pooled brake fraction, proven strictly upstream of the mean). Straight = remainder.
- `sector_nesting.py` — `derive_sector_lines` (FIA sector-line time→distance interpolation, pooled median
  sub-meter, off per-year DB `lap_times.sector{1,2}_time`) + `nest_sectors` (pure: split-not-snap,
  sliver-merge exempts sector cuts, fails CLOSED via `SectorLineUnavailableError`) + `SectorLineUnavailableError`.
- `corner_attributes.py` — `compute_corner_descriptor` ([radius_m, lateral_g] at the corner apex; a_lateral
  m/s²→g via `GRAVITY_MS2` at ONE documented call site, mirroring `segment_classifier.soft_class_membership`),
  `compute_turn_direction` (int8 from signed curvature), `fit_era_severity_mixture` (re-fit #638 k=4 from
  POOLED grip_bin_obs across the era), `compute_severity_membership` (soft, non-corner rows exactly 0.0),
  `derive_corner_attributes`.
- `derive.py` — `derive_segment_map(year, gp, session)` orchestrator (composes the above →
  `SegmentMap.build` → returns SegmentMap + VocabularyRef + MapVersion), `write_segment_map`
  (`SegmentMapStore.write` cold/historical path), `assemble_segment_map`, `weekend_key`.
  `layout_content_hash` fed the G2 base-tiling geometry (sector-independent by construction).
- `scripts/derive_segment_maps.py` — batch CLI (2023 quali, idempotent), non-map node.
- `scripts/validate_segment_map_662.py` — the GATING validation harness.

### Structural relationships (edges) for the packet
- `segment_map/derivation/*` → `segment_map/{runtime(SegmentMap.build,SegType), store(SegmentMapStore.write),
  identity(MapVersion,VocabularyRef,layout_content_hash,config_fingerprint), from_mixture(MixtureFitAdapter,
  vocabulary_from_fit), protocols(SeverityMixture)}` (populates the #661 runtime it consumes).
- → `physics.ribbon.build_ribbon` (geometry reuse).
- → `physics.session_fit.load_quali_session` (store-first telemetry; `physics → data` allowed direction).
- → `physics.layer2.{frozen_constants, corner_descriptors.descriptors_from_frame,
  property_mixture.fit_property_mixture/posterior_membership, grip_bin_obs GripBinStore}`.
- → `physics.constants.GRAVITY_MS2`, `physics.segment_classifier.soft_class_membership` (convention mirror).
- reads per-year DB `lap_times.sector{1,2,3}_time`; grip_bin_obs lives in main-checkout `damage_integrals.db`.
- **MEASURED-not-wired:** no live-prediction consumer yet (Phase-2/4 consumes later, per epic plan).

### Capability node
`serves purpose:segment_map_derivation` (NEW) — per-weekend telemetry → persisted typed SegmentMap.

## Decisions recorded (grade-tagged; for the map's decision anchors)
- decision:corner-gate-is-curvature @grade: settled/inherited (merged #660) — gate is curvature, not lateral-g.
- decision:braking-envelope-p10-not-mean @grade: settled/human — onset = field p10 envelope, never mean.
- decision:sector-split-not-snap @grade: settled/human — straddlers split same-class; sliver-merge exempts cuts; fail-closed.
- decision:a-lateral-g-boundary @grade: settled/human (#639) — m/s²→g via GRAVITY_MS2 at one documented site.
- decision:severity-refit-consume-k4 @grade: settled/human — re-fit k=4 pooled; Student-t + fresh F12 DEFERRED (T10).
- decision:derivation-subpackage-placement @grade: settled/measured — modules under segment_map/derivation/.
- decision:dormant-subphase @grade: settled/human — sub-phase reserved, not populated; adjacency not persisted.
- decision:stability-scoped-null-split-half @grade: settled/measured — cross-weekend stability is a 2023 scoped null (settle-experiment RAN: 2023 calendar = 22 GPs, zero repeats — mechanically confirmed); split-half within-weekend proxy measured (median drift Bahrain 2.18m / Austria 3.48m < 10m). Regraded guess→settled/measured at G6 (reviewer-recommended).

## Gating results (for the epic record)
- GATING-1 stability: 2023 cross-weekend = scoped NULL (22 GPs, no repeats). Split-half median boundary
  drift Bahrain 2.18m / Austria 3.48m < MAP_STABILITY_DRIFT_M (10m). PASS. (Max-drift caveat: p10
  braking-onset boundaries noisiest — 15.7m/80.7m — reported not asserted; triage candidate.)
- GATING-2 typing: Bahrain 12 physical corners ∈ P4 [11,17] (official 15); Austria 10 == official 10;
  corner distance-share 0.308 (map) vs 0.523 (regime_rollup) — directional PASS (stricter curvature gate).

## Follow-on / triage candidates (surfaced, for the Admiral to file if approved)
- tc1: `ribbon._get_clean_laps` uses `row.get('PitInTime')` which silently no-ops against DBSession
  (no PitIn/OutTime cols) — a future reuse against store-backed sessions would skip pit-lap filtering.
- tc2: `data/segment_maps.db` (the derived store the CLI writes) is NOT in `.gitignore`, unlike other
  derived `data/` stores — add it.
- tc3: split-half MAX boundary drift is large at p10 braking-zone-ONSET boundaries (median stable at
  2-3.5m); tighten the p10 onset estimate if braking boundaries become load-bearing downstream.
