# Phase 2 Code Review — Covariance-Sampled Monte Carlo Ideal Lap

**Epic:** #445  
**Reviewer:** Independent (fresh eyes)  
**Date:** 2026-06-16  
**Verdict: APPROVE-WITH-NITS**

Tests: 146 passed, 0 failed, 1 warning (non-PSD covariance in diverged-draw test).

---

## Independent Verification of the Headline Claim

Re-ran `monte_carlo_laps` with the exact test parameters (N=500, seed=42):

```
sigma_joint = 0.2819 s
sigma_indep = 0.4375 s
ratio       = 1.552
```

Confirmed seed-robust across seeds 0–9 (ratio range 1.39–1.55; minimum 1.39, all above the 1.3 threshold). The claim `σ_joint=0.28 vs σ_indep=0.44` is accurate and reproducible.

**Is the comparison fair?** Yes. Both arms draw (A0, A2) from the same marginal variances (sigma_A0=5.0, sigma_A2=0.001). The independent arm uses `sqrt(cov[0,0])` and `sqrt(cov[1,1])` directly, which are the same marginals as the multivariate normal's diagonals. The only difference is the cross-term. This is not rigged.

**Would the test fail if `_sample_parameters` used independent sampling in both paths?** Yes — the test passes `joint=True` and `joint=False` as separate calls and asserts `sigma_joint < sigma_indep`. If both arms ran the independent code path, both sigmas would be equal and the assertion would fail.

**Is N=500 sufficient?** Empirically yes — the tightest seed (seed=3) produced ratio=1.395, still 7% above the 1.3 threshold. With N=500 and ratio typically 1.45-1.55, there is adequate headroom. Not a hypothesis/property test, so seed-lock is the right choice at this sample count.

---

## Findings

### Finding 1 (NIT) — Dead `sample` parameter on `simulate_lap`
**File:** `src/physics/physics_simulator.py`, line 49  
**Severity:** Nit  
The `sample: bool = True` parameter on `simulate_lap` is now dead code — the function body never references it. The stochastic path was intentionally moved to `_sample_parameters` / `monte_carlo_laps`. The parameter should either be removed (with a deprecation note) or documented as no-op to avoid caller confusion. The test `test_simulate_lap_sample_false_deterministic` only tests `sample=False` and does not verify that `sample=True` produces the same deterministic result (they do, but this is untested).

### Finding 2 (NIT) — Missing upper bound on `theta_R` clipping
**File:** `src/physics/physics_simulator.py`, line ~218  
**Severity:** Nit  
`theta_R` is clipped only at 0 (`max(theta_R_nom, 0.0)`) with no upper bound, while `theta_D` is clipped at `cfg.theta_D_max_plausible` and config exposes `theta_R_max_plausible=5.0`. In practice the divergence filter (±2× lap time) provides an implicit upper guard, and sigma_R=0.05 means exceeding 5.0 requires a >90-sigma excursion, so this is not a practical bug. However the asymmetry between theta_D and theta_R clipping is inconsistent and should be reconciled.

### Finding 3 (NIT) — Non-PSD test matrix in `test_diverged_draws_filtered_finite_result`
**File:** `tests/unit/physics/test_monte_carlo.py`, lines 254-256  
**Severity:** Nit  
The `lateral_cov` used in this test is:
```python
lateral_cov = np.array([[100.0, -9.0], [-9.0, 0.1]])
```
This has eigenvalues `[-0.70, 100.80]` — not positive semidefinite (det = 10 - 81 = -71 < 0). The implied correlation is `−9 / (10 × 0.316) = −2.85`, which is outside `[−1, 1]` and physically impossible. NumPy warns but still samples by clamping negative eigenvalues to zero, producing a RuntimeWarning in the test suite. The `1e-30 * I` regularisation does not fix a matrix with a large negative eigenvalue. The intent — "huge variance → many diverged draws" — is valid, but the matrix should be constructed as a valid covariance (e.g., `_anti_corr_lateral_cov(sigma_A0=10, sigma_A2=0.3, corr=-0.9)` with the sigma values scaled up) rather than an incoherent one. The test passes and the warning is benign, but it suggests the author hand-wrote the matrix values without checking PSD.

