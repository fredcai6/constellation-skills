# .agent-work/638-f12-stability-rework/probe_final.py
"""G1 final: confirm the 5/5 support-driven winner in LOG space on FULL data.

Tests:
  1. fixed k=4 (log space) location stability, all 5 splits + split3-A k=4 min weight (the
     knife-edge: why full-data BIC+floor dropped it to k=3).
  2. log + bootstrap-modal-k, k_range=(2,4), B=25 (support-driven, floor-knife-edge averaged).
"""
from __future__ import annotations

import sys
from collections import Counter
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


def agreement(ma, mb):
    if ma.shape[0] != mb.shape[0]:
        return float("inf")
    scale = np.array([LOG_RADIUS_SCALE, LATERAL_G_SCALE])
    na, nb = ma / scale, mb / scale
    d = np.linalg.norm(na[:, None, :] - nb[None, :, :], axis=-1)
    r, c = linear_sum_assignment(d)
    return float(np.linalg.norm(na - nb[c], axis=1).mean())


def fit_fixed(d, seed, k):
    sc = StandardScaler(); X = sc.fit_transform(logX(d))
    g = GaussianMixture(n_components=k, random_state=seed).fit(X)
    return sc.inverse_transform(g.means_), g.weights_.min()


def boot_modal(d, seed, k_range=(2, 4), B=25, cap=30000):
    sc = StandardScaler(); X = sc.fit_transform(logX(d)); N = X.shape[0]
    rng = np.random.default_rng(seed); ks = []
    for _ in range(B):
        Xb = X[rng.integers(0, N, size=min(cap, N))]
        cand = {}
        for k in range(k_range[0], k_range[1] + 1):
            g = GaussianMixture(n_components=k, random_state=seed).fit(Xb)
            bic = -2 * g.score(Xb) * Xb.shape[0] + g._n_parameters() * np.log(Xb.shape[0])
            if g.weights_.min() >= FLOOR:
                cand[k] = bic
        ks.append(min(cand, key=cand.get) if cand else 1)
    kbest = Counter(ks).most_common(1)[0][0]
    gfull = GaussianMixture(n_components=kbest, random_state=seed).fit(X)
    return kbest, sc.inverse_transform(gfull.means_), Counter(ks)


def main():
    print("Loading FULL data...", flush=True); dbc = load(); names = list(dbc.keys())

    print("\n=== 1. FIXED k=4 (log space, FULL data) ===", flush=True)
    npass = 0
    for i, seed, ca, cb in splits(names):
        ma, wa = fit_fixed(np.concatenate([dbc[c] for c in ca]), seed, 4)
        mb, wb = fit_fixed(np.concatenate([dbc[c] for c in cb]), seed, 4)
        st = agreement(ma, mb); p = st < 1.0; npass += int(p)
        print(f"  split {i}: stat={st:.4f} {'PASS' if p else 'FAIL'} (wmin_A={wa:.4f} wmin_B={wb:.4f})", flush=True)
    print(f"  n_pass = {npass}/5  [floor={FLOOR}]", flush=True)

    print("\n=== 2. log + bootstrap-modal-k k_range=(2,4) B=25 (FULL data) ===", flush=True)
    npass = 0
    for i, seed, ca, cb in splits(names):
        ka, ma, ca_ct = boot_modal(np.concatenate([dbc[c] for c in ca]), seed)
        kb, mb, cb_ct = boot_modal(np.concatenate([dbc[c] for c in cb]), seed)
        st = agreement(ma, mb); p = st < 1.0; npass += int(p)
        s = "inf" if st == float("inf") else f"{st:.4f}"
        print(f"  split {i}: k_a={ka} k_b={kb} stat={s} {'PASS' if p else 'FAIL'}  (A={dict(ca_ct)} B={dict(cb_ct)})", flush=True)
    print(f"  n_pass = {npass}/5", flush=True)


if __name__ == "__main__":
    main()
