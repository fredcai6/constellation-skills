"""Independent reviewer reproduction for the #495 g1 diagnosis.

Re-runs >=3 claimed already-fixed cases + Saudi Arabia DEV from scratch via the
public seams (load_quali_session + fit_driver). Also independently inspects:
  - DEV's session-wide speed stream emptiness (driver_streams)
  - the calibration.py:879 tc.min() crash origin (direct traceback capture)

Written fresh by the reviewer; does NOT import the implementer's probes.
"""
import sys
import time
import traceback

from src.physics.session_fit import load_quali_session, fit_driver
from src.physics.fit_batch import _list_drivers
from src.preprocessing.trajectory.loaders import driver_num, driver_streams
from src.utils.constants import get_calendar

YEAR = 2023
SES = "Q"

# Sample of claimed already-fixed cases (handoff-named) + the one live bug.
FIXED_SAMPLE = [
    ("Bahrain", "ALO"),       # was NoneType
    ("Japan", "PIA"),         # was interleaved
    ("Azerbaijan", "GAS"),    # was interleaved
    ("Canada", "HUL"),        # extra: was NoneType
]
BUG_CASE = ("Saudi Arabia", "DEV")


def round_of(gp):
    for i, name in enumerate(get_calendar(YEAR), start=1):
        if name == gp:
            return i
    return None


def constructor_of(session, drv):
    for abbr, team in _list_drivers(session):
        if abbr == drv:
            return team
    return "Unknown"


def run_case(session, rho, gp, drv):
    ridx = round_of(gp)
    cons = constructor_of(session, drv)
    t0 = time.time()
    rec = fit_driver(session, drv, year=YEAR, gp_name=gp, round_idx=ridx,
                     session_type=SES, constructor=cons, rho=rho)
    dt = time.time() - t0
    return rec, dt


def main():
    print("=" * 72, flush=True)
    print("PART A — re-run claimed already-fixed cases (expect fit_status=ok)", flush=True)
    print("=" * 72, flush=True)
    sess_cache = {}
    a_results = []
    for gp, drv in FIXED_SAMPLE:
        if gp not in sess_cache:
            sess_cache[gp] = load_quali_session(YEAR, gp, SES)
        session, rho, _rho_fb = sess_cache[gp]
        rec, dt = run_case(session, rho, gp, drv)
        a_results.append((gp, drv, rec.fit_status, rec.error, rec.n_flying_laps,
                          rec.n_samples_used))
        print(f"  [{rec.fit_status}] {gp} {drv}: n_fly={rec.n_flying_laps} "
              f"n_samp={rec.n_samples_used} err={rec.error!r} ({dt:.1f}s)", flush=True)

    print("\n" + "=" * 72, flush=True)
    print("PART B — Saudi Arabia DEV (expect fit_status=error, zero-size array)", flush=True)
    print("=" * 72, flush=True)
    gp, drv = BUG_CASE
    if gp not in sess_cache:
        sess_cache[gp] = load_quali_session(YEAR, gp, SES)
    session, rho, _rho_fb = sess_cache[gp]

    # B1: full public-seam fit_driver (broad-except path -> recorded error)
    rec, dt = run_case(session, rho, gp, drv)
    print(f"  fit_driver: status={rec.fit_status!r} error={rec.error!r} "
          f"n_fly={rec.n_flying_laps} ({dt:.1f}s)", flush=True)

    # B2: independently confirm DEV speed stream empty session-wide
    num = driver_num(session, drv)
    pos_d, spd_d = driver_streams(session, num)
    print(f"  driver_num(DEV)={num}", flush=True)
    print(f"  session-wide pos stream N = {len(pos_d['t'])}", flush=True)
    print(f"  session-wide spd stream N = {len(spd_d['t'])}  "
          f"(EMPTY={len(spd_d['t']) == 0})", flush=True)

    # B3: capture the raw inner traceback at the calibration windows= branch
    print("\n  --- raw inner traceback (direct calibrate_session_hp call) ---", flush=True)
    from src.preprocessing.trajectory.calibration import calibrate_session_hp
    import numpy as np
    # mimic fit_driver's masking: empty spd in window -> empty tc
    try:
        calibrate_session_hp(
            pos_d["t"][:100], pos_d["X"][:100], pos_d["Y"][:100],
            np.array([]), np.array([]), order=4,
            windows=[(0.0, 1e9)],
        )
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)

    print("\n=== A SUMMARY ===", flush=True)
    for gp, drv, st, err, nfly, nsamp in a_results:
        print(f"  {gp:<14}{drv:<5}{st:<10}n_fly={nfly} n_samp={nsamp}", flush=True)
    print("=== B SUMMARY ===", flush=True)
    print(f"  Saudi DEV: status={rec.fit_status!r} error={rec.error!r} "
          f"spd_empty={len(spd_d['t']) == 0}", flush=True)


if __name__ == "__main__":
    main()
