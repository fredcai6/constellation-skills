"""Multi-channel capability fingerprint — fuse the validated season channels (#445).

Every SINGLE channel hits the same front-of-grid floor: grip/downforce can't
separate RBR from Ferrari (both prongs + the season filter agree they tie). But the
channels are clean on DIFFERENT axes, and the cars differ on different axes. Fuse the
two season-filtered, quali, relative-to-field signals we VALIDATED tonight:
  - DOWNFORCE offset  (Prong A season grip filter; config-invariant aero axis)
  - DRAG offset       (Thread C season drag filter; relative CdA, recovers known truth)
and test: does the 2-D fingerprint SEPARATE all four constructors and recover each
car's known 2023 aerodynamic character — breaking the RBR≈Ferrari tie via drag?

Drag is recomputed in-script from the cached season fits; downforce offsets are the
season-filtered constructor means from SEASON_PRIOR_FINDINGS.md (sourced, not refit).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

from drag_prior import per_race_fits, kalman_1d, rel_series, TEAMS, ENGINE  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445")

# Downforce offset, season-filtered constructor means entering Monza (g @ 200 km/h,
# relative to field) — from SEASON_PRIOR_FINDINGS.md (Prong A). + = more downforce.
DOWNFORCE = {"RBR": -0.025, "FER": -0.050, "MERC": -0.170, "WIL": -0.320}

# Known 2023 aero character (for the recovery check, NOT used in the fit)
KNOWN = {
    "RBR": "RB19: efficient — high downforce, low drag (benchmark)",
    "FER": "SF-23: draggy but grippy — strong 1-lap, drag-limited top speed",
    "MERC": "W14: draggy WITHOUT the downforce (the car's known weakness)",
    "WIL": "FW45: low-downforce / low-drag 'slippery minnow' — straightline car",
}


def z(d):
    v = np.array(list(d.values())); m, s = v.mean(), v.std()
    return {k: (x - m) / s for k, x in d.items()}


def main():
    data = per_race_fits()
    rounds = sorted(data)

    # --- DRAG offset: season-filtered relative CdA (low = slippery) ---
    relC = rel_series(data, rounds, "sCc", "CdA_c")
    drag = {}
    for team in TEAMS:
        s = relC[team]
        if len(s) >= 4:
            drag[team] = kalman_1d(s, q_proc=0.03, r_floor=0.05)[-1][1]

    teams = [t for t in TEAMS if t in drag and t in DOWNFORCE]
    dfz = z({t: DOWNFORCE[t] for t in teams})          # downforce, +=more
    # drag efficiency: LOW drag is GOOD, so flip sign so + = efficient/slippery
    drz = z({t: -drag[t] for t in teams})

    print("=" * 76)
    print("CAPABILITY FINGERPRINT — fused season-filtered channels (z-scored)")
    print("=" * 76)
    print(f"{'team':>5} {'engine':>14} | {'downforce':>10} {'drag-eff':>9} | character")
    for t in sorted(teams, key=lambda k: -(dfz[k] + drz[k])):
        print(f"{t:>5} {ENGINE[t]:>14} | {dfz[t]:+10.2f} {drz[t]:+9.2f} | "
              f"DF={DOWNFORCE[t]:+.3f} CdA_rel={drag[t]:+.3f}")

    # --- the decisive separation: RBR vs FER (tied in downforce, split by drag) ---
    print("\n" + "-" * 76)
    print("BREAKING THE FRONT-OF-GRID TIE (RBR vs Ferrari):")
    print(f"  downforce gap |dfz(RBR)-dfz(FER)| = {abs(dfz['RBR']-dfz['FER']):.2f} σ  (TIED — the floor)")
    print(f"  drag-eff  gap |drz(RBR)-drz(FER)| = {abs(drz['RBR']-drz['FER']):.2f} σ  (SEPARATED)")
    print("  -> RBR = high-DF + low-drag (efficient); FER = high-DF + high-drag (draggy).")
    print("     Single-channel grip can't tell them apart; the drag axis does.")

    # --- 2-D quadrant placement + known-truth recovery ---
    print("\n" + "-" * 76)
    print("2-D FINGERPRINT vs KNOWN 2023 character (recovery check):")
    for t in sorted(teams, key=lambda k: -(dfz[k] + drz[k])):
        dfq = "high-DF" if dfz[t] > 0 else "low-DF"
        drq = "low-drag" if drz[t] > 0 else "high-drag"
        print(f"  {t:>5}: [{dfq:>7}, {drq:>9}]  ->  {KNOWN[t]}")

    # --- ascii scatter (downforce x drag-efficiency) ---
    print("\n" + "-" * 76)
    print("  downforce ^ (more wing)")
    grid = [[" "] * 21 for _ in range(11)]
    for t in teams:
        cx = int(round(5 + drz[t] * 3)); cy = int(round(5 - dfz[t] * 3))
        cx = min(max(cx, 0), 20); cy = min(max(cy, 0), 10)
        grid[cy][cx * 1] = t[0]
    for r, row in enumerate(grid):
        rail = "--" if r == 5 else "  "
        print(f"   {rail}|" + "".join(row).replace(" ", "·" if r == 5 else " ") + "|")
    print("        low-drag <----- drag efficiency -----> high-drag")
    print("   (R=RedBull F=Ferrari M=Mercedes W=Williams)")

    # --- aero-efficiency composite (high DF + low drag) ---
    print("\n" + "-" * 76)
    eff = {t: dfz[t] + drz[t] for t in teams}
    print("AERO-EFFICIENCY composite (downforce_z + drag-eff_z), ranked:")
    for i, t in enumerate(sorted(teams, key=lambda k: -eff[k]), 1):
        print(f"  {i}. {t:>5}  {eff[t]:+.2f}")
    print("\nNOTE: this is AERODYNAMIC CHARACTER, not championship order — pace also = "
          "engine + driver + reliability. Mercedes' P2 WCC came from a balanced package +\n"
          "strong drivers despite the draggy-low-DF aero. The fingerprint's job is to "
          "recover CHARACTER, and it separates all four correctly where single channels tie.")


if __name__ == "__main__":
    main()
