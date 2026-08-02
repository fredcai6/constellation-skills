# Reviewer Handoff

## Gate
g2 — Gold-cycle config + CLI plumbing (NO parallelism)

## What Was Implemented
`utilization` added to GoldCycleRuntimeConfig (optional, default "balanced", validated against
UTILIZATION_LEVELS from src.utils.utilization); wired into _config_to_raw and the override section_map;
`[runtime] utilization = "balanced"` in gold_defaults.toml; `--utilization` on the gold-cycle subparser applied
via `_apply_utilization_hint` post-load, OUTSIDE apply_cli_overrides. 8 new config tests; TDD.

## How to Inspect the Diff
- `git diff -- src/evo_predictor/gold_cycle/config.py src/evo_predictor/run.py configs/evo/gold_defaults.toml tests/unit/evo_predictor/test_gold_cycle_config.py`
- `git status --porcelain` to confirm only those four files changed (ignore `.agent-work/`).
Full implementer result: `.agent-work/issue-356-utilization-knob/crew-handoffs/g2-implementer-result.md`.

## Task Statement
Make utilization a first-class gold config field + add a `--utilization` CLI hint that works in gold mode
without being recorded as a result-affecting override. No parallelism, no report-schema change. Full handoff:
`.agent-work/issue-356-utilization-knob/crew-handoffs/g2-implementer-handoff.md`.

## Close Criteria (each a review check)
- Valid levels accepted; invalid → GoldCycleConfigError naming field, expected set, actual.
- Default is "balanced" when the field is absent (back-compat for profiles lacking it).
- `_config_to_raw` round-trips utilization; section_map maps utilization→runtime (research/smoke override path works).
- gold_defaults.toml sets utilization = "balanced" explicitly.
- `_apply_utilization_hint` sets config.runtime.utilization in GOLD mode WITHOUT raising and WITHOUT populating
  applied_overrides (verify the test asserts applied_overrides stays empty). CLI default is None.
- UTILIZATION_LEVELS is reused from src.utils.utilization (not redefined).

## Allowed Scope
config.py, run.py (gold-cycle subparser + cmd_gold_cycle hint only), gold_defaults.toml, test_gold_cycle_config.py.

## Specific Exclusions (flag if touched)
No runner.py/runner_support.py/parallelism. No utilization in gold report schema / run_config / build_run_config.

## Constraints the Implementation Must Respect (each a review check)
- Reuse UTILIZATION_LEVELS; validation messages name field/expectation/actual; one canonical path.
- **SIMPLIFICATION STANDARD FOR THIS GATE (Commander-set):** the bar is **"G2 introduces NO NEW simplification
  violation"**, NOT "the strict --paths check exits 0". Rationale: the repo's `--baseline` gate is already RED on
  main from two UNRELATED legacy mega-files (`_param_dataclasses.py` 1122, `html_reports/__init__.py` 1627), and
  the strict `--paths` failures on config.py/run.py are PRE-EXISTING functions (`_parse_and_validate`,
  `_build_parser`, and `cmd_train_latent_power_module` which G2 never touched — G2 edits cmd_gold_cycle).
  VERIFY: (a) G2 created no new file>1000 / function>100 / CC>20; (b) the 3 strict violations are pre-existing
  (cmd_train_latent_power_module is dispositive — unmodified by G2); (c) the pre-existing config.py/run.py
  function-length debt is captured as triage candidate tc1. Do NOT block solely because `--paths` exits non-zero
  on pre-existing debt. DO block if G2 introduced a genuinely new violation.

## Evidence Produced
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py -q` → 69 passed (re-run to confirm).
- Simplification facts above (re-run `--paths` and `git stash` if you want to confirm pre-existence; cmd_train
  being a strict violation while untouched is the clean proof).

## Suggested Model Tier
simple bounded — config/CLI plumbing; the nuance is the simplification standard and the gold-mode-hint assertion.

## Stop Conditions
Return BLOCK if: a NEW simplification violation was introduced, the gold-mode hint leaks into applied_overrides,
validation is missing/non-descriptive, scope was exceeded, or evidence is unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
