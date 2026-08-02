"""M1 variant: model-shape onset anchor inside kind=3 (#496/#507 spike).

Mechanism
---------
The #498 plateau anchor constrains the SUSTAINED braking plateau (raw a_long,
plateau-only). M1 extends this to anchor the entire braking ONSET transient with
an anchor value derived from a braking-frontier model fit (a_b + b_b * v^2) from
this lap's raw braking samples. The model smoothly predicts decel across the full
speed range, capturing the onset shape as a physics-motivated prior rather than
smoothing noise.

Two-cycle structure (mirrors refine_trajectory):
  cycle 1: Student-t jerk prior (nu_proc=4.0), Gaussian smoother for heading.
  cycle 2: kind=3 AccelObs over the FULL braking arc with model-predicted values.

INVARIANT EXTENSION (decision:two_cycle_external_anchor_design):
  - Source change: anchor value = a_b + b_b * v_i^2 (MODEL from RAW fit), not raw sample.
    The model is fit ONLY from raw a_long_raw -- never from the smoothed trajectory.
    This satisfies the 'external & un-biased' requirement (external to the smoother,
    un-biased of the smoothed output). Risk: the model shape may impose A+Bv^2 even
    if the real transient deviates (e.g. thermal fade at top speed).
  - Placement change: the FULL braking arc, not plateau-only. Onset placement is
    justified because the smoother over-rounds the knee PRECISELY at onset; plateau
    anchoring misses the transition. The model anchor at onset is a predicted feature
    (physics: decel follows a+bv^2 for well-loaded brakes), not noise.
  - Risk: over-tight sigma forces the trajectory onto the model regardless of data.
    We test sigma sensitivity: 0.5 (tight), 1.0 (moderate), 2.0 (loose).
"""
from __future__ import annotations

import numpy as np

from src.physics.layer2.accel_obs import FrontierSamples, emit_accel_obs
from src.physics.layer2.scoreboard import CaseInputs, _long_accel
from src.physics.layer2.trajectory_refine import RefineInputs
from src.preprocessing.trajectory.smoother import AccelObs

_NU_PROC_DEFAULT = 4.0


def _fit_frontier_model(
    v: np.ndarray,
    a_long_raw: np.ndarray,
    brake_mask: np.ndarray,
    *,
    quantile: float = 0.85,
    min_pts: int = 8,
) -> tuple[float, float] | None:
    """Fit a_b + b_b * v^2 from raw braking samples.

    Uses quantile regression on speed bins (not raw samples directly, to avoid
    fitting to utilisation noise). The upper-quantile ridge approximates the
    frontier (capability, not utilisation).

    Returns (a_b, b_b) where model decel magnitude = a_b + b_b * v^2 (both >= 0
    expected for physics realism, but not constrained), or None if insufficient data.

    NOTE: Only fits from RAW a_long_raw, NEVER from any smoothed trajectory output.
    """
    if not brake_mask.any():
        return None

    v_brake = v[brake_mask]
    a_brake = a_long_raw[brake_mask]

    # Only genuine decel samples (a_long < 0 means decel)
    decel_mask = a_brake < 0.0
    if int(decel_mask.sum()) < min_pts:
        return None

    v_b = v_brake[decel_mask]
    decel_mag = -a_brake[decel_mask]  # positive magnitude

    # Bin by speed, take upper quantile per bin (frontier approximation)
    v_min, v_max = float(v_b.min()), float(v_b.max())
    if v_max - v_min < 5.0:
        # Too narrow a speed range -- can't fit a v^2 trend; fall back to median
        step = 2.0
    else:
        step = max((v_max - v_min) / 8.0, 2.0)

    bin_edges = np.arange(v_min, v_max + step, step)
    bin_v = []
    bin_d = []
    for left in bin_edges[:-1]:
        right = left + step
        mask = (v_b >= left) & (v_b < right)
        n = int(mask.sum())
        if n >= 2:
            bin_v.append(float(v_b[mask].mean()))
            bin_d.append(float(np.quantile(decel_mag[mask], quantile)))

    if len(bin_v) < 3:
        # Not enough bins -- fall back to naive OLS on all samples
        bin_v = v_b.tolist()
        bin_d = decel_mag.tolist()

    if len(bin_v) < 2:
        return None

    vb = np.array(bin_v, dtype=float)
    db = np.array(bin_d, dtype=float)
    X = np.column_stack([np.ones_like(vb), vb ** 2])
    coef, *_ = np.linalg.lstsq(X, db, rcond=None)
    a_b = float(coef[0])
    b_b = float(coef[1])
    return a_b, b_b


