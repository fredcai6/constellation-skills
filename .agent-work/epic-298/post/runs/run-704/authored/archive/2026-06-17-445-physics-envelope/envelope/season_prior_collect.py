"""Collect & cache 2023 quali cornering nodes for the season-prior filter (#445).

ADDITIVE: reuses grip_iter.collect_nodes (quali friction-circle node extractor) but
writes a single compact .npz keyed by (round, car) so the filter can iterate on the
cached cloud without ever re-running the StintSmoother. Collection of 14 races x 8
drivers is the only expensive step; do it ONCE here.

Cache schema (season_prior_nodes.npz):
  rounds : (R,) U-strings   calendar-ordered event names
  cars   : (8,) U-strings   driver abbrevs
  For each (round r, car c) present:
    f"v__{r}__{c}"  : (n,) speed m/s
    f"g__{r}__{c}"  : (n,) friction-circle magnitude (g units)
    f"w__{r}__{c}"  : (n,) circle-fit precision weight
A (r,c) absent from the file => that car had no/too-few usable nodes that weekend.
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
CACHE = OUT / "season_prior_nodes.npz"

# 13 pre-Monza 2023 rounds in calendar order, then Monza (Italy).
ROUNDS = [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami", "Monaco",
    "Spain", "Canada", "Austria", "Great Britain", "Hungary", "Belgium",
    "Netherlands", "Italy",
]
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "ALB", "SAR"]
MIN_NODES = 25


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    store = {}
    t_start = time.time()
    for r in ROUNDS:
        t0 = time.time()
        try:
            q = GI.H.load_session(2023, r, "Q")
        except Exception as e:
            log(f"{r}: LOAD FAILED {e}")
            continue
        counts = []
        for c in CARS:
            try:
                pts = GI.collect_nodes(q, c)
            except Exception as e:
                log(f"  {r}/{c}: {e}")
                continue
            if len(pts) < MIN_NODES:
                counts.append(f"{c}:{len(pts)}*")
                continue
            p = np.array(pts)
            store[f"v__{r}__{c}"] = p[:, 0].astype(np.float32)
            store[f"g__{r}__{c}"] = p[:, 1].astype(np.float32)
            store[f"w__{r}__{c}"] = p[:, 2].astype(np.float32)
            counts.append(f"{c}:{len(pts)}")
        log(f"{r:16s} {time.time()-t0:4.1f}s  " + " ".join(counts))
    store["rounds"] = np.array(ROUNDS)
    store["cars"] = np.array(CARS)
    np.savez_compressed(CACHE, **store)
    log(f"wrote {CACHE}  ({len(store)-2} clouds)  elapsed {time.time()-t_start:.0f}s")


if __name__ == "__main__":
    main()
