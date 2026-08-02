"""Joint engine-power + drag fit with DRS (two drag curves) (epic #445).

Full-throttle, power-limited: a_long = P/(m v) - 0.5 rho CdA v^2 / m. The 1/v
(power) and v^2 (drag) terms separate by curve SHAPE -> no reliance on the
contaminated coast. DRS opens the wing -> two CdA (open lower), ONE engine power
(DRS doesn't change the PU). Fit P, CdA_closed, CdA_open jointly per car.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num  # noqa: E402

RHO = 1.2
MASS = 808.0
G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = ["VER", "HAM", "ALB"]
TEAM = {"VER": "RBR", "HAM": "MERC", "ALB": "WIL"}
VMIN = 160.0 / 3.6   # power-limited region (above the traction-limited accel peak)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect(session, car):
    num = driver_num(session, car)
    cd = session.car_data[num]
    tc = cd["SessionTime"].dt.total_seconds().to_numpy()
    spd = cd["Speed"].to_numpy(dtype=float) / 3.6
    thr = cd["Throttle"].to_numpy(dtype=float)
    brk = cd["Brake"].to_numpy(dtype=float)
    drs = cd["DRS"].to_numpy(dtype=float)
    rows = []
    for ls, le in flying_windows(session, car):
        m = (tc >= ls) & (tc <= le)
        t, v, th, bk, dr = tc[m], spd[m], thr[m], brk[m], drs[m]
        o = np.argsort(t)
        t, v, th, bk, dr = t[o], v[o], th[o], bk[o], dr[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9])
        t, v, th, bk, dr = t[keep], v[keep], th[keep], bk[keep], dr[keep]
        for i in range(1, len(t) - 1):
            dt = t[i + 1] - t[i - 1]
            if dt <= 0:
                continue
            a = (v[i + 1] - v[i - 1]) / dt
            if th[i] > 95 and bk[i] < 1 and v[i] > VMIN:
                rows.append((v[i], a, dr[i]))
    return np.array(rows)


def joint_fit(d):
    """a = P/(m v) - 0.5 rho CdA v^2/m, shared P, CdA per DRS state."""
    v, a, drs = d[:, 0], d[:, 1], d[:, 2]
    op = drs >= 10
    x1 = 1.0 / (MASS * v)
    x2 = 0.5 * RHO * v**2 / MASS
    X = np.column_stack([x1, -x2 * (~op), -x2 * op])
    coef, *_ = np.linalg.lstsq(X, a, rcond=None)
    resid = a - X @ coef
    dof = max(len(a) - 3, 1)
    se = np.sqrt(np.sum(resid**2) / dof * np.diag(np.linalg.inv(X.T @ X)))
    P, CdA_c, CdA_o = coef
    return dict(P=P, CdA_c=CdA_c, CdA_o=CdA_o, sP=se[0], sCc=se[1], sCo=se[2],
               n=len(a), n_open=int(op.sum()))


def vtop(P, CdA):
    return (2 * P / (RHO * CdA)) ** (1 / 3) * 3.6


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    fits = {}
    print(f"\n{'car':>4} {'team':>5} {'P_engine(kW)':>13} {'CdA closed':>11} "
          f"{'CdA open':>10} {'DRS drag cut':>13} {'vtop o/c(km/h)':>15}")
    for car in CARS:
        d = collect(session, car)
        if len(d) < 40:
            log(f"  {car}: only {len(d)} nodes, skip")
            continue
        f = joint_fit(d)
        fits[car] = (f, d)
        cut = 100 * (1 - f["CdA_o"] / f["CdA_c"]) if f["CdA_o"] > 0 else np.nan
        print(f"{car:>4} {TEAM[car]:>5} {f['P']/1e3:6.0f}±{f['sP']/1e3:3.0f}  "
              f"{f['CdA_c']:5.2f}±{f['sCc']:.2f} {f['CdA_o']:5.2f}±{f['sCo']:.2f} "
              f"{cut:11.0f}% {vtop(f['P'],f['CdA_o']):5.0f}/{vtop(f['P'],f['CdA_c']):3.0f}")
    print("\n(P=engine+avg ERS deploy; CdA in m^2; DRS open lower drag -> higher vtop. "
          "ERS-deploy variation along the straight adds scatter.)")
    _plot(fits)


def _plot(fits):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    cols = {"RBR": "navy", "MERC": "teal", "WIL": "darkorange"}
    fig, ax = plt.subplots(figsize=(10, 6))
    vv = np.linspace(VMIN, 95, 80)
    for car, (f, d) in fits.items():
        c = cols[TEAM[car]]
        op = d[:, 2] >= 10
        ax.scatter(d[~op, 0] * 3.6, d[~op, 1] / G, s=6, alpha=0.3, color=c)
        ax.scatter(d[op, 0] * 3.6, d[op, 1] / G, s=10, alpha=0.5, color=c, marker="^")
        a_c = (f["P"] / (MASS * vv) - 0.5 * RHO * f["CdA_c"] * vv**2 / MASS) / G
        a_o = (f["P"] / (MASS * vv) - 0.5 * RHO * f["CdA_o"] * vv**2 / MASS) / G
        ax.plot(vv * 3.6, a_c, color=c, lw=1.5, label=f"{car} DRS-closed")
        ax.plot(vv * 3.6, a_o, color=c, lw=1.5, ls="--", label=f"{car} DRS-open")
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlabel("speed (km/h)"); ax.set_ylabel("longitudinal accel (g)")
    ax.set_title("Joint power+drag fit (full throttle); triangles=DRS open, dashed=DRS-open curve")
    ax.grid(alpha=0.3); ax.legend(fontsize=7, ncol=3)
    png = OUT / "joint_long.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
