"""Probe: is the POSITION error isotropic, with the along-track excess being a
separate TIMING term?  i.e. test the additive decomposition

    var_along(v) = sig_pos^2 + (v * sig_t)^2     (isotropic spatial + timing)
    var_cross(v) = sig_pos^2                      (flat, pure spatial)

vs the "over-shoved-into-time" model the speed-scale uses (var_along = (v sig_t)^2,
which wrongly -> 0 at standstill).

Verdict:
  sqrt(a) ~ sqrt(c)  => position spatial part IS isotropic; all along anisotropy
                        is the timing term -> drop sig_pos_cross, use sig_pos + sig_t.
  sqrt(a) >  sqrt(c)  => genuine spatial anisotropy remains; NOT just timing.
"""
import sys
import warnings
import logging

sys.path.insert(0, '.agent-work/445/envelope')
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
logging.getLogger('fastf1').setLevel(logging.ERROR)

import numpy as np

from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp
from src.preprocessing.trajectory.smoother import StintSmoother

print("Loading VER Monza 2023 Q...")
q = load_session(2023, 'Italy', 'Q')
num = driver_num(q, 'VER')
laps = q.laps.pick_drivers('VER')
valid = laps[laps['LapTime'].notna()]
fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
t0 = float(fast['LapStartTime'].total_seconds())
t1 = float(fast['Time'].total_seconds())

pos_d, spd_d = driver_streams(q, num)
PAD = 2.0
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc, V = spd_d['t'][mc], spd_d['V'][mc]

delta, _ = session_offset([(tp, X, Y, tc, V)])
hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
print(f"HPs: ell={hp['ell']:.2f} sig_pos={hp['sig_pos']:.3f} "
      f"chi2_pos={hp['chi2_pos']:.2f} chi2_spd={hp['chi2_spd']:.2f}")
iso = StintSmoother(hp['ell'], hp['sf'], hp['sig_pos'], delta, iters=3, order=4)
iso.fit(tp, X, Y, tc, V)

# residuals on the flying lap only
inlap = (tp >= t0) & (tp <= t1)
tpl, Xl, Yl = tp[inlap], X[inlap], Y[inlap]
Xh, Yh = iso.pos_at(tpl)
vx, vy = iso.vel_at(tpl)
spd = np.hypot(vx, vy)
ex, ey = vx / spd, vy / spd
nx, ny = -ey, ex
rx, ry = Xl - Xh, Yl - Yh
along = rx * ex + ry * ey
cross = rx * nx + ry * ny

# de-bias: obs-noise var = residual var + posterior predictive var (H P H^T)
# projected along/cross.  Use pos_predcov_local if available, else raw only.
have_debias = hasattr(iso, "pos_predcov_local")
if have_debias:
    # function returns (latent + obs) predictive var; the EM de-bias term is the
    # LATENT posterior var H P_s H^T only, so subtract the obs-noise we put in.
    pcv_along, pcv_cross, _, _ = iso.pos_predcov_local(tpl)
    sc2_obs = iso.sig_pos_cross ** 2 if iso.sig_pos_cross is not None else iso.sig_pos ** 2
    pv_along = pcv_along - iso.sig_pos ** 2
    pv_cross = pcv_cross - sc2_obs
else:
    pv_along = pv_cross = np.zeros(len(tpl))

# quantile speed bins (equal count)
NB = 7
order = np.argsort(spd)
bins = np.array_split(order, NB)
print(f"\n{'bin':>3} {'v(km/h)':>8} {'n':>4} "
      f"{'std_along':>9} {'std_cross':>9} {'std_alongDB':>11} {'std_crossDB':>11}")
vc_list, va_raw, vc_raw, va_db, vc_db = [], [], [], [], []
for b, idx in enumerate(bins):
    vcen = float(np.mean(spd[idx]))
    a_raw = float(np.mean(along[idx] ** 2))
    c_raw = float(np.mean(cross[idx] ** 2))
    a_db = a_raw + float(np.mean(pv_along[idx]))
    c_db = c_raw + float(np.mean(pv_cross[idx]))
    vc_list.append(vcen)
    va_raw.append(a_raw); vc_raw.append(c_raw); va_db.append(a_db); vc_db.append(c_db)
    print(f"{b:>3} {vcen*3.6:>8.0f} {len(idx):>4} "
          f"{np.sqrt(a_raw):>9.3f} {np.sqrt(c_raw):>9.3f} "
          f"{np.sqrt(a_db):>11.3f} {np.sqrt(c_db):>11.3f}")

vc_arr = np.array(vc_list)


def decomp(va, vc_, label):
    # var_along = a + b v^2 ; var_cross = c (mean)
    A = np.column_stack([np.ones_like(vc_arr), vc_arr ** 2])
    (a, b), *_ = np.linalg.lstsq(A, np.array(va), rcond=None)
    c = float(np.mean(vc_))
    sig_pos_along = np.sqrt(max(a, 0.0))
    sig_t = np.sqrt(max(b, 0.0))
    sig_cross = np.sqrt(max(c, 0.0))
    print(f"\n[{label}]")
    print(f"  along fit:  sig_pos(along intercept) = {sig_pos_along:.3f} m,  "
          f"sig_t = {sig_t*1000:.0f} ms")
    print(f"  cross flat: sig_cross               = {sig_cross:.3f} m")
    # is cross flat?
    cv = np.std(np.sqrt(vc_)) / (np.mean(np.sqrt(vc_)) + 1e-9)
    print(f"  cross speed-dependence (CV of std)  = {cv*100:.0f}%  "
          f"({'flat' if cv < 0.25 else 'NOT flat'})")
    # isotropy verdict
    ratio = sig_pos_along / (sig_cross + 1e-9)
    print(f"  ISOTROPY: along-floor / cross = {ratio:.2f}  ->  "
          f"{'ISOTROPIC spatial (all along-anisotropy is timing)' if 0.7 < ratio < 1.4 else 'spatial anisotropy REMAINS'}")
    # how much of low-speed along var does the pure-timing model wrongly call timing?
    v_lo = vc_arr.min()
    along_lo_var = a + b * v_lo ** 2
    timing_lo = b * v_lo ** 2
    print(f"  at v={v_lo*3.6:.0f} km/h: along var = {along_lo_var:.2f} m^2, "
          f"of which timing = {100*timing_lo/along_lo_var:.0f}% "
          f"(pure-timing model claims 100%)")


decomp(va_raw, vc_raw, "RAW residual variances")
if have_debias:
    decomp(va_db, vc_db, "DE-BIASED (obs-noise) variances")
print("\nDone.")
