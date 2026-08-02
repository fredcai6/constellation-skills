"""Production vs Exploration Validation — Multi-round, Full Field, Checkpointed.

Runs the FULL production chain (smoother calibration → StintSmoother fit →
physics_adapter → ParameterEstimator → apex_extract → capability.apex_pace)
on the fastest Q lap for ALL drivers across multiple 2023 rounds, then
compares per-team CdA ordering and apex_pace to the exploration artifacts
(season_drs.json and apex_feature.json).

Phase 1 (extraction): heavy checkpointed loop.  Checkpoint is persisted per-driver
    to .agent-work/445/validation_extraction.json; re-runs resume automatically.

Phase 2 (comparison): cheap aggregation + Spearman; appends a section to
    PRODUCTION_VS_EXPLORATION_VALIDATION.md.

Usage:
    # Smoke test (one round)
    py .agent-work/445/validate_production_vs_exploration.py --rounds Japanese

    # Full 6-round extraction (orchestrator runs this as background process)
    py .agent-work/445/validate_production_vs_exploration.py

    # Phase 2 only (re-read checkpoint, produce report without re-extracting)
    py .agent-work/445/validate_production_vs_exploration.py --phase2-only
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("src").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default season-spanning subset.  Each name must match a key in season_drs.json
# AND a valid FastF1 GP name for 2023.
DEFAULT_ROUNDS = ["Bahrain", "Spanish", "Austrian", "Italian", "Japanese", "Mexico City"]

YEAR = 2023
SESSION_TYPE = "Q"
CACHE_PATH = str(REPO / "outputs" / "cache")

MASS_KG = 808.0  # CdA = 2 * MASS_KG * theta_D

EXPLORATION_SEASON_DRS = REPO / ".agent-work" / "445" / "envelope" / "season_drs.json"
EXPLORATION_APEX = REPO / ".agent-work" / "445" / "envelope" / "apex_feature.json"
OUTPUT_MD = REPO / ".agent-work" / "445" / "PRODUCTION_VS_EXPLORATION_VALIDATION.md"
CHECKPOINT_JSON = REPO / ".agent-work" / "445" / "validation_extraction.json"

# Speed sanity: record inflation events but do NOT retry (production floor handles it)
_P99_SPEED_LIMIT = 120.0  # m/s

# ---------------------------------------------------------------------------
# Team abbreviation map: FastF1 TeamName -> exploration team key
# ---------------------------------------------------------------------------
TEAM_MAP = {
    "Red Bull Racing": "RBR",
    "Ferrari": "FER",
    "Mercedes": "MERC",
    "McLaren": "MCL",
    "Aston Martin": "AMR",
    "Alpine": "ALP",
    "Williams": "WIL",
    "AlphaTauri": "ATR",
    "Alfa Romeo": "ALF",
    "Haas F1 Team": "HAA",
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def spearman(x_dict: dict, y_dict: dict) -> float | None:
    """Spearman correlation over keys common to both dicts."""
    common = sorted(set(x_dict) & set(y_dict))
    if len(common) < 3:
        return None
    x = np.array([x_dict[k] for k in common], dtype=float)
    y = np.array([y_dict[k] for k in common], dtype=float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    cov = np.mean((rx - rx.mean()) * (ry - ry.mean()))
    std_x = rx.std() + 1e-12
    std_y = ry.std() + 1e-12
    return float(cov / (std_x * std_y))


def _checkpoint_key(round_name: str, abbrev: str) -> str:
    return f"{round_name}|{abbrev}"


def load_checkpoint() -> dict[str, Any]:
    if CHECKPOINT_JSON.exists():
        with open(CHECKPOINT_JSON, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(checkpoint: dict[str, Any]) -> None:
    with open(CHECKPOINT_JSON, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=2)


def apex_obs_to_dicts(apex_obs_list: list) -> list[dict]:
    """Serialize ApexObservation objects to plain dicts for JSON storage."""
    return [
        {
            "v_apex": float(o.v_apex),
            "radius_m": float(o.radius_m),
            "a_lat": float(o.a_lat),
            "on_limit": bool(o.on_limit),
            "corner_index": int(o.corner_index),
        }
        for o in apex_obs_list
    ]


# ---------------------------------------------------------------------------
# Per-driver extraction (keep the working body from original script)
# ---------------------------------------------------------------------------

def _build_control_df(session, drv_num: str, t0: float, t1: float, pad: float = 2.0):
    """Build a control_df from FastF1 car_data for one driver's lap window."""
    import pandas as pd
    cd = pd.DataFrame(session.car_data[drv_num]).copy()
    cd_t = cd["SessionTime"].dt.total_seconds().to_numpy()
    mask = (cd_t >= t0 - pad) & (cd_t <= t1 + pad)
    cd_lap = cd[mask].copy()
    if cd_lap.empty:
        return pd.DataFrame()
    out = pd.DataFrame({
        "session_time_ms": (cd_t[mask] * 1000.0).astype(int),
        "throttle": cd_lap["Throttle"].astype(float).values,
        "brake": (cd_lap["Brake"].astype(float).values * 100.0
                  if cd_lap["Brake"].max() <= 1.0
                  else cd_lap["Brake"].astype(float).values),
        "gear": cd_lap["nGear"].astype(float).values if "nGear" in cd_lap.columns else 0.0,
        "drs": cd_lap["DRS"].astype(float).values if "DRS" in cd_lap.columns else 0.0,
    })
    return out


