"""Dig into the sim's longitudinal constraints vs reality (#445). RBR Monza: plot the REAL
longitudinal accel dv/dt vs speed (accel + braking, from telemetry) and overlay what the sim
applies — forward bound min(a_meas(v), grip-traction) and braking bound √(G²−a_lat²) (straight-
line → G). See where exit accel is being clipped and what braking capacity the model assumes."""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
from ribbon_reeval import (load_session, driver_num, fit_grip_clean, get_apex_nodes,
                           load_cal_nodes, OUT)  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from ideal_lap_v2 import av_measured  # noqa: E402
from grip_iter import flying_windows  # noqa: E402

G = 9.81
GSAT = 5.2
RBR = ["VER", "PER"]


def long_accel(session, cars):
    """All longitudinal points: (v m/s, a=dv/dt m/s², throttle, brake)."""
    V, A, TH, BK = [], [], [], []
    for car in cars:
        try:
            num = driver_num(session, car); cd = session.car_data[num]
        except Exception:
            continue
        tc = cd["SessionTime"].dt.total_seconds().to_numpy()
        v = cd["Speed"].to_numpy(float) / 3.6
        th = cd["Throttle"].to_numpy(float); bk = cd["Brake"].to_numpy(float)
        for ls, le in flying_windows(session, car):
            m = (tc >= ls) & (tc <= le)
            t, vv, tt, bb = tc[m], v[m], th[m], bk[m]
            o = np.argsort(t); t, vv, tt, bb = t[o], vv[o], tt[o], bb[o]
            keep = np.concatenate([[True], np.diff(t) > 1e-9]); t, vv, tt, bb = t[keep], vv[keep], tt[keep], bb[keep]
            for i in range(1, len(t) - 1):
                dt = t[i + 1] - t[i - 1]
                if dt > 0:
                    V.append(vv[i]); A.append((vv[i + 1] - vv[i - 1]) / dt); TH.append(tt[i]); BK.append(bb[i])
    return map(np.array, (V, A, TH, BK))


def main():
    q = load_session(2023, "Italy", "Q"); cal = load_cal_nodes()
    v, a, th, bk = long_accel(q, RBR)
    vk, gg = get_apex_nodes(cal, "Italy", RBR); A, B, _ = fit_grip_clean(vk, gg)
    vt, at, _ = throttle_av(q, RBR); mv = av_measured(vt, at)
    vmax = mv["vmax"]; K = mv["K"]

    accel = (th > 90) & (bk < 0.5) & (a > -2)
    brake = (bk > 0.5) & (a < 0)          # Brake is boolean (0/1)

    vv = np.linspace(15, vmax, 200)
    a_meas = K * (vmax ** 3 / vv - vv ** 2) / G          # measured full-throttle frontier (g)
    Gs = np.minimum(A + B * vv * vv, GSAT)               # grip (g): traction cap (+) / braking cap (−)
    fwd_bound = np.minimum(a_meas, Gs)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.scatter(v[accel] * 3.6, a[accel] / G, s=6, alpha=0.25, color="seagreen", label="real accel (full throttle)")
    ax.scatter(v[brake] * 3.6, a[brake] / G, s=6, alpha=0.25, color="firebrick", label="real braking")
    ax.plot(vv * 3.6, a_meas, "g--", lw=1.6, label="a_meas(v): measured power/drag frontier")
    ax.plot(vv * 3.6, Gs, "b-", lw=1.6, label="grip-traction cap  G(v)")
    ax.plot(vv * 3.6, fwd_bound, "k-", lw=2.2, label="SIM forward bound = min(a_meas, G)")
    ax.plot(vv * 3.6, -Gs, "b-", lw=1.6, alpha=0.6)
    ax.plot(vv * 3.6, -Gs, "k:", lw=2.2, label="SIM braking bound = −G(v) (straight-line)")
    ax.axhline(0, color="gray", lw=0.6); ax.axvline(vmax * 3.6, color="green", ls=":", lw=1)
    ax.set_xlabel("speed (km/h)"); ax.set_ylabel("longitudinal accel (g)")
    ax.set_title("RBR Monza — real longitudinal envelope vs SIM constraints")
    ax.legend(fontsize=8, loc="upper right"); ax.grid(alpha=0.3)
    fig.tight_layout(); png = OUT / "long_constraints_monza_rbr.png"; fig.savefig(png, dpi=120)
    print(f"wrote {png}\n  grip A={A:.2f} B={B*1e3:.2f}e-3, vmax={vmax*3.6:.0f}")

    # numeric: real vs sim bound, by speed band
    for lab, lo, hi in [("EXIT 60-120", 60, 120), ("MID 120-220", 120, 220), ("HIGH 220-330", 220, 330)]:
        ma = accel & (v * 3.6 >= lo) & (v * 3.6 < hi)
        mb = brake & (v * 3.6 >= lo) & (v * 3.6 < hi)
        if ma.sum() > 5:
            vb = np.median(v[ma]); simf = min(K * (vmax ** 3 / vb - vb ** 2) / G, np.minimum(A + B * vb * vb, GSAT))
            print(f"  {lab}: real accel p90 {np.percentile(a[ma]/G,90):.2f}g  sim-fwd-bound {simf:.2f}g  (n={ma.sum()})")
        if mb.sum() > 5:
            vb = np.median(v[mb]); simb = -min(A + B * vb * vb, GSAT)
            print(f"  {lab}: real brake p10 {np.percentile(a[mb]/G,10):.2f}g  sim-brake-bound {simb:.2f}g  (n={mb.sum()})")


if __name__ == "__main__":
    main()
