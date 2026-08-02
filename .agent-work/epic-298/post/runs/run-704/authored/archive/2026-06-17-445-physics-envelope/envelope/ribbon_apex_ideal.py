"""Ideal lap with the cornering limit SWAPPED to MEASURED apex speed (#445, 2026-06-16).

A3 (ribbon_reeval.py) showed the ideal-lap sim fails because its cornering limit
vg = sqrt(G(v)·g/κ) comes from the fitted grip frontier B, which is unidentifiable
single-weekend. The apex-speed FEATURE (A2) measures the same v_apex-vs-radius
relationship directly and IS pace-relevant (Spearman −0.89). So swap the cornering
constraint to the measured season on-limit curve  v_apex(R) = exp(α_team)·R^β  and
compare per-constructor ideal-lap ordering/spread to the fitted-B version + quali pace.

Longitudinal (traction/braking tr, power/drag) kept identical to A3 (fitted A,B) so the
ONLY change is the binding cornering limit — a clean A/B on the swap.
"""
from __future__ import annotations

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

import ribbon_reeval as RR  # noqa: E402
from ribbon_reeval import (  # noqa: E402
    TRACKS, fit_grip_clean, full_q_pd, get_apex_nodes, load_cal_nodes,
    load_session, ideal_time, RHO, MASS, G_CONST, OUT)

APEX = OUT / "apex_corners.npz"
APEXFEAT = OUT / "apex_feature.json"   # A2's VALIDATED per-team on-limit offsets (Spearman −0.89)

TEAMS = {"RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"],
         "MCL": ["NOR", "PIA"], "AMR": ["ALO", "STR"], "ALP": ["GAS", "OCO"],
         "WIL": ["ALB", "SAR"], "ATR": ["TSU", "DEV", "RIC", "LAW"],
         "ALF": ["BOT", "ZHO"], "HAA": ["MAG", "HUL"]}


def apex_curves():
    """Absolute on-limit apex curve v_apex(R)=exp(α_team)·R^β. β + baseline from a global
    fit on apex_corners.npz; the DISCRIMINATING per-team offset δ_team is A2's VALIDATED
    apex_speed_q90 (per-weekend-centered season-median — the −0.89 pace-relevant signal).
    α_team = α0(on-limit baseline) + δ_team."""
    d = np.load(APEX, allow_pickle=True)
    car = d["car"].astype(str); v = d["v_apex"].astype(float); R = d["R_apex"].astype(float)
    ok = np.isfinite(v) & np.isfinite(R) & (v > 0) & (R > 3)
    v, R = v[ok], R[ok]
    logv, logR = np.log(v), np.log(R)
    A = np.column_stack([logR, np.ones_like(logR)])
    coef, *_ = np.linalg.lstsq(A, logv, rcond=None)
    beta = float(coef[0])
    a0 = float(np.quantile(logv - beta * logR, 0.90))   # field on-limit baseline
    feat = json.loads(APEXFEAT.read_text())
    delta = feat["apex_speed_q90"]                       # validated per-team offsets
    alpha = {t: a0 + delta[t] for t in delta}
    return beta, alpha, (R.min(), R.max())


def ideal_time_apex(s, kappa, alpha, beta, A, B, GS, P, cc, co, length):
    """A3's forward-backward sim, but vg = exp(alpha)·R^beta (measured apex) instead of
    sqrt(G·g/κ). Longitudinal tr/drag/power unchanged (fitted A,B)."""
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)

    def Gv(v):
        return min(A + B * v * v, GS)

    def drag(v, k):
        return 0.5 * RHO * (co if (abs(k) < 8e-4 and v > 200 / 3.6) else cc) * v * v / MASS

    R = 1.0 / np.maximum(kappa, 1e-6)
    vg = np.minimum(np.exp(alpha) * R ** beta, 100.0)        # <<< measured apex cornering limit
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G_CONST
            tr = np.sqrt(max(Gv(v[i]) ** 2 - al ** 2, 0)) * G_CONST
            a = min(tr, P / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)), vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            tr = np.sqrt(max(Gv(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST
            a_b = tr + drag(v[i + 1], kappa[i + 1])
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * a_b * ds[i], 1.0)), vg[i])
    t_sim = float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))
    return t_sim * length / s[-1]


def spear(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3:
        return np.nan
    return float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])


def main():
    beta, alpha, (Rlo, Rhi) = apex_curves()
    feat = json.loads(APEXFEAT.read_text())
    pace = feat["quali_pace"]                            # season per-team gap-to-median
    print(f"apex curve: v_apex = exp(α)·R^β, β={beta:.3f}, R {Rlo:.0f}–{Rhi:.0f} m")
    cal_nodes = load_cal_nodes()
    allf, alla, allp = [], [], []    # pooled across tracks

    for name, cfg in TRACKS.items():
        gp, length = cfg["gp"], cfg["length"]
        cache = OUT / f"ribbon_clean_{name.lower()}.npz"
        if not cache.exists():
            print(f"\n{name}: no cached ribbon, skip"); continue
        d = np.load(cache); s, kappa = d["s"], d["kappa"]
        q = load_session(2023, gp, "Q")
        rows = []
        for team, cars in TEAMS.items():
            if team not in alpha or team not in pace:
                continue
            v_kmh, g_g = get_apex_nodes(cal_nodes, gp, cars)
            if v_kmh is None or len(v_kmh) < 25:
                continue
            A, B, GS = fit_grip_clean(v_kmh, g_g)
            pd_ = full_q_pd(q, cars)
            if A is None or pd_ is None:
                continue
            P, cc, co = pd_
            t_fit = ideal_time(s, kappa, A, B, GS, P, cc, co, length)
            t_apex = ideal_time_apex(s, kappa, alpha[team], beta, A, B, GS, P, cc, co, length)
            rows.append((team, t_fit, t_apex, pace[team]))
        if len(rows) < 4:
            print(f"\n{name}: <4 constructors ({len(rows)}), skip"); continue
        print(f"\n{'='*58}\n{name} ({length} m, {len(rows)} constructors)\n{'='*58}")
        print(f"  {'team':>5} {'fit-B':>8} {'apex':>8} {'pace':>8}")
        for t, tf, ta, qp in sorted(rows, key=lambda r: r[2]):
            print(f"  {t:>5} {tf:>8.2f} {ta:>8.2f} {qp:>8.3f}")
        tf = [r[1] for r in rows]; ta = [r[2] for r in rows]; qp = [r[3] for r in rows]
        sf, sa = spear(tf, qp), spear(ta, qp)
        print(f"  spread: fit-B {max(tf)-min(tf):.2f}s  apex {max(ta)-min(ta):.2f}s")
        print(f"  Spearman vs pace (+=pace-relevant):  fit-B {sf:+.3f}   apex {sa:+.3f}")
        # within-track centered, for pooling across tracks
        allf += [x - np.mean(tf) for x in tf]; alla += [x - np.mean(ta) for x in ta]
        allp += [x - np.mean(qp) for x in qp]

    print(f"\n{'='*58}\nPOOLED across tracks (within-track centered, n={len(allp)})\n{'='*58}")
    print(f"  Spearman vs pace:   fit-B {spear(allf, allp):+.3f}   apex {spear(alla, allp):+.3f}")
    print(f"  Pearson  vs pace:   fit-B {np.corrcoef(allf, allp)[0,1]:+.3f}   "
          f"apex {np.corrcoef(alla, allp)[0,1]:+.3f}")


if __name__ == "__main__":
    main()
