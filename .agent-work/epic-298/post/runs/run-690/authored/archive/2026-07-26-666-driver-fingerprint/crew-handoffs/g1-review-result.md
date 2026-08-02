# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` (issue #666, epic #659)

## Result
`APPROVE`

## Handoff compliance
Full handoff intent satisfied. `FINGERPRINT_FROZEN` (`src/physics/fingerprint/frozen_constants.py`)
holds exactly the 4 commander-pre-registered values (`FINGERPRINT_NOMINAL_COVERAGE_LEVEL=0.80`,
`FINGERPRINT_UNDER_COVERAGE_BOUND=0.60`, `FINGERPRINT_RECENCY_HALFLIFE_ROUNDS=5.0`,
`FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR=1.0`), verified by direct read and by independently
re-running `test_frozen_constants.py` (4/4 pass). `scripts/fingerprint_class_coverage_675.py`
faithfully reproduces #665's synthetic-recovery coverage method
(`scripts/pooling_imbalance_validation_665.py`, read-only, confirmed untouched) but driven by
real per-(driver, class) support counts from the bounded slice DB instead of #665's proxy
class-share profiles: same generative model, same `fit_two_way`/`predictive_t(nu_loss=4.0,
FormulaRule())` wrap, `N_REPS=200`, Clopper-Pearson exact binomial CI. The load-bearing subtlety
— `n_eff` passed to `predictive_t` is the SUMMED REAL per-axis observation count, never
`fit_two_way`'s own `.n` — is correctly implemented (`_axis_totals` / `run_fit_two_way_branch`)
and I independently confirmed `TwoWayPool.n` (`src/physics/layer2/pooling.py:165`) is a
total-row count (`n = y.size`), NOT a per-axis effective count, so using it would have been
the exact bug this check exists to catch. Stop conditions all avoided.

## Scope drift
None. `git status --porcelain` shows only the 4 allowed new paths (`.agent-work/...`,
`scripts/fingerprint_class_coverage_675.py`, `src/physics/fingerprint/`,
`tests/unit/physics/fingerprint/`). `git diff`/`git diff --cached` on `pooling.py`,
`student_t.py`, `driver_utility.py` are empty — untouched, read-only imports only. Nothing
staged. G2/G3 (store/vocabulary/fit) correctly not built here. The driver-axis under-coverage
caveat is the known, commander-adjudicated finding named in the handoff's Specific Exclusions —
correctly documented by the implementer, not used to alter the `generalizes` rule, and not
treated as a defect of this gate.

## Evidence verdict
Independently reproduced both required commands, foreground, from the worktree root with the
pinned interpreter and `PYTHONPATH=.` (never bare `py`):
- `pytest tests/unit/physics/fingerprint/test_frozen_constants.py -v` → 4 passed (matches).
- `scripts/fingerprint_class_coverage_675.py --slice-db .agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db`
  → stdout byte-identical to the implementer's pasted evidence
  (`generalizes: {time: true, energy: true}`, `class_vs_driver_gap: {time: -0.0675, energy:
  0.026249999999999996}`); the resulting `coverage_675_verdict.json` on disk (produced fresh by
  my own re-run) matches the implementer's pasted full JSON exactly, including CI bounds,
  `generalizes` flags, and `shared_floor_recommendation` values.
- `py -m src.utils.simplification_limits --paths src/physics/fingerprint
  scripts/fingerprint_class_coverage_675.py tests/unit/physics/fingerprint` → PASS (5 files).

Required evidence is present and genuinely demonstrates the claimed behavior — nothing rested
on an unreproduced claim.

