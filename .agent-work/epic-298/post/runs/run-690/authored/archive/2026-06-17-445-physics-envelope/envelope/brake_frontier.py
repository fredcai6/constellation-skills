"""Braking frontier fit with an HONEST covariance σ (#445).

a_brake(v) = A_b + B_b·v²  (A_b = mechanical braking grip, config-INVARIANT per-car; B_b = downforce
braking, config-DEPENDENT/wing). Same lesson as drag: the bootstrap σ is blind to a short lever arm
(A_b is the v→0 intercept — extrapolated if braking points don't reach low speed). Use the linear-fit
covariance σ²(XᵀX)⁻¹ for σ_Ab, σ_Bb, and the A_b↔B_b estimator correlation (intercept/slope of a v²
fit are anti-correlated — the braking analogue of the P↔CdA degeneracy).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

from ribbon_reeval import G_CONST  # noqa: E402


def fit_brake_cov(vbr, decbr_g, q=0.95, lo=15.0, hi=96.0, step=8.0, minpts=8):
    """vbr (m/s), decbr_g (deceleration in g, positive). p95 upper edge per v-bin, fit A_b + B_b v².
    Returns dict with covariance σ's and the A_b↔B_b correlation, or None."""
    vb, db = [], []
    for l in np.arange(lo, hi, step):
        m = (vbr >= l) & (vbr < l + step)
        if m.sum() >= minpts:
            vb.append(vbr[m].mean()); db.append(np.quantile(decbr_g[m], q))
    vb, db = np.array(vb), np.array(db)
    if len(vb) < 4:
        return None
    X = np.column_stack([np.ones_like(vb), vb ** 2])
    coef, *_ = np.linalg.lstsq(X, db, rcond=None)
    Ab, Bb = float(coef[0]), float(coef[1])
    resid = db - X @ coef
    dof = max(len(db) - 2, 1)
    s2 = float(np.sum(resid ** 2) / dof)
    cov = s2 * np.linalg.pinv(X.T @ X)
    sA, sB = np.sqrt(np.clip(np.diag(cov), 0, None))
    corrAB = float(cov[0, 1] / np.sqrt(max(cov[0, 0] * cov[1, 1], 1e-30)))
    vlo = float(vb.min() * 3.6)   # lowest braking-bin speed (km/h) — A_b extrapolation lever
    return dict(Ab=Ab, Bb=Bb, sA=float(sA), sB=float(sB), corrAB=corrAB,
                n_bins=len(vb), n_pts=len(vbr), vlo_kmh=vlo)
