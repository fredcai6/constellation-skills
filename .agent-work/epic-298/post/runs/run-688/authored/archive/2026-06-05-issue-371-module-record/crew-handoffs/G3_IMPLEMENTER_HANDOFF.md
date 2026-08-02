# Implementer Handoff

## Gate
`g3`

## Task
Gold-cycle config flag + threading to all backtest template builders + docs.

1. **`src/evo_predictor/gold_cycle/config.py`**:
   - `GoldCycleRuntimeConfig` gains `emit_module_record: bool = False`.
   - `_validate_runtime_section`: `emit_module_record = runtime_raw.get("emit_module_record", False)`
     — the `utilization` optional-key precedent (config.py:266). Reject non-bool with
     `GoldCycleConfigError` naming field, expected type, actual value. Existing TOMLs
     without the key must keep loading unchanged.
   - `_config_to_raw`: include it in the `"runtime"` dict (so CLI-override re-validation
     round-trips).
   - Override section mapping (the `"utilization": "runtime"`-style dict, config.py:~399-407):
     add `"emit_module_record": "runtime"`.
   - **Do NOT add it to `build_run_config`** (gold_cycle/reports.py:247) or anything that
     lands in details.json/summary — protected byte-identity decision.
2. **`src/evo_predictor/run.py`**:
   - `_add_gold_cycle_parser` (run.py:547): add `--emit-module-record`
     (`action="store_true"`, `default=None` — None means "not overridden", matching the
     other overrides).
   - `cmd_gold_cycle` (run.py:202): add `"emit_module_record"` to the override key tuple
     (run.py:205-212). Gold mode then auto-rejects it via `apply_cli_overrides` — no extra
     code.
3. **Threading** — pass `emit_module_record=config.runtime.emit_module_record` into the
   backtest `argparse.Namespace` templates in all three builders:
   - mains: `build_main_train_backtest_jobs` (gold_cycle/runner.py:143-151)
   - calibration: `build_calibration_train_backtest_jobs` (gold_cycle/runner_support.py:659-672)
   - LOSO: `build_loso_train_backtest_jobs` (gold_cycle/runner_support.py:778+; templates
     built near the `_iter_loso_units` consumption — follow the existing template shape)
4. **`configs/evo/gold_defaults.toml`**: `[runtime]` gains `emit_module_record = false`
   with a one-line comment (record sidecars for offline fusion experiments; see docs page).
   Do not touch `smoke_defaults.toml` or `fusion_calibration_loso.toml` (optional key).
5. **Docs**: new `docs/evo/module_backtest_record.md` documenting the record contract
   exactly as implemented in G2 (sidecar naming, ordinal npz keys + index mapping, index
   fields, flag + config key + CLI override, reuse-guard behavior, non-committed artifact
   status, forward-compat note referencing issue #370). Link it from
   `docs/evo/gold_module_training_cycle.md` and check `docs/evo/analysis_refresh.md`
   (mentions `emit_fusion_train_rows`) for a natural one-line mention. Keep each doc's
   single job; commands belong in the new page only.

## Protected Intent
- Flag-off gold cycle produces byte-identical artifacts: the new key must NOT appear in
  details.json, summary JSON, or run_config echoes.
- Existing config files load unchanged without the key.
- Gold mode rejects the CLI override (existing `apply_cli_overrides` behavior — verify with
  a test, add no special code).

## Test Mode
Test-led (TDD). Extend the existing config/builder test files.

## Close Criteria
- Config: absent key ⇒ False; `emit_module_record = true` parses; non-bool (e.g. `"yes"`,
  `1`) ⇒ `GoldCycleConfigError` naming field/expected/actual; override applies in
  smoke/research and is rejected in gold mode; `_config_to_raw` round-trips the value.
- Builders: all three template builders produce Namespaces carrying the configured value
  (assert both False and True cases for mains; True case at least once for LOSO and
  calibration).
- run_config/details guard: a test asserts `build_run_config` output (or the details
  payload builder it feeds) contains no `emit_module_record` key.
- gold_defaults.toml still validates (existing config-load test or a new assertion).
- Docs build/check: the new page exists, the gold-cycle doc links it, references resolve
  (paths/commands valid per docs evidence rules; use `py` in any commands shown).
- Focused evo suite green: `py -m pytest tests/unit/evo_predictor/ -q`.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner.py src/evo_predictor/gold_cycle/runner_support.py src/evo_predictor/run.py` passes (strict).

## Allowed Scope
- `src/evo_predictor/gold_cycle/config.py`, `runner.py`, `runner_support.py`
- `src/evo_predictor/run.py` (gold-cycle parser + override tuple only)
- `configs/evo/gold_defaults.toml`
- `docs/evo/module_backtest_record.md` (new), `docs/evo/gold_module_training_cycle.md`,
  `docs/evo/analysis_refresh.md` (link/mention only)
- `tests/unit/evo_predictor/test_gold_cycle_config.py`, `test_gold_cycle_runner.py`,
  `test_gold_cycle_parallel_jobs.py` (or sibling test files as fits existing layout)

## Specific Exclusions
- `module_record.py` and the backtest command body (G2 — already landed; consume as-is)
- `build_run_config` / reports.py / gold_report_schema.py (must stay untouched)
- `evaluate_labeled_batches` (G1)
- smoke/fusion-calibration TOMLs

## Constraints
- `py` not `python`
- Match the existing override/validation idioms exactly (no new patterns)
- Docs describe current truth only; include `Last verified: 2026-06-05` if the doc family
  uses that convention (check sibling pages)

## Required Evidence
- Test output (config + builder tests, focused suite)
- simplification_limits output
- The docs diff summarized in IMPLEMENTER_RESULT

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_cycle_parallel_jobs.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle src/evo_predictor/run.py tests/unit/evo_predictor
```

## Suggested Model Tier
simple bounded — mechanical threading along researched, line-cited seams.

## Authority
Decided (Commander + user): optional-key parse with default False, no report echo,
uniform threading to all three builders, gold_defaults-only TOML edit, docs placement.
You must NOT decide alone: echoing the flag anywhere into reports, changing
`VALID_EMIT_MODES`/`emit_fusion_train_rows`, touching excluded files.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, the LOSO/calibration template builders
turn out not to flow through `cmd_backtest_latent_power_module` (re-verify before wiring),
required evidence cannot be produced, or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations.

## Working agreement
Work from repo root `C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record`.
Do not `cd` elsewhere; do not touch `.agent-work/` except to read this handoff and
PROBLEM_STATEMENT.md. Commit nothing — the Commander owns commits.
