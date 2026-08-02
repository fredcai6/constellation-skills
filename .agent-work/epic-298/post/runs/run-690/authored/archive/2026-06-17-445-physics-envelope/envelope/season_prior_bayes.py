"""Race-to-race RECURSIVE BAYESIAN downforce prior — prior-IN-the-fit (#445).

Replaces season_prior_filter.py's fit-fresh-then-smooth (a Kalman on point estimates,
the WRONG architecture) with a true recursive update: carry each car's downforce
deviation posterior forward and use it as a PRIOR INSIDE next weekend's penalized IRLS
frontier fit, so thin tracks borrow strength AT FIT TIME (the fit can't run away) instead
of being shrunk after the fact.

Model (clean lateral-apex frontier, per weekend r):
    G_c(v) = A_r + B_c v^2,   B_c = L_r + delta_c
  - A_r : shared mechanical grip, environmental, FREE per weekend (no prior, re-fit).
  - L_r = b0 + beta*W_r : track wing level, EXOGENOUS (W_r = hardcoded track downforce-
    demand index, NOT fit from the field -> no field-composition coupling, the fix for
    the dropped L_r). b0, beta are ONE global pair estimated once.
  - delta_c : per-car downforce deviation = THE season-carried latent.

Per weekend: penalized IRLS minimises  frontier-data-term + sum_c tau_c (B_c - (L_r+mu_c))^2
  where (mu_c, 1/tau_c) is the carried prior on delta_c (widened by process noise q0, with
  an adaptive jump on large innovations). Posterior delta_c + variance come straight from
  the fit (mean + Laplace curvature). No post-hoc smoothing, no field-mean.

Reads CLEAN nodes (calibrated_aniso_nodes.npz). Monza test: build prior over rounds 1-13,
show the prior-informed Monza posterior beats the Monza-only fresh fit.
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

import aniso_fit  # noqa: E402
from aniso_fit import clouds_lat, DRV2TEAM  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
aniso_fit.CACHE = OUT / "calibrated_aniso_nodes.npz"   # CLEAN kinematics
GSAT = 5.2
VREF = 200.0 / 3.6

# Exogenous track downforce-demand index W_r in [0,1] (domain knowledge, NOT field-fit),
# indexed by 2023 round order 1..22. high=more wing.
W = [0.50, 0.30, 0.50, 0.20, 0.50, 1.00, 0.80, 0.45, 0.50, 0.60,
     0.95, 0.20, 0.85, 0.10, 0.95, 0.80, 0.65, 0.60, 0.50, 0.55, 0.15, 0.55]
MONZA_IDX = 13   # round 14 (Italian GP) zero-based


def load_lateral():
    """Ordered [(orig_round_idx, rname, {car:(v, alat, w)})] from clean nodes, pure-lateral
    apex. Carries the original round index so W_r stays aligned if a thin weekend drops."""
    per = aniso_fit.load()                      # 22 in round order
    out = []
    for idx, (rname, cl) in enumerate(per):
        lat = clouds_lat(cl)                    # {car:(v,alat,w)}, |along|/alat<THRESH
        if len(lat) >= 4:
            out.append((idx, rname, lat))
    return out


def penalized_fit(clouds, m=None, tau=None, q=0.92, band=0.4, iters=30):
    """Penalized quantile-IRLS frontier. m/tau: per-car prior center + precision (1/var)
    on B_c, in CALIBRATED B^-2 units. Returns A, {car:B}, {car: posterior var of B}.

    Weights normalised to mean 1 (so effective sample size ≈ node count, not the inflated
    circle-fit quality sum), and the Hessian scaled by the frontier residual variance σ̂²,
    so cov = σ̂²(XᵀWX)⁻¹ is a calibrated covariance — thin tracks read as genuinely uncertain.
    """
    keys = list(clouds); K = len(keys)
    v = np.concatenate([clouds[k][0] for k in keys])
    g = np.concatenate([clouds[k][1] for k in keys])
    w0 = np.concatenate([clouds[k][2] for k in keys])
    w0 = w0 / max(np.mean(w0), 1e-12)                  # honest effective N
    kid = np.concatenate([np.full(len(clouds[k][0]), j) for j, k in enumerate(keys)])
    A = 1.6; B = np.full(K, 0.0015); H = np.eye(1 + K)
    for _ in range(iters):
        Gv = np.minimum(A + B[kid] * v * v, GSAT)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, q, 1 - q)
        wt = w0 * member * qw
        sel = (g < GSAT - 0.2) & (wt > 1e-9)
        if sel.sum() < 2 * K + 4:
            break
        X = np.zeros((int(sel.sum()), 1 + K)); X[:, 0] = 1.0
        vs = v[sel]; ks = kid[sel]
        for j in range(K):
            X[ks == j, 1 + j] = vs[ks == j] ** 2
        ww = wt[sel]; rr = r[sel]
        sig2 = max(float((ww * rr * rr).sum() / ww.sum()), 1e-9)   # frontier scatter
        WX = X * ww[:, None]
        H = (X.T @ WX) / sig2
        rhs = (WX.T @ g[sel]) / sig2
        if tau:
            for j, c in enumerate(keys):
                tc = tau.get(c, 0.0)
                H[1 + j, 1 + j] += tc; rhs[1 + j] += tc * m.get(c, 0.0)
        H += 1e-9 * np.eye(1 + K)
        coef = np.linalg.solve(H, rhs)
        A = float(np.clip(coef[0], 0.8, 3.2))
        B = np.clip(coef[1:], -2e-3, 8e-3)
    cov = np.linalg.inv(H)
    pv = {keys[j]: float(max(cov[1 + j, 1 + j], 1e-15)) for j in range(K)}
    return A, {keys[j]: float(B[j]) for j in range(K)}, pv


def estimate_Lr(per_round):
    """Global b0, beta for L_r = b0 + beta*W_r, from fresh per-weekend mean B vs W
    (one global pair -> no per-car field coupling)."""
    Wr, Br = [], []
    for idx, rn, cl in per_round:
        _, B, _ = penalized_fit(cl)
        Wr.append(W[idx]); Br.append(np.mean(list(B.values())))
    Wr = np.array(Wr); Br = np.array(Br)
    beta = float(np.cov(Wr, Br)[0, 1] / np.var(Wr))
    b0 = float(Br.mean() - beta * Wr.mean())
    return b0, beta


def estimate_sig2_op(per, b0, beta):
    """Operating-point observation noise σ²_op: the between-race scatter of fresh δ that
    is NOT explained by within-weekend fit variance (track/setup/fuel/conditions). The
    within-weekend Laplace var under-states the season-relevant uncertainty ~50×; this is
    the floor the filter's obs noise must include. Median over cars (robust to upgraders)."""
    dser, allvw = {}, []
    for idx, rn, cl in per:
        _, B, pv = penalized_fit(cl); Lr = b0 + beta * W[idx]
        for c in B:
            dser.setdefault(c, []).append(B[c] - Lr); allvw.append(pv[c])
    resid = []
    for c in dser:
        if len(dser[c]) >= 8:
            a = np.array(dser[c]); resid += list(a - np.median(a))      # per-car de-meaned
    total = (1.4826 * np.median(np.abs(resid))) ** 2                    # robust per-race scatter var
    return float(max(total - np.median(allvw), 1e-12))


