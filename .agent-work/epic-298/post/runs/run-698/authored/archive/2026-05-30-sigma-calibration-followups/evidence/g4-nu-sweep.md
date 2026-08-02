# G4-A — Student-t ν sensitivity (smoke)

**Train/eval:** [2023] → 2024, **epochs:** 5, **λ_sigma_nll:** 1.0

**Verdict:** `keep_shared_nu_4`

**G5 recommendation:** `student_t_nu=4.0`, `student_t_nu_sigma=None`

Smoke ν∈{3,4,6,8} moved |r/σ| tails and per-pair σ_std by &lt;2% on both modules; ν=2 invalid (config requires &gt;2). Keep ADR default ν=4; do not enable `student_t_nu_sigma` split in G5.

## Observations
- driver_race_start: p99 |r/σ| 1.612 (ν=4) vs 1.624 (ν=3) vs 1.551 (ν=8); σ_std 0.0390–0.0401 across ν.
- driver_quali: p99 1.278 (ν=4) vs 1.273 (ν=3); σ_std 0.0161–0.0168 — no phase-specific winner.
- Per-pair corr(σ,nll) stable ~0.32 (race-start) and ~0.11 (quali); raw supervised NLL deltas across ν are not comparable (dropped Student-t constants).

## Per-module sweep
### driver_race_start_power_from_race_weekend
| ν | status | p50 | p95 | p99 | σ_std | corr(σ,nll) | Δ sup vs ν=4 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | skipped | — | — | — | — | — | — |
| 3 | ok | 0.495 | 1.329 | 1.624 | 0.0391 | 0.33221850748154086 | — |
| 4 | ok | 0.486 | 1.315 | 1.612 | 0.0390 | 0.3169788096440261 | — |
| 6 | ok | 0.477 | 1.291 | 1.589 | 0.0394 | 0.3237516737214749 | 0.005410339683294296 |
| 8 | ok | 0.465 | 1.264 | 1.551 | 0.0401 | 0.32455386868782843 | 0.01513892536362016 |

### driver_quali_power_from_race_weekend
| ν | status | p50 | p95 | p99 | σ_std | corr(σ,nll) | Δ sup vs ν=4 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | skipped | — | — | — | — | — | — |
| 3 | ok | 0.431 | 1.091 | 1.273 | 0.0167 | 0.11301384645612648 | — |
| 4 | ok | 0.432 | 1.094 | 1.278 | 0.0161 | 0.1150082778456334 | — |
| 6 | ok | 0.428 | 1.089 | 1.272 | 0.0168 | 0.12202887183857337 | -0.00469332622985047 |
| 8 | ok | 0.431 | 1.090 | 1.275 | 0.0164 | 0.12009391745806494 | -0.009361554558078466 |
