"""Ribbon + ideal-lap re-evaluation on CLEAN (calibrated) kinematics (#445).

Re-evaluates two prior findings from the CONTAMINATED (chi2_pos~33) smoother:
  1. Track ribbon quality: is pooled kappa(s) materially cleaner on clean geometry?
  2. Ideal lap: does clean kinematics change the constructor spread / ordering?

The contaminated cross_circuit.py found:
  - spread ~749ms / ~715ms / ~749ms (track-INVARIANT ~1% of lap = fit-noise signature)
  - ordering SCRAMBLED (RBR slowest Hungary, WIL fastest Suzuka - both nonsensical)

This script:
  - builds CLEAN ribbons using per-session calibrated HPs from calibrated_hp.json
  - harvests constructor apex nodes from calibrated_aniso_nodes.npz (pure-lateral)
  - re-fits grip (shared A, per-car B) and power/drag (unchanged: CAN bus data)
  - re-runs the quasi-static ideal-lap sim on the clean ribbon
  - prints clean vs contaminated comparison + discrimination check

NAMESPACED outputs: ribbon_clean_{monza,hungary,suzuka}.npz
Run from repo root: py .agent-work/445/envelope/ribbon_reeval.py
"""
from __future__ import annotations

import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import (  # noqa: E402
    driver_num, driver_streams, load_session, stint_span,
)
from src.preprocessing.trajectory.smoother import StintSmoother  # noqa: E402
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp  # noqa: E402

try:
    from scipy.optimize import curve_fit
except ImportError:
    curve_fit = None

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
HP_JSON = OUT / "calibrated_hp.json"
CAL_ANISO = OUT / "calibrated_aniso_nodes.npz"

G_CONST, RHO, MASS = 9.81, 1.2, 808.0
NGRID = 1500

# Tracks: (gp_name_for_fastf1, official_length_m, HP_json_key)
TRACKS = {
    "Monza":   dict(gp="Italy",   length=5793, hp_key="Italian"),
    "Hungary": dict(gp="Hungary", length=4381, hp_key="Hungarian"),
    "Suzuka":  dict(gp="Japan",   length=5807, hp_key="Japanese"),
}

TEAMS = {
    "RBR":  ["VER", "PER"],
    "MERC": ["HAM", "RUS"],
    "FER":  ["LEC", "SAI"],
    "WIL":  ["ALB", "SAR"],
}

# Contaminated (old) cross_circuit.py results for comparison
OLD_IDEALS = {
    "Monza":   {"RBR": 71.06, "MERC": 71.41, "FER": 70.79, "WIL": 70.66},
    "Hungary": {"RBR": 69.71, "MERC": 69.04, "FER": 68.99, "WIL": 69.43},
    "Suzuka":  {"RBR": 82.84, "MERC": 83.33, "FER": 83.20, "WIL": 82.58},
}
OLD_POLES = {"Monza": 80.29, "Hungary": 76.61, "Suzuka": 88.88}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


# ============================================================
# Calibrated HP loading
# ============================================================

def load_hp(hp_key):
    """Load per-session calibrated HPs from the calibrated_hp.json."""
    with open(HP_JSON) as f:
        hps = json.load(f)
    if hp_key not in hps:
        raise KeyError(f"HP key '{hp_key}' not in calibrated_hp.json; "
                       f"available: {list(hps.keys())}")
    h = hps[hp_key]
    return h["ell"], h["sf"], h["sig_pos"], h["delta"], h["chi2_pos"], h["chi2_spd"]


# ============================================================
# Clean ribbon construction
# ============================================================

def lap_path(ss, ls, le):
    """Extract a single lap path (X,Y) on a NGRID grid from the smoother."""
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    if len(t) < 80:
        return None
    X, Y = ss.pos_at(t)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    if s[-1] < 2000 or s[-1] > 8000:
        return None
    u = s / s[-1]
    ug = np.linspace(0, 1, NGRID)
    return np.interp(ug, u, X), np.interp(ug, u, Y)


