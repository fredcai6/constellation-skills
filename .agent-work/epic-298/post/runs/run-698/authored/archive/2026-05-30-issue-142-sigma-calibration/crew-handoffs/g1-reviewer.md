# Crew Handoff

## Role
reviewer

## Assigned Gate
G1 — Cleanup: retire triangle_loss + dead bce path

## Suggested Model Tier
simple bounded (mechanical cleanup, clear close criteria)

## Test Mode
inspection-only + re-run verification command

## Task
Independently verify G1 implementer commit `ee6d501` meets gate close criteria.

## Intent Protected
- retro_delta is sole training path
- symmetry_loss preserved
- batch.outcome preserved for eval
- No G2 scope creep (sigma calibration not added)
- ADR 0001 boundary respected

## Close Criteria (from execute.json g1)
1. triangle_loss + dead bce path removed; symmetry kept; retro_delta unconditional
2. `py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q` green
3. No residual bce/triangle references in src (batch.outcome eval OK)
4. Verdict APPROVE or BLOCK with findings

## Authority
execute.json g1 postconditions

## Allowed Scope
Read-only review of commit `ee6d501` diff and re-run verification

## Specific Exclusions
Do not implement fixes — return BLOCK with findings if issues found

## Required Context
- Handoff: `.agent-work/issue-142-sigma-calibration/crew-handoffs/g1-implementer.md`
- Commit: `ee6d501`
- Implementer result summary in prior turn

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q
```

Also grep:
```bash
py -c "import pathlib; p=pathlib.Path('src/latent_power'); print('triangle_loss', any('triangle_loss' in f.read_text(encoding='utf-8') for f in p.rglob('*.py'))); print('bce branch', any('target_mode == \"bce\"' in f.read_text(encoding='utf-8') for f in p.rglob('*.py')))"
```

## Return Format
REVIEW_RESULT: verdict APPROVE|BLOCK, findings list, checks performed
