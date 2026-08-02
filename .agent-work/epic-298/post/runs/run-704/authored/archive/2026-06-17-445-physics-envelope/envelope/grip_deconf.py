"""Conditions-matrix de-confound, first cut (epic #445, the #2 direction).

Downforce B is tyre-INDEPENDENT (wing/floor aero); the mechanical intercept A
carries compound/wear. So turn race conditions from a confound into signal: fit a
covariate frontier where compound and tyre-age are SHARED tyre-physics terms and
B is per-(car,track):

    g = A + dCompound(soft/med/hard) + wear*age + B(car,track)*v^2   (cap GSAT)

Shared terms are pinned by the POOLED data (all cars, every node), so once removed
the per-(car,track) B uses ALL race volume with the confounds subtracted. Keyed by
(track, DRIVER) so we can re-run the teammate within/between decomposition: did
de-confounding lift the per-car signal out of the noise (vs iter3 ratio 0.61)?

First cut: quali tagged SOFT/age0 (approx); race all valid laps (FULL age range to
fit wear); slicks only; frontier via quantile-IRLS + EM peel. Validation pending.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import grip_iter as GI  # noqa: E402
from grip_iter import GSAT, TEAMS, TRACKS, emit_nodes, gat  # noqa: E402
from envelopes_1d import lap_arrays  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
SLICKS = ("SOFT", "MEDIUM", "HARD")


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_keyed(q, rc, car):
    """(v, gtot, w, compound, age) for quali (SOFT/age0) + all valid race laps."""
    rows = [(v, g, w, "SOFT", 0.0) for (v, g, w) in GI.collect_nodes(q, car)]
    num = driver_num(rc, car); pos_d, spd_d = driver_streams(rc, num)
    laps = rc.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()].copy()
    for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
        try:
            t0, t1, _ = stint_span(rc, car, st)
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
            comp = str(r.get("Compound"))
            if comp not in SLICKS:
                continue
            age = float(r.get("TyreLife")) if pd.notna(r.get("TyreLife")) else 0.0
            la = lap_arrays(ss, run, r["LapStartTime"].total_seconds(), r["Time"].total_seconds())
            if la is None:
                continue
            t, X, Y, v = la
            for (vi, gi, wi) in emit_nodes(t, X, Y, v, base_w=0.5):
                rows.append((vi, gi, wi, comp, age))
    return rows


def fit_deconf(rows_by_key, tau=0.92, band=0.4, iters=35):
    keys = list(rows_by_key)
    V, Gn, W, AGE, COMP, KID = [], [], [], [], [], []
    for j, k in enumerate(keys):
        for (v, g, w, comp, age) in rows_by_key[k]:
            V.append(v); Gn.append(g); W.append(w); AGE.append(age); COMP.append(comp); KID.append(j)
    V = np.array(V); Gn = np.array(Gn); W0 = np.array(W); AGE = np.array(AGE); KID = np.array(KID)
    isMED = np.array([c == "MEDIUM" for c in COMP], float)
    isHARD = np.array([c == "HARD" for c in COMP], float)
    nk = len(keys); ncol = 4 + nk
    A, dMed, dHard, wear = 1.6, -0.1, -0.2, -0.01
    B = np.full(nk, 0.0015)
    for _ in range(iters):
        Gv = np.minimum(A + dMed * isMED + dHard * isHARD + wear * AGE + B[KID] * V * V, GSAT)
        r = Gn - Gv
        member = 1.0 / (1.0 + np.exp(-(Gn - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = W0 * member * qw
        sel = (Gn < GSAT - 0.2) & (w > 1e-9)
        X = np.zeros((int(sel.sum()), ncol))
        X[:, 0] = 1.0; X[:, 1] = isMED[sel]; X[:, 2] = isHARD[sel]; X[:, 3] = AGE[sel]
        vs = V[sel]; ks = KID[sel]
        for j in range(nk):
            X[ks == j, 4 + j] = vs[ks == j] ** 2
        coef = GI.wls(X, Gn[sel], w[sel])
        A = float(np.clip(coef[0], 0.8, 3.2))
        dMed = float(np.clip(coef[1], -1.5, 0.2)); dHard = float(np.clip(coef[2], -1.5, 0.2))
        wear = float(np.clip(coef[3], -0.05, 0.005))
        B = np.clip(coef[4:], 1e-4, 6e-3)
    return dict(A=A, dMed=dMed, dHard=dHard, wear=wear,
                B={keys[j]: float(B[j]) for j in range(nk)},
                n=len(V))


def decompose(Bmap):
    """within-team teammate gap vs between-team car range, per track, on B (1e-3)."""
    within, between = [], []
    for name in TRACKS:
        tmeans = {}
        for team, drvs in TEAMS.items():
            bs = [Bmap[(name, d)] for d in drvs if (name, d) in Bmap]
            if len(bs) == 2:
                within.append(abs(bs[0] - bs[1]) * 1e3)
            if bs:
                tmeans[team] = np.mean(bs) * 1e3
        if len(tmeans) >= 2:
            v = np.array(list(tmeans.values())); between.append(v.max() - v.min())
    return within, between


def main():
    rows = {}
    for name, gp in TRACKS.items():
        log(f"collecting {name} (quali + all race) ...")
        q = GI.H.load_session(2023, gp, "Q")
        rc = GI.H.load_session(2023, gp, "R")
        for team, drvs in TEAMS.items():
            for car in drvs:
                try:
                    rr = collect_keyed(q, rc, car)
                except Exception as e:
                    log(f"  {name}/{car}: {e}"); continue
                if len(rr) < 40:
                    log(f"  {name}/{team}/{car}: thin ({len(rr)}), skip"); continue
                rows[(name, car)] = rr
        log(f"  {name}: {sum(len(v) for k,v in rows.items() if k[0]==name)} nodes")

    fit = fit_deconf(rows)
    print("\n" + "=" * 70)
    print(f"DE-CONFOUNDED FIT ({fit['n']} nodes)  A={fit['A']:.2f}g")
    print("tyre-physics terms (should be PHYSICAL: hard<med<0 grip, wear<0):")
    print(f"  compound offset  MEDIUM {fit['dMed']:+.2f} g   HARD {fit['dHard']:+.2f} g")
    print(f"  wear slope       {fit['wear']:+.4f} g / lap of tyre age")
    print("=" * 70)

    # per-driver B grouped by team
    Bmap = fit["B"]
    print(f"\n{'per-driver downforce B (de-confounded), G@140':>46}")
    for name in TRACKS:
        print(f"\n--- {name} ---")
        for team, drvs in TEAMS.items():
            for d in drvs:
                k = (name, d)
                if k in Bmap:
                    print(f"  {team:>5} {d:>4}: B={Bmap[k]*1e3:5.2f}  G140={gat(fit['A'], Bmap[k], 140):5.2f}")

    within, between = decompose(Bmap)
    wmean = float(np.mean(within)); bmean = float(np.mean(between))
    print("\n" + "=" * 70)
    print("ACID TEST: did de-confounding lift the per-car signal out of the noise?")
    print("=" * 70)
    print(f"  WITHIN-team teammate gap : {wmean:.2f}  (1e-3, n={len(within)})")
    print(f"  BETWEEN-team car range   : {bmean:.2f}  (1e-3, n={len(between)})")
    print(f"  between/within ratio = {bmean/wmean:.2f}   (iter3 quali-only was 0.61)")
    if bmean / wmean >= 1.5:
        print("  -> de-confound WORKED: car signal now dominates teammate scatter.")
    elif bmean / wmean >= 1.0:
        print("  -> partial: car edges ahead of teammate scatter.")
    else:
        print("  -> still driver/line-dominated; de-confound did not separate cars.")

    # constructor-level surviving signal (RBR-high / MERC-low?)
    print("\n  constructor mean B (de-confounded), per track:")
    for name in TRACKS:
        cells = []
        for team, drvs in TEAMS.items():
            bs = [Bmap[(name, d)] for d in drvs if (name, d) in Bmap]
            if bs:
                cells.append(f"{team}={np.mean(bs)*1e3:.2f}")
        print(f"    {name:>8}: " + "  ".join(cells))


if __name__ == "__main__":
    main()
