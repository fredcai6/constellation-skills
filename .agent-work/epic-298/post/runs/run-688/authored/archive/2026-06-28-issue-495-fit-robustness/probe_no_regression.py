"""G3 no-regression probe: re-fit 24 previously-ok 2023-Q cases on current code.

Compares new fit_status and key params against old data/physics_fits.db baseline.
Sample: 4 drivers x 6 circuits (Bahrain, Monaco, Japan, Brazil, Abu Dhabi, Italy).
"""
import sqlite3
import sys
import time
import traceback

from src.physics.session_fit import load_quali_session, fit_driver
from src.physics.fit_batch import _list_drivers
from src.utils.constants import get_calendar

YEAR = 2023
SES = "Q"
OLD_DB = "data/physics_fits.db"

# Sampled ok cases: (gp, driver, constructor, round_idx)
SAMPLE = [
    # Bahrain (round 1)
    ("Bahrain", "ALB", "Williams", 1),
    ("Bahrain", "BOT", "Alfa Romeo", 1),
    ("Bahrain", "DEV", "AlphaTauri", 1),
    ("Bahrain", "GAS", "Alpine", 1),
    # Monaco (round 6)
    ("Monaco", "ALB", "Williams", 6),
    ("Monaco", "ALO", "Aston Martin", 6),
    ("Monaco", "BOT", "Alfa Romeo", 6),
    ("Monaco", "DEV", "AlphaTauri", 6),
    # Japan (round 16)
    ("Japan", "ALB", "Williams", 16),
    ("Japan", "ALO", "Aston Martin", 16),
    ("Japan", "BOT", "Alfa Romeo", 16),
    ("Japan", "GAS", "Alpine", 16),
    # Brazil (round 20)
    ("Brazil", "ALB", "Williams", 20),
    ("Brazil", "ALO", "Aston Martin", 20),
    ("Brazil", "BOT", "Alfa Romeo", 20),
    ("Brazil", "GAS", "Alpine", 20),
    # Abu Dhabi (round 22)
    ("Abu Dhabi", "ALB", "Williams", 22),
    ("Abu Dhabi", "ALO", "Aston Martin", 22),
    ("Abu Dhabi", "BOT", "Alfa Romeo", 22),
    ("Abu Dhabi", "GAS", "Alpine", 22),
    # Italy (round 14)
    ("Italy", "ALB", "Williams", 14),
    ("Italy", "ALO", "Aston Martin", 14),
    ("Italy", "BOT", "Alfa Romeo", 14),
    ("Italy", "GAS", "Alpine", 14),
]

TOL_REL = 1e-6  # relative tolerance for float comparison


def load_old_params(db_path):
    """Load old baseline params for all sample cases."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    old = {}
    for gp, drv, cons, ridx in SAMPLE:
        cur.execute(
            """SELECT fit_status, spec_drag_m2_kg, rolling_decel_ms2, lateral_mech_grip_ms2
               FROM session_fits
               WHERE year=? AND gp_name=? AND session_type=? AND driver=?""",
            (YEAR, gp, SES, drv),
        )
        row = cur.fetchone()
        if row:
            old[(gp, drv)] = {
                "fit_status": row[0],
                "spec_drag_m2_kg": row[1],
                "rolling_decel_ms2": row[2],
                "lateral_mech_grip_ms2": row[3],
            }
    conn.close()
    return old


def floats_match(a, b, tol=TOL_REL):
    """Check two floats match within relative tolerance."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if a == 0 and b == 0:
        return True
    return abs(a - b) / max(abs(a), abs(b)) <= tol


