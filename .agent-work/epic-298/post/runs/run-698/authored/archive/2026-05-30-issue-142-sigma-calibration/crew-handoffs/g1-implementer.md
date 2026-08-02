# Crew Handoff

## Role
implementer

## Assigned Gate
G1 — Cleanup: retire triangle_loss + dead bce path

## Suggested Model Tier
stronger broad/ambiguous (multi-file cleanup across latent_power + evo_predictor + tests)

## Test Mode
test-after allowed (mechanical cleanup; run focused suites after edits)

## Task
Remove triangle_loss and the bce training path so retro_delta is the sole canonical training path. No new sigma-calibration behavior in this gate.

## Intent Protected
- Preserve symmetry_loss and regularization_loss
- Preserve batch.outcome (eval metrics still use it)
- Preserve Student-t heavy-tail robustness (do not touch student_t_nll yet)
- latent_power must not import evo_predictor (ADR 0001)
- One canonical path: retro_delta only

## Close Criteria
1. triangle_loss deleted; lambda_tri / n_triangles_per_event config plumbing removed
2. modules.loss_from_pairwise: supervised = student_t_nll unconditionally (requires target_mu)
3. bce removed from ALLOWED_TARGET_MODES everywhere; target_mode default = "retro_delta", only valid value
4. training.py: remove bce validation branches; always require target_mu
5. run.py: remove --target-mode bce choice; retro_root mandatory; always join retro labels
6. gold_cycle/config.py: VALID_TARGET_MODES = ("retro_delta",) only
7. LossBundle: remove tri field OR set tri to zero constant — prefer removing tri from LossBundle and training diagnostics if clean; if too invasive keep tri=0 stub — pilot prefers clean removal of tri from LossBundle + diagnostics
8. All affected unit tests updated/removed
9. Verification command passes

## Authority
Frozen gate plan: `.agent-work/issue-142-sigma-calibration/execute.json` g1 task

## Allowed Scope
- `src/latent_power/losses.py`, `modules.py`, `config.py`, `models.py`, `training.py`, `README.md`
- `src/evo_predictor/run.py`, `src/evo_predictor/gold_cycle/config.py`
- `tests/unit/latent_power/**`, `tests/unit/evo_predictor/test_gold_cycle_config.py`
- `tests/integration/test_retro_delta_smoke.py` if broken by default target_mode change

## Specific Exclusions
- Do NOT add lambda_sigma_nll, detached student-t term B, or solve-side W-cap (G2)
- Do NOT wire gold passthrough beyond target_mode pin (G3)
- Do NOT change committed gold report schema
- Do NOT remove target_mode field entirely (triage tc1)
- Do NOT touch params/gold artifacts

## Relevant Project Rules For This Gate
- Use `py` not `python`
- Test-led: run focused region tests before claiming done
- Prefer one canonical execution path

## Required Context
- `.agent-work/issue-142-sigma-calibration/execute.json` g1 imperative
- Branch: `codex/issue-142-sigma-calibration` (already merged main at f911c4d)

## Project Mechanics For This Gate
- Commit locally after verification passes (autonomous per ORCHESTRATOR_CONTEXT)
- Do not push

## Required Evidence
- Diff summary of files changed
- Output of verification command (full pass)
- Grep confirmation: no triangle_loss / bce training path in src/latent_power (batch.outcome eval usage OK)

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q
```

## Stop Conditions
Stop if LossBundle.tri removal cascades into G2 scope, or if gold report schema change seems required.

## Return Format
IMPLEMENTER_RESULT: diff summary, test output, grep evidence, blockers, assumptions
