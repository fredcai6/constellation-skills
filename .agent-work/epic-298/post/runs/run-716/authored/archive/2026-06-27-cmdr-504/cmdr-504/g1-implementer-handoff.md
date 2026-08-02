# Implementer Handoff

## Gate
`g1` — Split smoother.py

## Task
Split `src/preprocessing/trajectory/smoother.py` (1253 lines, 4 simplification violations) into 4 new private helper modules. Add 3 internal private methods to fix function-level metrics. Everything in `src/preprocessing/trajectory/`.

## Protected Intent
Zero behavior change. Public API stays identical. The byte-identical Gaussian path and nu/nu_proc/kind=3 semantics are preserved exactly. No src/physics touch. No compatibility shims.

## Test Mode
Test-after allowed. Run the region test suite after making changes.

## Close Criteria
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/smoother.py` exits 0 (PASS)
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/_accel_obs.py src/preprocessing/trajectory/_roughness.py src/preprocessing/trajectory/_gap_metric.py src/preprocessing/trajectory/_ns_smoother.py` exits 0 (PASS)
- `py -m pytest tests/unit/preprocessing/trajectory/ -q` exits 0 (all green)
- `from src.preprocessing.trajectory.smoother import AccelObs, StintSmoother, NSStintSmoother, build_roughness, driver_series, banded_gap` succeeds in Python (public API preserved)

## Allowed Scope
Only files under `src/preprocessing/trajectory/`:
- `smoother.py` — modify (the target)
- `_accel_obs.py` — create (new)
- `_roughness.py` — create (new)
- `_gap_metric.py` — create (new)
- `_ns_smoother.py` — create (new)

No other files. Do NOT touch `__init__.py`, `calibration.py`, `grading.py`, or any test file.

## Specific Exclusions
- `src/physics/*` — entirely off-limits
- `src/preprocessing/trajectory/__init__.py` — do not touch
- Any test file — do not touch
- Any other src file — do not touch

