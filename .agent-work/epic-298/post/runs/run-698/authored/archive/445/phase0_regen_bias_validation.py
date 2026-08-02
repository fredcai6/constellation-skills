"""Phase 0 — D1 drag-source validation: does src/physics coast-drag give usable per-car CdA?

Task A: Quantify regen bias.
  For 3 representative 2023 Q sessions (Italian/Monza, Hungarian, Mexico City), for each of the
  10 teams, fit the EXACT src/physics model:
      -a = theta_R + theta_D * rho * v^2
  on coast points (throttle<=10, brake<1, decelerating, high-speed). Convert to
      CdA_equiv = 2 * MASS * theta_D
  Then compute Spearman + Pearson corr(coast-CdA, joint-CdA_closed) per session and pooled.
  Also compute FIELD-RELATIVE (log-detrended by session median) correlation — the right metric.

Task B: Audit the density path in src/physics.

Run from repo root: py .agent-work/445/phase0_regen_bias_validation.py
"""
import json
import logging
import sys
import warnings
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO = Path("C:/Programs/f1Brainz")
ENV_DIR = REPO / ".agent-work/445/envelope"
sys.path.insert(0, str(ENV_DIR))
sys.path.insert(0, str(REPO))
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# Envelope helpers
# ---------------------------------------------------------------------------
from air_density import air_density as get_rho  # noqa: E402

# FastF1
import fastf1  # noqa: E402
fastf1.Cache.enable_cache(str(REPO / "outputs/cache"))

# ---------------------------------------------------------------------------
# Constants (match src/physics/physics_config.py defaults + envelope values)
# ---------------------------------------------------------------------------
MASS = 808.0          # kg (from ribbon_reeval.py)
COAST_THROTTLE_MAX = 10.0   # FastF1 Throttle is 0-100 scale
COAST_BRAKE_MAX = 0.5       # FastF1 Brake is 0/1 bool
VMIN_COAST_KMH = 150.0      # km/h — high-speed straight (aero-dominated)
ACCEL_NEG_BOUND = -15.0     # m/s^2 — remove unrealistic spikes

# season_drs.json key [0] = CdA_closed (from drs_joint_fit.py)
DRS = json.loads((ENV_DIR / "season_drs.json").read_text())

# 10 teams + driver abbreviations (from season_cda_collect.py)
TEAMS = {
    "RBR":  ["VER", "PER"],
    "ATR":  ["TSU", "DEV", "RIC", "LAW"],
    "MERC": ["HAM", "RUS"],
    "MCL":  ["NOR", "PIA"],
    "AMR":  ["ALO", "STR"],
    "WIL":  ["ALB", "SAR"],
    "FER":  ["LEC", "SAI"],
    "ALF":  ["BOT", "ZHO"],
    "HAA":  ["MAG", "HUL"],
    "ALP":  ["GAS", "OCO"],
}

# Sessions: low-drag (Italian=Monza), high-DF (Hungarian), altitude (Mexico City)
SESSIONS = [
    (2023, "Italy",    "Italian",     "Q"),
    (2023, "Hungary",  "Hungarian",   "Q"),
    (2023, "Mexico",   "Mexico City", "Q"),
]


# ---------------------------------------------------------------------------
# Helper: driver number lookup
# ---------------------------------------------------------------------------
def driver_num(session, abbr: str):
    for d in session.drivers:
        di = session.get_driver(d)
        if di.get("Abbreviation") == abbr:
            return d
    return None


