"""Monza/RBR ideal lap v4 — DRS-aware acceleration (#445).
Forward accel now uses two measured curves — a_open(v) (DRS open, low drag, high v_max) and
a_closed(v) — applied per ribbon section based on the DRS-open zones read from telemetry. The
top-speed cap is also DRS-zone-dependent. Braking unchanged (grip frontier). Solo lap (no tow).
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
from long_throttle_probe import throttle_av  # noqa: E402
from ideal_lap_v2 import frontier_pts, fit_anchored  # noqa: E402
from lap_trace import profile_to_t  # noqa: E402

GSAT = 5.2
RBR = ["VER", "PER"]


def fit_curve(vsub, asub, q=0.95):
    vb, ab = frontier_pts(vsub, asub, q)
    if len(vb) < 3:
        return None
    vmax = np.percentile(vsub, 99.5)
    K, P, CdA = fit_anchored(vb, ab, vmax)
    return dict(K=K, vmax=vmax, CdA=CdA)


def vg_minenv(kappa, A, B, vmax_node):
    k = np.abs(kappa); R = 1.0 / np.maximum(k, 1e-6)
    vg = np.sqrt(GSAT * G_CONST * R)
    for _ in range(25):
        vg = np.minimum(np.sqrt(np.minimum(A + B * vg * vg, GSAT) * G_CONST * R), vmax_node)
    return vg


def sim_drs(s, kappa, vg, a_node, vmax_node, Gs):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    v = vg.copy()
    for _ in range(5):
        for i in range(n - 1):
            af = min(a_node(v[i], i), Gs(v[i]) * G_CONST)
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * af * ds[i], 1.0)), vg[i + 1], vmax_node[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            ab = np.sqrt(max(Gs(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * ab * ds[i], 1.0)), vg[i])
    return v


def main():
    name, gp, length = "Monza", "Italy", 5793
    d = np.load(OUT / f"ribbon_clean_{name.lower()}.npz"); s, kappa = d["s"], d["kappa"]
    pct_rib = s / s[-1] * 100
    q = load_session(2023, gp, "Q"); cal = load_cal_nodes()
    vk, gg = get_apex_nodes(cal, gp, RBR); A, B, _ = fit_grip_clean(vk, gg)
    Gs = lambda v: min(A + B * v * v, GSAT)
    v, a, op = throttle_av(q, RBR)
    a_open = fit_curve(v[op], a[op]); a_closed = fit_curve(v[~op], a[~op])
    print(f"  DRS-open : v_max {a_open['vmax']*3.6:.0f} km/h, CdA {a_open['CdA']:.2f}")
    print(f"  DRS-closed: v_max {a_closed['vmax']*3.6:.0f} km/h, CdA {a_closed['CdA']:.2f}")

    # DRS-open zones on the ribbon from VER's fast lap telemetry
    lap = q.laps.pick_drivers("VER").pick_fastest(); tel = lap.get_car_data().add_distance()
    drs = tel["DRS"].to_numpy(float); dist = tel["Distance"].to_numpy(float)
    o = np.argsort(dist); dist, drs = dist[o], drs[o]
    pct_tel = dist / dist[-1] * 100
    drs_open_rib = np.interp(pct_rib, pct_tel, (drs >= 10).astype(float)) > 0.5
    zones = []
    inz = False
    for i, z in enumerate(drs_open_rib):
        if z and not inz:
            st = pct_rib[i]; inz = True
        elif not z and inz:
            zones.append((st, pct_rib[i])); inz = False
    print(f"  DRS zones (%lap): " + ", ".join(f"{a:.0f}-{b:.0f}" for a, b in zones))

    vmax_node = np.where(drs_open_rib, a_open["vmax"], a_closed["vmax"])
    a_node = lambda vv, i: (a_open if drs_open_rib[i] else a_closed)["K"] * \
        ((a_open if drs_open_rib[i] else a_closed)["vmax"] ** 3 / max(vv, 1.0) - vv * vv)
    a_node_pos = lambda vv, i: max(a_node(vv, i), 0.0)
    vg = vg_minenv(kappa, A, B, vmax_node)
    v_v4 = sim_drs(s, kappa, vg, a_node_pos, vmax_node, Gs)

    # v3 (single a_meas, no DRS) for contrast
    from ideal_lap_v2 import av_measured
    mv = av_measured(v, a)
    vmax_s = np.full_like(kappa, mv["vmax"])
    a_s = lambda vv, i: max(mv["K"] * (mv["vmax"] ** 3 / max(vv, 1.0) - vv * vv), 0.0)
    v_v3 = sim_drs(s, kappa, vg_minenv(kappa, A, B, vmax_s), a_s, vmax_s, Gs)

    profiles = {"v4: DRS-aware accel": (pct_rib, v_v4), "v3: single a(v)": (pct_rib, v_v3)}
    for drv in ("VER", "PER"):
        try:
            lp = q.laps.pick_drivers(drv).pick_fastest(); t2 = lp.get_car_data().add_distance()
            dd = t2["Distance"].to_numpy(float); vv = t2["Speed"].to_numpy(float) / 3.6
            profiles[f"real {drv} {lp['LapTime'].total_seconds():.2f}s"] = (dd / dd[-1] * 100, vv)
        except Exception as e:
            print(f"  {drv}: {e}")

    grid = np.linspace(0, 100, 600)
    ts = {nm: profile_to_t(p[0], p[1], length, grid) for nm, p in profiles.items()}
    ref = [k for k in ts if k.startswith("real VER")][0]; tref = ts[ref][0]
    kabs = np.abs(np.interp(grid, pct_rib, kappa)); pk, _ = find_peaks(kabs, prominence=np.percentile(kabs, 90), distance=15)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    col = {"v4: DRS-aware accel": "tab:red", "v3: single a(v)": "tab:green"}
    for nm, (t, vv) in ts.items():
        c = col.get(nm, "tab:blue" if "VER" in nm else "tab:purple"); lsv = "-" if nm.startswith("v") else "--"
        ax1.plot(grid, vv * 3.6, lsv, color=c, lw=1.3, label=nm)
        ax2.plot(grid, t - tref, lsv, color=c, lw=1.8)
    for a0, b0 in zones:
        ax1.axvspan(a0, b0, color="gold", alpha=0.12)
        ax2.axvspan(a0, b0, color="gold", alpha=0.12)
    for p in pk:
        for ax in (ax1, ax2):
            ax.axvline(grid[p], color="gray", ls=":", lw=0.7, alpha=0.5)
    ax1.set_ylabel("speed (km/h)"); ax1.legend(fontsize=8, loc="lower center", ncol=2); ax1.grid(alpha=0.3)
    ax1.set_title("Monza/RBR v4 DRS-aware (gold = DRS zones, dotted = corners)")
    ax2.axhline(0, color="k", lw=0.6); ax2.set_ylabel("cum Δt vs VER (s)"); ax2.set_xlabel("% lap"); ax2.grid(alpha=0.3)
    fig.tight_layout(); png = OUT / "lap_trace_v4_monza_rbr.png"; fig.savefig(png, dpi=120)
    print(f"wrote {png}")
    for nm, (t, vv) in ts.items():
        print(f"  {nm:>24}: lap {t[-1]:.2f}s  min {vv.min()*3.6:.0f}  top {vv.max()*3.6:.0f}")
    # localize where v4 loses/gains vs real VER (cumulative Δt change within DRS-zone spans)
    for tag, prof in [("v4", "v4: DRS-aware accel"), ("v3", "v3: single a(v)")]:
        dt = ts[prof][0] - tref
        inzone = 0.0
        for a0, b0 in zones:
            i0 = np.searchsorted(grid, a0); i1 = min(np.searchsorted(grid, b0), len(dt) - 1)
            inzone += dt[i1] - dt[i0]
        print(f"  {tag}-vs-real total {dt[-1]:+.2f}s  | accumulated IN DRS-zones {inzone:+.2f}s"
              f"  | elsewhere {dt[-1]-inzone:+.2f}s")


if __name__ == "__main__":
    main()
