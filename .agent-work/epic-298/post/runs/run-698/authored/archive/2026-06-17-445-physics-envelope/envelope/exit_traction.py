"""Slow-corner exit traction per constructor + walk-away (epic #445).

Corner exit is GRIP-limited at low speed (the reliable regime, not the noisy
high-speed saturation). So the grip differences should surface as an exit
deployment advantage that compounds down the next straight ('walk away').
Measure post-apex longitudinal accel off slow corners, both teammates pooled,
quali. Does Red Bull deploy harder, and does it compound?
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num  # noqa: E402

G, MASS = 9.81, 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
TEAMS = {"RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"], "WIL": ["ALB", "SAR"]}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def exit_points(session, car):
    """Post-apex longitudinal accel at slow corners, by exit speed."""
    num = driver_num(session, car); cd = session.car_data[num]
    tc = cd["SessionTime"].dt.total_seconds().to_numpy()
    spd = cd["Speed"].to_numpy(float) / 3.6
    pts = []
    for ls, le in flying_windows(session, car):
        m = (tc >= ls) & (tc <= le)
        t, v = tc[m], spd[m]
        o = np.argsort(t); t, v = t[o], v[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9]); t, v = t[keep], v[keep]
        if len(t) < 50:
            continue
        apex, _ = find_peaks(-v, prominence=8, distance=6)
        for ia in apex:
            if v[ia] * 3.6 > 130 or v[ia] * 3.6 < 50:   # slow corners
                continue
            for j in range(ia, min(ia + 12, len(t) - 1)):
                if v[j] <= v[ia]:
                    continue
                if v[j] * 3.6 > 150:                     # only the traction-limited part
                    break
                dt = t[j + 1] - t[j - 1]
                if dt > 0:
                    a = (v[j + 1] - v[j - 1]) / dt / G
                    if a > 0:
                        pts.append((v[j], a))
    return pts


def main():
    q = H.load_session(2023, "Japan", "Q")
    data = {}
    for team, drvs in TEAMS.items():
        pts = []
        for car in drvs:
            try:
                pts += exit_points(q, car)
            except Exception as e:
                log(f"  {team}/{car}: {e}")
        data[team] = np.array(pts)
        log(f"{team}: {len(pts)} exit nodes")

    print("\n=== slow-corner exit traction (longitudinal g) by exit speed ===")
    bins = [(60, 90), (90, 120), (120, 150)]
    hdr = " ".join(f"{lo}-{hi}km/h" for lo, hi in bins)
    print(f"{'team':>5} | {hdr}")
    dep = {}
    for team, p in data.items():
        if len(p) < 30:
            continue
        v, a = p[:, 0] * 3.6, p[:, 1]
        row = []
        for lo, hi in bins:
            b = (v >= lo) & (v < hi)
            row.append(np.percentile(a[b], 90) if b.sum() >= 5 else np.nan)
        dep[team] = row
        print(f"{team:>5} | " + "  ".join(f"{x:8.2f}" for x in row))

    # walk-away estimate: an exit-accel edge over ~80 m of exit -> delta-V -> time
    # gained over a 400 m straight at ~250 km/h
    print("\n=== walk-away estimate (vs field mean), 90-120 km/h exit ===")
    idx = 1
    field = np.nanmean([dep[t][idx] for t in dep])
    for team in dep:
        da = (dep[team][idx] - field) * G       # m/s^2 edge
        # dV over ~80 m exit at ~30 m/s: dV ~ da*t, t ~ 80/30 ~ 2.7s -> dV = da*2.7
        dV = da * 2.7
        # time gained over a 400 m straight at ~70 m/s mean: dt ~ -L*dV/v^2
        dt = -400 * dV / 70**2
        print(f"   {team:>5}: exit edge {da:+.2f} m/s^2 -> ~{dV:+.2f} m/s exit speed "
              f"-> ~{dt*1000:+.0f} ms/straight (x ~8 such corners)")
    print("\n(does Red Bull deploy harder off slow corners, in the RELIABLE grip regime, "
          "and does it compound? this is the exit/traction-ellipse discrimination.)")


if __name__ == "__main__":
    main()
