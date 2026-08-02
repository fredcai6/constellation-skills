"""Season-wide braking-frontier measurement (#445): per team per race, fit A_b (mechanical
braking grip, g) + B_b (downforce-braking) with a bootstrap σ. Feeds the general season-prior
filter so thin races (e.g. WIL Hungary, A_b=0.87 junk) borrow strength from the season.
Cache: season_braking.json  {round_name: {team: [A_b, B_b, sigma_Ab, n_pts]}}.
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

from ribbon_reeval import load_session, G_CONST, OUT  # noqa: E402
from long_constraints import long_accel  # noqa: E402
from lap_trace_v5 import fit_brake  # noqa: E402

CACHE = OUT / "season_braking.json"
ROUNDS = list(range(1, 23))
TEAMS = {"RBR": ["VER", "PER"], "ATR": ["TSU", "DEV", "RIC", "LAW"], "MERC": ["HAM", "RUS"],
         "MCL": ["NOR", "PIA"], "AMR": ["ALO", "STR"], "WIL": ["ALB", "SAR"], "FER": ["LEC", "SAI"],
         "ALF": ["BOT", "ZHO"], "HAA": ["MAG", "HUL"], "ALP": ["GAS", "OCO"]}
RNG = np.random.default_rng(11)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    store = {}
    t0 = time.time()
    for r in ROUNDS:
        try:
            q = load_session(2023, r, "Q")
        except Exception as e:
            log(f"round {r}: load fail {e}"); continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rec = {}
        for team, cars in TEAMS.items():
            try:
                va, aa, th, bk = long_accel(q, cars)
            except Exception:
                continue
            brk = (bk > 0.5) & (aa < 0)
            if brk.sum() < 20:
                continue
            vb = va[brk]; db = -aa[brk] / G_CONST
            try:
                Ab, Bb, _, _ = fit_brake(vb, db)
            except Exception:
                continue
            boots = []
            for _ in range(30):
                idx = RNG.integers(0, len(vb), len(vb))
                try:
                    a2, _, _, _ = fit_brake(vb[idx], db[idx])
                    if -2 < a2 < 5:
                        boots.append(a2)
                except Exception:
                    pass
            sAb = float(np.std(boots)) if len(boots) > 5 else np.nan
            rec[team] = [round(Ab, 4), round(Bb, 7), round(sAb, 4) if sAb == sAb else None, int(brk.sum())]
        store[nm] = rec
        log(f"round {r:>2} {nm:16s} {len(rec)} teams")
    CACHE.write_text(json.dumps(store, indent=2))
    log(f"wrote {CACHE.name} ({len(store)} rounds) elapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
