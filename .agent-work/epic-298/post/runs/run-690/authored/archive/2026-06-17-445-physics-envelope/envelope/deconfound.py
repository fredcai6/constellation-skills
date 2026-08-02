"""De-confound car capability using measured compound degradation (#445).

Reframe (user): compound exactness is for MEASUREMENT PROCESSING (clean past
observations), not prediction. Test the payoff: use the measured per-compound
grip degradation to normalize every slow-corner grip back to a FRESH-tyre
equivalent, and check whether that LINKS the stints -> each car's capability
becomes consistent across stints/compounds instead of stepping with tyre state.
If yes, compound info earns its keep. Also reveals: is compound purely
degradation (age), or also a peak-grip LEVEL difference?

Reuses compound_physics.csv (no new smoother runs).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
AGE0 = 3.0  # reference tyre age (laps) to normalize to


def fe_slope(df, yc, groupcols):
    x, y = [], []
    for _, sub in df.groupby(groupcols):
        if len(sub) < 3:
            continue
        a = sub["age"].to_numpy(); yy = sub[yc].to_numpy()
        x.append(a - a.mean()); y.append(yy - yy.mean())
    if not x:
        return np.nan, np.nan
    x = np.concatenate(x); y = np.concatenate(y)
    Sxx = (x * x).sum()
    slope = (x * y).sum() / Sxx
    resid = y - slope * x
    se = np.sqrt((resid * resid).sum() / max(len(x) - 1, 1) / Sxx)
    return slope, se


def main():
    df = pd.read_csv(OUT / "compound_physics.csv")
    df = df.dropna(subset=["age", "grip"])
    print(f"{len(df)} grip observations, compounds {sorted(df['C'].unique())}")

    # per-compound grip degradation (fixed effects car,corner,stint)
    gamma = {}
    for C in sorted(df["C"].unique()):
        sub = df[df["C"] == C]
        if len(sub) < 20:
            continue
        gs, gse = fe_slope(sub, "grip", ["car", "corner", "stint"])
        gamma[C] = (gs, gse)
        print(f"  C{C}: grip degradation {gs:+.4f} ± {gse:.4f} g/lap")

    # normalize each obs to fresh-tyre equivalent: grip + |gamma|*(age - AGE0) added back
    df["grip_norm"] = df.apply(
        lambda r: r["grip"] - gamma.get(r["C"], (0, 0))[0] * (r["age"] - AGE0), axis=1
    )

    # CROSS-STINT consistency per (car, corner): does normalization link the stints?
    raw_spreads, norm_spreads = [], []
    for (car, corner), g in df.groupby(["car", "corner"]):
        means_raw = g.groupby("stint")["grip"].mean()
        means_norm = g.groupby("stint")["grip_norm"].mean()
        if len(means_raw) >= 2:
            raw_spreads.append(means_raw.std())
            norm_spreads.append(means_norm.std())
    raw_spreads = np.array(raw_spreads)
    norm_spreads = np.array(norm_spreads)
    print(f"\n--- cross-stint capability consistency (per car-corner) ---")
    print(f"  median cross-stint spread RAW : {np.median(raw_spreads):.3f} g")
    print(f"  median cross-stint spread NORM: {np.median(norm_spreads):.3f} g")
    print(f"  -> normalization {'TIGHTENS' if np.median(norm_spreads) < np.median(raw_spreads) else 'does NOT tighten'} "
          f"the stints ({100*(1-np.median(norm_spreads)/np.median(raw_spreads)):+.0f}%)")

    # residual COMPOUND-LEVEL after age-normalization: compare normalized grip by
    # compound within (car,corner) -> is there a peak-grip level difference?
    print(f"\n--- residual compound LEVEL after age-normalization (HARD vs MEDIUM) ---")
    diffs = []
    for (car, corner), g in df.groupby(["car", "corner"]):
        mh = g[g["C"] == 1]["grip_norm"].mean()
        mm = g[g["C"] == 2]["grip_norm"].mean()
        if np.isfinite(mh) and np.isfinite(mm):
            diffs.append(mm - mh)   # medium - hard, fresh-equivalent
    diffs = np.array(diffs)
    if len(diffs):
        se = np.std(diffs) / np.sqrt(len(diffs))
        print(f"  fresh-equiv grip MEDIUM - HARD: {np.mean(diffs):+.3f} ± {se:.3f} g "
              f"(n={len(diffs)} corners, {abs(np.mean(diffs))/se:.1f} sigma)")
        print(f"  -> ~0 means compound is PURE degradation (no peak-grip level diff); "
              f"nonzero means a level difference too.")
    _plot(df)


def _plot(df):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    # one illustrative car: per-stint mean grip raw vs normalized
    car = "VER" if "VER" in df["car"].values else df["car"].iloc[0]
    g = df[df["car"] == car]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for label, col, ax in [("raw grip", "grip", ax1), ("fresh-normalized", "grip_norm", ax2)]:
        piv = g.groupby(["stint", "corner"])[col].mean().reset_index()
        for st, sub in piv.groupby("stint"):
            comp = g[g["stint"] == st]["C"].iloc[0]
            cname = {1: "HARD", 2: "MEDIUM", 3: "SOFT"}[comp]
            ax.scatter(sub["corner"], sub[col], label=f"stint {st} ({cname})", s=30)
        ax.set_xlabel("corner id")
        ax.set_title(f"{car}: {label}")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    ax1.set_ylabel("slow-corner grip (g)")
    fig.suptitle(f"{car} Suzuka race — de-confounding links stints (each corner should align across stints)")
    fig.tight_layout()
    png = OUT / "deconfound_ver.png"
    fig.savefig(png, dpi=110)
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
