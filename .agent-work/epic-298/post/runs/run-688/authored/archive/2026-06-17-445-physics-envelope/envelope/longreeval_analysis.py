"""Longitudinal (braking) re-evaluation on the CLEAN calibrated caches (#445).

Scrutinizes the aniso_long_fit approach end to end. Additive, namespaced longreeval_*.
Reads ONLY the clean calibrated caches; the lateral frontier comes from
calibrated_aniso_nodes via aniso_fit (CACHE overridden), braking from
calibrated_braking_nodes.

Produces the numbers cited in LONGITUDINAL_REEVAL_FINDINGS.md. Run from repo root:
    py .agent-work/445/envelope/longreeval_analysis.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ENV = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
sys.path.insert(0, str(ENV))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import aniso_fit  # noqa: E402
from season_prior_filter import fit_weekend, VREF, GSAT  # noqa: E402

aniso_fit.CACHE = ENV / "calibrated_aniso_nodes.npz"
from aniso_fit import clouds_lat, DRV2TEAM  # noqa: E402

BRK = ENV / "calibrated_braking_nodes.npz"
DRAG = ENV / "drag_fingerprint10_fits.json"
RNG = np.random.default_rng(445)


def load_braking():
    d = np.load(BRK, allow_pickle=True)
    rounds = [str(x) for x in d["rounds"]]
    cars = [str(x) for x in d["cars"]]
    out = {}
    for r in rounds:
        cl = {}
        for c in cars:
            k = f"v__{r}__{c}"
            if k in d.files:
                cl[c] = (d[f"v__{r}__{c}"].astype(float),
                         d[f"alat__{r}__{c}"].astype(float),
                         d[f"d__{r}__{c}"].astype(float),
                         d[f"w__{r}__{c}"].astype(float))
        if cl:
            out[r] = cl
    return out


def spear(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if len(a) < 3:
        return np.nan
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def teammate_gaps(B):
    bt = {}
    for k, val in B.items():
        t = DRV2TEAM.get(k)
        if t:
            bt.setdefault(t, []).append(val)
    return [abs(v[0] - v[1]) for v in bt.values() if len(v) == 2]


def fit_long_simple(clouds_g):
    """Fit a_brake(v) = A + B v^2 by ordinary least squares per car, shared A.

    clouds_g: car -> (v, decel_or_eq, w).  Returns (A, {car:B}).  Plain WLS on the
    cloud (NOT a quantile frontier) — for the censored vs un-censored comparison we
    want the same estimator on both so any shift is the truncation, not the fitter.
    """
    keys = list(clouds_g)
    v = np.concatenate([clouds_g[k][0] for k in keys])
    g = np.concatenate([clouds_g[k][1] for k in keys])
    w = np.concatenate([clouds_g[k][2] for k in keys])
    kid = np.concatenate([np.full(len(clouds_g[k][0]), j) for j, k in enumerate(keys)])
    X = np.zeros((len(v), 1 + len(keys)))
    X[:, 0] = 1.0
    for j in range(len(keys)):
        X[kid == j, 1 + j] = v[kid == j] ** 2
    Xw = X * w[:, None]
    M = X.T @ Xw + 1e-9 * np.eye(X.shape[1])
    coef = np.linalg.solve(M, Xw.T @ (g * w))
    return float(coef[0]), {keys[j]: float(coef[1 + j]) for j in range(len(keys))}


def quantile_long(clouds_g, tau=0.90, band=0.4, iters=25):
    """Upper-quantile (frontier) fit, mirrors fit_weekend but NO GSAT clip on the
    longitudinal arm (braking decel never reaches GSAT in this data; clipping would
    only mask the truncation we are studying)."""
    keys = list(clouds_g)
    v = np.concatenate([clouds_g[k][0] for k in keys])
    g = np.concatenate([clouds_g[k][1] for k in keys])
    w0 = np.concatenate([clouds_g[k][2] for k in keys])
    kid = np.concatenate([np.full(len(clouds_g[k][0]), j) for j, k in enumerate(keys)])
    A = 1.2
    B = np.full(len(keys), 3e-4)
    for _ in range(iters):
        Gv = A + B[kid] * v * v
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        sel = w > 1e-9
        if sel.sum() < 2 * len(keys) + 4:
            break
        X = np.zeros((int(sel.sum()), 1 + len(keys)))
        X[:, 0] = 1.0
        vs = v[sel]
        ks = kid[sel]
        for j in range(len(keys)):
            X[ks == j, 1 + j] = vs[ks == j] ** 2
        Xw = X * w[sel][:, None]
        M = X.T @ Xw + 1e-9 * np.eye(X.shape[1])
        coef = np.linalg.solve(M, Xw.T @ (g[sel] * w[sel]))
        A = float(np.clip(coef[0], 0.4, 2.5))
        B = np.clip(coef[1:], 1e-5, 4e-3)
    return A, {keys[j]: float(B[j]) for j in range(len(keys))}


# ----------------------------------------------------------------------
def run():
    per = dict(aniso_fit.load())
    brk = load_braking()
    rep = {}

    # ===== 1. ELLIPSE PROJECTION HEALTH ===============================
    print("=" * 78)
    print("1. ELLIPSE-PROJECTION HEALTH (clean caches)")
    print("=" * 78)
    ratios = []
    alat_brk = []
    clip_gsat = []
    clip097 = []
    lat_supp_hi = []   # fraction of braking speed ABOVE the lateral fit's p95 support
    for rname, latcl_all in per.items():
        if rname not in brk:
            continue
        clat = clouds_lat(latcl_all)
        clat = {c: v for c, v in clat.items() if len(v[0]) >= 18}
        if len(clat) < 4:
            continue
        A, Bl = fit_weekend(clat)
        lat_v = np.concatenate([clat[c][0] for c in clat])
        v95 = np.percentile(lat_v, 95)
        for c, (v, alat, decel, w) in brk[rname].items():
            if c not in Bl:
                continue
            graw = A + Bl[c] * v * v
            glat = np.minimum(graw, GSAT)
            ratio = alat / glat
            ratios.extend(ratio.tolist())
            alat_brk.extend(alat.tolist())
            clip_gsat.append(np.mean(graw > GSAT))
            clip097.append(np.mean(ratio >= 0.97))
            lat_supp_hi.append(np.mean(v > v95))
    rr = np.array(ratios)
    ab = np.array(alat_brk)
    rep["frac_ratio_gt1"] = float(np.mean(rr > 1.0))
    rep["frac_ratio_clip097"] = float(np.mean(clip097))
    rep["frac_glat_clip_gsat"] = float(np.mean(clip_gsat))
    rep["frac_alat_impossible"] = float(np.mean(ab > 5.2))
    rep["frac_brake_above_lat_support"] = float(np.mean(lat_supp_hi))
    print(f"  braking pts with alat/G_lat > 1  (outside ellipse):  {100*rep['frac_ratio_gt1']:.1f}%")
    print(f"  braking pts clipped at ratio 0.97 (singular proj):   {100*rep['frac_ratio_clip097']:.1f}%")
    print(f"  braking pts where G_lat hit GSAT ceiling:            {100*rep['frac_glat_clip_gsat']:.1f}%")
    print(f"  braking pts with alat > 5.2 g (impossible, noise):   {100*rep['frac_alat_impossible']:.1f}%")
    print(f"  braking speed ABOVE lateral-fit p95 support:         {100*rep['frac_brake_above_lat_support']:.1f}%")
    print(f"  ratio alat/G_lat: p50={np.percentile(rr,50):.2f} p90={np.percentile(rr,90):.2f} "
          f"p99={np.percentile(rr,99):.2f}")

    # ===== 2. CENSORING / TRUNCATION BIAS ON B_long ===================
    print("\n" + "=" * 78)
    print("2. SENSOR-CAP CENSORING BIAS ON B_long  (pure-decel frontier, NO ellipse)")
    print("=" * 78)
    # Use NEAR-STRAIGHT braking only (alat<0.6 g) so the ellipse projection is ~identity
    # and we isolate the truncation. Fit B_long on (a) all speeds vs (b) only v<200 km/h
    # (the sub-200 regime is less Nyquist-truncated: lower v -> dv/dt resolved better).
    seasonB_all = {}
    seasonB_lo = {}
    cap_by_v = {}
    for rname in brk:
        clo_all = {}
        clo_lo = {}
        for c, (v, alat, decel, w) in brk[rname].items():
            straight = alat < 0.6
            if straight.sum() < 25:
                continue
            vs, ds, ws = v[straight], decel[straight], w[straight]
            clo_all[c] = (vs, ds, ws)
            lo = vs * 3.6 < 200
            if lo.sum() >= 15:
                clo_lo[c] = (vs[lo], ds[lo], ws[lo])
        if len(clo_all) < 4:
            continue
        _, Ba = quantile_long(clo_all)
        common_lo = {c: clo_lo[c] for c in clo_lo if c in clo_all}
        Bl = quantile_long(common_lo)[1] if len(common_lo) >= 4 else {}
        for c in Ba:
            seasonB_all.setdefault(c, []).append(Ba[c])
            if c in Bl:
                seasonB_lo.setdefault(c, []).append(Bl[c])
    # frontier decel at vref under each
    car_all = {c: np.mean(seasonB_all[c]) * VREF * VREF for c in seasonB_all if len(seasonB_all[c]) >= 6}
    car_lo = {c: np.mean(seasonB_lo[c]) * VREF * VREF for c in seasonB_lo if len(seasonB_lo[c]) >= 6}
    common = [c for c in car_all if c in car_lo]
    if common:
        da = np.array([car_all[c] for c in common])
        dl = np.array([car_lo[c] for c in common])
        rep["censor_B_all_mean"] = float(np.mean(da))
        rep["censor_B_lo_mean"] = float(np.mean(dl))
        rep["censor_rank_spear"] = spear(da, dl)
        print(f"  cars with both fits: {len(common)}")
        print(f"  mean B_long*vref^2 (all speeds):   {np.mean(da):.3f} g")
        print(f"  mean B_long*vref^2 (v<200 only):   {np.mean(dl):.3f} g")
        print(f"  -> truncation SUPPRESSES the v^2 slope by {100*(1-np.mean(da)/max(np.mean(dl),1e-9)):.0f}% "
              f"at high speed (flattening)")
        print(f"  rank Spearman(all, lo) across cars = {rep['censor_rank_spear']:+.3f} "
              f"(does the car ORDER survive truncation?)")

    # decel ceiling vs speed (is the cap speed-dependent?)
    allv = []
    alld = []
    for rname in brk:
        for c, (v, alat, decel, w) in brk[rname].items():
            allv.extend(v.tolist())
            alld.extend(decel.tolist())
    allv = np.array(allv)
    alld = np.array(alld)
    print("\n  decel p98 ceiling by speed band (g):")
    for lo, hi in [(80, 150), (150, 200), (200, 250), (250, 330)]:
        m = (allv * 3.6 >= lo) & (allv * 3.6 < hi)
        if m.sum() > 50:
            rep[f"cap_p98_{lo}_{hi}"] = float(np.percentile(alld[m], 98))
            print(f"    {lo:>3}-{hi:<3} km/h: n={m.sum():>6}  p98={np.percentile(alld[m],98):.2f}  "
                  f"p99.5={np.percentile(alld[m],99.5):.2f}  max={alld[m].max():.2f}")

    # ===== 3. DRAG DECOMPOSITION (CORRECTED) ==========================
    print("\n" + "=" * 78)
    print("3. DRAG DECOMPOSITION: B_long vs B_lat vs independent CdA")
    print("=" * 78)
    # Project braking to long-equivalent (the production recipe) AND a robust variant
    # that DROPS the high-trail (ratio>0.8) and impossible-alat points.
    seasonLong, seasonLongRob, seasonLat = {}, {}, {}
    for rname, latcl_all in per.items():
        if rname not in brk:
            continue
        clat = clouds_lat(latcl_all)
        clat = {c: v for c, v in clat.items() if len(v[0]) >= 18}
        if len(clat) < 4:
            continue
        A, Bl = fit_weekend(clat)
        clong, clongR = {}, {}
        for c, (v, alat, decel, w) in brk[rname].items():
            if c not in Bl or len(v) < 25:
                continue
            glat = np.minimum(A + Bl[c] * v * v, GSAT)
            ratio = np.clip(alat / glat, 0.0, 0.97)
            along_eq = decel / np.sqrt(1.0 - ratio * ratio)
            ok = np.isfinite(along_eq) & (along_eq < 8.0)
            if ok.sum() >= 25:
                clong[c] = (v[ok], along_eq[ok], w[ok])
            # robust: near-straight only (alat<0.6) so projection ~ identity; no extrapolation reliance
            rb = (alat < 0.6) & np.isfinite(decel) & (decel < 8.0)
            if rb.sum() >= 20:
                clongR[c] = (v[rb], decel[rb], w[rb])
        if len(clong) >= 4:
            _, Bg = quantile_long(clong)
            for c in clong:
                seasonLong.setdefault(c, []).append(Bg[c] * VREF * VREF)
                if c in Bl:
                    seasonLat.setdefault(c, []).append(Bl[c] * VREF * VREF)
        if len(clongR) >= 4:
            _, BgR = quantile_long(clongR)
            for c in clongR:
                seasonLongRob.setdefault(c, []).append(BgR[c] * VREF * VREF)

    def to_team(season):
        cars = [c for c in season if len(season[c]) >= 6]
        teams = sorted({DRV2TEAM[c] for c in cars if c in DRV2TEAM})
        return {t: float(np.mean([np.mean(season[c]) for c in cars if DRV2TEAM.get(c) == t]))
                for t in teams}

    longT = to_team(seasonLong)
    longRT = to_team(seasonLongRob)
    latT = to_team(seasonLat)
    teams = [t for t in longT if t in latT]
    xl = np.array([longT[t] for t in teams])
    xa = np.array([latT[t] for t in teams])
    rep["corr_Blong_Blat"] = float(np.corrcoef(xl, xa)[0, 1])
    rep["spear_Blong_Blat"] = spear(xl, xa)
    print(f"  teams: {teams}")
    print(f"  corr(B_long[ellipse], B_lat)       = {rep['corr_Blong_Blat']:+.3f}  "
          f"Spearman {rep['spear_Blong_Blat']:+.3f}")
    teamsR = [t for t in longRT if t in latT]
    if len(teamsR) >= 4:
        xlr = np.array([longRT[t] for t in teamsR])
        xar = np.array([latT[t] for t in teamsR])
        rep["corr_BlongRob_Blat"] = float(np.corrcoef(xlr, xar)[0, 1])
        print(f"  corr(B_long[straight-only], B_lat) = {rep['corr_BlongRob_Blat']:+.3f}  "
              f"(no extrapolated-ellipse reliance)")

    # Drag cross-check with CORRECTED decomposition.
    # Model: a_brake = mu_x g + (mu_x * k_DF + k_drag) v^2 / m,  a_lat = mu_y g + mu_y k_DF v^2/m
    #   => B_long ~ mu_x*k_DF + k_drag ;  B_lat ~ mu_y*k_DF.
    # The naive proxy B_long - B_lat assumes mu_x==mu_y (false) AND same k_DF mapping.
    # Correct isolation of DRAG needs B_long - (mu_x/mu_y) B_lat. We estimate the ratio
    # mu_x/mu_y empirically from the median grip in each axis at matched speed, then test
    # whether the de-DF'd residual recovers the independent CdA order.
    if DRAG.exists():
        dfits = {int(k): v for k, v in json.loads(DRAG.read_text()).items()}
        dr = sorted(dfits)
        fieldCdA = {i: np.mean([dfits[rd][t]["CdA_c"] for t in dfits[rd]]) for i, rd in enumerate(dr)}
        dragoff = {}
        for t in teams:
            vals = [dfits[rd][t]["CdA_c"] - fieldCdA[i] for i, rd in enumerate(dr) if t in dfits[rd]]
            if len(vals) >= 6:
                dragoff[t] = float(np.mean(vals))
        common_t = [t for t in teams if t in dragoff]
        fl = np.mean([longT[t] for t in teams])
        fa = np.mean([latT[t] for t in teams])
        # naive residual
        resid_naive = {t: (longT[t] - fl) - (latT[t] - fa) for t in teams}
        # scaled residual with several plausible mu_x/mu_y ratios
        print("\n  drag cross-check (independent CdA offset vs braking residual):")
        if len(common_t) >= 4:
            dd = np.array([dragoff[t] for t in common_t])
            for kappa in [1.0, 0.85, 0.7]:
                resid_k = {t: (longT[t] - fl) - kappa * (latT[t] - fa) for t in common_t}
                rk = np.array([resid_k[t] for t in common_t])
                cc = float(np.corrcoef(rk, dd)[0, 1])
                sp = spear(rk, dd)
                tag = " (naive kappa=1)" if kappa == 1.0 else ""
                print(f"    kappa(mu_x/mu_y)={kappa:.2f}: corr={cc:+.3f} Spearman={sp:+.3f}{tag}")
                rep[f"drag_corr_kappa{kappa}"] = cc
            print("    CdA offsets (independent drag channel):")
            for t in sorted(common_t, key=lambda k: -dragoff[k]):
                print(f"      {t:>5}: CdA off {dragoff[t]:+.4f}  naive resid {resid_naive[t]:+.3f}")

    # ===== 4. TEAMMATE CONSISTENCY (is B_long a CAR property?) =========
    print("\n" + "=" * 78)
    print("4. IS B_long A CAR PROPERTY? (teammate gap vs between-team spread)")
    print("=" * 78)
    carB = {c: np.mean(seasonLong[c]) for c in seasonLong if len(seasonLong[c]) >= 6}
    tg = teammate_gaps(carB)
    teamvals = {}
    for c, val in carB.items():
        t = DRV2TEAM.get(c)
        if t:
            teamvals.setdefault(t, []).append(val)
    between = np.std([np.mean(v) for v in teamvals.values()])
    rep["Blong_teammate_gap"] = float(np.mean(tg)) if tg else np.nan
    rep["Blong_between_spread"] = float(between)
    print(f"  teammate |ΔB_long*vref^2| (within, noise floor): {np.mean(tg):.3f} g")
    print(f"  between-team spread:                              {between:.3f} g")
    print(f"  between/within = {between/np.mean(tg):.2f}  "
          f"({'CAR signal above noise' if between > np.mean(tg) else 'noise-dominated'})")

    (ENV / "longreeval_report.json").write_text(json.dumps(rep, indent=2))
    print("\nwrote longreeval_report.json")
    return rep


if __name__ == "__main__":
    run()
