# Crew Handoff

## Role
reviewer

## Assigned Gate
G1 — remove `target_mode` end-to-end + gold report schema 4→5 (issue #303)

## Suggested Model Tier
stronger broad — verify a multi-file removal + schema bump + scope expansions for correctness and hidden behavior change

## Test Mode
inspection + command verification (re-run the close-criteria commands independently)

## Task
Independently verify the G1 implementation is a clean, complete, behavior-preserving removal of the `target_mode` concept with a correct single schema bump.

## Intent Protected
- No training-math change (term A Student-t, detached term B, symmetry, reg, solve_sigma_floor all numerically identical).
- One canonical path: no residual mode field/alias/fallback.
- `latent_power` must not import `evo_predictor` (ADR 0001).
- Report producer + committed consumers + schema doc move together.

## Close Criteria (verdict APPROVE requires all)
1. `py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py tests/integration/test_retro_delta_smoke.py -q` → exit 0.
2. `rg "target_mode|ALLOWED_TARGET_MODES|VALID_TARGET_MODES" src` → no matches.
3. `REPORT_SCHEMA_VERSION == 5`.
4. The diff makes NO change to loss/training numeric behavior (verify by reading `modules.loss_from_pairwise`, `losses.py` usage, `training.py` — only the `target_mode` echo/branch removed; the `target_mu is None` guard preserved with a reworded message).
5. Schema bump is coherent: bump is 4→5 on the gold REPORT version only (NOT the gold config input `schema_version`/`SUPPORTED_SCHEMA_VERSIONS`); schema doc regenerated from source; no committed consumer pins an old report version unhandled.

## Authority
User-approved plan, gate G1. Reviewer issues APPROVE or BLOCK with findings.

## Allowed Scope
Read-only review of the working-tree diff (`git diff`), plus running the verification commands. Do not edit source.

## Specific Exclusions
- Do not require the term-B nu knob (G3) or |r/sigma| extension (G2) — out of this gate.
- The 11 pre-existing broader-evo failures (`n_triangles_per_event` kwarg, missing `--retro-root`) are NOT introduced by G1 — confirm they are pre-existing (e.g. `git stash` or inspect that they reference removed-by-#142 surface, not G1 changes) and treat as an out-of-scope triage candidate, NOT a G1 blocker.

## Relevant Project Rules For This Gate
- Use `py`.
- One canonical execution path.
- Report schema producer + consumers + doc move together.
- Generated artifacts (schema doc) are regenerated from source, not hand-edited.

## Required Context
- Implementer result + plan: `.agent-work/sigma-calibration-followups/g1-implementer-plan.json`
- Handoff: `.agent-work/sigma-calibration-followups/crew-handoffs/g1-implementer.md`
- `git diff` (uncommitted working tree)

## Project Mechanics For This Gate
Do not commit. Return a verdict only.

## Required Evidence
- Re-run of close-criteria commands (paste output).
- A read-level confirmation that training math is unchanged.
- A determination on whether the implementer's scope expansions (editing `configs/evo/*.toml`, regenerating the schema markdown) are justified and safe.
- Confirmation the 11 broader-evo failures are pre-existing.

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py tests/integration/test_retro_delta_smoke.py -q
rg "target_mode|ALLOWED_TARGET_MODES|VALID_TARGET_MODES" src
git diff --stat
```

## Stop Conditions
Return BLOCK (not stop) if any close criterion fails or a hidden behavior change is found. Stop and report if you cannot run the verification commands.

## Return Format
`REVIEW_RESULT`: verdict APPROVE|BLOCK, per-check pass/fail with findings, any out-of-scope triage candidates, and the verification command outputs.
