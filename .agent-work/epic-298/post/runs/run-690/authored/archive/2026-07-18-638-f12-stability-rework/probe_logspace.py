# .agent-work/638-f12-stability-rework/probe_logspace.py
"""G1 follow-up: does fitting in (log10 radius, lateral_g) space stabilize k AND locations?

Root cause from diagnose_k_instability.py: raw radius_m is a smooth heavy-tailed continuum
(p1=21m..p99=1169m, ~2 decades, right-skewed). GMM means land at density-weighted positions
that shift with circuit composition -> even FIXED-k locations are unstable (1/5). radius is
physically multiplicative (adjacent corner classes differ by ~order of magnitude), so log10
radius should be far more symmetric and its modes far more composition-stable.

Compares RAW vs LOG descriptor space on the 5 F12 splits, both BIC-selected and fixed-k, with
an agreement stat computed IN the fit's own space (log uses a log-radius scale). Subsampled per
half for speed (the winner is confirmed on full real data by the actual gate in G3).
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
# Frozen-from-domain log-radius scale: adjacent corner-radius classes differ by ~a factor of
# ~2 (e.g. 20m hairpin -> ~45m -> ~90m medium -> ~180m fast) => ~0.30 in log10. Chosen from
# reasoning, not tuned to results (mirrors the raw RADIUS_SCALE_M=50 rationale in log space).
LOG_RADIUS_SCALE = 0.30
SUB = 60000


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


def transform(d, logspace):
    d = np.asarray(d, float)
    if logspace:
        return np.column_stack([np.log10(d[:, 0]), d[:, 1]])
    return d


def fit_select(d, logspace, seed, k_range=(2, 6)):
    """BIC + support-floor selection in the chosen space; returns (k, means_in_space)."""
    X0 = transform(d, logspace)
    sc = StandardScaler(); X = sc.fit_transform(X0)
    N = X.shape[0]
    cand = {}
    for k in range(k_range[0], k_range[1] + 1):
        g = GaussianMixture(n_components=k, random_state=seed).fit(X)
        bic = -2 * g.score(X) * N + g._n_parameters() * np.log(N)
        if g.weights_.min() >= FLOOR:
            cand[k] = (bic, g, sc)
    if not cand:
        g = GaussianMixture(n_components=1, random_state=seed).fit(X); return 1, sc.inverse_transform(g.means_)
    k = min(cand, key=lambda kk: cand[kk][0])
    _, g, sc = cand[k]
    return k, sc.inverse_transform(g.means_)


def fit_fixed(d, logspace, seed, kfix):
    X0 = transform(d, logspace)
    sc = StandardScaler(); X = sc.fit_transform(X0)
    g = GaussianMixture(n_components=kfix, random_state=seed).fit(X)
    return kfix, sc.inverse_transform(g.means_)


def agreement(means_a, means_b, logspace):
    if means_a.shape[0] != means_b.shape[0]:
        return float("inf")
    rscale = LOG_RADIUS_SCALE if logspace else 50.0
    scale = np.array([rscale, LATERAL_G_SCALE])
    na, nb = means_a / scale, means_b / scale
    dist = np.linalg.norm(na[:, None, :] - nb[None, :, :], axis=-1)
    r, c = linear_sum_assignment(dist)
    return float(np.linalg.norm(na - nb[c], axis=1).mean())


def sub(d, seed):
    d = np.asarray(d, float)
    if d.shape[0] > SUB:
        d = d[np.random.default_rng(seed).choice(d.shape[0], SUB, replace=False)]
    return d


def run(dbc, logspace, mode, kfix=None):
    names = list(dbc.keys())
    npass = 0
    label = f"{'LOG' if logspace else 'RAW'} space, {mode}"
    print(f"\n=== {label} ===", flush=True)
    for i, seed, ca, cb in splits(names):
        da = sub(np.concatenate([dbc[c] for c in ca]), seed)
        db = sub(np.concatenate([dbc[c] for c in cb]), seed)
        if mode == "BIC":
            ka, ma = fit_select(da, logspace, seed); kb, mb = fit_select(db, logspace, seed)
        else:
            ka, ma = fit_fixed(da, logspace, seed, kfix); kb, mb = fit_fixed(db, logspace, seed, kfix)
        st = agreement(ma, mb, logspace)
        p = st < 1.0; npass += int(p)
        s = "inf" if st == float("inf") else f"{st:.4f}"
        print(f"  split {i}: k_a={ka} k_b={kb} stat={s} {'PASS' if p else 'FAIL'}", flush=True)
    print(f"  n_pass = {npass}/5", flush=True)
    return npass


def main():
    print(f"Loading... (SUB={SUB})", flush=True)
    dbc = load()
    print(f"{len(dbc)} circuits", flush=True)
    # density shape in log space
    pooled = np.concatenate(list(dbc.values()))
    lr = np.log10(pooled[:, 0])
    q = np.percentile(lr, [1, 10, 25, 50, 75, 90, 99])
    print(f"log10(radius): p1={q[0]:.2f} p10={q[1]:.2f} p25={q[2]:.2f} p50={q[3]:.2f} p75={q[4]:.2f} p90={q[5]:.2f} p99={q[6]:.2f}", flush=True)
    run(dbc, False, "BIC")
    run(dbc, True, "BIC")
    for kf in (2, 3, 4):
        run(dbc, True, f"FIXED k={kf}", kfix=kf)
    # show log-space BIC centroids for split 0
    print("\n=== LOG-space BIC centroids (split0), raw radius_m via 10**logr ===", flush=True)
    _, seed, ca, cb = next(splits(list(dbc.keys())))[:4] if False else (0, 42, None, None)
    for i, seed, ca, cb in splits(list(dbc.keys())):
        da = sub(np.concatenate([dbc[c] for c in ca]), seed)
        db = sub(np.concatenate([dbc[c] for c in cb]), seed)
        ka, ma = fit_select(da, True, seed); kb, mb = fit_select(db, True, seed)
        def fmt(m):
            o = np.argsort(m[:, 0])
            return ", ".join(f"(r={10**m[j,0]:.0f}m,lat={m[j,1]:.2f}g)" for j in o)
        print(f"  split{i} A k={ka}: {fmt(ma)}", flush=True)
        print(f"  split{i} B k={kb}: {fmt(mb)}", flush=True)
        break


if __name__ == "__main__":
    main()
