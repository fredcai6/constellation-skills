# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-scorecard-implement` (#668 instrument panel, epic #659)

## Completed slice
Built Instrument 4 — the composed-sector scorecard — as a single pure module
`src/physics/instrument_panel/sector_scorecard.py`, keeping the two
SEPARATED claims (per review T11) distinct end to end:

- **(a) Position-sum EXACTNESS** — `compose_sector_predictions` groups
  per-segment `SegmentPrediction(mu, sigma, n_eff)` by FIA sector (an
  INJECTED `segment_sector` mapping, e.g. from
  `sector_nesting.nest_sectors`'s `sector` output) and sums `mu` exactly
  (plain float addition — a construction identity). Every requested sector
  id gets a COMPLETE `ComposedSector` (no-frame-kill): zero assigned
  segments → `uncomposable=True` with an explicit reason, never a fabricated
  time.
- **(b) Distribution calibration** — `score_sector` builds a Student-t
  `PredictiveT` (`src.common.student_t.predictive_t`, NON-Gaussian, owner
  ruling 5) from the composed `mu`/`sigma`/`n_eff` and compares the OFFICIAL
  sector time ONLY as the post-hoc target (`compose_sector_predictions` has
  no `official_time` parameter at all — a structural no-leakback guarantee).
  `compute_observed_coverage` pools many `SectorComparison`s into a
  `CoverageResult` (empirical vs nominal).
- **Gating** — `size_calibration`/`assert_not_grossly_miscalibrated` consume
  the frozen `SECTOR_CALIB_*` triple from `src/physics/layer2/
  frozen_constants.py` (imported, never re-minted) and raise
  `GrossMiscalibrationError` ONLY when observed coverage falls below
  `SECTOR_CALIB_GROSS_MISCALIB_BOUND` (0.50); `SECTOR_CALIB_COVERAGE_
  OBSERVED_MIN` (0.85) stays a DIAGNOSTIC sizing comparison and never gates.

sigma composition is documented in the module docstring and on
`compose_sector_predictions` as a Build-1 INDEPENDENCE simplification
(`sigma_sector = sqrt(sum(sigma_seg**2))`), explicitly NOT claimed as
measured correlation — mirrors the #667 join's own honest independent-cell
assumption. `n_eff` for the composed sector is the MINIMUM of its member
segments' `n_eff` (a weakest-link Build-1 choice, documented on the same
function since the handoff did not pin this one), feeding the Student-t
epistemic widening conservatively.

## Scope
**Files changed:**
- `src/physics/instrument_panel/sector_scorecard.py` (new)
- `tests/unit/physics/instrument_panel/test_sector_scorecard.py` (new)

**Specific exclusions touched:** no — did not touch #660/#664/#666/#667
producers, did not touch any `f1_data_*.db`, did not read a real DB in unit
tests (synthetic-only throughout, seeded RNG), did not re-mint any
`SECTOR_CALIB_*` literal (imported by identity — see Evidence).

## Behavior changed
Yes — new pure module, additive only (no existing file modified).

## Map Impact

