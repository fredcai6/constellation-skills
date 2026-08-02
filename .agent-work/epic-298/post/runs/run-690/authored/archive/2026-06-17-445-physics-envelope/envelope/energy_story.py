"""Geometry bootstrap -> staged acceleration -> coherent energy story (#445).

Stage 0: raw smoother acceleration (prior-dominated, big sigma).
Stage 1: geometry-refined "smoother acceleration":
   a_long = dv/dt from SENSOR speed (3-pt central, clean);
   a_lat  = v^2/R from circle fit where reliable (slow/med corners, good fit),
            else FALL BACK to Stage 0 (keeping its honest large sigma).
Both saved as append-only ledger layers. Energy story off the best stage:
   E(s) = 1/2 m v^2 ;  power P = dE/dt = m v a_long ;  account in/out + valleys.
Demonstrator: VER Suzuka 2023 quali fastest lap.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_segment import circle_fit  # noqa: E402
import truth_ledger as TL  # noqa: E402

G = 9.81
MASS = 808.0          # kg, 2023 reg-min incl driver (~798) + ~10 kg quali fuel
MASS_SIG = 6.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
RNG = np.random.default_rng(3)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def stage0_accel(m, P):
    """Raw smoother tangential/normal accel + sigma via MC on [vx,vy,ax,ay]."""
    vx, vy, ax, ay = m[:, 1], m[:, 4], m[:, 2], m[:, 5]
    sel = np.array([1, 4, 2, 5])
    cov = P[:, sel][:, :, sel]
    cov = 0.5 * (cov + np.transpose(cov, (0, 2, 1))) + 1e-9 * np.eye(4)
    n = len(vx)
    L = np.linalg.cholesky(cov)
    z = RNG.standard_normal((n, 96, 4))
    samp = np.stack([vx, vy, ax, ay], 1)[:, None, :] + np.einsum("nij,nkj->nki", L, z)
    sx, sy, sax, say = samp[..., 0], samp[..., 1], samp[..., 2], samp[..., 3]
    v = np.maximum(np.hypot(sx, sy), 1e-3)
    along = (sax * sx + say * sy) / v
    lat = (sax * sy - say * sx) / v
    return (along.mean(1), along.std(1), lat.mean(1), lat.std(1))


def stage1_accel(t, v, X, Y, a_lat0, s_lat0, N=5):
    """Geometry-refined accel. a_long from sensor dv/dt; a_lat from v^2/R where
    the local circle fit is reliable, else fall back to Stage 0."""
    n = len(v)
    along = np.full(n, np.nan)
    s_along = np.full(n, np.nan)
    lat = np.full(n, np.nan)
    s_lat = np.full(n, np.nan)
    SIG_V = 0.49
    for i in range(n):
        # a_long: 3-pt central slope of sensor speed
        a, b = max(0, i - 1), min(n, i + 2)
        if b - a >= 2:
            dt = t[b - 1] - t[a]
            if dt > 1e-6:
                along[i] = (v[b - 1] - v[a]) / dt
                s_along[i] = SIG_V * np.sqrt(2) / dt
        # a_lat from local circle fit
        c, d = max(0, i - N), min(n, i + N + 1)
        reliable = False
        if d - c >= 5:
            xx, yy = X[c:d], Y[c:d]
            R = circle_fit(xx, yy)
            if np.isfinite(R) and 3 < R < 5000:
                cx = -(np.column_stack([xx, yy, np.ones_like(xx)]))
                # residual of the fit
                A = np.column_stack([xx, yy, np.ones_like(xx)])
                sol, *_ = np.linalg.lstsq(A, -(xx**2 + yy**2), rcond=None)
                ccx, ccy = -sol[0] / 2, -sol[1] / 2
                resid = np.sqrt(np.mean((np.hypot(xx - ccx, yy - ccy) - R) ** 2))
                if resid / R < 0.03 and v[i] * 3.6 < 185:
                    lat[i] = v[i] ** 2 / R
                    s_lat[i] = v[i] ** 2 / R**2 * max(resid, 0.15)
                    reliable = True
        if not reliable:
            lat[i] = a_lat0[i]      # fall back to Stage 0 (keep honest sigma)
            s_lat[i] = s_lat0[i]
    return along, s_along, lat, s_lat


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    laps = session.laps.pick_drivers("VER")
    laps = laps[laps["LapTime"].notna()]
    fl = laps.loc[laps["LapTime"].idxmin()]
    ls, le = fl["LapStartTime"].total_seconds(), fl["Time"].total_seconds()
    runs = H.driver_runs(session, "VER")
    run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le),
               max(runs, key=lambda r: r["t1"] - r["t0"]))
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])

    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    o = np.argsort(t)
    t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    m = ss.m_s[mask][o][keep]
    P = ss.P_s[mask][o][keep]
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])           # sensor speed
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    log(f"lap: {len(t)} nodes, {s[-1]:.0f} m")

    path = TL.ledger_path(2023, "Japan", "Q", "VER", int(fl["LapNumber"]))
    if path.exists():
        path.unlink()  # fresh demo
    TL.save_base(path, s, t, v, meta_extra={"mass_kg": MASS, "mass_sigma": MASS_SIG})

    # Stage 0
    al0, sal0, lat0, slat0 = stage0_accel(m, P)
    TL.save_stage(path, "s0_smoother",
                  {"a_long": al0, "a_long_sigma": sal0, "a_lat": lat0, "a_lat_sigma": slat0},
                  "raw Kalman-RTS acceleration state (prior-dominated)")
    # Stage 1
    al1, sal1, lat1, slat1 = stage1_accel(t, v, X, Y, lat0, slat0)
    TL.save_stage(path, "s1_geometry",
                  {"a_long": al1, "a_long_sigma": sal1, "a_lat": lat1, "a_lat_sigma": slat1},
                  "geometry-refined: dv/dt sensor + v^2/R reliable corners, else s0")
    log(f"ledger saved: {path}")
    log(f"  Stage0 median sigma: a_long {np.nanmedian(sal0)/G:.2f}g  a_lat {np.nanmedian(slat0)/G:.2f}g")
    log(f"  Stage1 median sigma: a_long {np.nanmedian(sal1)/G:.2f}g  a_lat {np.nanmedian(slat1)/G:.2f}g")

    # Energy story from best stage
    a_long, sa_long = TL.best_field(path, "a_long", ["s0_smoother", "s1_geometry"])
    E = 0.5 * MASS * v**2
    P_pow = MASS * v * a_long
    sP = np.abs(MASS * v) * sa_long
    dt = np.diff(t)
    Padd = np.sum(np.clip(P_pow[:-1], 0, None) * dt)
    Prem = np.sum(np.clip(-P_pow[:-1], 0, None) * dt)
    log("\n--- energy account (VER quali lap) ---")
    log(f"  KE range: {E.min()/1e6:.2f} - {E.max()/1e6:.2f} MJ "
        f"(apex {v.min()*3.6:.0f} km/h, top {v.max()*3.6:.0f} km/h)")
    log(f"  energy added by propulsion: {Padd/1e6:.2f} MJ")
    log(f"  energy removed (brake+drag): {Prem/1e6:.2f} MJ")
    log(f"  balance (should ~0 over a loop): {(Padd-Prem)/1e6:+.2f} MJ")
    log(f"  peak propulsion power: {np.nanpercentile(P_pow,99)/1e6:.2f} MW  "
        f"peak braking power: {np.nanpercentile(-P_pow,99)/1e6:.2f} MW")
    _plot(s, v, E, P_pow, sP, al0, sal0, al1, sal1, lat0, slat0, lat1, slat1)


def _plot(s, v, E, P_pow, sP, al0, sal0, al1, sal1, lat0, slat0, lat1, slat1):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(3, 1, figsize=(13, 11), sharex=True)
    # accel stages: longitudinal
    ax[0].fill_between(s, (al0 - sal0) / G, (al0 + sal0) / G, color="gray", alpha=0.3,
                       label="Stage 0 raw ±σ")
    ax[0].plot(s, al1 / G, color="seagreen", lw=1.3, label="Stage 1 refined (a_long)")
    ax[0].fill_between(s, (al1 - sal1) / G, (al1 + sal1) / G, color="seagreen", alpha=0.25)
    ax[0].set_ylabel("a_long (g)")
    ax[0].set_title("Longitudinal accel: Stage 0 (raw, wide band) vs Stage 1 (refined)")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    # lateral
    ax[1].fill_between(s, (lat0 - slat0) / G, (lat0 + slat0) / G, color="gray", alpha=0.3,
                       label="Stage 0 raw ±σ")
    ax[1].plot(s, lat1 / G, color="navy", lw=1.0, label="Stage 1 refined (a_lat)")
    ax[1].set_ylabel("a_lat (g)")
    ax[1].set_title("Lateral accel: Stage 1 refined where corners reliable, else Stage 0")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    # energy + power
    ax2 = ax[2]
    ax2.plot(s, E / 1e6, color="black", label="kinetic energy (MJ)")
    ax2.set_ylabel("KE (MJ)"); ax2.set_xlabel("arc length (m)")
    axb = ax2.twinx()
    axb.plot(s, P_pow / 1e6, color="firebrick", alpha=0.6, label="power dE/dt (MW)")
    axb.axhline(0, color="k", lw=0.4)
    axb.set_ylabel("power (MW)  [+engine / -brake&drag]", color="firebrick")
    ax2.set_title("Energy story: KE trajectory (valleys=corners) + power flow")
    ax2.legend(loc="upper left", fontsize=8); ax2.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "energy_story_ver.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
