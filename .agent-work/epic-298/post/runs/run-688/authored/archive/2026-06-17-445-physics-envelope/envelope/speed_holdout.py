"""Does Matern-7/2 (differentiable accel) reconstruct the SPEED trace better? (#445)

The right arbiter (per human): hold out SPEED observations, not position. Speed between
speed-posts is the time-integral of (tangential) acceleration, so held-out speed
prediction is DIRECTLY sensitive to the acceleration model — and speed is the clean
channel (sig 0.49 m/s) vs the ~meter-noisy position channel.

Hold out every Kth speed obs; fit on ALL positions + remaining speeds; inject held-out
speed times as zero-info query nodes so the RTS bridges them two-sided; score predictive
speed RMSE + NLL. 5/2 vs 7/2, ell swept per order + matched-ell (pure order effect).

If 7/2 predicts held-out speed BETTER, differentiable accel recovers real between-post
structure (human's hypothesis supported). If it ties/loses, accel sits below the floor
and the extra regularity is just a smoother prior (the catch).
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
ELLS = [0.5, 1.0, 1.5, 2.0, 3.0, 4.5]
HOLD = 4
MATCH_ELL = 1.5
LAPS = [(1, "Bahrain", ["VER", "HAM", "LEC", "RUS"]),
        (17, "Japan", ["VER", "HAM", "LEC", "RUS"])]


def flying_laps(q, car, min_n=150, max_per_car=2):
    runs = GI.H.driver_runs(q, car); out = []
    for ls, le in GI.flying_windows(q, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        tp = np.asarray(run["tp"], float); X = np.asarray(run["X"], float); Y = np.asarray(run["Y"], float)
        tc = np.asarray(run["tc"], float); V = np.asarray(run["V"], float)
        mp = (tp >= ls) & (tp <= le); mc = (tc >= ls) & (tc <= le)
        if mp.sum() >= min_n and mc.sum() >= min_n:
            out.append((tp[mp], X[mp], Y[mp], tc[mc], V[mc]))
    out.sort(key=lambda L: -len(L[3]))
    return out[:max_per_car]


def heldout_speed(lap, order, ell, hold=HOLD):
    tp, X, Y, tc, V = lap
    nc = len(tc)
    if nc < 60:
        return None
    test = np.arange(2, nc, hold); train = np.setdiff1d(np.arange(nc), test)
    sm = MaternSmoother(ell, SF, SIG_POS, DELTA, order=order, iters=2)
    sm.fit(tp, X, Y, tc[train], V[train], query_times=tc[test] + DELTA)
    pv, _ = sm.speed_predvar(tc[test] + DELTA)
    pred = sm.speed_at(tc[test] + DELTA)
    pv = np.clip(pv, 1e-6, None)
    r = V[test] - pred
    nll = 0.5 * (r * r / pv + np.log(2 * np.pi * pv))
    return float(np.sqrt(np.mean(r * r))), float(np.mean(nll))


def acc_p99(lap, order, ell):
    tp, X, Y, tc, V = lap
    sm = MaternSmoother(ell, SF, SIG_POS, DELTA, order=order, iters=2).fit(tp, X, Y, tc, V)
    ax, ay = sm.acc_at(tp)
    return float(np.percentile(np.hypot(ax, ay) / 9.81, 99))


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
    print(f"{len(laps)} flying laps (median {int(np.median([len(L[3]) for _, L in laps]))} speed samples)\n")

    print("=" * 76)
    print("HELD-OUT SPEED (hold every 4th speed; all positions kept) — the acc-sensitive test")
    print("=" * 76)
    agg = {3: {}, 4: {}}
    for order in (3, 4):
        for ell in ELLS:
            rs, ns = [], []
            for _, L in laps:
                res = heldout_speed(L, order, ell)
                if res:
                    rs.append(res[0]); ns.append(res[1])
            if rs:
                agg[order][ell] = (np.mean(rs), np.mean(ns))
    for order, lbl in ((3, "Matern-5/2 (a NOT differentiable)"), (4, "Matern-7/2 (a differentiable)")):
        print(f"\n  {lbl}:")
        print(f"    {'ell':>5} {'speed_RMSE(m/s)':>16} {'speed_NLL':>11}")
        for ell in ELLS:
            if ell in agg[order]:
                rmse, nll = agg[order][ell]
                print(f"    {ell:>5.1f} {rmse:>16.4f} {nll:>11.3f}")
    b3 = min(agg[3], key=lambda e: agg[3][e][0]); b4 = min(agg[4], key=lambda e: agg[4][e][0])
    print("\n  BEST speed-RMSE of each:")
    print(f"    5/2: ell={b3}  RMSE={agg[3][b3][0]:.4f} m/s")
    print(f"    7/2: ell={b4}  RMSE={agg[4][b4][0]:.4f} m/s   "
          f"Δ={agg[4][b4][0]-agg[3][b3][0]:+.4f} ({(agg[4][b4][0]-agg[3][b3][0])/agg[3][b3][0]*100:+.1f}%)")
    print(f"\n  Sanity floor: speed sensor sigma = 0.49 m/s (irreducible). Δ vs that scale tells")
    print(f"  whether the order matters relative to the noise the human flagged.")

    print("\n" + "=" * 76)
    print(f"MATCHED ell={MATCH_ELL} (pure order effect)")
    print("=" * 76)
    r3, n3 = agg[3][MATCH_ELL]; r4, n4 = agg[4][MATCH_ELL]
    a3 = np.mean([acc_p99(L, 3, MATCH_ELL) for _, L in laps])
    a4 = np.mean([acc_p99(L, 4, MATCH_ELL) for _, L in laps])
    print(f"  held-out speed RMSE: 5/2 {r3:.4f}   7/2 {r4:.4f} m/s   Δ {r4-r3:+.4f}")
    print(f"  acc |a| p99 (g):     5/2 {a3:6.2f}   7/2 {a4:6.2f}   (physical ~5g)")
    print("\n  READ: 7/2 wins only if speed RMSE drops MORE than noise. If RMSE ties but 7/2's")
    print("  acc p99 is far more physical, the speed data still can't see the order -> prior.")


if __name__ == "__main__":
    main()