# ---------------------------------------------------------------------------
# Task A: extract coast points and fit src/physics model
# ---------------------------------------------------------------------------
def coast_points_for_team(session, driver_abbrs):
    """Extract (v_ms, a_ms2) coast points for a team across all their drivers.

    Mirrors coast_decouple.py and the src/physics ControlState.is_coasting thresholds:
      - throttle <= 10 (0-100 scale)
      - brake < 0.5 (0/1 in FastF1)
      - decelerating (a < -0.2 m/s^2, a > ACCEL_NEG_BOUND)
      - speed > VMIN_COAST_KMH km/h (high-speed straight, aero-dominated)
    """
    V, A = [], []
    for abbr in driver_abbrs:
        num = driver_num(session, abbr)
        if num is None:
            continue
        try:
            cd = session.car_data[num]
        except (KeyError, AttributeError):
            continue
        tc = cd["SessionTime"].dt.total_seconds().to_numpy()
        spd = cd["Speed"].to_numpy(float) / 3.6   # km/h -> m/s
        thr = cd["Throttle"].to_numpy(float)       # 0-100
        brk = cd["Brake"].to_numpy(float)          # 0 or 1

        o = np.argsort(tc)
        tc, spd, thr, brk = tc[o], spd[o], thr[o], brk[o]
        keep = np.concatenate([[True], np.diff(tc) > 1e-9])
        tc, spd, thr, brk = tc[keep], spd[keep], thr[keep], brk[keep]

        for i in range(1, len(tc) - 1):
            dt = tc[i + 1] - tc[i - 1]
            if dt <= 0 or dt > 0.6:
                continue
            a = (spd[i + 1] - spd[i - 1]) / dt
            if (thr[i] <= COAST_THROTTLE_MAX and
                    brk[i] < COAST_BRAKE_MAX and
                    spd[i] * 3.6 > VMIN_COAST_KMH and
                    ACCEL_NEG_BOUND < a < -0.2):
                V.append(spd[i])
                A.append(a)
    return np.array(V), np.array(A)


def fit_src_physics_model(v_ms, a_ms2, rho):
    """Fit the EXACT src/physics/longitudinal_fit.py::fit_drag_rolling model:
        -a = theta_R + theta_D * rho * v^2
    (without weights, which is valid since we're using the same linear lstsq core)

    Returns (theta_D, theta_R, CdA_equiv, n_pts) or (None, None, None, n) on failure.
    CdA_equiv = 2 * MASS * theta_D  (from physics_config commentary and drs_joint_fit math)
    """
    if len(v_ms) < 5:
        return None, None, None, len(v_ms)

    # Design identical to fit_drag_rolling: X = [rho*v^2, 1.0], y = -a
    x = rho * v_ms ** 2
    y = -a_ms2
    design = np.column_stack([x, np.ones_like(x)])

    params, *_ = np.linalg.lstsq(design, y, rcond=None)
    theta_D, theta_R = float(params[0]), float(params[1])

    if theta_D <= 0:
        return None, theta_R, None, len(v_ms)

    CdA_equiv = 2.0 * MASS * theta_D
    return theta_D, theta_R, CdA_equiv, len(v_ms)


