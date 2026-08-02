# Problem Statement — fn-decomposition-and-bitrepro (Commander run #2)

Follow-ups from issue #356 triage (recorded, not filed as GitHub issues). Same branch
(claude/recursing-hofstadter-5c4e0d). Confirmed by human 2026-06-03.

## Part A — Decompose over-limit functions (behavior-preserving cleanup)
Split the 5 pre-existing simplification offenders surfaced (not caused) by #356 so strict
`py -m src.utils.simplification_limits --paths` passes on each touched file. **Exclude** the two legacy
mega-files (`_param_dataclasses.py`, `html_reports/__init__.py`) — out of scope.

Targets:
- `src/evo_predictor/run.py::_build_parser` (~201 lines)
- `src/evo_predictor/run.py::cmd_train_latent_power_module` (~124 lines)
- `src/evo_predictor/gold_cycle/config.py::_parse_and_validate` (~142 lines)
- `src/evo_predictor/gold_cycle/runner_support.py::_gold_preflight_coverage` (CC=21, ~114 lines)
- `scripts/run_sampled_runtime_comparison.py::run_comparison` (~134 lines)

Protected intent: NO behavior change. Each decomposition verified by the existing region tests staying
green + `--paths` passing on the file. Pure helper extraction; no contract/signature changes to callers.

## Part B — Bit-reproducibility spike + conditional implement
Investigate whether latent-power CPU training can be made bit-reproducible (the ~3e-4 run-to-run weight
drift #356 found). Measure `torch.use_deterministic_algorithms(True)` + deterministic reductions + thread
pinning on a smoke cycle: weight/metric stability AND training-time cost. Produce a report + go/no-go.

**Conditional implement:** IF the spike shows determinism is beneficial (bit-stable or near-bit-stable weights
at acceptable training-time cost), land a CONFIG-GATED deterministic-training mode (off by default; opt-in flag).
IF not beneficial, document the finding and stop (no production change). The go/no-go is a HUMAN decision
surfaced at the spike's completion, against a criterion proposed in the plan.

Protected intent: deterministic mode is OFF by default (no change to existing gold runs unless opted in);
DB-only analysis and gold-mode rules untouched; the #356 utilization determinism guarantee remains valid.

## Evidence obligations (Charter)
- `py -m src.utils.simplification_limits --paths <touched>` on every touched Python path.
- Region test suites green (evo unit for A's evo functions; rt-comparison tests for the script; gold-cycle
  smoke for B's measurement).
- B's report is machine-checkable where possible (captured measurements, seeds/tolerances named).

## Plan shape (to be authored at plan step)
- A: ~2 gates (evo-side functions; the script function).
- B: a spike gate (measure + report + surface go/no-go) and a CONDITIONAL implement gate (skipped if no-go).
