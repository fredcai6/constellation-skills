"""5/2 vs 7/2 acceleration test at PER-ORDER CALIBRATED HPs (#445, contamination-free).

The earlier order comparison used hand-tuned HPs (chi2~33) — contaminated. Redo it right:
calibrate EACH order to its own per-channel chi2~=1 (order-3 HPs are already in
calibrated_hp.json; order-4 calibrated here with the same chi2-target grid), then compare
held-out SPEED on ROBUST metrics (median|e|, MAE, glitch%) — the acc-sensitive, clean test.
"""
from __future__ import annotations

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

import grip_iter as GI  # noqa: E402
from matern_smoother import MaternSmoother  # noqa: E402
from src.preprocessing.trajectory.calibration import interleaved  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
HPJSON = OUT / "calibrated_hp.json"
SESS = [(1, "Bahrain"), (11, "Hungarian"), (5, "Miami"), (21, "Las Vegas")]
CARS = ["VER", "HAM", "LEC", "RUS", "NOR", "PIA"]


def _stream(run):
    return (np.asarray(run["tp"], float), np.asarray(run["X"], float), np.asarray(run["Y"], float),
            np.asarray(run["tc"], float), np.asarray(run["V"], float))


def _slice(s, dur=300.0):
    tp, X, Y, tc, V = s
    t0, t1 = tp.min(), tp.max()
    if t1 - t0 > dur:
        c = 0.5 * (t0 + t1); a, b = c - dur / 2, c + dur / 2
        mp = (tp >= a) & (tp <= b); mc = (tc >= a - 1) & (tc <= b + 1)
        return tp[mp], X[mp], Y[mp], tc[mc], V[mc]
    return s


def eval_hp(order, ell, sf, sp, delta, S, trp, trv, hop, hov, iters=3):
    tp, X, Y, tc, V = S
    try:
        sm = MaternSmoother(ell, sf, sp, delta, order=order, iters=iters)
        qt = np.union1d(tp[hop], tc[hov] + delta)
        sm.fit(tp[trp], X[trp], Y[trp], tc[trv], V[trv], query_times=qt)
        pvX, pvY = sm.pos_predvar(tp[hop]); Xh, Yh = sm.pos_at(tp[hop])
        c_pos = float(np.mean(((X[hop] - Xh) ** 2 / pvX + (Y[hop] - Yh) ** 2 / pvY) / 2))
        pvV, sh = sm.speed_predvar(tc[hov] + delta)
        c_spd = float(np.mean((V[hov] - sh) ** 2 / pvV))
    except Exception:
        return None
    if not (np.isfinite(c_pos) and np.isfinite(c_spd) and c_pos > 0 and c_spd > 0):
        return None
    return dict(obj=np.log(c_pos) ** 2 + np.log(c_spd) ** 2, ell=ell, sf=sf, sp=sp,
                c_pos=c_pos, c_spd=c_spd)


def calibrate_order(order, S, delta):
    S = _slice(S)
    trp, hop = interleaved(len(S[0]), 4); trv, hov = interleaved(len(S[3]), 4)
    sf_ref = float(np.std(np.diff(S[1])) + np.std(np.diff(S[2])) + 10.0)
    best = None
    for ell in (1.0, 1.4, 1.8, 2.4, 3.2, 4.5):
        for sf in sf_ref * np.array([0.5, 1.0, 2.0, 4.0]):
            for sp in (0.4, 0.6, 0.9, 1.2, 1.6, 2.1):
                r = eval_hp(order, ell, sf, sp, delta, S, trp, trv, hop, hov)
                if r and (best is None or r["obj"] < best["obj"]):
                    best = r
    if best is None:
        return None
    for sf in (best["sf"] * 0.7, best["sf"], best["sf"] * 1.4):
        for ell in (best["ell"] * 0.8, best["ell"], best["ell"] * 1.25):
            for sp in (best["sp"] * 0.85, best["sp"], best["sp"] * 1.18):
                r = eval_hp(order, ell, sf, sp, delta, S, trp, trv, hop, hov)
                if r and r["obj"] < best["obj"]:
                    best = r
    return best


