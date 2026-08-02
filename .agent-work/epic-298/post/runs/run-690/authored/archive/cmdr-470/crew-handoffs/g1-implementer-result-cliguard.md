# Implementation Result

## Assigned gate
`g1-cliguard — bypass pred_dir guard for --inherit-fusion + fix stale help text`

## Completed slice
1. **Guard bypass** (`scripts/run_walkforward_backtest.py` line 158): wrapped the `pred_dir.is_dir()` check in `if not args.inherit_fusion`, so inherit-fusion runs proceed without requiring the absent `params/gold/per_race_predictions` directory. Non-inherit mode guard is unchanged.
2. **Help text fix** (`scripts/run_walkforward_backtest.py` lines 130-135): replaced stale sentence "P0 still reuses the promoted gold per-race predictions." with "P0 scores the live gold sampled-runtime manifest directly over rounds 1-6 (no per-race-predictions reuse, no gold cycle for P0)."
3. **Tests added** (`tests/unit/evo_predictor/walkforward/test_run_scripts.py`): new class `TestMainGuards` with two tests:
   - `test_inherit_fusion_does_not_return_2_when_pred_dir_absent` — proves the bypass.
   - `test_non_inherit_returns_2_when_pred_dir_absent` — proves the guard is preserved in default mode.

## Scope
**Files changed:**
- `scripts/run_walkforward_backtest.py`
- `tests/unit/evo_predictor/walkforward/test_run_scripts.py`

**Specific exclusions touched:** no — orchestrator, pipeline, and all other files were not touched.

## Behavior changed
Yes. `main()` with `--inherit-fusion` no longer exits with rc=2 when `params/gold/per_race_predictions` is absent. Default mode behavior is identical to before.

## Map Impact
Trivial local CLI guard change — no structural, capability, constraint, or decision map impact beyond the CLI surface of `run_walkforward_backtest.py`. No new modules, no interface changes, no data-flow changes.

## Test mode
**Required:** test-first (TDD; test surface exists)
**Satisfied:** yes — confirmed red (1 failure) before applying fix, then green (2 pass) after fix.

## Evidence

```bash
# Red phase (before fix) — 1 failure, 1 pass:
py -m pytest tests/unit/evo_predictor/walkforward/test_run_scripts.py::TestMainGuards -q
# FAILED test_inherit_fusion_does_not_return_2_when_pred_dir_absent
# 1 failed, 1 passed in 0.15s

# Green phase (after fix):
py -m pytest tests/unit/evo_predictor/walkforward/test_run_scripts.py::TestMainGuards -q
# 2 passed in 0.12s

# Full walkforward suite:
py -m pytest tests/unit/evo_predictor/walkforward/ -q
# 155 passed in 3.55s

# Simplification limits:
py -m src.utils.simplification_limits --paths scripts/run_walkforward_backtest.py
# PASS (1 files checked)
```

**Result:** pass

## TDD evidence, if required

- Failing test observed: `FAILED test_inherit_fusion_does_not_return_2_when_pred_dir_absent — AssertionError: inherit-fusion mode must bypass the pred_dir guard; got rc=2`
- Passing test observed: `2 passed in 0.12s` after applying the one-line fix
- Refactor while green: no refactor needed — change was minimal

## Docs/contracts touched
- `scripts/run_walkforward_backtest.py` help text only (inline argparse doc, not a separate docs file). No docs/ files required updating — this was a CLI string correction.

## Assumptions
- `WalkforwardOrchestrator` in inherit mode never reads `promoted_predictions_dir` (confirmed by handoff and by the fact that the fix passes with the orchestrator mocked). The orchestrator is still constructed with `pred_dir` (which may not exist on disk in inherit mode) — this is safe per handoff guidance.
- `scripts/` is not in pyright `include` (per CLAUDE.md note), so pyright was not run on the script. This matches the handoff note.

## Stop conditions hit
- None.

## Out-of-scope observations
- `build_dry_run_plan()` in `scripts/run_walkforward_backtest.py` line 64 still renders P0 in `reuse_promoted_gold` mode even when `inherit_fusion=True` is passed. In the dry-run plan output this shows `REUSE promoted gold` for P0. This is a cosmetic inconsistency in `--dry-run` output only (no correctness impact since dry-run executes nothing). Triage candidate for a follow-up — out of scope for this fix.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: task, intent, allowed scope, exclusions, required evidence, test mode, and stop conditions were all explicit and unambiguous.
- **Context rediscovered:** the exact method signature of `simplification_limits` (`--paths` flag) was not in the handoff command; the handoff showed `py -m src.utils.simplification_limits scripts/run_walkforward_backtest.py` (positional arg), which the tool rejected. Discovered the correct form by running the command and reading the usage error. Minor friction.
- **Instructions improvised around:** the checklist engine (`scripts/checklist_engine.py`) was not present in the repo (neither in the skill bundle nor in `C:/Programs/f1Brainz`). Ran the plan as a self-managed gated checklist, driving each step and verifying postconditions by running the named commands directly. Documented plan in `.agent-work/cmdr-470/crew-handoffs/g1-impl-plan.json` for Commander visibility.
- **What would have made this easier:** include the correct `simplification_limits` invocation form (with `--paths`) in the handoff's test commands, matching what the tool actually accepts.

## Return status
`complete`