## Constraints
- Public API: all of `AccelObs, StintSmoother, NSStintSmoother, build_roughness, driver_series, banded_gap` must remain importable from `src.preprocessing.trajectory.smoother` (re-export via late imports)
- Circular import handling: `NSStintSmoother` in `_ns_smoother.py` imports `StintSmoother` from `smoother`. To avoid circular ImportError, add `from src.preprocessing.trajectory._ns_smoother import NSStintSmoother` at the VERY END of smoother.py, after `StintSmoother` is fully defined. Python's partial module provides `StintSmoother` by then.
- All new helper modules (`_accel_obs.py`, `_roughness.py`, `_gap_metric.py`) must NOT import from `smoother.py` (no circular dependency)
- `_ns_smoother.py` imports from `smoother.py` — handled by the late-import pattern above
- AccelObs type annotation in smoother.py: after moving AccelObs to `_accel_obs.py` and importing it, update `accel_obs: "AccelObs | None"` string annotations to `accel_obs: AccelObs | None` (without quotes), or leave as string — either is fine
- The three new private methods (`_validate_smoother_params`, `_fit_frozen_frame`, `_fit_standard`) are exact semantic-preserving extractions — do NOT change any logic, variable names, or numerical values

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing — src/preprocessing/trajectory/smoother.py` is the only file being split; the trajectory subpackage is self-contained
- **Capability:** `StintSmoother` Kalman-RTS smoother + `NSStintSmoother` non-stationary extension — behavior unchanged; `AccelObs` kind=3 channel preserved
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; public API frozen; no shims/dual paths
- **Decision anchors:** Circular import handled by late NSStintSmoother import at end of smoother.py
- **Evidence expectations:** All 4 violations (CC __init__=21, CC fit=26, file_lines=1253, fn_lines fit=134) must be resolved
- **Map confidence flags:** None — high confidence, bounded file

## Step-by-step Implementation

### Step 1: Create `_accel_obs.py`

Create `src/preprocessing/trajectory/_accel_obs.py` with EXACTLY this content (copy the AccelObs class from smoother.py lines 31-51 with its imports):

```python
"""Acceleration pseudo-observation dataclass for the smoother kind=3 channel."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Acceleration pseudo-observations (kind=3)
# ---------------------------------------------------------------------------
@dataclass
class AccelObs:
    """Acceleration pseudo-observations for the smoother's ``kind=3`` channel.

    Parallel arrays.  ``a`` is the (un-biased, physics-derived) acceleration along
    the ``(ex, ey)`` unit direction at time ``t``, with per-obs std ``sigma``.  The
    smoother projects the acceleration state onto that direction and does a soft
    1-row Kalman update toward ``a`` (so ``sigma`` controls the pull strength).

    The anchor is ALWAYS external and un-biased (the raw-sensor longitudinal fit),
    never re-read from the smoothed trajectory (#498 overfitting guard).  An empty
    ``AccelObs`` (``len(t) == 0``) is treated exactly like ``None`` -> no kind=3
    rows, byte-identical to the Gaussian path.
    """

    t: np.ndarray
    ex: np.ndarray
    ey: np.ndarray
    a: np.ndarray
    sigma: np.ndarray
```

### Step 2: Create `_roughness.py`

Create `src/preprocessing/trajectory/_roughness.py` with EXACTLY these two functions (copy from smoother.py lines 1105-1179):

```python
"""Roughness profile builders for NSStintSmoother (E11)."""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Roughness profile builders (E11)
# ---------------------------------------------------------------------------
def driver_series(
    t: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    V: np.ndarray,
    kind: str,
    smooth_n: int = 7,
) -> np.ndarray:
    """State-dependent roughness driver g(t) from a path/speed estimate.

    Parameters
    ----------
    kind : str — one of 'lon', 'tot', 'lat':
        'lon' : |dv/dt|        longitudinal-accel demand (brake/throttle)
        'tot' : |a_vec|        total accel magnitude (friction-circle demand)
        'lat' : |kappa| v^2    pure-lateral demand (E7 control lever)

    Returns non-negative array of length len(t).
    """
    if kind not in ("lon", "tot", "lat"):
        raise ValueError(
            f"kind must be one of 'lon', 'tot', 'lat'; got {kind!r}"
        )
    t = np.asarray(t, float)
    vx = np.gradient(X, t)
    vy = np.gradient(Y, t)
    ax = np.gradient(vx, t)
    ay = np.gradient(vy, t)
    if kind == "lat":
        sp = np.sqrt(np.maximum(vx * vx + vy * vy, 1e-9))
        g = np.abs(vx * ay - vy * ax) / sp
    elif kind == "tot":
        g = np.sqrt(ax * ax + ay * ay)
    else:  # 'lon'
        g = np.abs(np.gradient(V, t))
    if smooth_n > 1 and len(g) >= smooth_n:
        k = np.ones(smooth_n) / smooth_n
        g = np.convolve(g, k, mode="same")
    return np.maximum(g, 0.0)


def build_roughness(
    t: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    V: np.ndarray,
    kind: str,
    lam: float,
    a_ref: float | None = None,
    smooth_n: int = 7,
    r_max: float = 12.0,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    """Build (t, r, a_ref, g) where r(t) = 1 + lam * g(t) / a_ref.

    a_ref defaults to the 90th percentile of the positive driver values
    (the corner-demand scale), so lam ~ O(1) means ~2x jerk variance at
    typical corner demand.  r is capped at r_max (E10 pitfall guard).

    Returns
    -------
    t_drv : array — time knots (same as input t)
    r_drv : array — roughness values, clipped to [1, r_max]
    a_ref : float — demand reference scale used
    g     : array — raw driver values
    """
    g = driver_series(t, X, Y, V, kind, smooth_n=smooth_n)
    if a_ref is None:
        pos = g[g > 0]
        a_ref_val = float(np.percentile(pos, 90)) if len(pos) else 1.0
        a_ref_val = max(a_ref_val, 1e-9)
    else:
        a_ref_val = float(a_ref)
    r = 1.0 + lam * (g / a_ref_val)
    r = np.clip(r, 1.0, r_max)
    return np.asarray(t, float), r, a_ref_val, g
```

### Step 3: Create `_gap_metric.py`

Create `src/preprocessing/trajectory/_gap_metric.py` with EXACTLY these two functions (copy from smoother.py lines 1185-1253):

```python
"""Banded locus gap metric (E7/E8/E9)."""
from __future__ import annotations

from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Locus metric
# ---------------------------------------------------------------------------
def banded_gap(
    tq: np.ndarray,
    Xq: np.ndarray,
    Yq: np.ndarray,
    Vq: np.ndarray,
) -> dict:
    """S_geo - S_spd banded decomposition (E7/E8/E9 locus metric).

    Returns a dict with 'S_geo', 'S_spd', 'gap_total_m', 'gap_total_pct',
    and 'bands' (per-speed-band breakdown).
    """
    tq = np.asarray(tq, float)
    dt = np.diff(tq)
    dgeo = np.sqrt(np.diff(Xq) ** 2 + np.diff(Yq) ** 2)
    dspd = 0.5 * (Vq[1:] + Vq[:-1]) * dt
    vkmh = 0.5 * (Vq[1:] + Vq[:-1]) * 3.6
    vx = np.gradient(Xq, tq)
    vy = np.gradient(Yq, tq)
    ax = np.gradient(vx, tq)
    ay = np.gradient(vy, tq)
    sp2 = vx * vx + vy * vy
    kap = np.abs(vx * ay - vy * ax) / np.power(np.maximum(sp2, 1e-6), 1.5)
    kap = 0.5 * (kap[1:] + kap[:-1])
    gap = dgeo - dspd
    out: dict[str, Any] = dict(
        S_geo=float(dgeo.sum()),
        S_spd=float(dspd.sum()),
        gap_total_m=float(gap.sum()),
        gap_total_pct=float(100 * gap.sum() / max(dspd.sum(), 1e-9)),
    )
    bands = _banded_gap_bands(gap, dspd, vkmh, kap)
    out["bands"] = bands
    return out


def _banded_gap_bands(
    gap: np.ndarray,
    dspd: np.ndarray,
    vkmh: np.ndarray,
    kap: np.ndarray,
) -> dict:
    bands: dict = {}
    for name, lo, hi in [
        ("straight>=290", 290, 1e9),
        ("240-290", 240, 290),
        ("180-240", 180, 240),
        ("corner<180", 0, 180),
    ]:
        b = (vkmh >= lo) & (vkmh < hi)
        if b.sum() == 0:
            continue
        s = dspd[b].sum()
        bands[name] = dict(
            gap_m=float(gap[b].sum()),
            arc_m=float(s),
            m_per_km=float(1000 * gap[b].sum() / s) if s else None,
            n=int(b.sum()),
        )
    kc = np.percentile(kap, 75)
    msk = kap >= kc
    bands["high_kappa_corner"] = dict(
        gap_m=float(gap[msk].sum()),
        arc_m=float(dspd[msk].sum()),
        m_per_km=float(
            1000 * gap[msk].sum() / max(dspd[msk].sum(), 1e-9)
        ),
        n=int(msk.sum()),
    )
    return bands
```

### Step 4: Create `_ns_smoother.py`

Create `src/preprocessing/trajectory/_ns_smoother.py` with EXACTLY the NSStintSmoother class (copy from smoother.py lines 986-1099, adjusted imports):

```python
"""Non-stationary StintSmoother extension (E11)."""
from __future__ import annotations

import numpy as np
from scipy import linalg

from src.preprocessing.trajectory.dynamics import _block6, discretize, matern52_sde
from src.preprocessing.trajectory.smoother import StintSmoother


# ---------------------------------------------------------------------------
# Non-stationary extension: NSStintSmoother
# ---------------------------------------------------------------------------
class NSStintSmoother(StintSmoother):
    """E10 StintSmoother with STATE-DEPENDENT per-step jerk process variance.

    A roughness profile r(t) >= 1 multiplies the ACC-state process-noise in the
    discrete Q at each step.  r(t) supplied as (t_drv, r_drv) knots; r is
    interpolated to each merged-timeline step midpoint and capped at r_max.

    LIMIT: r==1 everywhere => Q==Q0 => identical to E10 StintSmoother (to
    ~1e-10, verified by self-test and required by g2 nesting gate).
    """

    def __init__(
        self,
        ell: float,
        sf: float,
        sig_pos: float,
        delta: float,
        sig_spd: float,
        iters: int = 2,
        t_drv: np.ndarray | None = None,
        r_drv: np.ndarray | None = None,
        r_max: float = 12.0,
        order: int = 3,
        sig_pos_cross: float | None = None,
        sig_t_along: float | None = None,
        nu: float | None = None,
        nu_proc: float | None = None,
    ) -> None:
        # order=3 (5/2) keeps the byte-exact per-axis path (matern52 + _block6),
        # required by the nesting gate.  order>=4 (7/2) uses the generic full-Q
        # scaling: r(t) scales the discrete process noise, which for any order
        # injects only into the top derivative -> r>1 lets that derivative (snap
        # for 7/2) follow fast transients.  The obs-model knobs (anisotropic cross,
        # additive timing along, Student-t nu) are forwarded so a non-stationary
        # fit COMPOSES with the honest observation model.
        super().__init__(
            ell, sf, sig_pos, delta, sig_spd=sig_spd, iters=iters, order=order,
            sig_pos_cross=sig_pos_cross, sig_t_along=sig_t_along, nu=nu, nu_proc=nu_proc,
        )
        self.r_max = float(r_max)
        if t_drv is not None and r_drv is not None:
            self.t_drv = np.asarray(t_drv, float)
            self.r_drv = np.clip(np.asarray(r_drv, float), 1.0, self.r_max)
        else:
            self.t_drv = None
            self.r_drv = None
        if self.order == 3:
            self._Fx, _, self._Pinf_x = matern52_sde(self.ell, self.sf)

    def _r_at(self, t: float) -> float:
        if self.t_drv is None or self.r_drv is None:
            return 1.0
        r = float(np.interp(t, self.t_drv, self.r_drv))
        return float(min(max(r, 1.0), self.r_max))

    def _precompute_steps(
        self, ts: np.ndarray
    ) -> tuple[list, list, list]:
        """Override: per-step (Phi, Q) with r(t) modulation.

        Phi depends only on dt (cached); Q is r-scaled per step, evaluated at the
        step midpoint.  Scaling Q by r scales the white-noise injection on the top
        derivative by r, letting it follow fast transients in corners while leaving
        straights (r~1) untouched.  r==1 => Q = Q0 (exact stationary limit).

        order==3 keeps the byte-exact per-axis 5/2 path; order>=4 scales the full
        discrete Q from ``discretize`` (the same Q0 the stationary smoother uses,
        so r==1 byte-reproduces it).

        Returns (Phis, Qs, Qs_nominal).  Qs is r-scaled; Qs_nominal is the pre-r Q0
        per step, which the Student-t jerk prior IRLS standardizes the jerk increment
        against (reviewer C2/C3 -- standardize against the nominal prior, not the
        r-inflated one).  The two scalings compose at the predict step: Qs_nominal*r
        is Qs, and the jerk prior further inflates Qs by 1/_w_proc.
        """
        if self.order != 3:
            dts = np.diff(ts)
            cache: dict = {}
            Phis: list = [None]
            Qs: list = [None]
            Qs_nominal: list = [None]
            for i, dt in enumerate(dts):
                key = round(float(dt), 5)
                if key not in cache:
                    cache[key] = discretize(self.F, self.Pinf, max(dt, 1e-9))
                Phi, Q0 = cache[key]
                tmid = 0.5 * (ts[i] + ts[i + 1])
                r = self._r_at(tmid)
                Phis.append(Phi)
                Qs.append(Q0 if r == 1.0 else r * Q0)
                Qs_nominal.append(Q0)
            return Phis, Qs, Qs_nominal
        # order==3: byte-exact 5/2 per-axis path.
        dts = np.diff(ts)
        phi_cache: dict = {}
        Phis = [None]
        Qs = [None]
        Qs_nominal = [None]
        for i, dt in enumerate(dts):
            key = round(float(dt), 5)
            if key not in phi_cache:
                Phi_x = linalg.expm(self._Fx * max(dt, 1e-9))
                Q0_x = self._Pinf_x - Phi_x @ self._Pinf_x @ Phi_x.T
                Q0_x = 0.5 * (Q0_x + Q0_x.T)
                phi_cache[key] = (Phi_x, Q0_x)
            Phi_x, Q0_x = phi_cache[key]
            tmid = 0.5 * (ts[i] + ts[i + 1])
            r = self._r_at(tmid)
            Phi = _block6(Phi_x, Phi_x)
            Q = _block6(r * Q0_x, r * Q0_x)
            Phis.append(Phi)
            Qs.append(Q)
            Qs_nominal.append(_block6(Q0_x, Q0_x))
        return Phis, Qs, Qs_nominal
```

**CRITICAL**: Note that `NSStintSmoother.__init__` in the original smoother.py has `sig_spd: float = SIG_SPD` with a default. In `_ns_smoother.py`, change it to `sig_spd: float` (no default) to avoid needing to import `SIG_SPD` here. The caller always provides it. Wait — actually check if any test constructs NSStintSmoother without sig_spd. If yes, keep the default by also importing SIG_SPD. SAFE CHOICE: import `SIG_SPD` from dynamics and keep the default `sig_spd: float = SIG_SPD`.

Correct `_ns_smoother.py` imports line to:
```python
from src.preprocessing.trajectory.dynamics import SIG_SPD, _block6, discretize, matern52_sde
```
And keep the `__init__` signature with `sig_spd: float = SIG_SPD`.

### Step 5: Rewrite `smoother.py`

The new `smoother.py` has:
1. Module docstring (unchanged)
2. Imports: same as before PLUS `from src.preprocessing.trajectory._accel_obs import AccelObs` and `from src.preprocessing.trajectory._roughness import build_roughness, driver_series` and `from src.preprocessing.trajectory._gap_metric import banded_gap`
3. New module-level function `_validate_smoother_params()` (before `StintSmoother`)
4. `StintSmoother` class with:
   - `__init__` that calls `_validate_smoother_params()` instead of the 9 validation ifs
   - All other methods UNCHANGED
   - NEW private methods `_fit_frozen_frame()` and `_fit_standard()`
   - `fit()` refactored to call `_fit_frozen_frame` or `_fit_standard`
5. At the VERY END of the file: `from src.preprocessing.trajectory._ns_smoother import NSStintSmoother  # noqa: E402`
6. NO `NSStintSmoother` class (moved to `_ns_smoother.py`)
7. NO roughness functions (moved to `_roughness.py`)
8. NO gap functions (moved to `_gap_metric.py`)
9. NO `AccelObs` class body (moved to `_accel_obs.py`)

#### New import section (top of smoother.py, after module docstring):

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import linalg

from src.preprocessing.trajectory._accel_obs import AccelObs
from src.preprocessing.trajectory._gap_metric import banded_gap
from src.preprocessing.trajectory._roughness import build_roughness, driver_series
from src.preprocessing.trajectory.dynamics import (
    SIG_SPD,
    SIG_SPD_MIN,
    _block6,
    discretize,
    matern52_sde,
    matern_sde,
)
```

Note: keep `from dataclasses import dataclass` and `from typing import Any` even though AccelObs/banded_gap moved — check if they're still used in smoother.py. `dataclass` is NOT used in smoother.py after moving AccelObs (remove it). `Any` is NOT used in smoother.py after moving banded_gap (remove it). Remove them from imports.

Correct new import section:
```python
from __future__ import annotations

import numpy as np
from scipy import linalg

from src.preprocessing.trajectory._accel_obs import AccelObs
from src.preprocessing.trajectory._gap_metric import banded_gap
from src.preprocessing.trajectory._roughness import build_roughness, driver_series
from src.preprocessing.trajectory.dynamics import (
    SIG_SPD,
    SIG_SPD_MIN,
    _block6,
    discretize,
    matern52_sde,
    matern_sde,
)
```

#### New `_validate_smoother_params()` function (add just BEFORE `StintSmoother` class):

```python
# ---------------------------------------------------------------------------
# Hyperparameter validation (shared by StintSmoother and NSStintSmoother)
# ---------------------------------------------------------------------------
def _validate_smoother_params(
    ell: float,
    sf: float,
    sig_pos: float,
    order: int,
    sig_pos_cross: float | None,
    sig_t_along: float | None,
    nu: float | None,
    nu_proc: float | None,
) -> None:
    """Validate StintSmoother/NSStintSmoother constructor hyperparameters."""
    if ell <= 0:
        raise ValueError(f"ell must be positive; got {ell!r}")
    if sf <= 0:
        raise ValueError(f"sf must be positive; got {sf!r}")
    if sig_pos <= 0:
        raise ValueError(f"sig_pos must be positive; got {sig_pos!r}")
    if order < 3:
        raise ValueError(f"order must be >= 3 (Matern-5/2); got {order!r}")
    if sig_pos_cross is not None and sig_pos_cross <= 0:
        raise ValueError(f"sig_pos_cross must be positive; got {sig_pos_cross!r}")
    if sig_t_along is not None and sig_t_along <= 0:
        raise ValueError(f"sig_t_along must be positive; got {sig_t_along!r}")
    if nu is not None and nu <= 0:
        raise ValueError(f"nu (Student-t dof) must be positive; got {nu!r}")
    if nu_proc is not None and nu_proc <= 0:
        raise ValueError(f"nu_proc (Student-t jerk dof) must be positive; got {nu_proc!r}")
    if nu_proc is not None and order < 4:
        raise ValueError(
            f"nu_proc requires order>=4 (jerk is the top state only for Matern-7/2); got order={order!r}"
        )
```

#### Refactored `__init__` (replace the 9 validation ifs at lines 90-109 with a single call):

After `def __init__(self, ...) -> None:`, replace lines 90-109 with:
```python
        _validate_smoother_params(ell, sf, sig_pos, order, sig_pos_cross, sig_t_along, nu, nu_proc)
```
Everything from line 110 onward in `__init__` (`self.ell = float(ell)` etc.) stays UNCHANGED.

#### New private methods `_fit_frozen_frame` and `_fit_standard` (add BEFORE the existing `fit` method):

Add these two methods BEFORE `def fit(self, ...)`. They contain the code extracted from the two branches of `fit`:

```python
    def _fit_frozen_frame(
        self,
        ts: np.ndarray,
        kind: np.ndarray,
        payX: np.ndarray,
        payY: np.ndarray,
        payV: np.ndarray,
        payAX: np.ndarray,
        payAY: np.ndarray,
        payAval: np.ndarray,
        payAsig: np.ndarray,
        lin_vel: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, dict]:
        """Frozen-frame forward-backward; relinearise IRLS weights at the fixed frame."""
        self._w_obs = np.ones(len(ts)) if self.nu is not None else None
        # Student-t jerk PROCESS IRLS also iterates at the frozen frame: the frame
        # stays fixed, only the per-step jerk down-weights update (mirrors _w_obs).
        self._w_proc = np.ones(len(ts)) if self.nu_proc is not None else None
        irls = self.nu is not None or self.nu_proc is not None
        n_pass = max(self.iters, 1) if irls else 1
        for it in range(n_pass):
            fwd = self._forward(
                ts, kind, payX, payY, payV,
                payAX=payAX, payAY=payAY, payAval=payAval, payAsig=payAsig,
                lin_vel=lin_vel,
            )
            m_s, P_s = self._backward(fwd)
            if not irls:
                break
            wconv = True
            if self.nu is not None:
                new_w = self._obs_weights(m_s, P_s, kind, payX, payY, payV, lin_vel)
                wconv = float(np.max(np.abs(new_w - self._w_obs))) < 1e-3
                self._w_obs = new_w
            proc_conv = True
            if self.nu_proc is not None:
                new_wp = self._proc_weights(m_s, fwd["Phis"], fwd["Qs_nominal"])
                proc_conv = float(np.max(np.abs(new_wp - self._w_proc))) < 1e-3
                self._w_proc = new_wp
            if wconv and proc_conv:
                break
        self._last_lin_dmax = 0.0
        self._n_iter_done = it + 1
        return m_s, P_s, fwd

    def _fit_standard(
        self,
        ts: np.ndarray,
        kind: np.ndarray,
        payX: np.ndarray,
        payY: np.ndarray,
        payV: np.ndarray,
        payAX: np.ndarray,
        payAY: np.ndarray,
        payAval: np.ndarray,
        payAsig: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, dict]:
        """Standard iterated-EKF: relinearise the velocity frame each pass."""
        lin_vel = None
        # Student-t IRLS: alternate (state | per-obs weights).  None -> Gaussian
        # (weights stay None so the update path is byte-identical).
        self._w_obs = np.ones(len(ts)) if self.nu is not None else None
        # Student-t jerk PROCESS IRLS: alternate (state | per-step jerk down-weights).
        # None -> Gaussian smoothness (weights stay None so the predict path is byte-identical).
        self._w_proc = np.ones(len(ts)) if self.nu_proc is not None else None
        for it in range(max(self.iters, 1)):
            fwd = self._forward(
                ts, kind, payX, payY, payV,
                payAX=payAX, payAY=payAY, payAval=payAval, payAsig=payAsig,
                lin_vel=lin_vel,
            )
            m_s, P_s = self._backward(fwd)
            new_lin = np.column_stack([m_s[:, self.iVX], m_s[:, self.iVY]])
            dmax = float(np.max(np.abs(new_lin - lin_vel))) if lin_vel is not None else np.inf
            lin_vel = new_lin
            self._last_lin_dmax = dmax if np.isfinite(dmax) else None
            wconv = True
            if self.nu is not None:
                new_w = self._obs_weights(m_s, P_s, kind, payX, payY, payV, new_lin)
                wconv = float(np.max(np.abs(new_w - self._w_obs))) < 1e-3
                self._w_obs = new_w
            proc_conv = True
            if self.nu_proc is not None:
                new_wp = self._proc_weights(m_s, fwd["Phis"], fwd["Qs_nominal"])
                proc_conv = float(np.max(np.abs(new_wp - self._w_proc))) < 1e-3
                self._w_proc = new_wp
            if dmax < 1e-3 and wconv and proc_conv:
                break
        self._n_iter_done = it + 1
        return m_s, P_s, fwd
```

#### Refactored `fit` method (replace lines 740-813 with the dispatch version):

Keep everything BEFORE line 740 in `fit` exactly as-is (lines 680-739: docstring, array conversions, validation, trend detrend, timeline build, ts_index, ts/kind assignment). Then replace the `if lin_vel_frozen is not None: ... else: ...` block and the final assignments with:

```python
        if lin_vel_frozen is not None:
            lin_vel = np.asarray(lin_vel_frozen, float)
            m_s, P_s, fwd = self._fit_frozen_frame(
                ts, kind, payX, payY, payV, payAX, payAY, payAval, payAsig, lin_vel
            )
        else:
            m_s, P_s, fwd = self._fit_standard(
                ts, kind, payX, payY, payV, payAX, payAY, payAval, payAsig
            )
        self.m_s = m_s
        self.P_s = P_s
        self._fwd = fwd
        self._payX = payX
        self._payY = payY
        self._payV = payV
        self._fitted = True
        return self
```

Note: `self._n_iter_done` is now set inside `_fit_frozen_frame` and `_fit_standard`. `self._last_lin_dmax` is also set inside the helpers. Remove those from `fit`'s tail.

#### End of smoother.py (after all class definitions, REPLACE the NSStintSmoother/roughness/gap sections):

Remove lines 983-1253 (NSStintSmoother, roughness, banded_gap) and instead add at the very end:

```python

# ---------------------------------------------------------------------------
# Re-exports for backward-compatible public API
# ---------------------------------------------------------------------------
# NSStintSmoother is defined in _ns_smoother.py, which imports StintSmoother
# from this module.  This late import works because StintSmoother is already
# registered in the partial module by the time _ns_smoother loads it.
from src.preprocessing.trajectory._ns_smoother import NSStintSmoother  # noqa: E402
```

## Required Evidence
1. Terminal output of: `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/smoother.py` showing PASS
2. Terminal output of: `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/_accel_obs.py src/preprocessing/trajectory/_roughness.py src/preprocessing/trajectory/_gap_metric.py src/preprocessing/trajectory/_ns_smoother.py` showing PASS
3. Terminal output of: `py -m pytest tests/unit/preprocessing/trajectory/ -q` showing all passed

## Verification Commands

Run from worktree root `C:/Programs/f1Brainz-worktrees/509-504`:

```bash
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/smoother.py
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/_accel_obs.py src/preprocessing/trajectory/_roughness.py src/preprocessing/trajectory/_gap_metric.py src/preprocessing/trajectory/_ns_smoother.py
py -m pytest tests/unit/preprocessing/trajectory/ -q
```

## Suggested Model Tier
`simple bounded` — the implementation is fully specified; no ambiguous algorithmic decisions.

## Authority
All decisions are pre-made in this handoff. The implementer must NOT:
- Change any algorithmic logic, numerical constants, or variable names
- Add any shims or compatibility layers
- Touch any file outside `src/preprocessing/trajectory/`
- Restructure class hierarchies

## Stop Conditions
Stop and return if:
- A test fails that cannot be explained by a transcription error in following these instructions
- An import cycle occurs that cannot be resolved by the late-import pattern specified
- A file outside the allowed scope must be touched to make tests pass

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
