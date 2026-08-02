"""Monza/RBR ideal lap v5 — every force its own MEASURED origin (#445):
  cornering  vg = min(√(G·g·R), v_max)         G(v)=A+B·v²   (measured lateral grip)
  accel      a(v) DRS-split open/closed        (measured full-throttle, p95)
  braking    a_brake(v) = A_b + B_b·v²         (measured braking frontier, p95) — NEW
             applied via friction circle: ab = √(a_brake² − a_lat²)
No borrowed axes. Solo lap. Compare to v4 (braking off lateral grip) and real.
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
from long_constraints import long_accel  # noqa: E402
from ideal_lap_v2 import frontier_pts, fit_anchored  # noqa: E402
from lap_trace import profile_to_t  # noqa: E402

GSAT = 5.2
BRAKE_SAT = 6.0
RBR = ["VER", "PER"]


def fit_curve(vsub, asub, q=0.95):
    vb, ab = frontier_pts(vsub, asub, q)
    if len(vb) < 3:
        return None
    vmax = np.percentile(vsub, 99.5)
    K, P, CdA = fit_anchored(vb, ab, vmax)
    return dict(K=K, vmax=vmax)


def fit_brake(vbr, decbr, q=0.95):
    """Braking frontier A_b + B_b·v² on the p95 upper edge of |decel| (g)."""
    vb, db = [], []
    for lo in np.arange(15, 96, 8):
        m = (vbr >= lo) & (vbr < lo + 8)
        if m.sum() >= 8:
            vb.append(vbr[m].mean()); db.append(np.quantile(decbr[m], q))
    vb, db = np.array(vb), np.array(db)
    X = np.column_stack([np.ones_like(vb), vb ** 2])
    (Ab, Bb), *_ = np.linalg.lstsq(X, db, rcond=None)
    return float(Ab), float(Bb), vb, db


def vg_minenv(kappa, A, B, vmax_node):
    k = np.abs(kappa); R = 1.0 / np.maximum(k, 1e-6)
    vg = np.sqrt(GSAT * G_CONST * R)
    for _ in range(25):
        vg = np.minimum(np.sqrt(np.minimum(A + B * vg * vg, GSAT) * G_CONST * R), vmax_node)
    return vg


def sim(s, kappa, vg, a_node, vmax_node, Gs, abrake):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    v = vg.copy()
    for _ in range(5):
        for i in range(n - 1):
            af = min(a_node(v[i], i), Gs(v[i]) * G_CONST)
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * af * ds[i], 1.0)), vg[i + 1], vmax_node[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            ab = np.sqrt(max(abrake(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST     # MEASURED braking ∘ friction circle
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

    # MEASURED braking frontier
    va, aa, th, bk = long_accel(q, RBR)
    brk = (bk > 0.5) & (aa < 0)
    Ab, Bb, vb, db = fit_brake(va[brk], -aa[brk] / G_CONST)
    abrake = lambda vv: min(Ab + Bb * vv * vv, BRAKE_SAT)
    print(f"  braking frontier: A_b={Ab:.2f}g  B_b={Bb*1e3:.2f}e-3  "
          f"(a_brake@80km/h {abrake(22.2):.2f}g, @300km/h {abrake(83.3):.2f}g)")

    # DRS zones
    lap = q.laps.pick_drivers("VER").pick_fastest(); tel = lap.get_car_data().add_distance()
    drs = tel["DRS"].to_numpy(float); dist = tel["Distance"].to_numpy(float)
    o = np.argsort(dist); dist, drs = dist[o], drs[o]
    drs_open_rib = np.interp(pct_rib, dist / dist[-1] * 100, (drs >= 10).astype(float)) > 0.5
    zones = []; inz = False
    for i, z in enumerate(drs_open_rib):
        if z and not inz:
            st = pct_rib[i]; inz = True
        elif not z and inz:
            zones.append((st, pct_rib[i])); inz = False
    vmax_node = np.where(drs_open_rib, a_open["vmax"], a_closed["vmax"])
    a_node = lambda vv, i: max((a_open if drs_open_rib[i] else a_closed)["K"] *
                               ((a_open if drs_open_rib[i] else a_closed)["vmax"] ** 3 / max(vv, 1.0) - vv * vv), 0.0)
    vg = vg_minenv(kappa, A, B, vmax_node)
    v_v5 = sim(s, kappa, vg, a_node, vmax_node, Gs, abrake)
    v_v4 = sim(s, kappa, vg, a_node, vmax_node, Gs, lambda vv: min(A + B * vv * vv, GSAT))  # braking off lateral grip

    profiles = {"v5: measured braking": (pct_rib, v_v5), "v4: lateral-grip braking": (pct_rib, v_v4)}
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
    col = {"v5: measured braking": "tab:red", "v4: lateral-grip braking": "tab:green"}
    for nm, (t, vv) in ts.items():
        c = col.get(nm, "tab:blue" if "VER" in nm else "tab:purple"); lsv = "-" if nm.startswith("v") else "--"
        ax1.plot(grid, vv * 3.6, lsv, color=c, lw=1.3, label=nm); ax2.plot(grid, t - tref, lsv, color=c, lw=1.8)
    for a0, b0 in zones:
        ax1.axvspan(a0, b0, color="gold", alpha=0.12); ax2.axvspan(a0, b0, color="gold", alpha=0.12)
    for p in pk:
        for ax in (ax1, ax2):
            ax.axvline(grid[p], color="gray", ls=":", lw=0.7, alpha=0.5)
    ax1.set_ylabel("speed (km/h)"); ax1.legend(fontsize=8, loc="lower center", ncol=2); ax1.grid(alpha=0.3)
    ax1.set_title("Monza/RBR v5 — measured braking frontier (gold=DRS, dotted=corners)")
    ax2.axhline(0, color="k", lw=0.6); ax2.set_ylabel("cum Δt vs VER (s)"); ax2.set_xlabel("% lap"); ax2.grid(alpha=0.3)
    fig.tight_layout(); png = OUT / "lap_trace_v5_monza_rbr.png"; fig.savefig(png, dpi=120); print(f"wrote {png}")
    for nm, (t, vv) in ts.items():
        print(f"  {nm:>26}: lap {t[-1]:.2f}s  min {vv.min()*3.6:.0f}  top {vv.max()*3.6:.0f}")


if __name__ == "__main__":
    main()
