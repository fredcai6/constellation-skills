"""The modeling loss in the drag model (#445).

Current model: CdA[track][team] ≈ per-team-constant + common-track-shift  (purely ADDITIVE).
The surviving log-relational residuals are real team×track structure (lever-arm refuted: Mexico has
the 2nd-highest top speed yet the biggest residual). Physical candidate for the missing term:
AERO EFFICIENCY — drag-per-downforce differs by team, so at high downforce-DEMAND tracks efficient
cars trim less wing (slippery) and inefficient ones read draggy.

Test: regress each team's residual on the EXOGENOUS track downforce trait W_r (circuits.yaml, 1–5).
A consistent per-team SLOPE b_c = aero efficiency (b_c<0 ⇒ drag grows slower with DF demand ⇒ more
efficient). Variance the per-team-slope model explains = the recoverable modeling loss. Shuffle-W
baseline shows whether it beats chance.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from network_rating import network_solve, build_edges  # noqa: E402
from src.evo_predictor.data_adapter._config import GP_TO_CIRCUIT  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CIRCUITS = yaml.safe_load(Path("C:/Programs/f1Brainz/src/evo_predictor/circuits.yaml").read_text(encoding="utf-8"))
RNG = np.random.default_rng(7)

# season_cda round name (EventName-stripped) -> circuits.yaml key
NAME_FIX = {"Saudi Arabian": "saudi_arabia", "Australian": "australia", "Mexico City": "mexico",
            "United States": "united_states", "Las Vegas": "las_vegas", "São Paulo": "brazil",
            "Abu Dhabi": "abu_dhabi"}


def circuit_key(name):
    if name in NAME_FIX:
        return NAME_FIX[name]
    return GP_TO_CIRCUIT.get(name)


def downforce_demand(name, year=2023):
    key = circuit_key(name)
    ent = CIRCUITS.get(key) if key else None
    if not ent:
        return None
    for y in (year, year - 1, year - 2, 2022, 2019, 2018):
        if y in ent and "downforce" in ent[y]:
            return float(ent[y]["downforce"])
    return None


def log_relationals(season):
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
    return out


def var_explained(per_team_pts, Wc):
    """Fit residual = a_c + b_c·W per team; return pooled R² and slopes."""
    ss_res = ss_tot = 0.0
    slopes = {}
    for t, pts in per_team_pts.items():
        if len(pts) < 6:
            continue
        W = np.array([Wc[rn] for rn, _ in pts]); y = np.array([v for _, v in pts])
        A = np.column_stack([np.ones_like(W), W])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ coef
        ss_res += np.sum((y - pred) ** 2); ss_tot += np.sum((y - y.mean()) ** 2)
        slopes[t] = float(coef[1])
    return 1 - ss_res / ss_tot, slopes


def main():
    season = json.loads((OUT / "season_cda.json").read_text())
    rels = log_relationals(season)

    Wc = {rn: downforce_demand(rn) for rn in rels}
    miss = [rn for rn, w in Wc.items() if w is None]
    if miss:
        print("WARN unresolved downforce demand:", miss)
    Wc = {rn: w for rn, w in Wc.items() if w is not None}

    per_team = {}
    for rn, tr in rels.items():
        if rn not in Wc:
            continue
        for t, v in tr.items():
            per_team.setdefault(t, []).append((rn, v))

    R2, slopes = var_explained(per_team, Wc)

    # shuffle-W null: break the track↔demand link, refit, 200×
    null = []
    rounds = list(Wc); Wvals = np.array([Wc[r] for r in rounds])
    for _ in range(200):
        perm = RNG.permutation(Wvals)
        Wc_s = {r: perm[i] for i, r in enumerate(rounds)}
        null.append(var_explained(per_team, Wc_s)[0])
    null = np.array(null)
    p = float(np.mean(null >= R2))

    print(f"downforce-demand W_r per track (exogenous, circuits.yaml 1–5):")
    for rn in sorted(Wc, key=lambda k: Wc[k]):
        print(f"   {rn:<16} W={Wc[rn]:.0f}")
    print(f"\nper-team-slope model:  pooled R² = {R2:+.3f}   "
          f"(shuffle-W null: mean {null.mean():+.3f}, 95th {np.percentile(null,95):+.3f}, p={p:.3f})")
    print(f"\naero-efficiency slope b_c (residual log-CdA per +1 downforce demand; "
          f"NEGATIVE = drag grows slower with DF = MORE efficient):")
    for t in sorted(slopes, key=lambda k: slopes[k]):
        eff = "efficient" if slopes[t] < 0 else "draggy-scaling"
        print(f"   {t:>4}  b={slopes[t]:+.4f}  ({eff})")


if __name__ == "__main__":
    main()
