"""Confirm the design: calibrate HPs ONCE (on ample data), then fit each lap in a
windowed [lap-W, lap+W] with those FIXED base HPs.  If the per-lap result is then
stable/monotonic in W (no bounce), the non-monotonicity was per-window HP
recalibration, and the clean split is: stable session HPs + windowed local fit.
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import (
    driver_num, driver_streams, load_session, stint_span,
)
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_nonstationary,
)
G = 9.81

def run(gp, drv, Ws):
    q = load_session(2023, gp, 'Q'); num = driver_num(q, drv)
    laps = q.laps.pick_drivers(drv); valid = laps[laps['LapTime'].notna()]
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    lt0 = float(fast['LapStartTime'].total_seconds()); lt1 = float(fast['Time'].total_seconds())
    stint_no = int(fast['Stint'])
    st0, st1, _ = stint_span(q, drv, stint_no, pad=2.0)
    pos_d, spd_d = driver_streams(q, num)
    # delta + HPs calibrated ONCE on the full available stint context
    mp = (pos_d['t'] >= st0) & (pos_d['t'] <= st1)
    mc = (spd_d['t'] >= st0) & (spd_d['t'] <= st1)
    tps, Xs, Ys = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
    tcs, Vs = spd_d['t'][mc], spd_d['V'][mc]
    delta, _ = session_offset([(tps, Xs, Ys, tcs, Vs)])
    HP = fit_stint_hp(tps, Xs, Ys, tcs, Vs, delta=delta, iters=3, order=4)
    print(f"\n{drv} {gp}: fixed HPs ell={HP['ell']:.2f} sig_pos={HP['sig_pos']:.2f} delta={delta:.3f}")
    print(f"   {'W(s)':>6} {'lap_p99':>8} {'lap_max':>8}")
    for W in Ws:
        w0 = max(lt0 - W, st0); w1 = min(lt1 + W, st1)
        mp = (pos_d['t'] >= w0) & (pos_d['t'] <= w1)
        mc = (spd_d['t'] >= w0) & (spd_d['t'] <= w1)
        tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
        tc, V = spd_d['t'][mc], spd_d['V'][mc]
        # FIXED HPs (no per-window recalibration); only the windowed fit + local r(t)
        ns, _ = fit_smoother_nonstationary(HP['ell'], HP['sf'], HP['sig_pos'], delta, tp, X, Y, tc, V, order=4, base_ell=6.0)
        fly = tp[(tp >= lt0) & (tp <= lt1)]
        ax, ay = ns.acc_at(fly); a = np.hypot(ax, ay) / G
        print(f"   {W:>6.0f} {np.percentile(a,99):>8.1f} {a.max():>8.1f}")

run('Saudi Arabia', 'HAM', [2, 4, 6, 8, 12, 16])
run('Italy', 'VER', [2, 6, 12])
print("\nDone.")
