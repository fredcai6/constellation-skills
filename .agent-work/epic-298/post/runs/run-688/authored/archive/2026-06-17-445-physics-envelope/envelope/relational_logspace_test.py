"""Why the Mexico CdA flags survived the density fix, and the log-space fix (#445).

The density correction is a per-track MULTIPLICATIVE factor (CdA = 2mK/rho, rho≈0.905 at Mexico
=> ×1.326). The relational detector removes the track regime ADDITIVELY (median field shift), which
cannot undo a multiplicative amplification of the team spread — so Mexico's amplified spread shows
up as per-team anomalies (and got WORSE after the fix, since physical CdA spread is larger).

Fix: do the relational comparison in LOG space. A per-track multiplicative factor becomes a common
ADDITIVE log-shift, which the median removes. Prediction (strong check): log-relational on the
fixed-rho file and the real-rho file are IDENTICAL — the detector becomes density-invariant.
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

from network_rating import network_solve, build_edges  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def relational(season, logspace, thr=2.5):
    """Return sorted flags (|z|, team, round, rel, z, n). If logspace, residuals in log(CdA)."""
    teams = sorted({t for rec in season.values() for t in rec})
    # network rating in the same space we score in
    if logspace:
        sl = {rn: {t: [np.log(v[0])] + v[1:] for t, v in rec.items()} for rn, rec in season.items()}
    else:
        sl = season
    r, _ = network_solve(build_edges(sl), teams)
    rels = []
    for rn, rec in sl.items():
        present = [t for t in rec if rec[t][1] is not None]
        if len(present) < 5:
            continue
        dev = {t: rec[t][0] - r[t] for t in present}
        common = np.median(list(dev.values()))
        for t in present:
            rels.append((dev[t] - common, t, rn, rec[t][2]))
    rvals = np.array([x[0] for x in rels])
    rsd = 1.4826 * np.median(np.abs(rvals - np.median(rvals))) + 1e-9
    flags = [(abs(rel / rsd), t, rn, rel, rel / rsd, n) for rel, t, rn, n in rels if abs(rel / rsd) > thr]
    flags.sort(reverse=True)
    return flags


def show(title, flags, n=8):
    print(f"\n{title}")
    for az, t, rn, rel, z, n_ in flags[:n]:
        d = "SLIPPERIER" if z < 0 else "DRAGGIER"
        print(f"  ⚠ {t:>4} {abs(z):4.1f}σ {d:>10} at {rn:<14} ({rel:+.3f})")
    if not flags:
        print("  (none)")


def main():
    new = json.loads((OUT / "season_cda.json").read_text())
    old = json.loads((OUT / "season_cda_fixedrho.json").read_text())

    show("ADDITIVE relational on real-rho CdA (current detector):", relational(new, False))
    show("LOG relational on real-rho CdA:", relational(new, True))
    show("LOG relational on fixed-rho CdA (should match the line above):", relational(old, True))

    # quantitative density-invariance check: top-12 z-scores, log-space, old vs new
    fn = {(t, rn): z for _, t, rn, _, z, _ in relational(new, True)}
    fo = {(t, rn): z for _, t, rn, _, z, _ in relational(old, True)}
    keys = sorted(set(fn) | set(fo), key=lambda k: -abs(fn.get(k, 0)))
    maxdiff = max((abs(fn.get(k, 0) - fo.get(k, 0)) for k in keys), default=0.0)
    print(f"\nlog-space density-invariance: max |z_new - z_old| over flagged set = {maxdiff:.4f}")
    print("(≈0 confirms the detector is invariant to the density correction in log-space)")


if __name__ == "__main__":
    main()
