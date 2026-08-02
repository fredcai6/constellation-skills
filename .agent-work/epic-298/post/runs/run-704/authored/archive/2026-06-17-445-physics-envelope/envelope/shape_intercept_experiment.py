"""EXPERIMENT (#445): is the INTERCEPT a car axis too? (per-car A_c vs shared A)

Today only B (downforce, v^2) is a car axis; A (mechanical grip) is shared/weekend.
But if cars also differ in mechanical grip, forcing all car-difference into B BIASES B.
Free the intercept per car:        G_c(v) = A_c + B_c * v^2
vs baseline shared intercept:      G_c(v) = A   + B_c * v^2

Prior result (grip_iter, per-track indep fits): per-car A spread 0.5-0.9g looked like
pure noise. Re-test in the clean full-season frame, with the proper diagnostics:
  - held-out PINBALL at tau (MATCHED split: both models scored on the same test half)
  - teammate gap on A_c and on B (same car => noise proxy, no wing confound)
  - condition number (does intercept/slope collinearity blow up like v did?)
Even if A_c is noisy, the question is whether freeing it CLEANS B or just absorbs noise.
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

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NODES = OUT / "season_prior_nodes_full.npz"
GSAT = 5.2
TAU = 0.92
BAND = 0.4
DRV2TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER",
            "SAI": "FER", "NOR": "MCL", "PIA": "MCL", "ALO": "AMR", "STR": "AMR",
            "GAS": "ALP", "OCO": "ALP", "ALB": "WIL", "SAR": "WIL", "TSU": "ATR",
            "DEV": "ATR", "RIC": "ATR", "LAW": "ATR", "BOT": "ALF", "ZHO": "ALF",
            "MAG": "HAA", "HUL": "HAA"}
RNG = np.random.default_rng(11)


def load_full():
    d = np.load(NODES, allow_pickle=True)
    rounds = [str(x) for x in d["rounds"]]
    cars = [str(x) for x in d["cars"]]
    out = []
    for r in rounds:
        cl = {}
        for c in cars:
            k = f"v__{r}__{c}"
            if k in d.files:
                cl[c] = (d[f"v__{r}__{c}"].astype(float),
                         d[f"g__{r}__{c}"].astype(float),
                         d[f"w__{r}__{c}"].astype(float))
        if cl:
            out.append((r, cl))
    return out


def _stack(clouds, keys):
    v = np.concatenate([clouds[k][0] for k in keys])
    g = np.concatenate([clouds[k][1] for k in keys])
    w = np.concatenate([clouds[k][2] for k in keys])
    kid = np.concatenate([np.full(len(clouds[k][0]), j) for j, k in enumerate(keys)])
    return v, g, w, kid


def build(v, kid, nk, intercept):
    n = len(v); cols = []; idx = {}
    if intercept == "shared":
        cols.append(np.ones(n)); idx["A"] = 0; b0 = 1
    else:  # free per-car intercept
        for k in range(nk):
            c = np.zeros(n); c[kid == k] = 1.0; cols.append(c)
        idx["A0"] = 0; b0 = nk
    idx["B0"] = b0
    for k in range(nk):
        c = np.zeros(n); m = kid == k; c[m] = v[m] ** 2; cols.append(c)
    return np.column_stack(cols), idx


def wls(X, y, w, ridge=1e-6):
    Xw = X * w[:, None]
    M = X.T @ Xw + ridge * np.eye(X.shape[1])
    return np.linalg.solve(M, Xw.T @ y), M


def fit(clouds, intercept, iters=30, tau=TAU, band=BAND):
    keys = list(clouds); nk = len(keys)
    v, g, w0, kid = _stack(clouds, keys)
    X, idx = build(v, kid, nk, intercept)
    p = X.shape[1]; coef = np.zeros(p)
    if intercept == "shared":
        coef[idx["A"]] = 1.6
    else:
        coef[idx["A0"]:idx["A0"] + nk] = 1.6
    coef[idx["B0"]:idx["B0"] + nk] = 0.0015
    cond = np.nan
    for _ in range(iters):
        Gv = np.minimum(X @ coef, GSAT)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        sel = (g < GSAT - 0.2) & (w > 1e-9)
        if sel.sum() < p + 4:
            break
        coef, M = wls(X[sel], g[sel], w[sel])
        cond = float(np.linalg.cond(M))
        if intercept == "shared":
            coef[idx["A"]] = np.clip(coef[idx["A"]], 0.8, 3.2)
        else:
            coef[idx["A0"]:idx["A0"] + nk] = np.clip(coef[idx["A0"]:idx["A0"] + nk], 0.8, 3.2)
        coef[idx["B0"]:idx["B0"] + nk] = np.clip(coef[idx["B0"]:idx["B0"] + nk], -2e-3, 8e-3)
    A = float(coef[idx["A"]]) if intercept == "shared" else \
        {keys[k]: float(coef[idx["A0"] + k]) for k in range(nk)}
    B = {keys[k]: float(coef[idx["B0"] + k]) for k in range(nk)}
    return dict(A=A, B=B, keys=keys, cond=cond, intercept=intercept)


def pinball(f, test, tau=TAU):
    losses = []
    for k in f["keys"]:
        if k not in test:
            continue
        v, g, w = test[k]
        A = f["A"] if f["intercept"] == "shared" else f["A"][k]
        Gh = np.minimum(A + f["B"][k] * v * v, GSAT)
        m = g < GSAT - 0.2
        r = (g - Gh)[m]
        if r.size:
            losses.append(np.where(r > 0, tau * r, (tau - 1) * r))
    return float(np.mean(np.concatenate(losses))) if losses else np.nan


def gaps(valdict):
    byteam = {}
    for k, val in valdict.items():
        t = DRV2TEAM.get(k)
        if t:
            byteam.setdefault(t, []).append(val)
    return [abs(vs[0] - vs[1]) for vs in byteam.values() if len(vs) == 2]


def main():
    per_round = load_full()
    modes = ["shared", "free"]
    name = {"shared": "A + B v^2  (shared intercept)", "free": "A_c + B_c v^2 (per-car intercept)"}
    agg = {m: dict(pin=[], bgap=[], cond=[]) for m in modes}
    agap_free = []
    for rname, clouds in per_round:
        clouds = {c: cl for c, cl in clouds.items() if len(cl[0]) >= 24}
        if len(clouds) < 4:
            continue
        # ONE matched split for both models
        train, test = {}, {}
        for c, (v, g, w) in clouds.items():
            perm = RNG.permutation(len(v)); h = len(v) // 2
            train[c] = (v[perm[:h]], g[perm[:h]], w[perm[:h]])
            test[c] = (v[perm[h:]], g[perm[h:]], w[perm[h:]])
        for m in modes:
            ffull = fit(clouds, m)              # full-data fit for teammate gaps
            ftr = fit(train, m)                 # train fit for held-out pinball
            agg[m]["bgap"] += gaps(ffull["B"])
            agg[m]["cond"].append(ffull["cond"])
            p = pinball(ftr, test)
            if p == p:
                agg[m]["pin"].append(p)
            if m == "free":
                agap_free += gaps(ffull["A"])

    print("=" * 80)
    print("RESULT (lower pinball=better fit; lower B-gap=cleaner downforce; cond# collinearity)")
    print("=" * 80)
    print(f"{'model':>36} {'heldout_pinball':>16} {'teammate_B_gap':>16} {'cond#':>11}")
    for m in modes:
        print(f"{name[m]:>36} {np.nanmean(agg[m]['pin']):>16.5f} "
              f"{np.mean(agg[m]['bgap'])*1e3:>16.4f} {np.nanmean(agg[m]['cond']):>11.2e}")
    dp = np.nanmean(agg['free']['pin']) - np.nanmean(agg['shared']['pin'])
    dg = (np.mean(agg['free']['bgap']) - np.mean(agg['shared']['bgap'])) * 1e3
    print(f"\nΔ free vs shared:  pinball {dp:+.5f} ({dp/np.nanmean(agg['shared']['pin'])*100:+.1f}%)"
          f"   B-gap {dg:+.4f} ({dg/(np.mean(agg['shared']['bgap'])*1e3)*100:+.1f}%)")
    print(f"\nper-car intercept A_c teammate gap: {np.mean(agap_free):.4f} g "
          f"(>~0.3g => A_c is noise/line, not a car property)")
    print("  VERDICT: free A_c helps only if pinball improves AND B-gap doesn't worsen AND")
    print("  A_c teammate gap is small. Otherwise mechanical grip isn't a separable car axis here.")


if __name__ == "__main__":
    main()