def run_filter(per_round, b0, beta, sig2_op, q0, jump_k=9.0, jump_mult=40.0):
    """Two-stage recursive Bayes (the correctly-calibrated update). Per weekend: fresh
    shared-A frontier fit -> weekend estimate y=B̂−L_r with within-weekend var v_w; Kalman
    update the season state with obs noise R = v_w + σ²_op. Thin tracks have large v_w ->
    large R -> small gain -> self-down-weight (borrow strength). Adaptive jump inflates the
    process step only when the innovation exceeds the operating-point noise (a real upgrade);
    jump_mult=1 disables it. state[car]=(mu, P). Returns per-weekend recs."""
    state = {}; recs = []
    for idx, rn, cl in per_round:
        Lr = b0 + beta * W[idx]
        A, B, vw = penalized_fit(cl)                  # data-only weekend estimate
        rec = {}
        for c in cl:
            y = B[c] - Lr; R = vw[c] + sig2_op
            if c in state:
                mu, P = state[c]; Ppred = P + q0
                innov = y - mu
                z2 = innov * innov / (Ppred + R)
                jumped = z2 > jump_k
                if jumped:
                    Ppred = P + q0 * jump_mult
                K = Ppred / (Ppred + R)
                mu, P = mu + K * innov, (1.0 - K) * Ppred
                state[c] = (mu, P)
            else:
                mu, P = y, R; state[c] = (mu, P); jumped = False; z2 = float("nan")
            rec[c] = dict(delta=mu, fresh=y, var=P, R=R, jump=jumped, z2=z2)
        recs.append((idx, rn, rec, A))
    return recs, state


