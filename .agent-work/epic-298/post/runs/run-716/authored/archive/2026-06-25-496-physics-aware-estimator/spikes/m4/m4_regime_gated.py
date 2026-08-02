"""M4 spike — Regime-gated process noise for trajectory smoother (#496/#507).

Mechanism: Inflate the jerk process variance ONLY inside brake-onset windows,
so the Matern prior stops penalizing the physically-expected decel step exactly
where a transient belongs — while staying tight elsewhere to avoid ringing.

Uses NSStintSmoother with a custom roughness schedule r(t):
  - r(t) = gate_strength  in a window [onset - lead_s, onset + trail_s]
  - r(t) = 1.0            everywhere else

Brake onsets are detected from two signals (combined OR):
  1. Regime transition into "straight_brake" (regime array)
  2. Large negative raw speed derivative: dv/dt < -thresh_g * 9.81 (m/s²)

This is a PURE process-noise mechanism — NO kind=3 anchor is added.
The two-cycle invariant (decision:two_cycle_external_anchor_design) is NOT
touched: anchor source and placement are unchanged (we add no anchor at all).

Seam: VariantFn = Callable[[CaseInputs], np.ndarray] as defined in scoreboard.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from src.physics.layer2.scoreboard import CaseInputs, _long_accel
from src.preprocessing.trajectory.smoother import NSStintSmoother


# ---------------------------------------------------------------------------
# Parameters dataclass for sweep
# ---------------------------------------------------------------------------

@dataclass
class M4Params:
    """Hyperparameters for M4 regime-gated process noise.

    gate_strength  : r(t) multiplier inside brake-onset windows (>= 1.0)
    lead_s         : seconds BEFORE onset to inflate process noise (key: the
                     prior must loosen BEFORE the step, not just after)
    trail_s        : seconds AFTER onset to keep inflation active
    thresh_g       : threshold on |dv/dt| in g's for speed-derivative detection
    use_regime     : if True, use regime transitions as onset signal
    use_dv         : if True, use speed derivative as onset signal
    nu_proc        : Student-t jerk prior dof (None = Gaussian; 4.0 matches kind3)
    r_max          : cap on roughness (passed to NSStintSmoother)
    """
    gate_strength: float = 6.0
    lead_s: float = 0.3
    trail_s: float = 0.5
    thresh_g: float = 1.5        # |dv/dt| > thresh_g * g treated as hard braking
    use_regime: bool = True
    use_dv: bool = True
    nu_proc: float | None = None  # None = Gaussian process prior (cleaner isolation)
    r_max: float = 12.0


# ---------------------------------------------------------------------------
# Roughness schedule builder
# ---------------------------------------------------------------------------

def _detect_brake_onsets(
    t: np.ndarray,
    v: np.ndarray,
    regime: np.ndarray,
    *,
    use_regime: bool = True,
    use_dv: bool = True,
    thresh_g: float = 1.5,
) -> np.ndarray:
    """Return array of onset timestamps (seconds).

    An onset is detected when:
      (use_regime) the regime transitions from non-brake to straight_brake, OR
      (use_dv)     dv/dt drops below -thresh_g * 9.81 m/s² (centred diff)
    """
    onsets: list[float] = []

    if use_regime:
        is_brake = regime == "straight_brake"
        # Transition: False -> True in consecutive samples
        for i in range(1, len(is_brake)):
            if is_brake[i] and not is_brake[i - 1]:
                onsets.append(float(t[i]))

    if use_dv:
        dv = np.gradient(v, t)   # centred diff, m/s²
        thresh = -thresh_g * 9.81
        is_hard = dv < thresh
        for i in range(1, len(is_hard)):
            if is_hard[i] and not is_hard[i - 1]:
                onsets.append(float(t[i]))

    # Deduplicate onsets that are within 0.2 s of each other
    if not onsets:
        return np.array([], dtype=float)
    onsets_sorted = sorted(set(onsets))
    merged: list[float] = [onsets_sorted[0]]
    for o in onsets_sorted[1:]:
        if o - merged[-1] > 0.2:
            merged.append(o)
    return np.array(merged, dtype=float)


def build_m4_roughness(
    t: np.ndarray,
    v: np.ndarray,
    regime: np.ndarray,
    params: M4Params,
) -> tuple[np.ndarray, np.ndarray]:
    """Build (t_drv, r_drv) roughness schedule for NSStintSmoother.

    Returns
    -------
    t_drv : same as input t (dense knots)
    r_drv : 1.0 everywhere except gate_strength in onset windows
    """
    onsets = _detect_brake_onsets(
        t, v, regime,
        use_regime=params.use_regime,
        use_dv=params.use_dv,
        thresh_g=params.thresh_g,
    )

    r = np.ones(len(t), dtype=float)

    for onset in onsets:
        window = (t >= onset - params.lead_s) & (t <= onset + params.trail_s)
        r[window] = params.gate_strength

    # Clip to [1, r_max]
    r = np.clip(r, 1.0, params.r_max)
    return t.copy(), r


# ---------------------------------------------------------------------------
# Variant function factory
# ---------------------------------------------------------------------------

def make_m4_variant(params: M4Params | None = None) -> Callable[[CaseInputs], np.ndarray]:
    """Return a VariantFn using M4 regime-gated process noise.

    The returned function reads calibrated HPs from inp.make_smoother(),
    then constructs an NSStintSmoother with the M4 roughness schedule.
    No kind=3 anchor is added — pure process-noise isolation.
    """
    if params is None:
        params = M4Params()

    def _variant_m4(inp: CaseInputs) -> np.ndarray:
        # Extract calibrated HPs from a dummy smoother instance
        _sm_dummy = inp.make_smoother(nu_proc=None)
        ell = _sm_dummy.ell
        sf = _sm_dummy.sf
        sig_pos = _sm_dummy.sig_pos
        delta = _sm_dummy.delta
        sig_spd = _sm_dummy.sig_spd
        iters = _sm_dummy.iters

        # Build the regime-gated roughness schedule
        t_drv, r_drv = build_m4_roughness(inp.t, inp.v, inp.regime, params)

        # Construct NSStintSmoother with roughness + optional nu_proc
        sm = NSStintSmoother(
            ell=ell,
            sf=sf,
            sig_pos=sig_pos,
            delta=delta,
            sig_spd=sig_spd,
            iters=iters,
            t_drv=t_drv,
            r_drv=r_drv,
            r_max=params.r_max,
            order=4,           # Matern-7/2; required for nu_proc + differentiable acc
            nu_proc=params.nu_proc,
        )
        sm.fit(inp.t, inp.x, inp.y, inp.t, inp.v)
        return _long_accel(sm, inp.t)

    return _variant_m4


# ---------------------------------------------------------------------------
# Default "m4" variant (used in scoreboard)
# ---------------------------------------------------------------------------
VARIANT_M4_DEFAULT = make_m4_variant(M4Params(
    gate_strength=6.0,
    lead_s=0.3,
    trail_s=0.5,
    thresh_g=1.5,
    use_regime=True,
    use_dv=True,
    nu_proc=None,
    r_max=12.0,
))
