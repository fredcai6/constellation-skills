"""Robustness of the apex-speed feature pace-relevance (#445).

(1) the fitted log-R slope beta per weekend (should be ~0.5 if v_apex ~ sqrt(a_lat*R))
(2) leave-one-team-out: is the -0.89 Spearman driven by a single team?
(3) bootstrap CI on Spearman(apex_q90, quali) over teams
(4) split-half stability: features from odd vs even rounds, do they agree?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import apex_feature as AF  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
RNG = np.random.default_rng(7)


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])


def main():
    d = AF.load()
    qp = AF.quali_pace_team()
    vapex = d["v_apex"].astype(float)
    Rapex = d["R_apex"].astype(float)

    # (1) per-weekend beta on log R
    print("(1) fitted log-R slope beta per weekend (expect ~0.5):")
    betas = []
    for rnd in d["rounds"]:
        m = d["round"] == rnd
        car = d["car"][m]; y = vapex[m]; g = Rapex[m]
        ok = np.isfinite(y) & np.isfinite(g) & (g > 0) & (y > 0)
        car, y, g = car[ok], y[ok], g[ok]
        cars = [c for c in set(car) if (car == c).sum() >= 10]
        mm = np.isin(car, cars)
        car, y, g = car[mm], y[mm], g[mm]
        if len(cars) < 4:
            continue
        cidx = {c: j for j, c in enumerate(cars)}
        X = np.zeros((len(y), 1 + len(cars))); X[:, 0] = np.log(g)
        for j, c in enumerate(cars):
            X[car == c, 1 + j] = 1.0
        coef, *_ = np.linalg.lstsq(X, np.log(y), rcond=None)
        betas.append(coef[0])
    print(f"    beta: mean {np.mean(betas):.3f}  median {np.median(betas):.3f}  "
          f"range {min(betas):.2f}-{max(betas):.2f}  (n={len(betas)})")

    # build the headline feature once
    fAq = AF.season_feature(d, vapex, Rapex, use_quantile=0.90)
    tAq = AF.team_agg(fAq)
    teams = sorted(set(tAq) & set(qp))
    f = np.array([tAq[t] for t in teams]); g = np.array([qp[t] for t in teams])
    base = spearman(f, g)
    print(f"\n(2) headline Spearman(apex_q90, quali) = {base:+.3f} over {len(teams)} teams")

    # leave-one-team-out
    print("    leave-one-team-out Spearman:")
    for i, t in enumerate(teams):
        idx = [j for j in range(len(teams)) if j != i]
        sp = spearman(f[idx], g[idx])
        print(f"      drop {t}: {sp:+.3f}")

    # (3) bootstrap CI (resample teams)
    boots = []
    for _ in range(2000):
        idx = RNG.integers(0, len(teams), len(teams))
        if len(set(idx)) < 4:
            continue
        boots.append(spearman(f[idx], g[idx]))
    boots = np.array(boots)
    print(f"\n(3) bootstrap Spearman: median {np.median(boots):+.3f}  "
          f"[{np.percentile(boots,5):+.3f}, {np.percentile(boots,95):+.3f}] (90% CI)")

    # (4) split-half: odd vs even rounds
    rounds = list(d["rounds"])
    odd = set(rounds[::2]); even = set(rounds[1::2])
    def feat_subset(rset):
        m = np.isin(d["round"], list(rset))
        ds = {k: (d[k][m] if d[k].shape == d["round"].shape else d[k]) for k in d}
        ds["round"] = d["round"][m]; ds["car"] = d["car"][m]
        ds["rounds"] = np.array(sorted(rset))
        ff = AF.season_feature(ds, ds["v_apex"].astype(float),
                               ds["R_apex"].astype(float), use_quantile=0.90)
        return AF.team_agg(ff)
    fo = feat_subset(odd); fe = feat_subset(even)
    common = sorted(set(fo) & set(fe))
    print(f"\n(4) split-half stability (odd vs even rounds), {len(common)} teams:")
    print(f"    Spearman(odd-feat, even-feat) = "
          f"{spearman([fo[t] for t in common],[fe[t] for t in common]):+.3f}")
    print(f"    odd-half  vs quali: {spearman([fo[t] for t in common],[qp[t] for t in common]):+.3f}")
    print(f"    even-half vs quali: {spearman([fe[t] for t in common],[qp[t] for t in common]):+.3f}")


if __name__ == "__main__":
    main()