def teammate_gaps(dvals):
    bt = {}
    for c, x in dvals.items():
        t = DRV2TEAM.get(c)
        if t:
            bt.setdefault(t, []).append(x)
    return [abs(v[0] - v[1]) for v in bt.values() if len(v) == 2]


def season_truth_delta(per_round, b0, beta):
    acc = {}
    for idx, rn, cl in per_round:
        _, B, _ = penalized_fit(cl)
        Lr = b0 + beta * W[idx]
        for c in B:
            acc.setdefault(c, []).append(B[c] - Lr)
    return {c: float(np.mean(v)) for c, v in acc.items()}


def spear(a, b):
    if len(a) < 3:
        return np.nan
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def full_baseline(per, b0, beta, sig2_op, q0):
    """Run the recursive Bayes filter over the WHOLE season -> clean per-car downforce
    descriptor; fuse with the drag channel for the efficiency fingerprint."""
    import json
    recs, state = run_filter(per, b0, beta, sig2_op, q0)
    final = {c: state[c][0] for c in state}            # end-of-season filtered δ
    truth = season_truth_delta(per, b0, beta)          # unweighted season-avg δ

    def tmean(dv):
        bt = {}
        for c, x in dv.items():
            t = DRV2TEAM.get(c)
            if t:
                bt.setdefault(t, []).append(x)
        return {t: float(np.mean(v)) for t, v in bt.items()}
    dff, dft = tmean(final), tmean(truth)
    teams = sorted(dft)

    print("\n" + "=" * 74)
    print("FULL-SEASON BASELINE — downforce-deviation descriptor (clean kinematics)")
    print("=" * 74)
    print("  descriptor = season-average δ (character); δ_final shown as drift diagnostic")
    print(f"  {'team':>5} {'δ_seasonavg ×1e3':>17} {'δ_final ×1e3':>13}")
    for t in sorted(teams, key=lambda k: -dft[k]):
        print(f"  {t:>5} {dft[t]*1e3:>17.3f} {dff.get(t, float('nan'))*1e3:>13.3f}")

    DRAG = OUT / "drag_fingerprint10_fits.json"
    if not DRAG.exists():
        print("\n  (drag cache absent — downforce-only baseline)"); return final, truth
    dfits = {int(k): v for k, v in json.loads(DRAG.read_text()).items()}
    dr = sorted(dfits)
    fieldC = {i: np.mean([dfits[rd][t]["CdA_c"] for t in dfits[rd]]) for i, rd in enumerate(dr)}
    drag = {}
    for t in teams:
        vals = [dfits[rd][t]["CdA_c"] - fieldC[i] for i, rd in enumerate(dr) if t in dfits[rd]]
        if len(vals) >= 6:
            drag[t] = float(np.mean(vals))
    common = [t for t in teams if t in drag]
    dfa = np.array([dft[t] for t in common]); dga = np.array([drag[t] for t in common])
    dz = {t: (dft[t] - dfa.mean()) / dfa.std() for t in common}
    gz = {t: (drag[t] - dga.mean()) / dga.std() for t in common}
    print("\n  EFFICIENCY FINGERPRINT (z-scored): DF↑ = more downforce, drag↓ = slippery")
    print(f"  {'team':>5} {'DF_z':>7} {'drag_z':>7} {'eff':>7}  quadrant")
    for t in sorted(common, key=lambda k: -(dz[k] - gz[k])):
        eff = dz[t] - gz[t]
        quad = ("efficient" if dz[t] >= 0 and gz[t] < 0 else
                "draggy-grippy" if dz[t] >= 0 else
                "slippery-minnow" if gz[t] < 0 else "draggy-no-DF")
        print(f"  {t:>5} {dz[t]:+7.2f} {gz[t]:+7.2f} {eff:+7.2f}  {quad}")
    print("\n  (OLD contaminated fingerprint put RBR in the WRONG/low-DF quadrant; clean baseline)")
    return final, truth


