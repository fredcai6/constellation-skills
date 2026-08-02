"""Clean power axis from the mid-speed at-peak-power band (#445).

P(v) is flat at peak from ~160 km/h (power_curve_probe), and in the mid band the drag term
½ρCdA·v³ is a small fraction of delivered power — so reading P there is nearly CdA-independent,
unlike the whole-range joint LSTSQ (P↔CdA corr +0.78). Estimate per team per weekend
  P_mid = 90th-pct of [m·a·v + ½ρ·CdA·v³]  over closed full-throttle points in [VLO, VHI] km/h,
then test whether the per-team power↔drag leakage (was cross-team +0.69) collapses.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging = __import__("logging"); logging.getLogger("fastf1").setLevel(logging.ERROR)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session, MASS  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from air_density import air_density  # noqa: E402
from season_cda_collect import TEAMS  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())  # CdA_c per (round,team) from joint fit
VLO, VHI = 150.0, 215.0   # km/h: at peak power, drag still a small fraction


def p_mid(v, a, op, rho, CdA_c):
    """Closed full-throttle points in the band; delivered P = m a v + ½ρCdA v³; 90th pct. Also the
    median drag fraction (how much of P the CdA term is — small ⇒ CdA-robust)."""
    m = (~op) & (v * 3.6 >= VLO) & (v * 3.6 < VHI) & (a > -0.5)
    if m.sum() < 15:
        return None
    vv, aa = v[m], a[m]
    drag_term = 0.5 * rho * CdA_c * vv ** 3
    P = MASS * aa * vv + drag_term
    return float(np.percentile(P, 90)), float(np.median(drag_term / np.maximum(P, 1)))


def main():
    rows = {}; dragfrac = []
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
        for team, cars in TEAMS.items():
            if team not in drs[nm]:
                continue
            v, a, op = throttle_av(q, cars)
            out = p_mid(v, a, op, rho, drs[nm][team][0])
            if out is None:
                continue
            rows.setdefault(team, []).append((nm, out[0] / 1e3))
            dragfrac.append(out[1])
    print(f"mid-band [{VLO:.0f}–{VHI:.0f}] km/h: drag term is median {np.median(dragfrac)*100:.0f}% of "
          f"delivered power ⇒ CdA-robust\n")

    # field-relative P_mid (global baseline), per-team mean
    perrace = {}
    for t, lst in rows.items():
        for nm, P in lst:
            perrace.setdefault(nm, {})[t] = P
    rel = {}
    for nm, d in perrace.items():
        if len(d) < 5:
            continue
        med = np.median(list(d.values()))
        for t, P in d.items():
            rel.setdefault(t, []).append(P - med)
    pmid = {t: float(np.mean(x)) for t, x in rel.items() if len(x) >= 8}

    # drag per team (field-relative log) for the leakage corr
    dmean = {}
    for nm, recs in drs.items():
        vals = {t: np.log(v[0]) for t, v in recs.items()}
        med = np.median(list(vals.values()))
        for t, lv in vals.items():
            dmean.setdefault(t, []).append(lv - med)
    dmean = {t: float(np.mean(x)) for t, x in dmean.items()}

    # joint-fit power (field-relative) for comparison
    jp = {}
    for nm, recs in drs.items():
        vals = {t: v[2] for t, v in recs.items()}
        med = np.median(list(vals.values()))
        for t, P in vals.items():
            jp.setdefault(t, []).append(P - med)
    jp = {t: float(np.mean(x)) for t, x in jp.items()}

    ts = [t for t in pmid if t in dmean]
    cc_mid = float(np.corrcoef([pmid[t] for t in ts], [dmean[t] for t in ts])[0, 1])
    cc_joint = float(np.corrcoef([jp[t] for t in ts], [dmean[t] for t in ts])[0, 1])
    print(f"leakage corr(power, drag):  JOINT-fit P = {cc_joint:+.2f}   MID-BAND P = {cc_mid:+.2f}")
    print("  (mid-band ≪ joint ⇒ the degeneracy is broken; power becomes a cleaner independent axis)\n")
    corr_mj = float(np.corrcoef([pmid[t] for t in ts], [jp[t] for t in ts])[0, 1])
    print(f"corr(mid-band P, joint P) across teams = {corr_mj:+.2f}\n")

    print(f"{'team':>5}{'P_mid rel kW':>13}{'drag rel':>10}")
    for t in sorted(pmid, key=lambda k: -pmid[k]):
        print(f"  {t:>4}{pmid[t]:>12.1f}{dmean.get(t, float('nan')):>10.3f}")


if __name__ == "__main__":
    main()
