# .agent-work/638-f12-stability-rework/probe_logselect.py
"""G1 part-2: in LOG space (locations already proven stable), find a k-SELECTOR that agrees
across halves and stays support-driven. Fit component LOCATIONS on full data at the selected k;
select k on a modest budget so BIC's parsimony penalty bites (raw N over-selects to the ceiling).

Candidates (log space, support floor kept):
  - subsample-BIC: select k by BIC on an N_SELECT-row subsample, refit locations on full data.
  - CV: select k by max per-point held-out LL (5-fold), refit locations on full.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sqlite3
from scipy.optimize import linear_sum_assignment
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

_WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_WORKTREE))
import src.physics.layer2.property_mixture as _pm
assert "f1-638" in _pm.__file__
from src.physics.layer2.corner_descriptors import descriptors_from_frame
from src.physics.layer2.property_mixture import MIN_COMPONENT_WEIGHT_FRAC as FLOOR

DB = "C:/Programs/f1Brainz/data/damage_integrals.db"
LATERAL_G_SCALE = 0.5
LOG_RADIUS_SCALE = 0.30
SUB = 80000  # per-half working cap for this probe (speed); G3 confirms on full real data


def load():
    uri = Path(DB).resolve().as_uri() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        df = pd.read_sql_query("SELECT gp_name, mu_lat_p90, v_mean FROM grip_bin_obs", con)
    finally:
        con.close()
    out = {}
    for gp, g in df.groupby("gp_name"):
        d = descriptors_from_frame(g)
        if d.shape[0] > 0:
            out[gp] = d
    return out


def splits(names, base_seed=42, n=5):
    names = sorted(names)
    for i in range(n):
        seed = base_seed + i
        sh = list(np.random.default_rng(seed).permutation(np.array(names, dtype=object)))
        h = len(sh) // 2
        yield i, seed, [str(x) for x in sh[:h]], [str(x) for x in sh[h:]]


def logX(d):
    d = np.asarray(d, float)
    return np.column_stack([np.log10(d[:, 0]), d[:, 1]])


def sub(d, seed, n):
    d = np.asarray(d, float)
    if d.shape[0] > n:
        d = d[np.random.default_rng(seed).choice(d.shape[0], n, replace=False)]
    return d


def select_subsample_bic(d, seed, n_select, k_range=(2, 6)):
    """k by BIC on an n_select subsample; locations refit at that k on ALL of d (log space)."""
    X0 = logX(d); sc = StandardScaler(); Xfull = sc.fit_transform(X0)
    Xs = sub(Xfull, seed, n_select)
    Ns = Xs.shape[0]
    cand = {}
    for k in range(k_range[0], k_range[1] + 1):
        g = GaussianMixture(n_components=k, random_state=seed).fit(Xs)
        bic = -2 * g.score(Xs) * Ns + g._n_parameters() * np.log(Ns)
        if g.weights_.min() >= FLOOR:
            cand[k] = bic
    if not cand:
        kbest = 1
    else:
        kbest = min(cand, key=cand.get)
    gfull = GaussianMixture(n_components=kbest, random_state=seed).fit(Xfull)
    return kbest, sc.inverse_transform(gfull.means_)


def select_cv(d, seed, k_range=(2, 6), folds=5, cap=40000):
    X0 = logX(d); sc = StandardScaler(); Xfull = sc.fit_transform(X0)
    Xc = sub(Xfull, seed, cap); N = Xc.shape[0]
    idx = np.array_split(np.random.default_rng(seed).permutation(N), folds)
    cvll = {}
    for k in range(k_range[0], k_range[1] + 1):
        tot = 0.0
        for f in range(folds):
            te = idx[f]; tr = np.concatenate([idx[j] for j in range(folds) if j != f])
            g = GaussianMixture(n_components=k, random_state=seed).fit(Xc[tr])
            tot += g.score(Xc[te]) * len(te)
        cvll[k] = tot / N
    cand = {}
    for k in range(k_range[0], k_range[1] + 1):
        g = GaussianMixture(n_components=k, random_state=seed).fit(Xfull)
        if g.weights_.min() >= FLOOR:
            cand[k] = cvll[k]
    kbest = max(cand, key=cand.get) if cand else 1
    gfull = GaussianMixture(n_components=kbest, random_state=seed).fit(Xfull)
    return kbest, sc.inverse_transform(gfull.means_)


def agreement(ma, mb):
    if ma.shape[0] != mb.shape[0]:
        return float("inf")
    scale = np.array([LOG_RADIUS_SCALE, LATERAL_G_SCALE])
    na, nb = ma / scale, mb / scale
    dist = np.linalg.norm(na[:, None, :] - nb[None, :, :], axis=-1)
    r, c = linear_sum_assignment(dist)
    return float(np.linalg.norm(na - nb[c], axis=1).mean())


def run(dbc, selector, label):
    names = list(dbc.keys()); npass = 0
    print(f"\n=== {label} ===", flush=True)
    for i, seed, ca, cb in splits(names):
        da = sub(np.concatenate([dbc[c] for c in ca]), seed, SUB)
        db = sub(np.concatenate([dbc[c] for c in cb]), seed, SUB)
        ka, ma = selector(da, seed); kb, mb = selector(db, seed)
        st = agreement(ma, mb); p = st < 1.0; npass += int(p)
        s = "inf" if st == float("inf") else f"{st:.4f}"
        print(f"  split {i}: k_a={ka} k_b={kb} stat={s} {'PASS' if p else 'FAIL'}", flush=True)
    print(f"  n_pass = {npass}/5", flush=True)
    return npass


def main():
    print("Loading...", flush=True); dbc = load(); print(f"{len(dbc)} circuits", flush=True)
    for ns in (1000, 2000, 5000):
        run(dbc, lambda d, s, ns=ns: select_subsample_bic(d, s, ns), f"LOG + subsample-BIC (N_select={ns})")
    run(dbc, lambda d, s: select_cv(d, s), "LOG + CV (max held-out LL)")


if __name__ == "__main__":
    main()
