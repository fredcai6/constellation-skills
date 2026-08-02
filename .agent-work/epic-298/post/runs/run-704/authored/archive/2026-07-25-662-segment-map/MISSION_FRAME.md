# Mission Frame — #662 per-weekend segment-map derivation

## Intent
Produce a per-weekend (2023, quali-side) **derivation** that tiles a circuit lap into physically-typed
segments and POPULATES the merged flat-array `SegmentMap` (#661), with every threshold imported from
merged `frozen_constants.py` (#660). Non-trivial build: the map keystone of epic #659. Map is context
here (physics packet is current); this frame is full, not skipped.

## Affected Capabilities
- **serves purpose:segment_map_derivation (NEW)** — turn per-weekend telemetry into a persisted
  `SegmentMap`. No prior implementation; this run creates it.
- **`SegmentMap` runtime (#661)** — the target object. `SegmentMap.build(...)` factory +
  `reclassify_severity(mixture)` consumed as-is; runtime.py stays Protocol-only (do not import
  concrete mixture there).
- **`SegmentMapStore` (#661 G2)** — cold/historical `write(map, vocab, MapVersion)` persistence.
- **Layer-2 severity substrate (#625/#638/#642)** — `corner_descriptors.descriptors_from_frame`,
  `property_mixture.fit_property_mixture` (k=4), `grip_bin_obs` table; `MixtureFitAdapter` +
  `vocabulary_from_fit` bridge (#661 from_mixture).
- **`ribbon.build_ribbon`** — median-pooled XY→κ(s); reused for the reference-lap geometry.

## Examples / Events
- Bahrain 2023: P4-RESULT records ~14.13 corner arcs/lap (min 11 / max 17); BIC = 15 official turns,
  lap ~5412 m. → typing spot-check reference (GATING check 2).
- #625 `regime_rollup` per-circuit corner tallies → second typing spot-check reference.

## Structural Anchors
- struct:src/physics/segment_map/runtime.py — SegmentMap.build / reclassify_severity / SegType, file
- struct:src/physics/segment_map/store.py — SegmentMapStore.write (cold path), file
- struct:src/physics/segment_map/from_mixture.py — MixtureFitAdapter, vocabulary_from_fit, file
- struct:src/physics/segment_map/identity.py — VocabularyRef, MapVersion, layout_content_hash (GEOMETRY cut points only)
- struct:src/physics/layer2/frozen_constants.py — CORNER_CURVATURE_THRESHOLD, BRAKING_ONSET_QUANTILE, MIN_SEGMENT_LENGTH_M, MAP_STABILITY_DRIFT_M
- struct:src/physics/ribbon.py — build_ribbon (agnostic core, reuse), file
- struct:src/physics/layer2/corner_descriptors.py — descriptors_from_frame; bin_row_to_descriptor
- struct:src/physics/layer2/property_mixture.py — fit_property_mixture / MixtureFit / posterior_membership
- struct:src/physics/layer2/grip_bin_obs.py — grip_bin_obs table (mixture re-fit source)
- struct:src/data/telemetry_store.py — durable per-lap X/Y/Speed/brake source (#541)
- struct:src/physics/session_fit.py — load_quali_session (store-first, cache-fallback) sample source
- struct:src/physics/segment_map/derivation/ (NEW subpackage) — reference_lap, tiling, sector_nesting, corner_attributes, derive
- struct:data/f1_data_2023.db lap_times.sector{1,2,3}_time — FIA sector-time source

## Governing Constraints / Assumptions
- constraint:frozen-constants — every threshold imported from frozen_constants.py; never a literal at
  the call site; never fit here. Changing a frozen value = STOP + float (new named set + re-run).
- constraint:db-only-analysis — no FastF1/live calls from analysis code; read the durable
  TelemetryStore + per-year DB. build_session_ribbon (FastF1-direct) NOT used.
- constraint:no-frame-kill — a measured negative / scoped null is a complete deliverable.
- constraint:pre-quali-fixed-per-weekend — map is fixed per weekend, upstream of prediction; no race
  outcome leakage; every lap scored against the fixed map (driver-invariance by construction).
- constraint:runtime-invariants — boundaries 0→lap_length strictly increasing; corner_descriptor
  finite + radius>0 on CORNER rows; severity_membership EXACTLY 0.0 on non-CORNER rows.
- constraint:map-fence — do NOT edit docs/architecture/* on the branch; stage map delta for Admiral.
- assumption:one-weekend-per-circuit-2023 — F1 runs each circuit once/season ⇒ cross-weekend stability
  is a scoped null within 2023-only.

## Decision Anchors & Decision Pressure
- decision:corner-gate-is-curvature — corner/straight gate is curvature > CORNER_CURVATURE_THRESHOLD
  off the reference lap, NOT lateral-g; a_lateral does not enter the gate.
  @grade: settled/inherited (merged #660 frozen_constants.py) · leans g2-*
- decision:reference-lap-pooled-not-per-lap — the gate is computed off a FIELD REFERENCE (pooled)
  lap; per-lap kinematic gates are demoted to observation filters.
  @grade: settled/human (launch order Pre-Rulings, spec §1) · leans g1-*,g2-*
- decision:braking-envelope-p10-not-mean — braking-zone onset = field ENVELOPE at BRAKING_ONSET_QUANTILE
  (p10) running to corner entry; NEVER a mean (a mean sits inside the real zone).
  @grade: settled/human (launch order, frozen const) · leans g2-*
- decision:sector-split-not-snap — FIA sector lines are mandatory cut points; straddlers SPLIT into
  same-class pieces (never snap); sliver-merge EXEMPTS sector cuts; nesting fails CLOSED
  (SectorLineUnavailableError).
  @grade: settled/human (launch order, spec §1) · leans g3-*
- decision:a-lateral-g-boundary — a_lateral is m/s² (#639); convert to g via GRAVITY_MS2 ONLY at the
  corner-descriptor call site, documented inline. No second conversion elsewhere.
  @grade: settled/human (#639, physics-unit-conventions.md) · leans g4-*
- decision:severity-refit-consume-k4 — re-fit the #638 k=4 mixture from grip_bin_obs (no persisted
  artifact); consume k=4 as-is; per-era Student-t refit + fresh F12 gate DEFERRED (review T10, stated).
  @grade: settled/human (launch order T10 deferral) · leans g4-*
- decision:dormant-subphase — sub-phase marks stay a reserved marks-only signature (no backing store,
  not populated); adjacency computed on demand (runtime mod-arithmetic), never persisted.
  @grade: settled/human (launch order) · leans g4-*,g5-*
- decision:corner-marker-cosmetic — official corner-number labels are optional cosmetic join at the
  very end only; default SKIP (map must be fully correct with zero official-corner input).
  @grade: guess · leans g4-*/g5-* · settle: skip unless the join is <~20 lines and needs no tuning
- decision:stability-scoped-null-split-half — cross-weekend stability is a scoped null for 2023;
  deliver split-half within-weekend boundary-drift as the substantive robustness proxy + report the gap.
  @grade: guess · leans g6-* · settle: enumerate 2023 calendar (confirm no circuit repeats); if a
  disjoint 2nd lap-set exists use it, else split-half
- **Decision pressure (candidate):** placement of the derivation subpackage
  (`segment_map/derivation/` vs `layer2/` vs a sibling) — surfaced to reconcile/cartographer.

## Claims / Evidence Surfaces
- claim:tiling-complete — segments partition the lap, no gaps/overlaps (construction check, g2/g3 tests).
- claim:sector-nesting-exact — every FIA sector line is a boundary; straddlers split; slivers merged
  except at sector cuts (construction check, g3 tests).
- claim:map-stable — same-circuit boundary drift < MAP_STABILITY_DRIFT_M (GATING; scoped null 2023 →
  split-half proxy, g6).
- claim:typing-correct — corner count + locations match P4 Bahrain (~14–15) + #625 rollup tallies
  (GATING, g6).

## Map Confidence / Staleness / Disputes
- src/physics/segment_map/* : current, freshly merged (#661) — high confidence; verified by direct read.
- frozen_constants.py corner gate : the CORNER_CURVATURE_THRESHOLD docstring states it is "NOT
  independently proven as the corner/straight gate" — carried pending THIS run's typing spot-checks +
  stability gate. Plan does NOT retune it; if a spot-check flags it, route to structural work / float
  (no silent retune) per constraint:frozen-constants.
- reference-lap + sector-line derivation : NO prior implementation → built fresh, test-led.

## Out of Scope
Cross-year corner history; per-corner identity beyond arc-length within a layout version; live/seeded
write path (Build 3 #664); per-era Student-t refit + fresh F12 gate; sub-phase population; wiring the
map into any live prediction path (MEASURED-not-wired substrate, per epic plan).
