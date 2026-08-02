"""Corner-zoom: the ideal car's grip-budget usage through a corner (epic #445).

Confirm the lap sim curvature-limits the exit: zoom a corner, plot the ideal
speed / lateral / longitudinal, and the g-g trace vs the friction-circle boundary.
Entry = braking + lateral; apex = full lateral, zero longitudinal; exit = lateral
unwinds as the corner opens, freeing longitudinal for deployment.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

G, RHO, MASS = 9.81, 1.2, 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
A, B, GSAT, P_ENG, CC, CO = 1.90, 0.00177, 4.95, 525e3, 1.53, 0.97


def Gv(v):
    return min(A + B * v * v, GSAT)


def drag(v, k):
    return 0.5 * RHO * (CO if (abs(k) < 8e-4 and v > 200 / 3.6) else CC) * v * v / MASS


def simulate(s, kappa):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    vg = np.sqrt(GSAT * G / np.maximum(kappa, 1e-6))
    for _ in range(10):
        vg = np.minimum(np.sqrt(np.array([Gv(x) for x in vg]) * G / np.maximum(kappa, 1e-6)), 100.0)
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G
            tr = np.sqrt(max(Gv(v[i]) ** 2 - al ** 2, 0)) * G
            a = min(tr, P_ENG / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)), vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G
            tr = np.sqrt(max(Gv(v[i + 1]) ** 2 - al ** 2, 0)) * G
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * (tr + drag(v[i + 1], kappa[i + 1])) * ds[i], 1.0)), vg[i])
    return v


def main():
    d = np.load(OUT / "ribbon_suzuka.npz"); s, kappa = d["s"], np.abs(d["kappa"])
    v = simulate(s, kappa)
    a_lat = v**2 * kappa / G
    a_long = np.gradient(v, s) * v / G       # v dv/ds, in g
    # zoom the hairpin (deepest speed min)
    c = int(np.argmin(v))
    lo = max(0, c - 90); hi = min(len(s), c + 110)
    sl = slice(lo, hi)
    s0 = s[lo]
    _plot(s[sl] - s0, v[sl], a_lat[sl], a_long[sl], v[c])


def _plot(s, v, al, alo, vapex):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    ax1.plot(s, v * 3.6, "k-", lw=2, label="speed (km/h)")
    ax1.set_ylabel("speed (km/h)"); ax1.set_xlabel("distance through corner (m)")
    axb = ax1.twinx()
    axb.plot(s, al, color="navy", lw=1.5, label="lateral (g)")
    axb.plot(s, alo, color="firebrick", lw=1.5, label="longitudinal (g)  [+accel/-brake]")
    axb.axhline(0, color="gray", lw=0.5)
    axb.set_ylabel("acceleration (g)")
    ax1.set_title(f"Hairpin: entry brake -> apex ({vapex*3.6:.0f} km/h, full lateral) -> exit deploy")
    h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = axb.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc="lower right")
    ax1.grid(alpha=0.3)
    # g-g trace through the corner vs friction circle
    sc = ax2.scatter(al, alo, c=v * 3.6, cmap="viridis", s=25)
    th = np.linspace(0, 2 * np.pi, 100)
    Gc = Gv(vapex)
    ax2.plot(Gc * np.cos(th), Gc * np.sin(th), "r--", lw=1.2, label=f"friction circle G={Gc:.1f}g @ apex")
    ax2.axhline(0, color="gray", lw=0.4); ax2.axvline(0, color="gray", lw=0.4)
    ax2.set_xlabel("lateral (g)"); ax2.set_ylabel("longitudinal (g)")
    ax2.set_title("Grip-budget usage through the corner (color = speed)")
    ax2.legend(fontsize=8); ax2.set_aspect("equal"); fig.colorbar(sc, ax=ax2, label="km/h")
    fig.tight_layout()
    png = OUT / "corner_zoom.png"
    fig.savefig(png, dpi=110)
    print(f"[{time.strftime('%H:%M:%S')}] wrote {png}; apex {vapex*3.6:.0f} km/h, "
          f"peak lateral {al.max():.1f}g, peak deploy {alo.max():.1f}g, peak brake {-alo.min():.1f}g")


if __name__ == "__main__":
    main()
