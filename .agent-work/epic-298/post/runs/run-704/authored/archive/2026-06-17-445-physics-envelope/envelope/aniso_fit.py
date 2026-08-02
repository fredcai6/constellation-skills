"""Anisotropy test (#445): does a PURE-LATERAL grip frontier carry cleaner / different
car signal than the isotropic g_tot MAGNITUDE frontier — and at what uncertainty cost?

Two frontiers per weekend (both shared-A + per-car-B, the established fitter):
  M (magnitude, current): g = hypot(alat, along)   on ALL cornering nodes
  L (pure lateral):       g = alat                 on near-apex nodes (|along|/alat < THRESH)

We assumed isotropy on purpose: pooling combined-loading nodes into one magnitude gives
MORE data -> firmer estimate. Anisotropy splits that, so uncertainty must rise. The test:
does the lateral channel reveal car signal (teammate-consistent, between>within) that the
magnitude blends away, and does the signal GAIN beat the uncertainty LOSS?

Metrics, M vs L:
  - teammate B gap (same car -> noise proxy)            lower = cleaner
  - between-team / within-team spread ratio              higher = more car signal
  - bootstrap R on B*vref^2 (the uncertainty COST)       lower = firmer
  - season-rank Spearman(M, L)                            ~1 => lateral adds nothing new
  - 'combined excess' G_M-G_L per car, teammate-consistent? => combined-loading IS a car axis
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from season_prior_filter import fit_weekend, VREF, GSAT  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "aniso_nodes_full.npz"
THRESH = 0.30          # |along|/alat below this = near-apex 'pure lateral'
MIN_LAT = 18           # min pure-lateral nodes to fit a car that weekend
NBOOT = 30
DRV2TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER",
            "SAI": "FER", "NOR": "MCL", "PIA": "MCL", "ALO": "AMR", "STR": "AMR",
            "GAS": "ALP", "OCO": "ALP", "ALB": "WIL", "SAR": "WIL", "TSU": "ATR",
            "DEV": "ATR", "RIC": "ATR", "LAW": "ATR", "BOT": "ALF", "ZHO": "ALF",
            "MAG": "HAA", "HUL": "HAA"}
RNG = np.random.default_rng(3)


def load():
    d = np.load(CACHE, allow_pickle=True)
    rounds = [str(x) for x in d["rounds"]]; cars = [str(x) for x in d["cars"]]
    out = []
    for r in rounds:
        cl = {}
        for c in cars:
            k = f"v__{r}__{c}"
            if k in d.files:
                cl[c] = dict(v=d[f"v__{r}__{c}"].astype(float),
                             alat=d[f"alat__{r}__{c}"].astype(float),
                             along=d[f"along__{r}__{c}"].astype(float),
                             w=d[f"w__{r}__{c}"].astype(float))
        if cl:
            out.append((r, cl))
    return out


def clouds_mag(cl):
    return {c: (d["v"], np.hypot(d["alat"], d["along"]), d["w"]) for c, d in cl.items()}


def clouds_lat(cl):
    out = {}
    for c, d in cl.items():
        m = np.abs(d["along"]) < THRESH * d["alat"]
        if m.sum() >= MIN_LAT:
            out[c] = (d["v"][m], d["alat"][m], d["w"][m])
    return out


def teammate_gaps(B):
    bt = {}
    for k, val in B.items():
        t = DRV2TEAM.get(k)
        if t:
            bt.setdefault(t, []).append(val)
    return [abs(v[0] - v[1]) for v in bt.values() if len(v) == 2]


def team_means(B):
    bt = {}
    for k, val in B.items():
        t = DRV2TEAM.get(k)
        if t:
            bt.setdefault(t, []).append(val)
    return {t: np.mean(v) for t, v in bt.items()}


def boot_R(clouds, nboot=NBOOT):
    """bootstrap var of B*vref^2 per car (resample each car's nodes, refit weekend)."""
    cars = list(clouds); acc = {c: [] for c in cars}
    for _ in range(nboot):
        bc = {}
        for c in cars:
            v, g, w = clouds[c]; n = len(v); idx = RNG.integers(0, n, n)
            bc[c] = (v[idx], g[idx], w[idx])
        try:
            _, B = fit_weekend(bc)
        except Exception:
            continue
        for c in cars:
            acc[c].append(B[c] * VREF * VREF)
    return {c: float(np.var(acc[c], ddof=1)) for c in cars if len(acc[c]) > 3}


def spear(a, b):
    if len(a) < 3:
        return np.nan
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    per_round = load()
    print(f"{len(per_round)} weekends, {len(set(c for _, cl in per_round for c in cl))} cars; "
          f"THRESH={THRESH} (|along|/alat), NBOOT={NBOOT}\n")

    gapM, gapL, btwM, btwL, RM, RL = [], [], [], [], [], []
    latfrac = []
    seasonM, seasonL, excess = {}, {}, {}   # car -> list across races
    for rname, cl in per_round:
        cm = clouds_mag(cl); cl_ = clouds_lat(cl)
        cm = {c: v for c, v in cm.items() if len(v[0]) >= 24}
        common = [c for c in cm if c in cl_]
        if len(common) < 4:
            continue
        cm = {c: cm[c] for c in common}; cl_ = {c: cl_[c] for c in common}
        latfrac.append(np.mean([len(cl_[c][0]) / len(cm[c][0]) for c in common]))
        Am, Bm = fit_weekend(cm)
        Al, Bl = fit_weekend(cl_)
        gapM += teammate_gaps(Bm); gapL += teammate_gaps(Bl)
        tmM, tmL = team_means(Bm), team_means(Bl)
        if len(tmM) >= 3:
            vals = np.array(list(tmM.values())) * 1e3
            within = np.mean(teammate_gaps(Bm)) * 1e3 if teammate_gaps(Bm) else np.nan
            btwM.append((vals.std(), within))
        if len(tmL) >= 3:
            vals = np.array(list(tmL.values())) * 1e3
            within = np.mean(teammate_gaps(Bl)) * 1e3 if teammate_gaps(Bl) else np.nan
            btwL.append((vals.std(), within))
        rm = boot_R(cm); rl = boot_R(cl_)
        RM += list(rm.values()); RL += list(rl.values())
        for c in common:
            seasonM.setdefault(c, []).append(Bm[c] * VREF * VREF)
            seasonL.setdefault(c, []).append(Bl[c] * VREF * VREF)
            gm = min(Am + Bm[c] * VREF * VREF, GSAT)
            gl = min(Al + Bl[c] * VREF * VREF, GSAT)
            excess.setdefault(c, []).append(gm - gl)

    print("=" * 80)
    print("ANISOTROPY: pure-lateral (L) vs magnitude (M) frontier")
    print("=" * 80)
    print(f"  pure-lateral kept {np.mean(latfrac)*100:.0f}% of nodes on average\n")
    print(f"  teammate B-gap (1e-3):   M {np.mean(gapM)*1e3:.3f}   L {np.mean(gapL)*1e3:.3f}"
          f"   ({'L cleaner' if np.mean(gapL)<np.mean(gapM) else 'M cleaner'})")
    bM = np.mean([s for s, w in btwM if w == w]); wM = np.mean([w for s, w in btwM if w == w])
    bL = np.mean([s for s, w in btwL if w == w]); wL = np.mean([w for s, w in btwL if w == w])
    print(f"  between/within ratio:    M {bM/wM:.2f}   L {bL/wL:.2f}"
          f"   (higher = more car signal)")
    print(f"  bootstrap R on B*vref^2: M {np.mean(RM):.4f}   L {np.mean(RL):.4f}"
          f"   (uncertainty COST: L/M = {np.mean(RL)/np.mean(RM):.2f}x)")

    # season ranking comparison
    carsS = [c for c in seasonM if len(seasonM[c]) >= 6 and c in seasonL]
    teams = sorted({DRV2TEAM[c] for c in carsS if c in DRV2TEAM})
    smM = {t: np.mean([np.mean(seasonM[c]) for c in carsS if DRV2TEAM.get(c) == t]) for t in teams}
    smL = {t: np.mean([np.mean(seasonL[c]) for c in carsS if DRV2TEAM.get(c) == t]) for t in teams}
    ex = {t: np.mean([np.mean(excess[c]) for c in carsS if DRV2TEAM.get(c) == t]) for t in teams}
    rM = np.array([smM[t] for t in teams]); rL = np.array([smL[t] for t in teams])
    print(f"\n  season-rank Spearman(M, L) = {spear(rM, rL):+.3f}  "
          f"(~1 => lateral reorders nothing; <1 => different ordering)")
    print("\n  per-constructor season downforce grip (g at vref) + combined excess:")
    print(f"  {'team':>5} {'G_mag':>8} {'G_lat':>8} {'excess':>8}")
    for t in sorted(teams, key=lambda k: -smM[k]):
        print(f"  {t:>5} {smM[t]:8.3f} {smL[t]:8.3f} {ex[t]:8.3f}")

    # is the combined excess a CAR axis (teammate-consistent)?
    exgap = []
    bycar_ex = {c: np.mean(excess[c]) for c in carsS}
    bt = {}
    for c, val in bycar_ex.items():
        t = DRV2TEAM.get(c)
        if t:
            bt.setdefault(t, []).append(val)
    exgap = [abs(v[0] - v[1]) for v in bt.values() if len(v) == 2]
    exspread = np.std(list(ex.values()))
    print(f"\n  combined-excess: between-team spread {exspread:.3f} g  vs "
          f"teammate gap {np.mean(exgap):.3f} g")
    print(f"  -> combined loading is a CAR axis if spread >> teammate gap "
          f"({'YES' if exspread > 1.8*np.mean(exgap) else 'NO/marginal'})")


if __name__ == "__main__":
    main()
