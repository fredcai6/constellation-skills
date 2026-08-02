"""Adaptive-jump test (#445): does the jump let the season filter FOLLOW a mid-season
upgrade where a fixed-q0 filter over-smooths it?

McLaren ran a big aero upgrade mid-2023 (Austria, ~R9) — its downforce deviation δ should
step UP. Run the recursive-Bayes filter with the jump ON (jump_mult=40) vs OFF (jump_mult=1,
fixed random walk) and compare each car's filtered δ trajectory to the fresh per-race δ.
Jump ON should track the step; OFF should lag toward the season average. Stable cars should
be unaffected (jump shouldn't fire spuriously).
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

from season_prior_bayes import (  # noqa: E402
    load_lateral, estimate_Lr, estimate_sig2_op, run_filter, DRV2TEAM)


def series(recs):
    d = {}
    for idx, rn, rec, A in recs:
        for c, rc in rec.items():
            d.setdefault(c, []).append((idx, rc["fresh"], rc["delta"], rc["jump"]))
    return d


def main():
    per = load_lateral()
    b0, beta = estimate_Lr(per)
    sig2_op = estimate_sig2_op(per, b0, beta)
    q0 = sig2_op * 0.1
    recON, _ = run_filter(per, b0, beta, sig2_op, q0, jump_mult=40.0)
    recOFF, _ = run_filter(per, b0, beta, sig2_op, q0, jump_mult=1.0)
    sON, sOFF = series(recON), series(recOFF)

    print("=" * 70)
    print("McLaren downforce δ trajectory (×1e3): fresh | filt-OFF | filt-ON  [*=jump]")
    print("=" * 70)
    for c in ("NOR", "PIA"):
        if c not in sON:
            continue
        offd = {i: d for i, f, d, j in sOFF[c]}
        print(f"  {c}:")
        for idx, fr, don, jon in sON[c]:
            mark = " *JUMP" if jon else ""
            print(f"    R{idx+1:>2}  fresh {fr*1e3:+6.2f} | off {offd[idx]*1e3:+6.2f} | "
                  f"on {don*1e3:+6.2f}{mark}")

    # pooled: for each car, 1st vs 2nd half fresh shift, and late tracking err ON vs OFF
    print("\n" + "=" * 70)
    print("Per-car: fresh 1st→2nd half SHIFT, late-season tracking err (filt vs fresh level)")
    print("=" * 70)
    print(f"  {'car':>4} {'shift×1e3':>10} {'errOFF×1e3':>11} {'errON×1e3':>10} {'jumped':>7}")
    rows = []
    for c in sON:
        if DRV2TEAM.get(c) is None or len(sON[c]) < 10:
            continue
        fr = np.array([a[1] for a in sON[c]])
        h = len(fr) // 2
        shift = fr[h:].mean() - fr[:h].mean()
        post = fr[-3:].mean()                                  # post-upgrade fresh level
        offd = {i: d for i, f, d, j in sOFF[c]}
        on_late = np.mean([a[2] for a in sON[c][-3:]])
        off_late = np.mean([offd[a[0]] for a in sON[c][-3:]])
        jumped = any(a[3] for a in sON[c])
        rows.append((c, shift, abs(off_late - post), abs(on_late - post), jumped))
    rows.sort(key=lambda r: -abs(r[1]))
    for c, sh, eo, en, jp in rows:
        print(f"  {c:>4} {sh*1e3:>+10.3f} {eo*1e3:>11.3f} {en*1e3:>10.3f} {str(jp):>7}")

    up = [r for r in rows if abs(r[1]) > np.percentile([abs(r[1]) for r in rows], 70)]
    sta = [r for r in rows if abs(r[1]) <= np.percentile([abs(r[1]) for r in rows], 30)]
    print(f"\n  UPGRADE cars (big shift): mean late-err  OFF {np.mean([r[2] for r in up])*1e3:.3f}  "
          f"ON {np.mean([r[3] for r in up])*1e3:.3f}  (ON<OFF => jump tracks the step)")
    print(f"  STABLE cars (small shift): mean late-err  OFF {np.mean([r[2] for r in sta])*1e3:.3f}  "
          f"ON {np.mean([r[3] for r in sta])*1e3:.3f}  (≈ => no spurious jumps)")


if __name__ == "__main__":
    main()
