# .agent-work/638-f12-stability-rework/diagnose_k_instability.py
"""G1 diagnosis: WHY is F12 k unstable, and which fix stabilizes it? (efficient rewrite)

READ-ONLY against C:/Programs/f1Brainz/data/damage_integrals.db grip_bin_obs.
Run unbuffered: py -u .agent-work/638-f12-stability-rework/diagnose_k_instability.py

Efficiency: for each (split, half) we fit k=1..KMAX GMMs ONCE on the full standardized
descriptors, then derive baseline / effective-N-capped-BIC / narrower-k_range selections from
those same fits (no refits). Subsample + CV variants use their own lighter fits.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

_WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_WORKTREE))
import src.physics.layer2.property_mixture as _pm
assert "f1-638" in _pm.__file__, f"WRONG SRC: {_pm.__file__}"
from src.physics.layer2.corner_descriptors import descriptors_from_frame
from src.physics.layer2.property_mixture import MIN_COMPONENT_WEIGHT_FRAC, MixtureFit
from src.physics.layer2.mixture_stability import F12_AGREEMENT_THRESHOLD, component_agreement_stat

DB = "C:/Programs/f1Brainz/data/damage_integrals.db"
KMAX = 6
FLOOR = MIN_COMPONENT_WEIGHT_FRAC


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


def pool(dbc, cs):
    return np.concatenate([dbc[c] for c in cs], axis=0)


class HalfFit:
    """Fit k=1..KMAX once on full standardized data; cache LL/params/wmin for cheap selection."""
    def __init__(self, descriptors, random_state):
        d = np.asarray(descriptors, float)
        self.scaler = StandardScaler()
        self.X = self.scaler.fit_transform(d)
        self.N = self.X.shape[0]
        self.gmm, self.ll, self.nparams, self.wmin = {}, {}, {}, {}
        for k in range(1, KMAX + 1):
            g = GaussianMixture(n_components=k, random_state=random_state).fit(self.X)
            self.gmm[k] = g
            self.ll[k] = g.score(self.X) * self.N
            self.nparams[k] = g._n_parameters()
            self.wmin[k] = g.weights_.min()

    def _mf(self, k):
        return MixtureFit(gmm=self.gmm[k], k=k, scaler=self.scaler)

    def select_baseline(self, k_range=(2, KMAX)):
        cand = {k: -2 * self.ll[k] + self.nparams[k] * np.log(self.N)
                for k in range(k_range[0], k_range[1] + 1) if self.wmin[k] >= FLOOR}
        if not cand:
            return self._mf(1)
        return self._mf(min(cand, key=cand.get))

    def select_effn(self, cap, k_range=(2, KMAX)):
        n_eff = min(self.N, cap)
        cand = {k: -2 * self.ll[k] + self.nparams[k] * np.log(n_eff)
                for k in range(k_range[0], k_range[1] + 1) if self.wmin[k] >= FLOOR}
        if not cand:
            return self._mf(1)
        return self._mf(min(cand, key=cand.get))


def agree(fa, fb):
    return component_agreement_stat(fa, fb)


def report(label, rows):
    npass = sum(1 for r in rows if r[-1])
    print(f"\n=== {label} ===", flush=True)
    for i, ka, kb, stat, p in rows:
        s = "inf" if stat == float("inf") else f"{stat:.4f}"
        print(f"  split {i}: k_a={ka} k_b={kb} stat={s} {'PASS' if p else 'FAIL'}", flush=True)
    print(f"  n_pass = {npass}/5", flush=True)
    return npass


def main():
    print("Loading (READ-ONLY)...", flush=True)
    dbc = load()
    names = list(dbc.keys())
    print(f"{len(dbc)} circuits, {sum(v.shape[0] for v in dbc.values())} rows", flush=True)

    # Pre-fit both halves of all 5 splits ONCE.
    print("Fitting k=1..6 per half for all 5 splits (once each)...", flush=True)
    HF = {}
    for i, seed, ca, cb in splits(names):
        HF[i] = (seed, HalfFit(pool(dbc, ca), seed), HalfFit(pool(dbc, cb), seed), ca, cb)
        print(f"  split {i} fitted (N_a={HF[i][1].N}, N_b={HF[i][2].N})", flush=True)

    # ---- A. Baseline reproduction ----
    rows = []
    for i in range(5):
        _, fa, fb, *_ = HF[i]
        a, b = fa.select_baseline(), fb.select_baseline()
        st = agree(a, b); rows.append((i, a.k, b.k, st, st < F12_AGREEMENT_THRESHOLD))
    report("A. BASELINE (shipped BIC over full N)", rows)

    # ---- B. BIC-vs-k on split-0 half A (representative) ----
    _, fa0, _, _, _ = HF[0]
    print(f"\n=== B. BIC-vs-k, split0 halfA (N={fa0.N}) ===", flush=True)
    for k in range(1, KMAX + 1):
        bic = -2 * fa0.ll[k] + fa0.nparams[k] * np.log(fa0.N)
        pen = fa0.nparams[k] * np.log(fa0.N)
        dll = "" if k == 1 else f" dLL/pt={(fa0.ll[k]-fa0.ll[k-1])/fa0.N:+.5f}"
        fl = " <FLOOR>" if fa0.wmin[k] < FLOOR else ""
        print(f"  k={k}: BIC={bic:.0f} penalty={pen:.0f} LL/pt={fa0.ll[k]/fa0.N:.5f}{dll} wmin={fa0.wmin[k]:.3f}{fl}", flush=True)

    # ---- C. Descriptor density shape ----
    pooled = pool(dbc, names)
    print("\n=== C. Descriptor density shape (pooled) ===", flush=True)
    for nm, arr in (("radius_m", pooled[:, 0]), ("lateral_g", pooled[:, 1])):
        q = np.percentile(arr, [1, 10, 25, 50, 75, 90, 99])
        print(f"  {nm}: p1={q[0]:.2f} p10={q[1]:.2f} p25={q[2]:.2f} p50={q[3]:.2f} p75={q[4]:.2f} p90={q[5]:.2f} p99={q[6]:.2f}", flush=True)

    # ---- D. Fixed-k location stability ----
    for kfix in (2, 3, 4):
        rows = []
        for i in range(5):
            _, fa, fb, *_ = HF[i]
            a, b = fa._mf(kfix), fb._mf(kfix)
            st = agree(a, b); rows.append((i, a.k, b.k, st, st < F12_AGREEMENT_THRESHOLD))
        report(f"D. FIXED k={kfix} (locations only; not support-driven)", rows)

    # ---- E1. effective-N-capped BIC (derived from same fits) ----
    best_cap = None
    for cap in (300, 500, 1000, 2000, 5000, 10000):
        rows = []
        for i in range(5):
            _, fa, fb, *_ = HF[i]
            a, b = fa.select_effn(cap), fb.select_effn(cap)
            st = agree(a, b); rows.append((i, a.k, b.k, st, st < F12_AGREEMENT_THRESHOLD))
        np_ = report(f"E1. effective-N-capped BIC (n_eff_cap={cap})", rows)
        if np_ == 5 and best_cap is None:
            best_cap = cap

    # ---- E4. narrower k_range (derived) ----
    for kr in ((2, 3), (2, 4)):
        rows = []
        for i in range(5):
            _, fa, fb, *_ = HF[i]
            a, b = fa.select_baseline(kr), fb.select_baseline(kr)
            st = agree(a, b); rows.append((i, a.k, b.k, st, st < F12_AGREEMENT_THRESHOLD))
        report(f"E4. narrower k_range={kr} (BIC over full N)", rows)

    # ---- E2. subsample-budget selection (own light fits) ----
    from src.physics.layer2.property_mixture import fit_property_mixture
    for nsub in (2000, 5000, 10000):
        rows = []
        for i, seed, ca, cb in splits(names):
            da, db = pool(dbc, ca), pool(dbc, cb)
            rng = np.random.default_rng(seed)
            if da.shape[0] > nsub: da = da[rng.choice(da.shape[0], nsub, replace=False)]
            if db.shape[0] > nsub: db = db[rng.choice(db.shape[0], nsub, replace=False)]
            a = fit_property_mixture(da, random_state=seed); b = fit_property_mixture(db, random_state=seed)
            st = agree(a, b); rows.append((i, a.k, b.k, st, st < F12_AGREEMENT_THRESHOLD))
        report(f"E2. subsample-budget (n_sub={nsub})", rows)

    # ---- Report centroids for the chosen effN cap (physical adequacy) ----
    if best_cap:
        print(f"\n=== CENTROIDS (raw units) for effN cap={best_cap}, split0 ===", flush=True)
        _, fa, fb, ca, cb = HF[0]
        for tag, f in (("halfA", fa.select_effn(best_cap)), ("halfB", fb.select_effn(best_cap))):
            raw = f.scaler.inverse_transform(f.gmm.means_)
            order = np.argsort(raw[:, 0])
            cs = ", ".join(f"(r={raw[j,0]:.0f}m, lat={raw[j,1]:.2f}g)" for j in order)
            print(f"  {tag} k={f.k}: {cs}", flush=True)

    print(f"\nSUMMARY: first-passing effN cap = {best_cap}", flush=True)


if __name__ == "__main__":
    main()
