"""Ideal-lap longitudinal-fix ablation ladder (#445, 2026-06-16). Paths 5,1,2,3,4.

Each config changes ONE thing vs the previous, so the pace-correlation delta attributes the
effect. Cornering limit is always the measured apex curve (vg=exp(α)·R^β). What varies is the
LONGITUDINAL side (friction-circle grip for traction/braking, power/drag, exit/entry structure):

 baseline  : vg=fitB,  G=fitB,    pd=team           (A3's original — both from fitted B)
 apex+fitB : vg=apex,  G=fitB,    pd=team           (current swap — longitudinal still fitted B)
 P5 neut.  : vg=apex,  G=SHARED,  pd=SHARED         (longitudinal fully neutralised → cornering ceiling)
 P1 shareG : vg=apex,  G=SHARED,  pd=team           (+ per-team power/drag)
 P2 apexG  : vg=apex,  G=apexC,   pd=team           (+ measured per-car apex grip in friction circle)
 P3 exitP  : vg=apex,  G=apexC,   pd=team, exit=POWER-only
 P4 honBrk : vg=apex,  G=apexC,   pd=team, exit=POWER, braking=downforce-scaled (not sensor-capped)

Reference: the raw apex FEATURE is Spearman −0.89 to pace; the ideal lap should approach that if
the longitudinal stops diluting it.
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

from ribbon_reeval import (  # noqa: E402
    TRACKS, fit_grip_clean, full_q_pd, get_apex_nodes, load_cal_nodes,
    load_session, RHO, MASS, G_CONST, OUT)
from ribbon_apex_ideal import apex_curves, TEAMS, spear  # noqa: E402

APEX = OUT / "apex_corners.npz"
APEXFEAT = OUT / "apex_feature.json"
GS = 5.2
BRAKE_FLOOR = 5.0   # g, domain peak braking (un-truncated)


def apex_const_grip():
    """Per-team measured apex lateral grip (median alat_apex, g) — a FLAT measured friction-circle
    grip that avoids the β<0.5 apex/frontier inconsistency (no unphysical decreasing G(v))."""
    d = np.load(APEX, allow_pickle=True)
    car = d["car"].astype(str); al = d["alat_apex"].astype(float)
    out = {}
    for t, drvs in TEAMS.items():
        m = np.isin(car, drvs) & np.isfinite(al)
        if m.sum() >= 20:
            out[t] = float(np.median(al[m]))
    return out


def sim(s, kappa, length, vg, Gfun, P, cc, co, exit_power=False, brake_df=False):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)

    def drag(v, k):
        return 0.5 * RHO * (co if (abs(k) < 8e-4 and v > 200 / 3.6) else cc) * v * v / MASS

    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G_CONST
            if exit_power:
                a = P / (MASS * max(v[i], 1.0)) - drag(v[i], kappa[i])
            else:
                tr = np.sqrt(max(Gfun(v[i]) ** 2 - al ** 2, 0)) * G_CONST
                a = min(tr, P / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)), vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            if brake_df:
                # downforce-scaled braking grip (rises with speed), floored at domain peak, NOT sensor-capped
                gb = min(BRAKE_FLOOR, Gfun(v[i + 1]) * (1.0 + 0.35 * (v[i + 1] / (200 / 3.6)) ** 2))
                a_b = np.sqrt(max(gb ** 2 - al ** 2, 0)) * G_CONST + drag(v[i + 1], kappa[i + 1])
            else:
                a_b = np.sqrt(max(Gfun(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST + drag(v[i + 1], kappa[i + 1])
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * a_b * ds[i], 1.0)), vg[i])
    return float(np.sum(ds / ((v[:-1] + v[1:]) / 2))) * length / s[-1]


def vg_fitB(kappa, A, B):
    k = np.abs(kappa); vg = np.sqrt(GS * G_CONST / np.maximum(k, 1e-6))
    for _ in range(10):
        vg = np.minimum(np.sqrt(np.minimum(A + B * vg * vg, GS) * G_CONST / np.maximum(k, 1e-6)), 100.0)
    return vg


def vg_apex(kappa, alpha, beta):
    R = 1.0 / np.maximum(np.abs(kappa), 1e-6)
    return np.minimum(np.exp(alpha) * R ** beta, 100.0)


CONFIGS = ["baseline", "apex+fitB", "P5 neut", "P1 shareG", "P2 apexG", "P3 exitP", "P4 honBrk"]


def main():
    beta, alpha, (Rlo, Rhi) = apex_curves()
    apexG = apex_const_grip()
    feat = json.loads(APEXFEAT.read_text()); pace = feat["quali_pace"]
    cal_nodes = load_cal_nodes()
    # diagnostic: apex vs frontier grip-vs-speed
    print(f"DIAGNOSTIC: apex β={beta:.3f} (pure-grip √R→0.5, downforce→>0.5). "
          f"β<0.5 ⇒ measured effective cornering grip FALLS with corner speed — CONTRADICTS the "
          f"A+B·v² frontier (grip rises). Apex is pace-true (−0.89); frontier is fitted/noisy.")
    print(f"per-team flat apex grip (median alat_apex, g): " +
          ", ".join(f"{t}:{apexG[t]:.2f}" for t in sorted(apexG)))

    pooled = {c: {"f": [], "p": []} for c in CONFIGS}
    for name, cfg in TRACKS.items():
        cache = OUT / f"ribbon_clean_{name.lower()}.npz"
        if not cache.exists():
            continue
        d = np.load(cache); s, kappa = d["s"], d["kappa"]
        q = load_session(2023, cfg["gp"], "Q")
        team_par = {}
        for team, cars in TEAMS.items():
            if team not in alpha or team not in pace or team not in apexG:
                continue
            v_kmh, g_g = get_apex_nodes(cal_nodes, cfg["gp"], cars)
            if v_kmh is None or len(v_kmh) < 25:
                continue
            A, B, _ = fit_grip_clean(v_kmh, g_g)
            pd_ = full_q_pd(q, cars)
            if A is None or pd_ is None:
                continue
            team_par[team] = dict(A=A, B=B, P=pd_[0], cc=pd_[1], co=pd_[2])
        if len(team_par) < 4:
            continue
        # shared (field-median) params
        Am = np.median([p["A"] for p in team_par.values()]); Bm = np.median([p["B"] for p in team_par.values()])
        Pm = np.median([p["P"] for p in team_par.values()]); ccm = np.median([p["cc"] for p in team_par.values()])
        com = np.median([p["co"] for p in team_par.values()])
        res = {c: {} for c in CONFIGS}
        for team, p in team_par.items():
            vgF = vg_fitB(kappa, p["A"], p["B"]); vgA = vg_apex(kappa, alpha[team], beta)
            Gf = lambda v, a=p["A"], b=p["B"]: min(a + b * v * v, GS)
            Gs = lambda v: min(Am + Bm * v * v, GS)
            Gc = lambda v, g=apexG[team]: g
            res["baseline"][team] = sim(s, kappa, cfg["length"], vgF, Gf, p["P"], p["cc"], p["co"])
            res["apex+fitB"][team] = sim(s, kappa, cfg["length"], vgA, Gf, p["P"], p["cc"], p["co"])
            res["P5 neut"][team] = sim(s, kappa, cfg["length"], vgA, Gs, Pm, ccm, com)
            res["P1 shareG"][team] = sim(s, kappa, cfg["length"], vgA, Gs, p["P"], p["cc"], p["co"])
            res["P2 apexG"][team] = sim(s, kappa, cfg["length"], vgA, Gc, p["P"], p["cc"], p["co"])
            res["P3 exitP"][team] = sim(s, kappa, cfg["length"], vgA, Gc, p["P"], p["cc"], p["co"], exit_power=True)
            res["P4 honBrk"][team] = sim(s, kappa, cfg["length"], vgA, Gc, p["P"], p["cc"], p["co"], exit_power=True, brake_df=True)
        teams = list(team_par)
        pc = [pace[t] for t in teams]
        print(f"\n{name} ({len(teams)} constructors):")
        for c in CONFIGS:
            tt = [res[c][t] for t in teams]
            print(f"  {c:>10}: Spearman {spear(tt, pc):+.3f}  spread {max(tt)-min(tt):5.2f}s")
            pooled[c]["f"] += [x - np.mean(tt) for x in tt]; pooled[c]["p"] += [x - np.mean(pc) for x in pc]

    print(f"\n{'='*58}\nPOOLED across tracks (within-track centered)\n{'='*58}")
    print(f"  reference: raw apex FEATURE Spearman −0.89")
    for c in CONFIGS:
        f, p = pooled[c]["f"], pooled[c]["p"]
        print(f"  {c:>10}: Spearman {spear(f, p):+.3f}  Pearson {np.corrcoef(f, p)[0,1]:+.3f}  (n={len(p)})")


if __name__ == "__main__":
    main()
