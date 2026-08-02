"""Test (not assume) position isotropy using a LOW-SPEED-anchored track.

On a Monza flying lap the slowest data is ~120 km/h, so the along-track spatial
floor and the timing term v*sig_t are confounded (no low-speed lever).  A hairpin
track (Hungary T1, Monaco Fairmont ~50 km/h) drops low enough that the timing
term shrinks and the spatial floor shows through.  Pool several laps so the
low-speed bins have real sample counts.

Decisive test: at the LOWEST speed bin, does std_along collapse to std_cross?
  yes  -> position spatial error is ISOTROPIC; along-excess is pure timing.
  no   -> genuine spatial anisotropy remains (along noisier than cross at all v).

Usage: py probe_isotropy_track.py [year] [gp] [session] [driver] [n_laps]
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

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
GP = sys.argv[2] if len(sys.argv) > 2 else 'Hungary'
SESS = sys.argv[3] if len(sys.argv) > 3 else 'Q'
DRV = sys.argv[4] if len(sys.argv) > 4 else 'VER'
NLAP = int(sys.argv[5]) if len(sys.argv) > 5 else 6

print(f"Loading {DRV} {GP} {YEAR} {SESS}...")
q = load_session(YEAR, GP, SESS)
num = driver_num(q, DRV)
laps = q.laps.pick_drivers(DRV)
valid = laps[laps['LapTime'].notna()].copy()
valid = valid.sort_values('LapTime').head(NLAP)
print(f"Using {len(valid)} fastest valid laps")

pos_d, spd_d = driver_streams(q, num)

# Calibrate HPs once on the fastest lap; reuse within the session (same car/cond).
fast = valid.iloc[0]
t0 = float(fast['LapStartTime'].total_seconds())
t1 = float(fast['Time'].total_seconds())
PAD = 2.0
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp0, X0, Y0 = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc0, V0 = spd_d['t'][mc], spd_d['V'][mc]
delta, _ = session_offset([(tp0, X0, Y0, tc0, V0)])
hp = fit_stint_hp(tp0, X0, Y0, tc0, V0, delta=delta, iters=3, order=4)
print(f"HPs (fastest lap): ell={hp['ell']:.2f} sig_pos={hp['sig_pos']:.3f} "
      f"delta={delta:.3f} chi2_pos={hp['chi2_pos']:.2f} chi2_spd={hp['chi2_spd']:.2f}")

# Pool residuals across laps
A_spd, A_along, A_cross, A_pva, A_pvc = [], [], [], [], []
for _, lap in valid.iterrows():
    t0 = float(lap['LapStartTime'].total_seconds())
    t1 = float(lap['Time'].total_seconds())
    mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
    mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
    tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
    tc, V = spd_d['t'][mc], spd_d['V'][mc]
    if len(tp) < 50 or len(tc) < 50:
        continue
    ss = StintSmoother(hp['ell'], hp['sf'], hp['sig_pos'], delta, iters=3, order=4)
    ss.fit(tp, X, Y, tc, V)
    inlap = (tp >= t0) & (tp <= t1)
    tpl, Xl, Yl = tp[inlap], X[inlap], Y[inlap]
    Xh, Yh = ss.pos_at(tpl)
    vx, vy = ss.vel_at(tpl)
    spd = np.hypot(vx, vy)
    ex, ey = vx / spd, vy / spd
    nx, ny = -ey, ex
    rx, ry = Xl - Xh, Yl - Yh
    pcv_a, pcv_c, _, _ = ss.pos_predcov_local(tpl)
    A_spd.append(spd)
    A_along.append(rx * ex + ry * ey)
    A_cross.append(rx * nx + ry * ny)
    A_pva.append(pcv_a - ss.sig_pos ** 2)   # latent posterior var (de-bias term)
    A_pvc.append(pcv_c - ss.sig_pos ** 2)

spd = np.concatenate(A_spd)
along = np.concatenate(A_along)
cross = np.concatenate(A_cross)
pva = np.concatenate(A_pva)
pvc = np.concatenate(A_pvc)
print(f"Pooled samples: {len(spd)}  (speed {spd.min()*3.6:.0f}-{spd.max()*3.6:.0f} km/h)")

# Fixed speed-bin edges (km/h) to guarantee a populated low-speed bin
edges_kmh = np.array([0, 70, 95, 120, 150, 185, 225, 270, 320, 400])
edges = edges_kmh / 3.6
print(f"\n{'v(km/h)':>9} {'n':>4} {'std_along':>9} {'std_cross':>9} "
      f"{'alongDB':>8} {'crossDB':>8}  {'A/C(DB)':>7}")
rows = []
for i in range(len(edges) - 1):
    m = (spd >= edges[i]) & (spd < edges[i + 1])
    if m.sum() < 10:
        continue
    vcen = float(np.mean(spd[m]))
    a_raw = float(np.mean(along[m] ** 2))
    c_raw = float(np.mean(cross[m] ** 2))
    a_db = a_raw + float(np.mean(pva[m]))
    c_db = c_raw + float(np.mean(pvc[m]))
    # robust (MAD->sigma) variances: outlier-resistant, distinguishes structural
    # anisotropy from a few low-speed glitches that game RMS.
    a_rob = (1.4826 * float(np.median(np.abs(along[m] - np.median(along[m]))))) ** 2
    c_rob = (1.4826 * float(np.median(np.abs(cross[m] - np.median(cross[m]))))) ** 2
    rows.append((vcen, m.sum(), a_raw, c_raw, a_db, c_db, a_rob, c_rob))
    print(f"{vcen*3.6:>9.0f} {m.sum():>4} {np.sqrt(a_raw):>9.3f} {np.sqrt(c_raw):>9.3f} "
          f"{np.sqrt(a_db):>8.3f} {np.sqrt(c_db):>8.3f}  {np.sqrt(a_db/c_db):>7.2f}")

vcen = np.array([r[0] for r in rows])
n = np.array([r[1] for r in rows])
a_raw = np.array([r[2] for r in rows])
c_raw = np.array([r[3] for r in rows])
va = np.array([r[4] for r in rows])
vc = np.array([r[5] for r in rows])
a_rob = np.array([r[6] for r in rows])
c_rob = np.array([r[7] for r in rows])

# ----- DECISIVE test on RAW residuals (model-light; the de-bias is fit-dependent
# and asymmetric, so it muddies the ratio).  Impose isotropy (along floor = cross
# floor) and read sig_t per bin.  If sig_t is FLAT across speed, isotropy holds and
# the along-excess is a single timing term.  If sig_t INFLATES at low speed, there
# is a genuine spatial anisotropy (extra along floor / v^2).
floor_raw = float(np.sqrt(np.average(c_raw, weights=n)))   # flat cross floor (raw)
sig_t_raw = np.sqrt(np.maximum(a_raw - floor_raw ** 2, 0.0)) / vcen
floor_db = float(np.sqrt(np.average(vc, weights=n)))
sig_t_db = np.sqrt(np.maximum(va - floor_db ** 2, 0.0)) / vcen
floor_rob = float(np.sqrt(np.average(c_rob, weights=n)))
sig_t_rob = np.sqrt(np.maximum(a_rob - floor_rob ** 2, 0.0)) / vcen
print(f"\nRaw cross floor = {floor_raw:.3f} m   DB cross floor = {floor_db:.3f} m"
      f"   ROBUST cross floor = {floor_rob:.3f} m")
print(f"\n{'v(km/h)':>9} {'sig_t_RAW(ms)':>13} {'sig_t_DB(ms)':>13} {'sig_t_ROB(ms)':>13}")
for v, tr, td, trob in zip(vcen, sig_t_raw, sig_t_db, sig_t_rob):
    print(f"{v*3.6:>9.0f} {tr*1000:>13.0f} {td*1000:>13.0f} {trob*1000:>13.0f}")
mrob = float(np.mean(sig_t_rob))
print(f"\nsig_t_ROBUST: mean = {mrob*1000:.0f} ms, "
      f"lowest-bin/mean = {sig_t_rob[0]/(mrob+1e-9):.2f}  "
      f"({'low-speed bump SURVIVES MAD -> structural' if sig_t_rob[0]/(mrob+1e-9) > 1.4 else 'low-speed bump GONE under MAD -> outliers, isotropy holds'})")
mean_t = float(np.mean(sig_t_raw))
cv_raw = float(np.std(sig_t_raw) / (mean_t + 1e-9))
low_excess = sig_t_raw[0] / (mean_t + 1e-9)   # spatial anisotropy => low bin INFLATED
print(f"\nsig_t_RAW: mean = {mean_t*1000:.0f} ms, CV = {cv_raw*100:.0f}%, "
      f"lowest-bin/mean = {low_excess:.2f}")
print("VERDICT:")
if cv_raw < 0.20 and low_excess < 1.3:
    print("  sig_t FLAT across speed, lowest bin not inflated  ==>  ISOTROPIC spatial"
          " floor + single timing term (along-excess is pure timing).")
elif low_excess > 1.4:
    print("  sig_t INFLATED at low speed  ==>  GENUINE spatial anisotropy on top of"
          " timing (along floor > cross floor).")
else:
    print("  borderline — wider speed range / more low-speed data would sharpen it.")
print("\nDone.")
