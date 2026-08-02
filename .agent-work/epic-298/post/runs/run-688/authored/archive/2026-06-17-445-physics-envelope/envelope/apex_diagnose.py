"""Per-car apex-speed diagnostics + HAA resolution check + scatter plot (#445).

After apex_feature.py builds the season features, this:
  - prints per-car (not just per-team) apex-speed offset vs frontier
  - explicitly checks: does HAA read appropriately SLOW in apex-speed where it read
    FAST in frontier-g?  (the paradox-resolution test)
  - scatter: apex-speed feature vs quali pace, frontier-g vs quali pace, side by side
  - HAA vs RBR direct apex-speed-at-radius comparison at matched radii bins
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NPZ = OUT / "apex_corners.npz"
DRV2TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER",
            "SAI": "FER", "NOR": "MCL", "PIA": "MCL", "ALO": "AMR", "STR": "AMR",
            "GAS": "ALP", "OCO": "ALP", "ALB": "WIL", "SAR": "WIL", "TSU": "ATR",
            "DEV": "ATR", "RIC": "ATR", "LAW": "ATR", "BOT": "ALF", "ZHO": "ALF",
            "MAG": "HAA", "HUL": "HAA"}


def main():
    feat = json.load(open(OUT / "apex_feature.json"))
    base = json.load(open(OUT / "apex_baseline_frontier.json"))
    qp = feat["quali_pace"]
    tA = feat["apex_speed_q90"]
    tF = feat["frontier_B"]

    print("=" * 70)
    print("HAA RESOLUTION CHECK")
    print("=" * 70)
    teams = sorted(set(tA) & set(tF) & set(qp))
    rankF = sorted(teams, key=lambda t: -tF[t])           # grip: high->low
    rankA = sorted(teams, key=lambda t: -tA[t])           # apex: fast->slow
    rankP = sorted(teams, key=lambda t: qp[t])            # pace: fast->slow
    print(f"{'team':>5} {'gripRk':>7} {'apexRk':>7} {'paceRk':>7}  {'grip':>7} {'apex':>8} {'pace':>7}")
    for t in rankP:
        print(f"{t:>5} {rankF.index(t)+1:>7} {rankA.index(t)+1:>7} {rankP.index(t)+1:>7}  "
              f"{tF[t]:7.3f} {tA[t]:8.4f} {qp[t]:7.3f}")
    print(f"\n  HAA: grip-rank #{rankF.index('HAA')+1}  apex-rank #{rankA.index('HAA')+1}  "
          f"pace-rank #{rankP.index('HAA')+1}")
    print(f"  -> apex-speed {'RESOLVES' if rankA.index('HAA') > rankF.index('HAA') else 'does NOT resolve'} "
          f"the HAA paradox (moves HAA toward its slow pace rank)")

    # HAA vs RBR apex-speed-at-radius at matched radius bins (raw, from npz)
    d = np.load(NPZ, allow_pickle=True)
    car = d["car"]; v = d["v_apex"].astype(float); R = d["R_apex"].astype(float)
    print("\n" + "=" * 70)
    print("HAA vs RBR raw apex-speed at MATCHED radius bins (km/h, season-pooled)")
    print("=" * 70)
    edges = [20, 40, 70, 120, 200, 400]
    print(f"  {'R bin (m)':>14}  {'RBR vapex':>10} {'HAA vapex':>10}  {'d(RBR-HAA)':>11}")
    for lo, hi in zip(edges[:-1], edges[1:]):
        def stat(team_cars):
            m = np.isin(car, team_cars) & (R >= lo) & (R < hi) & np.isfinite(v)
            if m.sum() < 10:
                return None, 0
            return float(np.median(v[m]) * 3.6), int(m.sum())
        vr, nr = stat(["VER", "PER"])
        vh, nh = stat(["MAG", "HUL"])
        if vr is None or vh is None:
            print(f"  {lo:>5}-{hi:<5}m   thin")
            continue
        print(f"  {lo:>5}-{hi:<5}m    {vr:10.1f} {vh:10.1f}  {vr-vh:+11.1f}  "
              f"(n {nr}/{nh})")

    _plot(feat)


def _plot(feat):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    qp = feat["quali_pace"]
    tA = feat["apex_speed_q90"]; tF = feat["frontier_B"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, (tf, name, hi) in zip(axes, [(tF, "frontier-g B (grip ceiling)", True),
                                         (tA, "apex-speed @ radius (90th)", True)]):
        teams = sorted(set(tf) & set(qp))
        x = [tf[t] for t in teams]; y = [qp[t] for t in teams]
        ax.scatter(x, y, s=40)
        for t in teams:
            col = "red" if t == "HAA" else ("navy" if t == "RBR" else "black")
            ax.annotate(t, (tf[t], qp[t]), fontsize=9, color=col)
        r = np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1]
        ax.set_xlabel(name); ax.set_ylabel("quali gap-to-median (s, lower=faster)")
        ax.set_title(f"{name}\nSpearman r={r:+.2f}")
        ax.grid(alpha=0.3)
        ax.invert_yaxis()  # faster (more negative) at top
    fig.suptitle("Cornering capability vs quali pace — frontier-g vs apex-speed")
    fig.tight_layout()
    png = OUT / "apex_vs_pace.png"
    fig.savefig(png, dpi=110)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
