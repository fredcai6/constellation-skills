"""Probe: speed-scaled timing-jitter along-track noise on VER Monza 2023 Q.

Compares:
  1. Isotropic fit (baseline)
  2. Constant-sigma anisotropic fit (fit_smoother_anisotropic)
  3. Speed-scaled timing-jitter fit (fit_smoother_anisotropic_speedscaled)

Reports: calibrated sig_t and sig_cross; along/cross residual RMS in low-speed
vs high-speed bins.
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
from src.preprocessing.trajectory.calibration import (
    session_offset,
    fit_stint_hp,
    fit_smoother_anisotropic,
    fit_smoother_anisotropic_speedscaled,
    measure_pos_timing_ellipse,
)
from src.preprocessing.trajectory.smoother import StintSmoother

print("Loading VER Monza 2023 Q...")
q = load_session(2023, 'Italy', 'Q')
num = driver_num(q, 'VER')
laps = q.laps.pick_drivers('VER')
valid = laps[laps['LapTime'].notna()]
fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
t0 = float(fast['LapStartTime'].total_seconds())
t1 = float(fast['Time'].total_seconds())
print(f"Lap window: {t0:.1f} -> {t1:.1f} s ({t1-t0:.1f} s)")

pos_d, spd_d = driver_streams(q, num)
PAD = 2.0
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc, V = spd_d['t'][mc], spd_d['V'][mc]
print(f"Pos samples: {len(tp)}, speed samples: {len(tc)}")

# 1. Calibrate HPs (isotropic, order=4)
print("\nCalibrating HPs...")
delta, _ = session_offset([(tp, X, Y, tc, V)])
hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
print(f"HPs: ell={hp['ell']:.2f} sf={hp['sf']:.0f} sig_pos={hp['sig_pos']:.3f} delta={hp['delta']:.3f}")
print(f"     chi2_pos={hp['chi2_pos']:.3f} chi2_spd={hp['chi2_spd']:.3f}")

ell, sf, sig_pos = hp['ell'], hp['sf'], hp['sig_pos']

# 2. Isotropic fit
print("\n--- ISOTROPIC FIT ---")
iso = StintSmoother(ell, sf, sig_pos, delta, iters=3, order=4)
iso.fit(tp, X, Y, tc, V)
sig_t_iso, sig_c_iso = measure_pos_timing_ellipse(iso, tp, X, Y)
print(f"measure_pos_timing_ellipse: sig_t_along={sig_t_iso:.4f} s, sig_cross={sig_c_iso:.4f} m")

# 3. Constant-sigma anisotropic
print("\n--- CONSTANT-SIGMA ANISOTROPIC FIT ---")
ani_const, ell_const = fit_smoother_anisotropic(ell, sf, sig_pos, delta, tp, X, Y, tc, V, order=4)
print(f"sig_along={ell_const['sig_along']:.3f} m, sig_cross={ell_const['sig_cross']:.3f} m")

# 4. Speed-scaled fit
print("\n--- SPEED-SCALED FIT ---")
ani_ss, ell_ss = fit_smoother_anisotropic_speedscaled(ell, sf, sig_pos, delta, tp, X, Y, tc, V, order=4)
print(f"sig_t_along={ell_ss['sig_t_along']:.4f} s (~{ell_ss['sig_t_along']*1000:.1f} ms), sig_cross={ell_ss['sig_cross']:.3f} m")

# 5. Residual analysis in velocity frame
# Use iso velocity frame to define along/cross consistently
Xh_iso, Yh_iso = iso.pos_at(tp)
vx, vy = iso.vel_at(tp)
spd = np.hypot(vx, vy)
ex, ey = vx / spd, vy / spd
nx_v, ny_v = -ey, ex

rx_iso = X - Xh_iso
ry_iso = Y - Yh_iso
along_iso = rx_iso * ex + ry_iso * ey
cross_iso = rx_iso * nx_v + ry_iso * ny_v

Xh_const, Yh_const = ani_const.pos_at(tp)
rx_c = X - Xh_const
ry_c = Y - Yh_const
along_const = rx_c * ex + ry_c * ey
cross_const = rx_c * nx_v + ry_c * ny_v

Xh_ss, Yh_ss = ani_ss.pos_at(tp)
rx_s = X - Xh_ss
ry_s = Y - Yh_ss
along_ss = rx_s * ex + ry_s * ey
cross_ss = rx_s * nx_v + ry_s * ny_v

# Speed bin analysis
spd_kmh = spd * 3.6
spd_median = float(np.median(spd_kmh))
lo = spd_kmh < spd_median
hi = spd_kmh >= spd_median

print(f"\nSpeed stats: median={spd_median:.1f} km/h, min={spd_kmh.min():.1f}, max={spd_kmh.max():.1f}")
print(f"Low-speed samples (<{spd_median:.0f} km/h): {lo.sum()}, High-speed: {hi.sum()}")

def rms(arr):
    return float(np.sqrt(np.mean(arr**2)))

def summarise(label, along, cross):
    print(f"\n  {label}:")
    print(f"    ALL : along RMS={rms(along):.3f} m  cross RMS={rms(cross):.3f} m")
    print(f"    LOW : along RMS={rms(along[lo]):.3f} m  cross RMS={rms(cross[lo]):.3f} m")
    print(f"    HIGH: along RMS={rms(along[hi]):.3f} m  cross RMS={rms(cross[hi]):.3f} m")
    # Timing jitter check: std(along/speed) should be flat
    timing = along / spd
    print(f"    std(along/speed) ALL={np.std(timing)*1000:.1f} ms  LOW={np.std(timing[lo])*1000:.1f} ms  HIGH={np.std(timing[hi])*1000:.1f} ms")

print("\n=== RESIDUAL SUMMARY (position residuals at obs times) ===")
summarise("ISOTROPIC", along_iso, cross_iso)
summarise("CONST-ANISO", along_const, cross_const)
summarise("SPEED-SCALED", along_ss, cross_ss)

print("\n=== IMPROVEMENT: SPEED-SCALED vs CONST-ANISO ===")
print(f"Cross ALL:  {rms(cross_const):.3f} -> {rms(cross_ss):.3f} m  ({100*(rms(cross_ss)/rms(cross_const)-1):+.1f}%)")
print(f"Cross LOW:  {rms(cross_const[lo]):.3f} -> {rms(cross_ss[lo]):.3f} m  ({100*(rms(cross_ss[lo])/rms(cross_const[lo])-1):+.1f}%)")
print(f"Along ALL:  {rms(along_const):.3f} -> {rms(along_ss):.3f} m  ({100*(rms(along_ss)/rms(along_const)-1):+.1f}%)")
print(f"Along LOW:  {rms(along_const[lo]):.3f} -> {rms(along_ss[lo]):.3f} m  ({100*(rms(along_ss[lo])/rms(along_const[lo])-1):+.1f}%)")
print("\nDone.")
