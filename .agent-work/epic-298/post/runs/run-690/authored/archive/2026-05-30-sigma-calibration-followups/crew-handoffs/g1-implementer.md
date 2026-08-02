# Crew Handoff

## Role
implementer

## Assigned Gate
G1 — remove the `target_mode` concept end-to-end + bump gold report schema 4→5 (issue #303)

## Suggested Model Tier
stronger broad/ambiguous — multi-file cleanup across `latent_power` + `evo_predictor` + tests + a report schema bump with consumers/doc

## Test Mode
test-after allowed (mechanical cleanup; run focused suites after edits). No training-math change is permitted.

## Task
Delete the vestigial `target_mode` field/concept. Post-#142 it is always `"retro_delta"`; it is dead dual-mode surface. Make `retro_delta` unconditional and remove the field everywhere, then bump the gold report schema to mark the run_config/diagnostics shape change.

Concretely:
1. **latent_power**
   - `src/latent_power/config.py`: remove `target_mode` field (line ~58), `ALLOWED_TARGET_MODES` (line ~24), and the `target_mode` validation block (lines ~162-165).
   - `src/latent_power/models.py`: remove `target_mode` from `LossBundle` (field ~204, `ALLOWED_TARGET_MODES` ~196/211, validation ~211-214). Keep the rest of `LossBundle` (incl. `sigma_nll`).
   - `src/latent_power/modules.py` (`loss_from_pairwise`, ~line 120-144): drop the `target_mode` local + branch; keep the `batch.target_mu is None` → `ValueError` guard (reword message to drop the `target_mode='retro_delta'` phrasing, keep it naming the missing field) and the unconditional Student-t term A + detached term B path. Do not pass `target_mode` into `LossBundle`.
   - `src/latent_power/training.py`: remove `target_mode` from the per-epoch diagnostics row (~155) and the `last_loss_payload` (~142). Keep all other diagnostics incl. the `r_over_sigma_p95/p99`/`sigma_mean` block (G2 extends it). Keep the two `required for target_mode='retro_delta'` messages' INTENT but reword to drop the dead mode name (they assert `target_mu` is required).
2. **evo_predictor**
   - `src/evo_predictor/run.py` (~246): drop the `target_mode="retro_delta"` kwarg when constructing the config.
   - `src/evo_predictor/gold_cycle/config.py`: remove the `target_mode` dataclass field (~44), `VALID_TARGET_MODES` + its validation (~159-162, ~216), and any `target_mode` entries in serialized/echoed dicts (~322, ~362).
   - `src/evo_predictor/gold_cycle/runner.py` (~575): drop `target_mode=config.training.target_mode` passthrough into module train args.
3. **Schema bump (single 4→5)**
   - `src/evo_predictor/gold_cycle/reports.py`: `REPORT_SCHEMA_VERSION = 4` → `5`.
   - First VERIFY whether the committed gold report `run_config` actually carries `target_mode` (audit: `build_run_config` did NOT; the `config.py` serialized dicts at ~322/~362 may feed a different echo). Remove it wherever it reaches a committed artifact.
   - `src/evo_predictor/gold_report_schema.py`: update `schema_version`/`report_schema_version` field interpretations to say v5; remove any `target_mode` field entry if one exists (grep found none at audit — confirm).
   - Update `docs/report_schemas/*` if such a doc exists for the gold report (none found at audit — confirm with a glob).
   - Add `5` to any consumer/reader that pins supported gold *report* versions. NOTE: the gold *config* input TOML `schema_version` (`SUPPORTED_SCHEMA_VERSIONS` in `gold_cycle/config.py`) is a SEPARATE version — do not change it.
4. **Tests**: update/remove `target_mode` assertions in `tests/unit/latent_power/{test_config,test_models,test_modules,test_training}.py`, `tests/unit/evo_predictor/{test_gold_cycle_config,test_gold_cycle_runner,test_gold_module_cycle}.py`, `tests/integration/test_retro_delta_smoke.py`. Add/keep a test asserting `REPORT_SCHEMA_VERSION == 5`.

## Intent Protected
- Training math unchanged (term A Student-t on mu+sigma, detached term B, symmetry, reg, `solve_sigma_floor`). This is pure dead-surface removal.
- `batch.outcome` stays (eval metrics use it).
- `latent_power` must not import `evo_predictor` (ADR 0001).
- One canonical path: no mode field, no alias, no fallback.

## Close Criteria
- `py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py tests/integration/test_retro_delta_smoke.py -q` → exit 0.
- `rg "target_mode|ALLOWED_TARGET_MODES|VALID_TARGET_MODES" src` → no matches.
- `REPORT_SCHEMA_VERSION == 5`.

## Authority
User-approved plan (Commander run `sigma-calibration-followups`, gate G1). Project rule: report producer + consumers + schema doc move together.

## Allowed Scope
The files listed above + their tests. A new ADR note is NOT in this gate (ADR 0008 update lands in G5).

## Specific Exclusions
- Do NOT change training loss math or any numeric default.
- Do NOT touch the gold *config* input `schema_version`/`SUPPORTED_SCHEMA_VERSIONS` (different contract).
- Do NOT add the term-B nu knob (G3) or `|r/sigma|` percentile extension (G2) here.
- Do NOT retrain or regenerate gold artifacts.
- Do NOT commit (Pilot handles commits after review).

## Relevant Project Rules For This Gate
- Use `py` for Python.
- Prefer one canonical execution path; no vestigial dual-mode branches.
- Validate inputs with messages naming field + expectation.
- Committed report schema changes update producers, committed consumers, and docs together.

## Required Context
- `src/latent_power/{config,models,modules,training}.py`
- `src/evo_predictor/run.py`, `src/evo_predictor/gold_cycle/{config,runner,reports}.py`, `src/evo_predictor/gold_report_schema.py`
- `docs/adr/0008-retro-delta-supervision.md` (single supervision path context)

## Project Mechanics For This Gate
Do not commit. Report diff + evidence back to Pilot.

## Required Evidence
- The two close-criteria commands' output (pytest exit 0; grep clean).
- A short note confirming whether the committed gold report carried `target_mode` and where it was removed.
- Confirmation `REPORT_SCHEMA_VERSION == 5`.

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py tests/integration/test_retro_delta_smoke.py -q
rg "target_mode|ALLOWED_TARGET_MODES|VALID_TARGET_MODES" src
```

## Stop Conditions
Stop and return if: removing `target_mode` forces a training-math change; a consumer outside the listed files pins the gold report version; the committed report schema change would cascade beyond the gold report; or any close-criteria command cannot reach green.

## Return Format
`IMPLEMENTER_RESULT`: diff summary (files + what changed), the two verification command outputs, the schema-carrier note, blockers, scope concerns, assumptions used.
