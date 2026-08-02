"""#488 sanity check (scratch): the measured full-throttle acceleration frontier.

Shows the real throttle-regime longitudinal acceleration vs speed (DRS-split),
its p90 frontier, and three candidate drive curves:

  * ANCHORED joint-fit:  a(v) = P/(m·v) − ½ρ·CdA·v²/m   using fit_drag_throttle's
    shared P + per-DRS CdA — the exploration's measured frontier (a=0 at vmax).
  * CURRENT sim drive:   a(v) = theta_P_mean/v − theta_D·ρ·v² − theta_R   using the
    deployed-power trajectory (what the simulator drives off today).
  * the 0.30×lateral traction cap (for reference).

Sanity question: does the anchored curve track the measured frontier (esp. the
low-speed roll-off), and how much does the current sim curve over-shoot there?
"""
from __future__ import annotations

import sys, warnings, logging
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
MASS = 808.0
YEAR, SESSION, DRV = 2023, "Q", "VER"
CACHE = str(REPO / "outputs" / "cache")
TRACKS = {"silverstone": ("Great Britain", "Silverstone", 1.1753),
          "monaco": ("Monaco", "Monaco", 1.19),
          "monza": ("Italy", "Monza", 1.16)}
TRACK = sys.argv[1] if len(sys.argv) > 1 else "silverstone"
GP, LABEL, RHO = TRACKS[TRACK]
OUT = str(REPO / ".agent-work" / "445" / f"throttle_frontier_{TRACK}.png")


def _build_control_df(session, drv_num, t0, t1, pad=2.0):
    cd = pd.DataFrame(session.car_data[drv_num]).copy()
    cd_t = cd["SessionTime"].dt.total_seconds().to_numpy()
    m = (cd_t >= t0 - pad) & (cd_t <= t1 + pad)
    cd = cd[m]
    if cd.empty:
        return pd.DataFrame()
    return pd.DataFrame({
        "session_time_ms": (cd_t[m] * 1000.0).astype(int),
        "throttle": cd["Throttle"].astype(float).values,
        "brake": (cd["Brake"].astype(float).values * 100.0 if cd["Brake"].max() <= 1.0
                  else cd["Brake"].astype(float).values),
        "gear": cd["nGear"].astype(float).values if "nGear" in cd.columns else 0.0,
        "drs": cd["DRS"].astype(float).values if "DRS" in cd.columns else 0.0,
    })


def frontier(v, a, q=0.90, lo=20, hi=100, step=6, minpts=6):
    vb, ab = [], []
    for left in np.arange(lo, hi, step):
        m = (v >= left) & (v < left + step)
        if int(m.sum()) >= minpts:
            vb.append(v[m].mean()); ab.append(np.quantile(a[m], q))
    return np.array(vb), np.array(ab)


