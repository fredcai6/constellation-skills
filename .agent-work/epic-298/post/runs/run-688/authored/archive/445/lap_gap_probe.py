"""#488 lap-gap diagnostic (scratch): sim ideal lap vs VER's real best quali lap.

Fits the per-car capability (pooled flying Q laps, full production path), builds
the track profile from VER's BEST lap geometry, runs the production
PhysicsSimulator ideal lap, and compares it to the real lap:

  * top:    speed vs distance (ideal sim vs real best lap)
  * bottom: cumulative time gap  Δt(s) = ∫ (1/v_sim − 1/v_real) ds
            (positive = sim is BEHIND / slower at that point on track)

This exposes WHERE the ideal-lap sim loses time vs reality — slow corners
(traction-grip cap) vs straights (deployed power) — to judge whether the #488
traction cap over-slows corner-heavy tracks (the Monaco regression question).
"""
from __future__ import annotations

import sys
import warnings
import logging
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("src").setLevel(logging.ERROR)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = 9.81
YEAR, SESSION, DRV = 2023, "Q", "VER"
CACHE = str(REPO / "outputs" / "cache")

TRACKS = {
    "monaco": ("Monaco", "Monaco", 1.1900),
    "hungary": ("Hungary", "Hungary", 1.1600),
    "silverstone": ("Great Britain", "Silverstone", 1.1753),
}
TRACK = sys.argv[1] if len(sys.argv) > 1 else "monaco"
GP, LABEL, RHO_FALLBACK = TRACKS[TRACK]
OUT = str(REPO / ".agent-work" / "445" / f"lap_gap_{TRACK}.png")


def _build_control_df(session, drv_num, t0, t1, pad=2.0):
    cd = pd.DataFrame(session.car_data[drv_num]).copy()
    cd_t = cd["SessionTime"].dt.total_seconds().to_numpy()
    mask = (cd_t >= t0 - pad) & (cd_t <= t1 + pad)
    cd_lap = cd[mask].copy()
    if cd_lap.empty:
        return pd.DataFrame()
    return pd.DataFrame({
        "session_time_ms": (cd_t[mask] * 1000.0).astype(int),
        "throttle": cd_lap["Throttle"].astype(float).values,
        "brake": (cd_lap["Brake"].astype(float).values * 100.0
                  if cd_lap["Brake"].max() <= 1.0 else cd_lap["Brake"].astype(float).values),
        "gear": cd_lap["nGear"].astype(float).values if "nGear" in cd_lap.columns else 0.0,
        "drs": cd_lap["DRS"].astype(float).values if "DRS" in cd_lap.columns else 0.0,
    })


