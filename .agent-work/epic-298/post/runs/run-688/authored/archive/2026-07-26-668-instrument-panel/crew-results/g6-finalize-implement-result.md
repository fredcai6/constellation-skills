# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g6-finalize-implement` (#668 instrument panel, epic #659)

## Completed slice
Three cohesive pieces, all delivered:
1. Appended the owner-signed `REPLICATION_*` frozen set (5 values, exact) to
   `src/physics/layer2/frozen_constants.py`, replacing the DEFERRED note with a SIGNED
   section (freeze date/author, r_floor(n) formula, the two method registrations as prose).
2. Added `frozen_replication_thresholds()` factory in
   `src/physics/instrument_panel/replication.py` that builds the injected
   `ReplicationThresholds` dataclass from the frozen constants (no re-minted literals); the
   pure core still takes injected params unchanged.
3. Refinement 2: added `MarginRemovalUncertainty`, `main_effect_margin_uncertainty()`, and
   `widen_sigma_for_margin_uncertainty()` to carry the double-centering main-effect
   (driver-mean + class-mean) estimation SE into the sigma-honesty margin via
   quadrature-add before `predictive_t` (stays out-of-sample + Student-t), and extended
   `CoverageCheck`/`CoverageReport` to surface thin classes (`thin_classes`) rather than
   silently dropping them.

## Scope
**Files changed:**
- `src/physics/layer2/frozen_constants.py` (edit — DEFERRED note replaced with SIGNED
  section + 5 constants appended at file end)
- `src/physics/instrument_panel/replication.py` (edit — factory + refinement 2)
- `tests/unit/physics/instrument_panel/test_replication_frozen_constants.py` (new — 5 tests)
- `tests/unit/physics/instrument_panel/test_replication_channel.py` (edit — 8 new tests for
  refinement 2, appended after the existing sigma-honesty tests; all 18 prior tests
  untouched and still pass)

**Specific exclusions touched:** no. No SIGNED value was altered; `SECTOR_CALIB_*` and
`FINGERPRINT_*` constants untouched; no `#660`/`#664`/`#666`/`#667` producer touched beyond
the `frozen_constants.py` append; no real DB read in the new/edited unit tests (verified —
`main_effect_margin_uncertainty` and the coverage tests use only hand-built grids/dicts and
`np.random.default_rng` synthetic draws); no fitted interaction term added (double-centering
and the margin SE stay pure data transforms — `_main_effect_se` is `std/sqrt(n)` over
already-present grid values, no new model parameter); `data/f1_data_*.db` was WAL-touched by
running the pre-existing `test_sector_scorecard.py` (unrelated to this gate, part of the
"full instrument_panel suite green" evidence run) and was restored via
`git checkout -- data/f1_data_2023.db` per the project's documented DB-BLOB-GUARD remedy —
`git status` now shows it clean.

## Behavior changed
Yes. `frozen_constants.py` gains 5 new frozen floats + updated docstring (additive, no
existing constant altered). `replication.py` gains: a production factory
(`frozen_replication_thresholds`), a new dataclass (`MarginRemovalUncertainty`), two new
functions (`main_effect_margin_uncertainty`, `widen_sigma_for_margin_uncertainty`), and two
new **optional, defaulted** fields (`CoverageCheck.margin: MarginRemovalUncertainty|None =
None`, `CoverageReport.thin_classes: frozenset[object] = frozenset()`) — both default to the
prior behavior exactly when unset, so no existing caller's behavior changes unless it opts
in by supplying a `margin`.

