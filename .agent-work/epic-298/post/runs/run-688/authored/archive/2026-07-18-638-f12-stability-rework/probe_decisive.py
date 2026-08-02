# .agent-work/638-f12-stability-rework/probe_decisive.py
"""G1 decisive test (FULL real data, log space): which support-driven k-selector gives
matched k + sub-threshold locations on ALL 5 F12 splits?

Findings so far: LOG-radius space fixes location stability (fixed k=2,4 -> 5/5); the only
remaining issue is agreeing on the integer k. CV/BIC over full N saturate the k_range ceiling
(both halves -> ceiling, so k AGREES) but k=6 over-tiles (one marginal fail). So test:
  (a) log + BIC, k_range=(2,4)   -- ceiling = physically-motivated max corner-severity classes
  (b) log + BIC, k_range=(2,3)
  (c) log + bootstrap-modal-k, k_range=(2,6)  -- support-driven, noise-averaged
All on FULL data (this is the real gate behavior). Pre-fit k=1..6 per half ONCE.
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


class Half:
    def __init__(self, d, seed):
        self.sc = StandardScaler(); self.X = self.sc.fit_transform(logX(d)); self.N = self.X.shape[0]
        self.g, self.bic, self.wmin = {}, {}, {}
        for k in range(1, 7):
            gm = GaussianMixture(n_components=k, random_state=seed).fit(self.X)
            self.g[k] = gm
            self.bic[k] = -2 * gm.score(self.X) * self.N + gm._n_parameters() * np.log(self.N)
            self.wmin[k] = gm.weights_.min()

    def means(self, k):
        return self.sc.inverse_transform(self.g[k].means_)

    def bic_k(self, k_range):
        cand = {k: self.bic[k] for k in range(k_range[0], k_range[1] + 1) if self.wmin[k] >= FLOOR}
        return min(cand, key=cand.get) if cand else 1

    def boot_modal_k(self, seed, k_range=(2, 6), B=21, cap=20000):
        rng = np.random.default_rng(seed)
        ks = []
        for _ in range(B):
            idx = rng.integers(0, self.N, size=min(cap, self.N))
            Xb = self.X[idx]
            cand = {}
            for k in range(k_range[0], k_range[1] + 1):
                gm = GaussianMixture(n_components=k, random_state=seed).fit(Xb)
                bic = -2 * gm.score(Xb) * Xb.shape[0] + gm._n_parameters() * np.log(Xb.shape[0])
                if gm.weights_.min() >= FLOOR:
                    cand[k] = bic
            ks.append(min(cand, key=cand.get) if cand else 1)
        return Counter(ks).most_common(1)[0][0]


def main():
    print("Loading FULL data...", flush=True)
    dbc = load(); names = list(dbc.keys())
    print("Pre-fitting k=1..6 per half (full data, log space)...", flush=True)
    HF = {}
    for i, seed, ca, cb in splits(names):
        A = Half(np.concatenate([dbc[c] for c in ca]), seed)
        B = Half(np.concatenate([dbc[c] for c in cb]), seed)
        HF[i] = (seed, A, B)
        print(f"  split {i} fitted (N_a={A.N}, N_b={B.N})", flush=True)

    for kr in ((2, 4), (2, 3), (2, 5)):
        rows = []
        for i in range(5):
            _, A, B = HF[i]
            ka, kb = A.bic_k(kr), B.bic_k(kr)
            st = agreement(A.means(ka), B.means(kb)); rows.append((i, ka, kb, st))
        npass = sum(1 for _, _, _, s in rows if s < 1.0)
        print(f"\n=== log + BIC k_range={kr} (FULL data) ===", flush=True)
        for i, ka, kb, s in rows:
            ss = "inf" if s == float("inf") else f"{s:.4f}"
            print(f"  split {i}: k_a={ka} k_b={kb} stat={ss} {'PASS' if s<1.0 else 'FAIL'}", flush=True)
        print(f"  n_pass = {npass}/5", flush=True)

    # bootstrap-modal-k
    rows = []
    for i in range(5):
        seed, A, B = HF[i]
        ka, kb = A.boot_modal_k(seed), B.boot_modal_k(seed)
        st = agreement(A.means(ka), B.means(kb)); rows.append((i, ka, kb, st))
    npass = sum(1 for _, _, _, s in rows if s < 1.0)
    print(f"\n=== log + bootstrap-modal-k k_range=(2,6) B=21 (FULL data) ===", flush=True)
    for i, ka, kb, s in rows:
        ss = "inf" if s == float("inf") else f"{s:.4f}"
        print(f"  split {i}: k_a={ka} k_b={kb} stat={ss} {'PASS' if s<1.0 else 'FAIL'}", flush=True)
    print(f"  n_pass = {npass}/5", flush=True)

    # centroids for k_range=(2,4) both halves, all splits (physical adequacy + stability visual)
    print("\n=== CENTROIDS log+BIC k_range=(2,4), raw radius via 10**logr ===", flush=True)
    for i in range(5):
        _, A, B = HF[i]
        ka, kb = A.bic_k((2, 4)), B.bic_k((2, 4))
        def fmt(m):
            o = np.argsort(m[:, 0]); return ", ".join(f"(r={10**m[j,0]:.0f}m,lat={m[j,1]:.2f}g)" for j in o)
        print(f"  split{i} A k={ka}: {fmt(A.means(ka))}", flush=True)
        print(f"  split{i} B k={kb}: {fmt(B.means(kb))}", flush=True)


if __name__ == "__main__":
    main()
