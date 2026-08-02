# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g6-finalize-review` (#668 instrument panel, epic #659)

## Result
`APPROVE`

## Handoff compliance
Met in full. The 5 owner-signed `REPLICATION_*` values in `src/physics/layer2/frozen_constants.py`
are byte-exact against the handoff's signature (`REPLICATION_MIN_SUPPORT_N=15.0`,
`REPLICATION_THRESHOLD=0.5`, `REPLICATION_R_FLOOR_CAP=0.7`, `REPLICATION_R_FLOOR_SUPPORT_REF=100.0`,
`REPLICATION_CHANNEL_TIE_MARGIN=0.1`). `frozen_replication_thresholds()` in
`src/physics/instrument_panel/replication.py` builds `ReplicationThresholds` purely from
`frozen_constants.REPLICATION_*` attribute reads — no re-minted literal. `r_floor()` implements
`threshold + (cap-threshold)*clip((ref-n)/ref,0,1)` exactly. Refinement 2 (`MarginRemovalUncertainty`,
`main_effect_margin_uncertainty`, `widen_sigma_for_margin_uncertainty`) quadrature-adds the SE of the
removed driver+class main effects to a cell's sigma inside `out_of_sample_coverage` **before**
`build_predictive`/`predictive_t` is called (confirmed by reading the call order); the whole coverage
path stays out-of-sample (training-half `mu`/`sigma`/`n_eff` vs. a held-out value) and Student-t. A
thin class (`class_support < min_support_n`) is unioned into `CoverageReport.thin_classes` while its
check still counts toward `n_checks`/`hits` — surfaced, never dropped. No fitted interaction term:
`grand_two_way_center` and `main_effect_margin_uncertainty` are both pure arithmetic (means,
`std/sqrt(n)`), no optimizer or new model parameter.

## Scope drift
None. `git status --porcelain` shows exactly one tracked-modified file
(`src/physics/layer2/frozen_constants.py`); `git diff` on it is exactly the DEFERRED-note-to-SIGNED
docstring replacement plus the 5-constant append at file end — no other line touched, no
`SECTOR_CALIB_*`/`FINGERPRINT_*` constant altered. `src/physics/instrument_panel/` and
`tests/unit/physics/instrument_panel/` show as untracked directories only because the whole module
tree predates any commit on this branch (confirmed against the g3-replication-implement-result, which
created `replication.py`/`test_replication_channel.py` as NEW at that gate). A file-mtime comparison
across the tree confirms only `replication.py`, `test_replication_frozen_constants.py`, and
`test_replication_channel.py` carry this gate's timestamp (~20:1x); `sector_scorecard.py`,
`variance_decomposition.py`, `__init__.py`, and their tests carry older g3/g4-era timestamps —
no producer beyond the allowed scope was touched. `data/` is clean.

## Evidence verdict
Both required commands independently reproduced (not accepted from the implement-result claim):

```
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/ -q
# 49 passed in 9.80s
```
26 in `test_replication_channel.py` (18 prior g3 tests + 8 new refinement-2 tests), 5 in
`test_replication_frozen_constants.py` (new), 11 in `test_sector_scorecard.py` (untouched, still
green), 7 in `test_variance_decomposition.py` (untouched, still green) — exact match to the claimed
breakdown.

```
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pyright \
  src/physics/layer2/frozen_constants.py src/physics/instrument_panel/replication.py
# 0 errors, 0 warnings, 0 informations
```
Same result on both test files. `git status --porcelain data/` empty after the run.

The evidence genuinely demonstrates the claimed behavior, not just import/shape checks:
`test_widen_sigma_for_margin_uncertainty_is_quadrature_add` hand-checks the exact `sqrt(29)` value;
`test_margin_uncertainty_widens_interval_and_recovers_out_of_sample_coverage` shows widened coverage
moving from materially-below-nominal back toward nominal (not merely changing, and not overshooting);
`test_thin_class_is_surfaced_in_coverage_report_not_silently_dropped` shows `n_checks` stays 2 while
`thin_classes` correctly flags the thin one.

