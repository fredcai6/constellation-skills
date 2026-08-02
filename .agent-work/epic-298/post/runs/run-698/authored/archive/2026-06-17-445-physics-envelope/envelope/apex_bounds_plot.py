"""RBR Monza: measured v_apex vs R against the two ideal bounds (#445).
  grip-limited curve  v_grip(R) = √(min(A+B·v²,GSAT)·g·R)   (cornering ceiling)
  top-speed cap       v_max                                   (straight-line ceiling)
Colour each apex by the lateral g it's actually pulling: grip-limited corners should ride the
grip curve at HIGH a_lat; speed-limited corners should flatten under v_max at LOW a_lat.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
from ribbon_reeval import fit_grip_clean, get_apex_nodes, load_cal_nodes, OUT  # noqa: E402
from ribbon_apex_ideal import apex_curves  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from ribbon_reeval import load_session  # noqa: E402

G = 9.81
GSAT = 5.2
RBR = ["VER", "PER"]


def v_grip(A, B, R):
    v = np.sqrt(min(A + B * 100.0, GSAT) * G * R)
    for _ in range(30):
        v = np.sqrt(min(A + B * v * v, GSAT) * G * R)
    return v


def main():
    d = np.load(OUT / "apex_corners.npz", allow_pickle=True)
    rnd = d["round"].astype(str); car = d["car"].astype(str)
    vap = d["v_apex"].astype(float); Rap = d["R_apex"].astype(float); al = d["alat_apex"].astype(float)
    m = (rnd == "Italian") & np.isin(car, RBR) & (Rap > 5) & np.isfinite(vap)
    R, v, alat = Rap[m], vap[m], al[m]

    cal = load_cal_nodes()
    vk, gg = get_apex_nodes(cal, "Italy", RBR)
    A, B, _ = fit_grip_clean(vk, gg)             # RBR season-stable grip frontier
    q = load_session(2023, "Italy", "Q")
    vth, _, _ = throttle_av(q, RBR)
    vmax = np.percentile(vth, 99.5) * 3.6        # km/h
    beta, alpha, _ = apex_curves()

    Rg = np.logspace(np.log10(8), np.log10(R.max() * 1.1), 200)
    vg = np.array([v_grip(A, B, r) for r in Rg]) * 3.6
    vfit = np.exp(alpha["RBR"]) * Rg ** beta * 3.6
    venv = np.minimum(vg, vmax)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    sc = ax.scatter(R, v * 3.6, c=alat, cmap="plasma", s=34, edgecolors="k",
                    linewidths=0.3, zorder=3, label="measured apex (RBR Monza)")
    ax.plot(Rg, vg, "b-", lw=2, label=f"grip bound √(G·g·R)  (A={A:.2f},B={B*1e3:.2f}e-3)")
    ax.axhline(vmax, color="green", lw=2, ls="-", label=f"top-speed cap {vmax:.0f} km/h")
    ax.plot(Rg, venv, "k--", lw=1.4, alpha=0.8, label="ideal bound = min(grip, top)")
    ax.plot(Rg, vfit, "r:", lw=2, label=f"single-β apex fit  exp(α)·R^{beta:.2f}")
    ax.set_xscale("log")
    ax.set_xlabel("corner radius R (m, log)"); ax.set_ylabel("apex speed (km/h)")
    ax.set_ylim(0, vmax * 1.1)
    ax.set_title("RBR Monza — measured apex vs ideal bounds (colour = lateral g at apex)")
    plt.colorbar(sc, ax=ax, label="a_lat at apex (g)")
    ax.legend(loc="upper left", fontsize=8); ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    png = OUT / "apex_bounds_monza_rbr.png"
    fig.savefig(png, dpi=120); print(f"wrote {png}")
    # numeric: where do points sit vs each bound, split by radius
    vg_at = np.array([v_grip(A, B, r) for r in R]) * 3.6
    slow = R < 80; fast = R >= 200
    print(f"  {m.sum()} apex pts. vmax={vmax:.0f} km/h, grip A={A:.2f}g")
    print(f"  SLOW (R<80m, n={slow.sum()}): a_lat med {np.median(alat[slow]):.2f}g, "
          f"v/grip-bound {np.median((v[slow]*3.6)/vg_at[slow]):.2f}, v/vmax {np.median(v[slow]*3.6)/vmax:.2f}")
    print(f"  FAST (R≥200m, n={fast.sum()}): a_lat med {np.median(alat[fast]):.2f}g, "
          f"v/grip-bound {np.median((v[fast]*3.6)/vg_at[fast]):.2f}, v/vmax {np.median(v[fast]*3.6)/vmax:.2f}")


if __name__ == "__main__":
    main()
