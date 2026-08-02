"""General season-prior filter for ANY measured per-car capability parameter (#445).

Generalises season_prior_bayes (built for grip downforce) into a force-agnostic two-stage
Kalman: each race contributes a measurement θ_c with a within-race uncertainty σ_fit; obs noise
R = σ_fit² + σ²_op (operating-point/between-race scatter); thin races (large σ_fit) self-down-
weight so the carried prior dominates. Adaptive jump for real step-changes (upgrades). Works for
grip B, drag CdA, power P, braking A_b/B_b — anything we measure per race with an error bar.

Config-INVARIANT params (A_b mechanical braking, power) use the plain random walk here. Config-
DEPENDENT ones (grip B, drag CdA, braking B_b — wing-level) should first subtract an exogenous
track covariate L_r=b0+β·W_r (as in season_prior_bayes); that extension is noted, not run here.

Demo: braking frontier A_b across 2023 — rescue the thin-fit junk (e.g. WIL Hungary A_b≈0.87).
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


def estimate_sig2_op(per_race):
    """Operating-point variance: robust (MAD) between-race scatter of θ minus the median fit var."""
    series, sigs = {}, []
    for key, meas in per_race:
        for c, (th, sg) in meas.items():
            series.setdefault(c, []).append(th)
            if sg is not None and sg == sg:
                sigs.append(sg)
    resid = []
    for c, vals in series.items():
        if len(vals) >= 6:
            a = np.array(vals); resid += list(a - np.median(a))
    total = (1.4826 * np.median(np.abs(resid))) ** 2 if resid else 1e-6
    vfit = np.median([s * s for s in sigs]) if sigs else 0.0
    return float(max(total - vfit, 1e-9))


class SeasonFilter:
    def __init__(self, q_frac=0.1, P0_scale=4.0, jump_k=9.0, jump_mult=40.0):
        self.q_frac = q_frac; self.P0_scale = P0_scale; self.jump_k = jump_k; self.jump_mult = jump_mult

    def fit(self, per_race):
        """per_race: ordered list of (key, {car: (theta, sigma_fit or None)}).
        Returns traj {car: [(key, raw, sigma, mu_post, P_post, jumped)]}, final state, sig2_op, q0."""
        sig2_op = estimate_sig2_op(per_race)
        q0 = sig2_op * self.q_frac
        big = np.sqrt(sig2_op) * 3.0
        state, traj = {}, {}
        for key, meas in per_race:
            for c, (th, sg) in meas.items():
                sgi = sg if (sg is not None and sg == sg and sg > 0) else big   # missing/bad σ → generous
                R = sgi * sgi + sig2_op
                jumped = False
                if c in state:
                    mu, P = state[c]; Pp = P + q0
                    innov = th - mu; z2 = innov * innov / (Pp + R)
                    if z2 > self.jump_k:
                        Pp = P + q0 * self.jump_mult; jumped = True
                    K = Pp / (Pp + R); mu, P = mu + K * innov, (1.0 - K) * Pp
                    state[c] = (mu, P)
                else:
                    mu, P = th, R * self.P0_scale; state[c] = (mu, P)
                traj.setdefault(c, []).append((key, th, sgi, mu, P, jumped))
        return traj, state, sig2_op, q0


def main():
    cache = OUT / "season_braking.json"
    if not cache.exists():
        print("season_braking.json not ready yet"); return
    d = json.loads(cache.read_text())
    rounds = list(d.keys())
    per_race = [(rn, {t: (d[rn][t][0], d[rn][t][2]) for t in d[rn]}) for rn in rounds]
    traj, state, sig2_op, q0 = SeasonFilter().fit(per_race)
    print(f"braking A_b season filter: σ²_op={sig2_op:.3e} (σ_op={np.sqrt(sig2_op):.2f}g), q0={q0:.3e}\n")

    # headline: rescue thin fits — show raw vs filtered, flag the worst raw outliers
    print(f"  {'team':>5} {'#races':>6} {'raw A_b range':>16} {'final A_b':>9} {'final σ':>8}")
    for t in sorted(traj):
        raws = [r[1] for r in traj[t]]
        mu, P = state[t]
        print(f"  {t:>5} {len(raws):>6} {min(raws):>7.2f}–{max(raws):<7.2f} {mu:>9.2f} {np.sqrt(P):>8.2f}")

    # WIL trace: where the thin junk gets pulled back
    if "WIL" in traj:
        print(f"\n  WIL per-race raw A_b → filtered (thin races rescued):")
        for key, raw, sg, mu, P, jp in traj["WIL"]:
            flag = "  <-- thin/junk rescued" if (raw < 1.2 or raw > 3.2) else ""
            print(f"    {key:>14}: raw {raw:5.2f} (σ{sg:4.2f}) → filt {mu:5.2f} ±{np.sqrt(P):4.2f}{flag}")


if __name__ == "__main__":
    main()
