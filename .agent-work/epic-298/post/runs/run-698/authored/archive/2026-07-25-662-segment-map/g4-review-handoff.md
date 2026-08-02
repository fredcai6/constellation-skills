# Reviewer Handoff — G4 Corner descriptors + turn direction + severity membership

## Gate
g4 (issue #662) — the HIGHEST-RISK gate (#639 a_lateral unit boundary). Pinned interpreter:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## What was implemented
`src/physics/segment_map/derivation/corner_attributes.py` — `compute_corner_descriptor`,
`compute_turn_direction`, `compute_severity_membership`, `fit_era_severity_mixture`,
`derive_corner_attributes`. Tests `tests/unit/physics/segment_map/derivation/test_corner_attributes.py`
(14). Result: `.agent-work/662-segment-map/g4-impl-result.md`.

## How to inspect
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_corner_attributes.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/corner_attributes.py
```
Read `corner_attributes.py`, `segment_classifier.py::soft_class_membership` (the convention it must
mirror), `layer2/corner_descriptors.py`, `layer2/property_mixture.py`, `segment_map/from_mixture.py`,
`physics/constants.py` (GRAVITY_MS2).

## Reviewer FOCUS (verify each)
1. **THE UNIT BOUNDARY (#1 check):** `a_lateral` (m/s²) → g via `GRAVITY_MS2` at EXACTLY ONE call site —
   no second/absent conversion, correct constant, imported (no literal 9.81, re-run grep). Verify the
   known-value/monkeypatch test genuinely proves single conversion (double would give 1/4, missing would
   leave unchanged, when GRAVITY_MS2 is scaled 2×). Confirm it mirrors `soft_class_membership`'s
   convention (radius=1/|κ|, lateral_g=a_lateral/GRAVITY_MS2).
2. **Descriptor on the mixture's axis:** radius = 1/|κ| (== grip_bin_obs v²/a_lat in steady state);
   lateral_g from a_lateral_ms2 = v_ref²·|κ| at the corner APEX (max |κ|). The median-vs-p90 lateral_g
   offset is DOCUMENTED inline as a bounded, deferred secondary-axis approximation (NOT silently ignored,
   NOT switched to a p90-capability descriptor).
3. **Membership invariants:** non-corner rows EXACTLY 0.0; corner rows sum to ~1.0; shape (n, k). SOFT,
   no hard argmax. k=4 consumed as-is; Student-t refit + fresh F12 DEFERRED and STATED.
4. **Mixture pool scope:** fit on POOLED grip_bin_obs across the era (all 2023), NOT the single weekend —
   so vocabulary_version is stable across weekends. Confirm the pool scope and the fail-closed behavior
   on missing/empty store.
5. **corner_descriptor validity:** finite + radius>0 on CORNER rows (SegmentMap.build will validate).
6. **turn_direction:** int8 from SIGN of curvature; non-corner = 0; documented convention.
7. **Sub-phase NOT populated.** No scope breach (no edit to docs/architecture/*, runtime/layer2 files,
   frozen_constants.py).

## Close Criteria (verdict basis)
Tests green (14/14) incl. the two load-bearing tests (unit boundary + membership invariants);
simplification clean; unit boundary fires exactly once; descriptor on the mixture axis with the offset
documented; pooled-era fit; non-corner membership 0.0.

## Constraints / Map Anchors
DB-only / pinned interpreter. Inherits decision:a-lateral-g-boundary (@grade settled/human #639),
decision:severity-refit-consume-k4 (@grade settled/human), decision:dormant-subphase.

## Required Evidence
Re-run both commands + the no-9.81 grep; quote the monkeypatch/known-value assertion proving single
conversion, and confirm non-corner membership is exactly 0.0.

## Return Format
REVIEW_RESULT to `.agent-work/662-segment-map/g4-review-result.md`: verdict APPROVE/BLOCK, findings
(severity + file:line), evidence reproduced, workflow feedback. **Deliver a concise summary (verdict +
result path) to "cmdr-662" via SendMessage before ending your turn.**