## Code/doc quality
Minimal, maintainable, matches surrounding style (mirrors `src/physics/layer2/frozen_constants.py`'s
module-level immutable-mapping convention and #665's harness structure). `from src...` import
style used throughout. No hidden fallback; errors raised visibly (missing slice DB, zero-spread
energy scale, all-cells-unresolved). DB-only/read-only access honored (`file:...?mode=ro`), no
FastF1/network calls. One non-blocking observation on a coincidental literal match (see Fowler
pass, `r4-quality` finding) — not a violation of the "no duplicate inline literal of the 4 frozen
values" rule, since it is a different, documented, unrelated quantity (`OBS_SIGMA_TIME=1.0`,
verbatim-inherited from #665's own generative-model sigma).

**Fowler code-smell pass** (`.agent-work/666-driver-fingerprint/g1-review/fowler_pass.json`,
cleared `verify_fowler_pass.py` exit 0): `duplicated-code` FLAGGED (non-blocking) —
`fingerprint_class_coverage_675.py`'s `_naive_group_sem`/`_axis_totals`/`draw_ground_truth`/
`draw_synthetic_long_form`/`run_fit_two_way_branch` are near-verbatim copies of the same-named
functions in `pooling_imbalance_validation_665.py`; extracting a shared harness module was out
of this gate's Allowed Scope and #665's script is explicitly not to be edited — worth a future
triage item if a third such script appears. `data-clumps` OVERRIDDEN (logged reason: the
handoff's binding requirement to faithfully reproduce #665's method's own call conventions
subordinates a cosmetic parameter-object redesign). All other 10 baseline smells absent.

## Map impact verdict
- **Evidence supports claimed change:** yes — the `claim: #675-coverage` evidence (verdict JSON
  + test pass) backs exactly the capability claimed (a per-channel/axis synthetic-recovery
  coverage verdict on the real bounded slice).
- **Constraints not violated:** yes — F12 pre-registration honored (values fixed before the
  first real-data run, none tuned to the observed numbers); forbidden files untouched.
- **Notes match the diff:** yes — the new `struct:physics.fingerprint` anchor, and the
  read-only consumption of `struct:physics.layer2 pooling.fit_two_way` /
  `struct:common student_t.predictive_t`/`FormulaRule`, match what the diff actually touches.
- **Decision candidates surfaced:** yes — `decision:pooled_sigma_shared_systematic_floor`'s
  class-axis lever (the `shared_floor_recommendation` output) is correctly surfaced as an input
  to that decision, with final apply/no-apply explicitly left to the commander, not decided here.
- **Durable context routed:** yes — the driver-axis floor question and the `.gitignore` gap were
  captured as implementer triage candidates; re-flagged below as `tc1` so they reach Triage.

## Reconciliation check
No unreconciled architecture divergence. Nothing here contradicts the recorded structural
baseline; the new package and script are additive and correctly scoped.

## Blockers
- none

## Out-of-scope observations
- Whether G3's `shared_floor` fix should also cover the DRIVER axis: this bounded 4×4 slice
  shows the driver axis under-covering nearly as badly as the class axis (a scoped few-groups
  artifact of restricting BOTH axes to k=4 entities, not necessarily true of the full
  ~20-driver production case). Open question for the G3 commander/implementer — not resolved
  here, and correctly not treated as a defect of this gate per the handoff's Specific Exclusions.
- `.gitignore` has no `*.json` pattern under `.agent-work/**` (only `*.db` etc.), so
  `coverage_675_verdict.json` is NOT actually git-ignored (`git check-ignore` exits 1) even
  though nothing was staged here. A future careless `git add -A` in this worktree could pick it
  up. Worth a small `.gitignore` follow-up.
- Both items filed as review-side triage candidate `tc1` in the survey for Commander/Triage to
  drain.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's pin of the coverage method (down to the `n_eff`
  semantics and the binomial-CI requirement) was precise enough to verify without guessing.
- **Context rediscovered:** none beyond the ordinary read of `pooling_imbalance_validation_665.py`,
  `student_t.py`, and `pooling.py` (specifically confirming `TwoWayPool.n = y.size` to validate
  the n_eff claim) that the handoff already pointed at directly.
- **Instructions improvised around:** none — the survey template + engine verbs covered this
  review cleanly; the `flag-candidate` verb was used to carry the implementer's out-of-scope
  observations forward into the survey's own bubble-up channel so they are not lost at
  consolidation.
- **What would have made this easier:** none — this was an unusually clean, precisely-scoped
  handoff; nothing to report beyond the routine triage items above.

## Return status
`complete`
