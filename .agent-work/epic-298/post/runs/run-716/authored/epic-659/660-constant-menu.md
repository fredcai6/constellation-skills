# #660 Frozen Constant Set — proposal menu for owner ratification

**F12 discipline:** these are pre-registered BEFORE any real-data run. Values are chosen from physical
reasoning + the #638/F12 precedent + the ephemeris pilot, **never fit to data**. Changing a value later
requires a NEW named constant set + full re-derivation. Owner (Fred) ratifies; then a small implementer
builds the named constant module (mirroring `mixture_stability.py`'s `LOG_RADIUS_SCALE` etc.), wires every
consumer to import it (no literals at call sites), and adds the no-duplicate-copy test.

Precedent already in-repo (`src/physics/layer2/mixture_stability.py`): `LOG_RADIUS_SCALE=0.30`,
`LATERAL_G_SCALE=0.5`, `F12_AGREEMENT_THRESHOLD=1.0`.

Legend: **[physical]** = clean physical/precedent call, recommend-and-freeze. **[statistical]** = a
design-of-experiment choice deserving your deliberate attention; structure proposed, exact value your call.

| # | Constant | Candidate range | **Recommended freeze** | Rationale / tradeoff |
|---|---|---|---|---|
| 1 | `BRAKING_ONSET_QUANTILE` [physical] | p5–p10 | **p10** | Low quantile of field brake-onset (never mean). p5 captures the earliest-braker frontier but is outlier-sensitive; p10 is more robust while still an early-onset marker. Pick p5 if you want the harder frontier. |
| 2 | `CORNER_LATERAL_G_GATE` [physical] | 0.8–1.5 g | **1.0 g** | On the field reference lap (v_ref²×curvature): ≥ gate ⇒ corner, below ⇒ straight/kink. 1.0 g cleanly separates genuine corners from straight-line wander; lower risks typing kinks as corners, higher drops the slowest corners. |
| 3 | `MIN_SEGMENT_LENGTH_M` [physical] | 3–10 m | **5 m** | Sliver-merge floor: segments shorter than this merge into a neighbor (sector cuts EXEMPT — split-not-snap preserved). 5 m ≈ below any real track feature at F1 scale; a numerical sliver, not a segment. |
| 4 | `MAP_STABILITY_DRIFT_M` [physical] | 5–15 m | **10 m** | Cross-weekend stability gate: same-circuit weekends must produce boundaries within this median drift. The fixed-per-weekend map should be far tighter than the 10–16% per-driver lap instability xP1 found; 10 m is a loose-but-real construction/stability bound. |
| 5 | `REPLICATION_MIN_SUPPORT_N` [statistical] | 10–20 | **15** | Minimum samples/cell for a fingerprint cell to be *scored* for split-half replication at all. 15 mirrors the compound-damage screening finding (n≥15 stabilizes per-bin estimates; below it, thin-bin artifacts dominate). Cells below this are `unresolved`, not failures. |
| 6 | `REPLICATION_THRESHOLD` + scaling formula [statistical] | see note | **structure below; exact floor = your call** | The load-bearing DIAGNOSTIC. Proposed structure: score split-half agreement of per-class cells AFTER removing overall skill (golf-corrected form — raw replication flatters). A cell "replicates" if its split-half correlation r ≥ `r_floor(n)`, where `r_floor(n)` is a support-scaled noise floor (thin cells are expected to replicate less). Proposed default: **r_floor(n) = 0.3·√(15/n)** capped at [0.15, 0.5], scored only for n≥15 (constant #5); doubles as the σ-honesty check (cells must replicate within stated σ). I recommend you either ratify this form or let me commission a focused 1-page pre-registration proposal from the #668 (instrument-panel) commander that you sign before its run — either way it's frozen before real data. |
| 7 | `SECTOR_CALIB_COVERAGE_NOMINAL` / `_MIN` + `_GROSS_MISCALIB_BOUND` [statistical] | see note | **90% nominal, ≥85% observed (DIAGNOSTIC); <50% observed = GATING fail** | Composed-sector distribution calibration vs official FIA sector times. For a nominal 90% predicted interval, observed coverage ≥85% passes the DIAGNOSTIC sizing check; observed coverage <50% for that interval trips the GATING gross-miscalibration bound (a mechanically broken calibration). Adjust the nominal/observed pair to taste. |

**Two things to decide with #6/#7 specifically** (they're statistical-design, not physical):
- **#6 replication floor:** ratify `r_floor(n)=0.3·√(15/n)` now, OR have me commission a 1-page pre-registration from the panel commander for your signature before that run. Both keep F12 discipline; the second gives you a more grounded formula at the cost of one extra sign-off.
- **#7 coverage pair:** the 90%/85%/50% triple is a reasonable default; if you have a stronger prior on how tight sector-time calibration should be, name it.

**Note on k=4:** these are frozen against the current #638 k=4 corner-class vocabulary. A future k change (issue #642) is, by this issue's own discipline, a NEW named constant set — not a silent edit.

---

## RATIFIED SET — Fred, 2026-07-25 (freeze v1)

The named constant module (`src/physics/<segment>/frozen_constants.py` or similar, implementer's call —
mirror `mixture_stability.py`'s style) ships with EXACTLY these, each with a one-line rationale + the freeze
date/author. Discipline docstring: changing any value requires a NEW named constant set + full
re-derivation/re-run, never a silent edit. A test asserts no consumer defines its own copy of a frozen
threshold (no literals at call sites).

| Name | Value | Unit | Rationale (goes in the module) |
|---|---|---|---|
| `CORNER_CURVATURE_THRESHOLD` | `0.005` | 1/m (radius ≤ 200 m ⇒ corner) | **Option A.** Inherited from #625's pre-existing `straight_curvature_threshold` — **NOT independently proven** as the corner/straight gate (#638 validated only the severity vocabulary's stability). Carried pending the map typing spot-checks + cross-weekend stability gate that first scrutinize it; if flagged, routes to structural work (no-kill), never a silent retune. |
| `BRAKING_ONSET_QUANTILE` | `0.10` (p10) | quantile of field brake-onset | Robust low quantile, never mean. p5 = harder frontier / outlier-sensitive; p10 more robust early-onset marker. |
| `MIN_SEGMENT_LENGTH_M` | `5.0` | m | Sliver-merge floor; sector cuts EXEMPT (split-not-snap). Below any real F1 track feature. |
| `MAP_STABILITY_DRIFT_M` | `10.0` | m | Cross-weekend boundary-drift stability gate (same-circuit weekends). Loose-but-real construction/stability bound; the fixed map should be far tighter than xP1's 10–16% per-driver lap instability. |
| `SECTOR_CALIB_COVERAGE_NOMINAL` | `0.90` | fraction | Nominal predicted sector-time interval. Tunable via new named set + re-run. |
| `SECTOR_CALIB_COVERAGE_OBSERVED_MIN` | `0.85` | fraction | DIAGNOSTIC sizing pass: observed coverage ≥ this for the nominal interval. |
| `SECTOR_CALIB_GROSS_MISCALIB_BOUND` | `0.50` | fraction | GATING: observed coverage below this for the nominal interval = mechanically broken calibration, blocks. |

**Unit discipline (closes #639 trap):** every lateral/accel-adjacent value is defined in explicit SI with
the g-conversion documented (`GRAVITY_MS2` exists). The corner gate here is curvature (1/m), so the
lateral-g unit ambiguity does not bite the gate — but the module docstring notes the descriptor path uses
`a_lateral` in m/s².

**DEFERRED (not in freeze v1, added to the SAME module before #668 runs — still pre-run/F12-clean):**
- `REPLICATION_*` (split-half replication floor + support-count-scaling formula + `REPLICATION_MIN_SUPPORT_N`).
  Per Fred: base it in data — the #668 (instrument-panel) commander produces a 1-page pre-registration
  proposal (grounded in the actual 2023 driver×class support distribution + a noise model) for Fred's
  signature BEFORE the panel's real-data run.

_Ratified by Fred 2026-07-25. #660 module build now dispatched (implementer); clears Wave 1 (#662)._

