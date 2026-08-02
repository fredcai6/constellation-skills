"""Cross-car power recovery: does full-throttle a(v) → P cluster by ENGINE? (#445)

If the full-throttle-frontier power (which is stable across tracks for RBR) DISCRIMINATES
between cars and same-engine teams cluster, then engine power is recoverable — overturning
the documented "P↔CdA degeneracy / power not recoverable" null. Fit (P, CdA) per team on the
low-drag high-top-speed tracks (cleanest P/CdA separation), median over races, group by engine.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session, OUT  # noqa: E402
from long_throttle_probe import throttle_av, frontier_fit  # noqa: E402

TEAMS = {"RBR": ["VER", "PER"], "ATR": ["TSU", "DEV", "RIC", "LAW"],
         "MERC": ["HAM", "RUS"], "MCL": ["NOR", "PIA"], "AMR": ["ALO", "STR"],
         "WIL": ["ALB", "SAR"], "FER": ["LEC", "SAI"], "ALF": ["BOT", "ZHO"],
         "HAA": ["MAG", "HUL"], "ALP": ["GAS", "OCO"]}
ENGINE = {t: e for e, ts in {
    "Honda": ["RBR", "ATR"], "Mercedes": ["MERC", "MCL", "AMR", "WIL"],
    "Ferrari": ["FER", "ALF", "HAA"], "Renault": ["ALP"]}.items() for t in ts}
ROUNDS = [14, 12, 4, 2, 21]   # Monza, Spa, Baku, Jeddah, Las Vegas (low-DF, high top speed)


def main():
    acc = {t: {"P": [], "CdA": [], "top": []} for t in TEAMS}
    for rnd in ROUNDS:
        try:
            q = load_session(2023, rnd, "Q")
        except Exception as e:
            print(f"round {rnd}: load failed {e}"); continue
        for team, cars in TEAMS.items():
            v, a, op = throttle_av(q, cars)
            if len(v) < 80:
                continue
            ff = frontier_fit(v, a)
            if ff is None:
                continue
            P, CdA, _, _ = ff
            if 300e3 < P < 1000e3 and 0.5 < CdA < 2.5:   # sane guard
                acc[team]["P"].append(P); acc[team]["CdA"].append(CdA); acc[team]["top"].append(v.max() * 3.6)
        print(f"round {rnd} done")

    rows = []
    for t in TEAMS:
        if len(acc[t]["P"]) >= 2:
            rows.append((t, ENGINE.get(t, "?"), np.median(acc[t]["P"]) / 1e3,
                         np.median(acc[t]["CdA"]), np.median(acc[t]["top"]), len(acc[t]["P"])))
    print("\n" + "=" * 64)
    print("POWER BY ENGINE (P = full-throttle wheel power incl. ERS, kW)")
    print("=" * 64)
    print(f"  {'engine':>9} {'team':>5} {'P(kW)':>7} {'CdA':>6} {'top':>6} {'nrace':>6}")
    for eng in ["Honda", "Mercedes", "Ferrari", "Renault"]:
        grp = [r for r in rows if r[1] == eng]
        for t, e, P, CdA, top, n in sorted(grp, key=lambda r: -r[2]):
            print(f"  {e:>9} {t:>5} {P:>7.0f} {CdA:>6.2f} {top:>6.0f} {n:>6}")
        if len(grp) >= 2:
            ps = [r[2] for r in grp]
            print(f"  {'':>9} {'(mean':>5} {np.mean(ps):>7.0f}  std {np.std(ps):.0f})")

    # clustering: within-engine vs between-engine P spread
    allP = [r[2] for r in rows]
    win = []
    for eng in ["Honda", "Mercedes", "Ferrari"]:
        ps = [r[2] for r in rows if r[1] == eng]
        if len(ps) >= 2:
            win += list(np.array(ps) - np.mean(ps))
    print(f"\n  within-engine P std  = {np.std(win):.0f} kW")
    print(f"  overall team P std   = {np.std(allP):.0f} kW")
    print(f"  -> engines cluster if within << overall (power recoverable & discriminating)")
    # engine-mean ranking
    print("\n  engine-mean P:")
    for eng in ["Honda", "Mercedes", "Ferrari", "Renault"]:
        ps = [r[2] for r in rows if r[1] == eng]
        if ps:
            print(f"    {eng:>9}: {np.mean(ps):.0f} kW  (n_teams={len(ps)})")


if __name__ == "__main__":
    main()
