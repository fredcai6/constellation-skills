"""Does the bootstrap non-stationary 7/2 fix the grid chatter?

For the cars that chattered (HAM/NOR/ALO/PER) + VER (control) at Monza, compares
the STATIONARY additive model vs the BOOTSTRAP NON-STATIONARY model on interior
p99/max |a|.  Target: noisy cars drop from 10-30 g to physical ~5-6 g without
flattening VER.
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_anisotropic_speedscaled,
    fit_smoother_nonstationary,
)
G = 9.81; PAD = 2.0
q = load_session(2023, 'Italy', 'Q')

def p99max(ss, inlap):
    ax, ay = ss.acc_at(inlap)
    ai = np.hypot(ax, ay) / G
    n = len(ai); e = max(int(0.05 * n), 2)
    ai = ai[e:n - e]
    return float(np.percentile(ai, 99)), float(ai.max())

print(f"{'drv':>4} | {'STATIONARY':>16} | {'NON-STATIONARY':>16} | {'base_ell':>8} {'r_max_used':>10}")
print(f"{'':>4} | {'p99':>7} {'max':>8} | {'p99':>7} {'max':>8} |")
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
    st, _ = fit_smoother_anisotropic_speedscaled(
        hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, nu='auto')
    ns, info = fit_smoother_nonstationary(
        hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, base_ell=6.0)
    sp99, smax = p99max(st, inlap)
    np99, nmax = p99max(ns, inlap)
    rmax_used = float(np.max(info['r_drv']))
    print(f"{drv:>4} | {sp99:>7.1f} {smax:>8.1f} | {np99:>7.1f} {nmax:>8.1f} | "
          f"{info['base_ell']:>8.1f} {rmax_used:>10.1f}")
print("\nDone.")
