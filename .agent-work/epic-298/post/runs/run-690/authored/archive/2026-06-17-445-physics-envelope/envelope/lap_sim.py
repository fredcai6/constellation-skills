"""Idealized lap sim, corner-anchored (epic #445).

The pure-physics ideal is blocked by noisy curvature. Sidestep it: anchor the
corner apex speeds to the MEASURED minima (grip-limited in quali = true corner
constraint), and simulate only the STRAIGHT-LINE connections we trust:
  accel out of corner: a = P/(m v) - drag/m        (power - drag)
  brake into corner:   a = G(v) g + drag/m          (grip + drag)
  v(s) = min(forward-accel, backward-brake), floored at the apex speeds.
Idealized lap time vs actual -> driver utilization of the physics ceiling.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402

G = 9.81
RHO = 1.2
MASS = 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
A, B, GSAT = 1.90, 0.00177, 4.95
P_ENG = 525e3
CDA_C, CDA_O = 1.53, 0.97


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def Gv(v):
    return min(A + B * v * v, GSAT)


def drag_acc(v):
    cda = CDA_O if v > 200 / 3.6 else CDA_C    # DRS open on straights (approx)
    return 0.5 * RHO * cda * v * v / MASS


def lap_geometry():
    session = H.load_session(2023, "Japan", "Q")
    laps = session.laps.pick_drivers("VER")
    laps = laps[laps["LapTime"].notna()]
    fl = laps.loc[laps["LapTime"].idxmin()]
    ls, le = fl["LapStartTime"].total_seconds(), fl["Time"].total_seconds()
    runs = H.driver_runs(session, "VER")
    run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le),
               max(runs, key=lambda r: r["t1"] - r["t0"]))
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    o = np.argsort(t); t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
    X, Y = ss.pos_at(t)
    v_act = np.interp(t, run["tc"], run["V"])
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    # classify cornering (robust: a_lat magnitude from circle fit, used only to
    # flag corner vs straight, not for its noisy magnitude)
    n = len(s)
    alat = np.zeros(n)
    for i in range(n):
        a, b = max(0, i - 4), min(n, i + 5)
        if b - a >= 5:
            xx, yy = X[a:b], Y[a:b]
            M = np.column_stack([xx, yy, np.ones_like(xx)])
            sol, *_ = np.linalg.lstsq(M, -(xx**2 + yy**2), rcond=None)
            cx, cy = -sol[0] / 2, -sol[1] / 2
            r2 = cx**2 + cy**2 - sol[2]
            if r2 > 9:
                alat[i] = v_act[i] ** 2 / np.sqrt(r2) / G
    return s, v_act, alat, fl["LapTime"].total_seconds()


def simulate(s, v_act, alat):
    n = len(s)
    ds = np.diff(s)
    # lock cornering points to the measured (grip-limited) speed; straights free
    corner = alat > 0.6
    vlim = np.where(corner, v_act, 100.0)
    v = np.minimum(v_act.copy() * 0 + 100.0, vlim)
    for _ in range(5):
        for i in range(n - 1):
            a = P_ENG / (MASS * max(v[i], 1.0)) - drag_acc(v[i])
            vn = np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0))
            v[i + 1] = min(v[i + 1], vn, vlim[i + 1])
        for i in range(n - 2, -1, -1):
            a = Gv(v[i + 1]) * G + drag_acc(v[i + 1])
            vp = np.sqrt(max(v[i + 1] ** 2 + 2 * a * ds[i], 1.0))
            v[i] = min(v[i], vp, vlim[i])
    return v, corner


def main():
    log("building lap geometry ...")
    s, v_act, alat, lap_act = lap_geometry()
    v_id, apex = simulate(s, v_act, alat)
    ds = np.diff(s)
    t_id = float(np.sum(ds / ((v_id[:-1] + v_id[1:]) / 2)))
    t_act = float(np.sum(ds / np.maximum((v_act[:-1] + v_act[1:]) / 2, 1.0)))
    log(f"lap {s[-1]:.0f} m, {len(apex)} corners")
    log(f"\nidealized lap time:  {t_id:.2f}s")
    log(f"actual lap (integrated): {t_act:.2f}s  (timing {lap_act:.2f}s)")
    log(f"utilization (ideal/actual): {t_id/t_act:.3f}  "
        f"-> driver achieved {100*t_id/t_act:.1f}% of the physics ideal "
        f"(left {t_act-t_id:.2f}s)")
    _plot(s, v_id, v_act, apex)


def _plot(s, v_id, v_act, apex):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(s, v_act * 3.6, color="navy", lw=1.4, label="actual (VER quali)")
    ax.plot(s, v_id * 3.6, color="firebrick", lw=1.2, alpha=0.8, label="idealized (physics)")
    ax.scatter(s[apex], v_act[apex] * 3.6, color="black", s=20, zorder=5, label="apex anchors")
    ax.set_xlabel("arc length (m)"); ax.set_ylabel("speed (km/h)")
    ax.set_title("Idealized vs actual lap (corner-anchored) -- straight-line utilization")
    ax.grid(alpha=0.3); ax.legend(fontsize=9); ax.set_ylim(0, 360)
    png = OUT / "lap_sim.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
