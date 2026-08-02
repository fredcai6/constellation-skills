"""Ideal lap with a COVARIANCE-AWARE joint Monte-Carlo uncertainty (#445).

Reapply the session's lessons to the capability ceiling, and (the next-level step) sample force
parameters from their JOINT FIT COVARIANCE, not independent marginals:

  - grip (A,B) drawn from the curve_fit 2×2 covariance. The frontier G(v)=A+B·v² is far better
    determined than A or B alone (intercept↔slope anti-correlate), so a joint draw keeps G(v) TIGHT
    in the measured speed range and only fans out in extrapolation. Independent-marginal draws let A
    and B both wander → G(v) inflates spuriously. This ABATES THE COLLINEARITY IN PRACTICE.
  - cornering and braking driven by the SAME grip draw (friction-circle identity: lateral grip =
    braking grip) — a low-grip draw slows the corner AND weakens braking together.
  - longitudinal scaled by its marginal σ_K only — the ideal lap uses the well-determined net a(v),
    which already sits on the manifold orthogonal to the P↔CdA degeneracy (so no split to respect).

Headline: σ_cov (covariance-aware) vs σ_indep (independent marginals) — the gap is the collinearity
that independent sampling spuriously injects. Real density; physical clips; diverged draws filtered.
"""
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import (load_session, fit_grip_clean, get_apex_nodes, load_cal_nodes, OUT)  # noqa: E402
from ribbon_apex_ideal import apex_curves, TEAMS  # noqa: E402
from ribbon_long_paths import vg_apex  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from ideal_lap_v2 import av_measured, sim, GS, TRACKS  # noqa: E402
from air_density import air_density  # noqa: E402

drs = json.loads((OUT / "season_drs.json").read_text())
GP2RND = {"Italy": "Italian", "Hungary": "Hungarian", "Japan": "Japanese"}
RNG = np.random.default_rng(17)
NMC = 300
SIG_CAP = 0.12
VREF = 35.0          # m/s (126 km/h) — apex speed inside the measured grip range for the cornering tie


def accel_sigma(gp, team):
    rn = GP2RND.get(gp)
    rec = drs.get(rn, {}).get(team) if rn else None
    return min(rec[9] / rec[2], SIG_CAP) if (rec and rec[2] > 0) else 0.05


def run(s, kappa, length, vg, a_meas, vmax, A, B, fa, A0, B0):
    Gs = (lambda v: min(max(A + B * v * v, 0.05), GS))
    am = (lambda v: max(a_meas(v) * fa, 0.0))
    G0 = max(A0 + B0 * VREF * VREF, 1e-3); Gd = max(A + B * VREF * VREF, 1e-3)
    fc = float(np.clip(np.sqrt(Gd / G0), 0.75, 1.25))      # cornering scale from the SAME grip draw
    return sim(s, kappa, length, vg * fc, am, vmax, Gs)


def mc(s, kappa, length, vg, a_meas, vmax, A0, B0, pcov, sa):
    t0 = run(s, kappa, length, vg, a_meas, vmax, A0, B0, 1.0, A0, B0)
    lo, hi = 0.7 * t0, 1.6 * t0
    sA = np.sqrt(max(pcov[0, 0], 0)); sB = np.sqrt(max(pcov[1, 1], 0))
    C = pcov + 1e-12 * np.eye(2)

    def collect(joint_grip):
        ts = []
        for _ in range(NMC):
            if joint_grip:                                   # draw (A,B) from the 2×2 covariance
                dA, dB = RNG.multivariate_normal([0, 0], C)
            else:                                            # independent marginals (ignores cov)
                dA, dB = RNG.normal(0, sA), RNG.normal(0, sB)
            A = float(np.clip(A0 + dA, 0.5, 3.5)); B = float(np.clip(B0 + dB, 1e-4, 6e-3))
            fa = float(np.clip(1 + RNG.normal(0, min(sa, SIG_CAP)), 0.8, 1.2))
            t = run(s, kappa, length, vg, a_meas, vmax, A, B, fa, A0, B0)
            if lo < t < hi:
                ts.append(t)
        return np.array(ts)

    cov = collect(True); ind = collect(False)
    return dict(t0=t0, sd_cov=float(cov.std()), sd_ind=float(ind.std()),
                p5=float(np.percentile(cov, 5)), p95=float(np.percentile(cov, 95)),
                valid=len(cov) / NMC, corrAB=float(pcov[0, 1] / np.sqrt(max(pcov[0, 0] * pcov[1, 1], 1e-30))))


def main():
    beta, alpha, _ = apex_curves()
    cal = load_cal_nodes(); t0 = time.time()
    print(f"{'track':>8}{'team':>5}{'ideal':>8}{'σ_cov':>7}{'σ_indep':>8}{'cov/ind':>8}"
          f"{'[p5':>8}{'p95]':>8}{'corrAB':>8}")
    for name, cfg in TRACKS.items():
        cache = OUT / f"ribbon_clean_{name.lower()}.npz"
        if not cache.exists():
            continue
        d = np.load(cache); s, kappa = d["s"], d["kappa"]
        q = load_session(2023, cfg["gp"], "Q"); rho = air_density(2023, cfg["gp"], "Q")
        for team, cars in TEAMS.items():
            if team not in alpha:
                continue
            vk, gg = get_apex_nodes(cal, cfg["gp"], cars)
            if vk is None or len(vk) < 25:
                continue
            gf = fit_grip_clean(vk, gg, with_cov=True)
            if gf[0] is None:
                continue
            A0_, B0_, _, _, _, pcov = gf
            v, a, _ = throttle_av(q, cars)
            if len(v) < 80:
                continue
            mv = av_measured(v, a, rho)
            if mv is None:
                continue
            vg = vg_apex(kappa, alpha[team], beta)
            a_meas = (lambda vv, K=mv["K"], vm=mv["vmax"]: max(K * (vm ** 3 / max(vv, 1.0) - vv * vv), 0.0))
            r = mc(s, kappa, cfg["length"], vg, a_meas, mv["vmax"], A0_, B0_, pcov,
                   accel_sigma(cfg["gp"], team))
            print(f"{name:>8}{team:>5}{r['t0']:>8.2f}{r['sd_cov']:>7.2f}{r['sd_ind']:>8.2f}"
                  f"{r['sd_cov']/max(r['sd_ind'],1e-9):>8.2f}{r['p5']:>8.2f}{r['p95']:>8.2f}{r['corrAB']:>8.2f}")
    print(f"\nelapsed {time.time()-t0:.0f}s   σ_cov<σ_indep ⇒ joint A,B sampling keeps the grip frontier "
          "on its well-determined manifold (collinearity abated in practice).")


if __name__ == "__main__":
    main()
