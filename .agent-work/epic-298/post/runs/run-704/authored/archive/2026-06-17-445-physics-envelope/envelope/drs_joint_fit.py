"""Joint DRS-closed + DRS-open drag fit with an HONEST identifiability σ (#445).

The closed-only CdA fit fails where the DRS-closed full-throttle data never reaches high speed
(Mexico: cars are on DRS for the whole straight, closed pts top out ~270 km/h, 0% above 280) — drag
is then extrapolated and the bootstrap σ is deceptively tight. Fix: fit BOTH regimes jointly with a
SHARED power P:

    a(v) = P/(m·v) − ½ρ·CdA_state(v)·v²/m ,  state ∈ {closed, open}

The DRS-OPEN points DO reach high speed (Mexico open vmax ~355) — they pin P (and CdA_open) on the
high-speed lever, which propagates through the shared P to identify CdA_closed from the closed
mid-speed points. Honest σ from the linear-fit covariance σ²·(XᵀX)⁻¹: it blows up exactly when the
design is ill-conditioned (no high-speed lever) and shrinks when drag is well-levered — unlike the
bootstrap, which only sees within-range scatter.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

from ribbon_reeval import MASS  # noqa: E402


def frontier_bins(v, a, q=0.90, lo=20.0, hi=100.0, step=6.0, minpts=6):
    """Upper-edge (q-quantile) accel per speed bin (m/s, m/s²)."""
    vb, ab = [], []
    for l in np.arange(lo, hi, step):
        m = (v >= l) & (v < l + step)
        if m.sum() >= minpts:
            vb.append(v[m].mean()); ab.append(np.quantile(a[m], q))
    return np.array(vb), np.array(ab)


def fit_drs_joint(v, a, op, rho, mass=MASS, q=0.90):
    """v (m/s), a (m/s²), op (bool DRS-open). Returns dict with P, CdA_closed/open and honest σ.

    σ_c / σ_o are the covariance-based standard errors — identifiability-aware (large when that
    drag term is poorly levered). cond = design condition number (high => weak identifiability).
    """
    vc, ac = frontier_bins(v[~op], a[~op], q)
    vo, ao = frontier_bins(v[op], a[op], q)
    # need closed bins to read configured-wing drag, and enough total to fit 3 params
    if len(vc) < 2 or (len(vc) + len(vo)) < 5:
        return None

    vv = np.concatenate([vc, vo]); aa = np.concatenate([ac, ao])
    is_o = np.concatenate([np.zeros(len(vc), bool), np.ones(len(vo), bool)])
    X = np.column_stack([
        1.0 / (mass * vv),
        -0.5 * rho * vv ** 2 / mass * (~is_o),
        -0.5 * rho * vv ** 2 / mass * is_o,
    ])
    coef, *_ = np.linalg.lstsq(X, aa, rcond=None)
    P, CdA_c, CdA_o = [float(c) for c in coef]

    resid = aa - X @ coef
    dof = max(len(aa) - 3, 1)
    s2 = float(np.sum(resid ** 2) / dof)
    XtX_inv = np.linalg.pinv(X.T @ X)
    cov = s2 * XtX_inv
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    # P↔CdA_closed estimator correlation (the degeneracy; +ve and large ⇒ power/drag not separated)
    corr_PCc = float(cov[0, 1] / np.sqrt(max(cov[0, 0] * cov[1, 1], 1e-30)))
    sv = np.linalg.svd(X, compute_uv=False)
    cond = float(sv[0] / max(sv[-1], 1e-12))

    # high-speed lever present in the OPEN set? (km/h reach of open frontier)
    vo_max = float(vo.max() * 3.6) if len(vo) else 0.0
    return dict(P=P, CdA_c=CdA_c, CdA_o=CdA_o,
                sP=float(se[0]), s_c=float(se[1]), s_o=float(se[2]),
                corr_PCc=corr_PCc, cond=cond, n_c=len(vc), n_o=len(vo), open_vmax_kmh=vo_max)
