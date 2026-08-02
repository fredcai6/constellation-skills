"""#488 gg-v capability envelope — FIRST probe (scratch, untracked).

Assembles the per-speed capability envelope (the friction ellipse vs v) from a
REAL clean Q session run through the FULL production path (smoother → adapter →
ParameterEstimator), so it BOTH

  (a) discharges the #488 classifier-leak caveat — prints the corner-regime speed
      distribution; corner vmax must be sane corner speeds, NOT 330-350 km/h
      straights (the failure the loose `a_lat>5` proxy hit), and

  (b) shows the anisotropic gg-v picture for us to evaluate.

Anisotropic friction ellipse per speed v (the thing #488 builds):

  lateral semi-axis   = params.lateral.lateral_capability(v, rho)    [#487, MEASURED]
  braking semi-axis   = params.braking.a_brake(v)                    [Phase 5, MEASURED]
  traction semi-axis  = min(RATIO_TRAC * lateral(v),                 [GRIP-1 population ratio]
                            power/v - drag(v) - rolling)             [power cap, the NEW piece]

The braking axis is ALSO measured here, so we can compare the measured
braking-to-lateral ratio against the GRIP-1 population band (0.55-0.75) — a free
cross-check of the anisotropy prior.

Plot: the g-g diagram parameterised by speed (nested asymmetric ellipses, wider
on the braking side), with the real regime-coloured (a_lat, a_long) cloud overlaid
and shaded by speed on the same colormap (a point sits inside its own speed's
envelope when the fit + classifier are clean).
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
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

G = 9.81
YEAR, SESSION, DRV = 2023, "Q", "VER"
CACHE = str(REPO / "outputs" / "cache")

# track registry: key -> (FastF1 GP name, label, rho fallback if weather unloaded)
TRACKS = {
    "silverstone": ("Great Britain", "Silverstone", 1.1753),  # fast/balanced
    "spa": ("Belgium", "Spa", 1.1400),                          # power (altitude ~400m)
    "hungary": ("Hungary", "Hungary", 1.1600),                  # slow/downforce
}
TRACK = sys.argv[1] if len(sys.argv) > 1 else "silverstone"
GP, LABEL, RHO_FALLBACK = TRACKS[TRACK]
OUT = str(REPO / ".agent-work" / "445" / f"gg_envelope_{TRACK}.png")

# GRIP-1 population anisotropy ratios (× lateral), midpoints of the ratified bands.
RATIO_TRAC = 0.30   # band 0.25-0.40 ; traction is the noisy axis -> anchor to lateral
RATIO_BRAKE = 0.65  # band 0.55-0.75 ; used only as a fallback if braking didn't fit


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


def fit_session():
    """Run the full production chain over ALL flying Q laps (pooled).

    One flying lap gives ~10 brake samples — far too few for the braking
    frontier (needs >=4 bins x 8 pts) and thin for drag/power.  Pool every lap
    within 1.08x best (the grip-probe path) so all axes have enough samples,
    then run the estimator ONCE on the concatenated telemetry.

    Returns (params, segmented, rho, best_lap, config).
    """
    from src.preprocessing.trajectory.loaders import (
        load_session, driver_num, driver_streams, stint_span,
    )
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.parameter_estimator import ParameterEstimator
    from src.physics.segment_classifier import SegmentClassifier
    from src.physics.control_alignment import ControlAlignment
    from src.physics.physics_config import PhysicsEstimatorConfig
    from src.physics.regulation_era import RegulationEra
    from src.utils.environment import moist_air_density_from_pressure

    print(f"[load] {YEAR} {GP} {SESSION} ...")
    q = load_session(YEAR, GP, SESSION, CACHE)
    era = RegulationEra.for_season(YEAR)
    num = driver_num(q, DRV)

    try:
        wd = q.weather_data
        rho = moist_air_density_from_pressure(
            float(wd["Pressure"].median()) * 100.0,
            float(wd["AirTemp"].median()),
            float(wd["Humidity"].median()),
        )
    except Exception:
        rho = RHO_FALLBACK  # weather not loaded by load_session; per-track fallback
    print(f"[env] air density = {rho:.4f} kg/m^3")

    pos_d, spd_d = driver_streams(q, num)
    valid = q.laps.pick_drivers(DRV)
    valid = valid[valid["LapTime"].notna()]
    valid = valid[valid["LapTime"].dt.total_seconds() > 60]
    best = valid["LapTime"].dt.total_seconds().min()
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    flying = valid[valid["LapTime"].dt.total_seconds() <= 1.08 * best]
    print(f"[laps] best {best:.3f}s ; pooling {len(flying)} flying laps (<=1.08x best)")

    # calibrate HPs once on the fastest stint window, reuse across flying laps
    st0, st1, _ = stint_span(q, DRV, int(fast["Stint"]), pad=2.0)
    mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
    mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
    hp = calibrate_session_hp(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                              spd_d["t"][mc], spd_d["V"][mc], order=4)

    span: dict[int, tuple] = {}
    proc_parts, ctrl_parts = [], []
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
            dfp = smoother_to_processed_telemetry(ss, info["lap_t"],
                                                  driver_id=DRV, lap_number=int(lap["LapNumber"]))
        except Exception as e:
            print(f"  skip lap {int(lap['LapNumber'])}: {e}")
            continue
        cdf = _build_control_df(q, num, lap_t0, lap_t1)
        if dfp.empty or cdf.empty:
            continue
        proc_parts.append(dfp)
        ctrl_parts.append(cdf)

    processed = pd.concat(proc_parts, ignore_index=True)
    control_df = pd.concat(ctrl_parts, ignore_index=True)
    print(f"[pool] {len(proc_parts)} laps -> {len(processed)} telemetry rows")

    cfg = PhysicsEstimatorConfig.from_config()
    # Segment ourselves too, so we can plot the real cloud + run the caveat check
    # on EXACTLY the regimes the estimator uses (same classifier + config).
    ca = ControlAlignment(cfg)
    controls = ca.align_controls(processed["session_time_ms"].to_numpy(float), control_df)
    segmented = SegmentClassifier(cfg).classify_samples(processed, controls)

    estimator = ParameterEstimator(cfg)
    params = estimator.estimate_parameters(
        processed,
        control_df=control_df if not control_df.empty else None,
        weather={"air_density": rho},
        era=era,
    )
    return params, segmented, rho, best, cfg


def classifier_sanity(segmented, cfg):
    """Discharge the #488 caveat: corner regime must be genuine corners."""
    regimes = {}
    for s in segmented.samples:
        regimes.setdefault(s.regime, []).append(s)
    print("\n=== classifier sanity (the #488 caveat) ===")
    print(f"  straight_curvature_threshold = {cfg.straight_curvature_threshold:.2e} /m "
          f"(radius >= {1.0/cfg.straight_curvature_threshold:.0f} m => 'straight')")
    for r in ("corner", "straight_throttle", "straight_brake", "straight_coast"):
        ss = regimes.get(r, [])
        if not ss:
            print(f"  {r:18s}: n=0")
            continue
        v = np.array([s.speed for s in ss]) * 3.6
        print(f"  {r:18s}: n={len(ss):4d}  v[min/med/p95/max] = "
              f"{v.min():5.0f}/{np.median(v):5.0f}/{np.percentile(v,95):5.0f}/{v.max():5.0f} km/h")
    # Caveat verdict: a LEAK puts straights (near-zero a_lat) into the corner
    # regime, so the corner cloud would reach straight-line top speed AND its
    # top-speed members would carry ~no lateral g.  The defense holds if (a)
    # corners cap below the throttle-straight top speed and (b) the fastest
    # corner samples still pull real lateral g.
    corner = regimes.get("corner", [])
    thr = regimes.get("straight_throttle", [])
    if corner and thr:
        cv = np.array([s.speed for s in corner]) * 3.6
        tv = np.array([s.speed for s in thr]) * 3.6
        ca_top = np.array([s.a_lateral for s in corner])[cv >= np.percentile(cv, 90)] / G
        margin = tv.max() - cv.max()
        clean = margin > 8 and np.median(ca_top) > 2.0
        print(f"  --> corner vmax {cv.max():.0f} vs throttle-straight vmax {tv.max():.0f} km/h "
              f"(margin {margin:+.0f}); top-decile corner a_lat median {np.median(ca_top):.1f} g")
        print(f"  --> VERDICT: {'CLEAN — classifier holds, no straight leak' if clean else 'INSPECT — possible leak'}")
    return regimes