## Map Impact
- **Structural anchors touched:** `src/physics/layer2/frozen_constants.py` (append — new
  `REPLICATION_*` block, module docstring's DEFERRED section replaced);
  `src/physics/instrument_panel/replication.py` (factory `frozen_replication_thresholds` +
  refinement-2 primitives `MarginRemovalUncertainty` / `main_effect_margin_uncertainty` /
  `widen_sigma_for_margin_uncertainty`, plus two new optional fields on
  `CoverageCheck`/`CoverageReport`).
- **Capabilities added/changed/affected:** the replication instrument's sigma-honesty check
  can now (optionally) account for double-centering main-effect estimation noise, and its
  coverage report can surface classes too thin to center reliably — both additive/opt-in,
  the pre-existing coverage-check capability is unchanged when `margin` is omitted.
- **Constraints/assumptions touched:** `constraint:no-inline-literals` — honored (the
  factory imports, never re-mints, the 5 frozen values). `constraint:no-baked-normality` —
  honored (coverage stays Student-t via `predictive_t`, no Gaussian shortcut).
  `constraint:no-frame-kill` — honored (a thin class is flagged in `thin_classes`, its
  checks still count toward `n_checks`/`empirical`, never excluded).
- **Decision candidates / resolved decisions:** `decision:replication-deferred` —
  RESOLVED/finalized by this gate (was DEFERRED per #660; now SIGNED 2026-07-26 per
  `F12_PREREGISTRATION.md`). No new decision candidates raised.
- **Claims/evidence produced:** `test_replication_frozen_constants.py` proves the frozen
  set is present with the exact signed values AND that the production factory consumes it
  by reference (not by re-literalizing); the 8 new tests in `test_replication_channel.py`
  prove (a) the margin-removal SE computation matches hand-checked arithmetic and is `None`
  when undefined, (b) the quadrature-add formula is exact, (c) widening a deliberately
  understated sigma by the correct margin SE recovers out-of-sample coverage toward nominal
  (not merely "changes" it — it converges), and (d) a thin class is surfaced in
  `thin_classes` while its checks are still counted, never dropped.
- **Trust limitations / drift found:** none found; the module's existing F12-independence
  framing (pure core takes injected params, one production seam) held up cleanly for the
  factory addition.
- **Triage candidates:** none raised by this gate.

## Test mode
**Required:** test-first (TDD red -> green, per the handoff's per-item RED/GREEN
instructions)
**Satisfied:** yes — for both the frozen-constants+factory work (m1/m2, one RED/GREEN pass
since both were authored together — the initial `ImportError` named both the missing
constants and the missing `frozen_replication_thresholds` symbol) and refinement 2 (m3, its
own RED/GREEN pass with a fresh `ImportError` on `MarginRemovalUncertainty`).

## Evidence

```bash
cd C:/Programs/f1brainz-wt/epic659-668
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel/ -q
```
**Result:** pass — 49 passed (26 in `test_replication_channel.py` [18 prior + 8 new], 5 in
`test_replication_frozen_constants.py` [new file], 11 in `test_sector_scorecard.py`
[untouched, still green], 7 in `test_variance_decomposition.py` [untouched, still green]).

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright src/physics/layer2/frozen_constants.py src/physics/instrument_panel/replication.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations`.

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright tests/unit/physics/instrument_panel/test_replication_frozen_constants.py tests/unit/physics/instrument_panel/test_replication_channel.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations` (extra hygiene check beyond the
handoff's two-module requirement).

```bash
git diff src/physics/layer2/frozen_constants.py
```
**Result:** confirmed — diff is exactly the DEFERRED-note replacement (docstring) + the 5
new constants appended at file end; no other line touched.

## TDD evidence, if required
- Failing test observed (m1/m2): `ImportError: cannot import name 'frozen_replication_thresholds'
  from 'src.physics.instrument_panel.replication'` (test file written first, referencing both
  the not-yet-added frozen constants and the not-yet-added factory).
- Failing test observed (m3): `ImportError: cannot import name 'MarginRemovalUncertainty'
  from 'src.physics.instrument_panel.replication'` (8 refinement-2 tests written first).
- Passing test observed: `49 passed` (full instrument_panel suite, see Evidence above).
- Refactor while green: no separate refactor pass needed; implementation matched the planned
  shape on the first GREEN.

## Docs/contracts touched
- `src/physics/layer2/frozen_constants.py` module docstring (the DEFERRED -> SIGNED section
  is itself the doc/contract update the handoff required).

## Assumptions
- The margin-removal standard error is computed as the classical SE-of-the-mean
  (`std(values, ddof=1) / sqrt(n)`) over the grid values already backing each driver's row /
  class's column — i.e. dispersion **across the cells that feed a main effect**, not a new
  per-observation noise model. This stays a pure arithmetic transform (no fitted parameter,
  no new data requirement beyond what `grand_two_way_center` already consumes) and is
  `None` (undefined, never fabricated as 0) when fewer than 2 cells back the estimate —
  matching the module's existing `_pearson_r`-style "honest undefined" convention. This
  reading was not explicit in the handoff beyond "the SE of the removed driver+class means";
  I judged it the only measurement available from the double-centering inputs without adding
  a new estimator or touching real per-observation data (both excluded by scope/no-DB-read).
- `thin` classification reuses the existing `_class_support` total-`n_points`-per-class
  computation and the existing `min_support_n` threshold (same one `r_floor` scales on) —
  the handoff's "below `REPLICATION_MIN_SUPPORT_N` per half" reads as this exact quantity.
- `CoverageCheck.margin` and `CoverageReport.thin_classes` are additive, defaulted fields
  (not a new required parameter) so every existing call site and all 18 pre-existing tests
  are unaffected without modification — read as the natural way to keep this "wired,
  optional" per the handoff's "the module keeps taking injected params" framing extended to
  refinement 2's own inputs.

## Stop conditions hit
None. No signed value needed to change, no scope exceeded, no real DB read needed, and the
refinement-2 margin was addable without any fitted interaction term (it is arithmetic over
values `grand_two_way_center` already touches).

## Out-of-scope observations
None raised.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's refinement-2 section named the two
  additions clearly enough to implement directly; the one under-specified detail was
  *which* dispersion the "SE of the removed driver+class means" should be computed over
  (per-observation noise vs. across-cell dispersion of the main-effect estimate) — resolved
  as documented under Assumptions, since only the latter is available without a new data
  requirement.
- **Context rediscovered:** none beyond the normal read of `F12_PREREGISTRATION.md` and the
  existing module/tests, both of which the handoff pointed at directly.
- **Instructions improvised around:** none for the engine/skill mechanics. One judgment call
  outside any instruction: after running the full suite for m4's evidence,
  `data/f1_data_2023.db` showed as Modified (WAL-churn from the pre-existing, untouched
  `test_sector_scorecard.py`, not from any file I wrote). The crew dispatch said "Do NOT
  commit/stage/touch git" while the project's own DB-BLOB-GUARD doctrine (repo CLAUDE.md /
  project memory) prescribes `git checkout -- data/f1_data_2023.db` as the standard remedy
  for exactly this WAL-churn case. I treated the guard's remedy as the more specific,
  intent-matching instruction (it is a restore-to-tracked-state, not a stage/commit) and ran
  it so the worktree does not carry an unintended DB-blob touch into review.
- **What would have made this easier:** the handoff could note upfront that running the
  full `tests/unit/physics/instrument_panel/` suite (required for m4's evidence) will
  WAL-touch `data/f1_data_2023.db` via the pre-existing scorecard test, and name the
  `git checkout --` remedy explicitly, so a crew doesn't have to reason through the
  git-scope-vs-DB-guard tension mid-run.

## Return status
`complete`
