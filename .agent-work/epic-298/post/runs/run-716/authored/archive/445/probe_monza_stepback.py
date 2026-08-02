"""Step back: what does the honest obs model mean for VER at Monza?

Compares the OLD Gaussian isotropic fit (one sig_pos in every direction) with the
NEW robust additive model (isotropic spatial floor + speed-scaled timing along +
Student-t), on VER's fastest 2023 Monza qualifying lap.  Reports the things we
actually use the lap for:
  - how tightly we pin the LATERAL racing line (cross-track posterior sigma)
  - along-track uncertainty (honestly loose at speed: timing jitter)
  - residuals to the raw GPS
  - acceleration peak (apex-curvature cleanliness)
  - glitches caught
  - apex speed + its uncertainty at the slowest corner
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_anisotropic_speedscaled,
)
from src.preprocessing.trajectory.smoother import StintSmoother

q = load_session(2023, 'Italy', 'Q'); num = driver_num(q, 'VER')
laps = q.laps.pick_drivers('VER'); valid = laps[laps['LapTime'].notna()]
fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
t0 = float(fast['LapStartTime'].total_seconds()); t1 = float(fast['Time'].total_seconds())
print(f"VER Monza 2023 Q, fastest lap {fast['LapTime']}  ({t1-t0:.1f} s)")
pos_d, spd_d = driver_streams(q, num); PAD = 2.0
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc, V = spd_d['t'][mc], spd_d['V'][mc]

delta, _ = session_offset([(tp, X, Y, tc, V)])
hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
ell, sf, sig_iso = hp['ell'], hp['sf'], hp['sig_pos']

iso = StintSmoother(ell, sf, sig_iso, delta, iters=4, order=4).fit(tp, X, Y, tc, V)
rob, info = fit_smoother_anisotropic_speedscaled(ell, sf, sig_iso, delta, tp, X, Y, tc, V, order=4, nu='auto')

print("\n--- calibrated obs model ---")
print(f"OLD (Gaussian isotropic): sig_pos = {sig_iso:.2f} m in ALL directions")
print(f"NEW (robust additive):    floor = {info['sig_floor']:.2f} m, "
      f"sig_t = {info['sig_t_along']*1000:.0f} ms, nu = {info['nu']:.1f}")

G = 9.81
inlap = (tp >= t0) & (tp <= t1)
tq = tp[inlap]

def local_frame(ss):
    vx, vy = ss.vel_at(tq); spd = np.hypot(vx, vy)
    ex, ey = vx/spd, vy/spd; nx, ny = -ey, ex
    return spd, ex, ey, nx, ny

def latent_sigma(ss):
    """Posterior position sigma (how well we KNOW the car), projected along/cross."""
    spd, ex, ey, nx, ny = local_frame(ss)
    C = ss.pos_cov2x2(tq)
    c00, c01, c11 = C[:,0,0], C[:,0,1], C[:,1,1]
    s_along = np.sqrt(ex*ex*c00 + 2*ex*ey*c01 + ey*ey*c11)
    s_cross = np.sqrt(nx*nx*c00 + 2*nx*ny*c01 + ny*ny*c11)
    return spd, s_along, s_cross

def resid(ss):
    spd, ex, ey, nx, ny = local_frame(ss)
    Xh, Yh = ss.pos_at(tq); rx, ry = X[inlap]-Xh, Y[inlap]-Yh
    return rx*ex+ry*ey, rx*nx+ry*ny

spd, sa_iso, sc_iso = latent_sigma(iso)
_,   sa_rob, sc_rob = latent_sigma(rob)
print("\n--- how tightly we pin VER's car (posterior position sigma, median) ---")
print(f"               {'along (m)':>10} {'cross/LINE (m)':>14}")
print(f"OLD isotropic  {np.median(sa_iso):>10.2f} {np.median(sc_iso):>14.2f}")
print(f"NEW additive   {np.median(sa_rob):>10.2f} {np.median(sc_rob):>14.2f}")
print(f"  -> lateral racing line pinned {np.median(sc_iso)/np.median(sc_rob):.1f}x tighter")

a_i, c_i = resid(iso); a_r, c_r = resid(rob)
def rms(x): return float(np.sqrt(np.mean(x**2)))
print("\n--- residual to raw GPS (m) ---")
print(f"               {'along RMS':>10} {'cross RMS':>10}")
print(f"OLD isotropic  {rms(a_i):>10.2f} {rms(c_i):>10.2f}")
print(f"NEW additive   {rms(a_r):>10.2f} {rms(c_r):>10.2f}")

def amax(ss):
    ax, ay = ss.acc_at(tq); a = np.hypot(ax, ay)/G
    return float(np.percentile(a, 99)), float(a.max())
print("\n--- acceleration (g) ---")
print(f"OLD isotropic  p99={amax(iso)[0]:.1f}  max={amax(iso)[1]:.1f}")
print(f"NEW additive   p99={amax(rob)[0]:.1f}  max={amax(rob)[1]:.1f}")

w = rob._w_obs[rob.kind == 0]
print(f"\n--- glitches down-weighted: {int(np.sum(w<0.5))}/{len(w)} obs (w<0.5), "
      f"min w={w.min():.2f} ---")

# Apex of the slowest corner: speed + lateral accel + uncertainty
k = int(np.argmin(spd))
vx, vy = rob.vel_at(tq[k:k+1]); ax, ay = rob.acc_at(tq[k:k+1])
ex, ey = vx[0]/spd[k], vy[0]/spd[k]; nx, ny = -ey, ex
alat = abs(ax[0]*nx + ay[0]*ny)/G
print(f"\n--- slowest corner (apex) ---")
print(f"apex speed = {spd[k]*3.6:.0f} km/h, lateral accel = {alat:.1f} g, "
      f"line pinned to +/-{sc_rob[k]:.2f} m (was +/-{sc_iso[k]:.2f} m)")
print("\nDone.")
