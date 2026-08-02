"""Real aero vs lever-arm artifact? (#445)

The residual CdA flags survive the density fix and log-space detrend. Two explanations:
  (A) REAL aero: team×track interaction (efficient cars trim less wing at high-DF tracks).
  (B) ARTIFACT: short top-speed lever arm -> CdA weakly constrained -> biased fit.
Discriminator = TOP SPEED per track (the lever-arm metric). If (B), |residual| tracks LOW top speed.
If (A), it does not — it tracks team aero-efficiency × track downforce demand.

Also reports, per track: top speed, mean |residual|, the worst team residual — and the Spearman
between per-track top speed and per-track mean |residual|.
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

from ribbon_reeval import load_session, driver_num  # noqa: E402
from network_rating import network_solve, build_edges  # noqa: E402
from season_cda_collect import TEAMS  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def log_relationals(season):
    """Per (round, team) log-space relational residual rel = (logCdA - rating) - field_median."""
    teams = sorted({t for rec in season.values() for t in rec})
    sl = {rn: {t: [np.log(v[0])] + list(v[1:]) for t, v in rec.items() if v[0] and v[0] > 0}
          for rn, rec in season.items()}
    r, _ = network_solve(build_edges(sl), teams)
    out = {}
    for rn, rec in sl.items():
        present = [t for t in rec if rec[t][1] is not None]
        if len(present) < 5:
            continue
        dev = {t: rec[t][0] - r[t] for t in present}
        common = np.median(list(dev.values()))
        out[rn] = {t: dev[t] - common for t in present}
    return out, r


def top_speed_by_round():
    """99.9th-pct Speed (km/h) across all cars in each 2023 Q session — the lever-arm metric."""
    allcars = sum(TEAMS.values(), [])
    out = {}
    for r in range(1, 23):
        try:
            q = load_session(2023, r, "Q")
        except Exception:
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        speeds = []
        for car in allcars:
            try:
                num = driver_num(q, car)
                speeds.append(q.car_data[num]["Speed"].to_numpy(float))
            except Exception:
                continue
        if speeds:
            out[nm] = float(np.percentile(np.concatenate(speeds), 99.9))
    return out


def main():
    season = json.loads((OUT / "season_cda.json").read_text())
    rels, rating = log_relationals(season)
    tops = top_speed_by_round()

    rows = []
    for rn, tr in rels.items():
        if rn not in tops:
            continue
        absres = {t: abs(v) for t, v in tr.items()}
        worst = max(tr.items(), key=lambda kv: abs(kv[1]))
        rows.append((tops[rn], rn, np.mean(list(absres.values())), worst[0], worst[1]))

    rows.sort()   # by top speed ascending (short lever first)
    print(f'{"round":<16}{"topspeed":>9}{"mean|res|":>10}{"worst team":>12}{"worst res%":>11}')
    for ts, rn, mr, wt, wr in rows:
        print(f"{rn:<16}{ts:>9.0f}{mr:>10.3f}{wt:>12}{(np.exp(wr)-1)*100:>+10.1f}%")

    ts = np.array([r[0] for r in rows]); mr = np.array([r[2] for r in rows])
    def spear(a, b):
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return float(np.corrcoef(ra, rb)[0, 1])
    print(f"\nSpearman(top_speed, mean|residual|) = {spear(ts, mr):+.3f}")
    print("  strongly NEGATIVE => lever-arm artifact (low top speed -> big residual)")
    print("  near ZERO / positive => not explained by top speed -> real team×track structure")


if __name__ == "__main__":
    main()
