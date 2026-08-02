"""Multi-track validation via the NEW windowed path: calibrate_session_hp ONCE on
the stint, then fit_lap the fastest lap in a padded window (overhang, fixed HPs).
Compares to the old single-lap NS numbers.  Target: 24/24 physical, no edge trim.
"""
import sys, warnings, logging, traceback
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import (
    driver_num, driver_streams, load_session, stint_span,
)
from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
G = 9.81
TRACKS = [
    ('Monaco', 'Monaco'), ('Singapore', 'Singapore'), ('Spain', 'Spain'),
    ('Great Britain', 'Silverstone'), ('Belgium', 'Spa'), ('Qatar', 'Qatar'),
    ('Saudi Arabia', 'Jeddah'), ('Austria', 'RBR'),
]
DRIVERS = ['VER', 'HAM', 'NOR']
# old single-lap NS p99 (from probe_multitrack_ns) for reference
OLD = {('Monaco','VER'):4.5,('Monaco','HAM'):4.4,('Monaco','NOR'):4.2,
       ('Singapore','VER'):4.2,('Singapore','HAM'):4.0,('Singapore','NOR'):4.3,
       ('Spain','VER'):5.7,('Spain','HAM'):6.0,('Spain','NOR'):5.4,
       ('Silverstone','VER'):5.4,('Silverstone','HAM'):5.8,('Silverstone','NOR'):5.5,
       ('Spa','VER'):5.0,('Spa','HAM'):5.6,('Spa','NOR'):5.6,
       ('Qatar','VER'):6.2,('Qatar','HAM'):5.1,('Qatar','NOR'):6.2,
       ('Jeddah','VER'):6.2,('Jeddah','HAM'):10.0,('Jeddah','NOR'):5.9,
       ('RBR','VER'):6.2,('RBR','HAM'):6.0,('RBR','NOR'):6.4}

results = []
print(f"{'track':>11} {'drv':>4} {'old_p99':>8} {'new_p99':>8} {'new_max':>8} {'verdict':>9}")
for gp, label in TRACKS:
    try:
        q = load_session(2023, gp, 'Q')
    except Exception as e:
        print(f"{label:>11}  LOAD ERROR: {e}"); continue
    pos_cache = {}
    for drv in DRIVERS:
        try:
            num = driver_num(q, drv)
            laps = q.laps.pick_drivers(drv); valid = laps[laps['LapTime'].notna()]
            if len(valid) == 0:
                continue
            fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
            lt0 = float(fast['LapStartTime'].total_seconds()); lt1 = float(fast['Time'].total_seconds())
            stint_no = int(fast['Stint'])
            st0, st1, _ = stint_span(q, drv, stint_no, pad=2.0)
            pos_d, spd_d = driver_streams(q, num)
            # calibrate HPs ONCE on the stint context
            mp = (pos_d['t'] >= st0) & (pos_d['t'] <= st1)
            mc = (spd_d['t'] >= st0) & (spd_d['t'] <= st1)
            if mp.sum() < 100:
                continue
            hp = calibrate_session_hp(pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp],
                                      spd_d['t'][mc], spd_d['V'][mc], order=4)
            # windowed per-lap fit (overhang, fixed HPs, clipped to the stint)
            ss, info = fit_lap(pos_d, spd_d, lt0, lt1, hp, overhang=8.0, bounds=(st0, st1))
            ax, ay = ss.acc_at(info['lap_t']); a = np.hypot(ax, ay) / G
            p99, mx = float(np.percentile(a, 99)), float(a.max())   # interior -> no trim
            verdict = 'physical' if p99 < 7 else ('HIGH' if p99 < 12 else 'FAIL')
            results.append((label, drv, p99, mx, verdict))
            old = OLD.get((label, drv), float('nan'))
            print(f"{label:>11} {drv:>4} {old:>8.1f} {p99:>8.1f} {mx:>8.1f} {verdict:>9}")
        except Exception as e:
            print(f"{label:>11} {drv:>4}  ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()

print("\n" + "=" * 56)
phys = [r for r in results if r[4] == 'physical']
print(f"cells {len(results)}, physical {len(phys)}, non-physical {len(results)-len(phys)}")
nm = [r[2] for r in results]
print(f"new p99: median {np.median(nm):.1f}, max {np.max(nm):.1f} g")
bad = [r for r in results if r[4] != 'physical']
for r in bad:
    print(f"  NON-PHYSICAL: {r[0]} {r[1]}: p99 {r[2]:.1f} max {r[3]:.1f}")
print("\nDone.")