def build_clean_ribbon(gp, hp_key, cars=("VER", "HAM")):
    """Pool lap paths using CALIBRATED per-session smoother HPs.

    Uses the per-session calibrated (ell, sf, sig_pos, delta) from calibrated_hp.json
    instead of the hardcoded contaminated (2, 100, 0.3, 0.06).
    Pools Q + R laps for each car.
    """
    ell, sf, sp, delta, chi2_p, chi2_s = load_hp(hp_key)
    log(f"  calibrated HP: ell={ell} sf={sf:.0f} sig_pos={sp:.2f} delta={delta:.2f} "
        f"(chi2_pos={chi2_p:.2f} chi2_spd={chi2_s:.2f})")

    paths = []
    for ses_type in ("Q", "R"):
        session = load_session(2023, gp, ses_type)
        for car in cars:
            if ses_type == "Q":
                runs = H.driver_runs(session, car)
                laps = session.laps.pick_drivers(car)
                laps = laps[laps["LapTime"].notna()]
                for _, r in laps.iterrows():
                    ls = r["LapStartTime"].total_seconds()
                    le = r["Time"].total_seconds()
                    run = next((rr for rr in runs
                                if rr["t0"] <= ls and rr["t1"] >= le), None)
                    if run is None:
                        continue
                    ss = StintSmoother(ell, sf, sp, delta, iters=2)
                    try:
                        ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
                    except Exception as e:
                        log(f"    Q lap smoother fail {car}: {e}")
                        continue
                    p = lap_path(ss, ls, le)
                    if p:
                        paths.append(p)
            else:
                import pandas as pd
                num = driver_num(session, car)
                pos_d, spd_d = driver_streams(session, num)
                laps = session.laps.pick_drivers(car)
                laps = laps[laps["LapTime"].notna()].copy()
                for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
                    try:
                        t0, t1, _ = stint_span(session, car, st)
                    except Exception:
                        continue
                    mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
                    mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
                    if mp.sum() < 100:
                        continue
                    ss = StintSmoother(ell, sf, sp, delta, iters=2)
                    try:
                        ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                               spd_d["t"][mc], spd_d["V"][mc])
                    except Exception as e:
                        log(f"    R stint smoother fail {car} st{st}: {e}")
                        continue
                    for _, r in laps[laps["Stint"] == st].iterrows():
                        import pandas as _pd
                        if (_pd.notna(r.get("PitInTime"))
                                or _pd.notna(r.get("PitOutTime"))
                                or int(r["LapNumber"]) <= 1):
                            continue
                        p = lap_path(ss, r["LapStartTime"].total_seconds(),
                                     r["Time"].total_seconds())
                        if p:
                            paths.append(p)

        log(f"  {ses_type} collected, {len(paths)} paths so far")

    if not paths:
        raise RuntimeError(f"No lap paths collected for {gp}")

    paths_arr = np.array(paths)  # (nlaps, 2, NGRID)
    mean = paths_arr.mean(axis=0)
    X, Y = mean[0], mean[1]
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    th = np.unwrap(np.arctan2(np.gradient(Y, s), np.gradient(X, s)))
    kappa_raw = np.gradient(th, s)
    kappa = np.convolve(kappa_raw, np.ones(9) / 9, mode="same")
    return s, X, Y, kappa, len(paths), kappa_raw


def ribbon_quality_metrics(kappa_raw, kappa_smooth, nlaps, label):
    """Report curvature noise metrics for the ribbon."""
    residuals = kappa_raw - kappa_smooth
    rms_raw = float(np.std(kappa_raw))
    rms_res = float(np.std(residuals))
    kmax = float(np.abs(kappa_smooth).max())
    Rmin = 1.0 / kmax if kmax > 1e-6 else np.inf
    log(f"  {label}: N_laps={nlaps}, rms_kappa_raw={rms_raw:.5f} 1/m, "
        f"rms_residual={rms_res:.5f} 1/m, Rmin={Rmin:.0f}m")
    return dict(nlaps=nlaps, rms_kappa_raw=rms_raw, rms_residual=rms_res, Rmin=Rmin)


# ============================================================
# Constructor apex nodes from calibrated_aniso_nodes.npz
# ============================================================

