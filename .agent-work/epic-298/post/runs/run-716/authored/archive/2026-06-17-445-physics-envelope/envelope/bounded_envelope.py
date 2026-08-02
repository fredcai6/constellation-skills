"""Bounded cornering-capability envelope per car (epic #445, channel #2).

For each car, pool clean slow/medium-corner grip from quali pushes + every race
lap, and estimate the CEILING at each corner speed (high quantile = best the car
achieved, approaching capability; the spread below is utilization), with a
bootstrap band. This is a LOWER BOUND on true capability (best observed), with
honest uncertainty — never the true ceiling, which we can't observe.

Slow/medium corners only (<185 km/h): grip = v^2/R is reliable there.
Cross-car test: do the bounded envelopes separate, or overlap?
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from envelopes_1d import corner_apexes, lap_arrays  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}
VMAX = 185.0      # km/h — reliable grip regime
Q_CEIL = 0.90     # capability = high quantile (approaching ceiling)
NBOOT = 300
RNG = np.random.default_rng(11)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def apexes_from_lap(ss, run, ls, le):
    la = lap_arrays(ss, run, ls, le)
    if la is None:
        return []
    t, X, Y, v = la
    out = []
    for (va, al) in corner_apexes(t, X, Y, v):
        if va * 3.6 < VMAX:
            out.append((va * 3.6, al / G))
    return out


def collect_quali(session, car):
    runs = H.driver_runs(session, car)
    fits = {}
    pts = []
    for ls, le in flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        pts += apexes_from_lap(ss, run, ls, le)
    return pts


def collect_race(session, car):
    num = driver_num(session, car)
    pos_d, spd_d = driver_streams(session, num)
    laps = session.laps.pick_drivers(car)
    laps = laps[laps["LapTime"].notna()].copy()
    stints = sorted(int(s) for s in laps["Stint"].dropna().unique())
    pts = []
    for st in stints:
        try:
            t0, t1, _ = stint_span(session, car, st)
        except Exception:
            continue
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
        mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < 100 or mc.sum() < 100:
            continue
        try:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                   spd_d["t"][mc], spd_d["V"][mc])
        except Exception:
            continue
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        for _, r in laps[laps["Stint"] == st].iterrows():
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")):
                continue
            if int(r["LapNumber"]) <= 1:
                continue
            pts += apexes_from_lap(ss, run, r["LapStartTime"].total_seconds(),
                                   r["Time"].total_seconds())
    return pts


def ceiling_envelope(pts):
    """High-quantile ceiling per speed bin with bootstrap band."""
    if len(pts) < 20:
        return None
    arr = np.array(pts)
    v, g = arr[:, 0], arr[:, 1]
    edges = np.arange(60, VMAX + 1, 15)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v >= lo) & (v < hi)
        n = int(b.sum())
        if n < 12:
            continue
        gg = g[b]
        ceil = np.quantile(gg, Q_CEIL)
        boots = [np.quantile(RNG.choice(gg, n, replace=True), Q_CEIL) for _ in range(NBOOT)]
        rows.append((0.5 * (lo + hi), ceil, np.percentile(boots, 16),
                     np.percentile(boots, 84), n))
    return np.array(rows) if rows else None


def main():
    log("loading 2023 Japan Q + R ...")
    quali = H.load_session(2023, "Japan", "Q")
    race = H.load_session(2023, "Japan", "R")
    envs = {}
    for car in CARS:
        pts = []
        try:
            pts += collect_quali(quali, car)
        except Exception as exc:
            log(f"  {car} quali: {exc}")
        try:
            pts += collect_race(race, car)
        except Exception as exc:
            log(f"  {car} race: {exc}")
        env = ceiling_envelope(pts)
        if env is not None:
            envs[car] = env
            log(f"  {car}: {len(pts)} corner obs, {len(env)} speed bins")

    print("\n=== bounded cornering-capability ceiling (g) [16,84 band] ===")
    print(f"{'car':>4} {'team':>5} | " + " ".join(f"{s:>16}" for s in ["~70km/h", "~115km/h", "~160km/h"]))
    for car in CARS:
        if car not in envs:
            continue
        e = envs[car]
        def at(vq):
            if vq < e[:, 0].min() or vq > e[:, 0].max():
                return None
            i = np.argmin(np.abs(e[:, 0] - vq))
            return e[i, 1], e[i, 2], e[i, 3]
        cells = []
        for vq in [70, 115, 160]:
            r = at(vq)
            cells.append(f"{r[0]:.2f}[{r[1]:.2f},{r[2]:.2f}]" if r else f"{'--':>16}")
        print(f"{car:>4} {TEAM[car]:>5} | " + " ".join(f"{c:>16}" for c in cells))
    print("\n(ceiling = lower bound on true capability; band = bootstrap [16,84]. "
          "do teams separate beyond bands?)")
    _plot(envs)


def _plot(envs):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    colors = {"RBR": "navy", "MERC": "teal", "WIL": "darkorange"}
    fig, ax = plt.subplots(figsize=(10, 6))
    for car, e in envs.items():
        c = colors[TEAM[car]]
        ax.plot(e[:, 0], e[:, 1], "-o", color=c, ms=4, label=f"{car} ({TEAM[car]})")
        ax.fill_between(e[:, 0], e[:, 2], e[:, 3], color=c, alpha=0.15)
    ax.set_xlabel("corner speed (km/h)")
    ax.set_ylabel("cornering capability ceiling (g)")
    ax.set_title("Bounded cornering-capability envelope (Suzuka 2023 quali+race, slow/med corners)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    png = OUT / "bounded_envelope.png"
    fig.tight_layout()
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
