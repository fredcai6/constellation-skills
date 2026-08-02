# Implementer Handoff — G2 Canonical gate + base tiling

## Gate
g2 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Task
Turn a G1 `ReferenceLap` into a **complete contiguous tiling** of the lap into typed segments. New files:
- `src/physics/segment_map/derivation/tiling.py`
- `tests/unit/physics/segment_map/derivation/test_tiling.py`

Provide `tile_reference_lap(ref: ReferenceLap) -> <tiling result>` returning, at minimum:
`boundaries_m` (float64, strictly increasing, `boundaries_m[0]==0.0`, `boundaries_m[-1]==ref.lap_length_m`)
and `seg_type_code` (int8, one per segment, values in {0 STRAIGHT, 1 BRAKING_ZONE, 2 CORNER}). Use the
`SegType` IntEnum from `src.physics.segment_map.runtime` for the codes — do NOT redefine them. The tiling
is a strict partition: contiguous, no gaps, no overlaps, covering [0, lap_length].

## Protected Intent
This gate DEFINES the physical typing of the whole lap. A silent mis-typing poisons every downstream
consumer. Two correctness invariants dominate: (a) the tiling is a genuine complete partition; (b) the
braking-zone onset is the field ENVELOPE (early) onset, NEVER a central tendency.

## Test Mode
TDD-lean. Write `test_tiling.py` first on synthetic ReferenceLaps (construct ReferenceLap instances
directly with hand-built distance_m/curvature/v_ref/brake_active_frac arrays — deterministic).

## Close Criteria
1. **Corner gate (curvature):** a grid point is CORNER where `abs(ref.curvature) >
   CORNER_CURVATURE_THRESHOLD`. IMPORT `CORNER_CURVATURE_THRESHOLD` from
   `src.physics.layer2.frozen_constants` — NEVER write the literal 0.005. (This is the owner-ratified
   `decision:corner-gate-is-curvature`: the gate is CURVATURE, not lateral-g.)
2. **Braking zone (ENVELOPE onset, p10 — the subtle-correctness heart of this gate):** each corner is
   entered from a braking zone. Define the braking zone for a corner as the interval
   `[onset, corner_entry)` where `onset` is the most-upstream distance (moving toward the corner) at which
   the pooled brake-active fraction `ref.brake_active_frac` FIRST reaches `BRAKING_ONSET_QUANTILE`
   (IMPORT from frozen_constants; = 0.10). Rationale: `brake_active_frac(s)` = fraction of the field
   braking at distance s; approaching a corner it rises 0→~1. The crossing of 0.10 = where the earliest
   ~10% of the field has begun braking = the p10 (robust LOW / EARLY) onset of the field's per-lap onset
   distribution. This is the ENVELOPE. A MEAN/median onset would be the 0.5 crossing, which sits INSIDE
   the real braking zone (misses the early brakers) — that is exactly the failure the frozen quantile
   forbids. Do NOT use mean/median of onset. If `brake_active_frac` never reaches 0.10 before a corner,
   that corner simply has no braking-zone segment (straight → corner directly).
3. **Straight = remainder:** every grid point not CORNER and not in a braking zone is STRAIGHT.
4. **Group** contiguous same-type grid points into segments; emit `boundaries_m` + `seg_type_code`.
5. **Completeness (construction check, MUST TEST):** `boundaries_m` strictly increasing, starts 0.0,
   ends lap_length_m, `np.diff > 0` everywhere; `len(seg_type_code) == len(boundaries_m) - 1`; the union
   of segments is exactly [0, lap_length] with no gap/overlap.
6. **Envelope-not-mean (MUST TEST):** build a synthetic corner where the field's brake onset is
   bimodal/skewed so the p10-envelope onset is DEMONSTRABLY EARLIER (smaller distance) than the
   0.5-crossing (mean/median) onset; assert the produced braking-zone onset equals the p10 crossing, and
   is strictly upstream of the 0.5 crossing.