def load_cal_nodes():
    """Load calibrated_aniso_nodes.npz and return by (round_name, car).

    Keys in the npz are: v__<RoundName>__<CAR>, alat__<RoundName>__<CAR>, etc.
    where RoundName matches the HP_json_key (e.g. 'Italian', 'Hungarian', 'Japanese').
    """
    if not CAL_ANISO.exists():
        raise FileNotFoundError(
            f"calibrated_aniso_nodes.npz not found: {CAL_ANISO}\n"
            "Run calibrated_extract.py first."
        )
    d = np.load(CAL_ANISO, allow_pickle=True)
    store = {}
    for k in d.files:
        if k.startswith("v__"):
            # format: v__<RoundName>__<CAR>  (RoundName may contain spaces -> only one __ split)
            tail = k[3:]  # e.g. "Italian__VER"
            idx = tail.rfind("__")
            if idx < 0:
                continue
            rnd_name = tail[:idx]   # e.g. "Italian"
            car = tail[idx + 2:]    # e.g. "VER"
            alat_key = f"alat__{rnd_name}__{car}"
            if alat_key not in d.files:
                continue
            store[(rnd_name, car)] = dict(
                v=d[k].astype(float),          # m/s
                alat=d[alat_key].astype(float),  # g's (from emit_nodes_aniso: v²/R/G)
            )
    return store


# Map GP fastf1-name -> HP_json round name (same as hp_key)
GP_ROUNDS = {
    "Italy":   "Italian",
    "Hungary": "Hungarian",
    "Japan":   "Japanese",
}


def get_apex_nodes(cal_nodes, gp, cars):
    """Pull pure-lateral apex nodes for a set of cars from the calibrated cloud.

    alat in calibrated_aniso_nodes.npz is already in g's (not m/s²),
    as emitted by aniso_collect.py: alat = v²/R/G with G=9.81.
    Uses alat > 0.6g gate (emit_nodes_aniso's own filter; stored nodes all pass it).
    Returns (v_kmh, g_g): v in km/h, g in g-units.
    """
    rnd_name = GP_ROUNDS.get(gp)
    if rnd_name is None:
        return None, None
    v_all, g_all = [], []
    for car in cars:
        key = (rnd_name, car)
        if key not in cal_nodes:
            continue
        v_ = cal_nodes[key]["v"]     # m/s
        alat_ = cal_nodes[key]["alat"]  # g's (already filtered >= 0.6g by emitter)
        v_all.append(v_)
        g_all.append(alat_)
    if not v_all:
        return None, None
    return np.concatenate(v_all) * 3.6, np.concatenate(g_all)  # km/h, g


def fit_grip_clean(v_kmh, g_g, gsat=5.2, with_cov=False):
    """Fit A + B*v^2 on the calibrated node cloud.

    Only the reliable slow/medium speed regime (40-150 km/h); shared Gsat.
    with_cov=True also returns (sigA, sigB) from the curve_fit covariance (honest σ).
    """
    if curve_fit is None:
        raise ImportError("scipy not available for curve_fit")
    edges = np.arange(40, 156, 12)
    vb, cb, sb = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (v_kmh >= lo) & (v_kmh < hi)
        if mask.sum() >= 6:
            vb.append(v_kmh[mask].mean())
            cb.append(np.quantile(g_g[mask], 0.90))
            sb.append(0.06)
    if len(vb) < 3:
        return (None, None, None, None, None) if with_cov else (None, None, None)

    def m2(vv, A, B):
        return np.minimum(A + B * (vv / 3.6) ** 2, gsat)

    popt, pcov = curve_fit(
        m2, np.array(vb), cb, p0=[1.8, 0.0018],
        sigma=sb, bounds=([1.0, 0.0005], [3.0, 0.005]), maxfev=20000
    )
    if with_cov:
        sig = np.sqrt(np.clip(np.diag(pcov), 0, None))
        return float(popt[0]), float(popt[1]), gsat, float(sig[0]), float(sig[1]), np.asarray(pcov, float)
    return float(popt[0]), float(popt[1]), gsat


# ============================================================
# Quasi-static ideal-lap sim (same as cross_circuit.py)
# ============================================================

