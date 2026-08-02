"""Grip frontier, iteration 2: feed the high-speed downforce end with RACE nodes
via the EM peel — and measure the cost of the shared-mu assumption (epic #445).

The downforce term B is starved of high-speed at-the-limit data in quali alone.
Race laps have many more fast-corner samples; the EM membership peel keeps only
at-the-limit nodes (dropping tyre-management/lift laps). BUT mechanical grip A
(=mu*g) is NOT common across cars in race conditions (compound splits, wear,
thermal state move mu per car), so the shared-A assumption that holds in quali is
violated. Guard against the loss:
  - FRESH-tyre gate (low TyreLife) -> race nodes closest to quali mu.
  - race nodes DOWN-weighted vs quali.
  - robustness: fit A SHARED and A FREED (per car); compare the signal on
    G@140 km/h (downforce-dominated, ~insensitive to the A/B split). Survive both
    => real; only shared-A => the caveat bit.
  - make the loss visible: freed per-car A spread + compound/age mix of race nodes.
"""
from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import grip_iter as GI  # noqa: E402
from grip_iter import GSAT, VMAX, TEAMS, TRACKS, emit_nodes, fit_independent, fit_shared, fit_global, gat  # noqa: E402
from envelopes_1d import lap_arrays  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
MAX_AGE = 6          # fresh-tyre gate: keep laps with TyreLife <= this
RACE_W = 0.4         # down-weight race nodes vs quali


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_race(session, car):
    """Cornering nodes from FRESH-tyre race laps; also return (compound, age)."""
    num = driver_num(session, car)
    pos_d, spd_d = driver_streams(session, num)
    laps = session.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()].copy()
    pts, meta = [], []
    for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
        try:
            t0, t1, _ = stint_span(session, car, st)
        except Exception:
            continue
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1); mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < 100:
            continue
        ss = GI.H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
        ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp], spd_d["t"][mc], spd_d["V"][mc])
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        for _, r in laps[laps["Stint"] == st].iterrows():
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")) or int(r["LapNumber"]) <= 1:
                continue
            age = r.get("TyreLife")
            if pd.notna(age) and float(age) > MAX_AGE:
                continue
            la = lap_arrays(ss, run, r["LapStartTime"].total_seconds(), r["Time"].total_seconds())
            if la is None:
                continue
            t, X, Y, v = la
            new = emit_nodes(t, X, Y, v, base_w=RACE_W)
            pts += new
            meta += [(str(r.get("Compound")), float(age) if pd.notna(age) else -1.0)] * len(new)
    return pts, meta


def hi_count(cloud, lo=120):
    v = cloud[0] * 3.6
    return int((v >= lo).sum())


def run_track(name, gp):
    log(f"==== {name} ({gp}) quali + fresh race ====")
    q = GI.H.load_session(2023, gp, "Q")
    rc = GI.H.load_session(2023, gp, "R")
    clouds_q, clouds_all, meta_all = {}, {}, []
    for team, drvs in TEAMS.items():
        qp, rp, rm = [], [], []
        for car in drvs:
            try:
                qp += GI.collect_nodes(q, car)
            except Exception as e:
                log(f"  {team}/{car} quali: {e}")
            try:
                p, m = collect_race(rc, car); rp += p; rm += m
            except Exception as e:
                log(f"  {team}/{car} race: {e}")
        if len(qp) + len(rp) < 80:
            log(f"  {team}: thin ({len(qp)}q+{len(rp)}r), skip")
            continue
        aq = np.array(qp); aa = np.array(qp + rp)
        clouds_q[team] = (aq[:, 0], aq[:, 1], aq[:, 2])
        clouds_all[team] = (aa[:, 0], aa[:, 1], aa[:, 2])
        meta_all += rm
        log(f"  {team}: quali {len(qp)} (hi {hi_count(clouds_q[team])}) "
            f"+ race {len(rp)} -> hi {hi_count(clouds_all[team])} nodes >=120km/h")
    return dict(q=clouds_q, all=clouds_all, meta=meta_all)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, gp in TRACKS.items():
        try:
            out[name] = run_track(name, gp)
        except Exception as e:
            log(f"  {name} FAILED: {e}")

    # high-speed feed check
    print("\n" + "=" * 74)
    print("HIGH-SPEED (>=120 km/h) node count: quali-only -> +fresh-race")
    print("=" * 74)
    for name, r in out.items():
        for t in r["all"]:
            print(f"  {name:>8} {t:>5}: {hi_count(r['q'][t]):4d} -> {hi_count(r['all'][t]):4d}")

    # signal under SHARED-A vs FREED-A, on G@140 (downforce-dominated)
    print("\n" + "=" * 74)
    print("G@140 km/h rank (1=most fast-corner grip): SHARED-A vs FREED-A, +race")
    print("Mercedes-low must survive BOTH to be real (not a forced-A artifact).")
    print("=" * 74)
    for name, r in out.items():
        clouds = r["all"]
        A_sh, B_sh = fit_shared(clouds)
        g_sh = {t: gat(A_sh, B_sh[t], 140) for t in clouds}
        indepA, g_fr = {}, {}
        for t, (v, g, w) in clouds.items():
            A, B = fit_independent(v, g, w)
            indepA[t] = A; g_fr[t] = gat(A, B, 140)
        ord_sh = sorted(g_sh, key=lambda k: -g_sh[k])
        ord_fr = sorted(g_fr, key=lambda k: -g_fr[k])
        aspread = max(indepA.values()) - min(indepA.values())
        print(f"\n--- {name} (shared A={A_sh:.2f}g; freed-A spread {aspread:.2f}g) ---")
        print(f"{'team':>5} | {'G140_sh':>8} {'#':>2} | {'G140_fr':>8} {'#':>2} | {'A_freed':>7}")
        for t in clouds:
            print(f"{t:>5} | {g_sh[t]:8.2f} {ord_sh.index(t)+1:>2} | "
                  f"{g_fr[t]:8.2f} {ord_fr.index(t)+1:>2} | {indepA[t]:7.2f}")

    # global-A across tracks with the enriched clouds
    out2 = {name: dict(clouds=r["all"]) for name, r in out.items()}
    A_g, B_g = fit_global(out2)
    print("\n" + "=" * 74)
    print(f"GLOBAL-A (+race) = {A_g:.2f}g; per-(track,car) downforce B, rank in track")
    print("=" * 74)
    cols = list(out)
    teams = sorted({t for r in out.values() for t in r["all"]})
    print(f"{'team':>5} | " + " ".join(f"{c:>11}" for c in cols))
    for team in teams:
        cells = []
        for c in cols:
            present = {k: B_g[k] for k in B_g if k[0] == c}
            key = (c, team)
            if key in B_g:
                rk = sorted(present, key=lambda k: -present[k]).index(key) + 1
                cells.append(f"{B_g[key]*1e3:5.2f}(#{rk})")
            else:
                cells.append("--")
        print(f"{team:>5} | " + " ".join(f"{c:>11}" for c in cells))

    # the loss made visible: compound / tyre-age mix of admitted race nodes
    print("\n" + "=" * 74)
    print("ADMITTED RACE NODES — compound & tyre-age mix (the shared-mu risk)")
    print("=" * 74)
    for name, r in out.items():
        comps = Counter(c for c, _ in r["meta"])
        ages = np.array([a for _, a in r["meta"] if a >= 0])
        amed = np.median(ages) if len(ages) else float("nan")
        print(f"  {name:>8}: {dict(comps)}  median TyreLife={amed:.0f}")


if __name__ == "__main__":
    main()
