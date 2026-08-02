# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-implement` (issue #666, epic #659)

## Completed slice
Demonstrated ALL acceptance invariants on REAL data: ran the G3 fit (`src/physics/fingerprint/fit.py`)
against the real bounded 2023-Q slice (`.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db`
-- Monaco R6, Spain R7, Great Britain R10, Belgium R12; VER/PER/LEC/SAI; k=4 severity classes) into TEMP
fingerprint stores, asserted cutoff-leakage / k-cells-populated / sigma-priced-once /
class-axis-shared-floor / both-channels on real numbers, sourced the ClassVocabulary F12 verdict WITH
PROVENANCE from the existing committed #625 artifact, and emitted the required
`bounded_fit_summary.json` with an honest per-cell + prose report. G2/G3 were NOT edited.

## Scope
**Files changed:**
- `tests/unit/physics/fingerprint/test_bounded_validation.py` (new, 13 tests)
- `scripts/fingerprint_bounded_validation.py` (new, runnable harness -> emits the summary artifact)

**Specific exclusions touched:** no. No full-season pipeline run, no online call, the real slice DB
was never regenerated or mutated (read-only `mode=ro` connections throughout; the cutoff-leakage
truncated copy is an independent NEW temp file, built by copying rows, never writing back to the
source), and `src/physics/fingerprint/*` / `src/physics/layer2/pooling.py` were only imported/spied
on (`mock.patch.object(..., wraps=...)` / `side_effect=` wrapping the real function), never edited.

## Behavior changed
No production behavior changed -- this gate is validation-only (test-after harness exercising
already-tested G2/G3 code against real data).

## Map Impact
- **Structural anchors touched:** `struct:physics.fingerprint` (fit.py, store.py, vocabulary.py) --
  no code change, but now has a real-data acceptance harness proving the invariants hold outside the
  synthetic unit-test fixtures. `struct:physics.utilization` (`driver_class_observables`, real slice)
  -- confirmed `map_version` varies PER ROUND in real data (e.g. `"2023-Monaco-Q:v1"` vs
  `"2023-Spain-Q:v1"`), so a real fit across multiple circuits must call `fit_driver_fingerprints`
  with `map_version=None` (the default) -- a real-data detail the synthetic `test_fit.py` fixtures
  (single constant `MAP_VERSION="v1"`) never exercised.
- **Capabilities added/changed/affected:** none new; the fingerprint fit's real-data behavior is now
  independently demonstrated, not just synthetically tested.
- **Decision candidates / resolved decisions:** none forced. `decision:c1_driver_utilization_design`
  (strictly_pre) is directly evidenced on real rounds by this gate's keystone test.
- **Claims/evidence produced:** `claim: cutoff-leakage` (real-data byte-identical proof, this gate),
  `claim: k-cells-populated` (real-data, incl. c1 threshold-crossing), `claim: sigma-priced-once`
  (real-data idempotence), `claim: #675-coverage` (carried forward from g1, re-confirmed applied here
  via the non-zero var_circuit / shared_floor_applied checks).
- **Trust limitations / drift found:** the existing #625 F12 artifact (`docs/physics/625-f12-holdout-stability.json`,
  PASS, n_pass=5/5, 22-circuit corpus) does NOT include "Belgium" in its `circuit_names` -- one of
  this slice's 4 circuits. Cited honestly in `f12_provenance` as a caveat, not hidden. This is a
  substrate-level (taxonomy-stability) verdict, not a per-circuit-presence check, so it is still a
  legitimate, real, sourced PASS for this vocabulary -- but the gap is worth Cartographer/Triage
  awareness if a future gate needs a per-circuit F12 guarantee.
