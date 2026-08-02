"""Full-grid quali cornering-node collection — all 10 teams x all 22 races (#445).

Extends season_prior_collect.py (which did 14 rounds x 8 drivers) to the WHOLE 2023
grid so the season grip filter + capability fingerprint cover all 10 constructors.
Heavy (StintSmoother per driver-race) but compute is unconstrained tonight.
Cache schema identical to season_prior_nodes.npz; new file season_prior_nodes_full.npz.
"""
from __future__ import annotations

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

import grip_iter as GI  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "season_prior_nodes_full.npz"

ROUNDS = list(range(1, 23))   # all 22 2023 rounds (numeric -> robust event resolution)
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
        "GAS", "OCO", "ALB", "SAR", "TSU", "DEV", "RIC", "LAW", "BOT", "ZHO",
        "MAG", "HUL"]
MIN_NODES = 25


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    store = {}
    rnames = []
    t_start = time.time()
    for r in ROUNDS:
        t0 = time.time()
        try:
            q = GI.H.load_session(2023, r, "Q")
        except Exception as e:
            log(f"round {r}: LOAD FAILED {e}")
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rnames.append(nm)
        n_ok = 0
        for c in CARS:
            try:
                pts = GI.collect_nodes(q, c)
            except Exception:
                continue
            if len(pts) < MIN_NODES:
                continue
            p = np.array(pts)
            store[f"v__{nm}__{c}"] = p[:, 0].astype(np.float32)
            store[f"g__{nm}__{c}"] = p[:, 1].astype(np.float32)
            store[f"w__{nm}__{c}"] = p[:, 2].astype(np.float32)
            n_ok += 1
        log(f"round {r:>2} {nm:16s} {time.time()-t0:5.1f}s  {n_ok} cars")
    store["rounds"] = np.array(rnames)
    store["cars"] = np.array(CARS)
    np.savez_compressed(CACHE, **store)
    log(f"wrote {CACHE}  ({(len(store)-2)//3} clouds)  elapsed {time.time()-t_start:.0f}s")


if __name__ == "__main__":
    main()
