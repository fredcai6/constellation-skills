"""Longitudinal channel: drag + engine power via throttle/brake regimes (#445).

Grip bounds cornering AND longitudinal (traction at low speed, braking). What
grip does NOT bound -- engine power (high speed) and drag -- is the missing ~85%
of the pace gap. Separate the regimes with the throttle/brake channels:
  COAST (throttle off, no brake): a_long = -drag/m -> drag (CdA), DRS-closed.
  FULL THROTTLE: m v a_long = P_engine - drag*v -> engine power.
  BRAKING: a_long = -(brake+drag)/m, grip-limited -> check vs G(v)+drag.
Pool VER Suzuka quali flying laps.
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

G = 9.81
RHO = 1.2          # air density kg/m^3
MASS = 808.0       # kg (quali)
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


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
        if len(t) < 50:
            continue
        for i in range(1, len(t) - 1):
            dt = t[i + 1] - t[i - 1]
            if dt <= 0 or v[i] < 8:
                continue
            a = (v[i + 1] - v[i - 1]) / dt
            rows.append((v[i], a, th[i], bk[i], dr[i]))
    return np.array(rows)   # v, a_long, throttle, brake, drs


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    d = collect(session, "VER")
    v, a, thr, brk, drs = d[:, 0], d[:, 1], d[:, 2], d[:, 3], d[:, 4]
    drs_closed = drs < 9
    log(f"{len(v)} nodes; throttle>90 {np.mean(thr>90)*100:.0f}%, "
        f"coast(thr<5&nobrake) {np.mean((thr<5)&(brk<1))*100:.0f}%, "
        f"braking {np.mean(brk>0)*100:.0f}%")

    # --- DRAG from coast (throttle off, no brake, DRS closed) ---
    coast = (thr < 8) & (brk < 1) & drs_closed & (v > 25)
    log(f"\n--- DRAG (coast nodes: {coast.sum()}) ---")
    if coast.sum() >= 20:
        vc, ac = v[coast], a[coast]
        # a = -(0.5 rho CdA/m) v^2 - Crr g  ; lower-envelope (least decel = pure drag)
        # use robust: per v-bin, the 25th pct of -a (least decel ~ cleanest coast)
        edges = np.arange(25, 90, 8)
        vb, ab = [], []
        for lo, hi in zip(edges[:-1], edges[1:]):
            b = (vc >= lo) & (vc < hi)
            if b.sum() >= 5:
                vb.append(vc[b].mean()); ab.append(np.percentile(ac[b], 50))
        vb, ab = np.array(vb), np.array(ab)
        A = np.column_stack([vb**2, np.ones_like(vb)])
        coef, *_ = np.linalg.lstsq(A, ab, rcond=None)
        CdA = -coef[0] * 2 * MASS / RHO
        Crr = -coef[1] / G
        log(f"  CdA = {CdA:.2f} m^2,  rolling Crr = {Crr:.3f}")
        log(f"  drag decel at 300 km/h: {0.5*RHO*CdA*(300/3.6)**2/MASS/G:.2f} g")
    else:
        CdA = 1.2
        log(f"  too few coast nodes; assuming CdA={CdA}")

    # --- ENGINE POWER from full throttle (DRS closed) ---
    full = (thr > 95) & (brk < 1) & drs_closed & (v > 20)
    log(f"\n--- ENGINE POWER (full-throttle nodes: {full.sum()}) ---")
    vf, af = v[full], a[full]
    P = MASS * vf * af + 0.5 * RHO * CdA * vf**3      # engine power = KE rate + drag power
    edges = np.arange(20, 90, 8)
    print(f"  {'speed(km/h)':>11} {'P_engine(kW)':>13} {'n':>4}")
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (vf >= lo) & (vf < hi)
        if b.sum() >= 5:
            print(f"  {0.5*(lo+hi)*3.6:11.0f} {np.percentile(P[b],90)/1e3:13.0f} {int(b.sum()):4d}")
    log(f"  peak P_engine (90th pct): {np.percentile(P, 95)/1e3:.0f} kW")

    # --- BRAKING vs grip+drag ---
    braking = (brk > 0) & (v > 25)
    log(f"\n--- BRAKING (nodes: {braking.sum()}) vs grip ceiling ---")
    vbk, abk = v[braking], -a[braking]   # positive decel
    edges = np.arange(25, 90, 10)
    print(f"  {'speed(km/h)':>11} {'max brake(g)':>13} {'grip+drag(g)':>13}")
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (vbk >= lo) & (vbk < hi)
        if b.sum() >= 5:
            vm = 0.5 * (lo + hi)
            meas = np.percentile(abk[b], 95) / G
            drag_g = 0.5 * RHO * CdA * vm**2 / MASS / G
            Gv = min(1.8 + 0.00177 * vm**2, 4.95)     # VER grip ceiling
            print(f"  {vm*3.6:11.0f} {meas:13.2f} {Gv+drag_g:13.2f}")
    print("\n(braking measured under-reads at 4.2Hz; grip+drag is the physical bound.)")
    _plot(v, a, thr, brk, drs_closed, CdA)


def _plot(v, a, thr, brk, drs_closed, CdA):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    coast = (thr < 8) & (brk < 1) & drs_closed
    full = (thr > 95) & (brk < 1) & drs_closed
    braking = brk > 0
    other = ~(coast | full | braking)
    for msk, c, lbl in [(other, "lightgray", "part-throttle"),
                        (full, "seagreen", "full throttle"),
                        (coast, "navy", "coast (drag)"),
                        (braking, "firebrick", "braking")]:
        ax.scatter(v[msk] * 3.6, a[msk] / G, s=6, alpha=0.5, color=c, label=lbl)
    vv = np.linspace(25, 330, 100) / 3.6
    ax.plot(vv * 3.6, -0.5 * RHO * CdA * vv**2 / MASS / G, "k--", lw=1.5,
            label=f"pure drag (CdA={CdA:.2f})")
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlabel("speed (km/h)"); ax.set_ylabel("longitudinal accel (g)")
    ax.set_title("VER Suzuka quali — longitudinal channel by throttle/brake regime")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    png = OUT / "longitudinal_channel.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
