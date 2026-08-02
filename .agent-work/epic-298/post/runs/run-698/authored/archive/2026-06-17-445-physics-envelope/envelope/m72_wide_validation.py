"""Wide Matern-7/2 validation across all 22 2023 Q sessions, multiple drivers.

Task (epic #445 subagent):
  - For each of the 22 sessions in calibrated_hp.json:
      1. Use the pre-calibrated delta for that session (from calibrated_hp.json).
      2. Calibrate BOTH order-3 (5/2) and order-4 (7/2) to chi2~1 on VER's longest
         run (same protocol as accel_order_calibrated.py).
      3. Measure held-out SPEED on ROBUST metrics (median|e|, glitch>5 m/s) for
         multiple drivers' flying laps.
  - Pooled results across all sessions + per-session table.
  - Report calibrated ell distributions per order (does 5/2 collapse to short ell?).
  - Measure per-fit wall-time and per-step cost for order 3 vs 4.
  - Cache per-session results to m72_validation_cache.json.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from matern_smoother import MaternSmoother  # noqa: E402
from src.preprocessing.trajectory.calibration import interleaved  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
HPJSON = OUT / "calibrated_hp.json"
CACHE_JSON = OUT / "m72_validation_cache.json"

# 22 2023 F1 sessions: (round, GP name matching calibrated_hp.json key)
# Round numbers from the 2023 F1 calendar
SESSIONS_2023 = [
    (1, "Bahrain"),
    (2, "Saudi Arabian"),
    (3, "Australian"),
    (4, "Azerbaijan"),
    (5, "Miami"),
    (6, "Monaco"),
    (7, "Spanish"),
    (8, "Canadian"),
    (9, "Austrian"),
    (10, "British"),
    (11, "Hungarian"),
    (12, "Belgian"),
    (13, "Dutch"),
    (14, "Italian"),
    (15, "Singapore"),
    (16, "Japanese"),
    (17, "Qatar"),
    (18, "United States"),
    (19, "Mexico City"),
    (20, "Sao Paulo"),
    (21, "Las Vegas"),
    (22, "Abu Dhabi"),
]

# Drivers to test held-out speed on (we'll take whoever has flying laps)
DRIVERS = ["VER", "HAM", "LEC", "RUS", "NOR", "PIA", "SAI", "ALO", "PER", "STR"]
MAX_DRIVERS_PER_SESSION = 6
MAX_LAPS_PER_DRIVER = 2

CALIBRATION_DRIVER = "VER"  # calibrate HPs on this driver's longest run
CALIBRATION_FALLBACKS = ["HAM", "LEC", "NOR", "SAI", "ALO"]  # if VER unavailable


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Stream helpers
# ---------------------------------------------------------------------------
def _stream(run):
    return (
        np.asarray(run["tp"], float),
        np.asarray(run["X"], float),
        np.asarray(run["Y"], float),
        np.asarray(run["tc"], float),
        np.asarray(run["V"], float),
    )


def _slice_mid(s, dur=300.0):
    """Slice to centre dur seconds (for calibration on long stints)."""
    tp, X, Y, tc, V = s
    t0, t1 = tp.min(), tp.max()
    if t1 - t0 > dur:
        c = 0.5 * (t0 + t1)
        a, b = c - dur / 2, c + dur / 2
        mp = (tp >= a) & (tp <= b)
        mc = (tc >= a - 1) & (tc <= b + 1)
        return tp[mp], X[mp], Y[mp], tc[mc], V[mc]
    return s


# ---------------------------------------------------------------------------
# Per-order chi2-target calibration (identical protocol as accel_order_calibrated)
# ---------------------------------------------------------------------------
def eval_hp(order, ell, sf, sp, delta, S, trp, trv, hop, hov, iters=3):
    tp, X, Y, tc, V = S
    try:
        sm = MaternSmoother(ell, sf, sp, delta, order=order, iters=iters)
        qt = np.union1d(tp[hop], tc[hov] + delta)
        sm.fit(tp[trp], X[trp], Y[trp], tc[trv], V[trv], query_times=qt)
        pvX, pvY = sm.pos_predvar(tp[hop])
        Xh, Yh = sm.pos_at(tp[hop])
        c_pos = float(
            np.mean(((X[hop] - Xh) ** 2 / pvX + (Y[hop] - Yh) ** 2 / pvY) / 2)
        )
        pvV, sh = sm.speed_predvar(tc[hov] + delta)
        c_spd = float(np.mean((V[hov] - sh) ** 2 / pvV))
    except Exception:
        return None
    if not (np.isfinite(c_pos) and np.isfinite(c_spd) and c_pos > 0 and c_spd > 0):
        return None
    return dict(
        obj=np.log(c_pos) ** 2 + np.log(c_spd) ** 2,
        ell=ell,
        sf=sf,
        sp=sp,
        c_pos=c_pos,
        c_spd=c_spd,
    )


def calibrate_order(order, S, delta):
    """Grid + local-refine calibration for one order."""
    S = _slice_mid(S)
    if len(S[0]) < 40 or len(S[3]) < 40:
        return None
    trp, hop = interleaved(len(S[0]), 4)
    trv, hov = interleaved(len(S[3]), 4)
    sf_ref = float(np.std(np.diff(S[1])) + np.std(np.diff(S[2])) + 10.0)
    best = None
    for ell in (1.0, 1.4, 1.8, 2.4, 3.2, 4.5, 6.0):
        for sf in sf_ref * np.array([0.5, 1.0, 2.0, 4.0]):
            for sp in (0.4, 0.6, 0.9, 1.2, 1.6, 2.1):
                r = eval_hp(order, ell, sf, sp, delta, S, trp, trv, hop, hov)
                if r and (best is None or r["obj"] < best["obj"]):
                    best = r
    if best is None:
        return None
    for sf in (best["sf"] * 0.7, best["sf"], best["sf"] * 1.4):
        for ell in (best["ell"] * 0.8, best["ell"], best["ell"] * 1.25):
            for sp in (best["sp"] * 0.85, best["sp"], best["sp"] * 1.18):
                r = eval_hp(order, ell, sf, sp, delta, S, trp, trv, hop, hov)
                if r and r["obj"] < best["obj"]:
                    best = r
    return best


# ---------------------------------------------------------------------------
# Flying lap extractor
# ---------------------------------------------------------------------------
def get_flying_laps(q, car, min_n=100, mx=MAX_LAPS_PER_DRIVER):
    try:
        runs = H.driver_runs(q, car)
    except Exception:
        return []
    out = []
    try:
        windows = flying_windows(q, car)
    except Exception:
        return []
    for ls, le in windows:
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        tp, X, Y, tc, V = _stream(run)
        mp = (tp >= ls) & (tp <= le)
        mc = (tc >= ls) & (tc <= le)
        if mp.sum() >= min_n and mc.sum() >= min_n:
            out.append((tp[mp], X[mp], Y[mp], tc[mc], V[mc]))
    out.sort(key=lambda L: -len(L[3]))
    return out[:mx]


# ---------------------------------------------------------------------------
# Held-out speed error on a flying lap
# ---------------------------------------------------------------------------
def heldout_speed_err(lap, order, ell, sf, sp, delta):
    tp, X, Y, tc, V = lap
    nc = len(tc)
    if nc < 20:
        return np.array([])
    test = np.arange(2, nc, 4)
    train = np.setdiff1d(np.arange(nc), test)
    try:
        sm = MaternSmoother(ell, sf, sp, delta, order=order, iters=2)
        sm.fit(tp, X, Y, tc[train], V[train], query_times=tc[test] + delta)
        return np.abs(V[test] - sm.speed_at(tc[test] + delta))
    except Exception:
        return np.array([])


# ---------------------------------------------------------------------------
# Timing: per-fit wall-time and approximate per-step cost
# ---------------------------------------------------------------------------
def time_order(order, hp, delta, n_trials=3):
    """Measure wall-time for a synthetic fit of order `order`."""
    rng = np.random.default_rng(42)
    # Synthetic data: ~300 position + 300 speed samples
    N = 300
    t = np.sort(rng.uniform(0, 70, N))
    X = 50.0 * t + 5 * np.sin(0.2 * t) + rng.normal(0, hp["sp"], N)
    Y = 20.0 * t + 8 * np.cos(0.15 * t) + rng.normal(0, hp["sp"], N)
    tc = t + delta + rng.uniform(-0.05, 0.05, N)
    tc = np.sort(tc)
    V = np.hypot(50.0 + 5 * 0.2 * np.cos(0.2 * tc), 20.0 - 8 * 0.15 * np.sin(0.15 * tc))
    V += rng.normal(0, 0.5, N)
    times = []
    for _ in range(n_trials):
        t0 = time.perf_counter()
        sm = MaternSmoother(hp["ell"], hp["sf"], hp["sp"], delta, order=order, iters=2)
        sm.fit(t, X, Y, tc, V)
        times.append(time.perf_counter() - t0)
    # Per-step = total / (2*N merged timeline steps roughly)
    n_steps = 2 * N  # rough merged timeline length
    median_t = float(np.median(times))
    return dict(
        order=order,
        median_fit_s=median_t,
        per_step_us=1e6 * median_t / n_steps,
        n_steps_approx=n_steps,
        n_trials=n_trials,
    )


# ---------------------------------------------------------------------------
# Main validation loop
# ---------------------------------------------------------------------------
def main():
    hp_all = json.loads(HPJSON.read_text())

    # Load cache if exists (to resume interrupted runs)
    if CACHE_JSON.exists():
        cache = json.loads(CACHE_JSON.read_text())
        log(f"Loaded existing cache with {len(cache)} sessions")
    else:
        cache = {}

    per_session = []  # list of dicts with per-session summary
    err3_all = []     # pooled order-3 errors
    err4_all = []     # pooled order-4 errors
    ell3_list = []    # calibrated ell for order-3 per session
    ell4_list = []    # calibrated ell for order-4 per session

    log(f"Starting wide validation: {len(SESSIONS_2023)} sessions")
    log("=" * 78)

    for rd, nm in SESSIONS_2023:
        if nm not in hp_all:
            log(f"  SKIP {nm}: not in calibrated_hp.json")
            continue

        delta = hp_all[nm]["delta"]
        cache_key = nm

        # Use cached result if available
        if cache_key in cache:
            c = cache[cache_key]
            log(f"  {nm}: CACHED  5/2 ell={c['ell3']:.1f} med={c['med3']:.3f}  "
                f"7/2 ell={c['ell4']:.1f} med={c['med4']:.3f}  "
                f"n_laps={c['n_laps']}")
            per_session.append(c)
            if c["ell3"] is not None:
                ell3_list.append(c["ell3"])
            if c["ell4"] is not None:
                ell4_list.append(c["ell4"])
            if c["err3"]:
                err3_all.append(np.array(c["err3"]))
            if c["err4"]:
                err4_all.append(np.array(c["err4"]))
            continue

        log(f"\n--- Session {rd}: {nm} (delta={delta}) ---")

        # Load session
        try:
            q = H.load_session(2023, rd, "Q")
        except Exception as e:
            log(f"  LOAD FAIL: {e}")
            c = dict(session=nm, round=rd, status="load_fail",
                     ell3=None, ell4=None, c_pos3=None, c_spd3=None,
                     c_pos4=None, c_spd4=None,
                     med3=None, med4=None, glitch3=None, glitch4=None,
                     n_laps=0, err3=[], err4=[])
            per_session.append(c); cache[cache_key] = c
            CACHE_JSON.write_text(json.dumps(cache, indent=2))
            continue

        # Find calibration driver (VER or fallback)
        cal_driver = None
        cal_runs = []
        for cand in [CALIBRATION_DRIVER] + CALIBRATION_FALLBACKS:
            try:
                runs = H.driver_runs(q, cand)
                if runs:
                    cal_driver = cand
                    cal_runs = runs
                    break
            except Exception:
                continue

        if not cal_driver:
            log(f"  NO CALIBRATION DRIVER")
            c = dict(session=nm, round=rd, status="no_cal_driver",
                     ell3=None, ell4=None, c_pos3=None, c_spd3=None,
                     c_pos4=None, c_spd4=None,
                     med3=None, med4=None, glitch3=None, glitch4=None,
                     n_laps=0, err3=[], err4=[])
            per_session.append(c); cache[cache_key] = c
            CACHE_JSON.write_text(json.dumps(cache, indent=2))
            continue

        # Pick longest run for calibration
        S_cal = _stream(max(cal_runs, key=lambda r: len(r["X"])))
        log(f"  Cal driver: {cal_driver}, pos={len(S_cal[0])} spd={len(S_cal[3])} pts")

        # Calibrate both orders
        t0 = time.perf_counter()
        h3 = calibrate_order(3, S_cal, delta)
        t_cal3 = time.perf_counter() - t0

        t0 = time.perf_counter()
        h4 = calibrate_order(4, S_cal, delta)
        t_cal4 = time.perf_counter() - t0

        if h3 is None or h4 is None:
            log(f"  CALIBRATION FAILED (h3={h3 is not None}, h4={h4 is not None})")
            c = dict(session=nm, round=rd, status="cal_fail",
                     ell3=None, ell4=None, c_pos3=None, c_spd3=None,
                     c_pos4=None, c_spd4=None,
                     med3=None, med4=None, glitch3=None, glitch4=None,
                     n_laps=0, err3=[], err4=[])
            per_session.append(c); cache[cache_key] = c
            CACHE_JSON.write_text(json.dumps(cache, indent=2))
            continue

        log(f"  5/2: ell={h3['ell']:.2f} sp={h3['sp']:.2f} chi2={h3['c_pos']:.2f}/{h3['c_spd']:.2f} ({t_cal3:.1f}s)")
        log(f"  7/2: ell={h4['ell']:.2f} sp={h4['sp']:.2f} chi2={h4['c_pos']:.2f}/{h4['c_spd']:.2f} ({t_cal4:.1f}s)")

        # Collect held-out speed errors from multiple drivers
        err3 = []
        err4 = []
        n_laps_used = 0
        drivers_tested = []

        for car in DRIVERS:
            if len(drivers_tested) >= MAX_DRIVERS_PER_SESSION:
                break
            laps = get_flying_laps(q, car)
            if not laps:
                continue
            car_err3 = []
            car_err4 = []
            for lap in laps:
                e3 = heldout_speed_err(lap, 3, h3["ell"], h3["sf"], h3["sp"], delta)
                e4 = heldout_speed_err(lap, 4, h4["ell"], h4["sf"], h4["sp"], delta)
                if len(e3) > 0 and len(e4) > 0:
                    car_err3.append(e3)
                    car_err4.append(e4)
                    n_laps_used += 1
            if car_err3:
                err3.extend(car_err3)
                err4.extend(car_err4)
                drivers_tested.append(car)

        if not err3:
            log(f"  NO HELD-OUT DATA")
            c = dict(session=nm, round=rd, status="no_data",
                     ell3=h3["ell"], ell4=h4["ell"],
                     c_pos3=h3["c_pos"], c_spd3=h3["c_spd"],
                     c_pos4=h4["c_pos"], c_spd4=h4["c_spd"],
                     med3=None, med4=None, glitch3=None, glitch4=None,
                     n_laps=0, err3=[], err4=[])
            per_session.append(c); cache[cache_key] = c
            CACHE_JSON.write_text(json.dumps(cache, indent=2))
            continue

        a3 = np.concatenate(err3)
        a4 = np.concatenate(err4)
        med3 = float(np.median(a3))
        med4 = float(np.median(a4))
        glitch3 = float(100 * np.mean(a3 > 5))
        glitch4 = float(100 * np.mean(a4 > 5))

        log(f"  drivers={drivers_tested} n_laps={n_laps_used}")
        log(f"  5/2 median|e|={med3:.3f} glitch={glitch3:.1f}%  "
            f"7/2 median|e|={med4:.3f} glitch={glitch4:.1f}%")
        log(f"  Delta: 7/2-5/2 median={med4-med3:+.3f}  "
            f"{'[7/2 WINS]' if med4 < med3 else '[5/2 WINS or TIED]'}")

        c = dict(
            session=nm, round=rd, status="ok",
            cal_driver=cal_driver, drivers=drivers_tested,
            ell3=h3["ell"], ell4=h4["ell"],
            c_pos3=h3["c_pos"], c_spd3=h3["c_spd"],
            c_pos4=h4["c_pos"], c_spd4=h4["c_spd"],
            med3=med3, med4=med4,
            glitch3=glitch3, glitch4=glitch4,
            n_laps=n_laps_used,
            n_pts3=int(len(a3)), n_pts4=int(len(a4)),
            err3=a3.tolist(), err4=a4.tolist(),
        )
        per_session.append(c)
        cache[cache_key] = c
        ell3_list.append(h3["ell"])
        ell4_list.append(h4["ell"])
        err3_all.append(a3)
        err4_all.append(a4)
        CACHE_JSON.write_text(json.dumps(cache, indent=2))

    # -------------------------------------------------------------------------
    # TIMING: per-fit wall-time order-3 vs order-4
    # -------------------------------------------------------------------------
    log("\n" + "=" * 78)
    log("TIMING: per-fit wall-time order-3 vs order-4")
    log("=" * 78)

    # Use Bahrain HPs (representative)
    ref_nm = "Bahrain"
    ref_hp = hp_all.get(ref_nm, list(hp_all.values())[0])
    ref_delta = ref_hp["delta"]
    timing3 = time_order(3, {"ell": ref_hp["ell"], "sf": ref_hp["sf"], "sp": ref_hp["sig_pos"]}, ref_delta)
    timing4 = time_order(4, {"ell": ref_hp["ell"], "sf": ref_hp["sf"], "sp": ref_hp["sig_pos"]}, ref_delta)
    timing_ratio = timing4["median_fit_s"] / max(timing3["median_fit_s"], 1e-9)
    log(f"  order-3 (5/2): {timing3['median_fit_s']*1000:.1f} ms  {timing3['per_step_us']:.2f} us/step")
    log(f"  order-4 (7/2): {timing4['median_fit_s']*1000:.1f} ms  {timing4['per_step_us']:.2f} us/step")
    log(f"  ratio 7/2 / 5/2 = {timing_ratio:.2f}x")

    # -------------------------------------------------------------------------
    # POOLED RESULTS
    # -------------------------------------------------------------------------
    log("\n" + "=" * 78)
    log("POOLED held-out speed (all sessions with data)")
    log("=" * 78)

    ok_sessions = [c for c in per_session if c.get("status") == "ok"]
    failed_sessions = [c for c in per_session if c.get("status") != "ok"]

    if err3_all:
        A3 = np.concatenate(err3_all)
        A4 = np.concatenate(err4_all)
        log(f"  Sessions OK: {len(ok_sessions)}  Failed/skipped: {len(failed_sessions)}")
        log(f"  Total points: {len(A3)}")
        log(f"")
        log(f"  {'order':>8} {'median|e|':>10} {'MAE':>8} {'glitch>5':>9} {'n':>8}")
        for lbl, A in [("5/2", A3), ("7/2", A4)]:
            log(f"  {lbl:>8} {np.median(A):>10.3f} {A.mean():>8.3f} {100*np.mean(A>5):>8.1f}% {len(A):>8}")
        log(f"")
        log(f"  Delta 7/2-5/2: median {np.median(A4)-np.median(A3):+.3f} m/s  "
            f"MAE {A4.mean()-A3.mean():+.3f}  glitch {100*(np.mean(A4>5)-np.mean(A3>5)):+.1f}pp")
    else:
        log("  NO DATA COLLECTED")

    # -------------------------------------------------------------------------
    # ELL DISTRIBUTION
    # -------------------------------------------------------------------------
    log("\n" + "=" * 78)
    log("CALIBRATED ell DISTRIBUTION (per-session chi2-target calibration)")
    log("=" * 78)
    if ell3_list:
        e3 = np.array(ell3_list)
        e4 = np.array(ell4_list)
        log(f"  order-3 (5/2): min={e3.min():.2f} median={np.median(e3):.2f} max={e3.max():.2f}  "
            f"n<=1.5: {int((e3<=1.5).sum())}/{len(e3)} (short-ell collapses)")
        log(f"  order-4 (7/2): min={e4.min():.2f} median={np.median(e4):.2f} max={e4.max():.2f}  "
            f"n<=1.5: {int((e4<=1.5).sum())}/{len(e4)} (short-ell collapses)")
        log(f"")
        log(f"  Per-session ell3/ell4:")
        for c in ok_sessions:
            log(f"    {c['session']:<15} 5/2 ell={c['ell3']:.2f}  7/2 ell={c['ell4']:.2f}  "
                f"med: 5/2={c['med3']:.3f} 7/2={c['med4']:.3f}  "
                f"{'[7/2 wins]' if c['med4'] < c['med3'] else '[5/2 wins/tied]'}")

    # -------------------------------------------------------------------------
    # PER-SESSION TABLE
    # -------------------------------------------------------------------------
    log("\n" + "=" * 78)
    log("PER-SESSION SUMMARY TABLE")
    log("=" * 78)
    hdr = (f"{'Session':>15} {'ell3':>6} {'chi2p3':>7} {'chi2s3':>7} "
           f"{'ell4':>6} {'chi2p4':>7} {'chi2s4':>7} "
           f"{'med3':>7} {'med4':>7} {'g3%':>6} {'g4%':>6} {'n_laps':>7} status")
    log(hdr)
    log("-" * len(hdr))
    for c in per_session:
        if c.get("status") == "ok":
            log(
                f"{c['session']:>15} {c['ell3']:>6.2f} {c['c_pos3']:>7.3f} {c['c_spd3']:>7.3f} "
                f"{c['ell4']:>6.2f} {c['c_pos4']:>7.3f} {c['c_spd4']:>7.3f} "
                f"{c['med3']:>7.3f} {c['med4']:>7.3f} {c['glitch3']:>6.1f} {c['glitch4']:>6.1f} "
                f"{c['n_laps']:>7} {c['status']}"
            )
        else:
            log(f"{c['session']:>15} {'---':>6} {'---':>7} {'---':>7} "
                f"{'---':>6} {'---':>7} {'---':>7} "
                f"{'---':>7} {'---':>7} {'---':>6} {'---':>6} "
                f"{'0':>7} {c.get('status','?')}")

    # -------------------------------------------------------------------------
    # Save timing to cache
    # -------------------------------------------------------------------------
    timing_result = dict(
        order3=timing3,
        order4=timing4,
        ratio_4_over_3=timing_ratio,
    )
    cache["_timing"] = timing_result
    CACHE_JSON.write_text(json.dumps(cache, indent=2))
    log(f"\nCache written to {CACHE_JSON}")

    # -------------------------------------------------------------------------
    # VERDICT
    # -------------------------------------------------------------------------
    log("\n" + "=" * 78)
    log("VERDICT")
    log("=" * 78)
    if err3_all:
        A3 = np.concatenate(err3_all)
        A4 = np.concatenate(err4_all)
        wins_7 = sum(1 for c in ok_sessions if c["med4"] < c["med3"])
        wins_5 = sum(1 for c in ok_sessions if c["med3"] <= c["med4"])
        log(f"  7/2 wins on median|e| in {wins_7}/{len(ok_sessions)} sessions")
        log(f"  5/2 wins or ties in {wins_5}/{len(ok_sessions)} sessions")
        margin = np.median(A3) - np.median(A4)
        log(f"  Pooled margin 5/2 - 7/2: {margin:.3f} m/s  (>0 = 7/2 better)")
        log(f"  Sensor floor: 0.49 m/s")
        log(f"  7/2 pooled median: {np.median(A4):.3f} m/s  (target: near 0.49)")
        log(f"  Cost ratio 7/2/5/2: {timing_ratio:.2f}x")
    log("=" * 78)

    return per_session, timing_result


if __name__ == "__main__":
    main()
