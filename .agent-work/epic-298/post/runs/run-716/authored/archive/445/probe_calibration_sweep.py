"""Calibration sweep: how do floor / sig_t / nu move across cars and tracks?

For each (track, driver) fits the robust additive model on the fastest quali lap
and tabulates the calibrated obs model.  Hypotheses to check:
  - sig_t (~47 ms) UNIVERSAL across cars/tracks? (timing is a FastF1 property)
  - spatial FLOOR car-dependent? (we saw VER 0.69 vs HAM 1.93 m)
  - nu (tail heaviness) stable?

Uses cached sessions (Monza + Hungary 2023 Q).  One fastest lap per driver.
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_anisotropic_speedscaled,
)

TRACKS = [(2023, 'Italy', 'Monza'), (2023, 'Hungary', 'Hungary')]
DRIVERS = ['VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'NOR', 'ALO']
TEAM = {'VER': 'RBR', 'PER': 'RBR', 'LEC': 'FER', 'SAI': 'FER',
        'HAM': 'MER', 'RUS': 'MER', 'NOR': 'MCL', 'ALO': 'AMR'}
G = 9.81
PAD = 2.0

rows = []
for year, gp, label in TRACKS:
    print(f"\n===== {label} {year} Q =====")
    q = load_session(year, gp, 'Q')
    print(f"{'drv':>4} {'team':>4} {'floor(m)':>9} {'sig_t(ms)':>9} {'nu':>6} "
          f"{'p99A(g)':>8} {'maxA(g)':>8} {'glitch%':>8} {'vmax(km/h)':>10}")
    for drv in DRIVERS:
        try:
            num = driver_num(q, drv)
            laps = q.laps.pick_drivers(drv)
            valid = laps[laps['LapTime'].notna()]
            if len(valid) == 0:
                continue
            fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
            t0 = float(fast['LapStartTime'].total_seconds())
            t1 = float(fast['Time'].total_seconds())
            pos_d, spd_d = driver_streams(q, num)
            mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
            mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
            tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
            tc, V = spd_d['t'][mc], spd_d['V'][mc]
            if len(tp) < 50 or len(tc) < 50:
                continue
            delta, _ = session_offset([(tp, X, Y, tc, V)])
            hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
            ss, info = fit_smoother_anisotropic_speedscaled(
                hp['ell'], hp['sf'], hp['sig_pos'], delta, tp, X, Y, tc, V,
                order=4, nu='auto',
            )
            inlap = (tp >= t0) & (tp <= t1)
            ax, ay = ss.acc_at(tp[inlap])
            ai = np.hypot(ax, ay) / G
            # trim 5% edges (smoother one-sided boundary / in-out-lap transitions)
            n = len(ai); e = max(int(0.05 * n), 2)
            ai_in = ai[e:n - e]
            p99 = float(np.percentile(ai_in, 99))
            maxa = float(ai_in.max())
            w = ss._w_obs[ss.kind == 0]
            glitch = 100.0 * float(np.mean(w < 0.5))
            vmax = float(np.max(V)) * 3.6
            r = dict(track=label, drv=drv, team=TEAM[drv], floor=info['sig_floor'],
                     sig_t=info['sig_t_along'] * 1000, nu=info['nu'], p99=p99, maxa=maxa,
                     glitch=glitch, vmax=vmax)
            rows.append(r)
            print(f"{drv:>4} {TEAM[drv]:>4} {r['floor']:>9.2f} {r['sig_t']:>9.0f} "
                  f"{r['nu']:>6.1f} {r['p99']:>8.1f} {r['maxa']:>8.1f} {r['glitch']:>8.0f} {r['vmax']:>10.0f}")
        except Exception as e:
            print(f"{drv:>4} {TEAM.get(drv,'?'):>4}  ERROR: {type(e).__name__}: {e}")

# ---- summary ----
print("\n" + "=" * 60)
print("SUMMARY across the grid")
print("=" * 60)
sig_t = np.array([r['sig_t'] for r in rows])
floor = np.array([r['floor'] for r in rows])
nu = np.array([r['nu'] for r in rows])
print(f"sig_t  : mean {sig_t.mean():.0f} ms, CV {100*sig_t.std()/sig_t.mean():.0f}%, "
      f"range {sig_t.min():.0f}-{sig_t.max():.0f} ms  "
      f"-> {'~UNIVERSAL' if sig_t.std()/sig_t.mean() < 0.25 else 'VARIES'}")
print(f"floor  : mean {floor.mean():.2f} m, range {floor.min():.2f}-{floor.max():.2f} m  "
      f"(ratio {floor.max()/floor.min():.1f}x)  -> {'CAR/SESSION-DEPENDENT' if floor.max()/floor.min() > 1.6 else 'stable'}")
print(f"nu     : mean {nu.mean():.1f}, range {nu.min():.1f}-{nu.max():.1f}  "
      f"-> {'heavy tails everywhere' if nu.mean() < 8 else 'mixed'}")

# per-car floor (averaged over tracks) to see the car ordering
print("\nfloor by car (mean over tracks):")
for drv in DRIVERS:
    fs = [r['floor'] for r in rows if r['drv'] == drv]
    if fs:
        print(f"  {drv} ({TEAM[drv]}): {np.mean(fs):.2f} m")
print("\nDone.")
