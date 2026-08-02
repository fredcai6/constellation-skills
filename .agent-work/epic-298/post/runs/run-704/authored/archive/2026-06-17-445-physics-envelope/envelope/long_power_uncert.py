"""Power as a feature WITH uncertainty (#445). Per car: P across low-DF races + within-race
bootstrap → mean ± σ. Which power differences clear the noise? Engine pooling sharpens it.
3% in F1 is ~several tenths/lap — worth carrying even as a soft signal."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session, MASS, RHO  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402

TEAMS = {"RBR": ["VER", "PER"], "ATR": ["TSU", "DEV", "RIC", "LAW"],
         "MERC": ["HAM", "RUS"], "MCL": ["NOR", "PIA"], "AMR": ["ALO", "STR"],
         "WIL": ["ALB", "SAR"], "FER": ["LEC", "SAI"], "ALF": ["BOT", "ZHO"],
         "HAA": ["MAG", "HUL"], "ALP": ["GAS", "OCO"]}
ENGINE = {t: e for e, ts in {"Honda": ["RBR", "ATR"],
          "Mercedes": ["MERC", "MCL", "AMR", "WIL"], "Ferrari": ["FER", "ALF", "HAA"],
          "Renault": ["ALP"]}.items() for t in ts}
ROUNDS = [14, 12, 4, 2, 21]
RNG = np.random.default_rng(7)


def fitP(v, a):
    vb, ab = [], []
    for lo in np.arange(20, 100, 6):
        m = (v >= lo) & (v < lo + 6)
        if m.sum() >= 8:
            vb.append(v[m].mean()); ab.append(np.quantile(a[m], 0.90))
    if len(vb) < 4:
        return None, None
    vb, ab = np.array(vb), np.array(ab)
    X = np.column_stack([1 / (MASS * vb), -0.5 * RHO * vb ** 2 / MASS])
    (P, CdA), *_ = np.linalg.lstsq(X, ab, rcond=None)
    return P, CdA


def boot_sigma(v, a, n=25):
    ps = []
    for _ in range(n):
        idx = RNG.integers(0, len(v), len(v))
        P, _ = fitP(v[idx], a[idx])
        if P and 300e3 < P < 1000e3:
            ps.append(P)
    return np.std(ps) / 1e3 if len(ps) > 3 else np.nan


def main():
    per = {t: {"P": [], "sfit": []} for t in TEAMS}
    for rnd in ROUNDS:
        try:
            q = load_session(2023, rnd, "Q")
        except Exception:
            continue
        for t, cars in TEAMS.items():
            v, a, _ = throttle_av(q, cars)
            if len(v) < 80:
                continue
            P, CdA = fitP(v, a)
            if P and 300e3 < P < 1000e3:
                per[t]["P"].append(P / 1e3); per[t]["sfit"].append(boot_sigma(v, a))
        print(f"round {rnd} done")

    rows = []
    for t in TEAMS:
        ps = per[t]["P"]
        if len(ps) >= 3:
            mean = np.mean(ps); sem = np.std(ps, ddof=1) / np.sqrt(len(ps))
            rows.append((t, ENGINE[t], mean, sem, np.nanmean(per[t]["sfit"]), len(ps)))

    print("\n" + "=" * 70)
    print("PER-CAR POWER ± uncertainty (kW). σ_between = race-to-race (deployment/track);")
    print("σ_fit = within-race bootstrap. SEM = σ_between/√n.")
    print("=" * 70)
    print(f"  {'team':>5} {'engine':>9} {'P(kW)':>7} {'±SEM':>6} {'σ_fit':>6} {'n':>3}")
    for t, e, m, sem, sfit, n in sorted(rows, key=lambda r: -r[2]):
        print(f"  {t:>5} {e:>9} {m:>7.0f} {sem:>6.1f} {sfit:>6.1f} {n:>3}")

    # engine pooling
    print("\n  ENGINE means (pooled teams, SEM shrinks with n_teams):")
    eng_stats = {}
    for eng in ["Mercedes", "Ferrari", "Honda", "Renault"]:
        ms = [r[2] for r in rows if r[1] == eng]
        if ms:
            mean = np.mean(ms); sem = (np.std(ms, ddof=1) / np.sqrt(len(ms))) if len(ms) > 1 else rows[0][3]
            eng_stats[eng] = (mean, sem)
            print(f"    {eng:>9}: {mean:.0f} ± {sem:.1f} kW  (n_teams={len(ms)})")
    # significance: best vs worst engine, and the spread vs noise
    if "Mercedes" in eng_stats and "Renault" in eng_stats:
        d = eng_stats["Mercedes"][0] - eng_stats["Renault"][0]
        se = np.hypot(eng_stats["Mercedes"][1], eng_stats["Renault"][1])
        print(f"\n  Mercedes − Renault = {d:.0f} kW  ({d/eng_stats['Renault'][0]*100:.1f}%)  z≈{d/se:.1f}")
    allm = [r[2] for r in rows]
    print(f"  grid power spread: {max(allm)-min(allm):.0f} kW ({(max(allm)-min(allm))/np.mean(allm)*100:.1f}%), "
          f"typical per-car SEM {np.median([r[3] for r in rows]):.1f} kW")
    print(f"  ≈ {(max(allm)-min(allm))/np.median([r[3] for r in rows]):.1f} SEM across the grid — "
          f"extremes resolvable, neighbours not. Carry P as a soft prior (mean±σ).")


if __name__ == "__main__":
    main()
