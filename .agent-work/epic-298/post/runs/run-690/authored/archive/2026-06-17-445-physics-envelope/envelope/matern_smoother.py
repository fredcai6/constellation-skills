"""Generic Matern-order windowless Kalman-RTS smoother (#445 acceleration poke).

Production smoother is Matern-5/2: state [f,fd,fdd] per axis, white noise on JERK,
so acceleration is continuous but NOT differentiable. Hypothesis (human): push the
white noise up one derivative -> Matern-7/2, state [f,fd,fdd,fddd], white noise on
SNAP, so jerk is the random process and ACCELERATION IS DIFFERENTIABLE. Physically
truer; the question is whether the data (4.2Hz pos + interleaved speed) supports it
or whether a sits below the noise floor and the extra regularity is unfalsifiable prior.

This vendors a generic per-axis-order smoother (additive; no src/ edits). P_inf for any
order via the continuous Lyapunov solve, scaled to sf^2 (exact stationary cov of the
SDE = exact Matern marginal). order=3 self-checks against the production StintSmoother.

State layout (joint, per-axis order d): X states [0..d-1], Y states [d..2d-1].
pos=(0,d)  vel=(1,d+1)  acc=(2,d+2).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy import linalg

sys.path.insert(0, "C:/Programs/f1Brainz")
from src.preprocessing.trajectory.dynamics import SIG_SPD  # noqa: E402


def matern_sde(ell: float, sf: float, order: int):
    """F (d,d), L (d,1), P_inf (d,d) for a Matern-(order-1/2) GP.

    order=3 -> Matern-5/2 (lam=sqrt(5)/ell); order=4 -> Matern-7/2 (lam=sqrt(7)/ell).
    F = companion of (s+lam)^order; L = e_d; P_inf from Lyapunov scaled to P_inf[0,0]=sf^2.
    """
    nu = order - 0.5
    lam = math.sqrt(2.0 * nu) / ell
    # companion of (s+lam)^order: coeffs a_k = C(order,k) lam^(order-k), k=0..order-1
    F = np.zeros((order, order))
    for k in range(order - 1):
        F[k, k + 1] = 1.0
    F[-1, :] = [-math.comb(order, k) * lam ** (order - k) for k in range(order)]
    L = np.zeros((order, 1)); L[-1, 0] = 1.0
    P1 = linalg.solve_continuous_lyapunov(F, -(L @ L.T))     # q=1
    P_inf = P1 * (sf * sf / P1[0, 0])
    P_inf = 0.5 * (P_inf + P_inf.T)
    return F, L, P_inf


def _blockJ(Ax, d):
    M = np.zeros((2 * d, 2 * d))
    M[:d, :d] = Ax
    M[d:, d:] = Ax
    return M


def discretize(F, P_inf, dt):
    Phi = linalg.expm(F * dt)
    Q = P_inf - Phi @ P_inf @ Phi.T
    return Phi, 0.5 * (Q + Q.T)


class MaternSmoother:
    """Windowless iterated-EKF Kalman-RTS smoother, generic per-axis Matern order."""

    def __init__(self, ell, sf, sig_pos, delta, order=3, sig_spd=SIG_SPD, iters=2):
        self.ell = float(ell); self.sf = float(sf); self.sig_pos = float(sig_pos)
        self.delta = float(delta); self.sig_spd = float(sig_spd); self.iters = int(iters)
        self.d = int(order); self.dim = 2 * self.d
        Fx, _Lx, Pinf = matern_sde(self.ell, self.sf, self.d)
        self._Fx = Fx; self._Pinf_x = Pinf
        self.F = _blockJ(Fx, self.d)
        self.Pinf = _blockJ(Pinf, self.d)
        self.iX, self.iY = 0, self.d          # position indices
        self.iVX, self.iVY = 1, self.d + 1    # velocity indices
        self.iAX, self.iAY = 2, self.d + 2    # acceleration indices

    # ---- timeline (identical to production) -------------------------------
    def _build_timeline(self, tp, yX, yY, tc, yV, extra=None):
        tsp = np.asarray(tp, float); tss = np.asarray(tc, float) + self.delta
        tex = np.asarray(extra, float) if extra is not None else np.zeros(0)
        n = len(tsp) + len(tss) + len(tex)
        ts = np.empty(n); kind = np.empty(n, np.int8)
        a, b = len(tsp), len(tsp) + len(tss)
        ts[:a] = tsp; kind[:a] = 0; ts[a:b] = tss; kind[a:b] = 1; ts[b:] = tex; kind[b:] = 2
        order = np.argsort(ts, kind="mergesort")
        ts = ts[order]; kind = kind[order]
        payX = np.full(n, np.nan); payY = np.full(n, np.nan); payV = np.full(n, np.nan)
        payX[:a] = yX; payY[:a] = yY; payV[a:b] = yV
        return ts, kind, payX[order], payY[order], payV[order]

    def _precompute_steps(self, ts):
        dts = np.diff(ts); cache = {}; Phis = [None]; Qs = [None]
        for dt in dts:
            key = round(float(dt), 5)
            if key not in cache:
                cache[key] = discretize(self.F, self.Pinf, max(dt, 1e-9))
            Phi, Q = cache[key]; Phis.append(Phi); Qs.append(Q)
        return Phis, Qs

    def _init_P0(self):
        P = np.zeros((self.dim, self.dim))
        P[self.iX, self.iX] = 1e6; P[self.iY, self.iY] = 1e6
        P[self.iVX, self.iVX] = 1e4; P[self.iVY, self.iVY] = 1e4
        # acc and any higher states: stationary marginal from Pinf
        for j in range(2, self.d):
            P[j, j] = self.Pinf[j, j]
            P[self.d + j, self.d + j] = self.Pinf[self.d + j, self.d + j]
        return P

    def _update_pos(self, mp, Pp, px, py, sp2, Iv):
        H = np.zeros((2, self.dim)); H[0, self.iX] = 1.0; H[1, self.iY] = 1.0
        yv = np.array([px, py]); R = np.diag([sp2, sp2])
        S = H @ Pp @ H.T + R; K = Pp @ H.T @ linalg.inv(S)
        m = mp + K @ (yv - H @ mp); P = (Iv - K @ H) @ Pp
        return m, P

    def _update_speed(self, mp, Pp, pv, sv2, vtx, vty, lv_i, Iv):
        if lv_i is not None:
            xd0, yd0 = lv_i
        else:
            xd0, yd0 = mp[self.iVX], mp[self.iVY]
        fx0 = xd0 + vtx; fy0 = yd0 + vty
        spd0 = max(np.hypot(fx0, fy0), 1e-6); jx = fx0 / spd0; jy = fy0 / spd0
        H = np.zeros((1, self.dim)); H[0, self.iVX] = jx; H[0, self.iVY] = jy
        pred = spd0 + jx * (mp[self.iVX] - xd0) + jy * (mp[self.iVY] - yd0)
        S = float((H @ Pp @ H.T)[0, 0]) + sv2; K = (Pp @ H.T) / S
        m = mp + K[:, 0] * (pv - pred); P = (Iv - np.outer(K[:, 0], H[0])) @ Pp
        return m, P

    def _forward(self, ts, kind, payX, payY, payV, lin_vel=None):
        vtx, vty = self._vtrend_x, self._vtrend_y
        n = len(ts); Phis, Qs = self._precompute_steps(ts)
        m = np.zeros(self.dim); P = self._init_P0()
        m_f = np.empty((n, self.dim)); P_f = np.empty((n, self.dim, self.dim))
        m_p = np.empty((n, self.dim)); P_p = np.empty((n, self.dim, self.dim))
        sp2 = self.sig_pos ** 2; sv2 = self.sig_spd ** 2; Iv = np.eye(self.dim)
        for i in range(n):
            if i == 0:
                mp, Pp = m, P
            else:
                mp = Phis[i] @ m; Pp = Phis[i] @ P @ Phis[i].T + Qs[i]; Pp = 0.5 * (Pp + Pp.T)
            m_p[i] = mp; P_p[i] = Pp
            ki = kind[i]
            if ki == 2:
                m, P = mp, Pp
            elif ki == 0:
                m, P = self._update_pos(mp, Pp, payX[i], payY[i], sp2, Iv)
            else:
                lv = (float(lin_vel[i, 0]), float(lin_vel[i, 1])) if lin_vel is not None else None
                m, P = self._update_speed(mp, Pp, payV[i], sv2, vtx, vty, lv, Iv)
            P = 0.5 * (P + P.T); m_f[i] = m; P_f[i] = P
        return dict(m_f=m_f, P_f=P_f, m_p=m_p, P_p=P_p, Phis=Phis, Qs=Qs)

    def _backward(self, fwd):
        m_f, P_f, m_p, P_p, Phis = fwd["m_f"], fwd["P_f"], fwd["m_p"], fwd["P_p"], fwd["Phis"]
        n = len(m_f); m_s = np.empty_like(m_f); P_s = np.empty_like(P_f)
        m_s[-1] = m_f[-1]; P_s[-1] = P_f[-1]
        for i in range(n - 2, -1, -1):
            Phi = Phis[i + 1]; Ppred = P_p[i + 1]
            C = P_f[i] @ Phi.T @ linalg.inv(Ppred)
            m_s[i] = m_f[i] + C @ (m_s[i + 1] - m_p[i + 1])
            P_s[i] = P_f[i] + C @ (P_s[i + 1] - Ppred) @ C.T
            P_s[i] = 0.5 * (P_s[i] + P_s[i].T)
        return m_s, P_s

    def fit(self, tp, yX, yY, tc, yV, query_times=None):
        tp = np.asarray(tp, float); yX = np.asarray(yX, float); yY = np.asarray(yY, float)
        tc = np.asarray(tc, float); yV = np.asarray(yV, float)
        self._tm = tp.mean()
        self._bx = np.polyfit(tp - self._tm, yX, 1); self._by = np.polyfit(tp - self._tm, yY, 1)
        self._vtrend_x = float(self._bx[0]); self._vtrend_y = float(self._by[0])
        yXr = yX - np.polyval(self._bx, tp - self._tm); yYr = yY - np.polyval(self._by, tp - self._tm)
        ts, kind, payX, payY, payV = self._build_timeline(tp, yXr, yYr, tc, yV, extra=query_times)
        self._ts_index = {round(float(tt), 9): i for i, tt in enumerate(ts)}
        self.ts = ts; self.kind = kind
        lin_vel = None
        for it in range(max(self.iters, 1)):
            fwd = self._forward(ts, kind, payX, payY, payV, lin_vel=lin_vel)
            m_s, P_s = self._backward(fwd)
            new_lin = np.column_stack([m_s[:, self.iVX], m_s[:, self.iVY]])
            dmax = float(np.max(np.abs(new_lin - lin_vel))) if lin_vel is not None else np.inf
            lin_vel = new_lin
            if dmax < 1e-3:
                break
        self.m_s = m_s; self.P_s = P_s; self._fwd = fwd
        self._payX, self._payY, self._payV = payX, payY, payV
        return self

    def _state_at(self, t):
        t = np.atleast_1d(np.asarray(t, float))
        idx = np.clip(np.searchsorted(self.ts, t, side="right") - 1, 0, len(self.ts) - 1)
        m = np.empty((len(t), self.dim)); P = np.empty((len(t), self.dim, self.dim))
        for k in range(len(t)):
            j = self._ts_index.get(round(float(t[k]), 9))
            if j is not None:
                m[k] = self.m_s[j]; P[k] = self.P_s[j]; continue
            i = idx[k]; dt = t[k] - self.ts[i]
            if dt <= 1e-12:
                m[k] = self.m_s[i]; P[k] = self.P_s[i]
            else:
                Phi, Q = discretize(self.F, self.Pinf, dt)
                m[k] = Phi @ self.m_s[i]; P[k] = Phi @ self.P_s[i] @ Phi.T + Q
        return m, P

    def pos_at(self, t):
        t = np.atleast_1d(np.asarray(t, float)); m, _ = self._state_at(t)
        return m[:, self.iX] + np.polyval(self._bx, t - self._tm), m[:, self.iY] + np.polyval(self._by, t - self._tm)

    def vel_at(self, t):
        m, _ = self._state_at(t)
        return m[:, self.iVX] + self._vtrend_x, m[:, self.iVY] + self._vtrend_y

    def acc_at(self, t):
        m, _ = self._state_at(t)
        return m[:, self.iAX], m[:, self.iAY]

    def pos_predvar(self, t):
        _, P = self._state_at(t)
        return (np.clip(P[:, self.iX, self.iX], 0, None) + self.sig_pos ** 2,
                np.clip(P[:, self.iY, self.iY], 0, None) + self.sig_pos ** 2)

    def speed_at(self, t):
        vx, vy = self.vel_at(t)
        return np.hypot(vx, vy)

    def speed_predvar(self, t):
        """Predictive variance of a speed obs at t (delta method on |v|) + noise."""
        m, P = self._state_at(t)
        Xd = m[:, self.iVX] + self._vtrend_x
        Yd = m[:, self.iVY] + self._vtrend_y
        spd = np.maximum(np.hypot(Xd, Yd), 1e-6)
        jx = Xd / spd; jy = Yd / spd
        varV = (jx ** 2 * P[:, self.iVX, self.iVX] + jy ** 2 * P[:, self.iVY, self.iVY]
                + 2 * jx * jy * P[:, self.iVX, self.iVY])
        return np.clip(varV, 0, None) + self.sig_spd ** 2, spd


# ---------------------------------------------------------------------------
# self-check: order=3 must reproduce production StintSmoother
# ---------------------------------------------------------------------------
def _selfcheck():
    from src.preprocessing.trajectory.smoother import StintSmoother
    rng = np.random.default_rng(0)
    t = np.cumsum(rng.uniform(0.2, 0.28, 120)); t -= t[0]
    X = 30 * t + 5 * np.sin(0.3 * t); Y = 2 * t + 8 * np.cos(0.25 * t)
    Xo = X + rng.normal(0, 0.1, len(t)); Yo = Y + rng.normal(0, 0.1, len(t))
    tc = t + 0.03; V = np.hypot(np.gradient(X, t), np.gradient(Y, t)) + rng.normal(0, 0.5, len(t))
    prod = StintSmoother(2.0, 100.0, 0.3, 0.06, iters=3).fit(t, Xo, Yo, tc, V)
    mine = MaternSmoother(2.0, 100.0, 0.3, 0.06, order=3, iters=3).fit(t, Xo, Yo, tc, V)
    tq = t[5:-5]
    pax, pay = prod.acc_at(tq); max_ = max(np.abs(pax).max(), 1e-9)
    max_a = float(np.abs(mine.acc_at(tq)[0] - pax).max())
    ppx, ppy = prod.pos_at(tq); max_p = float(np.abs(mine.pos_at(tq)[0] - ppx).max())
    # also check 5/2 P_inf matches analytic
    from src.preprocessing.trajectory.dynamics import matern52_sde
    _, _, Pa = matern52_sde(2.0, 100.0); _, _, Pm = matern_sde(2.0, 100.0, 3)
    print(f"order-3 vs production: max|dacc|={max_a:.2e} m/s^2  max|dpos|={max_p:.2e} m  "
          f"P_inf match={np.abs(Pa-Pm).max():.2e}")
    print("  -> PASS" if max_a < 1e-6 and max_p < 1e-6 else "  -> FAIL (debug before trusting order-4)")


if __name__ == "__main__":
    _selfcheck()