def ideal_time(s, kappa, A, B, GS, P, cc, co, length):
    """Forward-backward quasi-static lap sim on the ribbon."""
    kappa = np.abs(kappa)
    n = len(s)
    ds = np.diff(s)

    def Gv(v):
        return min(A + B * v * v, GS)

    def drag(v, k):
        return (0.5 * RHO
                * (co if (abs(k) < 8e-4 and v > 200 / 3.6) else cc)
                * v * v / MASS)

    vg = np.sqrt(GS * G_CONST / np.maximum(kappa, 1e-6))
    for _ in range(10):
        vg = np.minimum(
            np.sqrt(np.array([Gv(x) for x in vg]) * G_CONST
                    / np.maximum(kappa, 1e-6)),
            100.0,
        )
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G_CONST
            tr = np.sqrt(max(Gv(v[i]) ** 2 - al ** 2, 0)) * G_CONST
            a = min(tr, P / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1],
                           np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)),
                           vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G_CONST
            tr = np.sqrt(max(Gv(v[i + 1]) ** 2 - al ** 2, 0)) * G_CONST
            a_b = tr + drag(v[i + 1], kappa[i + 1])
            v[i] = min(v[i],
                       np.sqrt(max(v[i + 1] ** 2 + 2 * a_b * ds[i], 1.0)),
                       vg[i])
    t_sim = float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))
    return t_sim * length / s[-1]


def full_q_pd(session, cars, rho=RHO):
    """CAN-bus full-throttle power/drag fit (unchanged from cross_circuit.py).

    Uses car_data (Speed, Throttle, Brake, DRS) on flying laps only. rho defaults to the fixed
    sea-level constant for back-compat; pass the real per-session density to back out true CdA.
    Note: in ideal_time the density cancels (drag uses the same rho the CdA was fit at), so it only
    affects the REPORTED CdA_c/CdA_o, not the lap time.
    """
    rows = []
    VMIN_PD = 160 / 3.6
    for car in cars:
        try:
            num = driver_num(session, car)
            cd = session.car_data[num]
            tc = cd["SessionTime"].dt.total_seconds().to_numpy()
            spd = cd["Speed"].to_numpy(float) / 3.6
            thr = cd["Throttle"].to_numpy(float)
            brk = cd["Brake"].to_numpy(float)
            drs = cd["DRS"].to_numpy(float)
            for ls, le in flying_windows(session, car):
                m = (tc >= ls) & (tc <= le)
                t, v, th, bk, dr = tc[m], spd[m], thr[m], brk[m], drs[m]
                o = np.argsort(t)
                t, v, th, bk, dr = t[o], v[o], th[o], bk[o], dr[o]
                keep = np.concatenate([[True], np.diff(t) > 1e-9])
                t, v, th, bk, dr = t[keep], v[keep], th[keep], bk[keep], dr[keep]
                for i in range(1, len(t) - 1):
                    dt = t[i + 1] - t[i - 1]
                    if dt > 0 and th[i] > 95 and bk[i] < 1 and v[i] > VMIN_PD:
                        rows.append((v[i], (v[i + 1] - v[i - 1]) / dt, dr[i]))
        except Exception as e:
            log(f"    power/drag {car}: {e}")
    if len(rows) < 30:
        return None
    d = np.array(rows)
    v, a, drs_ = d[:, 0], d[:, 1], d[:, 2]
    op = drs_ >= 10
    X = np.column_stack([
        1 / (MASS * v),
        -0.5 * rho * v ** 2 / MASS * (~op),
        -0.5 * rho * v ** 2 / MASS * op,
    ])
    coef, *_ = np.linalg.lstsq(X, a, rcond=None)
    return float(coef[0]), float(coef[1]), float(coef[2])  # P, CdA_c, CdA_o


def best_quali_lap(q, cars):
    best = np.inf
    for car in cars:
        laps = q.laps.pick_drivers(car)
        laps = laps[laps["LapTime"].notna()]
        if len(laps):
            best = min(best, float(laps["LapTime"].dt.total_seconds().min()))
    return best


# ============================================================
# Main
# ============================================================

