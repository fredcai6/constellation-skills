# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` -- instrument panel over the FULL 2023 corpus (#670 season-scale run)

## Completed slice
Built `scripts/run_season_panel_670.py` -- a bounded read-adapter extension of the landed
`scripts/instrument_panel_668_report.py` that runs all 4 instruments over the G2-consolidated
2023-Q season slice (20 covered circuits, per-circuit driver sets), generalizing ONLY the
cross-circuit split scheme for instruments 2+3. Emits `season_panel_670_report.md` + `.json` to
the isolated `.agent-work/670-season-run/artifacts/` directory (never `docs/physics/*`).

## Scope
**Files changed:**
- `scripts/run_season_panel_670.py` (new)
- `tests/unit/physics/instrument_panel/test_panel_corpus.py` (new)

**Specific exclusions touched:** no -- `src/physics/instrument_panel/*`, `frozen_constants.py`,
and the committed #668 report/script were never edited; the tracked `data/f1_data_2023.db` was
never opened; no FastF1/online call was made.

## Behavior changed
Yes (new capability): a new script now produces a season-scale instrument panel report. No
existing behavior changed -- the #668 script, its committed report, and `src/physics/instrument_panel/*`
are byte-unmodified (confirmed by the unchanged 57-test #668-era suite still passing).

## The EXACT split scheme (K + construction) -- Admiral-ruled shape, implementer-chosen construction

**ROTATING-BLOCK (circle-method) deterministic, seed-free, balanced split-half scheme**, implemented
as `enumerate_rotating_half_partitions(circuits)`:

1. Sort the covered circuits into a fixed canonical order `c_0..c_{n-1}` (alphabetical --
   deterministic, independent of round order, which has parked-round gaps this season).
2. For `k = 0 .. (n/2 - 1)`: `half_a(k)` = the `n/2` circuits at CONTIGUOUS positions
   `[k, k+1, ..., k+n/2-1]` (mod `n`, wrapping around the sorted list); `half_b(k)` = the
   complementary `n/2` circuits.
3. This yields exactly **K = n/2 DISTINCT balanced partitions** -- rotating the window by `n/2`
   reproduces the same unordered partition with the two halves swapped, which is why `k` only
   needs to range over `n/2` values.

On the real 2023-Q corpus, `n = 20` covered circuits -> **K = 10** distinct, deterministic,
balanced 10-vs-10 partitions (confirmed in the real run: `k_partitions: 10`, 10 partitions listed).
No `random`/seed anywhere in the construction (verified structurally in
`test_split_scheme_source_uses_no_random_or_seed`).

r is averaged over the K partitions per (class, channel), then the **SAME registered decision
rule** the #668 script defines -- `decide_channel_from_mean_r` (imported unchanged, itself built
from the imported `r_floor` + `channel_tie_margin`) -- is re-applied to the averaged r. This is
the direct N-circuit generalization of the #668 4-circuit "exhaustive 2v2, averaged over the 3
distinct partitions" scheme, replacing infeasible full enumeration (C(20,10)/2 ~= 92378) with a
fixed deterministic rotating subsample. Every other frozen rule (`out_of_sample_coverage`,
`frozen_replication_thresholds`, `grand_two_way_center`, `main_effect_margin_uncertainty`,
`widen_sigma_for_margin_uncertainty`, `compare_channels_by_class`) is imported byte-unchanged from
`src/physics/instrument_panel/replication.py` (via the #668 script or directly) -- none is
re-minted.

## Map Impact

- **Structural anchors touched:** `scripts/run_season_panel_670.py::enumerate_rotating_half_partitions`
  (NEW -- the N-circuit generalization of `scripts/instrument_panel_668_report.py::enumerate_2v2_partitions`,
  4-circuit-only), `::run_season_panel` (NEW -- the corpus-scale counterpart of `instrument_panel_668_report.py::run_panel`,
  reusing `instrument1_variance_decomposition`/`instrument4_whole_lap_calibration`/`decide_channel_from_mean_r`
  unchanged via import).
- **Capabilities added/changed/affected:** cross-circuit replication now runs meaningfully over
  the full 20-circuit 2023-Q corpus (previously bounded to the #668 4-circuit slice) -- the
  deliverable's premise, confirmed via the real run.
- **Constraints/assumptions touched:** `decision:panel-corpus-split-scheme` (Admiral-ruled shape)
  -- honored: deterministic, seed-free, balanced, K>1 fixed partitions, frozen rules unchanged.
  The rotating-block construction and K=n/2 are the implementer's chosen instantiation of that
  ruled shape.
- **Claims/evidence produced:** real run over the actual corpus (see below) -- reproduce-identical
  confirmed both on synthetic fixtures and the real slice.
- **Trust limitations / drift found:** none found; #668's committed report/script/tests are
  unmodified and still pass.
- **Triage candidates:** the season-level replication verdict is mostly `unresolved`/`unmeasurable`
  per class on the real corpus (see real-run summary below) -- a small-signal outcome consistent
  with #668's own small-signal framing, not a defect in this adapter; any further investigation of
  *why* (e.g. whether double-centering removes too much signal at season scale) is out of this
  bounded read-adapter's scope and is left for the G5 season report/Admiral to route if desired.

## Test mode
**Required:** `test-after` (a read-adapter/wiring layer over four already-TDD'd pure instrument
modules, mirroring the #668 script's own test mode -- not new pure-algorithm behavior).
**Satisfied:** yes -- `tests/unit/physics/instrument_panel/test_panel_corpus.py` written alongside
the implementation and run to green before advancing each plan gate.

## Evidence

```bash
cd "C:/Programs/f1brainz-wt/epic659-670" && "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel/test_panel_corpus.py -q
```
**Result:** `10 passed in 1.75s`

```bash
cd "C:/Programs/f1brainz-wt/epic659-670" && "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel -q
```
**Result:** `67 passed in 11.78s` (57 pre-existing #668-era tests + 10 new; zero regressions)

```bash
cd "C:/Programs/f1brainz-wt/epic659-670" && "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/run_season_panel_670.py
```
**Result:** pass -- wrote `.agent-work/670-season-run/artifacts/season_panel_670_report.md` and
`.json`. **Real-run summary (all 4 instruments, real 2023-Q corpus)**:

- **Slice identity:** 20 covered circuits (Abu Dhabi, Australia, Austria, Azerbaijan, Belgium,
  Brazil, Canada, Great Britain, Hungary, Italy, Japan, Las Vegas, Mexico, Miami, Monaco,
  Netherlands, Qatar, Singapore, Spain, United States) -- Bahrain (`__error__`-only) and Saudi
  Arabia (absent from the slice) correctly excluded. Matches `season_results.json`'s covered set
  exactly (20/20).
- **Split scheme:** rotating-block, K=10 distinct balanced 10-vs-10 partitions (stated in the
  report).
- **Instrument 1** (variance decomposition): utilization channel n=1524, car_reference_share=0.6926,
  driver_utilization_share (FLOOR)=0.0000, residual_share=0.3074; energy channel n=1524,
  car_reference_share=0.8197, driver_utilization_share (FLOOR)=0.0000, residual_share=0.1803.
- **Instruments 2+3** (rotating-block split-half replication + per-class channel comparison,
  averaged over K=10 partitions): severity:c0 -> unresolved (mean_r util=0.278, energy=-0.099,
  r_floor=0.500); severity:c1 -> unmeasurable; severity:c2 -> unresolved (mean_r util=0.145,
  energy=-0.084); severity:c3 -> unresolved (mean_r util=0.290, energy=-0.199). Sigma-honesty:
  nominal=0.9, empirical=1.0000 (2604/2604 out-of-sample checks), no thin classes.
- **Instrument 4** (composed-sector scorecard + whole-lap calibration): (a) position-sum
  construction check PASS; (c) whole-lap calibration over 381 driver x circuit comparisons,
  observed coverage 0.9948 (379/381) vs nominal 0.9, diagnostic meets_observed_min (>=0.85) True,
  GATE grossly_miscalibrated (<0.5) False.

```bash
cd "C:/Programs/f1brainz-wt/epic659-670" && "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/run_season_panel_670.py --check-reproduce
```
**Result:** `REPRODUCE CHECK: PASS -- two runs produced identical output` (real slice, all 4
instruments).

```bash
cd "C:/Programs/f1brainz-wt/epic659-670" && "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright scripts/run_season_panel_670.py tests/unit/physics/instrument_panel/test_panel_corpus.py
```
**Result:** `0 errors, 0 warnings, 0 informations`

**No-reimplementation confirmation:** grepped `scripts/run_season_panel_670.py` for a local `def`
of `r_floor`/`compare_channels_by_class`/`grand_two_way_center`/`main_effect_margin_uncertainty`/
`widen_sigma_for_margin_uncertainty`/`out_of_sample_coverage`/`frozen_replication_thresholds`/
`decide_channel_from_mean_r` -- **zero matches** (all 8 names enter the script only via `from
scripts.instrument_panel_668_report import (...)` or `from src.physics.instrument_panel.replication
import (...)`; no local reassignment of `r_floor =` / `channel_tie_margin =` either).

## TDD evidence, if required
Test-after mode (see Test mode above) -- N/A.

## Docs/contracts touched
- none -- `docs/architecture/*` untouched per the handoff's constraint; the season panel report is
  local-only under `.agent-work/670-season-run/artifacts/`, not a committed doc.

## Assumptions
- The canonical circuit order for the rotating-block scheme is alphabetical (not round order),
  because round order has parked-round gaps this season (Bahrain/Saudi Arabia) that would make a
  round-order-based construction ambiguous/fragile; alphabetical order is fully deterministic and
  requires no extra input.
- Instrument 4's per-circuit driver set is derived from `driver_class_observables` rows actually
  present for that circuit (via `drivers_per_circuit`), not a fixed 4-driver list, per the
  handoff's "grid varies per round" instruction.
- The season_results.json intersection (`intersect_with_covered_season_results`) is a
  belt-and-suspenders check on top of the severity-row filter; on the real corpus both filters
  agreed exactly (20/20), so this assumption was never load-bearing on the actual data, only a
  documented defensive guard.

## Stop conditions hit
None. No frozen decision rule needed changing; no missing table/column blocked a deliverable; no
edit to `src/physics/instrument_panel/*` or a frozen set was required.

## Out-of-scope observations
- The per-class replication verdict is mostly `unresolved`/`unmeasurable` at season scale (only
  `severity:c1` is fully unmeasurable; the other 3 classes are `unresolved`, i.e. no channel
  clears `r_floor` after double-centering). This is a legitimate, honestly-reported small-signal
  result (same framing #668 used at 4-circuit scale) -- not a defect in this read-adapter. Whether
  this reflects a genuine null at season scale or motivates a future refinement is a question for
  the G5 season report / Admiral, out of this bounded gate's scope.

## Workflow Feedback

- **Handoff gaps:** none material. One small ambiguity: the handoff's "e.g. circuits sorted by
  round, then a fixed deterministic construction of K balanced partitions" suggested round order
  as an example, but round order has parked-round gaps (Bahrain=round 1, Saudi Arabia=round 2,
  both excluded) that make "sorted by round" ambiguous once parked rounds are dropped from the
  numbering. I used alphabetical order instead (still fully deterministic, and the handoff's "e.g."
  explicitly left the exact construction to the implementer) -- documented in both the script
  docstring and this result.
- **Context rediscovered:** the synthetic f1-db test fixture initially hand-rolled a
  `CREATE TABLE sessions/lap_times` schema, which failed against `DatabaseManager`'s real schema
  (missing `round_num` and other columns `_apply_schema_upgrades` expects). Rebuilt via
  `DatabaseManager.insert_session`/`insert_lap_times` (the project's own DB seam) instead --
  this is the correct pattern per `TESTING.md`/`CREW_CONTEXT.md` doctrine ("the SQLite database is
  the canonical seam") but wasn't explicitly called out in the handoff for a *test fixture* (as
  opposed to production code); worth noting in a future handoff that touches DB fixtures.
- **Instructions improvised around:** none -- the handoff's Allowed Scope (import freely from the
  #668 script + `src/physics/instrument_panel/*`, no edits to either) matched the actual
  implementation need exactly; some private module-level helper functions in the #668 script
  (`build_half_cells`, `half_cell_sem`, `_metric_field`) are duplicated here rather than imported,
  because the #668 script doesn't export them as public API and re-deriving the split-half cell
  AGGREGATION arithmetic (not a decision rule) is explicitly the kind of "small read-adapter"
  reuse the handoff's docstring anticipates -- flagged here for visibility, not as a rule
  violation (the actual DECISION rule, `decide_channel_from_mean_r`, is imported, never
  reimplemented).
- **What would have made this easier:** exporting the #668 script's private split-half
  cell-aggregation helpers (`build_half_cells`, `half_cell_sem`, `_resolved_grid`) as public API
  (or moving them into `src/physics/instrument_panel/replication.py` as pure, injectable
  utilities) would let a corpus-scale adapter import rather than duplicate them -- a candidate for
  a future doctrine tweak on the #668 module boundary, not urgent for this gate.

## Return status
`complete`
