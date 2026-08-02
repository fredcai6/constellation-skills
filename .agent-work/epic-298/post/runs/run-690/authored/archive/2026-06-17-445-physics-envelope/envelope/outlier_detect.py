"""Capability outlier detection (#445): flag when a team is "way off their usual" in a measured
force, with the data behind it. Two complementary signals:

 TEMPORAL  (config-invariant params, e.g. braking A_b): this race vs the car's own season norm
           (leave-one-out median), z-scored by fit σ + operating-point σ. "X braking 2.8σ below usual."
 RELATIONAL(config-dependent params, e.g. CdA): this race's position vs everyone ELSE, minus the
           common field shift (cancels track wing) — a team off its NETWORK rating relative to peers.

Each flag carries n_points so thin-data artifacts are distinguishable from real anomalies.
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

from ribbon_reeval import OUT  # noqa: E402
from network_rating import network_solve, build_edges  # noqa: E402


def _op_sigma(season):
    resid = []
    series = {}
    for rn, rec in season.items():
        for t in rec:
            series.setdefault(t, []).append(rec[t][0])
    for t, v in series.items():
        if len(v) >= 6:
            a = np.array(v); resid += list(a - np.median(a))
    return 1.4826 * np.median(np.abs(resid)) if resid else 0.1


def temporal_outliers(season, label, unit="g", thr=2.5):
    op = _op_sigma(season)
    series = {}
    for rn, rec in season.items():
        for t in rec:
            series.setdefault(t, []).append((rn, rec[t][0], rec[t][1], rec[t][2]))
    flags = []
    for t, races in series.items():
        for i, (rn, v, sg, n) in enumerate(races):
            others = [x[1] for j, x in enumerate(races) if j != i]
            if len(others) < 4:
                continue
            norm = np.median(others)
            sd = np.sqrt((sg or op) ** 2 + op ** 2)
            z = (v - norm) / sd
            if abs(z) > thr:
                flags.append((abs(z), t, rn, v, norm, z, n))
    flags.sort(reverse=True)
    print(f"\n=== TEMPORAL outliers — {label} (vs each car's own usual, |z|>{thr}) ===")
    for az, t, rn, v, norm, z, n in flags[:12]:
        d = "BELOW" if z < 0 else "ABOVE"
        thin = "  [thin: %d pts — suspect data]" % n if n < 60 else ""
        print(f"  ⚠ {t:>4} {label} {abs(z):.1f}σ {d} usual at {rn:<14}: "
              f"{v:.2f}{unit} vs usual {norm:.2f}{unit}{thin}")


def relational_outliers(season, label, unit="", thr=2.5):
    """Network position vs peers, field-common-shift removed — done in LOG space so a per-track
    MULTIPLICATIVE effect (e.g. air density: CdA=2mK/rho scales the whole field by 1/rho) becomes a
    common additive log-shift the median removes. Additive detrending can't undo a multiplicative
    confound (it amplifies the team spread — Mexico ×1.326), so log-space is the density/regime-
    robust comparison. rel is a log-ratio; reported as % deviation from the car's rating.

    σ-AWARE: each point's z divides by sqrt(rsd² + σ_meas²) where σ_meas is the measurement's own
    (identifiability) error in log units (σ/val). A poorly-levered fit (e.g. Mexico drag, σ~20%) can
    deviate that much WITHOUT flagging — only deviations beyond BOTH the natural relational spread
    AND the fit's own error are real anomalies."""
    teams = sorted({t for rec in season.values() for t in rec})
    sl = {rn: {t: [np.log(v[0])] + list(v[1:]) for t, v in rec.items() if v[0] and v[0] > 0}
          for rn, rec in season.items()}
    r, _ = network_solve(build_edges(sl), teams)
    rels = []
    for rn, rec in sl.items():
        present = [t for t in rec if rec[t][1] is not None]
        if len(present) < 5:
            continue
        dev = {t: rec[t][0] - r[t] for t in present}
        common = np.median(list(dev.values()))           # track regime (wing/density) — removed
        for t in present:
            logsig = rec[t][1] / np.exp(rec[t][0])        # measurement σ in log units (σ/val)
            rels.append((dev[t] - common, t, rn, rec[t][2], logsig))
    rvals = np.array([x[0] for x in rels])
    rsd = 1.4826 * np.median(np.abs(rvals - np.median(rvals))) + 1e-9   # normal relational spread
    flags = []
    for rel, t, rn, n, lsig in rels:
        z = rel / np.sqrt(rsd ** 2 + lsig ** 2)           # fold in the fit's own identifiability σ
        if abs(z) > thr:
            flags.append((abs(z), t, rn, rel, z, n))
    flags.sort(reverse=True)
    print(f"\n=== RELATIONAL outliers — {label} (network position vs peers, log-space, field-shift removed, |z|>{thr}) ===")
    for az, t, rn, rel, z, n in flags[:12]:
        d = "DRAGGIER" if z > 0 else "SLIPPERIER" if "Cd" in label else ("HIGHER" if z > 0 else "LOWER")
        thin = "  [thin: %d pts]" % n if n < 100 else ""
        print(f"  ⚠ {t:>4} {label} {abs(z):.1f}σ {d} than usual (vs peers) at {rn:<14}: "
              f"{(np.exp(rel)-1)*100:+.1f}% off its rating{thin}")


def main():
    brk = OUT / "season_braking.json"
    drs = OUT / "season_drs.json"; cda = OUT / "season_cda.json"
    if brk.exists():
        bj = json.loads(brk.read_text())   # [A_b, B_b, sigma, n] -> [A_b, sigma, n]
        bj = {rn: {t: [v[0], v[2], v[3]] for t, v in rec.items()} for rn, rec in bj.items()}
        temporal_outliers(bj, "braking-A_b", "g")
    if drs.exists():                       # JOINT DRS fit: [CdA_c,CdA_o,P,σ_c,σ_o,cond,nc,no,ovm]
        dj = json.loads(drs.read_text())
        dj = {rn: {t: [v[0], v[3], v[6]] for t, v in rec.items()} for rn, rec in dj.items()}
        relational_outliers(dj, "CdA_closed(joint,σ-aware)", "")
    elif cda.exists():
        relational_outliers(json.loads(cda.read_text()), "CdA(drag)", "")


if __name__ == "__main__":
    main()