### Finding 4 (NIT) — `valid_fraction` tested only for positivity, no low-water-mark assertion
**File:** `tests/unit/physics/test_monte_carlo.py`, line 273  
**Severity:** Nit  
```python
assert 0.0 < dist.valid_fraction <= 1.0
```
This only confirms at least one draw survived. There is no test establishing what constitutes an unhealthily low `valid_fraction`. The docstring warns "< 0.5 suggests poorly conditioned covariance" but no test exercises that warning or verifies that the all-diverged fallback path (`valid_fraction=0.0`) works correctly. The all-diverged branch sets `valid_fraction=0.0` and falls back to `lap_times=[nominal_t]`, but the diverged-draw test assertion `0.0 < vf <= 1.0` would FAIL for that case — meaning the all-diverged code path has no coverage.

### Finding 5 (NIT) — `theta_P_covariance` perturbation path has zero test coverage
**File:** `tests/unit/physics/test_monte_carlo.py`, all tests  
**Severity:** Nit  
All 9 tests pass `theta_P_cov=None` to `_make_params`. The `theta_P_covariance` perturbation branch in `_sample_parameters` (lines ~262-278 of the diff) is entirely untested. This means if that code has a bug (e.g., wrong indexing into the covariance diagonal, or the `frac_scale` clip being wrong), it would be invisible. Worth adding a single test that passes a non-trivial `theta_P_covariance` and asserts the power scale varies across draws.

### Finding 6 (OBSERVATION, not a bug) — Clipping introduces ~16% A2 truncation; does NOT confound the joint<indep comparison
**File:** `src/physics/physics_simulator.py`, line ~230  
**Severity:** Observation (no action needed)  
With sigma_A2=0.001 and nominal A2=0.001, ~16% of draws have A2 clipped to 0. This happens symmetrically in both joint and independent modes (empirically: 15.8% vs 16.9% clip rates). The post-clip correlation is preserved correctly: corr(A0, A2) = −0.87 in joint mode vs 0.008 in indep mode. The divergence filter is inactive for both (valid_fraction=1.000 for N=500). Clipping inflates E[A2] slightly (0.00109 vs 0.001) and suppresses std[A2] slightly, but does so symmetrically in both arms, so the comparison is valid. This is not a confound.

### Finding 7 (OBSERVATION) — Headline metric in PR description vs actual result
**Severity:** Observation  
The PR description states "σ_joint=0.28 vs σ_indep=0.44". Independent verification gives 0.2819 vs 0.4375. These match to 2 significant figures. No discrepancy.

---

## Summary Table

| # | Severity | File | Issue |
|---|----------|------|-------|
| 1 | Nit | physics_simulator.py:49 | Dead `sample` param on simulate_lap |
| 2 | Nit | physics_simulator.py:~218 | theta_R missing upper clip bound |
| 3 | Nit | test_monte_carlo.py:254-256 | Non-PSD test matrix → RuntimeWarning |
| 4 | Nit | test_monte_carlo.py:273 | valid_fraction has no lower-bound test; all-diverged path untested |
| 5 | Nit | test_monte_carlo.py (all) | theta_P_covariance path has zero test coverage |
| 6 | Obs | physics_simulator.py | A2 clipping symmetric; does not confound the comparison |
| 7 | Obs | PR description | Claimed σ values match actual output to 2 sig figs |

---

## Core Implementation Assessment

**Joint sampling is genuinely joint:** `_sample_parameters` calls `rng.multivariate_normal([0, 0], cov_reg)` for the 2×2 covariance in joint mode, and independent `rng.normal(0, s)` calls using the diagonal marginals in independent mode. Correct.

**Determinism/seedability:** `monte_carlo_laps` accepts `seed` (creates `default_rng(seed)`) or a pre-built `rng`. The RNG flows through all draws. Same-seed tests confirm identical output. Correct.

**`sample=False` path unchanged:** `simulate_lap(sample=False)` calls the same deterministic forward-backward sweep. `monte_carlo_laps` internally always calls `simulate_lap(..., sample=False)` on the already-perturbed parameter set. The separation of concerns is clean.

**Zero-covariance → σ≈0:** Confirmed. The `1e-30 * I` regulariser produces perturbations of order `1e-15`, yielding `std < 1e-9`. The test threshold of `1e-9` is correct.

**Divergence filter (±2× nominal):** Reasonable range for physical parameters. Would catch extreme draws (theta_R blowing up, A0 going negative post-clip, etc.). The fallback to `[nominal_t]` when all draws diverge is safe but untested.

**Power perturbation gating:** Power scale is only perturbed when `theta_P_covariance` is present. No hidden noise source when absent. Correct design.
