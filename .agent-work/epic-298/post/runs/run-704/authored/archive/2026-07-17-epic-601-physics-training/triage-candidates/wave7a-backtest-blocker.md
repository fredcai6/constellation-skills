# Triage candidate — sampled-runtime backtest hangs headless (blocks the evo A/B)

**Symptom:** `backtest_sampled_runtime` (and any `sampled_runtime_from_manifest` + score) HANGS with CPU=0 at the first race whenever run in a non-interactive / no-console context — verified across: explicit Bash `run_in_background`, `Start-Process -WindowStyle Hidden` (with and without pipe redirection), concurrent processes, and both the parallel `ResourcePlan(level=max)` pool AND plain sequential (`plan=None`). The ONLY configuration that completed was a single foreground command that the harness auto-backgrounded (219s/race, CPU active). This env also reaps background bash tasks aggressively (~minutes), so long foreground-style runs also die.

**Likely root cause:** a loky/joblib (or torch inter-op) backend that deadlocks on init without a controlling console/tty. CPU=0 at "race 1 start" = blocked acquiring a backend resource before any NN compute. Not a base issue (reproduced on origin/main, which has the #619 determinism fix).

**Impact:** Wave 8's real physics→evo A/B (the confirmatory step) CANNOT be driven headlessly here as-is. Options to file/resolve:
1. Add a `--no-parallel` / synchronous-safe path that avoids loky entirely (pure in-process, no executor) — usable headless.
2. Diagnose the exact blocking call (loky resource_tracker? tqdm on no-tty? torch threads) and guard it when `not sys.stdout.isatty()`.
3. Run the A/B in an interactive session/terminal where the console is attached (operational workaround).

**This wave's mitigation:** the go/no-go gate ran as a sampler-free PROXY screen (physics vs a data-only baseline residual) instead of the full evo backtest. Recommend filing option 1 or 2 as an issue before Wave 8 so the real A/B is runnable.
