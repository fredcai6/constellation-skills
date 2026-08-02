"""Friction-circle shape per constructor (epic #445).

Apex-only lateral grip throws away combined-load behavior. The g-g cloud (a_lat,
a_long) at cornering nodes traces the friction circle: entry = trail-brake
(a_long<0, a_lat>0), apex (a_long~0, a_lat max), exit = accel-while-cornering.
Pool both teammates, QUALI (car at the limit). Does the SHAPE -- especially the
trail-brake combined limit -- discriminate cars where pure lateral didn't?
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
VMAX = 185.0
TEAMS = {"RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"], "WIL": ["ALB", "SAR"]}
COL = {"RBR": "navy", "MERC": "teal", "FER": "firebrick", "WIL": "darkorange"}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_gg(session, car):
    runs = H.driver_runs(session, car)
    fits, pts = {}, []
    for ls, le in flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"]); fits[key] = ss
        mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
        t = ss.ts[mask]; o = np.argsort(t); t = t[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
        X, Y = ss.pos_at(t); v = np.interp(t, run["tc"], run["V"])
        n = len(v)
        for i in range(n):
            a, b = max(0, i - 5), min(n, i + 6)
            if b - a < 5:
                continue
            xx, yy = X[a:b], Y[a:b]
            M = np.column_stack([xx, yy, np.ones_like(xx)])
            sol, *_ = np.linalg.lstsq(M, -(xx**2 + yy**2), rcond=None)
            cx, cy = -sol[0] / 2, -sol[1] / 2
            r2 = cx**2 + cy**2 - sol[2]
            if r2 <= 9:
                continue
            R = np.sqrt(r2)
            resid = np.sqrt(np.mean((np.hypot(xx - cx, yy - cy) - R) ** 2))
            if resid / R > 0.03 or v[i] * 3.6 > VMAX:
                continue
            alat = v[i] ** 2 / R / G
            if alat < 0.6:
                continue
            c, dd = max(0, i - 1), min(n, i + 2)
            dt = t[dd - 1] - t[c]
            along = (v[dd - 1] - v[c]) / dt / G if dt > 0 else 0.0
            pts.append((alat, along))
    return pts


def main():
    q = H.load_session(2023, "Japan", "Q")
    data = {}
    for team, drvs in TEAMS.items():
        pts = []
        for car in drvs:
            try:
                pts += collect_gg(q, car)
            except Exception as e:
                log(f"  {team}/{car}: {e}")
        data[team] = np.array(pts)
        log(f"{team}: {len(pts)} cornering nodes")

    print("\n=== friction-circle metrics per constructor (g) ===")
    print(f"{'team':>5} {'lat max':>8} {'brake max':>10} {'trail-brake':>12} {'exit accel':>11}")
    for team, p in data.items():
        if len(p) < 50:
            continue
        al, alon = p[:, 0], p[:, 1]
        latmax = np.percentile(al, 97)
        brake = np.percentile(-alon[al < 1.5], 97) if (al < 1.5).any() else np.nan
        # trail-brake: combined magnitude in braking quadrant at meaningful lateral
        tb = al > 1.5
        comb = np.percentile(np.hypot(al[tb], alon[tb])[alon[tb] < 0], 95) if (tb & (alon < 0)).any() else np.nan
        ex = np.percentile(alon[al > 1.5], 95) if (al > 1.5).any() else np.nan
        print(f"{team:>5} {latmax:8.2f} {brake:10.2f} {comb:12.2f} {ex:11.2f}")
    print("\n(trail-brake = combined |a| while cornering+braking; the combined-load grip "
          "apex-only misses. does it separate cars / favor the under-rated ones?)")
    _plot(data)


def _plot(data):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    for team, p in data.items():
        if len(p) < 50:
            continue
        ax.scatter(p[:, 0], p[:, 1], s=5, alpha=0.25, color=COL[team], label=team)
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlabel("lateral a_lat (g)"); ax.set_ylabel("longitudinal a_long (g)  [+exit / -entry]")
    ax.set_title("Friction circle by constructor (cornering nodes, quali)")
    ax.grid(alpha=0.3); ax.legend(fontsize=9)
    png = OUT / "friction_circle.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
