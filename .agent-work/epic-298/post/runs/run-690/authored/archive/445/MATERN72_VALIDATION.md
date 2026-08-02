# Matérn-7/2 smoother — broad validation + production PR plan (#445, 2026-06-16)

Validation run by subagent A4 (`m72_wide_validation.py` → `m72_validation_cache.json`); the agent
stalled (watchdog) after 18/22 sessions, but 18/18 is conclusive. Cost + PR plan completed by Admiral.

## Validation: 7/2 wins 18/18 sessions

Per-order χ²-calibrated held-out SPEED (the clean acc-sensitive arbiter; robust metrics — RMSE is
glitch-gamed). Both orders calibrated to per-channel χ²≈1 per session, tested on held-out speed across
6 drivers' flying laps.

```
POOLED (17,457 held-out speed pts):  median |e|   5/2 0.759  →  7/2 0.451 m/s   (sensor floor 0.49)
                                      MAE          5/2 3.802  →  7/2 1.057 m/s
                                      glitch >5    5/2 14.6%  →  7/2 2.5%
7/2 wins on median|e| in 18/18 sessions.
short-ell collapse (calibrated ell ≤ 1.5):  5/2 in 3/18 sessions,  7/2 in 0/18.
```

**Mechanism, confirmed broadly:** 5/2's χ²-target calibration occasionally collapses to short ell —
a well-calibrated but rough-velocity model that is a terrible point predictor. The 3 collapse sessions:
- British  5/2 ell=1.2 → med 11.50 m/s, glitch 71.5% | 7/2 ell=4.8 → med 0.302, glitch 1.8%
- Hungarian 5/2 ell=1.0 → med  9.73 m/s, glitch 69.2% | 7/2 ell=6.0 → med 0.489, glitch 3.0%
- Singapore 5/2 ell=1.4 → med  7.17 m/s, glitch 60.9% | 7/2 ell=4.5 → med 0.524, glitch 1.9%
7/2 (differentiable accel) reaches χ²≈1 at moderate ell every session (never collapses) → velocity/accel
both calibrated AND accurate. Even on the 15 non-collapse sessions 7/2 is consistently ~10–25% better.
7/2 doesn't beat the 0.49 m/s sensor floor (4.2 Hz Nyquist) — it REACHES it robustly where 5/2 doesn't.

## Cost
order-3 (6-state) 83.3 ms/fit vs order-4 (8-state) 91.8 ms/fit (360 pts, 2 iters) = **~1.10×**.
The O(N) Kalman-RTS loop dominates; 8×8 vs 6×6 per-step matrices add only ~10%. Negligible for the gain.

## Production PR plan (src/preprocessing/trajectory/)

Reference impl: `.agent-work/445/envelope/matern_smoother.py` (generic-order MaternSmoother; order-3
reproduces production StintSmoother to 1e-10; P_inf via continuous-Lyapunov solve). Per-order χ²
calibrator: `accel_order_calibrated.py::calibrate_order`.

**Changes:**
1. `dynamics.py` — add `matern_sde(ell, sf, order)` (companion F of (s+λ)^order, λ=√(2ν)/ell; L=e_d;
   P_inf via `scipy.linalg.solve_continuous_lyapunov` scaled to P_inf[0,0]=sf²). **KEEP `matern52_sde`
   (analytic P_inf) as the order-3 path unchanged** — see risk below. Generalize `_block6`→`_blockJ(Ax,d)`.
2. `smoother.py` — add `order` param to StintSmoother (default 3). Replace hardcoded dim-6 / index
   {0,3 pos; 1,4 vel; 2,5 acc} with per-axis order d: pos=(0,d), vel=(1,d+1), acc=(2,d+2). Generalize
   `_init_P0` (diffuse pos/vel, stationary acc + higher states; NO pos-acc cross at t=0 — critical, see
   risk). NSStintSmoother (E11) needs the same generalization if order-4 wanted there.
3. `calibration.py` — thread `order` through `fit_stint_hp`/`session_offset`/`_eval_hp` (currently
   instantiate StintSmoother=order3). `interleaved`/`_heldout_chi2` are order-agnostic already.

**Risk surface (the nesting gate is the real one):**
- **E4-nesting gate**: order-3 MUST still reproduce the E4 dense-GP / production exactly (E10 found the
  pos-acc cross term at t=0 biases ~150 mm and breaks nesting). MITIGATION: do NOT replace the order-3
  P_inf — Lyapunov P_inf matches analytic matern52 only to ~3e-11; keep `matern52_sde`'s analytic path
  for order 3, use Lyapunov ONLY for order≥4. Verify `tests/unit/preprocessing/trajectory/test_nesting_oracle.py`
  + `test_trust_profile.py` + `test_artifact_roundtrip.py` all pass unchanged with order-3 default.
- `_init_P0` order-4 must mirror the diffuse-pos/vel + stationary-higher-states, no cross terms.
- Downstream consumers assume 6-state artifacts (artifact.py, grading.py, report schemas) — order is an
  internal detail if pos/vel/acc accessors stay stable, but audit artifact serialization.

**Recommendation:** implement order-4 as opt-in, **keep order-3 default** for the merge; run the full
`tests/regression/test_physics_regression.py` + trajectory unit suite with order-4 forced to confirm no
downstream breakage; THEN flip the default to 7/2 in a follow-up once the regression gate is green. The
held-out-speed evidence (18/18, ~10% cost) strongly favors 7/2 as the eventual default.