def main():
    print(f"Loading old DB baseline from {OLD_DB} ...", flush=True)
    old_params = load_old_params(OLD_DB)
    print(f"Loaded {len(old_params)} old-baseline records.\n", flush=True)

    sess_cache = {}
    results = []
    t_total = time.time()

    for gp, drv, cons, ridx in SAMPLE:
        t0 = time.time()
        try:
            if gp not in sess_cache:
                session, rho, rho_fb = load_quali_session(YEAR, gp, SES)
                sess_cache[gp] = (session, rho, rho_fb)
            session, rho, rho_fb = sess_cache[gp]
            rec = fit_driver(
                session, drv, year=YEAR, gp_name=gp, round_idx=ridx,
                session_type=SES, constructor=cons, rho=rho,
            )
            dt = time.time() - t0
            old = old_params.get((gp, drv))
            # Compare
            status_ok = rec.fit_status == "ok"
            drag_ok = floats_match(rec.spec_drag_m2_kg, old["spec_drag_m2_kg"] if old else None)
            roll_ok = floats_match(rec.rolling_decel_ms2, old["rolling_decel_ms2"] if old else None)
            lat_ok = floats_match(rec.lateral_mech_grip_ms2, old["lateral_mech_grip_ms2"] if old else None)
            all_ok = status_ok and drag_ok and roll_ok and lat_ok

            flag = "PASS" if all_ok else "FAIL"
            results.append({
                "gp": gp, "drv": drv,
                "new_status": rec.fit_status,
                "old_status": old["fit_status"] if old else None,
                "new_drag": rec.spec_drag_m2_kg,
                "old_drag": old["spec_drag_m2_kg"] if old else None,
                "new_roll": rec.rolling_decel_ms2,
                "old_roll": old["rolling_decel_ms2"] if old else None,
                "new_lat": rec.lateral_mech_grip_ms2,
                "old_lat": old["lateral_mech_grip_ms2"] if old else None,
                "drag_ok": drag_ok,
                "roll_ok": roll_ok,
                "lat_ok": lat_ok,
                "flag": flag,
                "dt": dt,
            })
            print(f"[{flag}] {gp:<14} {drv:<5} status={rec.fit_status} "
                  f"drag_match={drag_ok} roll_match={roll_ok} lat_match={lat_ok} "
                  f"({dt:.1f}s)", flush=True)
        except Exception as exc:
            dt = time.time() - t0
            tb = traceback.format_exc()
            results.append({
                "gp": gp, "drv": drv, "flag": "RAISED", "new_status": "RAISED",
                "error": str(exc), "dt": dt,
            })
            print(f"[RAISED] {gp:<14} {drv:<5} {exc!r} ({dt:.1f}s)", flush=True)
            print(tb, flush=True)

    total_dt = time.time() - t_total
    n_pass = sum(1 for r in results if r["flag"] == "PASS")
    n_fail = sum(1 for r in results if r["flag"] == "FAIL")
    n_raised = sum(1 for r in results if r["flag"] == "RAISED")

    print(f"\n=== NO-REGRESSION SUMMARY ===", flush=True)
    print(f"Total: {len(results)}  PASS: {n_pass}  FAIL: {n_fail}  RAISED: {n_raised}", flush=True)
    print(f"Wall time: {total_dt:.0f}s", flush=True)

    if n_fail > 0 or n_raised > 0:
        print("\nFAILURES / RAISES:", flush=True)
        for r in results:
            if r["flag"] in ("FAIL", "RAISED"):
                print(f"  {r['gp']} {r['drv']}: {r}", flush=True)

    print("\n=== DETAILED TABLE ===")
    print(f"{'GP':<14}{'DRV':<5}{'FLAG':<7}{'STATUS':<6}{'DRAG_MATCH':<12}{'ROLL_MATCH':<12}{'LAT_MATCH':<12}")
    for r in results:
        print(f"{r['gp']:<14}{r['drv']:<5}{r['flag']:<7}{r.get('new_status',''):<6}"
              f"{str(r.get('drag_ok','')):<12}{str(r.get('roll_ok','')):<12}{str(r.get('lat_ok','')):<12}")

    return 0 if (n_fail == 0 and n_raised == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