def main():
    from src.preprocessing.trajectory.loaders import (
        load_session, driver_num, driver_streams, stint_span,
    )
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.parameter_estimator import ParameterEstimator
    from src.physics.control_alignment import ControlAlignment
    from src.physics.physics_config import PhysicsEstimatorConfig
    from src.physics.physics_simulator import PhysicsSimulator
    from src.physics.regulation_era import RegulationEra

    print(f"[load] {YEAR} {GP} {SESSION}")
    q = load_session(YEAR, GP, SESSION, CACHE)
    era = RegulationEra.for_season(YEAR)
    num = driver_num(q, DRV)
    rho = RHO_FALLBACK
    pos_d, spd_d = driver_streams(q, num)

    valid = q.laps.pick_drivers(DRV)
    valid = valid[valid["LapTime"].notna()]
    valid = valid[valid["LapTime"].dt.total_seconds() > 50]
    best_s = valid["LapTime"].dt.total_seconds().min()
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    flying = valid[valid["LapTime"].dt.total_seconds() <= 1.08 * best_s]
    print(f"[laps] VER best Q lap {best_s:.3f}s ; pooling {len(flying)} flying laps")

    st0, st1, _ = stint_span(q, DRV, int(fast["Stint"]), pad=2.0)
    mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
    mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
    hp = calibrate_session_hp(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                              spd_d["t"][mc], spd_d["V"][mc], order=4)

    cfg = PhysicsEstimatorConfig.from_config()
    ca = ControlAlignment(cfg)

    # --- fit params from the pooled flying laps; keep the BEST lap's telemetry ---
    span: dict[int, tuple] = {}
    proc_parts, ctrl_parts = [], []
    best_df = None
    for _, lap in flying.iterrows():
        sn = int(lap["Stint"])
        if sn not in span:
            s0, s1, _ = stint_span(q, DRV, sn, pad=2.0)
            span[sn] = (s0, s1)
        s0, s1 = span[sn]
        lap_t0 = float(lap["LapStartTime"].total_seconds())
        lap_t1 = float(lap["Time"].total_seconds())
        try:
            ss, info = fit_lap(pos_d, spd_d, lap_t0, lap_t1, hp, overhang=8.0, bounds=(s0, s1))
            dfp = smoother_to_processed_telemetry(ss, info["lap_t"], driver_id=DRV,
                                                  lap_number=int(lap["LapNumber"]))
        except Exception as e:
            print("  skip", e); continue
        cdf = _build_control_df(q, num, lap_t0, lap_t1)
        if dfp.empty or cdf.empty:
            continue
        proc_parts.append(dfp); ctrl_parts.append(cdf)
        if int(lap["LapNumber"]) == int(fast["LapNumber"]):
            best_df, best_ctrl = dfp, cdf

    processed = pd.concat(proc_parts, ignore_index=True)
    control_df = pd.concat(ctrl_parts, ignore_index=True)
    params = ParameterEstimator(cfg).estimate_parameters(
        processed, control_df=control_df, weather={"air_density": rho}, era=era,
    )
    fqm = params.fit_quality_metrics
    print(f"[fit] A0={params.lateral.A0:.1f} A2={params.lateral.A2:.2e} "
          f"ceiling={'%.1fg'%(params.lateral.ceiling/G) if params.lateral.ceiling else 'None'} "
          f"theta_D={params.longitudinal.theta_D:.4f} power={params.longitudinal.max_power:.0f} "
          f"fb_long={int(fqm.get('fallback_longitudinal',0))} fb_lat={int(fqm.get('fallback_lateral',0))}")
    if params.traction is not None:
        print(f"[trac] a_t={params.traction.a_t:.1f} m/s^2 ({params.traction.a_t/G:.2f}g)  "
              f"b_t={params.traction.b_t:.2e}  source={fqm.get('traction_source')}")
    else:
        print(f"[trac] source={fqm.get('traction_source')} (no measured frontier)")

    # --- track profile from VER's best lap geometry ---
    px = best_df["px"].to_numpy(); py = best_df["py"].to_numpy()
    ds = np.hypot(np.diff(px), np.diff(py))
    dist = np.concatenate([[0.0], np.cumsum(ds)])
    curv = np.abs(best_df["curvature"].to_numpy())
    controls = ca.align_controls(best_df["session_time_ms"].to_numpy(float), best_ctrl)
    drs_open = np.array([c.drs for c in controls], dtype=bool)
    v_real = best_df["speed_ms"].to_numpy()
    track = pd.DataFrame({"distance_m": dist, "curvature": curv, "drs_open": drs_open})

    # --- ideal lap sim ---
    lap = PhysicsSimulator(cfg).simulate_lap(track, params, sample=False)
    v_sim = np.interp(dist, lap.distance_profile, lap.speed_profile)
    real_lap_s = best_s
    sim_lap_s = lap.lap_time_s
    print(f"[sim] ideal lap {sim_lap_s:.3f}s  vs  real best {real_lap_s:.3f}s  "
          f"(delta {sim_lap_s-real_lap_s:+.2f}s)")

    # --- delta velocity vs POSITION (the exploration diagnostic) ---
    # dv = v_sim - v_real.  Objective is asymmetric:
    #   * at corner APEXES (grip-ceiling-limited): dv ~ 0  -> ceiling honest
    #   * on corner EXITS / accel zones:           dv >= 0 -> accel not under-called
    # dv < 0 right after an apex = UNDERESTIMATING ACCELERATION (the miss).
    dv = (v_sim - v_real) * 3.6  # km/h, + = sim faster

    # mark apexes (local minima of the real speed trace) to flag exits
    from scipy.signal import find_peaks
    apex_idx, _ = find_peaks(-v_real, prominence=5.0, distance=8)

    # ---- plot ----
    fig, (axS, axG) = plt.subplots(2, 1, figsize=(13, 8.5), sharex=True,
                                   gridspec_kw=dict(height_ratios=[2, 1]))
    axS.plot(dist, v_real * 3.6, color="#222", lw=2.0, label=f"real best lap ({real_lap_s:.2f}s)")
    axS.plot(dist, v_sim * 3.6, color="#c1272d", lw=2.0, label=f"ideal sim ({sim_lap_s:.2f}s)")
    axS.plot(dist[apex_idx], v_real[apex_idx] * 3.6, "v", color="#7a4a00", ms=6,
             label="corner apex")
    axS.set_ylabel("speed (km/h)", fontsize=12)
    axS.set_title(f"Ideal-lap sim vs VER real best Q lap — {LABEL} {YEAR}  "
                  f"(lap Δ {sim_lap_s-real_lap_s:+.2f}s)", fontsize=13, weight="bold")
    axS.legend(loc="lower right", fontsize=9); axS.grid(alpha=0.25)

    axG.plot(dist, dv, color="#1f6fb2", lw=1.6)
    axG.axhline(0, color="#888", lw=0.8)
    axG.fill_between(dist, 0, dv, where=(dv < 0), color="#c1272d", alpha=0.30)
    axG.fill_between(dist, 0, dv, where=(dv > 0), color="#2a9d3a", alpha=0.18)
    for x in dist[apex_idx]:
        axG.axvline(x, color="#7a4a00", lw=0.6, alpha=0.4)
    axG.set_ylabel("Δv = sim − real (km/h)", fontsize=11)
    axG.set_xlabel("lap distance (m)", fontsize=12)
    axG.grid(alpha=0.25)
    axG.text(0.01, 0.04,
             "RED (Δv<0) = sim slower → UNDERESTIMATING accel (the miss) · "
             "GREEN = sim faster · brown lines = apexes (look just after for exits)",
             transform=axG.transAxes, fontsize=8, color="#666", va="bottom")
    # summary stat: median dv in the 40 m after each apex (the exit accel zones)
    exit_dv = []
    for i in apex_idx:
        seg = (dist >= dist[i]) & (dist <= dist[i] + 40.0)
        if seg.sum() > 1:
            exit_dv.append(np.median(dv[seg]))
    if exit_dv:
        print(f"[exits] median dv in 40 m after apexes: {np.median(exit_dv):+.1f} km/h "
              f"(negative = under-accelerating out of corners)")

    plt.tight_layout()
    plt.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
