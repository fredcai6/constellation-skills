"""RBR: frontier-predicted apex speed (x) vs measured apex speed (y), per corner (#445).

Visualises the β=0.329 apex/frontier contradiction. Frontier G(v)=A+B·v² (grip ceiling, fit
per-race from RBR's calibrated cornering nodes) predicts an apex speed for each corner radius:
  v_front = sqrt(min(A+B·v²,GSAT)·g·R)   (self-consistent).
Measured apex speed = the min-speed apex actually carried (apex_corners.npz). If the ceiling
overstates fast-corner grip, points sit BELOW y=x, increasingly at high speed (big R).
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
from ribbon_reeval import get_apex_nodes, fit_grip_clean, load_cal_nodes, OUT  # noqa: E402

G = 9.81
GSAT = 5.2
RBR = ["VER", "PER"]
RACES = [("Hungarian", "Hungary"), ("Italian", "Italy"), ("Japanese", "Japan")]


def v_frontier(A, B, R):
    v = np.sqrt(min(A + B * 100.0, GSAT) * G * R)
    for _ in range(30):
        v = np.sqrt(min(A + B * v * v, GSAT) * G * R)
    return v


def main():
    d = np.load(OUT / "apex_corners.npz", allow_pickle=True)
    rnd = d["round"].astype(str); car = d["car"].astype(str)
    vap = d["v_apex"].astype(float); Rap = d["R_apex"].astype(float)
    cal = load_cal_nodes()

    # RBR SEASON-pooled frontier (stable; per-weekend fits are too thin — itself the problem)
    vk = np.concatenate([cal[k]["v"] * 3.6 for k in cal if k[1] in RBR])
    gg = np.concatenate([cal[k]["alat"] for k in cal if k[1] in RBR])
    A, B, _ = fit_grip_clean(vk, gg)
    print(f"RBR season frontier: A={A:.2f}g  B={B*1e3:.2f}e-3  ({len(vk)} nodes)")

    fig, axes = plt.subplots(1, len(RACES), figsize=(5.2 * len(RACES), 5.2))
    for ax, (rn, gp) in zip(axes, RACES):
        m = (rnd == rn) & np.isin(car, RBR) & np.isfinite(vap) & (Rap > 5)
        R = Rap[m]; vmeas = vap[m]
        if len(R) < 5:
            ax.set_title(f"{rn}: {len(R)} corners"); continue
        vf = np.array([v_frontier(A, B, r) for r in R])
        sc = ax.scatter(vf * 3.6, vmeas * 3.6, c=R, cmap="viridis", s=28,
                        alpha=0.8, edgecolors="k", linewidths=0.3)
        lim = [0, max(vf.max(), vmeas.max()) * 3.6 * 1.05]
        ax.plot(lim, lim, "k--", lw=1.3, label="y = x (frontier achieved)")
        # robust regression line measured ~ a + b*frontier
        b, a = np.polyfit(vf * 3.6, vmeas * 3.6, 1)
        xs = np.array(lim)
        ax.plot(xs, a + b * xs, "r-", lw=1.6, label=f"fit: slope {b:.2f}")
        ax.set_xlim(lim); ax.set_ylim(lim)
        ax.set_title(f"{rn}  ({len(R)} corners)")
        ax.set_xlabel("frontier-predicted apex speed (km/h)")
        ax.set_ylabel("measured apex speed (km/h)")
        ax.legend(loc="upper left", fontsize=8); ax.grid(alpha=0.3)
        plt.colorbar(sc, ax=ax, label="corner radius R (m)")
    fig.suptitle("RBR — frontier-predicted vs measured apex speed, per corner "
                 "(below y=x ⇒ ceiling overstates achieved cornering)", fontsize=11)
    fig.tight_layout()
    png = OUT / "apex_frontier_rbr.png"
    fig.savefig(png, dpi=120)
    print(f"wrote {png}")
    for rn, gp in RACES:
        m = (rnd == rn) & np.isin(car, RBR) & np.isfinite(vap) & (Rap > 5)
        R = Rap[m]; vmeas = vap[m]
        if len(R) < 5:
            continue
        vf = np.array([v_frontier(A, B, r) for r in R])
        b, _ = np.polyfit(vf, vmeas, 1)
        hi = vf > np.median(vf)
        print(f"  {rn}: {len(R)} corners, measured/frontier slope={b:.2f}, "
              f"mean gap={(vf-vmeas).mean()*3.6:+.1f} km/h "
              f"(low-spd {(vf[~hi]-vmeas[~hi]).mean()*3.6:+.1f}, "
              f"hi-spd {(vf[hi]-vmeas[hi]).mean()*3.6:+.1f})")


if __name__ == "__main__":
    main()
