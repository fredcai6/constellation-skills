"""M3 spike: 1D physics-constrained longitudinal filter on the speed channel.

Mechanism: separate 1D Kalman-RTS smoother on v(t) alone (or v + soft a_long_raw),
with state [v, a], jerk process variance that is allowed to be large during braking
so a sharp decel onset is a *predicted feature*, not an artefact the
position-smoothness prior fights.

Design rationale (g2-m3.md):
- Root cause is the 2D position-smoothness prior fighting longitudinal transients.
- M3 decouples longitudinal estimation: 2D smoother keeps geometry/heading,
  1D filter owns a_long from the speed channel only.
- Anchor source = raw speed observation (un-biased; no dependence on the smoothed
  trajectory), so decision:two_cycle_external_anchor_design is not touched
  in its anchor-channel sense.
- Does NOT replace StintSmoother; it is a parallel estimator.

Output: a_long (m/s², signed; decel NEGATIVE) at inp.t.

Usage (scoreboard seam)::

    from src.physics.layer2.filter_m3 import variant_m3
    variants = {"m3": variant_m3, ...}
    table = run_scoreboard(cases, variants, cache=CACHE)

Hyperparameter notes:
- sig_v: speed obs noise std (m/s). Raw F1 speed sensor ~0.1–0.3 m/s.
- sig_a_brake: jerk process std during braking (m/s^1.5). THE crux HP.
  Large = knee un-rounds; too large = noisy.
- sig_a_other: jerk process std elsewhere.
- a_soft_obs_weight: sig_a_soft = sig_a_brake * a_soft_obs_weight.
  Soft accel pseudo-obs links the 1D filter to the raw sensor.
  Large weight = loose coupling (speed-channel dominated).
"""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# 1D RTS smoother kernel
# ---------------------------------------------------------------------------

def _rts_smooth_1d(
    t: np.ndarray,
    v_obs: np.ndarray,
    *,
    sig_v: float = 0.15,
    sig_a_brake: float = 35.0,
    sig_a_other: float = 4.0,
    is_brake: np.ndarray | None = None,
    a_soft_obs: np.ndarray | None = None,
    sig_a_soft: float = 5.0,
) -> tuple[np.ndarray, np.ndarray]:
    """1D Kalman-RTS smoother on the speed channel.

    State: x = [v, a]  (speed m/s, longitudinal accel m/s²)
    Process model (near-constant-accel):
        v_{k+1} = v_k + dt * a_k
        a_{k+1} = a_k + w_k,  w_k ~ N(0, sig_a^2 * dt)
    Observation model:
        z_k = v_k + e_k,  e_k ~ N(0, sig_v^2)
    Optional soft accel pseudo-obs:
        z_a_k = a_k + e_a_k, e_a_k ~ N(0, sig_a_soft^2)

    Parameters
    ----------
    t : time array (s), length N
    v_obs : speed observations (m/s), length N
    sig_v : speed obs noise std (m/s)
    sig_a_brake : jerk process std in straight_brake regime (m/s^1.5)
    sig_a_other : jerk process std elsewhere (m/s^1.5)
    is_brake : bool mask (length N); True = braking sample
    a_soft_obs : optional per-sample a_long_raw soft accel obs (m/s²)
    sig_a_soft : std of soft accel pseudo-obs (m/s²)

    Returns
    -------
    v_smooth : smoothed speed (m/s)
    a_smooth : smoothed longitudinal accel (m/s²; decel NEGATIVE)
    """
    n = len(t)
    if is_brake is None:
        is_brake = np.zeros(n, dtype=bool)

    # Initialise state and covariance
    x = np.array([v_obs[0], 0.0])
    P = np.diag([sig_v ** 2, (sig_a_brake if is_brake[0] else sig_a_other) ** 2])

    # Storage for forward pass
    xs = np.zeros((n, 2))
    Ps = np.zeros((n, 2, 2))
    xps = np.zeros((n, 2))
    Pps = np.zeros((n, 2, 2))
    Phis = [np.eye(2)] * n

    H_v = np.array([[1.0, 0.0]])
    R_v = sig_v ** 2

    for k in range(n):
        if k > 0:
            dt = max(float(t[k] - t[k - 1]), 1e-6)

            # Regime-dependent jerk process noise
            sig_a = sig_a_brake if is_brake[k] else sig_a_other
            q_a = (sig_a ** 2) * dt   # discrete variance for accel increment

            Phi = np.array([[1.0, dt], [0.0, 1.0]])
            # Q: small speed process noise (model noise) + large accel jerk
            Q = np.array([[(sig_v * 0.01) ** 2 * dt, 0.0],
                           [0.0,                       q_a]])

            # Predict
            xp = Phi @ x
            Pp = Phi @ P @ Phi.T + Q
            Phis[k] = Phi
        else:
            xp = x.copy()
            Pp = P.copy()

        xps[k] = xp
        Pps[k] = Pp
        x = xp.copy()
        P = Pp.copy()

        # Update: speed observation
        innov = v_obs[k] - x[0]
        S = P[0, 0] + R_v
        K = P[:, 0] / S
        x = x + K * innov
        P = P - np.outer(K, P[0, :])

        # Update: optional soft accel pseudo-obs
        if a_soft_obs is not None:
            innov_a = a_soft_obs[k] - x[1]
            R_a = sig_a_soft ** 2
            S_a = P[1, 1] + R_a
            if S_a > 1e-12:
                K_a = P[:, 1] / S_a
                x = x + K_a * innov_a
                P = P - np.outer(K_a, P[1, :])

        P = 0.5 * (P + P.T)
        xs[k] = x.copy()
        Ps[k] = P.copy()

    # Backward RTS pass
    m_s = xs.copy()
    P_s = Ps.copy()
    for k in range(n - 2, -1, -1):
        Phi = Phis[k + 1]
        Pp = Pps[k + 1]
        Pp_sym = 0.5 * (Pp + Pp.T)
        try:
            C = Ps[k] @ Phi.T @ np.linalg.inv(Pp_sym)
        except np.linalg.LinAlgError:
            C = np.zeros((2, 2))
        m_s[k] = xs[k] + C @ (m_s[k + 1] - xps[k + 1])
        P_s[k] = Ps[k] + C @ (P_s[k + 1] - Pp_sym) @ C.T
        P_s[k] = 0.5 * (P_s[k] + P_s[k].T)

    return m_s[:, 0], m_s[:, 1]


