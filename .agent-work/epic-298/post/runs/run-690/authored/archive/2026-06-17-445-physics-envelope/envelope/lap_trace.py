"""General lap-trace comparison tool (#445). Compare any set of lap profiles by cumulative
TIME DELTA vs % lap complete, plus the RATE of delta change (where divergences happen), with
corner markers from the ribbon curvature. First use: Monza/RBR — ideal(apex-only),
ideal(+power), and a couple real fast laps.
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
                           RHO, MASS, G_CONST, OUT)  # noqa: E402
from ribbon_apex_ideal import apex_curves  # noqa: E402
from ribbon_long_paths import vg_apex  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from ideal_lap_v2 import av_measured  # noqa: E402

GS = 5.2
TEAM = {"RBR": ["VER", "PER"]}


def sim_profile(s, kappa, vg, a_meas, vmax, Gs):
    """Forward-backward sim, returns the speed profile v(s)."""
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    v = np.minimum(vg, vmax)
    for _ in range(5):
        for i in range(n - 1):
            af = min(a_meas(v[i]), Gs(v[i]) * G_CONST)
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * af * ds[i], 1.0)), vg[i + 1], vmax)
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            ab = np.sqrt(max(Gs(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * ab * ds[i], 1.0)), vg[i])
    return v


def cum_time(pct, v):
    """Cumulative time vs %lap for a (pct, speed) profile."""
    o = np.argsort(pct); pct, v = pct[o], v[o]
    keep = np.concatenate([[True], np.diff(pct) > 1e-9]); pct, v = pct[keep], v[keep]
    # arc spacing ∝ pct; we only need RELATIVE timing so use pct as distance proxy scaled by lap length later
    return pct, v


def profile_to_t(pct, v, length, grid):
    """Map (pct, v) to cumulative time on a common %-grid (seconds), lap of given length (m)."""
    o = np.argsort(pct); pct, v = pct[o], v[o]
    keep = np.concatenate([[True], np.diff(pct) > 1e-9]); pct, v = pct[keep], v[keep]
    d = pct / 100.0 * length
    vv = np.maximum(np.interp(grid / 100.0 * length, d, v), 1.0)
    dgrid = np.diff(grid / 100.0 * length)
    t = np.concatenate([[0.0], np.cumsum(dgrid / ((vv[:-1] + vv[1:]) / 2))])
    return t, vv


def main():
    name = "Monza"; gp = "Italy"; length = 5793
    cache = OUT / f"ribbon_clean_{name.lower()}.npz"
    d = np.load(cache); s, kappa = d["s"], d["kappa"]
    pct_rib = s / s[-1] * 100
    q = load_session(2023, gp, "Q")
    cal = load_cal_nodes()
    beta, alpha, _ = apex_curves()

    # RBR ideal inputs
    vk, gg = get_apex_nodes(cal, gp, TEAM["RBR"]); A, B, _ = fit_grip_clean(vk, gg)
    Gs = lambda v: min(A + B * v * v, GS)
    v_ft, a_ft, _ = throttle_av(q, TEAM["RBR"]); mv = av_measured(v_ft, a_ft)
    vg = vg_apex(kappa, alpha["RBR"], beta)
    a_power = lambda vv, K=mv["K"], vm=mv["vmax"]: max(K * (vm ** 3 / max(vv, 1.0) - vv * vv), 0.0)
    # apex-only = a generic shared accel (flat-ish high cap) so cornering+braking dominate
    a_flat = lambda vv: 12.0   # ~1.2g shared accel cap (longitudinal neutral)

    v_apexonly = sim_profile(s, kappa, vg, a_flat, mv["vmax"], Gs)
    v_power = sim_profile(s, kappa, vg, a_power, mv["vmax"], Gs)

    profiles = {"ideal: apex-only": (pct_rib, v_apexonly),
                "ideal: +power a(v)": (pct_rib, v_power)}
    # real fast laps
    for drv in ("VER", "PER"):
        try:
            lap = q.laps.pick_drivers(drv).pick_fastest()
            tel = lap.get_car_data().add_distance()
            dd = tel["Distance"].to_numpy(float); vv = tel["Speed"].to_numpy(float) / 3.6
            profiles[f"real: {drv} {lap['LapTime'].total_seconds():.2f}s"] = (dd / dd[-1] * 100, vv)
        except Exception as e:
            print(f"  {drv} real lap fail: {e}")

    grid = np.linspace(0, 100, 600)
    ts = {nm: profile_to_t(p[0], p[1], length, grid) for nm, p in profiles.items()}
    ref = [k for k in ts if k.startswith("real: VER")][0]
    tref = ts[ref][0]

    # corners from curvature peaks
    kabs = np.abs(np.interp(grid, pct_rib, kappa))
    pk, _ = find_peaks(kabs, prominence=np.percentile(kabs, 90), distance=15)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    col = {"ideal: apex-only": "tab:green", "ideal: +power a(v)": "tab:red"}
    for nm, (t, vv) in ts.items():
        dt = t - tref
        c = col.get(nm, "tab:blue" if "VER" in nm else "tab:purple")
        ls = "-" if nm.startswith("ideal") else "--"
        ax1.plot(grid, dt, ls, color=c, lw=1.8, label=nm)
        ax2.plot(grid, np.gradient(dt, grid), ls, color=c, lw=1.4)
    for p in pk:
        for ax in (ax1, ax2):
            ax.axvline(grid[p], color="gray", ls=":", lw=0.7, alpha=0.6)
    ax1.axhline(0, color="k", lw=0.6)
    ax1.set_ylabel("cumulative Δtime vs VER real (s)\n(− = ahead of VER)")
    ax1.set_title("Monza / RBR — lap-trace comparison (dotted = corners)")
    ax1.legend(fontsize=9, loc="lower left"); ax1.grid(alpha=0.3)
    ax2.axhline(0, color="k", lw=0.6)
    ax2.set_ylabel("Δtime RATE (s per %lap)\n(spikes = where gap opens)")
    ax2.set_xlabel("% lap complete"); ax2.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "lap_trace_monza_rbr.png"
    fig.savefig(png, dpi=120); print(f"wrote {png}")
    for nm, (t, vv) in ts.items():
        print(f"  {nm:>26}: lap {t[-1]:.2f}s, top {vv.max()*3.6:.0f} km/h, min {vv.min()*3.6:.0f}")


if __name__ == "__main__":
    main()