def assemble_and_plot(params, regimes, rho, lap_dur):
    lat = params.lateral
    lon = params.longitudinal
    brk = params.braking
    power = lon.max_power

    def a_lat_max(v):
        return lat.lateral_capability(v, rho)

    def a_brake_meas(v):
        return brk.a_brake(v) if brk is not None else RATIO_BRAKE * a_lat_max(v)

    def a_brake_ratio(v):  # population-prior braking axis (GRIP-1, Decision 1)
        return RATIO_BRAKE * a_lat_max(v)

    # ---- OPTION 2 GUARD (settled on #488): use the measured braking frontier
    # only when it is physical (b_b >= 0) and passed the estimator SNR gate;
    # otherwise source braking from the population ratio (0.65 x lateral).
    brake_use_measured = brk is not None and brk.b_b >= 0.0

    def a_brake_env(v):
        return a_brake_meas(v) if brake_use_measured else a_brake_ratio(v)

    def a_trac_max(v):
        grip = RATIO_TRAC * a_lat_max(v)
        drive = power / max(v, 1e-3) - lon.drag_acceleration(v, rho) - lon.theta_R
        return max(0.0, min(grip, drive))

    print("\n=== fitted axes ===")
    print(f"  lateral:  A0={lat.A0:.2f}  A2={lat.A2:.2e}  ceiling="
          f"{'%.2f g' % (lat.ceiling/G) if lat.ceiling else 'None'}  "
          f"aero_identifiable={lat.aero_identifiable}")
    print(f"  braking:  source={'frontier' if brk else 'CONSTANT-fallback'}", end="")
    if brk is not None:
        print(f"  a_b={brk.a_b:.2f}  b_b={brk.b_b:.2e}")
    else:
        print()
    cda_closed = 2 * 808.0 * lon.theta_D
    src = params.fit_quality_metrics.get("theta_D_source", "?")
    if lon.theta_D_open is not None:
        cda_open = 2 * 808.0 * lon.theta_D_open
        drs_cut = (1.0 - cda_open / cda_closed) * 100.0
        drs_str = f"CdA_open={cda_open:.3f} m^2  (DRS cut {drs_cut:+.0f}%)"
    else:
        drs_str = "CdA_open=None (no DRS lever resolved)"
    print(f"  drag:     theta_D={lon.theta_D:.5f}  CdA_closed={cda_closed:.3f} m^2  {drs_str}  "
          f"[source={src}]")
    print(f"  power:    specific_power={power:.0f} m^2/s^3")

    # measured braking-to-lateral ratio vs the GRIP-1 band, sampled across speed
    if brk is not None:
        vs = np.linspace(30, 90, 7)
        ratios = [a_brake_meas(v) / max(a_lat_max(v), 1e-6) for v in vs]
        print(f"  measured braking/lateral ratio over 110-320 km/h: "
              f"{np.min(ratios):.2f}-{np.max(ratios):.2f}  (GRIP-1 band 0.55-0.75)")
    print(f"  --> braking axis source: "
          f"{'MEASURED frontier (b_b>=0, SNR ok)' if brake_use_measured else 'POPULATION RATIO 0.65xlateral (measured b_b<0 rejected)'}")

    # per-speed-bin frontier of the real cloud (upper quantile per bin)
    def binned_frontier(samples, value_fn, q=0.90, lo=15, hi=95, step=8, minpts=6):
        if not samples:
            return np.array([]), np.array([])
        v = np.array([s.speed for s in samples])
        y = np.array([value_fn(s) for s in samples])
        vb, yb = [], []
        for left in np.arange(lo, hi, step):
            m = (v >= left) & (v < left + step)
            if int(m.sum()) >= minpts:
                vb.append(v[m].mean()); yb.append(np.quantile(y[m], q))
        return np.array(vb), np.array(yb)

    # ---------------------------------------------------------------- figure
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(16, 7.2),
                                   gridspec_kw=dict(width_ratios=[1.05, 1]))

    # ===== LEFT: the assembled g-g envelope at three speeds =====
    speeds_kmh = [80, 150, 250]
    norm = Normalize(vmin=60, vmax=270)
    cmap = plt.cm.viridis
    th = np.linspace(0, 2 * np.pi, 400)
    low = th[np.sin(th) < 0]
    for skmh in speeds_kmh:
        v = skmh / 3.6
        al, at = a_lat_max(v) / G, a_trac_max(v) / G
        ab_env, ab_m = a_brake_env(v) / G, a_brake_meas(v) / G
        color = cmap(norm(skmh))
        x = al * np.cos(th)
        # THE envelope (option-2 guarded braking): traction up, guarded brake down
        y_env = np.where(np.sin(th) >= 0, at, ab_env) * np.sin(th)
        axL.fill(np.r_[x, -x], np.r_[y_env, y_env], color=color, alpha=0.10, zorder=2)
        axL.plot(np.r_[x, -x], np.r_[y_env, y_env], color=color, lw=2.6, zorder=4,
                 label=f"{skmh} km/h")
        # rejected measured braking (faint dotted, bottom only) for transparency
        if not brake_use_measured:
            axL.plot(np.r_[al * np.cos(low), -al * np.cos(low)],
                     np.r_[ab_m * np.sin(low), ab_m * np.sin(low)],
                     color=color, lw=1.0, ls=":", alpha=0.6, zorder=3)
    axL.axhline(0, color="#ccc", lw=0.8); axL.axvline(0, color="#ccc", lw=0.8)
    axL.annotate("traction\n(power-capped\nat high speed)", xy=(0.2, a_trac_max(80/3.6)/G),
                 xytext=(1.7, 1.15), fontsize=9, color="#225522", ha="center",
                 arrowprops=dict(arrowstyle="->", color="#225522", lw=1.2))
    brake_msg = ("braking = 0.65×lateral PRIOR\n(measured frontier rejected: b_b<0;\nshown dotted)"
                 if not brake_use_measured else "braking = MEASURED frontier\n(b_b≥0, SNR ok)")
    axL.annotate(brake_msg, xy=(-0.2, -a_brake_env(150/3.6)/G), xytext=(-2.4, -3.3),
                 fontsize=8.5, color="#992222", ha="center",
                 arrowprops=dict(arrowstyle="->", color="#992222", lw=1.2))
    axL.set_xlabel("lateral  a_lat  (g)", fontsize=12)
    axL.set_ylabel("longitudinal  a_long  (g)     ←braking      traction→", fontsize=12)
    axL.set_title("Assembled gg-v envelope (3 speeds, option-2 braking)\n"
                  "anisotropic ellipse; downforce grows it, power caps traction", fontsize=11)
    axL.legend(loc="upper left", fontsize=9, title="capability @ speed")
    axL.grid(True, alpha=0.25); axL.set_axisbelow(True)

    # ===== RIGHT: per-axis frontiers vs speed (each axis evaluable) =====
    vg = np.linspace(15, 92, 200); vg_k = vg * 3.6
    axR.plot(vg_k, [a_lat_max(v) / G for v in vg], color="#1f6fb2", lw=2.6, label="lateral grip (measured #487)")
    axR.plot(vg_k, [a_trac_max(v) / G for v in vg], color="#2a9d3a", lw=2.6, label="traction = 0.30×lat ∩ power")
    meas_used = brake_use_measured
    axR.plot(vg_k, [a_brake_meas(v) / G for v in vg], color="#c1272d",
             lw=2.6 if meas_used else 1.3, ls="-" if meas_used else ":",
             label=f"braking MEASURED (Phase 5){' ← USED' if meas_used else ' (rejected: b_b<0)'}")
    axR.plot(vg_k, [a_brake_ratio(v) / G for v in vg], color="#c1272d",
             lw=1.6 if meas_used else 2.6, ls=(0, (4, 3)) if meas_used else "-",
             label=f"braking 0.65×lateral prior{' ← USED' if not meas_used else ''}")
    # cloud frontier points
    vb, yb = binned_frontier(regimes.get("corner", []), lambda s: s.a_lateral)
    if vb.size: axR.scatter(vb * 3.6, yb / G, c="#1f6fb2", s=28, zorder=5, edgecolor="white", lw=0.5)
    vb, yb = binned_frontier(regimes.get("straight_brake", []), lambda s: -s.a_longitudinal)
    if vb.size: axR.scatter(vb * 3.6, yb / G, c="#c1272d", s=28, zorder=5, edgecolor="white", lw=0.5)
    vb, yb = binned_frontier(regimes.get("straight_throttle", []), lambda s: s.a_longitudinal)
    if vb.size: axR.scatter(vb * 3.6, yb / G, c="#2a9d3a", s=28, zorder=5, edgecolor="white", lw=0.5)
    axR.set_xlabel("speed (km/h)", fontsize=12)
    axR.set_ylabel("capability (g)", fontsize=12)
    axR.set_title("Per-axis frontiers vs speed\n(points = binned cloud frontier; lines = fits)", fontsize=11)
    axR.legend(loc="upper left", fontsize=9)
    axR.grid(True, alpha=0.25); axR.set_axisbelow(True)
    axR.set_ylim(0, None)

    fig.suptitle(f"gg-v capability envelope — VER · {LABEL} 2023 Q  "
                 "(pooled flying laps, full production path)", fontsize=13, weight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    plt.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"\nwrote {OUT}")


def main():
    params, segmented, rho, lap_dur, cfg = fit_session()
    regimes = classifier_sanity(segmented, cfg)
    assemble_and_plot(params, regimes, rho, lap_dur)


if __name__ == "__main__":
    main()
