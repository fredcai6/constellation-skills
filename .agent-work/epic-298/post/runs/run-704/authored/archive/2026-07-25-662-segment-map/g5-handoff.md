# Implementer Handoff — G5 Assembly + persistence + derivation entrypoint

## Gate
g5 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Task
Compose G1–G4 into the end-to-end derivation, build the `SegmentMap`, and persist it. New files:
- `src/physics/segment_map/derivation/derive.py`
- `scripts/derive_segment_maps.py` (CLI, non-map node)
- `tests/unit/physics/segment_map/derivation/test_derive.py`

Provide `derive_segment_map(year, gp_name, session_type="Q", ...) -> (SegmentMap, VocabularyRef,
MapVersion)` that:
1. `reference_lap_from_store(year, gp_name, session_type)` (G1) → ReferenceLap.
2. `tile_reference_lap(ref)` (G2) → base tiling (boundaries + seg_type_code) — KEEP these base
   "geometry cut points" for the layout hash (they carry NO sector-forced splits yet).
3. `derive_sector_lines(year, gp_name, session_type)` + `nest_sectors(...)` (G3) → nested tiling +
   sector array.
4. `derive_corner_attributes(...)` (G4) → corner_descriptor, turn_direction, severity_membership +
   the fitted `MixtureFitAdapter` and its `VocabularyRef`.
5. `SegmentMap.build(...)` with all arrays + identity (see below).
6. Return `(SegmentMap, VocabularyRef, MapVersion)`.

Provide `write_segment_map(store, segment_map, vocabulary, provenance)` (or fold into derive) that calls
`SegmentMapStore.write(segment_map, vocabulary, provenance)` (COLD/historical path; `prior_map=None`).

CLI `scripts/derive_segment_maps.py`: batch 2023 quali weekends (calendar from `src.utils.constants`
`get_calendar(2023)` / `F1_CALENDARS`), idempotent, writing to a segment-map store db
(e.g. `data/segment_maps.db`, configurable `--db-path`). Skip weekends whose telemetry/grip data is
unavailable with a logged reason (do not crash the batch).

