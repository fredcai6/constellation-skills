# Implementer Handoff

## Gate
g2 — Gold-cycle config + CLI plumbing (NO parallelism this gate)

## Task
Make `utilization` a first-class gold-cycle config field and add a `--utilization` CLI override that
works even in gold mode as a non-policy hint. No fan-out / no behavior change to the cycle yet.

## Protected Intent
`--utilization` is a runtime hint that does NOT change results, so it must be allowed in gold mode
(which otherwise rejects mutating overrides) AND must never appear in `applied_overrides` (provenance
records only result-affecting overrides). Gold-mode leakage rules and existing config validation must
remain intact.

## Test Mode
TDD required. Add config tests first (red), then implement to green.

## Close Criteria
- `GoldCycleRuntimeConfig` (in `src/evo_predictor/gold_cycle/config.py`) gains `utilization: str`.
- `_parse_and_validate` reads `runtime.utilization` as **OPTIONAL, defaulting to "balanced"**, and validates it
  against `UTILIZATION_LEVELS` imported from `src.utils.utilization` (invalid → `GoldCycleConfigError` naming
  field, expected set, actual). (Optional-with-default avoids breaking existing TOML profiles that lack the
  field; this is a non-policy hint so a default is acceptable — Commander-decided.)
- `_config_to_raw` emits `runtime.utilization`.
- `_apply_overrides_to_raw` section_map maps `utilization -> "runtime"` (so research/smoke `--utilization` flows
  through the normal override path too).
- `configs/evo/gold_defaults.toml` sets `[runtime] utilization = "balanced"` explicitly (with a short comment).
- `run.py` gold-cycle subparser gains `--utilization`, choices `("background","balanced","max")`, default `None`.
- `cmd_gold_cycle` applies the hint DIRECTLY post-load and OUTSIDE `apply_cli_overrides`: e.g. a small helper
  `_apply_utilization_hint(config, args)` that sets `config.runtime.utilization = args.utilization` only when
  `args.utilization is not None`. It must NOT go through `apply_cli_overrides` (so gold mode accepts it and it
  stays out of `applied_overrides`). Factor it as a tiny testable helper.
- Tests prove: valid levels accepted; invalid rejected with a field-naming message; default is `balanced`;
  `_config_to_raw` round-trips utilization; the hint helper sets utilization in gold mode WITHOUT raising and
  WITHOUT populating `applied_overrides`; research/smoke `--utilization` still works via the override path.

## Allowed Scope
- `src/evo_predictor/gold_cycle/config.py`
- `configs/evo/gold_defaults.toml`
- `src/evo_predictor/run.py` (gold-cycle subparser + cmd_gold_cycle hint application only)
- `tests/unit/evo_predictor/test_gold_cycle_config.py` (and a focused test for the hint helper)

## Specific Exclusions
- NO changes to `runner.py` / `runner_support.py` / any parallelization (that is G3).
- NO `utilization` in the gold report schema / `run_config` / `build_run_config` (Commander-decided: runtime-only hint).
- Do NOT add a CLI default other than `None` (the TOML/schema default is the single source of truth).

## Constraints
- Use `py`, not `python`.
- Reuse `UTILIZATION_LEVELS` from `src.utils.utilization` — do not redefine the level set.
- Validation messages name field, expectation, actual.
- One canonical path; no dual-format acceptance.
- Run `py -m src.utils.simplification_limits --paths <touched>`.

## Required Evidence
- Red-then-green noted.
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py -q` → pass (paste tail).
- `py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle/config.py src/evo_predictor/run.py tests/unit/evo_predictor/test_gold_cycle_config.py` → clean.
- Show the gold-mode hint test: applying `--utilization max` in gold mode does not raise and `applied_overrides` stays empty.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py -q
py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle/config.py src/evo_predictor/run.py tests/unit/evo_predictor/test_gold_cycle_config.py
```

## Suggested Model Tier
simple bounded — well-specified config/CLI plumbing; the only subtlety is the apply-outside-overrides helper.

## Authority
Decided (do not re-litigate): utilization is OPTIONAL in the schema defaulting to "balanced"; gold_defaults sets
it explicitly; the CLI hint applies post-load outside apply_cli_overrides and stays out of applied_overrides;
no report-schema change. You may choose the helper's exact shape and test structure.

## Stop Conditions
Stop and return if allowed scope must be exceeded, an exclusion must be touched, evidence cannot be produced,
or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (command tails),
assumptions, stop conditions hit, out-of-scope observations.
