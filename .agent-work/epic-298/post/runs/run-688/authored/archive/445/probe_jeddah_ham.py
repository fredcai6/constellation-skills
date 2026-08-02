"""Diagnose the one non-physical cell: HAM Jeddah 2023 Q (NS p99 ~10 g).

Where does the high acceleration come from -- a single glitch sample or a region?
Was it down-weighted by the Student-t?  Is it v^2-amplified at high speed?  Did
the curvature driver over-roughen a fast kink?
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_nonstationary,
)
G = 9.81; PAD = 2.0
q = load_session(2023, 'Saudi Arabia', 'Q'); num = driver_num(q, 'HAM')
laps = q.laps.pick_drivers('HAM'); valid = laps[laps['LapTime'].notna()]
fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
t0 = float(fast['LapStartTime'].total_seconds()); t1 = float(fast['Time'].total_seconds())
pos_d, spd_d = driver_streams(q, num)
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc, V = spd_d['t'][mc], spd_d['V'][mc]
delta, _ = session_offset([(tp, X, Y, tc, V)])
hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
ns, info = fit_smoother_nonstationary(hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V, order=4, base_ell=6.0)
print(f"HAM Jeddah Q: floor={info['sig_floor']:.2f} sig_t={info['sig_t_along']*1000:.0f}ms nu={info['nu']:.1f}")

inlap = (tp >= t0) & (tp <= t1)
ti = tp[inlap]
ax, ay = ns.acc_at(ti); ag = np.hypot(ax, ay) / G
vx, vy = ns.vel_at(ti); spd = np.hypot(vx, vy)
# distance along lap
dist = np.concatenate([[0], np.cumsum(0.5*(spd[1:]+spd[:-1])*np.diff(ti))])
n = len(ag); e = max(int(0.05*n), 2)
interior = np.zeros(n, bool); interior[e:n-e] = True
print(f"\naccel profile: p99={np.percentile(ag[interior],99):.1f}g max={ag[interior].max():.1f}g "
      f"| samples >7g: {int(np.sum(ag[interior]>7))}, >9g: {int(np.sum(ag[interior]>9))}")

# Student-t weights on position obs, mapped to inlap times
wpos = ns._w_obs[ns.kind == 0]
tpos = ns.ts[ns.kind == 0]
# r(t) profile
r_drv = info['r_drv']; t_knots = np.linspace(float(tp[0]), float(tp[-1]), len(r_drv))

print(f"\ntop high-accel interior samples:")
print(f"{'t-t0(s)':>8} {'dist(m)':>8} {'a(g)':>6} {'v(km/h)':>8} {'r@t':>6} {'min_w_near':>11}")
idx = np.argsort(ag * interior)[::-1][:8]
for i in sorted(idx):
    tt = ti[i]
    r_here = float(np.interp(tt, t_knots, r_drv))
    near = np.abs(tpos - tt) < 0.5
    minw = float(wpos[near].min()) if near.any() else float('nan')
    print(f"{tt-t0:>8.1f} {dist[i]:>8.0f} {ag[i]:>6.1f} {spd[i]*3.6:>8.0f} {r_here:>6.1f} {minw:>11.2f}")

print(f"\nweights: {int(np.sum(wpos<0.5))}/{len(wpos)} pos obs <0.5, min={wpos.min():.2f}")
print(f"r(t): max={r_drv.max():.1f}, frac at cap(>=11.5)={100*np.mean(r_drv>=11.5):.0f}%")
print("\nDone.")