def main():
    from src.preprocessing.trajectory.loaders import load_session, driver_num, driver_streams, stint_span
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.parameter_estimator import ParameterEstimator
    from src.physics.segment_classifier import SegmentClassifier
    from src.physics.control_alignment import ControlAlignment
    from src.physics.physics_config import PhysicsEstimatorConfig
    from src.physics.longitudinal_fit import LongitudinalFit
    from src.physics.regulation_era import RegulationEra

    q = load_session(YEAR, GP, SESSION, CACHE)
    era = RegulationEra.for_season(YEAR)
    num = driver_num(q, DRV)
    pos_d, spd_d = driver_streams(q, num)
    valid = q.laps.pick_drivers(DRV); valid = valid[valid["LapTime"].notna()]
    valid = valid[valid["LapTime"].dt.total_seconds() > 50]
    best = valid["LapTime"].dt.total_seconds().min()
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    flying = valid[valid["LapTime"].dt.total_seconds() <= 1.08 * best]
    st0, st1, _ = stint_span(q, DRV, int(fast["Stint"]), pad=2.0)
    mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1); mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
    hp = calibrate_session_hp(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp], spd_d["t"][mc], spd_d["V"][mc], order=4)

    cfg = PhysicsEstimatorConfig.from_config(); ca = ControlAlignment(cfg)
    span = {}; proc, ctrl = [], []
    for _, lap in flying.iterrows():
        sn = int(lap["Stint"])
        if sn not in span:
            s0, s1, _ = stint_span(q, DRV, sn, pad=2.0); span[sn] = (s0, s1)
        s0, s1 = span[sn]
        try:
            ss, info = fit_lap(pos_d, spd_d, float(lap["LapStartTime"].total_seconds()),
                               float(lap["Time"].total_seconds()), hp, overhang=8.0, bounds=(s0, s1))
            dfp = smoother_to_processed_telemetry(ss, info["lap_t"], driver_id=DRV, lap_number=int(lap["LapNumber"]))
        except Exception:
            continue
        cdf = _build_control_df(q, num, float(lap["LapStartTime"].total_seconds()), float(lap["Time"].total_seconds()))
        if not dfp.empty and not cdf.empty:
            proc.append(dfp); ctrl.append(cdf)
    processed = pd.concat(proc, ignore_index=True); control_df = pd.concat(ctrl, ignore_index=True)

    controls = ca.align_controls(processed["session_time_ms"].to_numpy(float), control_df)
    seg = SegmentClassifier(cfg).classify_samples(processed, controls)
    params = ParameterEstimator(cfg).estimate_parameters(processed, control_df=control_df,
                                                         weather={"air_density": RHO}, era=era)

    # throttle-regime samples (high throttle), DRS-split
    thr = [s for s in seg.get_regime("straight_throttle") if s.control.throttle_value >= 0.9]
    v = np.array([s.speed for s in thr]); a = np.array([s.a_longitudinal for s in thr])
    isopen = np.array([bool(s.control.drs) for s in thr])

    fit = LongitudinalFit(cfg).fit_drag_throttle(seg.get_regime("straight_throttle"), RHO)
    theta_P_mean = float(np.mean(params.longitudinal.theta_P_values))
    theta_P_max = float(params.longitudinal.max_power)
    theta_D = params.longitudinal.theta_D
    theta_R = params.longitudinal.theta_R

    print(f"[{LABEL}] throttle samples: {len(thr)} ({isopen.sum()} open / {(~isopen).sum()} closed)")
    if fit is not None:
        print(f"  joint fit: P={fit.power/1e3:.0f} kW (spec {fit.power/MASS:.0f})  "
              f"CdA_closed={fit.cda_closed:.2f}  CdA_open={fit.cda_open:.2f}")
    print(f"  sim power: theta_P mean={theta_P_mean:.0f} max={theta_P_max:.0f} (spec power)")

    vg = np.linspace(12, 95, 200)
    def drive_anchored(vv, cda):
        return fit.power / (MASS * vv) - 0.5 * RHO * cda * vv * vv / MASS
    def drive_current(vv):
        return theta_P_mean / vv - theta_D * RHO * vv * vv - theta_R
    lat = params.lateral
    trac_cap = np.array([0.30 * lat.lateral_capability(x, RHO) for x in vg])

    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.scatter(v[~isopen]*3.6, a[~isopen]/G, s=10, c="#c8a0a0", alpha=0.35, label="throttle samples (DRS closed)")
    ax.scatter(v[isopen]*3.6, a[isopen]/G, s=10, c="#9ec8e0", alpha=0.45, label="throttle samples (DRS open)")
    vb, ab = frontier(v[~isopen], a[~isopen]); ax.scatter(vb*3.6, ab/G, c="#c1272d", s=42, zorder=5, edgecolor="white", label="p90 frontier (closed)")
    vb, ab = frontier(v[isopen], a[isopen]); ax.scatter(vb*3.6, ab/G, c="#1f6fb2", s=42, zorder=5, edgecolor="white", label="p90 frontier (open)")
    if fit is not None:
        ax.plot(vg*3.6, drive_anchored(vg, fit.cda_closed)/G, "#c1272d", lw=2.6, label="ANCHORED joint-fit (closed)")
        ax.plot(vg*3.6, drive_anchored(vg, fit.cda_open)/G, "#1f6fb2", lw=2.6, label="ANCHORED joint-fit (open)")
    ax.plot(vg*3.6, drive_current(vg)/G, "k--", lw=2.4, label="CURRENT sim drive (theta_P mean)")
    ax.plot(vg*3.6, trac_cap/G, color="#7a4a00", lw=1.6, ls=":", label="0.30×lateral cap (current)")
    ax.axhline(0, color="#bbb", lw=0.8)
    ax.set_xlabel("speed (km/h)", fontsize=12); ax.set_ylabel("longitudinal acceleration (g)", fontsize=12)
    ax.set_title(f"Full-throttle acceleration frontier — VER {LABEL} {YEAR} Q\n"
                 "does the anchored joint-fit track the measured frontier? where does the current curve over-shoot?",
                 fontsize=12)
    ax.set_ylim(-0.1, max(1.6, np.percentile(a/G, 99)+0.2)); ax.set_xlim(40, 340)
    ax.legend(fontsize=8.5, loc="upper right"); ax.grid(alpha=0.25)
    plt.tight_layout(); plt.savefig(OUT, dpi=150, bbox_inches="tight"); print("wrote", OUT)


if __name__ == "__main__":
    main()
