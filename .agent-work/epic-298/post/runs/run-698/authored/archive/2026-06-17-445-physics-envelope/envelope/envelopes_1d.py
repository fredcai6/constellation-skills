"""Two 1-D capability limits for one car (epic #445) — the simplest model.

Each direction on its own (no combined trade-off yet):
  (1) Forward/backward limit vs speed: strongest braking and strongest
      acceleration at each speed, from the SENSOR-speed rate of change dv/dt
      (1st derivative of a measured quantity -> clean).
  (2) Cornering limit vs speed: sideways grip v^2/R at each corner apex, from
      the validated circle-fit radius.

VER, all flying laps, Suzuka 2023 Q.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from corner_segment import circle_fit  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
DRIVER = "VER"


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def lap_arrays(ss, run, ls, le):
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    o = np.argsort(t)
    t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    if len(t) < 50:
        return None
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])
    return t, X, Y, v


def long_accel(t, v, W=2):
    """dv/dt from sensor speed via a tight local slope (captures braking bite)."""
    n = len(v)
    a = np.full(n, np.nan)
    for i in range(n):
        c, d = max(0, i - W), min(n, i + W + 1)
        if d - c >= 3:
            tt, vv = t[c:d], v[c:d]
            tb = tt - tt.mean()
            den = (tb * tb).sum()
            if den > 1e-9:
                a[i] = (tb * (vv - vv.mean())).sum() / den
    return a


def corner_apexes(t, X, Y, v, N=5):
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    n = len(v)
    R = np.full(n, np.nan)
    for i in range(n):
        a, b = max(0, i - N), min(n, i + N + 1)
        if b - a >= 5:
            r = circle_fit(X[a:b], Y[a:b])
            if np.isfinite(r) and 3 < r < 5000:
                R[i] = r
    alat = np.nan_to_num(v**2 / R, nan=0.0)
    idx, _ = find_peaks(alat, height=5.0, prominence=4.0, distance=4)
    out = []
    for i in idx:
        if v[i] * 3.6 > 45 and np.isfinite(R[i]) and alat[i] / G < 6.0:
            out.append((v[i], alat[i]))   # (apex speed m/s, apex lateral m/s^2)
    return out


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    runs = H.driver_runs(session, DRIVER)
    fits = {}
    v_all, along_all, apex = [], [], []
    nlaps = 0
    for ls, le in flying_windows(session, DRIVER):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        la = lap_arrays(ss, run, ls, le)
        if la is None:
            continue
        t, X, Y, v = la
        nlaps += 1
        a = long_accel(t, v)
        ok = np.isfinite(a)
        v_all.append(v[ok])
        along_all.append(a[ok])
        apex += corner_apexes(t, X, Y, v)
    v_all = np.concatenate(v_all)
    along_all = np.concatenate(along_all)
    log(f"{nlaps} flying laps, {len(v_all)} nodes, {len(apex)} corner apexes")

    # (1) forward/backward limit vs speed
    edges = np.arange(20, 92, 8)
    print("\n--- forward/backward limit vs speed ---")
    print(f"{'speed(km/h)':>11} {'max brake(g)':>13} {'max accel(g)':>13} {'n':>5}")
    brake_curve, accel_curve, mids = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v_all >= lo) & (v_all < hi)
        if b.sum() < 15:
            continue
        seg = along_all[b]
        brk = -np.percentile(seg[seg < 0], 5) if (seg < 0).any() else np.nan   # strongest decel
        acc = np.percentile(seg[seg > 0], 95) if (seg > 0).any() else np.nan
        mid = 0.5 * (lo + hi)
        mids.append(mid)
        brake_curve.append(brk)
        accel_curve.append(acc)
        print(f"{mid*3.6:11.0f} {brk/G:13.2f} {acc/G:13.2f} {int(b.sum()):5d}")

    # (2) cornering limit vs speed (apexes)
    apex = np.array(apex)
    print("\n--- cornering limit vs speed (corner apexes) ---")
    aedges = np.arange(15, 90, 12)
    print(f"{'apex(km/h)':>11} {'corner(g)':>11} {'n':>4}")
    cs, cg = [], []
    for lo, hi in zip(aedges[:-1], aedges[1:]):
        m = (apex[:, 0] >= lo) & (apex[:, 0] < hi)
        if m.sum() < 2:
            continue
        mid, gmean = 0.5 * (lo + hi), np.median(apex[m, 1])
        cs.append(mid)
        cg.append(gmean)
        print(f"{mid*3.6:11.0f} {gmean/G:11.2f} {int(m.sum()):4d}")

    _plot(mids, brake_curve, accel_curve, apex, cs, cg)


def _plot(mids, brake_curve, accel_curve, apex, cs, cg):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    mk = np.array(mids) * 3.6
    ax1.plot(mk, np.array(brake_curve) / G, "o-", color="firebrick", label="strongest braking")
    ax1.plot(mk, np.array(accel_curve) / G, "o-", color="seagreen", label="strongest acceleration")
    ax1.set_xlabel("speed (km/h)")
    ax1.set_ylabel("acceleration limit (g)")
    ax1.set_title("Forward/backward grip limit vs speed")
    ax1.grid(alpha=0.3)
    ax1.legend()
    ax2.scatter(apex[:, 0] * 3.6, apex[:, 1] / G, s=18, alpha=0.5, color="slateblue",
                label="each corner apex")
    ax2.plot(np.array(cs) * 3.6, np.array(cg) / G, "o-", color="black", label="median")
    ax2.set_xlabel("corner apex speed (km/h)")
    ax2.set_ylabel("cornering limit (g)")
    ax2.set_title("Cornering grip limit vs speed")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig.suptitle(f"{DRIVER} Suzuka 2023 Q — capability limits (each direction alone)")
    fig.tight_layout()
    png = OUT / "limits_1d_ver.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