## Allowed Scope
`src/physics/segment_map/derivation/tiling.py`; `tests/unit/physics/segment_map/derivation/test_tiling.py`.
Read (not edit): `src/physics/segment_map/derivation/reference_lap.py` (ReferenceLap contract),
`src/physics/segment_map/runtime.py` (SegType), `src/physics/layer2/frozen_constants.py`.

## Specific Exclusions
- Do NOT do sector nesting (g3), corner descriptors/severity (g4), assembly/store (g5).
- Do NOT edit `docs/architecture/*`, any existing `src/physics/segment_map/*.py` runtime file, or
  `frozen_constants.py`. Do NOT retune CORNER_CURVATURE_THRESHOLD (it is carried not-independently-proven;
  g6 scrutinizes it — if you suspect it's wrong, STOP and note it, never edit).

## Constraints
- **frozen-constants:** import CORNER_CURVATURE_THRESHOLD + BRAKING_ONSET_QUANTILE; NEVER a literal
  0.005/0.10 at the call site.
- ReferenceLap fields you consume (name them explicitly): `distance_m`, `curvature` (1/m, signed),
  `v_ref` (m/s), `brake_active_frac` (fraction in [0,1] per grid point), `lap_length_m`. Confirm the
  exact field names by reading reference_lap.py.
- Closed-loop: the lap wraps; handle a corner/braking region straddling start/finish sensibly (the map
  is a closed loop; boundaries still run 0→lap_length). If wrap handling is non-trivial, keep it simple
  and note the choice.

## Map Anchors (inbound)
- **Structural:** `segment_map/derivation/tiling.py` (NEW); `frozen_constants.py`
  CORNER_CURVATURE_THRESHOLD/BRAKING_ONSET_QUANTILE; `runtime.py` SegType.
- **Decision anchors:**
  - decision:corner-gate-is-curvature — gate is curvature > threshold, NOT lateral-g.
    @grade: settled/inherited (merged #660) · leans g2
  - decision:braking-envelope-p10-not-mean — onset = field envelope at p10, never central tendency.
    @grade: settled/human (launch order, frozen const) · leans g2
- **Evidence expectations:** claim:tiling-complete (partition); the p10 envelope onset is EARLIER than
  the field mean onset.
- **Map confidence flags:** CORNER_CURVATURE_THRESHOLD carried not-independently-proven — do NOT retune.

## Deliverable Path Check
- **Committed:** `tiling.py`, `test_tiling.py` — `git check-ignore` exits 1 (not ignored). New files in
  `git status` until staged.

## Required Evidence
- pytest `test_tiling.py` green on the pinned interpreter, INCLUDING the completeness test and the
  envelope-not-mean test (LOAD-BEARING — these two prove the gate).
- `simplification_limits --paths src/physics/segment_map/derivation/tiling.py` clean.
- In IMPLEMENTER_RESULT: confirm the exact imported constant names + that no literal threshold appears
  (paste a grep: `grep -nE "0\\.005|0\\.10|0\\.1[^0-9]" tiling.py` should show only imports/comments).

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_tiling.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/tiling.py
```

## Suggested Model Tier
Stronger — the envelope-not-mean braking onset is the subtle correctness hazard.

## Authority
Corner-gate-is-curvature, braking-envelope-p10, and the frozen thresholds are DECIDED — do not relitigate.
You MAY decide the tiling result's dataclass shape, wrap handling, and grouping details (note them).

## Stop Conditions
Stop and return if: the ENVELOPE onset cannot be computed from the ReferenceLap's exposed fields (e.g.
brake_active_frac missing), a frozen threshold looks wrong, or completeness cannot be guaranteed.

## Return Format
IMPLEMENTER_RESULT to `.agent-work/662-segment-map/g2-impl-result.md`: slice, files, test mode, evidence
(pasted pytest incl. the two load-bearing tests + simplification_limits + the grep), the ReferenceLap
fields consumed, wrap-handling choice, assumptions, stop conditions, out-of-scope observations, workflow
feedback. **Deliver a concise summary to "cmdr-662" via SendMessage before ending your turn.**