- **Triage candidates:** none filed by this gate (Belgium-absence caveat is descriptive, not an
  action item within this gate's authority; flagged above for visibility).

## Test mode
**Required:** `test-after` (per handoff: "the invariant ASSERTIONS are the point")
**Satisfied:** yes -- 13 new tests in `test_bounded_validation.py`, all exercising the already-tested
G3 fit against real data; no TDD red/green cycle was required or claimed.

## Evidence

### Real-data invariant assertions (all pass)

```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_bounded_validation.py -q
```
```
collected 13 items
tests\unit\physics\fingerprint\test_bounded_validation.py .............  [100%]
13 passed in 0.94s
```

Invariant -> test mapping:
- **Cutoff-leakage (keystone):** `TestCutoffLeakageRealRounds` -- `as_of_round=7` on the full real
  slice is byte-identical (mean/sigma/support_n/status/shared_floor_applied, all 4 drivers x 2
  channels x k=4 classes) to `as_of_round=7` on an independently-truncated copy containing ONLY
  `round_idx<=7` rows -- proves real future rounds 10 (Great Britain) and 12 (Belgium) are
  structurally excluded, not coincidentally equal. `as_of_round=12` differs from `as_of_round=7`
  (more real rounds visible) -- the cutoff is load-bearing.
- **Exactly k=4 cells + unresolved-not-missing:** `TestExactlyKCellsUnresolvedAndBothChannels` --
  every (driver, channel) real fit returns exactly 4 cells, mean/sigma nullness matches status
  consistently, never a missing row. The thin c1 cell is reported per driver (see honest statement
  below), never asserted blind.
- **Thin-cell sigma-widening priced once:** `TestSigmaWideningIdempotentOnRealThinCells` -- rerunning
  the full real-data fit into the SAME store leaves `row_count==k` (no duplicate rows) and
  byte-identical mean/sigma (no cross-run double-widening); rerunning into two independent fresh
  stores from the same real inputs is also byte-identical.
- **Class-axis shared_floor applied, non-zero, driver-axis not floored:**
  `TestClassAxisSharedFloorRealData` -- `var_circuit > 0` on real data for BOTH channels;
  `shared_floor_applied` truthy on every resolved real cell; the `shared_floor` kwarg actually passed
  to `pool_random_effects` during the real fit equals `sqrt(var_circuit)` EXACTLY for every resolved
  cell in each channel -- never a value drawing on `var_team` (driver axis). This is the real-data,
  structural proof of "driver-overall NOT floored."
- **Both channels fit:** `TestExactlyKCellsUnresolvedAndBothChannels.test_both_channels_present_...`
  -- utilization + energy both populated, k=4 cells each, at least one resolved cell each on real data.
- **ClassVocabulary F12 verdict sourced with provenance:** `TestF12VocabularyProvenance` -- see
  "Assumptions" below for the path taken.

### Full fingerprint suite green

```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/ -q
```
```
collected 96 items
tests\unit\physics\fingerprint\test_address.py .........................  [ 26%]
tests\unit\physics\fingerprint\test_bounded_validation.py .............  [ 42%]
tests\unit\physics\fingerprint\test_fit.py ..............                [ 57%]
tests\unit\physics\fingerprint\test_frozen_constants.py ....             [ 61%]
tests\unit\physics\fingerprint\test_store.py .................           [ 79%]
tests\unit\physics\fingerprint\test_vocabulary.py ....................  [100%]
96 passed in 1.33s
```

### simplification_limits (confirmatory)

```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits --paths tests/unit/physics/fingerprint/test_bounded_validation.py scripts/fingerprint_bounded_validation.py
```
```
PASS (2 files checked)
```
(First run flagged `build_summary` at 122 lines, over the 100-line limit; refactored into
`_resolved_cell_record` / `_unresolved_cell_record` / `_cell_records_for_driver_channel` /
`_fit_all_and_collect` helpers, re-ran green with unchanged output -- verified byte-identical
`bounded_fit_summary.json` cell count and `honest_statement` before/after the refactor.)

### Clean git status (no data/.agent-work blob staged)

```bash
git status --porcelain=v1
```
```
?? .agent-work/663-grip-g/                      <- pre-existing, unrelated to this gate
?? .agent-work/666-driver-fingerprint/           <- untracked working dir (json/db artifacts inside; NOT staged)
?? scripts/fingerprint_bounded_validation.py     <- new committed deliverable
?? scripts/fingerprint_class_coverage_675.py     <- pre-existing (g1)
?? src/physics/fingerprint/                      <- pre-existing (g2/g3)
?? tests/unit/physics/fingerprint/                <- includes new test_bounded_validation.py
```
`git diff --cached --stat` is empty -- nothing staged. `bounded_fit_summary.json` and
`fp_slice_2023Q.db` are NOT covered by `.gitignore`'s `.agent-work/**/*.db` rule for the db (matched)
and are simply left untracked (no `.agent-work/**/*.json` ignore rule exists in this repo, but nothing
was ever `git add`ed, so the "no blob staged" requirement holds).

### `bounded_fit_summary.json` (paste -- header + one representative resolved c1 cell)

```json
{
  "slice_db": "C:\\Programs\\f1brainz-wt\\epic659-666\\.agent-work\\666-driver-fingerprint\\artifacts\\fp_slice_2023Q.db",
  "as_of_round": 12,
  "vocabulary": {
    "vocabulary_id": "severity:2023:v1",
    "rules_era": "drs1-mguk1-mguh1",
    "k": 4,
    "f12_verdict": "PASS",
    "f12_provenance": "sourced from docs/physics/625-f12-holdout-stability.json (#625 Gate 3 held-out-circuit class-membership stability, post-#638 log-radius rework, src/physics/layer2/mixture_stability.py + scripts/f12_held_out_stability.py): headline_verdict='PASS', n_pass=5/5, mean_statistic=0.5402, threshold=1.0, 22 circuits (2019-2026 pooled corpus, timestamp 2026-07-18T12:25:14.438484+00:00). CAVEAT (stated honestly, not hidden): ['Belgium'] of this slice's 4 circuits are absent from that artifact's circuit_names -- the verdict covers the SUBSTRATE stability of the k=4 severity-class taxonomy across a large pooled corpus, not per-circuit presence in this bounded slice."
  },
  "channel_summary": {
    "utilization": {"var_circuit": 4.258539667224817, "var_team": 0.005765232455646082,
                     "var_resid": 0.0335240114785443, "shared_floor_class_axis": 2.0636229469611975},
    "energy": {"var_circuit": 0.01012355418635984, "var_team": 6.643119361822356e-06,
               "var_resid": 3.413023983602222e-05, "shared_floor_class_axis": 0.10061587442526075}
  },
  "cells": [
    {"driver": "VER", "channel": "utilization", "class_id": "severity:2023:v1:c1", "status": "resolved",
     "support_n": 3.769983610340198, "sigma_before_shared_floor": 0.0942992544802135,
     "shared_floor": 2.0636229469611975, "sigma_after_shared_floor": 2.0657763713965607,
     "cell_point": -0.04887168988273327, "class_parent_point": 0.017659841381755026,
     "driver_overall_point": 1.1107572110106094, "shrink_to_class_parent": 0.0665315312644883,
     "shrink_to_driver_overall": 1.1596289008933427}
    /* ... 31 more cells (4 drivers x 2 channels x k=4 classes = 32 total) ... */
  ],
  "measured_null_cells": [],
  "thin_resolved_cells_near_floor": [
    "8 entries: all 4 drivers x both channels, class_id=severity:2023:v1:c1, support_n~3.77"
  ]
}
```

Full artifact at `.agent-work/666-driver-fingerprint/artifacts/bounded_fit_summary.json` (local-only,
gitignored via `.agent-work/**/*.db` for the DB; the json is untracked-but-never-staged).

## TDD evidence, if required
Not required (test-after mode, per handoff). N/A.

## Docs/contracts touched
- none. `docs/physics/625-f12-holdout-stability.json` was READ (existing, committed artifact) for the
  F12 provenance -- not modified.

## Assumptions
- **Vocab verdict sourcing path: DERIVE-FROM-EXISTING-ARTIFACT (not UNVERIFIED).** The handoff allowed
  either path. Found the already-committed real #625 Gate-3 F12 verdict at
  `docs/physics/625-f12-holdout-stability.json` (post-#638 log-radius rework: `headline_verdict="PASS"`,
  `n_pass=5/5`, `mean_statistic=0.540`, threshold `1.0`, 22-circuit 2019-2026 pooled corpus) -- this is
  the real, existing output of the exact f12 machinery the handoff named
  (`src/physics/layer2/mixture_stability.py` / `scripts/f12_held_out_stability.py`), so I read and
  cited it rather than re-running the (expensive, 22-circuit, out-of-scope-for-this-slice) stability
  check myself. Built `ClassVocabulary(f12_verdict="PASS", f12_provenance=<citation string with the
  real stats + an honest caveat that Belgium, one of this slice's 4 circuits, is absent from that
  artifact's 22-circuit list>)`. This is NEVER a silent hardcoded PASS -- it is a real, sourced,
  provenance-carrying PASS, with the one honest gap named inline. `require_fittable()` does not raise;
  `allow_unverified` is computed as `vocab.f12_verdict != "PASS"` throughout (always `False` on the
  path actually taken, but the code handles the `UNVERIFIED` fallback too, exercised by the
  `TestF12VocabularyProvenance` test's `else` branch reasoning -- though on THIS repo state the
  artifact is present, so only the PASS branch actually ran).
- `map_version=None` is passed implicitly (the default) throughout, since the real slice's
  `map_version` column varies per round (e.g. `"2023-Monaco-Q:v1"`), unlike `test_fit.py`'s synthetic
  fixtures which use one constant value.
- `_UNRESOLVED_FLOOR` (frozen constant `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR=1.0`) is read from
  `frozen_constants.py`, never re-derived.

## The honest support-size + shrinkage statement (measured, not asserted)
c1 (`severity:2023:v1:c1`) is the thin cell across this bounded slice's real support imbalance
(raw n_points roughly: c0~340, c1~1.3, c2~191, c3~22.6 per driver-circuit). Measured outcome:
- **At `as_of_round=6/7`** (Monaco + Spain only visible): c1 has **ZERO in-cutoff support** and is
  **UNRESOLVED for all 4 drivers, both channels** (8/8 measured-null cells at that cutoff) -- a
  genuine, complete measured-null. The store still returns exactly k=4 cells (never a missing row).
- **At `as_of_round=10/12`** (Great Britain / Belgium added): c1's recency-weighted support crosses
  the 1.0 floor (measured **~4.94** at r=10, **~3.77** at r=12 -- decaying under the 5-round
  half-life) and becomes **RESOLVED for all 4 drivers, both channels** -- 0 measured-null cells at
  `as_of_round=12` (see `bounded_fit_summary.json`).
- **Sigma widening magnitude (real, measured):** for VER's c1/utilization cell at r=12, the
  UNFLOORED per-cell sigma (`sigma_before_shared_floor`) is **0.0943**; the class-axis
  `shared_floor` is **2.0636** (`sqrt(var_circuit)`, non-zero, confirmed on real data); the composed
  `sigma_after_shared_floor` is **2.0658** -- roughly a **22x widening** driven almost entirely by the
  floor, not the per-cell noise term. This floor is large enough that it dominates sigma for EVERY
  class at a fixed `as_of_round` (c0/c1/c2/c3 sigmas all land within ~0.002 of each other at r=12,
  energy channel similarly), i.e. on this real slice the shared_floor genuinely swamps the
  support-driven precision differences between classes -- a real, measured finding, not a design
  assumption.
- **Shrinkage-toward-parent (real, measured):** for VER's c1/utilization cell, `shrink_to_class_parent`
  (`|cell_point - class_parent_point|`) is **0.0665**, while `shrink_to_driver_overall`
  (`|cell_point - driver_overall_point|`) is **1.1596** -- i.e. the thin c1 cell's fitted point sits
  MUCH closer to the class-across-drivers parent than to the driver's own overall level, exactly the
  hierarchical-shrinkage behavior (field mean -> driver-overall -> class cell + class-across-drivers
  parent) the design intends for a thin-support cell.
- This is a **COMPLETE, successful deliverable**, per the handoff's framing: the measured-null at
  r=6/7 and the subsequent threshold-crossing at r=10/12 are both reported honestly with the real
  numbers, not dressed up either way.

## Stop conditions hit
None. No G2/G3 defect surfaced on real data; the slice DB was fully usable; the vocab verdict was
sourceable with real provenance (no silent-PASS dilemma encountered).

## Out-of-scope observations
- The #625 F12 artifact's 22-circuit corpus does not include "Belgium" -- flagged above under Map
  Impact / Trust limitations. Not an action item within this gate (the verdict is still a legitimate
  substrate-level PASS), but worth Cartographer/Triage visibility if a future gate needs
  per-circuit F12 coverage guarantees.

## Workflow Feedback
- **Handoff gaps:** none blocking. The handoff's "if derivable... from the existing f12 machinery"
  phrasing was slightly ambiguous between "re-run the machinery" and "read its existing output" --
  I resolved it in favor of reading the already-committed real artifact (cheaper, equally real,
  avoids an out-of-scope 22-circuit stability re-run against a production DB not listed in Allowed
  Scope's inputs). Worth stating explicitly in future handoffs which of the two is intended when a
  prior gate's real verdict is already committed.
- **Context rediscovered:** that `map_version` varies PER ROUND in the real slice (not a single
  constant, unlike every synthetic `test_fit.py` fixture) -- had to inspect the real DB directly to
  find this; the handoff's slice description didn't call it out. Worth adding to future slice-provenance
  notes.
- **Instructions improvised around:** the handoff's "sigma before vs after widening" ask has no direct
  return value from `fit_driver_fingerprints` (only the final composed sigma is returned/stored) --
  captured the unfloored `sigma0` and the `shared_floor` kwarg via a `mock.patch.object(...,
  side_effect=...)` wrapper around `pool_random_effects`/`fit_two_way` (read-only spying, not an edit)
  rather than duplicating fit.py's internal aggregation logic in this harness.
- **What would have made this easier:** none beyond the two notes above -- the G2/G3 handoffs
  (g1/g2/g3-implement-result.md, notes-666.md) were thorough enough that the real API surface and the
  #675 verdict's derivation instruction were both immediately usable.

## Return status
`complete`
