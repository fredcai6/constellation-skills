"""Season-wide JOINT DRS drag fit (#445): per team per race, shared-P fit of CdA_closed + CdA_open
with the honest identifiability σ. Replaces the closed-only anchored fit (which extrapolated drag
where the closed set had no high-speed reach — Mexico). season_drs.json:
  {round: {team: [CdA_c, CdA_o, P_kW, sig_c, sig_o, cond, n_c, n_o, open_vmax_kmh]}}.
"""
import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

from ribbon_reeval import load_session, OUT  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from drs_joint_fit import fit_drs_joint  # noqa: E402
from air_density import air_density  # noqa: E402
from season_cda_collect import TEAMS  # noqa: E402

CACHE = OUT / "season_drs.json"
ROUNDS = list(range(1, 23))


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    store = {}; t0 = time.time()
    for r in ROUNDS:
        try:
            q = load_session(2023, r, "Q")
        except Exception:
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rho = air_density(2023, r, "Q")
        rec = {}
        for team, cars in TEAMS.items():
            v, a, op = throttle_av(q, cars)
            if len(v) < 100 or (~op).sum() < 60:
                continue
            res = fit_drs_joint(v, a, op, rho)
            if res is None:
                continue
            cc = res["CdA_c"]
            if not (0.5 < cc * rho / 1.2 < 3.5):   # density-normalized sanity (configured wing)
                continue
            rec[team] = [round(cc, 4), round(res["CdA_o"], 4), round(res["P"] / 1e3, 1),
                         round(res["s_c"], 4), round(res["s_o"], 4), round(res["cond"], 1),
                         res["n_c"], res["n_o"], round(res["open_vmax_kmh"], 0),
                         round(res["sP"] / 1e3, 2),     # [9] σ_P (kW)
                         round(res["corr_PCc"], 3)]     # [10] P↔CdA_c estimator corr (degeneracy)
        store[nm] = rec
        log(f"round {r:>2} {nm:16s} {len(rec)} teams")
    CACHE.write_text(json.dumps(store, indent=2))
    log(f"wrote {CACHE.name} ({len(store)} rounds) elapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