def process_driver(
    session,
    abbrev: str,
    drv_num: str,
    rho: float,
    era,
    round_name: str,
    team_key: str,
) -> dict:
    """Run the full production chain for one driver's fastest Q lap.

    Returns a serialisable dict.  On failure: {'driver': ..., 'error': ..., ...}.
    NOTE: ell_retry workaround REMOVED — production calibration floor handles it.
    A speed_inflation flag is RECORDED if p99 > 120 m/s but we do NOT retry.
    """
    from src.preprocessing.trajectory.loaders import driver_streams
    from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp
    from src.preprocessing.trajectory.smoother import StintSmoother
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.parameter_estimator import ParameterEstimator
    from src.physics.apex_extract import extract_apex_observations

    try:
        # --- Pick fastest FLYING Q lap ---
        laps = session.laps.pick_drivers(abbrev)
        valid = laps.dropna(subset=["LapTime"])
        valid = valid[valid["LapTime"].dt.total_seconds() > 60]
        if len(valid) == 0:
            return {"driver": abbrev, "round": round_name, "team": team_key,
                    "error": "no_valid_laps"}
        fast = valid.loc[valid["LapTime"].idxmin()]
        lap_t0 = float(fast["LapStartTime"].total_seconds())
        lap_t1 = float(fast["Time"].total_seconds())
        lap_num = int(fast["LapNumber"])
        lap_dur = lap_t1 - lap_t0

        # --- Raw streams ---
        pos_d, spd_d = driver_streams(session, drv_num)
        tp, Xm, Ym = pos_d["t"], pos_d["X"], pos_d["Y"]
        tc, Vm = spd_d["t"], spd_d["V"]

        # Clip to the flying lap window (±2s padding for edge effects)
        pad = 2.0
        mp = (tp >= lap_t0 - pad) & (tp <= lap_t1 + pad)
        mc = (tc >= lap_t0 - pad) & (tc <= lap_t1 + pad)
        if mp.sum() < 50 or mc.sum() < 20:
            return {"driver": abbrev, "round": round_name, "team": team_key,
                    "error": "too_few_samples",
                    "n_pos": int(mp.sum()), "n_spd": int(mc.sum())}

        tp_l, X_l, Y_l = tp[mp], Xm[mp], Ym[mp]
        tc_l, V_l = tc[mc], Vm[mc]

        # --- Session offset (calibrate inter-stream timing) ---
        delta, _ = session_offset([(tp_l, X_l, Y_l, tc_l, V_l)])

        # --- Calibrate smoother HPs (production floor: max(1.0, 6·dt_median)) ---
        hp = fit_stint_hp(tp_l, X_l, Y_l, tc_l, V_l, delta=delta, iters=3)
        if hp is None:
            return {"driver": abbrev, "round": round_name, "team": team_key,
                    "error": "hp_calibration_failed"}

        # Use calibrated ell DIRECTLY — no workaround, production floor handles it
        ell_used = float(hp["ell"])

        # --- Fit smoother and build processed_telemetry ---
        smoother = StintSmoother(ell_used, hp["sf"], hp["sig_pos"], hp["delta"], iters=3)
        smoother.fit(tp_l, X_l, Y_l, tc_l, V_l)

        qm = (tp >= lap_t0) & (tp <= lap_t1)
        tp_q = tp[qm]
        if len(tp_q) < 10:
            tp_q = tp_l  # fallback: use full clipped window

        processed = smoother_to_processed_telemetry(
            smoother, tp_q,
            driver_id=abbrev,
            lap_number=lap_num,
        )

        # Speed sanity check: RECORD inflation flag, do NOT retry
        p99 = float(processed["speed_ms"].quantile(0.99))
        speed_inflation = p99 > _P99_SPEED_LIMIT

        # If still inflated after production floor, record it but continue
        # (if the fix works this rarely fires; if it fires, that's data)

        # --- Build control_df ---
        control_df = _build_control_df(session, drv_num, lap_t0, lap_t1)

        # --- Physics parameter estimation ---
        estimator = ParameterEstimator()
        params = estimator.estimate_parameters(
            processed,
            control_df=control_df if not control_df.empty else None,
            weather={"air_density": rho},
            era=era,
        )

        theta_D = params.longitudinal.theta_D
        fallback_long = bool(params.fit_quality_metrics.get("fallback_longitudinal", True))
        theta_D_source = str(params.fit_quality_metrics.get("theta_D_source", "unknown"))
        fallback_reason = params.fit_quality_metrics.get("fallback_reason_longitudinal")
        CdA = 2.0 * MASS_KG * theta_D

        # --- Apex observations ---
        apex_obs = extract_apex_observations(
            processed,
            air_density=rho,
            lateral_envelope=params.lateral if not bool(
                params.fit_quality_metrics.get("fallback_lateral", True)
            ) else None,
        )

        return {
            "driver": abbrev,
            "round": round_name,
            "team": team_key,
            "theta_D": float(theta_D),
            "CdA": float(CdA),
            "fallback_longitudinal": fallback_long,
            "theta_D_source": theta_D_source,
            "fallback_reason": str(fallback_reason) if fallback_reason is not None else None,
            "fallback_lateral": bool(params.fit_quality_metrics.get("fallback_lateral", True)),
            "p99_speed": p99,
            "speed_inflation": speed_inflation,
            "ell_used": ell_used,
            "chi2": float(hp.get("chi2_pos", float("nan"))),
            "n_apex": len(apex_obs),
            "n_on_limit": sum(1 for o in apex_obs if o.on_limit),
            "apex_obs": apex_obs_to_dicts(apex_obs),
            "lap_time_s": float(lap_dur),
            "error": None,
        }

    except Exception as exc:
        return {
            "driver": abbrev,
            "round": round_name,
            "team": team_key,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Phase 1: extraction loop
# ---------------------------------------------------------------------------

def run_phase1(rounds: list[str]) -> None:
    from src.preprocessing.trajectory.loaders import enable_cache
    from src.physics.regulation_era import RegulationEra
    from src.utils.environment import moist_air_density_from_pressure
    import fastf1

    log("Phase 1: extraction")
    enable_cache(CACHE_PATH)
    try:
        fastf1.Cache.offline_mode(True)
    except AttributeError:
        pass

    era = RegulationEra.for_season(YEAR)
    log(f"RegulationEra: drs_enabled={era.drs_enabled}, mguk_regen={era.mguk_regen}")

    # Load checkpoint (supports resume)
    checkpoint = load_checkpoint()
    log(f"Checkpoint: {len(checkpoint)} entries already done")

    for round_name in rounds:
        log(f"\n=== Loading {YEAR} {round_name} Q (offline cache) ===")
        try:
            session = fastf1.get_session(YEAR, round_name, SESSION_TYPE)
            session.load(telemetry=True, laps=True, weather=True, messages=False)
        except Exception as exc:
            log(f"  FAILED to load session: {exc}")
            continue

        log(f"  Session loaded: {len(session.drivers)} drivers")

        # Air density from measured weather
        wd = session.weather_data
        pressure_mbar = float(wd["Pressure"].median())
        temp_c = float(wd["AirTemp"].median())
        humidity_pct = float(wd["Humidity"].median())
        rho = moist_air_density_from_pressure(pressure_mbar * 100.0, temp_c, humidity_pct)
        log(f"  Air density: {rho:.4f} kg/m³ (P={pressure_mbar:.1f} mbar, "
            f"T={temp_c:.1f}°C, RH={humidity_pct:.0f}%)")

        # Full field: all drivers in this session
        for drv_num in session.drivers:
            try:
                info = session.get_driver(drv_num)
            except Exception:
                log(f"    Skipping driver {drv_num}: get_driver failed")
                continue

            abbrev = info.get("Abbreviation", drv_num)
            team_name = info.get("TeamName", "Unknown")
            team_key = TEAM_MAP.get(team_name, team_name)

            key = _checkpoint_key(round_name, abbrev)
            if key in checkpoint:
                log(f"  SKIP {abbrev} ({round_name}) — already in checkpoint")
                continue

            log(f"  Processing {abbrev} ({team_key}, drv={drv_num}) [{round_name}] ...")
            t_start = time.time()
            result = process_driver(session, abbrev, drv_num, rho, era, round_name, team_key)
            elapsed = time.time() - t_start

            if result.get("error"):
                log(f"    FAILED: {result['error']} ({elapsed:.1f}s)")
            else:
                inflation_note = " SPEED_INFLATION" if result.get("speed_inflation") else ""
                log(f"    OK: theta_D={result['theta_D']:.5f} CdA={result['CdA']:.4f} "
                    f"fallback={result['fallback_longitudinal']} "
                    f"src={result['theta_D_source']} "
                    f"n_apex={result['n_apex']} on_limit={result['n_on_limit']} "
                    f"ell={result['ell_used']:.2f} chi2={result['chi2']:.2f}"
                    f"{inflation_note} ({elapsed:.1f}s)")

            # Flush after each driver — critical for resumability
            checkpoint[key] = result
            save_checkpoint(checkpoint)

    log(f"\nPhase 1 complete. Checkpoint: {len(checkpoint)} entries.")


# ---------------------------------------------------------------------------
# Phase 2: comparison + report
# ---------------------------------------------------------------------------

def run_phase2(rounds: list[str]) -> None:
    from src.physics.capability import apex_pace
    from src.physics.apex_extract import ApexObservation

    log("\nPhase 2: comparison")

    # Load checkpoint
    checkpoint = load_checkpoint()
    if not checkpoint:
        log("ERROR: checkpoint is empty — run Phase 1 first.")
        return

    # Load exploration artifacts
    with open(EXPLORATION_SEASON_DRS, encoding="utf-8") as f:
        season_drs = json.load(f)
    with open(EXPLORATION_APEX, encoding="utf-8") as f:
        apex_feat = json.load(f)

    expl_apex_q90: dict[str, float] = apex_feat.get("apex_speed_q90", {})
    expl_quali_pace: dict[str, float] = apex_feat.get("quali_pace", {})

    # Confirm requested rounds exist in season_drs.json
    missing_drs_rounds = [r for r in rounds if r not in season_drs]
    if missing_drs_rounds:
        log(f"WARNING: rounds not in season_drs.json: {missing_drs_rounds}")

    # Rebuild per-round per-team CdA and apex obs from checkpoint
    # Structure: round -> team -> [CdA values], team -> [ApexObservation]
    round_team_cda: dict[str, dict[str, list[float]]] = {}
    # Per-round apex obs: round -> team -> [ApexObservation]
    round_team_apex: dict[str, dict[str, list]] = {}

    n_total = 0
    n_error = 0
    n_fallback_long = 0
    n_speed_inflation = 0
    rounds_seen: set[str] = set()
    drivers_seen: set[str] = set()

    for key, result in checkpoint.items():
        round_name = result.get("round", "")
        if round_name not in rounds:
            continue  # only aggregate requested rounds
        rounds_seen.add(round_name)
        abbrev = result.get("driver", key.split("|")[-1])
        drivers_seen.add(f"{round_name}|{abbrev}")
        n_total += 1

        if result.get("error"):
            n_error += 1
            continue

        team = result.get("team", "?")

        if result.get("speed_inflation"):
            n_speed_inflation += 1

        # Drag: only use non-fallback fits
        if not result.get("fallback_longitudinal", True):
            cda = result.get("CdA")
            if cda is not None and np.isfinite(cda) and cda > 0:
                round_team_cda.setdefault(round_name, {}).setdefault(team, []).append(float(cda))
        else:
            n_fallback_long += 1

        # Apex observations: per round (reconstruct from dicts)
        for obs_d in result.get("apex_obs", []):
            ao = ApexObservation(
                v_apex=obs_d["v_apex"],
                radius_m=obs_d["radius_m"],
                a_lat=obs_d["a_lat"],
                on_limit=obs_d["on_limit"],
                corner_index=obs_d["corner_index"],
            )
            round_team_apex.setdefault(round_name, {}).setdefault(team, []).append(ao)

    n_drivers = len(drivers_seen)
    n_rounds = len(rounds_seen)
    fallback_rate = (n_fallback_long + n_error) / n_total if n_total > 0 else float("nan")
    inflation_rate = n_speed_inflation / n_total if n_total > 0 else float("nan")

    log(f"  Checkpoint entries used: {n_total} ({n_rounds} rounds, {n_drivers} driver-rounds)")
    log(f"  Errors: {n_error}, Fallback (long): {n_fallback_long}, "
        f"Speed inflation: {n_speed_inflation}")
    log(f"  Fallback rate (error+fallback): {fallback_rate:.1%}")
    log(f"  Speed inflation rate: {inflation_rate:.1%}")

    # Per-round Spearman: prod avg CdA per team vs exploration CdA_closed
    per_round_drag_spearman: dict[str, float | None] = {}
    per_round_n_teams: dict[str, int] = {}

    for round_name in sorted(rounds_seen):
        expl_cda_round = season_drs.get(round_name, {})
        if not expl_cda_round:
            log(f"  {round_name}: no exploration CdA data, skipping drag comparison")
            per_round_drag_spearman[round_name] = None
            continue

        expl_cda_by_team = {team: float(vals[0]) for team, vals in expl_cda_round.items()}

        team_cda_map = round_team_cda.get(round_name, {})
        prod_cda_by_team = {
            team: float(np.mean(vals)) for team, vals in team_cda_map.items()
        }

        rho_drag = spearman(prod_cda_by_team, expl_cda_by_team)
        n_common = len(set(prod_cda_by_team) & set(expl_cda_by_team))
        per_round_drag_spearman[round_name] = rho_drag
        per_round_n_teams[round_name] = n_common
        log(f"  {round_name}: drag Spearman={rho_drag} (n={n_common} teams)")

    # Apex_pace PER ROUND (matching the exploration's per-weekend regression),
    # then SEASON-MEDIAN per team.  Pooling all rounds into ONE regression mixes
    # different track geometries into the shared β·log R fit and contaminates the
    # per-car intercept — that produced the spurious near-zero pooled result.
    from types import SimpleNamespace
    log("\nRunning capability.apex_pace PER ROUND, then season-median per team ...")
    team_round_pace: dict[str, list[float]] = {}
    team_on_limit: dict[str, int] = {}
    for round_name, team_obs in round_team_apex.items():
        try:
            round_pace = apex_pace(team_obs, min_apexes=5)
        except Exception as exc:
            log(f"  {round_name}: apex_pace failed: {exc}")
            continue
        for team, ap in round_pace.items():
            team_round_pace.setdefault(team, []).append(ap.pace)
        for team, obs in team_obs.items():
            team_on_limit[team] = team_on_limit.get(team, 0) + sum(1 for o in obs if o.on_limit)
    prod_apex_pace_by_team: dict[str, float] = {
        team: float(np.median(paces)) for team, paces in team_round_pace.items() if paces
    }
    prod_apex = {team: SimpleNamespace(n_on_limit=team_on_limit.get(team, 0))
                 for team in prod_apex_pace_by_team}
    log(f"  Teams with apex_pace (season-median over {len(round_team_apex)} rounds): "
        f"{sorted(prod_apex_pace_by_team.keys())}")

    rho_apex_q90 = spearman(prod_apex_pace_by_team, expl_apex_q90)
    rho_apex_quali = spearman(prod_apex_pace_by_team, expl_quali_pace)
    n_apex_common = len(set(prod_apex_pace_by_team) & set(expl_apex_q90))
    n_quali_common = len(set(prod_apex_pace_by_team) & set(expl_quali_pace))

    log(f"\nPer-round-median apex_pace vs expl apex_speed_q90: {rho_apex_q90} (n={n_apex_common})")
    log(f"Per-round-median apex_pace vs quali_pace: {rho_apex_quali} (n={n_quali_common})")

    # Append richer validation section to output MD
    _append_richer_section(
        rounds=sorted(rounds_seen),
        per_round_drag_spearman=per_round_drag_spearman,
        per_round_n_teams=per_round_n_teams,
        rho_apex_q90=rho_apex_q90,
        rho_apex_quali=rho_apex_quali,
        n_apex_common=n_apex_common,
        n_quali_common=n_quali_common,
        n_total=n_total,
        n_error=n_error,
        n_fallback_long=n_fallback_long,
        n_speed_inflation=n_speed_inflation,
        fallback_rate=fallback_rate,
        inflation_rate=inflation_rate,
        prod_apex_pace_by_team=prod_apex_pace_by_team,
        expl_apex_q90=expl_apex_q90,
        expl_quali_pace=expl_quali_pace,
        prod_apex=prod_apex,
        round_team_cda=round_team_cda,
        season_drs=season_drs,
    )
    log(f"\nReport section appended to {OUTPUT_MD}")


# ---------------------------------------------------------------------------
# Report writing (Phase 2)
# ---------------------------------------------------------------------------

def _fmt(v: float | None) -> str:
    if v is None:
        return "n/a"
    if not np.isfinite(v):
        return "n/a"
    return f"{v:+.3f}"


def _append_richer_section(
    rounds: list[str],
    per_round_drag_spearman: dict,
    per_round_n_teams: dict,
    rho_apex_q90: float | None,
    rho_apex_quali: float | None,
    n_apex_common: int,
    n_quali_common: int,
    n_total: int,
    n_error: int,
    n_fallback_long: int,
    n_speed_inflation: int,
    fallback_rate: float,
    inflation_rate: float,
    prod_apex_pace_by_team: dict,
    expl_apex_q90: dict,
    expl_quali_pace: dict,
    prod_apex: dict,
    round_team_cda: dict,
    season_drs: dict,
) -> None:
    # Per-round drag table
    drag_rows = []
    for rnd in rounds:
        sp = per_round_drag_spearman.get(rnd)
        n = per_round_n_teams.get(rnd, 0)
        drag_rows.append(f"| {rnd} | {_fmt(sp)} | {n} |")

    # Per-team pooled apex_pace table
    apex_rows = []
    common_apex = sorted(set(prod_apex_pace_by_team) & set(expl_apex_q90))
    for team in sorted(common_apex, key=lambda t: prod_apex_pace_by_team.get(t, 0), reverse=True):
        n_ol = prod_apex[team].n_on_limit if team in prod_apex else 0
        apex_rows.append(
            f"| {team} | {prod_apex_pace_by_team[team]:+.4f} | "
            f"{expl_apex_q90.get(team, float('nan')):+.4f} | "
            f"{expl_quali_pace.get(team, float('nan')):+.3f} | {n_ol} |"
        )

    # Determine average per-round drag spearman (excluding None)
    valid_drag = [v for v in per_round_drag_spearman.values() if v is not None]
    avg_drag = float(np.mean(valid_drag)) if valid_drag else float("nan")

    section = f"""
## Richer validation (multi-round, fixed calibration)

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

Rounds: {', '.join(rounds)}
Driver-rounds processed: {n_total} ({n_error} errors, {n_fallback_long} longitudinal fallbacks)
Speed-inflation events (p99 > {_P99_SPEED_LIMIT} m/s, fixed calibration): {n_speed_inflation} ({inflation_rate:.1%})
Overall fallback rate (error + longitudinal fallback): {fallback_rate:.1%}

### Per-round drag Spearman (prod avg CdA vs exploration CdA_closed [index 0])

| Round | Spearman | n teams |
|-------|----------|---------|
{chr(10).join(drag_rows)}

Average drag Spearman across {len(valid_drag)} rounds: **{avg_drag:+.3f}**

### Pooled apex pace (all rounds) vs exploration

| Team | Prod apex_pace | Expl apex_speed_q90 | Expl quali_pace | n_on_limit |
|------|---------------|---------------------|-----------------|------------|
{chr(10).join(apex_rows)}

- **apex_pace vs apex_speed_q90 Spearman: {_fmt(rho_apex_q90)}** (n={n_apex_common} teams)
- **apex_pace vs quali_pace Spearman: {_fmt(rho_apex_quali)}** (n={n_quali_common} teams; expected ~−0.89)

Note: The full-season exploration target was −0.89 (apex_speed_q90 vs quali_pace)
using all 22 rounds with multiple drivers per team.  This multi-round pooling
progressively reduces noise; the season-complete result should approach that target.
"""

    # Append (or create) the markdown file
    if OUTPUT_MD.exists():
        existing = OUTPUT_MD.read_text(encoding="utf-8")
        # Remove any previous "Richer validation" section before appending fresh one
        marker = "\n## Richer validation (multi-round, fixed calibration)"
        if marker in existing:
            existing = existing[:existing.index(marker)]
        OUTPUT_MD.write_text(existing + section, encoding="utf-8")
    else:
        OUTPUT_MD.write_text(section, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Production vs Exploration Validation")
    parser.add_argument(
        "--rounds",
        nargs="+",
        default=DEFAULT_ROUNDS,
        help="GP names to process (default: 6-round season-spanning subset)",
    )
    parser.add_argument(
        "--phase2-only",
        action="store_true",
        help="Skip Phase 1, run Phase 2 on existing checkpoint only",
    )
    args = parser.parse_args()
    rounds = args.rounds

    log(f"Rounds: {rounds}")
    log(f"Checkpoint path: {CHECKPOINT_JSON}")

    if not args.phase2_only:
        run_phase1(rounds)
    else:
        log("--phase2-only: skipping Phase 1")

    run_phase2(rounds)


if __name__ == "__main__":
    main()