# ---------------------------------------------------------------------------
# VariantFn factory for the scoreboard seam
# ---------------------------------------------------------------------------

def make_variant_m3(
    sig_v: float = 0.15,
    sig_a_brake: float = 35.0,
    sig_a_other: float = 4.0,
    a_soft_obs_weight: float = 3.0,
    name: str = "m3",
):
    """Factory: returns (name, VariantFn) for M3 with given hyperparameters.

    Parameters
    ----------
    sig_v : speed obs noise std (m/s)
    sig_a_brake : jerk process std in braking (m/s^1.5); the crux HP.
    sig_a_other : jerk process std elsewhere (m/s^1.5)
    a_soft_obs_weight : sig_a_soft = sig_a_brake * a_soft_obs_weight.
                        Large = loose coupling to raw sensor (speed-dominated).
    name : variant name in the scoreboard
    """
    sig_a_soft = sig_a_brake * a_soft_obs_weight

    def _fn(inp) -> np.ndarray:
        is_brake = inp.regime == "straight_brake"
        _v_sm, a_sm = _rts_smooth_1d(
            inp.t, inp.v,
            sig_v=sig_v,
            sig_a_brake=sig_a_brake,
            sig_a_other=sig_a_other,
            is_brake=is_brake,
            a_soft_obs=inp.a_long_raw,
            sig_a_soft=sig_a_soft,
        )
        return a_sm

    _fn.__name__ = name
    return name, _fn


# Default variant (hand-tuned HP sweet spot after sweep)
_DEFAULT_NAME, variant_m3 = make_variant_m3(
    sig_v=0.15,
    sig_a_brake=35.0,
    sig_a_other=4.0,
    a_soft_obs_weight=3.0,
)


# ---------------------------------------------------------------------------
# Synthetic sanity test
# ---------------------------------------------------------------------------

def synthetic_sanity_check(
    v0: float = 80.0,
    a_step: float = -45.0,
    t_brake_start: float = 1.0,
    dt: float = 0.04,
    duration: float = 3.0,
    sig_v: float = 0.15,
    sig_a_brake: float = 35.0,
    sig_a_other: float = 4.0,
    a_soft_obs_weight: float = 3.0,
    noise_seed: int = 42,
) -> dict:
    """Synthetic known sharp-decel step test.

    Generates a speed trace from v0 (m/s) decelerating at a_step (m/s²) from
    t_brake_start. Adds Gaussian noise with std=sig_v. Runs M3 and reports
    recovered peak decel vs the true value.

    Returns dict with truth, recovered, error, and pass/fail.
    """
    rng = np.random.default_rng(noise_seed)
    n = int(duration / dt) + 1
    t = np.linspace(0.0, (n - 1) * dt, n)

    # True speed: constant then linear decel
    v_true = np.where(
        t < t_brake_start,
        v0,
        np.maximum(0.0, v0 + a_step * (t - t_brake_start)),
    )

    v_obs = v_true + rng.normal(0.0, sig_v, size=n)

    # True a_long: 0 before brake_start, a_step during
    a_true = np.where(t >= t_brake_start, float(a_step), 0.0)
    is_brake = t >= t_brake_start

    # Soft obs = true a_long + small noise (mimics a_long_raw)
    a_soft = a_true + rng.normal(0.0, 1.0, size=n)
    sig_a_soft = sig_a_brake * a_soft_obs_weight

    _v_sm, a_sm = _rts_smooth_1d(
        t, v_obs,
        sig_v=sig_v,
        sig_a_brake=sig_a_brake,
        sig_a_other=sig_a_other,
        is_brake=is_brake,
        a_soft_obs=a_soft,
        sig_a_soft=sig_a_soft,
    )

    # Steady-state recovered accel in the braking region (exclude transient entry)
    brake_region = is_brake & (t > t_brake_start + 4 * dt)
    if brake_region.any():
        recovered_plateau = float(np.percentile(a_sm[brake_region], 10))  # near-min
    else:
        recovered_plateau = float(a_sm[is_brake].min()) if is_brake.any() else float("nan")

    recovered_knee = float(a_sm[is_brake].min()) if is_brake.any() else float("nan")
    true_knee = float(a_step)
    error = recovered_knee - true_knee  # positive = under-reading

    return {
        "true_knee_ms2": true_knee,
        "recovered_knee_ms2": recovered_knee,
        "recovered_plateau_ms2": recovered_plateau,
        "error_ms2": error,
        "pass": abs(error) < 5.0,  # within 5 m/s² of truth on a -45 m/s² step
        "t": t,
        "v_true": v_true,
        "v_obs": v_obs,
        "a_true": a_true,
        "a_sm": a_sm,
    }


if __name__ == "__main__":
    result = synthetic_sanity_check()
    print(f"Synthetic sanity: true={result['true_knee_ms2']:.1f} m/s2  "
          f"recovered={result['recovered_knee_ms2']:.2f} m/s2  "
          f"error={result['error_ms2']:.2f} m/s2  "
          f"PASS={result['pass']}")