def run_track(name, cfg, cal_nodes):
    gp = cfg["gp"]
    length = cfg["length"]
    hp_key = cfg["hp_key"]

    log(f"\n{'=' * 60}")
    log(f"  TRACK: {name} ({gp}, {length} m)")
    log(f"{'=' * 60}")

    # ---- 1. Clean ribbon ----
    cache_clean = OUT / f"ribbon_clean_{name.lower()}.npz"
    if cache_clean.exists():
        d = np.load(cache_clean)
        s, kappa = d["s"], d["kappa"]
        kappa_raw = d.get("kappa_raw", kappa)
        nlaps = int(d.get("nlaps", 0))
        log(f"  ribbon: loaded cached {cache_clean.name} ({nlaps} laps, {s[-1]:.0f} m)")
        qmet = ribbon_quality_metrics(kappa_raw, kappa, nlaps, "CLEAN")
    else:
        log(f"  building CLEAN ribbon (calibrated HPs, VER+HAM Q+R) ...")
        s, X, Y, kappa, nlaps, kappa_raw = build_clean_ribbon(gp, hp_key)
        np.savez(cache_clean, s=s, X=X, Y=Y, kappa=kappa,
                 kappa_raw=kappa_raw, nlaps=nlaps)
        log(f"  ribbon: {nlaps} laps, mean line {s[-1]:.0f} m, "
            f"tightest R={1/np.abs(kappa).max():.0f} m")
        qmet = ribbon_quality_metrics(kappa_raw, kappa, nlaps, "CLEAN")

    # Also compare old ribbon if cached (contaminated)
    cache_old = OUT / f"ribbon_{name.lower()}.npz"
    if cache_old.exists():
        d_old = np.load(cache_old)
        s_old, k_old = d_old["s"], d_old["kappa"]
        kappa_raw_old = np.gradient(
            np.unwrap(np.arctan2(np.gradient(d_old.get("Y", np.zeros_like(s_old)), s_old),
                                 np.gradient(d_old.get("X", np.zeros_like(s_old)), s_old))),
            s_old
        )
        nlaps_old = int(d_old.get("nlaps", 0))
        log(f"  old ribbon: {nlaps_old} laps, mean line {s_old[-1]:.0f} m")
        ribbon_quality_metrics(k_old, k_old, nlaps_old, "OLD (contaminated)")
    else:
        log(f"  (no old ribbon cached for {name})")

    # ---- 2. Constructor grip from calibrated nodes ----
    q = load_session(2023, gp, "Q")
    pole = best_quali_lap(q, sum(TEAMS.values(), []))

    res = {}
    for team, cars in TEAMS.items():
        # Calibrated apex nodes (pure-lateral, from the full-season extraction)
        v_kmh, g_g = get_apex_nodes(cal_nodes, gp, cars)
        if v_kmh is None or len(v_kmh) < 30:
            n_nodes = len(v_kmh) if v_kmh is not None else 0
            log(f"  {team}: thin calibrated nodes ({n_nodes}), trying raw extraction ...")
            # Fall back: collect nodes live from the calibrated smoother for this session
            v_kmh, g_g = collect_nodes_live(q, gp, cars, hp_key)
            if v_kmh is not None and len(v_kmh) >= 30:
                log(f"  {team}: live fallback gave {len(v_kmh)} nodes")

        if v_kmh is None or len(v_kmh) < 25:
            log(f"  {team}: still thin ({len(v_kmh) if v_kmh is not None else 0}), skip")
            continue

        A, B, GS = fit_grip_clean(v_kmh, g_g)
        if A is None:
            log(f"  {team}: grip fit failed, skip")
            continue

        # Power/drag: CAN bus, unchanged (smoother doesn't affect car_data throttle).
        # Real per-track density so the reported CdA is the true drag area (RHO cancels in the sim).
        from air_density import air_density
        pd_result = full_q_pd(q, cars, air_density(2023, gp, "Q"))
        if pd_result is None:
            log(f"  {team}: power/drag fit failed, skip")
            continue
        P, cc, co = pd_result

        t_id = ideal_time(s, kappa, A, B, GS, P, cc, co, length)
        res[team] = dict(A=A, B=B, GS=GS, P=P, cc=cc, co=co, t=t_id,
                         n_apex=len(v_kmh))
        log(f"  {team}: A={A:.2f} B={B:.5f} GS={GS:.2f} CdA_c={cc:.2f} "
            f"P={P/1e3:.0f}kW -> ideal {t_id:.2f}s ({len(v_kmh)} apex nodes)")

    return dict(
        length=length, ideals=res, pole=pole,
        ribbon_quality=qmet,
    )


