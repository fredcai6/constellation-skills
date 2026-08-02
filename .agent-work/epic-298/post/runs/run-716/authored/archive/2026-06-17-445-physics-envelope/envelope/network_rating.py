"""Pairwise-NETWORK rating from per-race measurements (#445) — the alternative to field-mean.

Each race gives pairwise differences d_ij = θ_i − θ_j for the teams present (a graph). Solve for
per-team ratings r minimizing Σ_edges w(r_i − r_j − d_ij)², gauge Σr=0 — robustly, IRLS-down-
weighting outlier edges so a team compromised for ONE weekend just loses those linkages without
shifting everyone's baseline (unlike field-mean, where one bad team poisons the mean).

For config-dependent params (CdA, grip B), pairwise differencing cancels the common track wing-
level the same way field-mean does, but networked & outlier-robust. General over any param.
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


def network_solve(edges, teams, iters=15, huber_c=1.8):
    """edges: list (i, j, d_ij, w_ij). Returns {team: rating} (zero-mean gauge) + final edge weights."""
    idx = {t: k for k, t in enumerate(teams)}; n = len(teams)
    ii = np.array([idx[e[0]] for e in edges]); jj = np.array([idx[e[1]] for e in edges])
    dd = np.array([e[2] for e in edges], float); w0 = np.array([e[3] for e in edges], float)
    w = w0.copy(); r = np.zeros(n)
    for _ in range(iters):
        L = np.zeros((n, n)); b = np.zeros(n)
        for k in range(len(edges)):
            a, c, d, we = ii[k], jj[k], dd[k], w[k]
            L[a, a] += we; L[c, c] += we; L[a, c] -= we; L[c, a] -= we
            b[a] += we * d; b[c] -= we * d
        r = np.linalg.solve(L + 1e-6 * np.eye(n), b); r -= r.mean()
        resid = np.abs((r[ii] - r[jj]) - dd)
        s = 1.4826 * np.median(resid) + 1e-9
        u = resid / (huber_c * s)
        w = w0 * np.where(u < 1, 1.0, 1.0 / np.maximum(u, 1e-9))   # Huber down-weight
    return {t: float(r[idx[t]]) for t in teams}, w


def build_edges(season, drop=None):
    """season: {round: {team: [val, sigma, n]}}. drop: optional (round, team) to remove."""
    edges = []
    for rn, rec in season.items():
        present = [t for t in rec if rec[t][1] is not None and (drop != (rn, t))]
        for a in range(len(present)):
            for b in range(a + 1, len(present)):
                ti, tj = present[a], present[b]
                si, sj = rec[ti][1], rec[tj][1]
                edges.append((ti, tj, rec[ti][0] - rec[tj][0], 1.0 / (si * si + sj * sj + 1e-6)))
    return edges


def field_mean(season, override=None):
    """Per-team mean of (val − field_mean) per race. override: {(round,team): val}."""
    acc = {}
    for rn, rec in season.items():
        vals = {t: (override.get((rn, t), rec[t][0]) if override else rec[t][0]) for t in rec}
        m = np.mean(list(vals.values()))
        for t, v in vals.items():
            acc.setdefault(t, []).append(v - m)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def main():
    cache = OUT / "season_cda.json"
    if not cache.exists():
        print("season_cda.json not ready"); return
    season = json.loads(cache.read_text())
    teams = sorted({t for rec in season.values() for t in rec})

    net, _ = network_solve(build_edges(season), teams)
    fm = field_mean(season)
    print("CdA RATING (relative, zero-mean): NETWORK vs FIELD-MEAN  (lower = slipperier)")
    print(f"  {'team':>5} {'network':>9} {'fieldmean':>10}")
    for t in sorted(teams, key=lambda k: net[k]):
        print(f"  {t:>5} {net[t]:>+9.3f} {fm[t]:>+10.3f}")
    a = np.array([net[t] for t in teams]); b = np.array([fm[t] for t in teams])
    print(f"  corr(network, fieldmean) = {np.corrcoef(a, b)[0,1]:+.3f}")

    # ROBUSTNESS: compromise ONE team for ONE weekend (corrupt its CdA), see who moves
    rn0 = list(season.keys())[10]; victim = "WIL"
    if victim in season[rn0]:
        bad = season[rn0][victim][0] + 0.6          # spurious huge drag one weekend
        net2, _ = network_solve(build_edges({**season}), teams)  # baseline (unchanged season)
        # network with corruption: replace the value via a temp season
        sc = json.loads(cache.read_text()); sc[rn0][victim][0] = bad
        net_c, _ = network_solve(build_edges(sc), teams)
        fm_c = field_mean(season, override={(rn0, victim): bad})
        print(f"\n  ROBUSTNESS — corrupt {victim} at {rn0} by +0.60 CdA. |Δrating| for the OTHER teams:")
        others = [t for t in teams if t != victim]
        dnet = np.mean([abs(net_c[t] - net[t]) for t in others])
        dfm = np.mean([abs(fm_c[t] - fm[t]) for t in others])
        print(f"    NETWORK   mean |Δ| on others = {dnet:.4f}   ({victim}: {net[victim]:+.3f}→{net_c[victim]:+.3f})")
        print(f"    FIELDMEAN mean |Δ| on others = {dfm:.4f}   ({victim}: {fm[victim]:+.3f}→{fm_c[victim]:+.3f})")
        print(f"    -> network shrugs off the bad weekend ({dnet/max(dfm,1e-9):.2f}× the field-mean's contamination)")


if __name__ == "__main__":
    main()
