"""Windowed (STINT) fit vs single-lap hard-cutoff fit.

The probes so far cut ONE lap [LapStartTime-2, Time+2] and trim 5% edges -- a
band-aid for the boundary. The right unit is the continuous STINT (out-lap ->
flying laps -> in-lap, cut only at pit where the car is stationary): the flying
lap becomes INTERIOR, so no edge effect and no trim needed, and the HP/roughness
calibrate on more data.

Prediction: HAM Jeddah's spike sits at t-t0 ~ 79 s of an 80 s lap -- right at the
single-lap t1 cutoff.  A stint fit gives that final sector in-lap context on the
far side, so it should drop.  Compares flying-lap interior p99/max |a| for the
single-lap fit vs the stint fit (flying lap selected from the stint, NO trim).
"""
import sys, warnings, logging
sys.path.insert(0, '.agent-work/445/envelope'); sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
from src.preprocessing.trajectory.loaders import (
    driver_num, driver_streams, load_session, stint_span,
)
from src.preprocessing.trajectory.calibration import (
    session_offset, fit_stint_hp, fit_smoother_nonstationary,
)
G = 9.81

def accel_stats(ss, tmask, trim):
    ax, ay = ss.acc_at(tmask)
    a = np.hypot(ax, ay) / G
    if trim:
        n = len(a); e = max(int(0.05 * n), 2); a = a[e:n - e]
    return float(np.percentile(a, 99)), float(a.max())

def run(gp, drv):
    q = load_session(2023, gp, 'Q'); num = driver_num(q, drv)
    laps = q.laps.pick_drivers(drv); valid = laps[laps['LapTime'].notna()]
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    lt0 = float(fast['LapStartTime'].total_seconds()); lt1 = float(fast['Time'].total_seconds())
    stint_no = int(fast['Stint'])
    pos_d, spd_d = driver_streams(q, num)

    # --- single-lap (hard cutoff, PAD=2, with edge trim) ---
    PAD = 2.0
    mp = (pos_d['t'] >= lt0 - PAD) & (pos_d['t'] <= lt1 + PAD)
    mc = (spd_d['t'] >= lt0 - PAD) & (spd_d['t'] <= lt1 + PAD)
    tp1, X1, Y1 = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
    tc1, V1 = spd_d['t'][mc], spd_d['V'][mc]
    d1, _ = session_offset([(tp1, X1, Y1, tc1, V1)])
    hp1 = fit_stint_hp(tp1, X1, Y1, tc1, V1, delta=d1, iters=3, order=4)
    ns1, _ = fit_smoother_nonstationary(hp1['ell'], hp1['sf'], hp1['sig_pos'], d1, tp1, X1, Y1, tc1, V1, order=4, base_ell=6.0)
    fly1 = tp1[(tp1 >= lt0) & (tp1 <= lt1)]
    lap_p99, lap_max = accel_stats(ns1, fly1, trim=True)

    # --- STINT window (continuous; flying lap is interior, NO trim) ---
    st0, st1, table = stint_span(q, drv, stint_no, pad=2.0)
    mp = (pos_d['t'] >= st0) & (pos_d['t'] <= st1)
    mc = (spd_d['t'] >= st0) & (spd_d['t'] <= st1)
    tps, Xs, Ys = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
    tcs, Vs = spd_d['t'][mc], spd_d['V'][mc]
    ds, _ = session_offset([(tps, Xs, Ys, tcs, Vs)])
    hps = fit_stint_hp(tps, Xs, Ys, tcs, Vs, delta=ds, iters=3, order=4)
    nss, _ = fit_smoother_nonstationary(hps['ell'], hps['sf'], hps['sig_pos'], ds, tps, Xs, Ys, tcs, Vs, order=4, base_ell=6.0)
    flys = tps[(tps >= lt0) & (tps <= lt1)]
    st_p99, st_max = accel_stats(nss, flys, trim=False)   # interior of the stint -> no trim

    nlaps = len(table)
    span = st1 - st0
    print(f"{drv} {gp:>14}: stint #{stint_no} = {nlaps} laps, {span:.0f}s "
          f"({len(tps)} pos vs {len(tp1)} single-lap)")
    print(f"   single-lap (cut+trim): p99={lap_p99:.1f} max={lap_max:.1f} g")
    print(f"   STINT window (interior): p99={st_p99:.1f} max={st_max:.1f} g")

for gp, drv in [('Italy', 'VER'), ('Saudi Arabia', 'HAM'), ('Saudi Arabia', 'NOR')]:
    try:
        run(gp, drv)
    except Exception as e:
        import traceback; print(f"{drv} {gp}: ERROR {e}"); traceback.print_exc()
print("\nDone.")
