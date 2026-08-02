# Reviewer Handoff — G5 Assembly + persistence + derivation entrypoint

## Gate
g5 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## What was implemented
`src/physics/segment_map/derivation/derive.py` (`weekend_key`, `assemble_segment_map`,
`derive_segment_map`, `write_segment_map`), `scripts/derive_segment_maps.py` (batch CLI), tests
`tests/unit/physics/segment_map/derivation/test_derive.py` (7). Result:
`.agent-work/662-segment-map/g5-impl-result.md`. Real Bahrain 2023 Q: 36 segments, 13 corners,
sector lines [1748.9, 3920.1]m.

## How to inspect
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_derive.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/derive.py scripts/derive_segment_maps.py
```
Read `derive.py`, `segment_map/runtime.py` (SegmentMap.build), `store.py` (write cold path),
`identity.py` (layout_content_hash contract).

## Reviewer FOCUS (verify each)
1. **Geometry-only layout hash (#1):** `layout_content_hash` input is GEOMETRY cut points only — the
   sector-forced split distances are excluded (the implementer captures the G2 base-tiling boundaries
   BEFORE nesting). Verify the load-bearing test proves two derivations with same geometry + different
   sector lines hash IDENTICALLY. Confirm the persisted SegmentMap still carries the FULL nested
   boundaries (hash-only strip, not a map strip).
2. **Store round-trip:** build → write (COLD, status="historical") → get_by_version/get_current
   reproduces geometry + membership + class_ids. Verify the round-trip test.
3. **SegmentMap.build invariants** hold on the assembled map (non-corner membership 0.0, corner radius>0,
   monotone boundaries) — assembly didn't corrupt G1–G4 outputs.
4. **Identity:** vocabulary_version == VocabularyRef.vocabulary_id; map_version globally-unique (the
   implementer keyed it `{year}-{gp}-{session}:v1` because the store PK is global — verify this is
   correct, not a spec deviation that breaks anything); status="historical"; config_fingerprint set;
   layout_id documented.
5. **Cold path only** (no prior_map/supersede). Sub-phase NOT populated; adjacency NOT persisted.
6. **No scope breach:** no edit to docs/architecture/*, existing segment_map runtime/store/identity
   files, frozen_constants.py. CLI is thin.
7. **Sanity:** the real Bahrain result (13 corners, 36 segments) is plausible (g6 does the rigorous
   typing check; here just confirm nothing absurd).

## Close Criteria (verdict basis)
Tests green (7/7) incl. round-trip + geometry-only-hash; simplification clean; hash is sector-independent;
round-trip reproduces; cold-path; identity fields correct.

## Constraints / Map Anchors
DB-only / pinned interpreter. Inherits decision:dormant-subphase, decision:derivation-subpackage-placement.

## Required Evidence
Re-run both commands; confirm the geometry-only-hash test proves sector-independence and the round-trip
reproduces the map.

## Return Format
REVIEW_RESULT to `.agent-work/662-segment-map/g5-review-result.md`: verdict APPROVE/BLOCK, findings
(severity + file:line), evidence reproduced, workflow feedback. **Deliver a concise summary (verdict +
result path) to "cmdr-662" via SendMessage before ending your turn.**
