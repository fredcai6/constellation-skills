# Implementer Handoff

## Gate
`g2` (wide-sigma A/B checkpoint)

## Task
Push the EXISTING five-view `session_estimates` physics estimates for ONE real weekend through the EXISTING residual-history injection seam with a deliberately WIDENED sigma, then run the headless `sampled-predict` once with the injection ON and once OFF (G0/G1 read once, no tuning/iteration). This confirms whether the prototype seam wires, and gives an informational read of whether raw physics estimates already carry signal through this seam — it does NOT build any new machinery.

## Protected Intent
This is an INFORMATIONAL checkpoint (F1/F11, no kill switch). Do NOT build the Phase-6 BT injection or any new seam. If wiring genuinely requires more than the existing `driver_residual_history_adapter.build_neutral_driver_residual_history_field` + `RuntimeModuleContext.driver_residual_states` seam supports, STOP — do not build a workaround — and report that as the finding instead (this is expressly sanctioned: Pre-Ruling #3 says float rather than build Phase 1-6 machinery).

## Test Mode
Inspection-only / evidence-only — this is a probe, not a production behavior change. No existing test suite covers this seam being actually populated (it always runs neutral today).

## Close Criteria
- Read `src/evo_predictor/driver_residual_history_adapter.py:9-24,32-115` (`DriverResidualState`, `DriverResidualStateEntry`, `build_neutral_driver_residual_history_field`) and `src/evo_predictor/module_context.py:25` (`RuntimeModuleContext.driver_residual_states`) and `src/evo_predictor/module_adapters/_runtime_builders.py:536-581` (`_make_runtime_driver_residual_history`) to confirm the EXACT signature/contract before writing any code — this is the existing seam, verify it from source, do not guess.
- Pick ONE real weekend with `session_estimates` Q rows available (any year 2019-2025, prefer one also usable for g3's tracer — 2025 Japan is a good default if it has physics estimates; check first).
- For that weekend, build a `DriverResidualState` populated with `DriverResidualStateEntry(residual_mean=<pre-registered primary axis value for that driver's constructor>, residual_variance=<deliberately WIDENED sigma>)` for every driver in the field. Broadcast constructor-grain physics to both of that constructor's drivers (same simplification as g1, state it explicitly).
- **Widened sigma discipline**: do not just copy a single view's own diagonal variance. `x7-basis-map-RESULT.md` section (c) establishes there is NO stored cross-view covariance and the views are NOT jointly solved — the store's within-view sigma structurally understates true uncertainty for a composite axis like `lateral_total_grip_g` (sum of two correlated-in-reality-but-uncoupled-in-the-store components). Inflate accordingly (e.g. a documented multiplicative factor, or sum the two components' own variances as a conservative independence-assumption floor PLUS an explicit inflation factor) and WRITE DOWN the exact formula and its justification in the findings doc — this is exactly what "honestly accounting for the uncoupled covariance" means operationally.
- Wire this `DriverResidualState` into a `RuntimeModuleContext` for a `sampled-predict` run on that weekend (year/race args matching the launch order's verified headless invocation shape: `--sampled-runtime-manifest params/gold/sampled_runtime_manifest.json --year <Y> --race <race> --seed 42 --compound-prior-root params/gold/compound_prior --db-path data/f1_data_<Y>.db --output <path>`, all absolute paths into `C:/Programs/f1Brainz/`). You will likely need a small driver script (not a change to `run.py`) that constructs the `RuntimeModuleContext` with `driver_residual_states={'quali': <state>}` and calls the same runtime entry point `sampled-predict` uses internally — find that entry point from `src/evo_predictor/run.py`'s `sampled-predict` command handler and `SampledEvoRuntime.predict_from_features`, and confirm whether `RuntimeModuleContext` is constructable/injectable from outside without deeper plumbing changes. If it is NOT cleanly injectable without modifying `run.py`/`sampled_runtime.py` internals beyond a thin driver script, that itself is the STOP condition above — report it, do not modify those files.
- Run headless with `PYTHONIOENCODING=utf-8`, confirm CPU>0 (not the #623 deadlock signature — if you see 0% CPU at race 1, STOP and report that as a regression finding immediately).
- Run ONCE with the injection populated (widened sigma), ONCE with it absent (baseline, i.e. today's default neutral behavior) — same weekend, same seed. Read G0 (does the injected field show up sanely in the output — e.g. does it perturb the quali stage output at all, in the expected direction for the pre-registered axis's sign convention) and G1 (Brier score of the quali predictions, injection vs baseline) ONCE each. Do not iterate/tune to a preferred outcome.
- **After the run(s), `cd C:/Programs/f1Brainz && git checkout -- data/` to discard any DB rewrite side-effect from running against `--db-path` (per known issue #632 — running the sampler against a `--db-path` DB rewrites/bloats it via `processed_telemetry`). Do this in the MAIN checkout, not this worktree.**
- Write findings to `.agent-work/624-phase0/G2_FINDINGS.md`: exact seam used, exact sigma-widening formula + justification, G0/G1 reads for both runs, whether the headless smoke was green (confirms #623 fix holds under this modification), and an honest read (this is a raw-estimate probe, not the Phase-3 unified-basis result — say so).

## Allowed Scope
- New file(s) under `C:/Programs/f1-624/scripts/` (e.g. `g2_wide_sigma_ab.py` or similar) — a standalone driver script.
- New file `.agent-work/624-phase0/G2_FINDINGS.md`.
- Read-only on `src/evo_predictor/driver_residual_history_adapter.py`, `module_context.py`, `_runtime_builders.py`, `run.py`, `sampled_runtime.py` — to understand the seam, NOT to modify them.
- Read `data/physics_estimates.db` (absolute path into `C:/Programs/f1Brainz/data/`) and the season DB for the chosen weekend.

## Specific Exclusions
- Do NOT modify any file under `src/` (this is a probe using the EXISTING seam only, from outside).
- Do NOT build a new injection seam, the Phase-6 BT injection, or any `params/gold/*` default change.
- Do NOT commit or stage any `data/*.db` file.

## Constraints
- `py` not `python`. `PYTHONIOENCODING=utf-8` on the sampler subprocess.
- Absolute paths into `C:/Programs/f1Brainz/` for manifest/compound-prior-root/db-path (per the launch order's verified invocation shape and `lesson:worktree-untracked-data`).
- After any sampler run against `--db-path`, `git checkout -- data/` in the MAIN checkout.
- Expect this run to take ~3-4 min per race headless (per prior-wave verdict); budget for two runs (~10 min total).

## Map Anchors (inbound)
- **Structural:** `src/evo_predictor/driver_residual_history_adapter.py:9-24,32-115`; `src/evo_predictor/module_context.py:25`; `src/evo_predictor/module_adapters/_runtime_builders.py:536-581`.
- **Capability:** `struct:evo.sampled_runtime` — the live 3-stage sampled predictor, headless-safe per #623.
- **Constraints/assumptions:** Pre-Ruling #3 (no Phase 1-6 machinery; float if the seam doesn't support this without new construction).
- **Decision anchors:** none new.
- **Evidence expectations:** `x7-basis-map-RESULT.md` section (c) — the "no cross-view covariance stored" fact that must ground the sigma-widening formula.
- **Map confidence flags:** the `driver_residual_states` seam has ZERO current callers that populate it non-empty (verified at understand-step) — you are the first real exercise of this path; expect the unexpected and report friction honestly rather than forcing it to work.

## Deliverable Path Check
- **Committed** — `C:/Programs/f1-624/scripts/g2_wide_sigma_ab.py` (or your chosen name); run `git check-ignore` on it before finishing, record exit code.
- **Local-only** — `.agent-work/624-phase0/G2_FINDINGS.md`.

## Required Evidence
- Full stdout of both sampler runs (or the STOP-condition finding if the seam doesn't support clean injection).
- CPU>0 confirmation (describe how you checked — e.g. `Get-Process`/`top` snapshot during the run, or wall-clock-vs-expected-idle reasoning).
- The exact sigma-widening formula used, in the findings doc.
- `git status --short` in BOTH the worktree (`C:/Programs/f1-624`) and, if you touched `data/`, confirmation the main checkout's `data/` is clean after `git checkout --`.

## Verification Commands
```bash
cd C:/Programs/f1-624 && py scripts/g2_wide_sigma_ab.py --check   # or equivalent smoke re-run
cd C:/Programs/f1Brainz && git status --short data/               # confirm no dirty DB left behind
```

## Suggested Model Tier
Stronger — reason: real risk the seam doesn't cleanly support external injection without touching `run.py`/`sampled_runtime.py`, requiring a judgment call on whether to STOP-and-report vs proceed; also real numerical/statistical care needed on the sigma-widening formula.

## Authority
The seam choice (existing prototype only, no Phase-6 BT injection), the pre-registered axis, and the "no new modeling" boundary are already decided — do not re-litigate. You decide: which weekend, exact driver-script shape, exact sigma-widening formula (document your reasoning).

## Stop Conditions
Stop and return if: the seam cannot be exercised without modifying `src/` files beyond a thin external driver script (this is the Pre-Ruling #3 float trigger — report exactly what would be needed, do not build it); the headless run shows 0% CPU (the #623 deadlock signature — report as a regression, do not debug/fix it yourself); a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (full stdout), assumptions used, stop conditions hit (if any — a STOP here is a legitimate, complete result), out-of-scope observations, workflow feedback.