def flying_laps(q, car, min_n=150, mx=2):
    runs = GI.H.driver_runs(q, car); out = []
    for ls, le in GI.flying_windows(q, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        tp, X, Y, tc, V = _stream(run)
        mp = (tp >= ls) & (tp <= le); mc = (tc >= ls) & (tc <= le)
        if mp.sum() >= min_n and mc.sum() >= min_n:
            out.append((tp[mp], X[mp], Y[mp], tc[mc], V[mc]))
    out.sort(key=lambda L: -len(L[3])); return out[:mx]


def heldout_speed_err(lap, order, ell, sf, sp, delta):
    tp, X, Y, tc, V = lap; nc = len(tc)
    test = np.arange(2, nc, 4); train = np.setdiff1d(np.arange(nc), test)
    sm = MaternSmoother(ell, sf, sp, delta, order=order, iters=2)
    sm.fit(tp, X, Y, tc[train], V[train], query_times=tc[test] + delta)
    return np.abs(V[test] - sm.speed_at(tc[test] + delta))


def main():
    hp = json.loads(HPJSON.read_text())
    err = {3: [], 4: []}
    print("Per-order calibration (chi2-target) + held-out speed:\n")
    print(f"{'session':>12} | {'5/2 ell/sp':>12} {'X2p/X2s':>9} | {'7/2 ell/sp':>12} {'X2p/X2s':>9}")
    for rd, nm in SESS:
        try:
            q = GI.H.load_session(2023, rd, "Q")
        except Exception as e:
            print(f"{nm}: load failed {e}"); continue
        delta = hp[nm]["delta"]
        # calibrate BOTH orders with the IDENTICAL chi2-target procedure (fair)
        runs = GI.H.driver_runs(q, "VER")
        S = _stream(max(runs, key=lambda r: len(r["X"])))
        h3 = calibrate_order(3, S, delta)
        h4 = calibrate_order(4, S, delta)
        if h3 is None or h4 is None:
            print(f"{nm}: cal failed"); continue
        print(f"{nm:>12} | {h3['ell']:.1f}/{h3['sp']:.1f}      {h3['c_pos']:.2f}/{h3['c_spd']:.2f} | "
              f"{h4['ell']:.1f}/{h4['sp']:.1f}      {h4['c_pos']:.2f}/{h4['c_spd']:.2f}")
        for c in CARS:
            for lap in flying_laps(q, c):
                err[3].append(heldout_speed_err(lap, 3, h3["ell"], h3["sf"], h3["sp"], delta))
                err[4].append(heldout_speed_err(lap, 4, h4["ell"], h4["sf"], h4["sp"], delta))

    a3 = np.concatenate(err[3]); a4 = np.concatenate(err[4])
    print("\n" + "=" * 70)
    print("HELD-OUT SPEED at per-order CALIBRATED HPs (floor 0.49 m/s; robust metrics)")
    print("=" * 70)
    print(f"{'order':>8} {'median|e|':>10} {'MAE':>8} {'glitch>5':>9} {'n':>7}")
    for o, a in ((3, a3), (4, a4)):
        lbl = "5/2" if o == 3 else "7/2"
        print(f"{lbl:>8} {np.median(a):>10.3f} {a.mean():>8.3f} {100*np.mean(a>5):>8.1f}% {len(a):>7}")
    print(f"\n  Δ(7/2 − 5/2): median {np.median(a4)-np.median(a3):+.3f}  "
          f"MAE {a4.mean()-a3.mean():+.3f}  glitch {100*(np.mean(a4>5)-np.mean(a3>5)):+.1f}pp")
    print("  VERDICT: at honestly-calibrated HPs, does differentiable-a (7/2) still buy the")
    print("  robustness/tail edge, or did clean per-order calibration erase it?")


if __name__ == "__main__":
    main()
