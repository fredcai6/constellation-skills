"""How much OVERHANG is enough?  Fit a padded window [lap-W, lap+W] (clipped to the
stint so we never cross a pit stop), keep only the lap interior, and sweep W to
find where the lap-edge acceleration stabilises.

NOT the whole stint -- just enough context that the lap's edges have real data
beyond them.  The asymptote (full available stint context) is the reference.
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

def lap_accel(ss, fly):
    ax, ay = ss.acc_at(fly); a = np.hypot(ax, ay) / G
    return float(np.percentile(a, 99)), float(a.max())

def run(gp, drv, Ws):
    q = load_session(2023, gp, 'Q'); num = driver_num(q, drv)
    laps = q.laps.pick_drivers(drv); valid = laps[laps['LapTime'].notna()]
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    lt0 = float(fast['LapStartTime'].total_seconds()); lt1 = float(fast['Time'].total_seconds())
    stint_no = int(fast['Stint'])
    st0, st1, _ = stint_span(q, drv, stint_no, pad=2.0)
    pos_d, spd_d = driver_streams(q, num)
    print(f"\n{drv} {gp} (lap {lt1-lt0:.0f}s, stint {st0:.0f}-{st1:.0f}s avail "
          f"overhang ~{lt0-st0:.0f}/{st1-lt1:.0f}s):")
    print(f"   {'W(s)':>6} {'win(s)':>7} {'lap_p99':>8} {'lap_max':>8}")
    for W in Ws:
        w0 = max(lt0 - W, st0); w1 = min(lt1 + W, st1)
        mp = (pos_d['t'] >= w0) & (pos_d['t'] <= w1)
        mc = (spd_d['t'] >= w0) & (spd_d['t'] <= w1)
        tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
        tc, V = spd_d['t'][mc], spd_d['V'][mc]
        if len(tp) < 50:
            continue
        d, _ = session_offset([(tp, X, Y, tc, V)])
        hp = fit_stint_hp(tp, X, Y, tc, V, delta=d, iters=3, order=4)
        ns, _ = fit_smoother_nonstationary(hp['ell'], hp['sf'], hp['sig_pos'], d, tp, X, Y, tc, V, order=4, base_ell=6.0)
        fly = tp[(tp >= lt0) & (tp <= lt1)]
        p99, mx = lap_accel(ns, fly)
        label = f"{W:.0f}" if W < 900 else "FULL"
        print(f"   {label:>6} {w1-w0:>7.0f} {p99:>8.1f} {mx:>8.1f}")

run('Saudi Arabia', 'HAM', [2, 4, 6, 8, 12, 16, 9999])
run('Italy', 'VER', [2, 6, 12, 9999])
print("\nDone.")
