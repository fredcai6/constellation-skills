"""Recast grip-from-geometry into RACE conditions (epic #445 wilderness).

One car, one race: corner grip per lap, tagged with compound / tyre age / lap
(fuel). Split SLOW-corner grip (mechanical, wear-sensitive) from FAST-corner grip
(downforce, fuel/mass-sensitive). Three signatures predicted, each a different
shape -> separable:
  - tyre age: grip falls within each stint (sawtooth, resets at pit stop)
  - fuel:     fast-corner grip drifts UP across the race (lighter -> downforce/m
              term grows); ~independent of stint
  - compound: step change between stints
Stint-based segmentation (race pit stops are too short to show as speed gaps).
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
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
DRIVER = "VER"


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    log("loading 2023 Japan R ...")
    session = H.load_session(2023, "Japan", "R")
    num = driver_num(session, DRIVER)
    pos_d, spd_d = driver_streams(session, num)
    laps = session.laps.pick_drivers(DRIVER)
    laps = laps[laps["LapTime"].notna()].copy()
    stints = sorted(int(s) for s in laps["Stint"].dropna().unique())
    log(f"{DRIVER}: {len(laps)} timed laps, stints {stints}")

    rows = []
    for st in stints:
        try:
            t0, t1, _ = stint_span(session, DRIVER, st)
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
        except Exception as exc:
            log(f"  stint {st}: smoother failed ({exc})")
            continue
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        stlaps = laps[laps["Stint"] == st]
        nlap = 0
        for _, r in stlaps.iterrows():
            # racing laps only: skip in/out laps and lap 1
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")):
                continue
            if int(r["LapNumber"]) <= 1:
                continue
            ls, le = r["LapStartTime"].total_seconds(), r["Time"].total_seconds()
            la = lap_arrays(ss, run, ls, le)
            if la is None:
                continue
            t, X, Y, v = la
            apex = corner_apexes(t, X, Y, v)
            if len(apex) < 4:
                continue
            apex = np.array(apex)
            vk = apex[:, 0] * 3.6
            slow = apex[(vk < 130), 1]
            fast = apex[(vk > 180), 1]
            rows.append(dict(
                lap=int(r["LapNumber"]),
                stint=st,
                compound=str(r["Compound"]),
                tyre_age=float(r["TyreLife"]) if pd.notna(r["TyreLife"]) else np.nan,
                grip_slow=float(np.median(slow) / G) if len(slow) else np.nan,
                grip_fast=float(np.median(fast) / G) if len(fast) else np.nan,
                laptime=r["LapTime"].total_seconds(),
            ))
            nlap += 1
        log(f"  stint {st} ({stlaps['Compound'].iloc[0]}): {nlap} racing laps")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "race_recast_ver.csv", index=False)
    print("\n--- per-lap cornering grip across the race ---")
    print(f"{'lap':>4} {'stint':>5} {'comp':>8} {'age':>4} {'slow(g)':>8} {'fast(g)':>8} {'laptime':>8}")
    for _, r in df.iterrows():
        print(f"{r['lap']:4.0f} {r['stint']:5.0f} {r['compound']:>8} "
              f"{r['tyre_age']:4.0f} {r['grip_slow']:8.2f} {r['grip_fast']:8.2f} "
              f"{r['laptime']:8.2f}")

    # crude signature read: within-stint slope (wear) and across-race fast trend (fuel)
    print("\n--- signatures ---")
    for st in stints:
        s = df[df["stint"] == st].dropna(subset=["grip_slow", "tyre_age"])
        if len(s) >= 3:
            sl = np.polyfit(s["tyre_age"], s["grip_slow"], 1)[0]
            print(f"  stint {st} ({s['compound'].iloc[0]}): slow-grip vs tyre age "
                  f"= {sl:+.4f} g/lap  (negative = wear)")
    d2 = df.dropna(subset=["grip_fast", "lap"])
    if len(d2) >= 4:
        ff = np.polyfit(d2["lap"], d2["grip_fast"], 1)[0]
        print(f"  across race: fast-grip vs lap = {ff:+.4f} g/lap "
              f"(positive = fuel burn-off lightening the car)")
    _plot(df, stints)


def _plot(df, stints):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    comps = df["compound"].unique()
    cmap = {"SOFT": "red", "MEDIUM": "gold", "HARD": "dimgray"}
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for c in comps:
        d = df[df["compound"] == c]
        col = cmap.get(c, "blue")
        ax1.scatter(d["lap"], d["grip_slow"], color=col, s=25, label=c)
        ax2.scatter(d["lap"], d["grip_fast"], color=col, s=25, label=c)
    for st in stints[1:]:
        b = df[df["stint"] == st]["lap"].min()
        for ax in (ax1, ax2):
            ax.axvline(b - 0.5, color="k", ls=":", lw=0.8)
    ax1.set_ylabel("slow-corner grip (g)\n[mechanical / wear]")
    ax2.set_ylabel("fast-corner grip (g)\n[downforce / fuel]")
    ax2.set_xlabel("lap number")
    ax1.set_title(f"{DRIVER} Suzuka 2023 RACE — cornering grip vs conditions")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "race_recast_ver.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