## Code/doc quality
Meets project rules. No mutable module-level state introduced; tunable thresholds live in named
frozen constants; no DB access anywhere in the new/edited code (confirmed no sqlite/`DatabaseManager`
import, both new test files build synthetic grids/dicts only). Truth-anchored tests hit the highest
applicable level for this refinement: L1 analytical (`sqrt(29)`, `driver_se==5.0` exact), L2
known-answer/invariant (coverage recovery toward nominal), L3 degenerate case (`None`-SE contributes
zero, `margin=None` is a no-op). Uncertainty inflation and fallback behavior (thin flag, undefined-SE
handling, no-op default) are visible in both code and dedicated tests. All new randomness in tests
uses `np.random.default_rng` with explicit seeds.

**Fowler refactoring pass** (survey item `r6-fowler`, full record in
`.agent-work/668-instrument-panel/g6-finalize-review/fowler_pass.json`, `verify_fowler_pass.py` exits 0):
10 of 12 baseline smells absent. `duplicated-code` **flagged** (non-blocking): `main_effect_margin_uncertainty()`'s
driver/class grouping loop structurally echoes `_axis_means()`'s grouping loop (different aggregation
need — SE requires the raw value list, mean only needs sum/count) — a shared axis-grouping helper
would remove the near-duplicate shape; routed to triage as a simplify-pass candidate, not a rework
request. `comments-as-deodorant` **overridden**: the module's extensive docstrings are required
frozen-constant/physics-model provenance documentation per the project's own `frozen_constants.py`
discipline and CREW_CONTEXT.md's traceability rule, not cover for unclear naming — the underlying
names and structure were independently readable during review without the prose.

## Map impact verdict
- **Evidence supports claimed change:** yes — the 5 frozen constants, the factory, and refinement 2
  are all backed by tests that were independently reproduced.
- **Constraints not violated:** yes — F12-independence held (the pure core still takes injected
  params; `frozen_replication_thresholds()` is the one production seam); no-frame-kill held (thin
  classes surfaced); no-baked-normality held (Student-t throughout).
- **Notes match the diff:** yes — the Map Impact section's structural/capability/constraint claims
  match exactly what the diff touches, no overstatement.
- **Decision candidates surfaced:** n/a — this gate resolves `decision:replication-deferred`
  (already graded `settled/human` in the epic's own `execute.json` spine, `leans g6,g7`); no new
  decision requiring authority beyond this gate arose.
- **Durable context routed:** yes — the one non-blocking Fowler observation is routed to triage
  (`tc1`), not silently dropped or over-escalated to a blocker.

## Reconciliation check
No gap. `decision:replication-deferred` lives only in this epic's own `execute.json` spine (graded
`settled/human`) plus `MISSION_FRAME.md`/`PROBLEM_STATEMENT.md`; no `docs/architecture/` anchor yet
references `instrument_panel` or `frozen_constants.py` (grep confirmed) — correct, since this epic
has not reached its architecture-map reconciliation/closeout gate. Promotion to Cartographer is a
later-gate concern, not this one's.

## Blockers
- none

## Out-of-scope observations
- Simplify-pass candidate (non-blocking, flagged to triage as `tc1`): extract a shared axis-grouping
  helper in `replication.py` so `main_effect_margin_uncertainty()` and `_axis_means()` stop
  duplicating the same driver/class grouping loop shape.

## Workflow Feedback
- **Handoff gaps:** none. The handoff's 5 close criteria mapped cleanly onto the survey's `r1-handoff`
  item; the "quadrature-adds ... BEFORE predictive_t" ordering requirement was concrete enough to
  verify directly by reading the call sequence in `out_of_sample_coverage`.
- **Context rediscovered:** the fact that the whole `src/physics/instrument_panel/` tree shows as
  untracked in `git status` (because the epic has never committed on this branch) was not called out
  in the handoff and needed independent confirmation — I resolved it by cross-checking the g3-gate
  implement-result (which documents `replication.py` as NEW at g3) and a file-mtime comparison across
  the whole tree, rather than being able to `git diff` against a prior commit for scope verification.
- **Instructions improvised around:** none for the engine/skill mechanics; the survey drove cleanly
  end to end.
- **What would have made this easier:** a one-line handoff note that the module tree is uncommitted
  on this branch (so scope verification for untracked-directory gates needs mtime/prior-gate-result
  cross-checking rather than `git diff`) would have saved the extra research step — the same friction
  the implementer's own workflow feedback flagged for the `data/` WAL-touch case; this is the
  analogous gap for scope verification.

## Return status
`complete`
