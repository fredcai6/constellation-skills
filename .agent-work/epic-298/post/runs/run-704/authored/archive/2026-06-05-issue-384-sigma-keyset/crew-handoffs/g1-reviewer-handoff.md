# Reviewer Handoff

## Gate
`g1`

## What Was Implemented
Issue #384 fix: aligned the consumer σ-correlation key set `module_uncertainty_diagnostics._SIGMA_ERROR_CORR_KEYS` to the two σ channels the gold-cycle producer (`gold_module_cycle.uncertainty_calibration`) actually emits — `corr_sigma_pi_trace_vs_nll` + `corr_sigma_pi_trace_vs_rank_mae`. Added a structural producer≡consumer pin test, reworked the diagnostics tests that previously fabricated `log_loss`/`brier` keys, fixed a stale pipeline-validation fixture, and appended a resolution note to the design doc.

## How to Inspect the Diff
Working tree vs the branch point (this branch has no commits yet):
```bash
cd C:/Programs/f1Brainz/.claude/worktrees/agent-a43c9994cf94e812c
git diff HEAD -- src/evo_predictor/module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py docs/evo/prediction_ceiling_and_priorities.md
```
NOTE: do NOT use `git diff origin/main` — origin/main advanced ~10 sibling commits after this branch was cut, so that diff is misleading. Use `git diff HEAD` (4 files only). Full IMPLEMENTER_RESULT: `.agent-work/issue-384-sigma-keyset/crew-handoffs/g1-implementer-result.md`.

## Task Statement
Reconcile the σ key sets so consumer ≡ producer, make the n-aware wrong-sign/insignificant σ gate evaluate the channels it claims (not `rank_mae` alone), and pin producer ≡ consumer with a STRUCTURAL test that can't drift. Direction (consumer→producer; nll+rank_mae) was decided by Admiral PRE-RULING R2 + code/schema/git evidence.

## Close Criteria
- `_SIGMA_ERROR_CORR_KEYS == ("corr_sigma_pi_trace_vs_nll", "corr_sigma_pi_trace_vs_rank_mae")`.
- A structural pin test exists that derives BOTH key sets from live code (imports the consumer constant; CALLS the real producer `uncertainty_calibration()` and filters to `corr_sigma_pi_trace_*`) and asserts set-equality. It must be able to FAIL on drift — NOT a hardcoded expected list.
- The σ gate now reads both σ channels: there is a test proving the gate fires on a significantly wrong-signed `nll` correlation while `rank_mae` is benign (the #384 symptom).
- Reworked diagnostics tests + pipeline-validation fixture use producer-real keys; no test still asserts the gate fires on `log_loss`/`brier`.
- Doc note under §6.2 F2 is append-shaped (existing prose untouched), references #384.
- `py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q` passes.
- Pyright clean on the touched src module.

## Allowed Scope
`src/evo_predictor/module_uncertainty_diagnostics.py` (constant + comment only); `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`; `tests/unit/evo_predictor/test_pipeline_validation.py` (correlation fixture only); `docs/evo/prediction_ceiling_and_priorities.md` (append under §6.2 F2 only).

## Specific Exclusions (flag if touched)
- Producer `src/evo_predictor/gold_module_cycle.py` — must be UNTOUCHED.
- `gold_report_schema.py` / any emitted-report field or summary-key name — must be UNCHANGED.
- `entity_count` / `event_level_metrics` / calibration dof term — sibling #383, must be UNTOUCHED.
- No `brier`/`log_loss` correlations emitted anywhere; no field_std widening of the σ gate.
- No rewrite of existing prose in `prediction_ceiling_and_priorities.md` (append only).

## Constraints the Implementation Must Respect
- Consumer aligns to producer (one canonical key set; no dual sets / shims).
- The pin test must be structural (live-code-derived both sides).
- Doc edit append-shaped.
- `py` for Python.

## Evidence Produced (from IMPLEMENTER_RESULT — verify independently)
- `py -m pytest <both files> -q` → 79 passed.
- `py -m pyright src/evo_predictor/module_uncertainty_diagnostics.py` → 0 errors.
- `py -m src.utils.simplification_limits --baseline` → FAIL on 2 PRE-EXISTING unrelated files only (`_param_dataclasses.py`, `html_reports/__init__.py`); none in touched functions. (`--paths` strict mode additionally flags pre-existing `render_module_uncertainty_diagnostics_markdown` complexity — untouched by this diff. Confirm it is not a regression.)
- Pin test red→green transition documented (RED showed extra brier+log_loss / missing nll).

## Verification You Should Run
```bash
cd C:/Programs/f1Brainz/.claude/worktrees/agent-a43c9994cf94e812c
git diff HEAD --stat
py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q
py -m pyright src/evo_predictor/module_uncertainty_diagnostics.py
# Optional: prove the pin test is genuinely structural — temporarily break the
# constant, confirm test_consumer_sigma_keys_equal_producer_sigma_keys FAILS, restore.
```

## Suggested Model Tier
`simple bounded` — dispatch with model: sonnet. Small, well-specified diff; the one judgment call is whether the pin test is genuinely structural (live-derived) vs a disguised hardcoded list.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent/unverifiable, the pin test is not actually structural, an exclusion was touched, or a policy decision is required before a verdict.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
