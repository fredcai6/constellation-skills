# Triage Recommendations — issue #356 closeout

Two issue-ready recommendations from three engine triage candidates (tc1+tc2 consolidated; tc3 standalone).

---

# Triage Recommendation: Decompose over-limit functions in evo CLI/config + scripts

## Classification
cleanup

## Source checklist/artifact
execute.json triage_candidates tc1, tc2; G2/G3/G5 implementer+reviewer findings.

## Structural anchor
src/evo_predictor/gold_cycle/config.py, src/evo_predictor/run.py,
src/evo_predictor/gold_cycle/runner_support.py, scripts/run_sampled_runtime_comparison.py

## Problem
Several functions exceed the project's simplification limits (function < 100 lines, CC < 20). They are
PRE-EXISTING (not caused by #356) but were surfaced by the strict `--paths` check while touching these files.
The canonical `--baseline` gate grandfathers them, so they don't block, but they're real maintainability debt.

## Current truth
- `config.py::_parse_and_validate` ~142 lines (was 134 pre-#356).
- `run.py::_build_parser` ~201 lines; `run.py::cmd_train_latent_power_module` 124 lines (untouched by #356).
- `runner_support.py::_gold_preflight_coverage` CC=21, 114 lines (untouched by #356).
- `scripts/run_sampled_runtime_comparison.py::run_comparison` 134 lines (was 135 pre-#356).

## Desired/future concern
Decompose each into focused helpers so strict `--paths` passes on these files and the baseline debt shrinks.

## Evidence
- `py -m src.utils.simplification_limits --paths <files>` reports these function-length / CC violations.
- #356 reviewers confirmed they are pre-existing (cmd_train_latent_power_module unchanged = dispositive).

## Impact
Maintainability + agent navigability; unblocks strict per-file simplification on these heavily-edited modules.

## Suggested scope
Extract sub-helpers from each named function until `--paths` passes for these files; no behavior change.

## Non-goals
The two legacy mega-files in the baseline (`_param_dataclasses.py`, `html_reports/__init__.py`); any behavior change.

## Acceptance criteria
- [ ] `py -m src.utils.simplification_limits --paths` passes for config.py, run.py, runner_support.py, run_sampled_runtime_comparison.py.
- [ ] No behavior change (focused region tests stay green).

## Recommended priority
low

**Reason:** pre-existing, grandfathered by baseline, not blocking; cleanup value only.

## Issue creation authority
ask user

---

# Triage Recommendation: Investigate bit-reproducibility of latent-power CPU training

## Classification
research hardening (performance/resource adjacent)

## Source checklist/artifact
execute.json triage_candidate tc3; G6 implementer finding; human decision 2026-06-03.

## Structural anchor
src/latent_power/training.py (and the gold-cycle artifact pipeline)

## Problem
Latent-power training is not bit-reproducible run-to-run on torch 2.10 CPU (py3.14/Win) even with single thread,
fixed seed, and fixed PYTHONHASHSEED: weights drift ~3e-4 and rank-based backtest metrics swing O(0.1-0.3).

## Current truth
#356 empirically established this is intrinsic to torch CPU training (NOT a run_jobs/parallelism defect:
1-vs-2-worker drift 2.8e-4 ≈ same-path rerun drift 3.1e-4). The #356 determinism guarantee was reframed
accordingly (structural byte-identity + weight agreement within 1e-2).

## Desired/future concern
Determine whether bit-stable gold artifacts are achievable/desirable: torch.use_deterministic_algorithms(True),
deterministic reductions, thread pinning; quantify the training-speed cost and any accuracy impact.

## Evidence
- G6 measurements: ~3e-4 weight drift single-thread/same-seed; worker-count adds no systematic divergence.
- tests/integration/test_utilization_determinism.py documents the reframed guarantee.

## Impact
Affects whether committed gold artifacts can be claimed bit-reproducible; relevant to reproducibility/audit and to
any future exact-artifact-diff workflow.

## Suggested scope
A spike: enable deterministic algorithms, measure weight/metric stability + training-time cost on a smoke cycle;
report whether to adopt, with tradeoffs. No commitment to adopt within the spike.

## Non-goals
Changing the #356 determinism guarantee; forcing determinism if the cost is prohibitive.

## Acceptance criteria
- [ ] A short report quantifying achievable bit-stability and its training-time cost.
- [ ] A recommendation: adopt (with config flag) / don't / conditional.

## Recommended priority
medium

**Reason:** affects reproducibility claims for promoted artifacts; human explicitly asked to file it.

## Issue creation authority
ask user (human pre-approved filing 2026-06-03)