def _build_onset_anchor(
    inp: CaseInputs,
    vx_cycle1: np.ndarray,
    vy_cycle1: np.ndarray,
    *,
    a_b: float,
    b_b: float,
    sigma: float = 1.0,
    margin: int = 2,
) -> AccelObs:
    """Build AccelObs over the FULL braking arc with model-predicted decel values.

    The anchor direction (ex, ey) comes from cycle-1 smoother heading (external
    to cycle-2, satisfying the 'geometric frame only' rule from trajectory_refine).
    The anchor value = -(a_b + b_b * v_i^2) (signed: decel negative), from the
    RAW-fit model.

    margin: trim margin samples from each brake-run edge to avoid onset/offset noise.
    """
    spd = np.maximum(inp.v, 1e-6)  # raw speed from CaseInputs
    vx = vx_cycle1
    vy = vy_cycle1
    heading_spd = np.maximum(np.hypot(vx, vy), 1e-6)
    ex = vx / heading_spd
    ey = vy / heading_spd

    # Full braking mask, optionally trimmed at edges (reduce onset/offset transient noise)
    brake_idx = np.where(inp.brake_mask)[0]
    if len(brake_idx) == 0:
        z = np.zeros(0)
        return AccelObs(t=z, ex=z, ey=z, a=z, sigma=z)

    # Split into contiguous brake runs; optionally trim edges
    selected = []
    runs = np.split(brake_idx, np.where(np.diff(brake_idx) > 1)[0] + 1)
    for run in runs:
        if margin > 0 and len(run) > 2 * margin:
            run = run[margin:-margin]
        elif margin > 0:
            # Short run: include all (not enough to trim)
            pass
        selected.extend(run.tolist())

    if not selected:
        z = np.zeros(0)
        return AccelObs(t=z, ex=z, ey=z, a=z, sigma=z)

    idx = np.array(sorted(selected))
    v_at = spd[idx]
    # Model-predicted decel (signed: decel negative)
    a_model = -(a_b + b_b * v_at ** 2)

    return AccelObs(
        t=inp.t[idx],
        ex=ex[idx],
        ey=ey[idx],
        a=a_model,
        sigma=np.full(len(idx), sigma),
    )


def variant_m1(inp: CaseInputs, *, sigma: float = 1.0) -> np.ndarray:
    """M1 variant: model-shape onset anchor inside kind=3.

    Parameters
    ----------
    inp : CaseInputs
    sigma : float
        Anchor noise std. Tighter = stronger pull toward the model.
        0.5 = tight, 1.0 = moderate, 2.0 = loose (sigma sensitivity test).

    Returns
    -------
    a_long : np.ndarray aligned to inp.t (m/s², signed, decel negative)
    """
    # --- fit braking frontier model from RAW a_long only ---
    fit = _fit_frontier_model(inp.v, inp.a_long_raw, inp.brake_mask)
    if fit is None:
        # Fall back to kind3 if no frontier fit (degenerate case)
        from src.physics.layer2.trajectory_refine import refine_trajectory
        ref_inp = RefineInputs(
            t=inp.t, x=inp.x, y=inp.y, tc=inp.t, v=inp.v,
            a_long=inp.a_long_raw, regime=inp.regime,
        )
        sm_fb = refine_trajectory(inp.make_smoother, ref_inp, nu_proc=_NU_PROC_DEFAULT)
        return _long_accel(sm_fb, inp.t)

    a_b, b_b = fit

    # --- cycle 1: Student-t jerk prior, get heading ---
    sm1 = inp.make_smoother(nu_proc=_NU_PROC_DEFAULT)
    sm1.fit(inp.t, inp.x, inp.y, inp.t, inp.v)
    vx1, vy1 = sm1.vel_at(inp.t)

    # --- build onset anchor from model (RAW fit, cycle-1 heading) ---
    obs = _build_onset_anchor(inp, vx1, vy1, a_b=a_b, b_b=b_b, sigma=sigma, margin=2)

    # --- cycle 2: fit with kind=3 onset anchor ---
    sm2 = inp.make_smoother(nu_proc=_NU_PROC_DEFAULT)
    sm2.fit(inp.t, inp.x, inp.y, inp.t, inp.v, accel_obs=obs)

    return _long_accel(sm2, inp.t)


def variant_m1_tight(inp: CaseInputs) -> np.ndarray:
    """M1 with sigma=0.5 (tight anchor)."""
    return variant_m1(inp, sigma=0.5)


def variant_m1_moderate(inp: CaseInputs) -> np.ndarray:
    """M1 with sigma=1.0 (moderate anchor, default)."""
    return variant_m1(inp, sigma=1.0)


def variant_m1_loose(inp: CaseInputs) -> np.ndarray:
    """M1 with sigma=2.0 (loose anchor)."""
    return variant_m1(inp, sigma=2.0)
