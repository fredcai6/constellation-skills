"""G1 NoneType root-cause probe.

The 3 OLD-store NoneType cases (Bahrain ALO/HAM, Canada HUL) now return ok on
current code because PR #548 added windows= flying-lap calibration AND guarded
the None return (calibration.py:898-902 raises typed no_accel_samples instead of
letting hp["ell"] subscript None at the old line 861).

This probe reproduces the EXACT None-producing condition faithfully: it replays
the OLD full-span code path (calibrate_session_hp WITHOUT windows=) on these
sessions and shows fit_stint_hp returns None -> which the pre-#548 code
subscripted at calibration.py:861. On current code the same condition now raises
the typed ValueError 'no_accel_samples' at the same call site (the guard #543
added), proving (a) the None origin and (b) the fix. We also confirm WITH
windows= the fit succeeds (why current main returns ok).
"""
import traceback
import numpy as np
import pandas as pd

from src.physics.session_fit import load_quali_session, _FLY_FRACTION
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span
from src.preprocessing.trajectory.calibration import (
    calibrate_session_hp, fit_stint_hp, session_offset,
)

CASES = [("Bahrain", "ALO"), ("Bahrain", "HAM"), ("Canada", "HUL")]
YEAR, SES = 2023, "Q"


def build_inputs(session, driver):
    num = driver_num(session, driver)
    pos_d, spd_d = driver_streams(session, num)
    valid = session.laps.pick_drivers(driver)
    valid = valid[valid["LapTime"].notna()]
    valid = valid[valid["LapTime"].dt.total_seconds() > 50]
    best_s = float(valid["LapTime"].dt.total_seconds().min())
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    flying = valid[valid["LapTime"].dt.total_seconds() <= _FLY_FRACTION * best_s]
    st0, st1, _ = stint_span(session, driver, int(fast["Stint"]), pad=2.0)
    mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
    mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
    flying_windows = [
        (float(lap["LapStartTime"].total_seconds()), float(lap["Time"].total_seconds()))
        for _, lap in flying.iterrows()
        if lap["LapStartTime"] is not pd.NaT and lap["Time"] is not pd.NaT
    ]
    return pos_d, spd_d, mp, mc, st0, st1, flying_windows


def main():
    sess_cache = {}
    for gp, drv in CASES:
        print(f"\n########## {gp} {drv} ##########", flush=True)
        if gp not in sess_cache:
            sess_cache[gp] = load_quali_session(YEAR, gp, SES)
        session, rho, _ = sess_cache[gp]
        pos_d, spd_d, mp, mc, st0, st1, fly_w = build_inputs(session, drv)
        n_pos = int(mp.sum())
        n_spd = int(mc.sum())
        print(f"stint window [st0={st0:.1f}, st1={st1:.1f}] span={st1-st0:.1f}s "
              f"n_pos_in_window={n_pos} n_spd_in_window={n_spd} "
              f"n_flying_windows={len(fly_w)}", flush=True)

        # 1) Replay OLD full-span path: fit_stint_hp on the stint-window mask,
        #    WITHOUT windows= -> does it return None? (the None producer)
        tp, X, Y = pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp]
        tc, V = spd_d["t"][mc], spd_d["V"][mc]
        delta, _ = session_offset([(tp, X, Y, tc, V)])
        hp_dict = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
        print(f"OLD full-span fit_stint_hp -> {('None' if hp_dict is None else 'dict')}"
              f"  (None => pre-548 line 861 `hp[\"ell\"]` would raise NoneType)", flush=True)

        # 2) Show the EXACT pre-548 failure: subscript None like old line 861.
        if hp_dict is None:
            try:
                _ = hp_dict["ell"]  # reproduces the pre-548 line 861 subscript
            except TypeError:
                print("  -> reproduced OLD NoneType subscript exception:", flush=True)
                traceback.print_exc()

        # 3) Current code WITHOUT windows= (typed guard #543): should raise
        #    'no_accel_samples' at the same call site (calibration.py:898-902).
        try:
            calibrate_session_hp(tp, X, Y, tc, V, order=4)
            print("  current calibrate_session_hp (no windows): SUCCEEDED", flush=True)
        except ValueError as exc:
            print(f"  current calibrate_session_hp (no windows): ValueError {exc!r}", flush=True)

        # 4) Current code WITH windows= (the #548 fix path used by fit_driver):
        try:
            hp = calibrate_session_hp(tp, X, Y, tc, V, order=4,
                                      windows=fly_w if fly_w else None)
            print(f"  current calibrate_session_hp (WITH windows): SUCCEEDED "
                  f"ell={hp.ell:.2f} chi2_pos={hp.chi2_pos:.3f}", flush=True)
        except Exception as exc:
            print(f"  current calibrate_session_hp (WITH windows): {type(exc).__name__} {exc!r}",
                  flush=True)


if __name__ == "__main__":
    main()
