"""Season braking frontier with honest covariance σ (#445). Per team per race:
season_brake2.json {round: {team: [A_b, B_b, σ_Ab, σ_Bb, corr_AB, n_pts, vlo_kmh]}} (A_b,B_b in g)."""
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

from ribbon_reeval import load_session, G_CONST, OUT  # noqa: E402
from long_constraints import long_accel  # noqa: E402
from brake_frontier import fit_brake_cov  # noqa: E402
from season_cda_collect import TEAMS  # noqa: E402

CACHE = OUT / "season_brake2.json"


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    store = {}; t0 = time.time()
    for r in range(1, 23):
        try:
            q = load_session(2023, r, "Q")
        except Exception:
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rec = {}
        for team, cars in TEAMS.items():
            try:
                va, aa, th, bk = long_accel(q, cars)
            except Exception:
                continue
            brk = (bk > 0.5) & (aa < 0)
            if brk.sum() < 25:
                continue
            res = fit_brake_cov(va[brk], -aa[brk] / G_CONST)
            if res is None or not (0.5 < res["Ab"] < 5.0):
                continue
            rec[team] = [round(res["Ab"], 4), round(res["Bb"], 7), round(res["sA"], 4),
                         round(res["sB"], 7), round(res["corrAB"], 3), res["n_pts"],
                         round(res["vlo_kmh"], 0)]
        store[nm] = rec
        log(f"round {r:>2} {nm:16s} {len(rec)} teams")
    CACHE.write_text(json.dumps(store, indent=2))
    log(f"wrote {CACHE.name} ({len(store)} rounds) elapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
