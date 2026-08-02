# Student-t — Quali position-sigma calibration: is nu=4 appropriate for quali?

**Date:** 2026-06-02
**Experiment:** `scripts/quali_sigma_calibration.py`
**Report:** `reports/calibration/quali_sigma_calibration.json`

## Why

Phase 3 routed the QualiSimulator's Q3 probability through a Student-t CDF but
borrowed the project's aleatoric `nu_loss = 4`. Unlike the latent-power tasks, the
quali position `sigma` is a *heuristic* spread (`3.0 - quali_component/100·2.5`,
scaled by confidence) that had never been calibration-checked. Question: is `nu=4`
right for quali, and is the heuristic `sigma` even the right scale?

## Method

For every event in 2023-2025: build the `StrengthMatrix`, run
`setup_quali_simulation` to get per-driver `(expected_position, position_std_dev)`,
join the actual qualifying classification positions (by `round_num`), and score the
pooled `(mu, sigma, actual)` under the same sweep as the latent-power tasks
(Gaussian vs fixed-`nu` grid; coverage / PIT / best-`nu`). Also checked Q3-probability
reliability (mean predicted `P(pos<=10)` vs actual Q3 rate). The simulator is a
heuristic fed by rolling history, not a trained model, so all events are fair game.

## Results

| year | n | best ν@0.9 | t(4)@.5 | t(4)@.9 | t(4)@.95 | PIT var | r/σ p99 | Q3 pred vs actual |
|---|---|---|---|---|---|---|---|---|
| 2023 | 440 | 3.5 | 0.484 | 0.893 | 0.941 | 0.0816 | 5.90 | 0.450 vs 0.500 |
| 2024 | 479 | 2.5 | 0.474 | 0.860 | 0.937 | 0.0786 | 4.83 | 0.438 vs 0.503 |
| 2025 | 477 | 3.0 | 0.447 | 0.876 | 0.956 | 0.0885 | 4.09 | 0.459 vs 0.501 |
| **pooled** | **1396** | **3.0** | 0.468 | **0.876** | 0.945 | **0.0835** | 4.92 | — |

Pooled coverage@0.90 by ν: `{2.5: 0.918, 3.0: 0.900, 3.5: 0.884, 4.0: 0.876}`.

## Findings

1. **The heuristic σ is the right *scale*.** Pooled PIT variance 0.0835 ≈ the ideal
   0.0833, and 50%-coverage 0.468 ≈ 0.50. The old `3.0 - quali/100·2.5` heuristic,
   for all its crudeness, is not mis-scaled — reassuring, and it means the tail
   shape is the only thing to fix.

2. **ν=4 is too thin for quali.** t(4) under-covers at 0.90 (0.876) and the
   best-calibrating tail is **ν ≈ 3** (t(3) → 0.900, exactly nominal). Qualifying
   outcomes are genuinely heavy-tailed — r/σ p99 ≈ 4–6, driven by upsets (a
   front-runner knocked out in Q1, a wet session). This is the **opposite** of the
   tire-wear correction (a parameter CI that wanted *Gaussian*), and concrete proof
   that a single shared ν is wrong across fundamentally different uses.

3. **Action taken:** `QUALI_NU_LOSS` decoupled from the shared `DEFAULT_NU_LOSS=4`
   and set to a quali-specific, calibrated **3.0** (`src/simulation/quali_simulator.py`),
   with the evidence cited inline. Easily retunable if the heuristic σ is ever
   replaced by a trained quali model.

## Residual / out of scope

- Q3 probability is mildly *under*-predicted on average (mean pred ≈ 0.45 vs actual
  ≈ 0.50). That is a **location** (`expected_position` mapping) issue, not a tail
  issue — the percentile→position map and the position≥1 boundary, not ν. Left as a
  separate follow-up; ν=3 addresses the dispersion/tail, not the mean.
- Positions are discrete (1..N) scored against a continuous t-CDF; standard
  approximation for a position model, noted for completeness.
