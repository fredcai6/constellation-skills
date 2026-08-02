"""Per-team POWER signal from the joint fit (#445) — global baseline, pick up team info when rich.

The joint DRS fit breaks the power↔drag degeneracy (open high-speed points anchor the balance), so P
is far better identified than the old closed-only fit. Treat power like drag: field-relative per
weekend (global baseline, not a PU-manufacturer baseline), with the honest covariance σ_P. Questions:
  1. Is there REAL per-team power separation beyond measurement noise?
  2. Per-track (within-team) variance vs drag — the user expects power to vary LESS than drag.
  3. Do PU-mates (Merc/Ferrari/Honda/Renault) cluster? If within-PU spread is large, the ICE baseline
     is insufficient (setups matter) → go fully per-team with a global baseline + season prior.
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

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
drs = json.loads((OUT / "season_drs.json").read_text())

PU = {"MERC": "Mercedes", "WIL": "Mercedes", "MCL": "Mercedes", "AMR": "Mercedes",
      "FER": "Ferrari", "HAA": "Ferrari", "ALF": "Ferrari",
      "RBR": "Honda", "ATR": "Honda", "ALP": "Renault"}


def field_relative(idx, sidx, logspace=False):
    """Per (team): list of (round, dev_from_field_median, measurement σ). idx=value col, sidx=σ col."""
    per = {}
    for rn, rec in drs.items():
        vals = {t: (np.log(v[idx]) if logspace else v[idx]) for t, v in rec.items() if v[idx] > 0}
        if len(vals) < 5:
            continue
        m = np.median(list(vals.values()))
        for t, v in vals.items():
            sg = rec[t][sidx] / rec[t][idx] if logspace else rec[t][sidx]   # σ in (log) units
            per.setdefault(t, []).append((rn, v - m, sg))
    return per


def decompose(per, label, unit):
    """between-team vs within-team(per-track) vs measurement σ."""
    means, withins, meas = {}, {}, []
    for t, pts in per.items():
        d = np.array([p[1] for p in pts]); s = np.array([p[2] for p in pts])
        w = 1.0 / (s ** 2 + 1e-9)
        mt = np.average(d, weights=w); means[t] = mt
        withins[t] = np.sqrt(np.average((d - mt) ** 2, weights=w))
        meas += list(s)
    between = float(np.std(list(means.values())))
    within = float(np.median(list(withins.values())))
    msig = float(np.median(meas))
    n = float(np.median([len(p) for p in per.values()]))
    se = within / np.sqrt(n)
    print(f"\n=== {label} ===")
    print(f"  between-team σ = {between:.3f}{unit}   within-team(per-track) σ = {within:.3f}{unit}"
          f"   measurement σ = {msig:.3f}{unit}")
    print(f"  team-mean SE ≈ {se:.3f}{unit}   ⇒ between/SE = {between/se:.1f} "
          f"({'REAL per-team separation' if between/se > 2 else 'not resolved'})")
    print(f"  discriminability between/within = {between/within:.2f}")
    # within-team scatter beyond measurement = real per-weekend (setup) variation
    real_within = np.sqrt(max(within ** 2 - msig ** 2, 0))
    print(f"  within beyond measurement (real per-weekend setup) σ = {real_within:.3f}{unit}")
    return means, withins


def main():
    # absolute power level sanity
    allP = [v[2] for rec in drs.values() for v in rec.values()]
    print(f"absolute joint-fit power: median {np.median(allP):.0f} kW, IQR "
          f"[{np.percentile(allP,25):.0f}, {np.percentile(allP,75):.0f}] kW")

    # POWER (field-relative, kW) vs DRAG (CdA_closed, log so % comparable)
    powP = field_relative(2, 9, logspace=False)
    pmeans, _ = decompose(powP, "POWER (field-relative, kW)", " kW")

    dragL = field_relative(0, 3, logspace=True)
    dmeans, _ = decompose(dragL, "DRAG CdA_closed (field-relative, log ⇒ fractional)", "")

    # LEAKAGE CHECK. The P↔CdA fit degeneracy is POSITIVE (over-P forces over-CdA to hold the curve),
    # so leakage shows up as POSITIVE corr(power, drag). Compare the cross-team corr to the median
    # per-FIT estimator corr: if cross-team ≈ per-fit degeneracy, the power signal is contaminated.
    teams = [t for t in pmeans if t in dmeans]
    pv = np.array([pmeans[t] for t in teams]); dv = np.array([dmeans[t] for t in teams])
    cc = float(np.corrcoef(pv, dv)[0, 1])
    perfit = np.median([v[10] for rec in drs.values() for v in rec.values() if len(v) > 10])
    print(f"\nLEAKAGE CHECK: cross-team corr(power, drag) = {cc:+.2f}   "
          f"median per-FIT P↔CdA_c corr = {perfit:+.2f}")
    if cc > 0.5 and perfit > 0.5:
        print("   ⚠ both positive & large ⇒ per-team power is partly the drag degeneracy leaking in — "
              "NOT yet a clean independent axis.")
    elif cc > 0.5 and perfit < 0.3:
        print("   per-fit degeneracy is broken, yet teams correlate ⇒ a REAL power↔drag philosophy "
              "correlation (high-power teams also run more wing), not leakage.")
    else:
        print("   power and drag look separable.")
    print("   per-team DRAG (field-relative, log) for context:")
    for t in sorted(dmeans, key=lambda k: dmeans[k]):
        print(f"      {t:>4} drag {dmeans[t]:+.3f}   power {pmeans[t]:+6.1f} kW")
    powL = field_relative(2, 9, logspace=True)
    decompose(powL, "POWER (field-relative, log ⇒ fractional, compare to drag above)", "")

    # per-team mean power + PU grouping
    print("\nper-team mean power (field-relative), grouped by PU:")
    by_pu = {}
    for t, m in sorted(pmeans.items(), key=lambda kv: -kv[1]):
        by_pu.setdefault(PU[t], []).append((t, m))
    for pu in ["Mercedes", "Ferrari", "Honda", "Renault"]:
        ts = by_pu.get(pu, [])
        gm = np.mean([m for _, m in ts]) if ts else 0
        members = "  ".join(f"{t}{m:+.1f}" for t, m in ts)
        print(f"   {pu:>9} (mean {gm:+5.1f} kW):  {members}")

    # PU clustering: between-PU vs within-PU
    pu_means = {pu: np.mean([m for _, m in ts]) for pu, ts in by_pu.items()}
    between_pu = np.std([pu_means[PU[t]] for t in pmeans])           # weighted by team count
    within_pu = np.std([pmeans[t] - pu_means[PU[t]] for t in pmeans])
    print(f"\n  PU clustering: between-PU σ = {between_pu:.1f} kW   within-PU σ = {within_pu:.1f} kW")
    if within_pu >= between_pu:
        print("   ⇒ within-PU spread ≥ between-PU: same engine ≠ same power. The ICE/PU baseline is "
              "INSUFFICIENT — setups dominate. Use a GLOBAL baseline + per-team pickup (PU only a weak prior).")
    else:
        print("   ⇒ PU explains most of the between-team power: the manufacturer grouping carries real signal.")


if __name__ == "__main__":
    main()
