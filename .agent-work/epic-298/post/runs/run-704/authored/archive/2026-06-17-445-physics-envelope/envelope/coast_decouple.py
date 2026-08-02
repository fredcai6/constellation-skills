"""Power-free CdA from quali COAST-DOWN, then clean per-team power (#445).

P and CdA share the full-throttle equation → degenerate (joint fit P↔CdA corr +0.78). Break it with a
power-free drag measurement: off-throttle, no-brake COASTING (cooldown / in-laps — the only place a
quali car coasts) has drive power ≈ 0, so the deceleration is pure resistance:
    −a = ½ρ·CdA/m · v²  +  (rolling + engine-brake + MGU-K regen)
Fit −a = A + B·v²: the v² slope B → CdA (aero, INDEPENDENT of drive power); A absorbs the roughly
constant/regen terms. Then power from full-throttle with this independent CdA — no degeneracy:
    P = m·a·v + ½ρ·CdA_coast·v³.
Validate CdA_coast vs the joint-fit CdA_c, and check the power↔drag leakage collapses.
"""
import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session, driver_num, MASS  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from air_density import air_density  # noqa: E402
from season_cda_collect import TEAMS  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())
VMIN_COAST = 180.0   # km/h — high-speed straight coast (aero-dominated, away from corners)


def coast_points(session, cars):
    """Off-throttle, no-brake, decelerating points (m/s, m/s²) — predominantly cooldown/in-laps."""
    V, A = [], []
    for car in cars:
        try:
            num = driver_num(session, car)
            cd = session.car_data[num]
        except Exception:
            continue
        tc = cd["SessionTime"].dt.total_seconds().to_numpy()
        spd = cd["Speed"].to_numpy(float) / 3.6
        thr = cd["Throttle"].to_numpy(float)
        brk = cd["Brake"].to_numpy(float)
        o = np.argsort(tc); tc, spd, thr, brk = tc[o], spd[o], thr[o], brk[o]
        keep = np.concatenate([[True], np.diff(tc) > 1e-9])
        tc, spd, thr, brk = tc[keep], spd[keep], thr[keep], brk[keep]
        for i in range(1, len(tc) - 1):
            dt = tc[i + 1] - tc[i - 1]
            if dt <= 0 or dt > 0.6:
                continue
            a = (spd[i + 1] - spd[i - 1]) / dt
            if thr[i] < 5 and brk[i] < 0.5 and spd[i] * 3.6 > VMIN_COAST and -15 < a < -0.2:
                V.append(spd[i]); A.append(a)
    return np.array(V), np.array(A)


def fit_coast_cda(v, a, rho):
    """−a = A + B v²  (median per v-bin, robust). Returns CdA = 2 m B / ρ and n."""
    dec = -a
    vb, db = [], []
    for lo in np.arange(VMIN_COAST, 340, 12):
        m = (v * 3.6 >= lo) & (v * 3.6 < lo + 12)
        if m.sum() >= 5:
            vb.append((v[m] ** 2).mean()); db.append(np.median(dec[m]))
    if len(vb) < 3:
        return None, 0
    vb, db = np.array(vb), np.array(db)
    X = np.column_stack([np.ones_like(vb), vb])
    coef, *_ = np.linalg.lstsq(X, db, rcond=None)
    B = coef[1]
    if B <= 0:
        return None, len(vb)
    return float(2 * MASS * B / rho), len(vb)


def main():
    t0 = time.time()
    coast_cda, joint_cda, pclean, npts = {}, {}, {}, {}
    for r in range(1, 23):
        try:
            q = load_session(2023, r, "Q")
        except Exception:
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        if nm not in drs:
            continue
        rho = air_density(2023, r, "Q")
        nteam = 0
        for team, cars in TEAMS.items():
            if team not in drs[nm]:
                continue
            vc, ac = coast_points(q, cars)
            cda, nb = fit_coast_cda(vc, ac, rho)
            if cda is None or not (0.3 < cda < 3.5):
                continue
            # clean power from full-throttle using the INDEPENDENT coast CdA
            v, a, op = throttle_av(q, cars)
            m = (~op) & (v * 3.6 >= 150) & (v * 3.6 < 215) & (a > -0.5)
            if m.sum() < 15:
                continue
            P = np.percentile(MASS * a[m] * v[m] + 0.5 * rho * cda * v[m] ** 3, 90)
            coast_cda.setdefault(team, []).append((nm, cda))
            joint_cda.setdefault(team, []).append((nm, drs[nm][team][0]))
            pclean.setdefault(team, []).append((nm, P / 1e3))
            npts.setdefault(team, []).append(len(vc))
            nteam += 1
        print(f"[{time.strftime('%H:%M:%S')}] round {r:>2} {nm:14s} {nteam} teams with coast fit",
              flush=True)

    # field-relative helper
    def field_rel(d, log=False):
        per = {}
        byr = {}
        for t, lst in d.items():
            for nm, val in lst:
                byr.setdefault(nm, {})[t] = (np.log(val) if log else val)
        for nm, rec in byr.items():
            if len(rec) < 5:
                continue
            med = np.median(list(rec.values()))
            for t, x in rec.items():
                per.setdefault(t, []).append(x - med)
        return {t: float(np.mean(x)) for t, x in per.items() if len(x) >= 6}

    cc_coast = field_rel(coast_cda, log=True)
    cc_joint = field_rel(joint_cda, log=True)
    pc = field_rel(pclean, log=False)

    # validation: coast CdA vs joint CdA (per-team, field-relative)
    ts = [t for t in cc_coast if t in cc_joint]
    agree = float(np.corrcoef([cc_coast[t] for t in ts], [cc_joint[t] for t in ts])[0, 1])
    # leakage: clean power vs coast drag (independent CdA) — should collapse vs the +0.48/+0.63 before
    ts2 = [t for t in pc if t in cc_coast]
    leak = float(np.corrcoef([pc[t] for t in ts2], [cc_coast[t] for t in ts2])[0, 1])

    print(f"\n--- elapsed {time.time()-t0:.0f}s ---")
    print(f"coast points per team (season total, median): "
          f"{int(np.median([np.sum(v) for v in npts.values()]))}")
    print(f"\nVALIDATION corr(coast-CdA, joint-CdA) per team = {agree:+.2f}  "
          f"(high ⇒ the power-free drag agrees with the full-throttle drag)")
    print(f"LEAKAGE   corr(clean power, coast-drag) per team = {leak:+.2f}  "
          f"(was joint +0.63 / mid-band +0.48; →0 ⇒ decoupled)\n")
    print(f"{'team':>5}{'P_clean rel kW':>15}{'coast-drag rel':>15}")
    for t in sorted(pc, key=lambda k: -pc[k]):
        print(f"  {t:>4}{pc[t]:>14.1f}{cc_coast.get(t, float('nan')):>15.3f}")


if __name__ == "__main__":
    main()
