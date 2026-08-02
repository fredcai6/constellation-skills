"""Validate the honest obs model on real data: additive floor + speed-scaled
timing + Student-t robustness, vs the current Gaussian isotropic fit.

Metric that matters (the whole 7/2 / apex-curvature motivation): spurious
acceleration spikes.  A single along-track timing glitch injects a fake
acceleration; the Student-t model should down-weight it and tame the peak |a|
without flattening the real cornering accel.

Usage: py probe_robust_model.py [year] [gp] [session] [driver]
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp
from src.preprocessing.trajectory.smoother import StintSmoother

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
GP = sys.argv[2] if len(sys.argv) > 2 else 'Italy'
SESS = sys.argv[3] if len(sys.argv) > 3 else 'Q'
DRV = sys.argv[4] if len(sys.argv) > 4 else 'VER'

print(f"Loading {DRV} {GP} {YEAR} {SESS}...")
q = load_session(YEAR, GP, SESS); num = driver_num(q, DRV)
laps = q.laps.pick_drivers(DRV); valid = laps[laps['LapTime'].notna()]
fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
t0 = float(fast['LapStartTime'].total_seconds()); t1 = float(fast['Time'].total_seconds())
pos_d, spd_d = driver_streams(q, num); PAD = 2.0
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc, V = spd_d['t'][mc], spd_d['V'][mc]

delta, _ = session_offset([(tp, X, Y, tc, V)])
hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
ell, sf, sig_iso = hp['ell'], hp['sf'], hp['sig_pos']
print(f"Isotropic HPs: ell={ell:.2f} sig_pos={sig_iso:.2f} delta={delta:.3f}")

# Additive model: floor = measured cross floor (tight), timing sig_t ~47ms.
FLOOR, SIG_T, NU = 0.9, 0.047, 4.0
G = 9.81
inlap = (tp >= t0) & (tp <= t1)

def amax(ss):
    ax, ay = ss.acc_at(tp[inlap])
    a = np.hypot(ax, ay) / G
    return float(np.percentile(a, 99)), float(a.max())

iso = StintSmoother(ell, sf, sig_iso, delta, iters=4, order=4).fit(tp, X, Y, tc, V)
add = StintSmoother(ell, sf, FLOOR, delta, iters=4, order=4, sig_t_along=SIG_T).fit(tp, X, Y, tc, V)
rob = StintSmoother(ell, sf, FLOOR, delta, iters=6, order=4, sig_t_along=SIG_T, nu=NU).fit(tp, X, Y, tc, V)

print(f"\n{'model':<22} {'p99 |a|(g)':>11} {'max |a|(g)':>11}")
for name, ss in [("Gaussian isotropic", iso), ("additive floor+timing", add), ("  + Student-t (nu=4)", rob)]:
    p99, mx = amax(ss)
    print(f"{name:<22} {p99:>11.1f} {mx:>11.1f}")

w = rob._w_obs[rob.kind == 0]
print(f"\nStudent-t down-weighting (position obs, n={len(w)}):")
print(f"  weight min={w.min():.2f}  median={np.median(w):.2f}  "
      f"frac w<0.5 = {100*np.mean(w < 0.5):.0f}%  frac w<0.2 = {100*np.mean(w < 0.2):.0f}%")
print("\nDone.")
