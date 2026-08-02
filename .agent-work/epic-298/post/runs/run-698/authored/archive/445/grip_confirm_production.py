"""Confirm the PRODUCTION LateralEnvelopeFit reproduces what we saw in the probe.

Builds real corner KinematicSamples (a_lat>5 m/s^2 proxy) from Silverstone/Hungary
Q (VER) smoothed telemetry and runs the merged production fit_envelope. Checks the
data-driven ceiling + the identifiability flag against the probe behaviour
(Silverstone: ceiling ~5g, identifiable; Hungary: no real ceiling, aero NOT
identifiable).
"""
import sys, warnings, logging
sys.path.insert(0, '.')
warnings.filterwarnings('ignore'); logging.getLogger('fastf1').setLevel(logging.ERROR)
import numpy as np
import fastf1; fastf1.Cache.enable_cache(r'C:\Programs\f1Brainz\outputs\cache')
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session, stint_span
from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
from src.physics.lateral_envelope import LateralEnvelopeFit
from src.physics.physics_data_models import KinematicSample, ControlState

G = 9.81
COV = np.eye(9)
CTRL = ControlState(timestamp_ms=0, throttle_confidence=1.0, throttle_value=1.0, brake_probability=0.0)


def derive(df):
    vx = df['vx'].to_numpy(); vy = df['vy'].to_numpy()
    ax = df['ax'].to_numpy(); ay = df['ay'].to_numpy()
    V = np.maximum(np.hypot(vx, vy), 1e-6); s = vx*ay - vy*ax
    return V, np.abs(s/V), (vx*ax + vy*ay)/V, df['curvature'].to_numpy(), df['session_time_ms'].to_numpy()


def run(gp, label, rho):
    q = load_session(2023, gp, 'Q'); num = driver_num(q, 'VER')
    pos_d, spd_d = driver_streams(q, num)
    valid = q.laps.pick_drivers('VER'); valid = valid[valid['LapTime'].notna()]
    best = valid['LapTime'].dt.total_seconds().min()
    fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
    st0, st1, _ = stint_span(q, 'VER', int(fast['Stint']), pad=2.0)
    mp = (pos_d['t']>=st0)&(pos_d['t']<=st1); mc = (spd_d['t']>=st0)&(spd_d['t']<=st1)
    hp = calibrate_session_hp(pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp], spd_d['t'][mc], spd_d['V'][mc], order=4)
    flying = valid[valid['LapTime'].dt.total_seconds() <= 1.08*best]; span = {}
    samples = []
    for _, lap in flying.iterrows():
        sn = int(lap['Stint'])
        if sn not in span: s0,s1,_ = stint_span(q,'VER',sn,pad=2.0); span[sn]=(s0,s1)
        s0,s1 = span[sn]
        try:
            ss, info = fit_lap(pos_d, spd_d, float(lap['LapStartTime'].total_seconds()),
                               float(lap['Time'].total_seconds()), hp, overhang=8.0, bounds=(s0,s1))
            df = smoother_to_processed_telemetry(ss, info['lap_t'])
        except Exception:
            continue
        V, alat, along, kappa, ts = derive(df)
        for k in range(len(V)):
            if alat[k] > 5.0:
                samples.append(KinematicSample(
                    timestamp_ms=int(ts[k]), position=np.zeros(3),
                    velocity=np.array([V[k], 0.0, 0.0]), acceleration=np.zeros(3),
                    covariance=COV, speed=float(V[k]), a_longitudinal=float(along[k]),
                    a_lateral=float(alat[k]), curvature=float(kappa[k]),
                    control=CTRL, regime='corner'))
    fit = LateralEnvelopeFit().fit_envelope(samples, air_density=rho)
    vmax = max(s.speed for s in samples) * 3.6
    ceil = 'None' if fit.ceiling is None else f'{fit.ceiling/G:.2f} g'
    print(f"{label:>11}: n_corner={len(samples):>4}  vmax={vmax:.0f} km/h  "
          f"A0={fit.A0/G:.2f} g  A2={fit.A2:.2e}  ceiling={ceil}  "
          f"aero_identifiable={fit.aero_identifiable}")


run('Great Britain', 'Silverstone', 1.18)
run('Hungary', 'Hungary', 1.16)
print("Done.")
