"""Ideal lap v2 — three MEASURED truths (#445):
  cornering  = measured apex curve   v_apex(R)=exp(α)·R^β          (per-car, season)
  accel      = measured full-throttle a(v), TOP-SPEED-ANCHORED     (per-car, per-track)
  braking    = SHARED friction-circle grip                          (not a clean per-car axis)
No fitted-B grip anywhere on the per-car axes. Compare to P5 (shared longitudinal, +0.864) and
the raw apex feature (−0.89).

TOP-SPEED ANCHOR (the certainty trick): at top speed a=0 ⇒ v_max³=2P/(ρCdA), so the measured
v_max fixes P/CdA and the 2-param (P,CdA) fit collapses to a 1-param fit a(v)=K(v_max³/v − v²)
(K=½ρCdA/m). Lower σ. We report σ_P for the 2-param vs anchored fit to confirm the gain.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import (load_session, fit_grip_clean, get_apex_nodes, load_cal_nodes,
                           RHO, MASS, G_CONST, OUT)  # noqa: E402
from ribbon_apex_ideal import apex_curves, TEAMS, spear  # noqa: E402
from ribbon_long_paths import vg_apex  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from air_density import air_density  # noqa: E402

GS = 5.2
APEXFEAT = OUT / "apex_feature.json"
TRACKS = {"Monza": dict(gp="Italy", length=5793), "Hungary": dict(gp="Hungary", length=4381),
          "Suzuka": dict(gp="Japan", length=5807)}
RNG = np.random.default_rng(3)


def frontier_pts(v, a, q=0.90):
    vb, ab = [], []
    for lo in np.arange(20, 100, 6):
        m = (v >= lo) & (v < lo + 6)
        if m.sum() >= 8:
            vb.append(v[m].mean()); ab.append(np.quantile(a[m], q))
    return np.array(vb), np.array(ab)


def fit_2param(vb, ab, rho=RHO):
    X = np.column_stack([1 / (MASS * vb), -0.5 * rho * vb ** 2 / MASS])
    (P, CdA), *_ = np.linalg.lstsq(X, ab, rcond=None)
    return P, CdA


def fit_anchored(vb, ab, vmax, rho=RHO):
    x = vmax ** 3 / vb - vb ** 2
    K = float(np.sum(x * ab) / np.sum(x * x))          # 1-param: a = K*(vmax³/v − v²)
    CdA = 2 * MASS * K / rho; P = MASS * K * vmax ** 3  # K (and P) are density-free; CdA = 2mK/rho
    return K, P, CdA


def av_measured(v, a, rho=RHO):
    """Top-speed-anchored measured accel curve a_K(v) + diagnostics + σ comparison."""
    vb, ab = frontier_pts(v, a)
    if len(vb) < 4:
        return None
    vmax = np.percentile(v, 99.5)
    K, P, CdA = fit_anchored(vb, ab, vmax, rho)
    # σ via bootstrap, both methods
    P2s, PKs = [], []
    for _ in range(25):
        idx = RNG.integers(0, len(v), len(v))
        b, c = frontier_pts(v[idx], a[idx])
        if len(b) >= 4:
            P2, _ = fit_2param(b, c, rho); P2s.append(P2 / 1e3)
            vm = np.percentile(v[idx], 99.5); _, PK, _ = fit_anchored(b, c, vm, rho); PKs.append(PK / 1e3)
    return dict(K=K, P=P, CdA=CdA, vmax=vmax,
                sP_2param=np.std(P2s) if P2s else np.nan,
                sP_anchor=np.std(PKs) if PKs else np.nan)


def sim(s, kappa, length, vg, a_meas, vmax, Gs):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    v = np.minimum(vg, vmax)
    for _ in range(4):
        for i in range(n - 1):
            af = min(a_meas(v[i]), Gs(v[i]) * G_CONST)        # measured accel, traction-capped
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * af * ds[i], 1.0)), vg[i + 1], vmax)
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            ab = np.sqrt(max(Gs(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST   # SHARED braking grip
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * ab * ds[i], 1.0)), vg[i])
    return float(np.sum(ds / ((v[:-1] + v[1:]) / 2))) * length / s[-1]


def main():
    beta, alpha, _ = apex_curves()
    pace = json.loads(APEXFEAT.read_text())["quali_pace"]
    cal = load_cal_nodes()
    s2, sA = [], []     # σ collectors
    allnew, allp5, allp = [], [], []

    for name, cfg in TRACKS.items():
        cache = OUT / f"ribbon_clean_{name.lower()}.npz"
        if not cache.exists():
            continue
        d = np.load(cache); s, kappa = d["s"], d["kappa"]
        q = load_session(2023, cfg["gp"], "Q")
        rho = air_density(2023, cfg["gp"], "Q")        # real per-track density (not fixed 1.2)
        # shared grip (field-median A,B) for braking + traction cap + P5 baseline
        AB = []
        meas = {}
        for team, cars in TEAMS.items():
            if team not in alpha or team not in pace:
                continue
            vk, gg = get_apex_nodes(cal, cfg["gp"], cars)
            if vk is None or len(vk) < 25:
                continue
            A, B, _ = fit_grip_clean(vk, gg)
            if A is None:
                continue
            v, a, _ = throttle_av(q, cars)
            if len(v) < 80:
                continue
            mv = av_measured(v, a, rho)
            if mv is None:
                continue
            AB.append((A, B)); meas[team] = mv
            if np.isfinite(mv["sP_2param"]) and np.isfinite(mv["sP_anchor"]):
                s2.append(mv["sP_2param"]); sA.append(mv["sP_anchor"])
        if len(meas) < 4:
            continue
        Am = np.median([x[0] for x in AB]); Bm = np.median([x[1] for x in AB])
        Gs = lambda v: min(Am + Bm * v * v, GS)
        rows = []
        for team, mv in meas.items():
            vg = vg_apex(kappa, alpha[team], beta)
            a_meas = (lambda vv, K=mv["K"], vm=mv["vmax"]: max(K * (vm ** 3 / max(vv, 1.0) - vv * vv), 0.0))
            t_new = sim(s, kappa, cfg["length"], vg, a_meas, mv["vmax"], Gs)
            # P5 baseline: shared accel cap (field-median measured) + shared braking
            Km = np.median([m["K"] for m in meas.values()]); vmm = np.median([m["vmax"] for m in meas.values()])
            a_shared = (lambda vv, K=Km, vm=vmm: max(K * (vm ** 3 / max(vv, 1.0) - vv * vv), 0.0))
            t_p5 = sim(s, kappa, cfg["length"], vg, a_shared, vmm, Gs)
            rows.append((team, t_new, t_p5, pace[team]))
        tn = [r[1] for r in rows]; t5 = [r[2] for r in rows]; pc = [r[3] for r in rows]
        print(f"{name}: NEW(measured a(v)) Spearman {spear(tn, pc):+.3f}   "
              f"P5(shared) {spear(t5, pc):+.3f}   (n={len(rows)})")
        allnew += [x - np.mean(tn) for x in tn]; allp5 += [x - np.mean(t5) for x in t5]
        allp += [x - np.mean(pc) for x in pc]

    print(f"\nσ_P (per-race power fit): 2-param {np.mean(s2):.1f} kW  →  "
          f"top-speed-anchored {np.mean(sA):.1f} kW  ({(1-np.mean(sA)/np.mean(s2))*100:.0f}% tighter)")
    print(f"\nPOOLED Spearman vs pace:  NEW (measured per-car a(v)) {spear(allnew, allp):+.3f}   "
          f"P5 (shared longitudinal) {spear(allp5, allp):+.3f}   (raw apex feature −0.89)")


if __name__ == "__main__":
    main()
