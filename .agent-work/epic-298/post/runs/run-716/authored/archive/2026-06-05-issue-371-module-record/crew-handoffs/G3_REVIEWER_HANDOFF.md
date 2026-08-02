# Reviewer Handoff

## Gate
`g3`

## What Was Implemented
emit_module_record on GoldCycleRuntimeConfig (optional-key parse default False, GoldCycleConfigError on non-bool, _config_to_raw round-trip, override section mapping); --emit-module-record CLI override on the gold-cycle parser + override key tuple; threading into all three backtest template builders (mains build_main_train_backtest_jobs, LOSO build_loso_train_backtest_jobs, calibration build_calibration_train_backtest_jobs); gold_defaults.toml [runtime] entry; new docs/evo/module_backtest_record.md contract page + one-line mention in docs/evo/analysis_refresh.md. 15 new tests (11 config + 4 builder).

## How to Inspect the Diff
Repo root: C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record
- `git diff` (uncommitted vs HEAD 42877a6 — G1/G2 are already committed; everything uncommitted is G3)
- New untracked file: docs/evo/module_backtest_record.md — read in full.

## Task Statement
Original implementer handoff (read it): .agent-work/issue-371-module-record/crew-handoffs/G3_IMPLEMENTER_HANDOFF.md
Frozen intent: .agent-work/issue-371-module-record/PROBLEM_STATEMENT.md

## Close Criteria (each is a review check)
- Config: absent key ⇒ False (existing TOMLs load unchanged); true parses; non-bool ("yes", 1 — note bool is an int subclass in Python, check how the guard treats literal 1 vs True) ⇒ GoldCycleConfigError naming field/expected/actual; override applies in smoke/research, rejected in gold mode via existing apply_cli_overrides (no special-case code added); _config_to_raw round-trips.
- Threading: all three builders put emit_module_record into the backtest Namespace from config.runtime; mains tested both False and True; LOSO and calibration at least True. Verify the Namespace key matches EXACTLY what cmd_backtest_latent_power_module reads (getattr(args, "emit_module_record", False)) — a typo here silently no-ops the whole feature for gold-cycle runs.
- Byte-identity guard: build_run_config / reports.py / gold_report_schema.py untouched (git diff must not contain them); a test asserts no emit_module_record key in the run_config/details payload.
- gold_defaults.toml: [runtime] emit_module_record = false with comment; smoke_defaults.toml and fusion_calibration_loso.toml untouched.
- Docs (apply docs evidence rules): docs/evo/module_backtest_record.md must describe the G2 contract AS IMPLEMENTED — verify claims against src/evo_predictor/module_record.py and run.py line by line (sidecar naming, ordinal ev0000__* keys, index fields incl. format_version/has_* flags, reuse-guard semantics, emit-without-output error, dtype preservation note incl. outcome float32, all-or-nothing fail-fast, non-committed artifact status, #370 forward-compat note). Commands shown must use `py` and actually be valid. Check Last verified convention against sibling pages.
- DOCS JUDGMENT CALL: the handoff told the implementer to link from docs/evo/gold_module_training_cycle.md — that file does not exist (handoff error). The implementer linked from docs/evo/analysis_refresh.md instead. Assess against docs/DOCUMENTATION.md rules: is analysis_refresh.md the right/sufficient home for the link (it carries the gold-cycle config table)? Should docs/evo/training_process.md also mention it? Render a verdict on link placement; a missing-but-warranted second link is a note or rework item per your judgment of the doc rules, not automatically a BLOCK.
- Scope: ONLY config.py/runner.py/runner_support.py/run.py (gold-cycle parser + override tuple)/gold_defaults.toml/the two docs/the test files. Exclusions untouched: module_record.py, backtest command body, build_run_config/reports.py/gold_report_schema.py, evaluate_labeled_batches, smoke/fusion TOMLs.
- Focused evo suite green (expect ~1258 passed); simplification PASS on each touched file, zero new dir-wide violations.

## Constraints the Implementation Must Respect
- Existing override/validation idioms only (compare to utilization handling side by side); `py` not `python`; docs single-job rule.

## Evidence Produced (verify, don't trust)
- 110 targeted, 1258 full suite, PASS (7 files checked). Re-run yourself:
  - py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_parallel_jobs.py -q
  - py -m pytest tests/unit/evo_predictor/ -q
  - py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner.py src/evo_predictor/gold_cycle/runner_support.py src/evo_predictor/run.py configs/evo docs/evo (adjust to files if dirs unsupported)

## Suggested Model Tier
simple bounded — mechanical threading; docs accuracy is the part needing care.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.

## Working agreement
Work from repo root C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record. Read-only on src/ and docs/; you may run tests/commands. Do not modify code; do not commit.
