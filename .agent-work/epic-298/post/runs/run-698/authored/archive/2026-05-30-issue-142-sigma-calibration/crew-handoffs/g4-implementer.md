# Crew Handoff — G4 Implementer

## Role: implementer | Gate: G4 — Smoke validation

## Task
Validate sigma calibration path end-to-end with evidence file.

### Required steps
1. Run `py -m pytest tests/integration/test_retro_delta_smoke.py -q` (must pass)

2. Run a smoke training script (create if needed under `.agent-work/issue-142-sigma-calibration/` or `scripts/`) that:
   - Trains with `lambda_sigma_nll=1.0`, `solve_sigma_floor=0.05` on synthetic OR real data if DB+retro available
   - Captures per-epoch or final: sigma min/median/max, fraction at solve_sigma_floor, sigma_nll loss component
   - Confirms no NaNs, loss decreases
   - If real DB unavailable, synthetic with target_mu is acceptable but document limitation

3. Write evidence to `.agent-work/issue-142-sigma-calibration/evidence/g4-smoke.md` with:
   - Commands run
   - Sigma distribution stats
   - Whether sigma varies (not stuck ~10-17 constant)
   - field_solve / W-cap sanity (max effective W)
   - Recommendation on solve_sigma_floor (keep 0.05 or adjust)

4. If real evo train path works (DB + retro_root present), optionally run one module via `py -m src.evo_predictor run train-latent-power-module` for 2-3 epochs — but synthetic is OK if data missing.

## Verification
```bash
py -m pytest tests/integration/test_retro_delta_smoke.py -q
```

## Exclusions
- No full gold retrain (G5)
- Do not promote params/gold

## Commit
Only commit if you add a reusable smoke script to scripts/ — otherwise evidence file only (untracked .agent-work is fine)

Return IMPLEMENTER_RESULT with evidence summary.
