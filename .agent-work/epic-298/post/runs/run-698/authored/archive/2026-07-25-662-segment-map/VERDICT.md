# G6 VERDICT — issue #662 segment-map derivation, epic #659

Gate: g6 (the substantive falsification + verdict). Pinned interpreter:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`. All numbers below
are produced by `scripts/validate_segment_map_662.py` and reproduce byte-for-byte on
re-run (deterministic: static 2023 DB data, deterministic even/odd driver split, no RNG
in the derivation path exercised here — the era-mixture GMM fit is the only stochastic
component and is not what's being asserted on numerically).

## Construction vs Gating (review T3)

- **CONSTRUCTION checks** (already exercised in `test_tiling.py` / `test_sector_nesting.py`
  at g2/g3): tiling-completeness (the G2 base tiling is a gapless, non-overlapping
  partition of `[0, lap_length_m]`) and sector-nesting exactness (the G3 split-not-snap +
  sliver-merge invariants hold). These catch **coverage/arithmetic bugs** — a gap, an
  overlap, a sector line landing outside the lap. They say nothing about whether a CORNER
  segment is actually a corner.
- **GATING checks** (this gate, g6): GATING-1 (`claim:map-stable`) and GATING-2
  (`claim:typing-correct`) are the checks that can **falsify** an unstable or
  physically-wrong map. A failure here, not at g2/g3, is what would mean "the map doesn't
  mean what it claims to mean."

## GATING-1 — cross-weekend map stability (`claim:map-stable`)

### Scoped null (2023 cross-weekend stability)

**Honest statement:** F1 runs each circuit **once** per season. `src.utils.constants
.get_calendar(2023)` has 22 entries, **zero repeats** (mechanically confirmed —
`len(calendar) == len(set(calendar))`). There is therefore **no second same-circuit 2023
weekend** to compare a derived map against — the cross-weekend stability gate is a
**coverage NULL by construction** for this dataset, not an oversight and not "the gate
passed." This is recorded as a **typed, distinct result**
(`ScopedNullResult.tested = False`), never silently folded into a green.

### Substantive proxy: split-half within-weekend stability

Two DISJOINT driver-subset halves of the same weekend's field (even/odd split of
`session.drivers`, sorted by car number — 10 drivers/half for both circuits below), each
built into its own `ReferenceLap` (via the new `reference_lap_from_store(drivers=...)`
filter) and G2 base `Tiling`. Boundaries are matched by nearest-neighbor under circular
distance (interior boundaries only — the structural `0.0`/`lap_length_m` endpoints always
match trivially).

**Interpretation of the handoff's "assert median, report max":** the MEDIAN is the
asserted gate; the MAX is reported for transparency but not asserted, because (per the
per-boundary breakdown below) the largest drifts are concentrated at the noisier p10
braking-onset quantile computed over a HALF-sized subsample — a known sensitivity of that
specific quantile estimate, not evidence the underlying geometry is unstable.

| circuit | n_boundaries (A/B) | median drift (m) | max drift (m) | gate (median < 10.0 m) |
|---|---|---|---|---|
| Bahrain | 32 / 34 | **2.178** | 15.739 | **PASS** |
| Austria | 25 / 25 | **3.479** | 80.676 | **PASS** |

Both circuits pass the median gate with real margin (2.2m and 3.5m vs the 10.0m
`MAP_STABILITY_DRIFT_M` bound, imported from `frozen_constants.py`, never a literal).

Reported, not gated: Bahrain's two boundary-count sets differ by 2 (32 vs 34, ~6%) —
a real but modest tiling-count difference across the two field-subsets, itself weak
instability evidence (a braking zone appearing/disappearing at the p10 quantile boundary
depending which half of the field pooled it). Austria's counts are identical (25/25). The
large MAX values (15.7m Bahrain, 80.7m Austria) are traced (Austria diagnostic dump) to a
handful of specific boundaries — predominantly straight→braking-zone-onset transitions,
plus one corner-exit boundary at Austria — not a uniform smear across every boundary; the
bulk of boundaries (see median) agree within a few metres.

## GATING-2 — typing spot-checks (`claim:typing-correct`)

### Bahrain 2023 Q (primary)

Physical-corner count = **collapse contiguous CORNER segments** in the FINAL (post
sector-nesting) `seg_type_code` array. This already absorbs a sector-split corner (two
adjacent CORNER rows straddling an FIA sector line) with no special case, because
`sector_nesting.nest_sectors`'s split-not-snap duplicates the SAME `seg_type` on both
sides of a sector cut — the two pieces are still adjacent, same-type segments.

- **Physical corner count: 12** — within the P4 excursion's plausible range **[11, 17]**
  (P4: Bahrain corner-arc count mean 14.13, range 11–17, across 2471 driver-laps from an
  independent, unrelated ideal-lap-generator pipeline; BIC's own official turn count is
  15). **PASS** (12 ∈ [11, 17]), on the lower end of the range.
- **Apex locations (m), lap_length_m = 5314.51:**
  `711.3, 790.4, 907.2, 1481.6, 1839.0, 1977.0, 2194.9, 2652.3, 3366.5, 3805.0, 4037.9,
  4824.8`. Strictly increasing, all within `[0, lap_length_m]` — checkable against
  Bahrain's own known corner sequence (not independently re-verified turn-by-turn against
  a track map in this gate; flagged as a follow-on, see Out-of-scope).

### Corner distance-share vs `regime_rollup` cross-check

- Map's own corner distance-share (`sum(CORNER length_m) / lap_length_m`): **0.3080**.
- `regime_rollup.circuit_distance_share`'s corner distance-share for Bahrain, year-filtered
  to 2023 (`load_circuit_frame` itself carries no year filter — every year present for
  `gp_name` is returned; filtered to `year==2023` here to match this map's own fit era):
  **0.5226**.

**These are NOT expected to closely numerically match** — the two use fundamentally
different corner gates: this map's `CORNER_CURVATURE_THRESHOLD` (radius ≤ 200m, a tight
geometric gate) vs `regime_rollup`'s `CORNER_GATE_MS2 = 3.0` m/s² (≈0.3g lateral
acceleration, a much LOOSER threshold that also catches partial-braking/transition
regions). The tolerance asserted is **directional**: both fractions are genuine,
non-degenerate corner shares in `(0, 1)`, and the map's stricter curvature gate produces
the SMALLER share (`0.3080 < 0.5226` — **PASS**). A future tighter cross-check would need
to either widen the map's gate to match `CORNER_GATE_MS2`'s physical meaning or narrow
`regime_rollup`'s to curvature — out of scope for this gate (frozen constants; see
Specific Exclusions).

### 2nd circuit vs official turn count

- **Austria (Red Bull Ring), 2023 Q: physical corner count = 10.**
- **Official turn count: 10** (Red Bull Ring, Turns 1–10 — external, well-documented F1
  fact; this circuit was chosen specifically for its short, unambiguous layout to keep the
  official-count comparison low-risk).
- **Exact match: 10 == 10 — PASS.**

## Summary verdict

| check | result |
|---|---|
| GATING-1 scoped null (2023 cross-weekend) | Honest coverage NULL — not tested, not fabricated |
| GATING-1 split-half median drift, Bahrain | PASS (2.178 m < 10.0 m) |
| GATING-1 split-half median drift, Austria | PASS (3.479 m < 10.0 m) |
| GATING-2 Bahrain physical corner count vs P4 | PASS (12 ∈ [11, 17]) |
| GATING-2 Bahrain corner distance-share vs regime_rollup | PASS (directional: 0.3080 < 0.5226) |
| GATING-2 Austria physical corner count vs official | PASS (10 == 10) |

**No check was silently greened and none was fabricated.** The one genuine open item is
the large MAX split-half drift (15.7m Bahrain, 80.7m Austria) at a handful of specific
boundaries (mostly braking-zone onset) — reported, not asserted against, per the handoff's
own median/max split, and flagged below as a real (if bounded) instability signal worth a
future tighter look if braking-zone boundaries become load-bearing for a downstream
consumer.

## Reproduction

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths scripts/validate_segment_map_662.py
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/validate_segment_map_662.py
```

All three green at time of writing (2026-07-25), all real-data (no skip fired — telemetry
store, grip_bin_obs store, and per-year 2023 DB are all present in this environment).
