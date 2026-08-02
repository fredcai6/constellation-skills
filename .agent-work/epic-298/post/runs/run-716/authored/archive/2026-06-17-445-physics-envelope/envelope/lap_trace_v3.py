"""Monza/RBR re-trace with the TWO-BOUND cornering model (#445):
  vg(R) = min( √(min(A+B·v²,GSAT)·g·R),  v_max )      [grip curve ∧ top-speed cap]
Replaces the single-β apex power-law (too flat → 154 km/h chicanes). Grip frontier is the
Monza-stable fit; v_max + a(v) measured. Compare to the old apex-curve ideal and the real laps.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
from ribbon_reeval import (load_session, fit_grip_clean, get_apex_nodes, load_cal_nodes,
                           G_CONST, OUT)  # noqa: E402
from ribbon_apex_ideal import apex_curves  # noqa: E402
from ribbon_long_paths import vg_apex  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from ideal_lap_v2 import av_measured  # noqa: E402
from lap_trace import sim_profile, profile_to_t  # noqa: E402

GSAT = 5.2
RBR = ["VER", "PER"]


def vg_minenv(kappa, A, B, vmax_ms):
    k = np.abs(kappa); R = 1.0 / np.maximum(k, 1e-6)
    vg = np.sqrt(GSAT * G_CONST * R)
    for _ in range(25):
        vg = np.minimum(np.sqrt(np.minimum(A + B * vg * vg, GSAT) * G_CONST * R), vmax_ms)
    return vg


def main():
    name, gp, length = "Monza", "Italy", 5793
    d = np.load(OUT / f"ribbon_clean_{name.lower()}.npz"); s, kappa = d["s"], d["kappa"]
    pct_rib = s / s[-1] * 100
    q = load_session(2023, gp, "Q"); cal = load_cal_nodes()
    beta, alpha, _ = apex_curves()
    vk, gg = get_apex_nodes(cal, gp, RBR); A, B, _ = fit_grip_clean(vk, gg)
    Gs = lambda v: min(A + B * v * v, GSAT)
    vth, ath, _ = throttle_av(q, RBR); mv = av_measured(vth, ath)
    vmax = mv["vmax"]
    a_meas = lambda vv, K=mv["K"], vm=mv["vmax"]: max(K * (vm ** 3 / max(vv, 1.0) - vv * vv), 0.0)

    vg_new = vg_minenv(kappa, A, B, vmax)
    vg_old = np.minimum(vg_apex(kappa, alpha["RBR"], beta), vmax)
    v_new = sim_profile(s, kappa, vg_new, a_meas, vmax, Gs)
    v_old = sim_profile(s, kappa, vg_old, a_meas, vmax, Gs)

    profiles = {"ideal NEW: min(grip,top)": (pct_rib, v_new),
                "ideal OLD: apex-β curve": (pct_rib, v_old)}
    for drv in ("VER", "PER"):
        try:
            lap = q.laps.pick_drivers(drv).pick_fastest()
            tel = lap.get_car_data().add_distance()
            dd = tel["Distance"].to_numpy(float); vv = tel["Speed"].to_numpy(float) / 3.6
            profiles[f"real {drv} {lap['LapTime'].total_seconds():.2f}s"] = (dd / dd[-1] * 100, vv)
        except Exception as e:
            print(f"  {drv}: {e}")

    grid = np.linspace(0, 100, 600)
    ts = {nm: profile_to_t(p[0], p[1], length, grid) for nm, p in profiles.items()}
    ref = [k for k in ts if k.startswith("real VER")][0]; tref = ts[ref][0]
    kabs = np.abs(np.interp(grid, pct_rib, kappa))
    pk, _ = find_peaks(kabs, prominence=np.percentile(kabs, 90), distance=15)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    col = {"ideal NEW: min(grip,top)": "tab:red", "ideal OLD: apex-β curve": "tab:green"}
    for nm, (t, vv) in ts.items():
        c = col.get(nm, "tab:blue" if "VER" in nm else "tab:purple")
        lsv = "-" if nm.startswith("ideal") else "--"
        ax1.plot(grid, vv * 3.6, lsv, color=c, lw=1.3, label=nm)
        ax2.plot(grid, t - tref, lsv, color=c, lw=1.8)
        ax3.plot(grid, np.gradient(t - tref, grid), lsv, color=c, lw=1.3)
    for p in pk:
        for ax in (ax1, ax2, ax3):
            ax.axvline(grid[p], color="gray", ls=":", lw=0.7, alpha=0.6)
    ax1.set_ylabel("speed (km/h)"); ax1.legend(fontsize=8, loc="lower center", ncol=2); ax1.grid(alpha=0.3)
    ax1.set_title("Monza/RBR — NEW min(grip,top) cornering vs OLD apex-β vs real (dotted=corners)")
    ax2.axhline(0, color="k", lw=0.6); ax2.set_ylabel("cum Δt vs VER (s)"); ax2.grid(alpha=0.3)
    ax3.axhline(0, color="k", lw=0.6); ax3.set_ylabel("Δt rate (s/%lap)"); ax3.set_xlabel("% lap"); ax3.grid(alpha=0.3)
    fig.tight_layout(); png = OUT / "lap_trace_v3_monza_rbr.png"; fig.savefig(png, dpi=120)
    print(f"wrote {png}\n  grip A={A:.2f}g B={B*1e3:.2f}e-3, vmax={vmax*3.6:.0f} km/h")
    for nm, (t, vv) in ts.items():
        print(f"  {nm:>28}: lap {t[-1]:.2f}s  min {vv.min()*3.6:.0f}  top {vv.max()*3.6:.0f} km/h")


if __name__ == "__main__":
    main()
