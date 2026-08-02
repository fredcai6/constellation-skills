# Crew Handoff

## Role
implementer

## Assigned Gate
G2 — Sigma-calibration core: detached Student-t NLL term + lambda knob + solve-side W-cap

## Suggested Model Tier
stronger broad/ambiguous (loss math, detach correctness, field_solve numerics)

## Test Mode
TDD required for new behavior (term B, W-cap, config knobs)

## Task
In `src/latent_power` only, implement sigma calibration per interrogation decisions:

1. **Detached Student-t NLL (term B):** Add `detach_mu` support to `student_t_nll` (or thin wrapper) — residual uses `pairwise.mu.detach()`, sigma stays attached. Shared `config.student_t_nu`.

2. **Config:** Add `lambda_sigma_nll: float = 1.0` (>= 0 validation). Add `solve_sigma_floor: float = 0.05` (validated > 0 and >= sigma_floor).

3. **loss_from_pairwise:** Add `sigma_nll = lambda_sigma_nll * detached_student_t_nll(...)`. Include in total. Remove any leftover tri references if still present.

4. **LossBundle:** Add `sigma_nll` field (scalar tensor). Update training diagnostics JSONL to include it.

5. **field_solve.py:** Before `W = 1/sigma**2`, clamp: `sigma_for_solve = torch.clamp(sigma, min=config.solve_sigma_floor)`. Training sigma_floor (1e-3) untouched on network output.

## Intent Protected
- Mean (mu) objective unchanged — B MUST detach mu
- Student-t heavy-tail robustness preserved (same nu, same functional form)
- latent_power must NOT import evo_predictor (ADR 0001)
- Tunable weights in config, not inline

## Close Criteria
```bash
py -m pytest tests/unit/latent_power/test_modules.py tests/unit/latent_power/test_config.py tests/unit/latent_power/test_field_solve.py tests/unit/latent_power/test_network.py -q
```

Tests must cover:
- B=0 at lambda_sigma_nll=0
- mu.grad unaffected by B (detach)
- sigma gradient scales with lambda
- LossBundle.sigma_nll present and finite
- config validation for both new knobs
- field_solve W-cap bounds W at large 1/sigma²

## Authority
execute.json g2 + interrogation consolidation

## Allowed Scope
- `src/latent_power/losses.py`, `modules.py`, `config.py`, `models.py`, `training.py`, `field_solve.py`
- `tests/unit/latent_power/test_modules.py`, `test_config.py`, `test_field_solve.py`, `test_network.py`, `test_losses.py`

## Specific Exclusions
- Do NOT touch evo_predictor (G3)
- Do NOT run gold retrain (G5)
- Do NOT remove target_mode field

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power/test_modules.py tests/unit/latent_power/test_config.py tests/unit/latent_power/test_field_solve.py tests/unit/latent_power/test_network.py -q
```

## Stop Conditions
Stop if detach implementation would change term A (coupled student_t) behavior.

## Return Format
IMPLEMENTER_RESULT: diff summary, test output, blockers
