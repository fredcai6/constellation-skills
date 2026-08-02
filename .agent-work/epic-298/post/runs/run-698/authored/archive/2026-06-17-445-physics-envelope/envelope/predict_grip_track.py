"""NORTH STAR test #2: does the DOWNFORCE fingerprint predict quali pace? (#445)

Drag was null (quali pace is grip-dominated, not drag). The grip/downforce channel
is the one that SHOULD predict cornering pace. Three escalating tests, full grid:
  A. CROSS-SECTIONAL: does season downforce offset rank the 10 constructors by their
     season-average quali pace? (the foundational "capability = pace" link)
  B. INTERACTION: downforce_off × track-DF-demand → track-specific residual.
  C. LEAVE-FUTURE-OUT: build the offset causally through race N-1, predict race N's
     constructor pace order; beat the recency baselines (last race, season-avg)?

Reads full-grid grip nodes (season_prior_collect_full.py) + cached quali pace.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from season_prior_filter import fit_weekend, VREF  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NODES = OUT / "season_prior_nodes_full.npz"
PACE = OUT / "quali_pace_2023.json"

DRV2TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER",
            "SAI": "FER", "NOR": "MCL", "PIA": "MCL", "ALO": "AMR", "STR": "AMR",
            "GAS": "ALP", "OCO": "ALP", "ALB": "WIL", "SAR": "WIL", "TSU": "ATR",
            "DEV": "ATR", "RIC": "ATR", "LAW": "ATR", "BOT": "ALF", "ZHO": "ALF",
            "MAG": "HAA", "HUL": "HAA"}


def load_full():
    d = np.load(NODES, allow_pickle=True)
    rounds = [str(x) for x in d["rounds"]]
    cars = [str(x) for x in d["cars"]]
    per_round = []
    for r in rounds:
        clouds = {}
        for c in cars:
            k = f"v__{r}__{c}"
            if k in d.files:
                clouds[c] = (d[f"v__{r}__{c}"].astype(float),
                             d[f"g__{r}__{c}"].astype(float),
                             d[f"w__{r}__{c}"].astype(float))
        if clouds:
            per_round.append((r, clouds))
    return per_round


def constructor_offsets(per_round):
    """Per race: fit weekend, per-driver downforce term -> constructor mean ->
    offset vs field; also field-DF level and node counts."""
    seq = []
    for rname, clouds in per_round:
        A, B = fit_weekend(clouds)
        gdrv = {c: B[c] * VREF * VREF for c in clouds}
        # aggregate to constructor
        teamvals, teamn = {}, {}
        for drv, val in gdrv.items():
            t = DRV2TEAM.get(drv)
            if t is None:
                continue
            teamvals.setdefault(t, []).append(val)
            teamn[t] = teamn.get(t, 0) + len(clouds[drv][0])
        gteam = {t: float(np.mean(v)) for t, v in teamvals.items()}
        fmean = float(np.mean(list(gteam.values())))
        off = {t: gteam[t] - fmean for t in gteam}
        seq.append(dict(race=rname, off=off, fieldDF=fmean, n=teamn))
    return seq


def kfilter(seq, q0=2.5e-4):
    """Forward causal filter per constructor; R from node count (1/n proxy)."""
    teams = sorted({t for s in seq for t in s["off"]})
    state = {}; traj = {t: [] for t in teams}
    for s in seq:
        for t in teams:
            if t not in s["off"]:
                if t in state:
                    m, P = state[t]; state[t] = (m, P + q0)
                continue
            y = s["off"][t]; R = max(0.02, 4.0 / max(s["n"].get(t, 1), 1))
            if t not in state:
                state[t] = (y, 4 * R)
            else:
                m, P = state[t]; P += q0; K = P / (P + R)
                state[t] = (m + K * (y - m), (1 - K) * P)
            traj[t].append((s["race"], state[t][0]))
    return traj, state


def spear(a, b):
    if len(a) < 3:
        return np.nan
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return np.corrcoef(ra, rb)[0, 1]


def main():
    if not NODES.exists():
        print("full-grid nodes not ready yet:", NODES); return
    per_round = load_full()
    seq = constructor_offsets(per_round)
    rounds = [s["race"] for s in seq]
    print(f"{len(seq)} races, "
          f"{len(set(t for s in seq for t in s['off']))} constructors")

    _, final = kfilter(seq)
    df_off = {t: final[t][0] for t in final}              # season-filtered downforce offset

    pace = {int(k): v for k, v in json.loads(PACE.read_text()).items()}
    # map race-name -> round index in pace via order (pace keyed by round 1..22)
    pace_by_round = [pace[r] for r in sorted(pace)]
    # align: seq is in collection order = round order; assume same ordering
    teams = sorted(df_off)
    TEAMMAP = {"RBR": "RBR", "MERC": "MERC", "FER": "FER", "MCL": "MCL", "AMR": "AMR",
               "ALP": "ALP", "WIL": "WIL", "ATR": "ATR", "ALF": "ALF", "HAA": "HAA"}

    # season-avg pace gap per team
    gap_season = {}
    for t in teams:
        vals = [pr[t] for pr in pace_by_round if t in pr]
        if vals:
            gap_season[t] = float(np.mean(vals))

    common = [t for t in teams if t in gap_season]
    x = np.array([df_off[t] for t in common]); y = np.array([gap_season[t] for t in common])
    print("\n" + "=" * 72)
    print("TEST A — CROSS-SECTIONAL: downforce offset vs season-avg quali pace")
    print("=" * 72)
    print(f"{'team':>5} {'df_off':>8} {'pace_gap(s)':>12}")
    for t in sorted(common, key=lambda k: -df_off[k]):
        print(f"{t:>5} {df_off[t]:+8.3f} {gap_season[t]:+12.3f}")
    print(f"\n  corr(df_off, pace_gap) = {np.corrcoef(x, y)[0,1]:+.3f}  "
          f"(expect NEGATIVE: more downforce -> faster -> smaller gap)")
    print(f"  Spearman rank = {spear(x, y):+.3f}")

    # TEST B — interaction with track DF demand
    print("\n" + "=" * 72)
    print("TEST B — INTERACTION: df_off × track-DF-demand → track residual pace")
    print("=" * 72)
    fieldDF = {s["race"]: s["fieldDF"] for s in seq}
    dfmean = np.mean(list(fieldDF.values()))
    rows = []
    for i, s in enumerate(seq):
        pr = pace_by_round[i]
        for t in s["off"]:
            if t not in pr or t not in gap_season:
                continue
            resid = pr[t] - gap_season[t]
            axis = fieldDF[s["race"]] - dfmean
            rows.append((t, i, resid, df_off[t] * axis))
    yy = np.array([r[2] for r in rows]); xx = np.array([r[3] for r in rows])
    b = np.sum(xx * yy) / np.sum(xx * xx)
    print(f"  n={len(rows)}; interaction β={b:+.3f}, corr={np.corrcoef(xx,yy)[0,1]:+.3f}")
    print("  (expect NEGATIVE: high-DF car [df_off>0] at high-DF track [axis>0] -> faster)")

    # TEST C — leave-future-out: predict race N order from causal filter
    print("\n" + "=" * 72)
    print("TEST C — LEAVE-FUTURE-OUT: predict race N pace order vs baselines")
    print("=" * 72)
    cap_s, last_s, savg_s = [], [], []
    for n in range(4, len(seq)):
        # causal downforce offset through race n-1
        _, st = kfilter(seq[:n])
        cappred = {t: st[t][0] for t in st}
        prN = pace_by_round[n]
        tgt = [t for t in prN if t in cappred]
        if len(tgt) < 5:
            continue
        actual = np.array([prN[t] for t in tgt])
        cap = np.array([-cappred[t] for t in tgt])               # more DF -> faster (neg gap)
        last = np.array([pace_by_round[n-1].get(t, 0.0) for t in tgt])
        savg = np.array([np.mean([pace_by_round[k].get(t, np.nan) for k in range(n)
                                  if t in pace_by_round[k]]) for t in tgt])
        cap_s.append(spear(cap, -actual))                        # predict fastest=rank
        last_s.append(spear(-last, -actual))
        savg_s.append(spear(-savg, -actual))
    print(f"  predict-next-race rank corr (higher=better):")
    print(f"    capability fingerprint : {np.nanmean(cap_s):+.3f}")
    print(f"    baseline last-race pace: {np.nanmean(last_s):+.3f}")
    print(f"    baseline season-avg    : {np.nanmean(savg_s):+.3f}")
    print(f"  (n={len(cap_s)} predicted races; does capability beat recency?)")


if __name__ == "__main__":
    main()
