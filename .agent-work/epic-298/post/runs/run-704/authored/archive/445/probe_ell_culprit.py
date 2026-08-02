"""Is the unphysical acceleration on noisy cars driven by a SHORT calibrated ell
(the chi^2 objective is blind to acceleration) rather than the obs-noise model?

For HAM/NOR (chatter) vs VER (clean) at Monza: report the calibrated ell and the
interior p99 |a|, then REFIT with ell forced to VER's 4.5 and re-measure.  If
forcing a longer ell tames the acceleration, ell (not the obs noise) is the cause.
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_anisotropic_speedscaled,
)
G = 9.81; PAD = 2.0
q = load_session(2023, 'Italy', 'Q')

def p99a(ss, inlap):
    ax, ay = ss.acc_at(inlap)
    ai = np.hypot(ax, ay) / G
    n = len(ai); e = max(int(0.05 * n), 2)
    return float(np.percentile(ai[e:n - e], 99))

print(f"{'drv':>4} {'ell_cal':>8} {'p99@cal':>8} {'p99@ell4.5':>11} {'floor':>6} {'sig_t':>6}")
for drv in ['VER', 'HAM', 'NOR', 'ALO', 'PER']:
    num = driver_num(q, drv)
    laps = q.laps.pick_drivers(drv); valid = laps[laps['LapTime'].notna()]
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    t0 = float(fast['LapStartTime'].total_seconds()); t1 = float(fast['Time'].total_seconds())
    pos_d, spd_d = driver_streams(q, num)
    mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
    mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
    tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
    tc, V = spd_d['t'][mc], spd_d['V'][mc]
    inlap = tp[(tp >= t0) & (tp <= t1)]
    delta, _ = session_offset([(tp, X, Y, tc, V)])
    hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
    ss_cal, info = fit_smoother_anisotropic_speedscaled(
        hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, nu='auto')
    ss_long, _ = fit_smoother_anisotropic_speedscaled(
        4.5, hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, nu='auto')
    print(f"{drv:>4} {hp['ell']:>8.2f} {p99a(ss_cal, inlap):>8.1f} "
          f"{p99a(ss_long, inlap):>11.1f} {info['sig_floor']:>6.2f} {info['sig_t_along']*1000:>6.0f}")
print("\nDone.")
