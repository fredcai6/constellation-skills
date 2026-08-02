"""Does Matern-7/2 (differentiable acceleration) beat 5/2? (#445 acceleration poke)

Falsifiable arbiter: HELD-OUT POSITION NLL. Hold out every 4th position sample, fit on
the rest (+ all speeds), inject the held-out times as zero-info query nodes so the RTS
bridges them EXACTLY (two-sided), and score the predictive density of the held-out
observations. ell is tuned per order (fair: best-of-each), sf/sig fixed.

If 7/2 lowers held-out NLL, the data SUPPORTS differentiable acceleration. If it doesn't
(but 7/2 still reports a tighter, prettier acc), that's the human's catch confirmed: the
extra regularity is unfalsifiable prior and a sits below the noise floor.

Secondary (at each order's best ell): acc posterior sigma + acc-magnitude p99 -> shows
what 7/2 DOES to acceleration even if the data doesn't back it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import grip_iter as GI  # noqa: E402
from matern_smoother import MaternSmoother  # noqa: E402

SF, SIG_POS, DELTA = 100.0, 0.3, 0.06
ELLS = [1.0, 1.5, 2.0, 3.0, 4.5, 6.0]
HOLD = 4
MATCH_ELL = 2.0    # production ell, for the pure order comparison
LAPS = [(1, "Bahrain", ["VER", "HAM", "LEC", "RUS"]),
        (17, "Japan", ["VER", "HAM", "LEC", "RUS"])]


def flying_laps(q, car, min_n=200, max_per_car=2):
    """Clean SINGLE flying laps (raw pos+speed inside each flying window) — no
    pit/slow/gap contamination (driver_runs returns whole multi-lap stints)."""
    runs = GI.H.driver_runs(q, car)
    out = []
    for ls, le in GI.flying_windows(q, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        tp = np.asarray(run["tp"], float); X = np.asarray(run["X"], float); Y = np.asarray(run["Y"], float)
        tc = np.asarray(run["tc"], float); V = np.asarray(run["V"], float)
        mp = (tp >= ls) & (tp <= le); mc = (tc >= ls) & (tc <= le)
        if mp.sum() >= min_n and mc.sum() >= min_n and np.diff(tp[mp]).max() < 0.5:
            out.append((tp[mp], X[mp], Y[mp], tc[mc], V[mc]))
    out.sort(key=lambda L: -len(L[0]))
    return out[:max_per_car]


def heldout_nll(lap, order, ell, hold=HOLD):
    tp, X, Y, tc, V = lap
    n = len(tp)
    if n < 60:
        return None
    test = np.arange(0, n, hold); train = np.setdiff1d(np.arange(n), test)
    sm = MaternSmoother(ell, SF, SIG_POS, DELTA, order=order, iters=2)
    sm.fit(tp[train], X[train], Y[train], tc, V, query_times=tp[test])
    px, py = sm.pos_at(tp[test]); vx, vy = sm.pos_predvar(tp[test])
    vx = np.clip(vx, 1e-6, None); vy = np.clip(vy, 1e-6, None)
    rx = X[test] - px; ry = Y[test] - py
    nll = 0.5 * (rx * rx / vx + np.log(2 * np.pi * vx) + ry * ry / vy + np.log(2 * np.pi * vy))
    rmse = np.sqrt(np.mean(rx * rx + ry * ry))
    return float(np.mean(nll)), float(rmse)


def acc_profile(lap, order, ell):
    tp, X, Y, tc, V = lap
    sm = MaternSmoother(ell, SF, SIG_POS, DELTA, order=order, iters=2).fit(tp, X, Y, tc, V)
    ax, ay = sm.acc_at(tp); amag = np.hypot(ax, ay) / 9.81
    _, P = sm._state_at(tp)
    sig = np.sqrt(np.clip(P[:, sm.iAX, sm.iAX], 0, None)) / 9.81
    return float(np.percentile(amag, 99)), float(np.mean(sig))


def main():
    laps = []
    for rd, nm, cars in LAPS:
        try:
            q = GI.H.load_session(2023, rd, "Q")
        except Exception as e:
            print(f"{nm}: load failed {e}"); continue
        for c in cars:
            for L in flying_laps(q, c):
                laps.append((f"{nm}/{c}", L))
    print(f"{len(laps)} clean flying laps "
          f"(median {int(np.median([len(L[0]) for _, L in laps]))} pos samples)\n")

    print("=" * 78)
    print("HELD-OUT POSITION (hold every 4th pos; speeds kept); ell swept per order")
    print("RMSE is the robust arbiter (NLL is gameable by variance inflation)")
    print("=" * 78)
    agg = {3: {}, 4: {}}
    for order in (3, 4):
        for ell in ELLS:
            nlls, rmses = [], []
            for _, L in laps:
                res = heldout_nll(L, order, ell)
                if res:
                    nlls.append(res[0]); rmses.append(res[1])
            if nlls:
                agg[order][ell] = (np.mean(nlls), np.mean(rmses))
    for order, lbl in ((3, "Matern-5/2 (a NOT differentiable)"), (4, "Matern-7/2 (a differentiable)")):
        print(f"\n  {lbl}:")
        print(f"    {'ell':>5} {'heldout_RMSE(mm)':>17} {'heldout_NLL':>12}")
        for ell in ELLS:
            if ell in agg[order]:
                nll, rmse = agg[order][ell]
                print(f"    {ell:>5.1f} {rmse*1000:>17.2f} {nll:>12.3f}")
    b3 = min(agg[3], key=lambda e: agg[3][e][1]); b4 = min(agg[4], key=lambda e: agg[4][e][1])
    n3, r3 = agg[3][b3]; n4, r4 = agg[4][b4]
    print("\n  BEST-RMSE of each:")
    print(f"    5/2: ell={b3}  RMSE={r3*1000:.2f}mm")
    print(f"    7/2: ell={b4}  RMSE={r4*1000:.2f}mm   Δ={(r4-r3)*1000:+.2f}mm "
          f"({(r4-r3)/r3*100:+.1f}%)")

    print("\n" + "=" * 78)
    print(f"MATCHED ell={MATCH_ELL} (pure order effect — same smoothing scale)")
    print("=" * 78)
    rm3, rm4 = agg[3][MATCH_ELL][1], agg[4][MATCH_ELL][1]
    print(f"  held-out RMSE: 5/2 {rm3*1000:.2f}mm   7/2 {rm4*1000:.2f}mm   "
          f"Δ {(rm4-rm3)*1000:+.2f}mm")
    p3 = [acc_profile(L, 3, MATCH_ELL) for _, L in laps]
    p4 = [acc_profile(L, 4, MATCH_ELL) for _, L in laps]
    print(f"  acc |a| p99 (g):     5/2 {np.mean([p[0] for p in p3]):6.2f}   "
          f"7/2 {np.mean([p[0] for p in p4]):6.2f}   (physical peak ~5g)")
    print(f"  acc posterior σ (g): 5/2 {np.mean([p[1] for p in p3]):6.2f}   "
          f"7/2 {np.mean([p[1] for p in p4]):6.2f}")
    print("\n  VERDICT: if 7/2 held-out RMSE ≈ 5/2 but acc is far more physical (lower p99,")
    print("  smaller σ), the data can't ARBITRATE the order — 7/2's smoother a is a better")
    print("  PRIOR, not better-recovered signal. That is the human's catch, quantified.")


if __name__ == "__main__":
    main()