def collect_nodes_live(q, gp, cars, hp_key):
    """Live extraction of apex nodes using calibrated smoother for a session.

    Fallback when calibrated_aniso_nodes.npz doesn't cover this round/car.
    """
    ell, sf, sp, delta, _, _ = load_hp(hp_key)
    v_all, g_all = [], []
    for car in cars:
        try:
            runs = H.driver_runs(q, car)
            for ls, le in flying_windows(q, car):
                run = next((r for r in runs
                            if r["t0"] <= ls and r["t1"] >= le), None)
                if run is None:
                    continue
                ss = StintSmoother(ell, sf, sp, delta, iters=2)
                ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
                # apex extraction: min-speed local minima within the lap
                mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
                t = ss.ts[mask]
                o = np.argsort(t); t = t[o]
                if len(t) < 10:
                    continue
                X_, Y_ = ss.pos_at(t)
                v_ = np.interp(t, run["tc"], run["V"])
                s_ = np.concatenate([[0.0],
                                     np.cumsum(np.hypot(np.diff(X_), np.diff(Y_)))])
                # curvature via local heading slope
                th_ = np.unwrap(np.arctan2(np.gradient(Y_, s_),
                                            np.gradient(X_, s_)))
                kap_ = np.gradient(th_, s_)
                alat_ms2 = v_ ** 2 * np.abs(kap_)   # m/s²
                alat_g = alat_ms2 / G_CONST           # g's
                # filter: alat > 0.6g, v < 185 km/h
                m2 = (alat_g > 0.6) & (v_ * 3.6 < 185)
                v_all.append(v_[m2] * 3.6)            # km/h
                g_all.append(alat_g[m2])              # g's
        except Exception as e:
            log(f"    live node {car}: {e}")
    if not v_all:
        return None, None
    return np.concatenate(v_all), np.concatenate(g_all)