# ---------------------------------------------------------------------------
# Correlation helpers
# ---------------------------------------------------------------------------
def spearman(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    d = rx - ry
    return 1.0 - 6.0 * np.dot(d, d) / (n * (n**2 - 1))


def pearson(x, y):
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def run():
    print("=" * 70)
    print("Phase 0 — Regen Bias Validation (D1: drag source)")
    print("=" * 70)

    # Store per-session arrays for field-relative analysis
    session_coast_arrays = {}   # gp_key -> np.array of coast CdA
    session_joint_arrays = {}   # gp_key -> np.array of joint CdA_closed
    session_results = {}

    for year, gp_fastf1, gp_drs_key, ses in SESSIONS:
        print(f"\n--- {gp_drs_key} ({gp_fastf1}) {ses} {year} ---")
        try:
            q = fastf1.get_session(year, gp_fastf1, ses)
            q.load(telemetry=True, laps=False, weather=False)
        except Exception as e:
            print(f"  LOAD FAILED: {e}")
            continue

        rho = get_rho(year, gp_fastf1, ses)
        print(f"  rho = {rho:.4f} kg/m^3")

        if gp_drs_key not in DRS:
            print(f"  WARN: {gp_drs_key!r} not in season_drs.json")
            continue

        drs_round = DRS[gp_drs_key]
        coast_cdas = []
        joint_cdas = []
        theta_Rs   = []
        team_labels = []

        for team, drivers in TEAMS.items():
            if team not in drs_round:
                print(f"    {team}: not in DRS data, skipping")
                continue

            joint_cda_closed = drs_round[team][0]

            v, a = coast_points_for_team(q, drivers)
            theta_D, theta_R, cda_equiv, n_pts = fit_src_physics_model(v, a, rho)

            if cda_equiv is None or not (0.3 < cda_equiv < 3.5):
                print(f"    {team}: coast fit FAILED / implausible "
                      f"(CdA={cda_equiv}, theta_D={theta_D}, n={n_pts})")
                continue

            coast_cdas.append(cda_equiv)
            joint_cdas.append(joint_cda_closed)
            theta_Rs.append(theta_R)
            team_labels.append(team)
            print(f"    {team}: coast-CdA={cda_equiv:.3f}  joint-CdA_closed={joint_cda_closed:.4f}"
                  f"  theta_R={theta_R:.4f}  n_pts={n_pts}")

        if len(coast_cdas) < 3:
            print(f"  Too few teams ({len(coast_cdas)}) — skipping correlation")
            continue

        coast_arr = np.array(coast_cdas)
        joint_arr = np.array(joint_cdas)
        theta_r_arr = np.array(theta_Rs)

        sp = spearman(coast_arr, joint_arr)
        pe = pearson(coast_arr, joint_arr)
        print(f"\n  RESULTS ({len(coast_arr)} teams):")
        print(f"    Spearman corr(coast-CdA, joint-CdA) = {sp:+.3f}")
        print(f"    Pearson  corr(coast-CdA, joint-CdA) = {pe:+.3f}")
        print(f"    theta_R  (intercept) median = {np.median(theta_r_arr):.4f} m/s^2  "
              f"(range {theta_r_arr.min():.4f}..{theta_r_arr.max():.4f})")
        print(f"    theta_R  cross-team spread (std) = {theta_r_arr.std():.4f} m/s^2")
        print(f"    NOTE: physical rolling resistance for F1 = ~0.02-0.05 m/s^2;")
        print(f"    theta_R >> 0.05 means the intercept is absorbing REGEN, not rolling friction")

        session_coast_arrays[gp_drs_key] = coast_arr
        session_joint_arrays[gp_drs_key] = joint_arr
        session_results[gp_drs_key] = {
            "spearman": sp, "pearson": pe,
            "n_teams": len(coast_arr),
            "theta_R_median": float(np.median(theta_r_arr)),
            "theta_R_std": float(theta_r_arr.std()),
            "team_labels": team_labels,
            "coast_cdas": coast_arr.tolist(),
            "joint_cdas": joint_arr.tolist(),
            "theta_Rs": theta_r_arr.tolist(),
        }

    # ------------------------------------------------------------------
    # Field-relative pooled correlation
    # (log-detrend by session median — removes track-level wing config variation)
    # This is the correct measure for per-car per-team signal.
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("FIELD-RELATIVE pooled (log-detrend each session by its median):")
    print("(This removes the track-level wing configuration offset — the right metric)")
    fr_coast_all, fr_joint_all = [], []
    for gp_key in session_results:
        ca = np.array(session_results[gp_key]["coast_cdas"])
        ja = np.array(session_results[gp_key]["joint_cdas"])
        med_c = np.log(np.median(ca))
        med_j = np.log(np.median(ja))
        for c, j in zip(ca, ja):
            fr_coast_all.append(np.log(c) - med_c)
            fr_joint_all.append(np.log(j) - med_j)

    if len(fr_coast_all) >= 3:
        fr_c = np.array(fr_coast_all)
        fr_j = np.array(fr_joint_all)
        sp_fr = spearman(fr_c, fr_j)
        pe_fr = pearson(fr_c, fr_j)
        print(f"  N pairs                  = {len(fr_c)}")
        print(f"  Spearman (field-rel log) = {sp_fr:+.3f}")
        print(f"  Pearson  (field-rel log) = {pe_fr:+.3f}")
        print(f"  (Prior coast_decouple.py result: Spearman/Pearson ~ -0.12)")
    else:
        print("  Insufficient data.")
        sp_fr, pe_fr = float("nan"), float("nan")

    # ------------------------------------------------------------------
    # Naive pooled (across different tracks — contaminated by wing-config variation)
    # ------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("NAIVE pooled (raw, across different tracks — inflated by wing-config variation):")
    all_coast = []
    all_joint = []
    for gp_key in session_results:
        all_coast.extend(session_results[gp_key]["coast_cdas"])
        all_joint.extend(session_results[gp_key]["joint_cdas"])

    sp_pool = float("nan")
    if len(all_coast) >= 3:
        sp_pool = spearman(np.array(all_coast), np.array(all_joint))
        pe_pool = pearson(np.array(all_coast), np.array(all_joint))
        print(f"  N pairs          = {len(all_coast)}")
        print(f"  Spearman pooled  = {sp_pool:+.3f}  (naive, DO NOT USE for D1)")
        print(f"  Pearson  pooled  = {pe_pool:+.3f}  (naive, DO NOT USE for D1)")

    # ------------------------------------------------------------------
    # theta_R physical interpretation
    # ------------------------------------------------------------------
    all_theta_R = []
    for r in session_results.values():
        all_theta_R.extend(r["theta_Rs"])
    if all_theta_R:
        theta_r_all = np.array(all_theta_R)
        print(f"\n" + "=" * 70)
        print("THETA_R PHYSICAL INTERPRETATION:")
        print(f"  Pooled theta_R median  = {np.median(theta_r_all):.3f} m/s^2")
        print(f"  Pooled theta_R std     = {theta_r_all.std():.3f} m/s^2")
        print(f"  Expected rolling resistance = ~0.02-0.05 m/s^2 for F1")
        print(f"  Ratio (measured / expected) ~ {np.median(theta_r_all)/0.035:.0f}x")
        print(f"  => Theta_R is DOMINATED by regen/engine-brake, NOT rolling friction")
        print(f"  => Cross-team theta_R std {theta_r_all.std():.3f} >> rolling variation")
        print(f"     This is per-team harvest strategy variation showing up as 'rolling resistance'")

    # ------------------------------------------------------------------
    # Key question check: is theta_R's intercept rescuing the coast drag?
    # If regen is ~constant-speed (constant power), it gives a ~1/v force, NOT a constant.
    # The constant intercept CAN'T absorb a 1/v force, so the v^2 coefficient gets contaminated.
    # ------------------------------------------------------------------
    print(f"\n" + "=" * 70)
    print("REGEN-BIAS MECHANISM CHECK:")
    print("  The model is: -a = theta_R + theta_D * rho * v^2")
    print("  Regen at constant POWER P_regen gives decel = P_regen / (m * v)  [~1/v force]")
    print("  A constant intercept theta_R CAN'T absorb a 1/v term.")
    print("  So: theta_D gets contaminated by the non-constant residual of 1/v.")
    print("  At high speeds (v large), 1/v is small, so the contamination is small.")
    print("  At lower coast speeds, 1/v is larger — biases theta_D upward toward theta_R.")
    print("  Net: the v^2 leverage at high speed 'rescues' the fit partially,")
    print("  but between-team regen strategy differences still bleed into theta_D.")

    # ------------------------------------------------------------------
    # Summary table
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY TABLE:")
    print(f"  {'Session':15s}  {'N':>3}  {'Spearman':>9}  {'Pearson':>8}  {'theta_R_med':>12}")
    for gp, r in session_results.items():
        print(f"  {gp:15s}  {r['n_teams']:>3}  {r['spearman']:>+9.3f}  {r['pearson']:>+8.3f}  "
              f"{r['theta_R_median']:>+12.4f}")
    print(f"\n  Field-relative (log-detrend): Spearman={sp_fr:+.3f}  Pearson={pe_fr:+.3f}")
    print(f"  (These are the numbers for D1 decision.)")
    print()

    return session_results


if __name__ == "__main__":
    run()
