"""EXPERIMENT (#445): does a linear v term help the grip frontier? (additive, throwaway)

Model now:        G_c(v) = A + B_c * v^2                 (A shared/weekend, B per-car)
Experiment adds:  G_c(v) = A + C   * v + B_c * v^2       (C shared)
              or: G_c(v) = A + C_c * v + B_c * v^2       (C per-car)

Physics: pure downforce is v^2; a linear v is NOT downforce -- it would capture tyre
LOAD-SENSITIVITY (mu falls as load rises, bending the frontier below pure v^2) or flex
the effective exponent. Risk: over a corner's speed range v and v^2 are collinear, so C
and B trade off and B can get NOISIER. So we measure both fit gain AND whether B stays clean.

Metrics (all vs the no-v baseline):
  1. held-out PINBALL loss at tau (proper quantile score; penalises overfit)  -> lower better
  2. teammate B gap within a weekend (same car => pure noise proxy, NO wing confound) -> lower better
  3. condition number of the weighted normal matrix (collinearity diagnosis)  -> higher worse
  4. C sign/magnitude consistency across weekends (is it a real consistent term?)

Reads cached full-grid quali nodes (season_prior_nodes_full.npz). Additive, imports nothing mutable.
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
RNG = np.random.default_rng(7)


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


def _stack(clouds, keys):
    v = np.concatenate([clouds[k][0] for k in keys])
    g = np.concatenate([clouds[k][1] for k in keys])
    w = np.concatenate([clouds[k][2] for k in keys])
    kid = np.concatenate([np.full(len(clouds[k][0]), j) for j, k in enumerate(keys)])
    return v, g, w, kid


def build_design(v, kid, nk, vmode):
    """Columns: [A] [C_shared?] [B_c per car (v^2)] [C_c per car (v)?]. Returns X, idx dict."""
    n = len(v)
    cols = [np.ones(n)]
    idx = {"A": 0}
    j = 1
    if vmode == "shared":
        cols.append(v.copy()); idx["C"] = j; j += 1
    idx["B0"] = j
    for k in range(nk):
        c = np.zeros(n); m = kid == k; c[m] = v[m] ** 2
        cols.append(c); j += 1
    if vmode == "percar":
        idx["C0"] = j
        for k in range(nk):
            c = np.zeros(n); m = kid == k; c[m] = v[m]
            cols.append(c); j += 1
    return np.column_stack(cols), idx


def wls(X, y, w, ridge=1e-6):
    Xw = X * w[:, None]
    M = X.T @ Xw + ridge * np.eye(X.shape[1])
    return np.linalg.solve(M, Xw.T @ y), M


def fit(clouds, vmode=None, iters=30, tau=TAU, band=BAND):
    keys = list(clouds)
    nk = len(keys)
    v, g, w0, kid = _stack(clouds, keys)
    X, idx = build_design(v, kid, nk, vmode)
    p = X.shape[1]
    coef = np.zeros(p); coef[idx["A"]] = 1.6
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
        coef[idx["A"]] = np.clip(coef[idx["A"]], 0.8, 3.2)
        coef[idx["B0"]:idx["B0"] + nk] = np.clip(coef[idx["B0"]:idx["B0"] + nk], -2e-3, 8e-3)
    B = {keys[k]: float(coef[idx["B0"] + k]) for k in range(nk)}
    C = None
    if vmode == "shared":
        C = float(coef[idx["C"]])
    elif vmode == "percar":
        C = {keys[k]: float(coef[idx["C0"] + k]) for k in range(nk)}
    return dict(coef=coef, idx=idx, keys=keys, A=float(coef[idx["A"]]), B=B, C=C, cond=cond)


def pinball_heldout(clouds, vmode, tau=TAU, min_nodes=24):
    """Split each car's nodes train/test; fit on train, score quantile pinball on test."""
    train, test = {}, {}
    for c, (v, g, w) in clouds.items():
        if len(v) < min_nodes:
            continue
        perm = RNG.permutation(len(v)); h = len(v) // 2
        tr, te = perm[:h], perm[h:]
        train[c] = (v[tr], g[tr], w[tr])
        test[c] = (v[te], g[te], w[te])
    if len(train) < 3:
        return np.nan
    f = fit(train, vmode=vmode)
    keys = f["keys"]
    # build test design aligned to the SAME key order/columns
    tkeys = [k for k in keys if k in test]
    if not tkeys:
        return np.nan
    # remap test onto the trained column layout (per-car columns keyed by train index)
    losses = []
    for k in tkeys:
        v, g, w = test[k]
        ki = keys.index(k)
        A = f["A"]; B = f["B"][k]
        Gh = A + B * v * v
        if vmode == "shared":
            Gh = Gh + f["C"] * v
        elif vmode == "percar":
            Gh = Gh + f["C"][k] * v
        Gh = np.minimum(Gh, GSAT)
        m = g < GSAT - 0.2
        r = (g - Gh)[m]
        losses.append(np.where(r > 0, tau * r, (tau - 1) * r))
    if not losses:
        return np.nan
    return float(np.mean(np.concatenate(losses)))


