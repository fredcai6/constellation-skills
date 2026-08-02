"""Idealized lap on the track ribbon -> utilization probe (epic #445).

Continuous-grip quasi-static sim on the pooled track curvature kappa(s):
  v_grip(s): v^2 kappa = G(v) g
  forward accel: a = min(sqrt(G^2 - a_lat^2) g, P/(m v)) - drag/m   (friction circle + power - drag)
  backward brake: a = sqrt(G^2 - a_lat^2) g + drag/m
  v(s) = min(v_grip, forward, backward)
Idealized lap time vs actual best lap -> how much of the physics ideal the driver
extracts. The ideal lives on the GENERALIZED ribbon, not any driver's line.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

G = 9.81
RHO = 1.2
MASS = 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
A, B, GSAT = 1.90, 0.00177, 4.95
P_ENG = 525e3
CDA_C, CDA_O = 1.53, 0.97
VER_QUALI = 88.88


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def Gv(v):
    return np.minimum(A + B * v * v, GSAT)


def drag_a(v, kappa):
    straight = (np.abs(kappa) < 8e-4) & (v > 200 / 3.6)
    cda = np.where(straight, CDA_O, CDA_C)
    return 0.5 * RHO * cda * v * v / MASS


def v_grip(kappa):
    v = np.sqrt(GSAT * G / np.maximum(kappa, 1e-6))
    for _ in range(10):
        v = np.sqrt(Gv(v) * G / np.maximum(kappa, 1e-6))
    return np.minimum(v, 105.0)


def simulate(s, kappa):
    n = len(s)
    ds = np.diff(s)
    vg = v_grip(kappa)
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            alat = v[i] ** 2 * kappa[i] / G
            trac = np.sqrt(max(Gv(np.array([v[i]]))[0] ** 2 - alat ** 2, 0)) * G
            pw = P_ENG / (MASS * max(v[i], 1.0))
            a = min(trac, pw) - drag_a(np.array([v[i]]), np.array([kappa[i]]))[0]
            vn = np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0))
            v[i + 1] = min(v[i + 1], vn, vg[i + 1])
        for i in range(n - 2, -1, -1):
            alat = v[i + 1] ** 2 * kappa[i + 1] / G
            trac = np.sqrt(max(Gv(np.array([v[i + 1]]))[0] ** 2 - alat ** 2, 0)) * G
            a = trac + drag_a(np.array([v[i + 1]]), np.array([kappa[i + 1]]))[0]
            vp = np.sqrt(max(v[i + 1] ** 2 + 2 * a * ds[i], 1.0))
            v[i] = min(v[i], vp, vg[i])
    return v, vg


def main():
    d = np.load(OUT / "ribbon_suzuka.npz")
    s, kappa = d["s"], np.abs(d["kappa"])
    log(f"ribbon: {len(s)} pts, {s[-1]:.0f} m, {int(d['nlaps'])} laps pooled")
    v, vg = simulate(s, kappa)
    ds = np.diff(s)
    t_id = float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))
    # scale to true track length (mean line cuts ~3% shorter than the 5807 m track)
    t_id_scaled = t_id * 5807 / s[-1]
    log(f"\nidealized lap time (mean-line): {t_id:.2f}s")
    log(f"idealized lap (length-scaled to 5807 m): {t_id_scaled:.2f}s")
    log(f"VER actual quali: {VER_QUALI:.2f}s")
    util = t_id_scaled / VER_QUALI
    log(f"\nUTILIZATION: ideal/actual = {util:.3f}  -> VER extracted {100*util:.1f}% "
        f"of the physics ideal (left {VER_QUALI - t_id_scaled:.2f}s on the table)")
    log(f"  ideal mean speed {np.mean(v)*3.6:.0f} km/h, top {np.max(v)*3.6:.0f} km/h, "
        f"min {np.min(v)*3.6:.0f} km/h")
    _plot(s, v, vg)


def _plot(s, v, vg):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(s, v * 3.6, color="firebrick", lw=1.4, label="idealized speed (physics on ribbon)")
    ax.plot(s, vg * 3.6, color="gray", lw=0.6, ls=":", label="grip-limited ceiling")
    ax.set_xlabel("arc length (m)"); ax.set_ylabel("speed (km/h)")
    ax.set_title("Idealized lap on the track ribbon")
    ax.grid(alpha=0.3); ax.legend(fontsize=9); ax.set_ylim(0, 360)
    png = OUT / "ideal_lap.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
