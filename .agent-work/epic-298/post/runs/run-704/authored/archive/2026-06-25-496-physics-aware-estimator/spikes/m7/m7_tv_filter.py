"""M7 spike: TV-denoised raw speed → kind=3 anchor over full braking arc (#496/#507).

Mechanism:
  1. Take inp.a_long_raw (already the un-biased raw-sensor longitudinal accel, derived
     from clean_longitudinal_from_raw).
  2. Apply a 1D edge-preserving total-variation (TV / Huber-L1) denoise to a_long_raw
     that PERMITS sharp onset edges (brake slams) while killing high-frequency sensor
     noise. Implemented via the ADMM / L1-trend approach.
  3. Build an AccelObs (kind=3) over the FULL braking arc (not just plateau-plateau
     samples) using the denoised value as anchor magnitude and cycle-1 heading as frame.
  4. Cycle-2 smoother with the extended anchor → return a_long.

INVARIANT EXTENSION NOTE:
  - Anchor magnitude: DENOISED RAW (edge-preserving transform of raw only, never from
    the smoothed trajectory) → stays "external & un-biased" in spirit.
  - Anchor placement: extended from plateau-only to the full braking arc.  Rationale:
    the raw signal already shows the onset transient; TV denoise keeps the knee but
    removes noise, so anchoring the onset is justified (the step is real, not noise).
  - Two-cycle structure: preserved.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import medfilt

from src.preprocessing.trajectory.smoother import AccelObs


# ---------------------------------------------------------------------------
# TV denoise (1D, isotropic) via iterative reweighted least squares (IRLS)
# Equivalent to L1 total variation regularisation: min_u (||u-y||^2 + lam*||Du||_1)
# ---------------------------------------------------------------------------

def _tv_denoise_irls(y: np.ndarray, lam: float, n_iter: int = 30, eps: float = 1e-4) -> np.ndarray:
    """1D total-variation denoising via IRLS (edge-preserving).

    Minimises  (1/2)||u - y||^2 + lam * sum |u_{i+1} - u_i|
    using iteratively reweighted least squares (IRLS):
      Each iteration solves a weighted least squares problem where the weights
      are 1/max(|u_{i+1}-u_i|, eps) — this approximates the L1 norm.

    Edge-preserving: sharp steps (|u_{i+1}-u_i| >> eps) get low weight in the
    roughness penalty so they are preserved, while small wiggles (|diff| ~ eps) are
    smoothed heavily.  The brake-onset step (raw shows ~52 m/s^2 drop) is preserved
    because the IRLS weight goes to zero there.

    Parameters
    ----------
    y   : noisy signal
    lam : regularisation strength (larger = smoother; sweep 0.1..5.0)
    n_iter : IRLS iterations (converges in ~15-30 for typical signals)
    eps    : IRLS stability floor (prevents division by zero)
    """
    n = len(y)
    if n <= 1:
        return y.copy()
    u = y.copy()
    for _ in range(n_iter):
        diff = np.diff(u)
        w = 1.0 / np.maximum(np.abs(diff), eps)   # IRLS weights: small at edges
        # Build tridiagonal system: (I + lam * D^T W D) u = y
        # D^T W D is tridiagonal: diag = [...w[i-1]+w[i]...], off-diag = -w
        main_diag = np.zeros(n)
        main_diag[0] = 1.0 + lam * w[0]
        main_diag[-1] = 1.0 + lam * w[-1]
        for i in range(1, n - 1):
            main_diag[i] = 1.0 + lam * (w[i - 1] + w[i])
        off_diag = -lam * w  # length n-1

        # Solve tridiagonal system via Thomas algorithm (no scipy needed)
        a = off_diag.copy()   # sub-diag (length n-1, used as [1..n-1])
        b = main_diag.copy()  # main diag
        c = off_diag.copy()   # super-diag (length n-1, used as [0..n-2])
        d = y.copy()

        # Forward sweep
        for i in range(1, n):
            m = a[i - 1] / b[i - 1]
            b[i] -= m * c[i - 1]
            d[i] -= m * d[i - 1]
        # Back substitution
        u_new = np.zeros(n)
        u_new[-1] = d[-1] / b[-1]
        for i in range(n - 2, -1, -1):
            u_new[i] = (d[i] - c[i] * u_new[i + 1]) / b[i]
        u = u_new
    return u


# ---------------------------------------------------------------------------
# Helper: emit kind=3 AccelObs over FULL braking arc (not plateau-only)
# ---------------------------------------------------------------------------

def _emit_braking_arc_obs(
    t: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    regime: np.ndarray,
    a_long_tv: np.ndarray,
    sigma: float = 1.0,
    edge_margin: int = 2,
) -> AccelObs:
    """Build kind=3 obs over all straight_brake samples (contiguous runs).

    M7 extends the standard plateau-only emitter: it anchors the FULL braking
    arc including the onset transient, using the TV-denoised a_long as value.
    A small edge_margin trims the very first/last sample of each braking run to
    avoid injecting transient boundary noise (2 samples ~ 0.1 s at 20 Hz).

    heading (ex, ey) comes from cycle-1 smoother vel_at (geometry frame only).
    """
    spd = np.maximum(np.hypot(vx, vy), 1e-6)
    brake_mask = regime == "straight_brake"
    idx = np.where(brake_mask)[0]
    if len(idx) == 0:
        z = np.zeros(0)
        return AccelObs(t=z, ex=z, ey=z, a=z, sigma=z)

    # Split into contiguous runs; trim edges
    # NOTE: r[0:-0] = r[0:0] = [] due to Python's -0==0; guard with explicit slice.
    keep = np.zeros(len(t), dtype=bool)
    runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    for r in runs:
        if edge_margin == 0:
            keep[r] = True
        elif len(r) > 2 * edge_margin:
            keep[r[edge_margin:-edge_margin]] = True
        # else: run too short for this margin → skip (degrade gracefully)

    pick = np.where(keep)[0]
    if len(pick) == 0:
        z = np.zeros(0)
        return AccelObs(t=z, ex=z, ey=z, a=z, sigma=z)

    order = pick[np.argsort(t[pick])]
    return AccelObs(
        t=t[order],
        ex=vx[order] / spd[order],
        ey=vy[order] / spd[order],
        a=a_long_tv[order],
        sigma=np.full(len(order), sigma),
    )


# ---------------------------------------------------------------------------
# M7 VariantFn factory
# ---------------------------------------------------------------------------

def make_m7_variant(lam: float = 1.0, nu_proc: float = 4.0, sigma_anchor: float = 1.0):
    """Return a VariantFn implementing M7 TV-denoised braking-arc anchor.

    Parameters
    ----------
    lam           : TV regularisation strength (sweep 0.1 .. 5.0 for the report)
    nu_proc       : Student-t jerk dof (same as kind3 baseline)
    sigma_anchor  : noise std for the kind=3 anchor (m/s²; tighter = smoother accepted more)
    """
    from src.physics.layer2.scoreboard import _long_accel

    def variant_m7(inp) -> np.ndarray:
        # --- Cycle 1: Student-t jerk prior re-smooth (geometry frame) ---
        sm1 = inp.make_smoother(nu_proc=nu_proc)
        sm1.fit(inp.t, inp.x, inp.y, inp.t, inp.v)
        vx, vy = sm1.vel_at(inp.t)  # heading only (frame, not magnitude)

        # --- TV denoise the RAW a_long (edge-preserving, never from smoothed traj) ---
        a_long_tv = _tv_denoise_irls(inp.a_long_raw, lam=lam)

        # --- Build kind=3 obs over FULL braking arc using TV-denoised a_long ---
        obs = _emit_braking_arc_obs(
            inp.t, vx, vy, inp.regime, a_long_tv, sigma=sigma_anchor
        )

        # --- Cycle 2: re-smooth with TV-denoised braking-arc anchor ---
        sm2 = inp.make_smoother(nu_proc=nu_proc)
        sm2.fit(inp.t, inp.x, inp.y, inp.t, inp.v, accel_obs=obs)
        return _long_accel(sm2, inp.t)

    variant_m7.__name__ = f"m7_lam{lam:.2f}"
    return variant_m7
