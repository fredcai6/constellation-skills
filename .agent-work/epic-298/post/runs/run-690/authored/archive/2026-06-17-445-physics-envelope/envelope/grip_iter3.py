"""Per-driver grip frontier: is downforce B a CAR property? (epic #445).

The one car-difference that survived (RBR-high / Merc-low cornering downforce) was
fit per CONSTRUCTOR (teammates pooled). Test it's the car, not the driver's line:
fit B per DRIVER (quali, one global mechanical A), then decompose the spread —
WITHIN-team (teammate gap) vs BETWEEN-team (car gap). If between >> within, B is a
car property and the de-confound (#2) is worth building. If teammates disagree as
much as cars, "downforce" is really driver/line and we stop calling it capability.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import grip_iter as GI  # noqa: E402
from grip_iter import GSAT, TEAMS, TRACKS, gat  # noqa: E402

MIN_NODES = 25


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def fit_global_keyed(clouds, tau=0.92, band=0.4, iters=30):
    """One global A across all keys, per-key downforce B."""
    keys = list(clouds)
    v = np.concatenate([clouds[k][0] for k in keys])
    g = np.concatenate([clouds[k][1] for k in keys])
    w0 = np.concatenate([clouds[k][2] for k in keys])
    kid = np.concatenate([np.full(len(clouds[k][0]), j) for j, k in enumerate(keys)])
    A = 1.6; B = np.full(len(keys), 0.0015)
    for _ in range(iters):
        Gv = np.minimum(A + B[kid] * v * v, GSAT)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        sel = (g < GSAT - 0.2) & (w > 1e-9)
        X = np.zeros((int(sel.sum()), 1 + len(keys))); X[:, 0] = 1.0
        vs = v[sel]; ks = kid[sel]
        for j in range(len(keys)):
            X[ks == j, 1 + j] = vs[ks == j] ** 2
        coef = GI.wls(X, g[sel], w[sel])
        A = float(np.clip(coef[0], 0.8, 3.2))
        B = np.clip(coef[1:], 1e-4, 6e-3)
    return A, {keys[j]: float(B[j]) for j in range(len(keys))}


def main():
    clouds = {}                       # (track, team, driver) -> cloud
    for name, gp in TRACKS.items():
        log(f"collecting {name} quali per-driver ...")
        q = GI.H.load_session(2023, gp, "Q")
        for team, drvs in TEAMS.items():
            for car in drvs:
                try:
                    pts = GI.collect_nodes(q, car)
                except Exception as e:
                    log(f"  {name}/{car}: {e}"); continue
                if len(pts) < MIN_NODES:
                    log(f"  {name}/{team}/{car}: thin ({len(pts)}), skip"); continue
                p = np.array(pts)
                clouds[(name, team, car)] = (p[:, 0], p[:, 1], p[:, 2])

    A, B = fit_global_keyed(clouds)
    log(f"global A = {A:.2f} g")

    # report per track, grouped by team, with teammate gap
    print("\n" + "=" * 70)
    print(f"PER-DRIVER downforce B (global A={A:.2f}g) and G@140 km/h, by team")
    print("=" * 70)
    within, between_rows = [], []
    for name in TRACKS:
        print(f"\n--- {name} ---")
        team_means = {}
        for team, drvs in TEAMS.items():
            bs = []
            for car in drvs:
                k = (name, team, car)
                if k in B:
                    g140 = gat(A, B[k], 140)
                    print(f"  {team:>5} {car:>4}: B={B[k]*1e3:5.2f}  G140={g140:5.2f}")
                    bs.append((car, B[k]))
            if len(bs) == 2:
                gap = abs(bs[0][1] - bs[1][1]) * 1e3
                within.append(gap)
                print(f"        -> teammate gap {gap:.2f}  (within-team)")
            if bs:
                team_means[team] = np.mean([b for _, b in bs]) * 1e3
        if len(team_means) >= 2:
            vals = np.array(list(team_means.values()))
            between_rows.append(vals.max() - vals.min())
            print(f"  between-team B range: {vals.max()-vals.min():.2f}  "
                  f"({', '.join(f'{t}={m:.2f}' for t, m in team_means.items())})")

    # verdict
    print("\n" + "=" * 70)
    print("VERDICT: is downforce B a CAR property?")
    print("=" * 70)
    wmean = float(np.mean(within)) if within else float("nan")
    bmean = float(np.mean(between_rows)) if between_rows else float("nan")
    print(f"  mean WITHIN-team teammate gap : {wmean:.2f}  (1e-3, n={len(within)} pairs)")
    print(f"  mean BETWEEN-team car range   : {bmean:.2f}  (1e-3, n={len(between_rows)} tracks)")
    if wmean == wmean and bmean == bmean:
        ratio = bmean / wmean if wmean > 0 else float("inf")
        print(f"  between/within ratio = {ratio:.2f}")
        if ratio >= 1.5:
            print("  -> CAR property: cars differ more than teammates. #2 justified.")
        elif ratio <= 0.8:
            print("  -> DRIVER/line: teammates differ as much as cars. 'downforce' is not capability.")
        else:
            print("  -> AMBIGUOUS: car and teammate spreads comparable; signal marginal.")

    # is the surviving RBR-high / MERC-low ordering driver-consistent?
    print("\n  RBR vs MERC per-driver G@140 (the surviving signal):")
    for name in TRACKS:
        cells = []
        for team in ("RBR", "MERC"):
            for car in TEAMS[team]:
                k = (name, team, car)
                if k in B:
                    cells.append(f"{car}={gat(A, B[k], 140):.2f}")
        print(f"    {name:>8}: " + "  ".join(cells))


if __name__ == "__main__":
    main()
