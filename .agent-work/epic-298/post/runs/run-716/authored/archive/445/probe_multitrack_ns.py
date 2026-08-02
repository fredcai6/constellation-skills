"""Multi-track validation of the non-stationary 7/2 model.

For a diverse set of 2023 tracks (street/slow -> fast sweepers) and the clean
control (VER) + cars that chattered at Monza (HAM, NOR), compares interior p99 |a|
for the STATIONARY additive model vs the BOOTSTRAP NON-STATIONARY model.

Questions:
  - Does NS bring p99 |a| to physical (~5-6 g) across ALL track characters?
  - Does the fixed base_ell=6 hold on very twisty (Monaco/Singapore) and very fast
    (Spa/Silverstone/Jeddah) tracks, or does it need to be track-adaptive?
  - Is the clean control (VER) preserved everywhere (no v^2 over-roughening)?
"""
import sys, warnings, logging, traceback
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_anisotropic_speedscaled,
    fit_smoother_nonstationary,
)
G = 9.81; PAD = 2.0
# (gp, short label, character)
TRACKS = [
    ('Monaco', 'Monaco', 'street/slowest'),
    ('Singapore', 'Singapore', 'street/twisty'),
    ('Spain', 'Spain', 'medium/mix'),
    ('Great Britain', 'Silverstone', 'fast sweepers'),
    ('Belgium', 'Spa', 'fast/long'),
    ('Qatar', 'Qatar', 'medium-fast flow'),
    ('Saudi Arabia', 'Jeddah', 'fast street'),
    ('Austria', 'RedBullRing', 'short/medium'),
]
DRIVERS = ['VER', 'HAM', 'NOR']

def p99(ss, inlap):
    ax, ay = ss.acc_at(inlap)
    ai = np.hypot(ax, ay) / G
    n = len(ai); e = max(int(0.05 * n), 2)
    return float(np.percentile(ai[e:n - e], 99))

results = []
print(f"{'track':>12} {'char':>16} {'drv':>4} {'vmax':>5} {'stat_p99':>9} {'ns_p99':>8} {'verdict':>9}")
for gp, label, char in TRACKS:
    try:
        q = load_session(2023, gp, 'Q')
    except Exception as e:
        print(f"{label:>12} {char:>16}  LOAD ERROR: {type(e).__name__}: {e}")
        continue
    for drv in DRIVERS:
        try:
            num = driver_num(q, drv)
            laps = q.laps.pick_drivers(drv); valid = laps[laps['LapTime'].notna()]
            if len(valid) == 0:
                continue
            fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
            t0 = float(fast['LapStartTime'].total_seconds()); t1 = float(fast['Time'].total_seconds())
            pos_d, spd_d = driver_streams(q, num)
            mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
            mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
            tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
            tc, V = spd_d['t'][mc], spd_d['V'][mc]
            if len(tp) < 50 or len(tc) < 50:
                continue
            inlap = tp[(tp >= t0) & (tp <= t1)]
            delta, _ = session_offset([(tp, X, Y, tc, V)])
            hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
            st, _ = fit_smoother_anisotropic_speedscaled(
                hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, nu='auto')
            ns, info = fit_smoother_nonstationary(
                hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, base_ell=6.0)
            sp, npv = p99(st, inlap), p99(ns, inlap)
            vmax = float(np.max(V)) * 3.6
            verdict = 'physical' if npv < 7.0 else ('HIGH' if npv < 12 else 'FAIL')
            results.append((label, drv, sp, npv, verdict))
            print(f"{label:>12} {char:>16} {drv:>4} {vmax:>5.0f} {sp:>9.1f} {npv:>8.1f} {verdict:>9}")
        except Exception as e:
            print(f"{label:>12} {char:>16} {drv:>4}  ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()

print("\n" + "=" * 60)
ns_vals = [r[3] for r in results]
phys = [r for r in results if r[4] == 'physical']
print(f"cells: {len(results)}, physical (ns p99<7g): {len(phys)}, "
      f"HIGH/FAIL: {len(results)-len(phys)}")
print(f"ns p99 |a|: median {np.median(ns_vals):.1f}, max {np.max(ns_vals):.1f} g")
ver = [r for r in results if r[1] == 'VER']
print(f"VER (control): " + ", ".join(f"{r[0]} {r[2]:.1f}->{r[3]:.1f}" for r in ver))
bad = [r for r in results if r[4] != 'physical']
if bad:
    print("NON-physical cells:")
    for r in bad:
        print(f"  {r[0]} {r[1]}: stat {r[2]:.1f} -> ns {r[3]:.1f} g  [{r[4]}]")
print("\nDone.")
