# Launch Order: `cmdr-7a-residual-screen` — physics↔evo residual screen (the go/no-go gate)

You are a delegated Commander under Admiral `epic-601-physics-training`. Run the full Commander spine (understand → plan → execute → cleanup) in your worktree. There is NO reachable human — float decisions to the Admiral via your return report.

## Mission
Answer ONE question with evidence: **does the physics capability signal correlate with what the evo predictor gets WRONG?** This is the gate that decides whether the whole physics→evo wiring effort (Wave 8) is justified. Concretely: build the **as-of-round pooled physics pace axes** (apex/lateral-grip and drag CdA — the established "pace core") per (year, round, constructor) from the EXISTING quali fits, and correlate them against the **evo predictor's per-constructor per-race residuals** on a held-out window. If physics does not correlate with evo's errors, no fusion scheme can extract lift and Wave 8 is unjustified — a clean, valuable negative. This is **analysis only: no production wiring, no changes to `src/evo_predictor` or `src/physics` production code.** Scratch scripts + a findings report.

## Prior-Wave Verdicts / Recon (pasted — you start cold)
- **Live predictor:** `src/evo_predictor/sampled_runtime.py` `SampledEvoRuntime.predict_from_features` (3-stage sampled sim over module adapters in `src/evo_predictor/module_adapters/_registry.py`, fused via `src/evo_predictor/fusion.py` + `src/latent_power/field_solve.py`). It is 100% fed from the SQLite `session_classifications` table; NO physics axis enters any feature today (verified: zero `src.physics` imports under `src/evo_predictor/` or `src/latent_power/`).
- **Evo residuals source:** the A/B/backtest harness in `src/evo_predictor/run.py` (`sampled-backtest` handler `cmd_sampled_backtest`, and `latent-backtest`/`gold-cycle`) already computes held-out predictions and metrics (`pairwise_brier_against_actual_order` in `src/evo_predictor/sampled_backtest.py`; per-module `rank_mae_vs_actual`/`spearman` in gold_module_cycle). Use the existing backtest to obtain per-race predicted vs actual finishing order, and derive a per-constructor residual (predicted position/strength minus realized). Do NOT invent a new predictor.
- **Physics store:** `src/physics/layer2/estimate_store.py` `EstimateStore` — SQLite table `session_estimates`, one row per (year, gp_name, session_type, constructor), holding the five capability views + per-param σ + 2×2 covariances + support metadata. Pooling primitive: `src/physics/layer2/pool_driver.py` `pool_store(df, year, session_type)` → per-constructor (μ, σ_μ, τ). Lateral grip = `lateral_mech_grip_g`/`lateral_aero_grip_g`; drag = `drag_area_closed_m2`. The DB with real rows is at the MAIN checkout: `C:/Programs/f1Brainz/data/physics_estimates.db` (spans 2019–2026, quali fits).
- **Known prior:** CdA/pace is a circuit/setup-conflated, fine-margin axis (frac_team ≤ 3%); ship covariance, treat as relative. So expect a possibly-weak signal — the screen must be careful about noise vs real correlation.

## Pre-Rulings (overridable with evidence — say so if you override)
- **As-of-round only.** For predicting race R of season Y, physics features may use ONLY sessions strictly before R's qualifying (prior rounds' quali fits, and Y−1). A prior-round quali fit is a legal pre-quali feature (it's a slowly-varying car property). NEVER use the current round's quali/race. This is the leak guard — enforce and state it.
- Use the EXISTING quali fits already in `physics_estimates.db`. Do NOT run new physics fits or FP fits (that's deferred #513).
- Correlate the physics axis against evo RESIDUALS (where evo is wrong), not against raw finishing order (physics correlating with order it already predicts proves nothing).
- Hold-out window: 2025 season (per project pre-ruling: train ≤2024, hold out 2025). Additionally report 2026-to-date if the data supports it.
- Constructor-vocabulary join: physics store team names may not match evo `constructor_id` — build and document the mapping; drop unmatched with a logged count, don't silently skip.

## Honest-Null Clause
"Physics does not correlate with evo's residuals under this as-of-round construction" is a COMPLETE, successful deliverable. Report it with the same rigor as a positive. A null here saves two waves — it is a win, not a failure.

## Inherited Latitude
Delegated: subagent dispatch (Sonnet), local analysis/scratch scripts, reading the main-checkout DBs. Float to Admiral (do not do): any production-code change, any DB write/migration, filing/closing issues, merges. Analysis scratch outputs go under your worktree `.agent-work/` or a `reports/` scratch path — do not commit large artifacts.

## File Ownership
Sole writer of your findings file `.agent-work/cmdr-7a-residual-screen/RESULT.md` and any scratch scripts under your worktree. You touch NO production source. No shared-file contention with 7B/7C (they touch `regulation_era.py`/pooling and git-reconcile respectively).

## Workspace
Worktree: `C:/tmp/f1brainz-601-7a-residual`, branch `wave7a-residual-screen`, base `5e8e92d7` (local main). Created via `git worktree add -b wave7a-residual-screen C:/tmp/f1brainz-601-7a-residual 5e8e92d7`.
FIRST STEP before any git op: run `py scripts/verify_worktree_isolation.py --here C:/tmp/f1brainz-601-7a-residual` — must exit 0; paste output into your report.

## Inherited Context (invariants)
- Python is `py` (3.14). Tests: `py -m pytest tests/...`. Shell is PowerShell primary; a Bash tool exists.
- **Editable-install .pth trap:** a global editable `.pth` makes ad-hoc scripts in a worktree silently import the MAIN repo `src/`. For any bespoke script, insert your worktree `src/` at the front of `sys.path` (or run with `PYTHONPATH` pinned to the worktree) so you analyze YOUR tree. pytest is unaffected.
- DB is the single source of data; no direct FastF1 calls from analysis code.
- The physics store DB and per-year DBs live in the MAIN checkout (see Data Locations) — worktrees do not carry the untracked/large DBs.
- Windows: write PR/GH bodies to a temp file and use `gh ... -F <file>`.

## Data Locations (main checkout — worktrees lack these)
- Physics estimates: `C:/Programs/f1Brainz/data/physics_estimates.db`
- Per-year classification DBs: `C:/Programs/f1Brainz/data/f1_data_<year>.db` (2022–2026)
- If a needed DB is absent in your worktree, read from the main-checkout absolute path (read-only).

## Budget
- **Model tier (required):** Sonnet. Escalate only if the residual construction proves genuinely ambiguous.
- Compute: local analysis only; no long detached training. Keep it to a day's worth of analysis.

## Stop Conditions
Stop and return when: the screen produces a clear signed correlation verdict (positive OR null) with CIs; OR you'd need to change production code / write a DB / run new physics fits to proceed (out of scope — return and say so); OR you need context this order doesn't cover. Asking up is always sanctioned.

## Return Shape
Write `.agent-work/cmdr-7a-residual-screen/RESULT.md` BEFORE going idle. Include: verdict (`signal` / `null` / `inconclusive`) with the correlation statistic(s) + confidence intervals per axis (lateral-grip, drag) and per hold-out (2025, 2026-to-date); the exact as-of-round construction used; the constructor-vocab mapping + dropped-row counts; the evo-residual definition and which backtest produced it; a plain-English go/no-go recommendation for Wave 8; the `verify_worktree_isolation.py --here` output; and any triage candidates. Keep scratch code in the worktree; do not commit large data.
