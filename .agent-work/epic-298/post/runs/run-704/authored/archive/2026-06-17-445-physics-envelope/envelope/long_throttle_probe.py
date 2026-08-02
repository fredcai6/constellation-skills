"""Full-throttle longitudinal acceleration vs speed — the straight-line capability curve (#445).

Analogue of apex speed for cornering: under FULL throttle (no brake) the car is on its
LONGITUDINAL limit. Physics: m·a = P/v − ½ρ·CdA·v²  (drive power minus drag), so a(v) falls
with speed and → 0 at TOP SPEED (drive = drag) — the clean high-speed truth. Trace a(v) for
RBR across a few races, DRS-separated, fit the power/drag frontier, and read top speed.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
from ribbon_reeval import driver_num, load_session, RHO, MASS, OUT  # noqa: E402
from grip_iter import flying_windows  # noqa: E402
from air_density import air_density  # noqa: E402

G = 9.81
RBR = ["VER", "PER"]
RACES = [("Italian", "Italy"), ("Hungarian", "Hungary"), ("Japanese", "Japan")]


def throttle_av(session, cars):
    """Full-throttle (thr>98, brake<1) points: (v m/s, a m/s², drs_open bool)."""
    V, A, OPEN = [], [], []
    for car in cars:
        try:
            num = driver_num(session, car)
            cd = session.car_data[num]
        except Exception:
            continue
        tc = cd["SessionTime"].dt.total_seconds().to_numpy()
        spd = cd["Speed"].to_numpy(float) / 3.6
        thr = cd["Throttle"].to_numpy(float)
        brk = cd["Brake"].to_numpy(float)
        drs = cd["DRS"].to_numpy(float)
        for ls, le in flying_windows(session, car):
            m = (tc >= ls) & (tc <= le)
            t, v, th, bk, dr = tc[m], spd[m], thr[m], brk[m], drs[m]
            o = np.argsort(t); t, v, th, bk, dr = t[o], v[o], th[o], bk[o], dr[o]
            keep = np.concatenate([[True], np.diff(t) > 1e-9])
            t, v, th, bk, dr = t[keep], v[keep], th[keep], bk[keep], dr[keep]
            for i in range(1, len(t) - 1):
                dt = t[i + 1] - t[i - 1]
                if dt > 0 and th[i] > 98 and bk[i] < 1:
                    V.append(v[i]); A.append((v[i + 1] - v[i - 1]) / dt); OPEN.append(dr[i] >= 10)
    return np.array(V), np.array(A), np.array(OPEN)


def frontier_fit(v, a, rho=RHO):
    """Upper-edge power/drag fit a = P/(m v) − ½ρ CdA v²/m on 90th-pct-in-bin points."""
    vb, ab = [], []
    for lo in np.arange(20, 100, 6):
        mm = (v >= lo) & (v < lo + 6)
        if mm.sum() >= 8:
            vb.append(v[mm].mean()); ab.append(np.quantile(a[mm], 0.90))
    vb, ab = np.array(vb), np.array(ab)
    if len(vb) < 4:
        return None
    X = np.column_stack([1 / (MASS * vb), -0.5 * rho * vb ** 2 / MASS])
    (P, CdA), *_ = np.linalg.lstsq(X, ab, rcond=None)
    return float(P), float(CdA), vb, ab


def main():
    fig, axes = plt.subplots(1, len(RACES), figsize=(5.4 * len(RACES), 5.2), sharey=True)
    for ax, (rn, gp) in zip(axes, RACES):
        q = load_session(2023, gp, "Q")
        rho = air_density(2023, gp, "Q")
        v, a, op = throttle_av(q, RBR)
        if len(v) < 50:
            ax.set_title(f"{rn}: thin"); continue
        ax.scatter(v[~op] * 3.6, a[~op] / G, s=6, alpha=0.25, color="steelblue", label="DRS closed")
        ax.scatter(v[op] * 3.6, a[op] / G, s=6, alpha=0.25, color="orange", label="DRS open")
        vmax = v.max() * 3.6
        ax.axvline(vmax, ls=":", color="k", lw=1)
        ax.text(vmax - 3, 1.5, f"top {vmax:.0f}", rotation=90, va="bottom", ha="right", fontsize=8)
        ff = frontier_fit(v, a, rho)
        if ff:
            P, CdA, vb, ab = ff
            vv = np.linspace(20, v.max(), 100)
            apred = P / (MASS * vv) - 0.5 * rho * CdA * vv ** 2 / MASS
            ax.plot(vv * 3.6, apred / G, "r-", lw=1.8,
                    label=f"P={P/1e3:.0f}kW CdA={CdA:.2f}")
            ax.plot(vb * 3.6, ab / G, "k.", ms=7)
            v0 = (2 * P / (rho * CdA)) ** (1 / 3) * 3.6 if CdA > 0 else np.nan
            ax.text(0.04, 0.06, f"a=0 (drag=power) @ {v0:.0f} km/h\nmeasured top {vmax:.0f}",
                    transform=ax.transAxes, fontsize=8, va="bottom")
        ax.axhline(0, color="gray", lw=0.6)
        ax.set_title(f"{rn}  ({len(v)} full-throttle pts)")
        ax.set_xlabel("speed (km/h)"); ax.grid(alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
        print(f"  {rn}: {len(v)} pts, measured top {vmax:.0f} km/h"
              + (f", fit P={P/1e3:.0f}kW CdA={CdA:.2f}, drag=power@{v0:.0f}" if ff else ""))
    axes[0].set_ylabel("full-throttle longitudinal accel (g)")
    fig.suptitle("RBR — full-throttle longitudinal accel vs speed "
                 "(a→0 at top speed = drive=drag anchor)", fontsize=11)
    fig.tight_layout()
    png = OUT / "long_throttle_rbr.png"
    fig.savefig(png, dpi=120); print(f"wrote {png}")


if __name__ == "__main__":
    main()
