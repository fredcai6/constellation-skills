"""G1 stream-overlap quantification for the 15 interleaved n=0 cases.

For each: n_pos and n_spd in the stint window, the window span, whether the speed
stream is empty session-wide, and whether pos/speed overlap in time. This
establishes recover (overlap present -> windows= path recovers) vs skip-clean
(no overlap / empty speed stream -> typed skip).
"""
import numpy as np
import pandas as pd

from src.physics.session_fit import load_quali_session, _FLY_FRACTION
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span

# the 15 interleaved n=0 cases
CASES = [
    ("Japan", "PIA"), ("Japan", "NOR"), ("Japan", "LEC"), ("Japan", "SAI"),
    ("Japan", "MAG"), ("Netherlands", "SAR"), ("Mexico", "ZHO"),
    ("Brazil", "PIA"), ("Las Vegas", "BOT"), ("Abu Dhabi", "VER"),
    ("Saudi Arabia", "DEV"), ("Azerbaijan", "GAS"), ("Azerbaijan", "DEV"),
    ("Miami", "BOT"), ("Canada", "ALB"),
]
YEAR, SES = 2023, "Q"


def overlap_span(a_t, b_t):
    if len(a_t) == 0 or len(b_t) == 0:
        return 0.0, (None, None)
    lo = max(a_t.min(), b_t.min())
    hi = min(a_t.max(), b_t.max())
    return (hi - lo if hi > lo else 0.0), (lo, hi)


def main():
    sess_cache = {}
    print(f"{'GP':<14}{'DRV':<5}{'POS_N':<7}{'SPD_N':<7}{'SPD_EMPTY':<10}"
          f"{'WIN_SPAN':<10}{'POS_IN_W':<9}{'SPD_IN_W':<9}{'OVERLAP_S':<10}")
    rows = []
    for gp, drv in CASES:
        if gp not in sess_cache:
            sess_cache[gp] = load_quali_session(YEAR, gp, SES)
        session, rho, _ = sess_cache[gp]
        num = driver_num(session, drv)
        pos_d, spd_d = driver_streams(session, num)
        spd_empty = len(spd_d["t"]) == 0
        valid = session.laps.pick_drivers(drv)
        valid = valid[valid["LapTime"].notna()]
        valid = valid[valid["LapTime"].dt.total_seconds() > 50]
        if valid.empty:
            print(f"{gp:<14}{drv:<5} NO VALID LAPS")
            continue
        best_s = float(valid["LapTime"].dt.total_seconds().min())
        fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
        st0, st1, _ = stint_span(session, drv, int(fast["Stint"]), pad=2.0)
        mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
        mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
        win_span = st1 - st0
        n_pos_w = int(mp.sum())
        n_spd_w = int(mc.sum())
        ov, _ = overlap_span(pos_d["t"][mp], spd_d["t"][mc])
        print(f"{gp:<14}{drv:<5}{len(pos_d['t']):<7}{len(spd_d['t']):<7}"
              f"{str(spd_empty):<10}{win_span:<10.1f}{n_pos_w:<9}{n_spd_w:<9}{ov:<10.1f}")
        rows.append((gp, drv, len(pos_d['t']), len(spd_d['t']), spd_empty,
                     win_span, n_pos_w, n_spd_w, ov))

    print("\n=== recover-vs-skip read ===")
    for gp, drv, pn, sn, se, ws, pw, sw, ov in rows:
        if se or sw == 0:
            verdict = "SKIP-CLEAN (speed stream empty in window / session)"
        elif pw > 0 and sw > 0 and ov > 0:
            verdict = "RECOVER (pos+speed overlap present)"
        else:
            verdict = "INVESTIGATE"
        print(f"  {gp:<14}{drv:<5} -> {verdict}  (pos_in_w={pw} spd_in_w={sw} overlap={ov:.1f}s)")


if __name__ == "__main__":
    main()