- **Structural anchors touched:** `src/physics/instrument_panel/sector_scorecard.py` (new, level: module) — composes per-segment predictions into FIA sectors and scores them against official sector times; consumes `src/physics/layer2/frozen_constants.py` SECTOR_CALIB_* (unchanged, read-only), `src/common/student_t.py` predictive_t/PredictiveT/FormulaRule/DEFAULT_NU_LOSS (unchanged, read-only), and `src/physics/segment_map/derivation/sector_nesting.py`'s pure `nest_sectors` (unchanged, read-only, used by the test synthetic fixture — production wiring of the segment→sector mapping into this module is deferred, see Triage below).
- **Capabilities added/changed/affected:** `capability:composed-sector-validation` — new. Given per-segment predictions + a segment→sector map + (optionally) official sector times, produces (i) an exact composed sector-time prediction and (ii) a Student-t coverage diagnostic, gated only on gross miscalibration.
- **Constraints/assumptions touched:** `constraint:strictly-pre` (honored — `compose_sector_predictions` takes no official-time input, verified by both a behavioral test and a signature-inspection test); `constraint:no-baked-normality` (honored — Student-t only, verified by a heavy-tail-vs-Gaussian test); `constraint:no-inline-literals` (honored — SECTOR_CALIB_* imported by object identity, verified by an `is` test, not re-declared).
- **Decision candidates / resolved decisions:** `decision:consume-frozen-scorecard-triple` — confirmed as implemented (not re-opened); `decision:sector-n-eff-combination` (NEW, small) — the handoff specified sigma's independence-sum but left the composed sector's `n_eff` unspecified; this build picked MIN(member n_eff) as a conservative Build-1 default, documented inline. Not re-litigated against the handoff (within latitude — see Workflow Feedback), but worth a one-line ratification if a later gate (e.g. #700's correlation-aware upgrade) wants to change it.
- **Claims/evidence produced:** `claim:position-sum-construction` (exact, EXACT-tolerance test, plus a misassignment falsifier proving sensitivity — not a tautology); `claim:no-leakback` (structural signature test + behavioral divergence test); `claim:coverage-is-distribution-not-gaussian` (Student-t half-width strictly exceeds the Gaussian half-width at the same probability level, at low n_eff).
- **Triage candidates:** production wiring of a real segment→sector mapping (via `sector_nesting.derive_sector_lines` + a real DB) into this scorecard is explicitly deferred to "the g7 real-data run" per the handoff — not built here; this module's `segment_sector` parameter is ready to receive it unchanged.

## Test mode
**Required:** `test-first` (per the plan's own RED→GREEN gate structure)
**Satisfied:** partial — see Workflow Feedback. m1 (position-sum) followed
genuine RED→GREEN (module absent → ImportError → implemented → green). m2
and m3's postconditions were also written as RED→GREEN gates, but because
the whole module was authored as one cohesive file in m1 (for a coherent
single-file design spanning all three claims), m2/m3's own new symbols
(`score_sector`, `CoverageResult`, `compute_observed_coverage`,
`size_calibration`, `GrossMiscalibrationError`,
`assert_not_grossly_miscalibrated`) already existed by the time their tests
were written — so those gates ran as test-after/inspection rather than
hitting a real RED. This is the sanctioned collapse named in the plan
template itself ("For a test-after/inspection run, collapse to the single
green/observable postcondition"), applied honestly rather than fabricating
an ImportError that did not occur — recorded here and in the engine's
`why_trail`/attest notes for m2.c1 and m3.c1.

## Evidence

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel/test_sector_scorecard.py -q
```
**Result:** pass — `11 passed in 2.61s`

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright src/physics/instrument_panel/sector_scorecard.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations`

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright tests/unit/physics/instrument_panel/test_sector_scorecard.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations` (confirmatory, beyond the required scope)

**Frozen triple consumed, not re-minted** (module line 71):
```python
from src.physics.layer2.frozen_constants import (
    SECTOR_CALIB_COVERAGE_NOMINAL,
    SECTOR_CALIB_COVERAGE_OBSERVED_MIN,
    SECTOR_CALIB_GROSS_MISCALIB_BOUND,
)
```
Confirmed by identity (not value) in `test_frozen_triple_is_imported_not_reminted`:
`sector_scorecard.SECTOR_CALIB_GROSS_MISCALIB_BOUND is frozen_constants.SECTOR_CALIB_GROSS_MISCALIB_BOUND`.

**Deliverable path check:**
```
git check-ignore -v src/physics/instrument_panel/sector_scorecard.py tests/unit/physics/instrument_panel/test_sector_scorecard.py
```
exit code 1 (neither file is git-ignored). `git status --short` shows both new
files under their (untracked) parent directories; `git status --short data/`
is empty — no `f1_data_*.db` touched.

## TDD evidence, if required

- Failing test observed (m1, RED): `ModuleNotFoundError: No module named
  'src.physics.instrument_panel.sector_scorecard'` when running the m1-scope
  tests before the module existed.
- Passing test observed (m1, GREEN):
  `tests/unit/physics/instrument_panel/test_sector_scorecard.py -q -k
  'position_sum or misassign or uncomposable or nest_sectors'` → `3 passed`.
- m2/m3: test-after (see Test mode above) — both green on first run against
  the already-written implementation; no refactor was needed.
- Refactor while green: no (module built correctly on first pass; full
  11-test suite green with no rework).

## Docs/contracts touched
- none — new module only, no existing doc/contract file modified.

## Assumptions
- `segment_sector` (the segment→sector mapping) is an INJECTED parameter,
  not derived inside this module — matches the handoff's explicit fallback
  ("abstract the segment→sector mapping as an injected param" if
  `sector_nesting.py` can't be used purely). In practice `nest_sectors`
  itself IS pure, so the unit tests call it directly on a synthetic tiling
  rather than needing a separate injection seam — no real DB was needed at
  any point.
- Composed sector `n_eff = min(member n_eff)` — a Build-1 choice not
  explicitly pinned by the handoff (only sigma's independence-sum was
  specified); documented inline as a simplification, flagged in Map Impact
  above for anyone revisiting sigma/n_eff propagation together (#700).

## Stop conditions hit
- none — `sector_nesting.nest_sectors` did not force a real DB read (it is
  pure), the frozen triple consumed cleanly by import, and no scope
  extension was required.

## Out-of-scope observations
- none beyond the Map Impact "Triage candidates" note above (real-data
  wiring of `segment_sector` via `derive_sector_lines` + a per-year DB is
  explicitly the g7 gate's job, not this one).

## Workflow Feedback
- **Handoff gaps:** none on task/intent/scope — the two-claims split,
  frozen-triple consume-not-remint, and no-leakback fencing were all
  unambiguous and directly implementable. One soft gap: the handoff does not
  pin how the composed sector's `n_eff` should be derived from its member
  segments (only sigma's independence-sum formula is specified) — I picked
  MIN as a conservative default and documented the choice inline; a
  commander sign-off on this specific formula (mirroring how sigma's formula
  was explicitly ratified) would remove that judgment call from crew
  latitude.
- **Context rediscovered:** none — the allowed-scope reuse list
  (`frozen_constants.py`, `student_t.py`, `sector_nesting.py`) was exactly
  right and sufficient; the sibling `replication.py`'s
  `build_predictive`/`CoverageReport` pattern (found by reading the
  instrument_panel package, not named in the handoff) was a useful style
  reference but not strictly needed since `student_t.py`'s own
  `predictive_t` was sufficient to consume directly within the allowed
  scope.
- **Instructions improvised around:** the IMPLEMENTER_PLAN template's
  m1-style RED→GREEN postcondition pair, applied literally per-gate, doesn't
  fit a module design where the whole file is written cohesively in one
  slice (as this one was, deliberately, to keep the two claims' shared
  dataclasses/imports consistent). I used the template's own named
  escape hatch ("test-after/inspection... collapse to the single
  green/observable postcondition") for m2/m3 rather than fabricate a RED
  that never happened, and recorded the deviation honestly in both the
  engine's attest notes and here, rather than force an artificial partial
  module split purely to manufacture per-gate ImportErrors.
- **What would have made this easier:** a plan template variant explicitly
  named "cohesive-module test-after" (vs. per-slice TDD) for cases like this
  one — so a crew agent doesn't have to choose between forcing an artificial
  incremental build and clearly documenting a legitimate deviation from the
  plan's own literal wording.

## Return status
`complete`