## Protected Intent
`layout_content_hash` must fingerprint TRACK GEOMETRY ONLY. Two weekends of the SAME track with
DIFFERENTLY-DRAWN sector lines MUST hash identically — so the sector-forced split boundaries are STRIPPED
before hashing (per `identity.py::layout_content_hash`'s explicit contract). The persisted `SegmentMap`
still carries the full nested boundaries (with sector splits); only the HASH input is geometry-only.

## Test Mode
TDD-lean. Unit tests on a small SYNTHETIC assembled map (construct arrays directly) for the round-trip +
the hash invariant (deterministic). A real 2023-weekend end-to-end smoke guarded on store availability
(needs the telemetry store + grip_bin_obs; skip cleanly if absent).

## Close Criteria (MUST TEST)
1. **Store round-trip:** `SegmentMap.build(...)` → `SegmentMapStore.write(...)` →
   `store.get_by_version(mv)` (and `get_current(gp, year, weekend)`) reproduces the map: geometry arrays
   byte-identical, severity membership reproduced, class_ids preserved.
2. **Geometry-only layout hash (LOAD-BEARING):** two derivations with the SAME geometry cut points but
   DIFFERENT sector-line placements produce the SAME `layout_content_hash`. Prove the sector-forced split
   distances are removed from the hash input (feed the base-tiling geometry boundaries, i.e. the FINAL
   boundaries with the derived sector-line distances removed — those two removed distances are the only
   difference from the persisted boundaries).
3. **SegmentMap.build invariants pass** (non-corner membership exactly 0.0, corner radius>0, boundaries
   monotone 0→lap_length) — these come from G1–G4 but the assembly must not corrupt them.
4. **Identity fields:** `vocabulary_version == VocabularyRef.vocabulary_id`; `map_version="v1"`;
   `MapVersion.status="historical"`; `layout_id` set to a stable structural id (use the geometry-only
   `layout_content_hash` as the layout_id, or a documented gp-derived id — state your choice);
   `config_fingerprint` from `identity.config_fingerprint(<build config>)`; `built_at` ISO-8601 UTC.

## Allowed Scope
`derive.py`, `scripts/derive_segment_maps.py`, `test_derive.py`. Read (not edit): all G1–G4 derivation
modules, `segment_map/runtime.py` (SegmentMap.build), `segment_map/store.py` (SegmentMapStore.write),
`segment_map/identity.py` (MapVersion/VocabularyRef/layout_content_hash/config_fingerprint),
`segment_map/from_mixture.py`, `src/utils/constants.py` (calendar).

## Specific Exclusions
- Do NOT compute the gating checks / verdict (g6). Do NOT populate sub-phase marks or persist adjacency
  (adjacency is computed on demand by the runtime's mod-arithmetic — never persisted).
- Do NOT edit docs/architecture/*, existing segment_map runtime/store/identity files, or frozen_constants.py.
- Do NOT use the seeded/supersede write path (`prior_map` — Build 3 #664); COLD path only.

## Constraints
- layout_content_hash: geometry cut points ONLY (strip the 2 sector-line distances before hashing).
- COLD/historical write path only (status="historical").
- DB-only: telemetry via store-first (G1); grip_bin_obs via G4's fitter (note: grip_bin_obs lives in the
  main-checkout `damage_integrals.db` — G4's `fit_era_severity_mixture` already locates it; reuse it,
  don't re-derive the path).
- Segment-map store db path is a derived store under `data/` (gitignored) — it will NOT appear in the PR.

## Map Anchors (inbound)
- **Structural:** derive.py (NEW), scripts/derive_segment_maps.py (NEW); runtime.SegmentMap.build;
  store.SegmentMapStore.write; identity.{MapVersion,VocabularyRef,layout_content_hash,config_fingerprint}.
- **Decision anchors:**
  - decision:derivation-subpackage-placement @grade: settled/measured · leans g5
  - decision:dormant-subphase — adjacency computed on demand, never persisted. @grade: settled/human · leans g5
- **Evidence expectations:** claim: store round-trip reproduces the map; layout_content_hash excludes
  sector-forced splits.

## Deliverable Path Check
- **Committed:** `derive.py`, `scripts/derive_segment_maps.py`, `test_derive.py` — `git check-ignore`
  exits 1. The `data/segment_maps.db` store is gitignored (local-only) — state this; it is NOT in the diff.

## Required Evidence
- pytest `test_derive.py` green incl. the round-trip + geometry-only-hash tests (LOAD-BEARING).
- `simplification_limits --paths src/physics/segment_map/derivation/derive.py` clean (also the CLI if
  it carries logic; keep the CLI thin).
- In IMPLEMENTER_RESULT: the layout_id choice, the weekend key, and a real 2023-weekend derive result
  (n_segments, sector counts, corner count) if the store is present.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_derive.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/derive.py scripts/derive_segment_maps.py
```

## Suggested Model Tier
Stronger — the geometry-only hash strip + the full compose are the subtle bits.

## Authority
Cold-path-only, geometry-only-hash, dormant-subphase are DECIDED. You MAY decide the layout_id source,
weekend key, store db path default, and CLI shape (state them).

## Stop Conditions
Stop and return if: the compose needs to edit a G1–G4 module or a runtime file; the round-trip can't
reproduce the map; the geometry-only hash can't be made sector-independent.

## Return Format
IMPLEMENTER_RESULT to `.agent-work/662-segment-map/g5-impl-result.md`: slice, files, test mode, evidence
(pytest incl. round-trip + hash tests + simplification), layout_id/weekend-key choices, real-weekend
derive result if store present, assumptions, stop conditions, out-of-scope, workflow feedback.
**Deliver a concise summary (verdict + result path + the real-weekend derive result) to "cmdr-662" via
SendMessage before ending your turn.**
