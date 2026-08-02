# Crew Handoff

## Role
reviewer

## Assigned Gate
G2 — Sigma-calibration core

## Commit
`816f6b6` — feat(latent_power): add detached sigma Student-t NLL + solve W-cap (issue #142 g2)

## Review criteria
1. `student_t_nll(..., detach_mu=True)` uses mu.detach() for residual; sigma attached
2. Term A (coupled student_t) unchanged — still trains mu
3. `lambda_sigma_nll=1.0` default, >=0 validation
4. `solve_sigma_floor=0.05` default, validated >= sigma_floor
5. LossBundle.sigma_nll field + training diagnostics
6. field_solve clamps sigma before W; training sigma_floor untouched
7. Tests: detach mu grads, lambda=0, lambda scaling, W-cap
8. No evo_predictor changes (G3 scope)
9. ADR 0001 respected

## Verification
```bash
py -m pytest tests/unit/latent_power/test_modules.py tests/unit/latent_power/test_config.py tests/unit/latent_power/test_field_solve.py tests/unit/latent_power/test_network.py -q
```

Return REVIEW_RESULT: APPROVE or BLOCK
