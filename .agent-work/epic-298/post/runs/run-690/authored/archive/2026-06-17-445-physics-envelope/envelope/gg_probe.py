"""Geometric acceleration field -> g-g diagram (epic #445 Stage-2 bootstrap).

Replace the smoother's prior-dominated acceleration state (sigma ~3g) with a
geometric acceleration built from MEASURED quantities:
    a_long = dv/dt        (local slope of SENSOR speed; 1st deriv of a measurement)
    a_lat  = v^2 / R       (R from circle fit on smoothed position; centripetal)
Honest sigma on each (a_lat sigma grows where R is unreliable: fast corners, few
points, v^2 amplification). Pool all VER flying laps -> g-g diagram. Validation:
should trace a bounded friction envelope; the outer boundary is the grip
PSEUDO-ceiling (we approach it with varying reliability, never observe it).

Headline: geometric a_lat sigma vs the smoother acceleration-state sigma (~29).
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

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def circle_fit_resid(x, y):
    A = np.column_stack([x, y, np.ones_like(x)])
    b = -(x**2 + y**2)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    a, bb, c = sol
    cx, cy = -a / 2, -bb / 2
    r2 = cx**2 + cy**2 - c
    if r2 <= 0:
        return np.nan, np.nan
    R = np.sqrt(r2)
    resid = np.sqrt(np.mean((np.hypot(x - cx, y - cy) - R) ** 2))
    return float(R), float(resid)


def process_lap(ss, run, ls, le, N=5, Wt=2):
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
    n = len(t)
    a_lat = np.full(n, np.nan)
    s_lat = np.full(n, np.nan)
    a_lon = np.full(n, np.nan)
    for i in range(n):
        a, b = max(0, i - N), min(n, i + N + 1)
        if b - a >= 5:
            R, resid = circle_fit_resid(X[a:b], Y[a:b])
            # Only trust a_lat where the local path is GENUINELY circular: a bad
            # small-R fit through near-straight high-speed points has large
            # residual -> reject (kills the spurious >5g high-speed tail).
            if np.isfinite(R) and 3 < R < 5000 and resid < 0.8 and resid / R < 0.03:
                a_lat[i] = v[i] ** 2 / R
                # honest sigma: R error floored by smoothed-position uncertainty
                # (~0.15 m), NOT just the residual on already-smoothed points.
                sR = max(resid, 0.15)
                s_lat[i] = v[i] ** 2 / R**2 * sR
        c, d = max(0, i - Wt), min(n, i + Wt + 1)
        if d - c >= 3:
            tt, vv = t[c:d], v[c:d]
            tb = tt - tt.mean()
            denom = (tb * tb).sum()
            if denom > 1e-9:
                a_lon[i] = (tb * (vv - vv.mean())).sum() / denom
    return dict(v=v, a_lat=a_lat, s_lat=s_lat, a_lon=a_lon)


def smoother_accel_sigma(ss, ls, le):
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    P = ss.P_s[mask]
    return float(np.median(np.sqrt(np.clip(P[:, 2, 2] + P[:, 5, 5], 0, None))))


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    runs = H.driver_runs(session, "VER")
    fits = {}
    chunks = []
    a_state_sigmas = []
    for ls, le in flying_windows(session, "VER"):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        g = process_lap(ss, run, ls, le)
        if g is not None:
            chunks.append(g)
            a_state_sigmas.append(smoother_accel_sigma(ss, ls, le))
    out = {k: np.concatenate([c[k] for c in chunks]) for k in chunks[0]}
    good = np.isfinite(out["a_lat"]) & np.isfinite(out["a_lon"])
    al, alon, vv = out["a_lat"][good], out["a_lon"][good], out["v"][good]
    slat = out["s_lat"][good]
    log(f"{len(al)} nodes over {len(chunks)} flying laps")

    print("\n--- acceleration uncertainty: smoother state vs geometric ---")
    print(f"  smoother accel-state sigma : {np.mean(a_state_sigmas):6.1f} m/s^2 "
          f"({np.mean(a_state_sigmas)/G:.2f} g)")
    print(f"  geometric a_lat sigma (med): {np.nanmedian(slat):6.1f} m/s^2 "
          f"({np.nanmedian(slat)/G:.2f} g)")
    print(f"  -> reduction factor ~ {np.mean(a_state_sigmas)/max(np.nanmedian(slat),1e-9):.0f}x")

    print("\n--- g-g envelope extent (95th pct) ---")
    print(f"  max |a_lat|   : {np.percentile(al,95):5.1f} m/s^2 ({np.percentile(al,95)/G:.1f} g)")
    acc = alon[alon > 0]
    brk = -alon[alon < 0]
    print(f"  max accel     : {np.percentile(acc,95):5.1f} m/s^2 ({np.percentile(acc,95)/G:.1f} g)")
    print(f"  max braking   : {np.percentile(brk,95):5.1f} m/s^2 ({np.percentile(brk,95)/G:.1f} g)")

    _plot(al, alon, vv)


def _plot(al, alon, vv):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(7, 7))
    sc = ax.scatter(al / G, alon / G, c=vv * 3.6, s=6, cmap="viridis", alpha=0.6)
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlabel("lateral a_lat (g)")
    ax.set_ylabel("longitudinal a_long (g)   [+accel / -brake]")
    ax.set_title("VER Suzuka 2023 Q — g-g diagram (geometric accel, all flying laps)")
    ax.grid(alpha=0.3)
    fig.colorbar(sc, ax=ax, label="speed (km/h)")
    png = OUT / "gg_ver_suzuka.png"
    fig.tight_layout()
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
