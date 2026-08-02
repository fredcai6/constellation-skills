"""Season-wide DRS-closed CdA (drag) per team per race (#445) — for the pairwise-network rating.
CdA is circuit-specific (wing), so absolute values aren't comparable across tracks, but pairwise
differences CdA_i − CdA_j are ~track-invariant (both teams adjust wing similarly). Cache with a
bootstrap σ. season_cda.json {round: {team: [CdA, sigma, n]}}."""
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

from ribbon_reeval import load_session, MASS, RHO, OUT  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from ideal_lap_v2 import frontier_pts, fit_anchored  # noqa: E402
from air_density import air_density  # noqa: E402

CACHE = OUT / "season_cda.json"
ROUNDS = list(range(1, 23))
TEAMS = {"RBR": ["VER", "PER"], "ATR": ["TSU", "DEV", "RIC", "LAW"], "MERC": ["HAM", "RUS"],
         "MCL": ["NOR", "PIA"], "AMR": ["ALO", "STR"], "WIL": ["ALB", "SAR"], "FER": ["LEC", "SAI"],
         "ALF": ["BOT", "ZHO"], "HAA": ["MAG", "HUL"], "ALP": ["GAS", "OCO"]}
RNG = np.random.default_rng(5)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def cda_fit(v, a, rho=RHO):
    vb, ab = frontier_pts(v, a, 0.90)
    if len(vb) < 4:
        return None
    vmax = np.percentile(v, 99.5)
    K, P, CdA = fit_anchored(vb, ab, vmax, rho)
    return CdA


def main():
    store = {}; t0 = time.time()
    for r in ROUNDS:
        try:
            q = load_session(2023, r, "Q")
        except Exception:
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rho = air_density(2023, r, "Q")   # real per-track density, not fixed 1.2 (Mexico altitude!)
        # Sanity-clamp the DENSITY-NORMALIZED value (reference 1.2) so junk-rejection is identical
        # at every track — CdA scales as 1/rho, so a fixed [0.5,3.0] would wrongly clip high-DF cars
        # at low-density tracks (Mexico ×1.326 pushed max-wing cars past 3.0).
        def sane(c):
            return c is not None and 0.5 < c * rho / 1.2 < 3.0
        rec = {}
        for team, cars in TEAMS.items():
            v, a, op = throttle_av(q, cars)
            m = ~op & (a > -2)            # DRS-closed configured-wing drag
            if m.sum() < 80:
                continue
            cda = cda_fit(v[m], a[m], rho)
            if not sane(cda):
                continue
            boots = []
            for _ in range(25):
                idx = RNG.integers(0, m.sum(), m.sum())
                c2 = cda_fit(v[m][idx], a[m][idx], rho)
                if sane(c2):
                    boots.append(c2)
            sig = float(np.std(boots)) if len(boots) > 5 else np.nan
            rec[team] = [round(float(cda), 4), round(sig, 4) if sig == sig else None, int(m.sum())]
        store[nm] = rec
        log(f"round {r:>2} {nm:16s} {len(rec)} teams")
    CACHE.write_text(json.dumps(store, indent=2))
    log(f"wrote {CACHE.name} ({len(store)} rounds) elapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
