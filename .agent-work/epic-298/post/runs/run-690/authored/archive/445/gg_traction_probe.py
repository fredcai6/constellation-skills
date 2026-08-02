"""#488 traction-cap calibration (scratch): the corner-exit g-g envelope.

Pulls CORNER-regime samples and plots longitudinal vs lateral acceleration,
NORMALISED by the fitted lateral grip G_lat(v) so all speeds collapse onto one
friction diagram:

    x = a_lat / G_lat(v)      (1.0 = full lateral grip, the apex)
    y = a_long / G_lat(v)      (>0 traction, <0 braking)

This directly answers the two open questions for the traction cap:
  1. What is the traction ratio?  -> the upper envelope of y at small x.
  2. Friction circle or not?      -> does the upper envelope fall off as
     y = r*sqrt(1-x^2) (ellipse) or stay flat y~r up to x->1 (no circle)?

Overlays candidate ratios r in {0.30, 0.40, 0.50} as ellipse curves and as flat
caps, plus the binned p90 traction frontier of the real data.
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
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

G = 9.81
YEAR, SESSION, DRV = 2023, "Q", "VER"
CACHE = str(REPO / "outputs" / "cache")
TRACKS = {"silverstone": ("Great Britain", "Silverstone", 1.1753),
          "monaco": ("Monaco", "Monaco", 1.19), "monza": ("Italy", "Monza", 1.16)}
TRACK = sys.argv[1] if len(sys.argv) > 1 else "silverstone"
GP, LABEL, RHO = TRACKS[TRACK]
OUT = str(REPO / ".agent-work" / "445" / f"gg_traction_{TRACK}.png")


def _ctrl(session, drv_num, t0, t1, pad=2.0):
    cd = pd.DataFrame(session.car_data[drv_num]).copy()
    t = cd["SessionTime"].dt.total_seconds().to_numpy(); m = (t >= t0 - pad) & (t <= t1 + pad)
    cd = cd[m]
    if cd.empty:
        return pd.DataFrame()
    return pd.DataFrame({"session_time_ms": (t[m]*1000).astype(int),
        "throttle": cd["Throttle"].astype(float).values,
        "brake": (cd["Brake"].astype(float).values*100 if cd["Brake"].max() <= 1 else cd["Brake"].astype(float).values),
        "gear": cd["nGear"].astype(float).values if "nGear" in cd.columns else 0.0,
        "drs": cd["DRS"].astype(float).values if "DRS" in cd.columns else 0.0})


def main():
    from src.preprocessing.trajectory.loaders import load_session, driver_num, driver_streams, stint_span
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.parameter_estimator import ParameterEstimator
    from src.physics.segment_classifier import SegmentClassifier
    from src.physics.control_alignment import ControlAlignment
    from src.physics.physics_config import PhysicsEstimatorConfig
    from src.physics.regulation_era import RegulationEra

    q = load_session(YEAR, GP, SESSION, CACHE); era = RegulationEra.for_season(YEAR)
    num = driver_num(q, DRV); pos_d, spd_d = driver_streams(q, num)
    valid = q.laps.pick_drivers(DRV); valid = valid[valid["LapTime"].notna()]
    valid = valid[valid["LapTime"].dt.total_seconds() > 50]
    best = valid["LapTime"].dt.total_seconds().min()
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    flying = valid[valid["LapTime"].dt.total_seconds() <= 1.08*best]
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
        cdf = _ctrl(q, num, float(lap["LapStartTime"].total_seconds()), float(lap["Time"].total_seconds()))
        if not dfp.empty and not cdf.empty:
            proc.append(dfp); ctrl.append(cdf)
    processed = pd.concat(proc, ignore_index=True); control_df = pd.concat(ctrl, ignore_index=True)
    controls = ca.align_controls(processed["session_time_ms"].to_numpy(float), control_df)
    seg = SegmentClassifier(cfg).classify_samples(processed, controls)
    params = ParameterEstimator(cfg).estimate_parameters(processed, control_df=control_df,
                                                         weather={"air_density": RHO}, era=era)
    lat = params.lateral

    corner = seg.get_regime("corner")
    v = np.array([s.speed for s in corner])
    alat = np.array([s.a_lateral for s in corner])
    along = np.array([s.a_longitudinal for s in corner])
    thr = np.array([s.control.throttle_value for s in corner])
    Glat = np.array([lat.lateral_capability(x, RHO) for x in v])
    xn = alat / np.maximum(Glat, 1e-6)        # lateral utilisation
    yn = along / np.maximum(Glat, 1e-6)        # longitudinal / lateral grip

    # traction frontier: p90 of yn (accelerating) per lateral-utilisation bin
    on = (yn > 0) & (thr > 0.2)
    xb, yb = [], []
    for lo in np.arange(0.0, 1.0, 0.1):
        m = on & (xn >= lo) & (xn < lo + 0.1)
        if m.sum() >= 8:
            xb.append((lo + 0.05)); yb.append(np.quantile(yn[m], 0.90))
    xb, yb = np.array(xb), np.array(yb)
    # pure-traction ratio estimate: p90 of yn at low lateral use (xn<0.3)
    r_meas = float(np.quantile(yn[on & (xn < 0.3)], 0.90)) if (on & (xn < 0.3)).sum() else float("nan")
    print(f"[{LABEL}] corner samples {len(corner)}, throttle-on accel {on.sum()}")
    print(f"  measured traction ratio (p90 a_long/G_lat at low lateral use): {r_meas:.2f}")
    print(f"  binned traction frontier yn: {np.round(yb,2)}")

    fig, ax = plt.subplots(figsize=(10.5, 8))
    norm = Normalize(40, 320); cmap = plt.cm.viridis
    ax.scatter(xn, yn, c=v*3.6, cmap=cmap, norm=norm, s=12, alpha=0.45, edgecolor="none")
    ax.scatter(xb, yb, c="k", s=55, zorder=6, marker="D", label="measured p90 traction frontier")
    xc = np.linspace(0, 1, 100)
    for r, col in [(0.30, "#c1272d"), (0.40, "#7a4a00"), (0.50, "#1f6fb2")]:
        ax.plot(xc, r*np.sqrt(np.maximum(1-xc**2, 0)), color=col, lw=2.0,
                label=f"ellipse r={r:.2f}  (friction circle ON)")
        ax.plot([0, 1], [r, r], color=col, lw=1.2, ls=":", alpha=0.7)
    ax.axhline(0, color="#bbb", lw=0.8); ax.axvline(1.0, color="#888", lw=1.0, ls="--")
    ax.text(1.005, ax.get_ylim()[1]*0.5, "lateral limit (apex)", rotation=90, fontsize=8, color="#555", va="center")
    ax.set_xlabel("a_lat / G_lat(v)   (lateral grip utilisation)", fontsize=12)
    ax.set_ylabel("a_long / G_lat(v)   (+traction / −braking)", fontsize=12)
    ax.set_title(f"Corner-exit g-g traction envelope (speed-normalised) — VER {LABEL} {YEAR} Q\n"
                 f"measured traction ratio at low lateral use ≈ {r_meas:.2f}  "
                 "(dotted = flat cap / no friction circle)", fontsize=11.5)
    ax.set_xlim(0, 1.25); ax.set_ylim(-0.2, 0.8)
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.02); cb.set_label("speed (km/h)")
    ax.legend(loc="upper right", fontsize=8.5); ax.grid(alpha=0.25)
    plt.tight_layout(); plt.savefig(OUT, dpi=150, bbox_inches="tight"); print("wrote", OUT)


if __name__ == "__main__":
    main()