def teammate_gap(fitres):
    keys = fitres["keys"]; B = fitres["B"]
    byteam = {}
    for k in keys:
        t = DRV2TEAM.get(k)
        if t:
            byteam.setdefault(t, []).append(B[k])
    gaps = [abs(vs[0] - vs[1]) for vs in byteam.values() if len(vs) == 2]
    return gaps


def main():
    per_round = load_full()
    print(f"{len(per_round)} weekends, "
          f"{len(set(c for _, cl in per_round for c in cl))} cars\n")

    modes = [None, "shared", "percar"]
    names = {None: "A+B v^2 (baseline)", "shared": "A + C v + B v^2 (C shared)",
             "percar": "A + C_c v + B v^2 (C per-car)"}
    agg = {m: dict(pin=[], gap=[], cond=[], Cs=[]) for m in modes}

    for rname, clouds in per_round:
        clouds = {c: cl for c, cl in clouds.items() if len(cl[0]) >= 12}
        if len(clouds) < 4:
            continue
        for m in modes:
            f = fit(clouds, vmode=m)
            agg[m]["gap"] += teammate_gap(f)
            agg[m]["cond"].append(f["cond"])
            p = pinball_heldout(clouds, vmode=m)
            if p == p:
                agg[m]["pin"].append(p)
            if m == "shared":
                agg[m]["Cs"].append(f["C"])

    print("=" * 78)
    print("RESULT  (lower pinball = better fit; lower gap = cleaner B; lower cond = ok)")
    print("=" * 78)
    print(f"{'model':>32} {'heldout_pinball':>16} {'teammate_B_gap':>16} {'cond#':>12}")
    for m in modes:
        pin = np.nanmean(agg[m]["pin"]) if agg[m]["pin"] else np.nan
        gap = np.mean(agg[m]["gap"]) * 1e3 if agg[m]["gap"] else np.nan
        cond = np.nanmean(agg[m]["cond"]) if agg[m]["cond"] else np.nan
        print(f"{names[m]:>32} {pin:>16.5f} {gap:>16.4f} {cond:>12.2e}")

    base_pin = np.nanmean(agg[None]["pin"])
    base_gap = np.mean(agg[None]["gap"]) * 1e3
    print("\nΔ vs baseline (negative = better):")
    for m in ("shared", "percar"):
        dp = np.nanmean(agg[m]["pin"]) - base_pin
        dg = np.mean(agg[m]["gap"]) * 1e3 - base_gap
        print(f"  {names[m]:>32}: Δpinball {dp:+.5f} ({dp/base_pin*100:+.1f}%)   "
              f"Δgap {dg:+.4f} ({dg/base_gap*100:+.1f}%)")

    Cs = np.array(agg["shared"]["Cs"])
    if len(Cs):
        same = np.mean(np.sign(Cs) == np.sign(np.median(Cs))) * 100
        print(f"\nShared C across {len(Cs)} weekends: mean {Cs.mean():+.4f}, "
              f"median {np.median(Cs):+.4f}, std {Cs.std():.4f}, "
              f"{same:.0f}% same sign as median")
        print("  (a real load-sensitivity term -> consistent sign + tighter held-out + lower/equal gap;")
        print("   noise stealing curvature -> inconsistent sign and/or WORSE teammate gap)")


if __name__ == "__main__":
    main()