def main():
    per = load_lateral()
    mz = next(e for e in per if e[0] == MONZA_IDX)
    print(f"{len(per)} weekends (clean lateral-apex nodes), Monza = '{mz[1]}'\n")
    b0, beta = estimate_Lr(per)
    print(f"exogenous L_r = {b0:.5f} + {beta:.5f}*W_r  (B units)")

    # estimate operating-point obs noise σ²_op (the calibration fix) + process noise q0
    sig2_op = estimate_sig2_op(per, b0, beta)
    q0 = sig2_op * 0.1
    fv = []
    for idx, rn, cl in per:
        _, _, pv = penalized_fit(cl); fv += list(pv.values())
    print(f"within-weekend var(B) median {np.median(fv):.3e}  vs  σ²_op {sig2_op:.3e}  "
          f"({sig2_op/np.median(fv):.0f}× larger — the miscalibration)  ->  q0 = {q0:.3e}\n")

    # build season state across rounds before Monza, then Monza posterior vs fresh
    pre = [e for e in per if e[0] < MONZA_IDX]
    recs, state = run_filter(pre, b0, beta, sig2_op, q0)
    _, mz_name, mz_cloud = mz
    Lr_mz = b0 + beta * W[MONZA_IDX]

    A_f, B_f, vw_f = penalized_fit(mz_cloud)          # fresh Monza weekend fit
    dprior, var_prior, dfresh, var_fresh = {}, {}, {}, {}
    for c in mz_cloud:
        y = B_f[c] - Lr_mz; R = vw_f[c] + sig2_op
        dfresh[c] = y; var_fresh[c] = R
        if c in state:
            mu, P = state[c]; Ppred = P + q0; K = Ppred / (Ppred + R)
            dprior[c] = mu + K * (y - mu); var_prior[c] = (1.0 - K) * Ppred
    truth = season_truth_delta(per, b0, beta)

    print("=" * 74)
    print("MONZA borrow-strength: prior posterior vs Monza-only fresh (calibrated R = v_w+σ²_op)")
    print("=" * 74)
    var_p = np.mean([var_prior[c] for c in dprior]); var_f = np.mean([var_fresh[c] for c in dprior])
    print(f"  mean var(δ):  prior {var_p:.3e}   fresh {var_f:.3e}   ({(1-var_p/var_f)*100:.0f}% tighter)")
    gp = teammate_gaps(dprior); gf = teammate_gaps({c: dfresh[c] for c in dprior})
    print(f"  teammate |Δδ| (×1e3):   prior {np.mean(gp)*1e3:.3f}   fresh {np.mean(gf)*1e3:.3f}   "
          f"({(1-np.mean(gp)/np.mean(gf))*100:.0f}% more consistent)")
    com = [c for c in dprior if c in truth]
    rp = spear(np.array([dprior[c] for c in com]), np.array([truth[c] for c in com]))
    rf = spear(np.array([dfresh[c] for c in com]), np.array([truth[c] for c in com]))
    print(f"  rank-corr vs season truth: prior {rp:+.3f}   fresh {rf:+.3f}")

    # constructor ordering at Monza (prior) vs truth
    def team_mean(dv):
        bt = {}
        for c, x in dv.items():
            t = DRV2TEAM.get(c)
            if t:
                bt.setdefault(t, []).append(x)
        return {t: float(np.mean(v)) for t, v in bt.items()}
    tp = team_mean(dprior); tt = team_mean(truth)
    print("\n  per-constructor Monza downforce deviation δ (prior) vs season truth:")
    print(f"  {'team':>5} {'δ_prior':>9} {'δ_truth':>9}")
    for t in sorted(tt, key=lambda k: -tt[k]):
        pp = f"{tp[t]:+.4f}" if t in tp else "   --"
        print(f"  {t:>5} {pp:>9} {tt[t]:+9.4f}")

    full_baseline(per, b0, beta, sig2_op, q0)


if __name__ == "__main__":
    main()
