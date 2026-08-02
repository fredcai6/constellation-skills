"""G1 root-cause probe for the ONE remaining live error: Saudi Arabia DEV 2023 Q.

Current fit_driver returns error 'zero-size array to reduction operation minimum
which has no identity' (NEW vs old interleaved n=0). It fails in ~0.3s with
n_fly=0 -> before the per-lap loop. We replay the inner chain (bypassing the
broad except via direct calls to the public seams fit_driver itself uses) to get
the RAW traceback and the exact .min()/np.min on an empty array.
"""
import traceback
import numpy as np
import pandas as pd

from src.physics.session_fit import load_quali_session, _FLY_FRACTION
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span
from src.preprocessing.trajectory.calibration import calibrate_session_hp

YEAR, GP, DRV, SES = 2023, "Saudi Arabia", "DEV", "Q"


def main():
    session, rho, _ = load_quali_session(YEAR, GP, SES)
    num = driver_num(session, DRV)
    print(f"driver_num({DRV}) = {num}", flush=True)
    pos_d, spd_d = driver_streams(session, num)
    print(f"pos stream: n={len(pos_d['t'])} "
          f"t=[{pos_d['t'].min():.1f},{pos_d['t'].max():.1f}]" if len(pos_d['t']) else "pos stream EMPTY",
          flush=True)
    print(f"spd stream: n={len(spd_d['t'])} "
          f"t=[{spd_d['t'].min():.1f},{spd_d['t'].max():.1f}]" if len(spd_d['t']) else "spd stream EMPTY",
          flush=True)

    valid = session.laps.pick_drivers(DRV)
    print(f"\nraw laps for {DRV}: {len(valid)}", flush=True)
    cols = ["LapNumber", "Stint", "LapTime", "LapStartTime", "Time"]
    have = [c for c in cols if c in valid.columns]
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(valid[have].to_string(), flush=True)

    valid2 = valid[valid["LapTime"].notna()]
    valid2 = valid2[valid2["LapTime"].dt.total_seconds() > 50]
    print(f"\nvalid laps (LapTime notna & >50s): {len(valid2)}", flush=True)
    if valid2.empty:
        print("valid empty -> would return no_laps (but we got error, so not this path)", flush=True)
        return
    best_s = float(valid2["LapTime"].dt.total_seconds().min())
    fast = valid2.loc[valid2["LapTime"].dt.total_seconds().idxmin()]
    flying = valid2[valid2["LapTime"].dt.total_seconds() <= _FLY_FRACTION * best_s]
    print(f"best_s={best_s:.3f} fast stint={int(fast['Stint'])} n_flying={len(flying)}", flush=True)
    print("flying stints:", sorted(set(int(s) for s in flying['Stint'])), flush=True)

    # stint_span on the fast lap's stint — this is the likely .min() on empty.
    try:
        st0, st1, table = stint_span(session, DRV, int(fast["Stint"]), pad=2.0)
        print(f"\nstint_span(stint={int(fast['Stint'])}) -> st0={st0:.1f} st1={st1:.1f} "
              f"lap_table_rows={len(table)}", flush=True)
        mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
        mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
        print(f"  n_pos_in_window={int(mp.sum())} n_spd_in_window={int(mc.sum())}", flush=True)
    except Exception:
        print("\nstint_span RAISED — RAW TRACEBACK:", flush=True)
        traceback.print_exc()
        # dig into the stint membership
        laps = session.laps.pick_drivers(DRV)
        st = laps[laps["Stint"] == int(fast["Stint"])]
        print(f"  laps with Stint=={int(fast['Stint'])}: {len(st)}", flush=True)
        ls = st["LapStartTime"].dt.total_seconds().to_numpy()
        print(f"  LapStartTime values: {ls}", flush=True)
        return

    # If stint_span survived, run the full calibrate to find the empty-reduction.
    flying_windows = [
        (float(lap["LapStartTime"].total_seconds()), float(lap["Time"].total_seconds()))
        for _, lap in flying.iterrows()
        if lap["LapStartTime"] is not pd.NaT and lap["Time"] is not pd.NaT
    ]
    print(f"\nflying_windows: {flying_windows}", flush=True)
    try:
        hp = calibrate_session_hp(
            pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
            spd_d["t"][mc], spd_d["V"][mc], order=4,
            windows=flying_windows if flying_windows else None,
        )
        print(f"calibrate ok ell={hp.ell}", flush=True)
    except Exception:
        print("calibrate_session_hp RAISED — RAW TRACEBACK:", flush=True)
        traceback.print_exc()


if __name__ == "__main__":
    main()