def main():
    log("=== ribbon_reeval.py: CLEAN kinematics re-evaluation ===")
    log(f"calibrated_hp.json: {HP_JSON}")
    log(f"calibrated_aniso_nodes: {CAL_ANISO}")
    log(f"Output dir: {OUT}")

    # Load calibrated node clouds
    log("\nLoading calibrated_aniso_nodes.npz ...")
    try:
        cal_nodes = load_cal_nodes()
        log(f"  {len(cal_nodes)} (round,car) entries loaded")
    except FileNotFoundError as e:
        log(f"  WARNING: {e}")
        log("  Will extract apex nodes live from calibrated smoother.")
        cal_nodes = {}

    # GP_ROUNDS maps gp -> hp_key (round name); log for clarity
    log("\nGP -> round-name mapping:")
    for trk, cfg in TRACKS.items():
        log(f"  {trk} ({cfg['gp']}) -> '{GP_ROUNDS.get(cfg['gp'])}'")


    # Run each track
    all_results = {}
    ribbon_metrics = {}
    for name, cfg in TRACKS.items():
        try:
            r = run_track(name, cfg, cal_nodes)
            all_results[name] = r
            ribbon_metrics[name] = r.get("ribbon_quality", {})
        except Exception as e:
            log(f"  {name} FAILED: {e}")
            import traceback; traceback.print_exc()

    # ============================================================
    # Print comparison table: CLEAN vs OLD
    # ============================================================
    print("\n" + "=" * 72)
    print("RIBBON QUALITY: CLEAN vs CONTAMINATED")
    print("(fewer rms_residual = cleaner curvature profile)")
    print("=" * 72)
    for trk, met in ribbon_metrics.items():
        print(f"  {trk}: nlaps={met.get('nlaps','?')}, "
              f"rms_kappa_residual={met.get('rms_residual','?'):.5f} 1/m, "
              f"Rmin={met.get('Rmin','?'):.0f}m")

    print("\n" + "=" * 72)
    print("IDEAL LAP: CLEAN kinematics")
    print("=" * 72)
    for name, r in all_results.items():
        ids = r["ideals"]
        if not ids:
            print(f"\n  {name}: no constructor ideals computed")
            continue
        mean_t = np.mean([p["t"] for p in ids.values()])
        spread = (max(p["t"] for p in ids.values())
                  - min(p["t"] for p in ids.values()))
        old_ids = OLD_IDEALS.get(name, {})
        old_mean = (np.mean(list(old_ids.values())) if old_ids else None)
        old_spread = ((max(old_ids.values()) - min(old_ids.values()))
                      if old_ids else None)
        print(f"\n--- {name} ({r['length']}m, pole {r['pole']:.2f}s) ---")
        print(f"  field-mean ideal (CLEAN): {mean_t:.2f}s, spread {spread*1000:.0f}ms")
        if old_spread is not None:
            print(f"  field-mean ideal (OLD):   {old_mean:.2f}s, spread {old_spread*1000:.0f}ms")
        print(f"  {'team':>5} {'ideal_clean(s)':>14} {'d_mean_clean(ms)':>17} "
              f"{'ideal_OLD(s)':>13} {'delta_vs_old(ms)':>17}")
        for team, p in sorted(ids.items(), key=lambda kv: kv[1]["t"]):
            dms_clean = (p["t"] - mean_t) * 1000
            old_t = old_ids.get(team)
            if old_t is not None:
                dms_vs_old = (p["t"] - old_t) * 1000
                old_t_str = f"{old_t:13.2f}"
                dvso_str = f"{dms_vs_old:+17.0f}"
            else:
                old_t_str = f"{'--':>13}"
                dvso_str = f"{'--':>17}"
            print(f"  {team:>5} {p['t']:14.2f} {dms_clean:+17.0f} "
                  f"{old_t_str} {dvso_str}")

    # ============================================================
    # Discrimination check: delta-from-mean across tracks
    # ============================================================
    print("\n" + "=" * 72)
    print("DISCRIMINATION CHECK (CLEAN): constructor delta-from-field-mean (ms)")
    print("Low-drag (WIL/RBR) should be -ve at Monza, +ve at Hungary.")
    print("If track-INVARIANT ~same spread everywhere = fit noise.")
    print("=" * 72)
    teams = sorted({t for r in all_results.values() for t in r["ideals"]})
    cols = [n for n in all_results if all_results[n]["ideals"]]
    header = f"{'team':>5} | " + " ".join(f"{c:>10}" for c in cols)
    print(header)
    for team in teams:
        row = []
        for c in cols:
            ids = all_results[c]["ideals"]
            if team in ids:
                mean_t = np.mean([p["t"] for p in ids.values()])
                row.append(f"{(ids[team]['t'] - mean_t)*1000:+10.0f}")
            else:
                row.append(f"{'--':>10}")
        print(f"{team:>5} | " + " ".join(row))
    print("\n(ms vs field mean; negative = faster than field at that track.)")

    # OLD comparison
    print("\n" + "=" * 72)
    print("DISCRIMINATION CHECK (OLD/contaminated, for comparison)")
    print("=" * 72)
    old_teams = sorted({t for od in OLD_IDEALS.values() for t in od})
    old_cols = list(OLD_IDEALS.keys())
    print(f"{'team':>5} | " + " ".join(f"{c:>10}" for c in old_cols))
    for team in old_teams:
        row = []
        for c in old_cols:
            od = OLD_IDEALS[c]
            if team in od:
                om = np.mean(list(od.values()))
                row.append(f"{(od[team]-om)*1000:+10.0f}")
            else:
                row.append(f"{'--':>10}")
        print(f"{team:>5} | " + " ".join(row))

    print("\n" + "=" * 72)
    print("SPREAD COMPARISON (clean vs contaminated)")
    print("=" * 72)
    print(f"{'Track':>10} | {'Spread_CLEAN(ms)':>18} | {'Spread_OLD(ms)':>15}")
    for name, r in all_results.items():
        ids = r["ideals"]
        if ids:
            sp_clean = (max(p["t"] for p in ids.values())
                        - min(p["t"] for p in ids.values())) * 1000
        else:
            sp_clean = float("nan")
        od = OLD_IDEALS.get(name, {})
        sp_old = ((max(od.values()) - min(od.values())) * 1000 if od else float("nan"))
        print(f"{name:>10} | {sp_clean:>18.0f} | {sp_old:>15.0f}")

    log("\nDone.")


if __name__ == "__main__":
    main()
