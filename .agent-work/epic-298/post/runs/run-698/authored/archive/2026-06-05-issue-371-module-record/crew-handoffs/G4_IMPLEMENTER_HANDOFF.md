# Implementer Handoff

## Gate
`g4`

## Task
Bounded real-data integration test + flag-on smoke gold-cycle evidence run.

1. **`tests/integration/test_module_record_emit.py`** — in the mold of
   `tests/integration/test_utilization_determinism.py` (same skip guard style: requires
   `data/f1_data_<year>.db` for the chosen years + `params/retro_truth`; skips cleanly
   where absent — note both ARE present in this checkout, so it must RUN here):
   - Train ONE cheap module once (`driver_quali_power_from_recent_history` — no
     compound-prior dependency), bounded: train_years `[2022, 2023]`, eval 2024,
     `max_rounds_per_year=1`, 2 epochs, seed 0, threads 1. Reuse the production builders
     (`build_main_train_backtest_jobs` + `run_train_backtest`) or the train command
     directly — whichever is leaner; the determinism test shows both.
   - Run the backtest command twice against the SAME bundle into two output paths:
     once flag off, once with `--emit-module-record` (drive `cmd_backtest_latent_power_module`
     via its args Namespace, as production does).
   - Assert: the two backtest JSON files are **byte-identical** after normalizing ONLY the
     embedded `bundle_manifest_path` if the two invocations share it (same bundle ⇒ likely
     no normalization needed — prefer raw byte equality, fall back to the determinism
     test's normalizer with a comment if a volatile field genuinely differs).
   - Assert: `.record.npz` + `.record.json` exist ONLY next to the flag-on output; none
     next to the flag-off output.
   - Assert: `load_module_record` round-trips the real flag-on record — every index event
     has matching arrays, `pi` length == n_entities, `sigma_pi` shape (n,n), and the index
     event count equals the backtest JSON's `event_count`.
2. **Evidence smoke run** (not a committed test): write
   `.agent-work/issue-371-module-record/evidence/g4_smoke_config.toml` — `mode = "smoke"`,
   train_years `[2022, 2023]`, eval_year 2024, `emit_fusion_train_rows =
   "leave_one_season_out"`, `emit_module_record = true`, bounded training budgets (2
   epochs, seed 0), `output_dir`/`report_dir` INSIDE
   `.agent-work/issue-371-module-record/evidence/` — then run:
   `py -m src.evo_predictor.run gold-cycle --config <that file> --max-rounds-per-year 1`.
   Capture into `evidence/g4-smoke-run.md`: the exact command, a recursive listing of every
   `*.record.npz`/`*.record.json` under the output dir grouped by mains `backtests/`,
   `loso_folds/heldout_*/backtests/`, and `uncertainty_calibration_fit/backtests/`, plus a
   short loaded-record printout (one mains module: event count, first event_id, pi shape,
   sigma_pi shape) proving a real record loads. Note the wall-clock duration.

## Protected Intent
- The integration test must not weaken G1-G3 guarantees (no tolerance-based comparisons of
  the JSON bytes; byte equality is the point).
- The smoke run writes NOTHING outside the evidence dir (no `outputs/evo_runs`,
  no `reports/evo` pollution).
- `details.json` from the smoke run contains no `emit_module_record` key (spot-check it in
  the evidence file — guards the no-echo decision end-to-end).

## Test Mode
Test-after acceptable for the integration test scaffolding (the units under test landed in
G1-G3 test-led); the test itself IS the verification artifact.

## Close Criteria
- `py -m pytest tests/integration/test_module_record_emit.py -q` passes locally (runs, not
  skips — data is present).
- `evidence/g4-smoke-run.md` exists with command, duration, grouped `.record.*` listing
  showing all three dir families populated (12 modules mains; folds × modules for LOSO;
  calibration set), loaded-record printout, and the details.json no-echo spot-check.
- `py -m src.utils.simplification_limits --paths tests/integration/test_module_record_emit.py` passes (strict).

## Allowed Scope
- `tests/integration/test_module_record_emit.py` (new)
- `.agent-work/issue-371-module-record/evidence/` (config + evidence artifacts)

## Specific Exclusions
- ANY `src/` or `configs/` or `docs/` file (G1-G3 landed them; if the run exposes a defect,
  STOP and return — the Commander decides rework, you do not patch src in this gate)
- Committed test fixtures involving large generated artifacts

## Constraints
- `py` not `python`
- Bounded budgets exactly as specified (this is evidence, not science)
- The smoke run is long (likely 15-45 min); run it in the foreground of your session and
  report honestly if it exceeds ~60 min (stop condition)

## Required Evidence
- pytest output for the new integration test
- `evidence/g4-smoke-run.md` (as above)
- simplification_limits output

## Verification Commands
```bash
py -m pytest tests/integration/test_module_record_emit.py -q
py -m src.utils.simplification_limits --paths tests/integration/test_module_record_emit.py
```

## Suggested Model Tier
simple bounded — assembly of established patterns; the judgment calls are already made.

## Authority
Decided (Commander + user): test shape, module choice, bounded budgets, evidence-run TOML
location/content, no-src-changes rule. You must NOT decide alone: loosening byte-equality,
changing budgets upward materially, touching src.

## Stop Conditions
Stop and return if: the flag-off/flag-on JSONs differ (defect — do not normalize it away),
any `.record.*` appears in a flag-off context, the smoke run errors or exceeds ~60 min,
allowed scope must be exceeded, or required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations.

## Working agreement
Work from repo root `C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record`.
Do not `cd` elsewhere; `.agent-work/issue-371-module-record/evidence/` is your only
allowed write location outside tests/. Commit nothing — the Commander owns commits.
