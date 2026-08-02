# Implementer Handoff

## Gate
g3 — Bit-reproducibility spike (measurement + report; NO production code change)

## Task
Empirically determine whether latent-power CPU training can be made (near-)bit-reproducible run-to-run, and at what
training-time cost. Produce a report + a GO/NO-GO recommendation against the criterion below.

## Protected Intent
This is a measurement spike. Do NOT change production training code in this gate. The output is a report with
honest, reproducible measurements that the human will use to decide whether to implement a deterministic mode (G4).

## Background (from #356 G6)
Latent-power training drifts ~3e-4 in weights run-to-run on torch 2.10 CPU even single-thread + same-seed + fixed
PYTHONHASHSEED. The #356 determinism test (`tests/integration/test_utilization_determinism.py`) already has a bounded
harness (2 recent_history quali modules, train_years=[2022,2023], eval_year=2024, max_rounds_per_year=1, ~2 epochs,
real `cmd_train` via `run_jobs`). REUSE that harness/setup for fair, bounded measurement.

## The measurement (fair comparison — vary only the determinism knobs)
Identical seeds/data/config across all runs; vary only the determinism settings. For each condition, run training
TWICE and measure (a) run-to-run weight drift (max abs diff over the model state_dict) and (b) wall-time per run.

Conditions:
1. **baseline** — current behavior (single thread, same seed).
2. **deterministic** — `torch.use_deterministic_algorithms(True)` + `torch.set_num_threads(1)` + any applicable
   deterministic env (note: `CUBLAS_WORKSPACE_CONFIG` is CUDA-only — document as N/A on CPU; consider
   `torch.backends` flags that apply to CPU). Set these BEFORE training ops.

Important: `torch.use_deterministic_algorithms(True)` (strict) may RAISE if an op used in training lacks a
deterministic implementation. If so, that is itself a key finding — capture which op(s), then also try
`warn_only=True` to measure drift while logging the nondeterministic ops. Report both.

## GO/NO-GO criterion (Commander-set; human makes final call)
- **GO** if deterministic mode reaches run-to-run weight drift < 1e-6 (effectively bit-stable) at < 2× baseline
  training wall-time, AND without requiring production code changes beyond a contained set-flags call.
- **NO-GO** otherwise (e.g. strict mode errors on an op with no deterministic impl, drift stays >> 1e-6, or cost >= 2×).
Recommend GO or NO-GO with the numbers behind it.

## Close Criteria
- A report (write to `.agent-work/fn-decomposition-and-bitrepro/bitrepro-report.md`) containing: methodology,
  the harness/config used, a measurements table (drift + wall-time per condition, ≥2 runs each), which ops (if any)
  lack deterministic implementations, and a clear GO/NO-GO recommendation against the criterion.
- The measurement script/harness itself may live as a throwaway under .agent-work (no production change) OR as a
  clearly-marked spike test; do NOT modify src/ training code.

## Allowed Scope
- A measurement harness (throwaway script or spike test under .agent-work or tests/, NOT modifying src/ training code).
- The report file.

## Specific Exclusions
- NO production code change (src/latent_power/training.py etc. stay untouched — that's G4 if GO).
- NO change to the gold cycle, the decomposition targets, or the #356 determinism test (you may IMPORT/reuse its setup).

## Constraints
- Use `py`, not `python`. Bounded runtime; name seeds + tolerances.
- Fair comparison: identical seeds/data; vary only determinism knobs. Report wall-time honestly (warm vs cold).
- Deterministic, reproducible measurement; capture raw numbers.

## Required Evidence
- The report with the measurements table + GO/NO-GO.
- The commands/script used to produce the numbers (so the reviewer can re-run).
- If `use_deterministic_algorithms(True)` raised, the exact op + error captured.

## Verification Commands
```bash
# whatever harness you build, e.g.:
py <your measurement script>   # prints the drift/time table
```

## Suggested Model Tier
stronger — reason: designing a fair determinism experiment, interpreting torch CPU nondeterminism, and handling the
use_deterministic_algorithms-raises case correctly is subtle; a sloppy measurement gives a false GO/NO-GO.

## Authority
Decided: spike-only (no production change here); the GO/NO-GO criterion above (human makes the final call at integrate).
You choose the harness construction and report structure.

## Stop Conditions
Stop and return if: the measurement cannot be made bounded/fair; production code would need changing to even measure
(report that as a finding/NO-GO rather than changing src/); scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT: the measurements (drift + wall-time table), which ops lack deterministic impls (if any),
your GO/NO-GO recommendation with reasoning, the report path, how to re-run, assumptions, stop conditions hit.
