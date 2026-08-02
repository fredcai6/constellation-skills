# Crew Handoff — G5 Implementer

## Role: implementer | Gate: G5 — Full gold retrain + promotion + docs

## Task
Final gate: full gold cycle with sigma calibration enabled, baseline comparison, artifact promotion, docs.

### Steps
1. **Update `configs/evo/gold_defaults.toml`**: Set `lambda_sigma_nll = 1.0` and update comments (remove "post-hoc only" language). target_mode already retro_delta.

2. **Run full gold cycle**:
   ```bash
   py -m src.evo_predictor gold-cycle --config configs/evo/gold_defaults.toml
   ```
   This trains all 12 modules + backtests + manifest. LONG RUN — use adequate timeout. If gold mode blocks, use research/smoke profile copy with same lambda but document why.

3. **Brier-primary comparison** vs current promoted baseline:
   - Baseline: existing reports in `reports/evo/` (e.g. gold_cycle_260526_004033 or fusion_260530 from main merge)
   - Compare module-level Brier / pairwise_log_loss from new run summary vs baseline
   - Require no regression; report improvements

4. **Sigma metrics**: From new run uncertainty diagnostics — sigma_pi_trace dynamic range, corr(sigma_pi, accuracy) vs issue targets

5. **Promote artifacts** to `params/gold/` per repo artifact policy (module bundles, sampled_runtime_manifest if applicable)

6. **Docs**: Update `docs/architecture/packets/latent_power.md` and ADR 0008 (or docs/adr/) for retro-only path + sigma NLL calibration. Update stale `gold_report_schema` field notes if needed.

7. **Evidence**: Write `.agent-work/issue-142-sigma-calibration/evidence/g5-gold.md` with comparison table, promotion paths, commands.

### Verification
At minimum after gold run:
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q
```

### Exclusions
- Do not push unless explicitly needed

### Commit
Commit config + docs + promoted artifacts per artifact policy. Message: `feat(gold): retrain with sigma calibration NLL (issue #142 g5)`

Return IMPLEMENTER_RESULT with metrics comparison and promotion paths.
