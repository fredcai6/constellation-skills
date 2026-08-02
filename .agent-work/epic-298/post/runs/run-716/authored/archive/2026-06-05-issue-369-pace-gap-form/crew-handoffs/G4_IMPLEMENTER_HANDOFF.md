# Implementer Handoff

## Gate
g4 — A/B evidence (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## Task
Evaluation run, minimal-to-zero code. Produce the A/B evidence that closes issue #369's acceptance section: does the pace-gap encoding enrich the variance/uncertainty channel, with no ordering regression?

**Arms (per module: `driver_quali_power_from_recent_history`, `constructor_quali_power_from_recent_history`):**
- **Control (primary)**: the promoted gold report's per-module eval metrics — `reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json` / `.details.json`, plus per-module uncertainty material in `reports/evo/unc_diag_260530_152746_2018thru2024.json` and `params/gold/uncertainty_calibration/unc_cal_260530_152746_2018thru2024.json`. Extract the recorded run_config (epochs/seed/lr/etc.) — this defines the training params the treatment must replicate.
- **Treatment**: train both modules on THIS branch with `--recent-history-form-encoding quali_pace_gap`, canonical split (`--train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025`), gold-default params replicated from the promoted run_config (gold defaults: epochs 25, seed 0, retro_root `params/retro_truth`; pull the rest — lr, optimizer, weight_decay, early-stop, hidden_dim, dropout, lambda_sigma_nll, solve_sigma_floor, student_t_nu_sigma — from the promoted report / `configs/evo/gold_defaults.toml` / `runner_support._module_train_args`, and SAY which source each came from). Then backtest each trained bundle on 2025 with the same flag.
- **Comparability sanity arm (cheap, also run)**: retrain the same two modules on THIS branch with the DEFAULT encoding (same params/seed) and backtest. Purpose: executable proof the promoted control numbers are still reproducible on this branch (default path is supposed to be bit-identical; training is seeded). If fresh-v1 ≈ promoted (exact or within float noise) the promoted numbers stand as control; if they DIVERGE, that is a finding to report prominently — do not paper over it.

CLI shape (read `--help` for both subcommands first):
```bash
py -m src.evo_predictor.run train-latent-power-module --module <name> --train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025 --retro-root params/retro_truth --db-root <per --help/db layout: per-year data/f1_data_<year>.db> --seed 0 --epochs 25 [... replicate remaining gold params ...] --recent-history-form-encoding quali_pace_gap --artifact-root outputs/evo_runs --run-name <descriptive>
py -m src.evo_predictor.run backtest-latent-power-module ... (read --help; same encoding flag)
```

**Metrics to tabulate per module × arm** (issue's acceptance — variance channel is the claim, ordering is the no-regression guard):
- `corr_sigma_pi_trace_vs_rank_mae`, `corr_sigma_pi_trace_vs_nll` — the variance claim under test. Find where these are computed for the promoted report (gold cycle uncertainty-calibration path; check `unc_cal_*.json` / `gold_module_cycle.py`) and compute them for the treatment arm by REUSING the same functions over your run outputs — import and call the existing code; do NOT reimplement the math. If the standalone backtest output lacks an input that computation needs, say so and surface the gap rather than approximating silently.
- `rank_mae_vs_actual`, `pairwise_sign_accuracy`, `pairwise_nll_skill` (each with floor/skill where the report provides them) — expected ~flat per the issue's probe.
- Availability/missingness diagnostics: pace-gap availability vs position availability on the eval year (the adapters' availability features / batch event diagnostics carry this; report mean availability_fraction or the closest first-class diagnostic both arms expose, plus DNS/no-valid-lap counts if visible).

**Deliverable**: `.agent-work/issue-369-pace-gap-form/evidence/ab_comparison.md` with:
1. Arms table per module (control-promoted, control-fresh-v1, treatment-v2) × the metrics above.
2. Config-comparability note: every param matched/mismatched between promoted run_config and your runs; fresh-v1 vs promoted reproduction status.
3. Availability comparison + what changed in missingness semantics (DNS → missing not slowest).
4. A sober verdict paragraph: what the variance-channel correlations show (better σ↔error alignment or not), whether ordering regressed, explicitly NOT overselling (the issue predicts ~flat ordering; the variance signal is the open question). State n (events scored) alongside any correlation — small-n insignificance is a finding, not a failure.
5. Provenance appendix: run names/paths under `outputs/evo_runs/`, exact commands used, bundle feature_schema_version strings observed (treatment bundles must record `...v2` — confirm and state it; this also exercises the G3 consistency seam).

## Protected Intent
- This is EVIDENCE, not a promotion: no gold-cycle run, no writes to `params/gold/`, no manifest changes, no default flips, nothing committed under `reports/` or `outputs/` (generated artifacts stay out of git per artifact policy).
- Metric provenance: every number in the doc traceable to a file under `outputs/evo_runs/` or the promoted report — cite the source path next to each table.
- No silent approximation: if a control metric has no treatment-side equivalent computable through existing code, the gap is reported, not bridged with ad-hoc math.

## Test Mode
inspection-only — evaluation run; no production code changes expected. (If a tiny harness script helps, put it under the work area `.agent-work/issue-369-pace-gap-form/evidence/`, not `src/` or `scripts/`.)

## Close Criteria
- Both treatment trainings + backtests completed on the canonical split with the flag on; bundles record the v2 schema.
- Fresh-v1 sanity arm completed and reproduction status vs promoted stated.
- `ab_comparison.md` exists with all five sections, every metric sourced.
- No repo file changed (git status clean apart from the work area and untracked outputs/).

## Allowed Scope
- Running `py -m src.evo_predictor.run ...` commands; reading promoted reports/configs; writing under `outputs/evo_runs/` (via the CLI) and `.agent-work/issue-369-pace-gap-form/evidence/`.
- Small read-only analysis snippets (e.g. `py -c` or a script in the evidence dir) that import existing functions to compute treatment-arm metrics.

## Specific Exclusions
- ANY edit under `src/`, `tests/`, `configs/`, `docs/`, `scripts/`, `params/`, `reports/` — if the run reveals a bug in G1–G3 code, STOP and return with the failure details; the commander decides.
- No FastF1 calls; DB only (the CLI does this already).

## Constraints
- `py` not `python`. Long runs: run commands sequentially and capture tails; trainings are small MLPs over recent-history features (expect minutes each, not hours — if a training appears hung >30 min, stop and report).
- Seed 0 everywhere; identical params across arms except the encoding flag.

## Required Evidence
- The ab_comparison.md itself + verbatim command list + tail of each training/backtest log showing completion.

## Verification Commands
```bash
py -c "import pathlib,sys; p=pathlib.Path('.agent-work/issue-369-pace-gap-form/evidence/ab_comparison.md'); sys.exit(0 if p.exists() and p.stat().st_size>500 else 1)"
git status --short
```

## Suggested Model Tier
stronger-leaning bounded — methodical multi-step evaluation; metric-provenance discipline matters more than cleverness.

## Authority
Human-confirmed problem statement + frozen plan. You may choose run names, table layout, and which existing function to import for the correlation metrics (documented). You must NOT decide alone: changing any training param away from gold defaults (beyond what replication requires), bridging missing metrics with new math, touching excluded paths.

## Stop Conditions
Stop and return if: a G1–G3 defect surfaces (training/backtest fails, schema mismatch fires wrongly, features missing), a control metric cannot be honestly reproduced for the treatment arm, any excluded path would need editing, or a training hangs.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, commands run, evidence produced (path + section list), reproduction status of fresh-v1 vs promoted, headline A/B numbers, assumptions, stop conditions hit, out-of-scope observations.
