"""G1 repro probe: re-run the 19 OLD-store failing 2023-Q cases on current code.

Calls load_quali_session + fit_driver per case (the natural per-case unit).
Captures current FitRecord.fit_status + error. Throwaway; lives under .agent-work/.
"""
import sys
import time
import traceback

from src.physics.session_fit import load_quali_session, fit_driver
from src.physics.fit_batch import _list_drivers
from src.utils.constants import get_calendar

# (gp, driver, old_status, old_error_pattern)
CASES = [
    ("Japan", "PIA", "error", "interleaved"),
    ("Japan", "NOR", "error", "interleaved"),
    ("Japan", "LEC", "error", "interleaved"),
    ("Japan", "SAI", "error", "interleaved"),
    ("Japan", "MAG", "error", "interleaved"),
    ("Netherlands", "SAR", "error", "interleaved"),
    ("Mexico", "ZHO", "error", "interleaved"),
    ("Brazil", "PIA", "error", "interleaved"),
    ("Las Vegas", "BOT", "error", "interleaved"),
    ("Abu Dhabi", "VER", "error", "interleaved"),
    ("Saudi Arabia", "DEV", "error", "interleaved"),
    ("Azerbaijan", "GAS", "error", "interleaved"),
    ("Azerbaijan", "DEV", "error", "interleaved"),
    ("Miami", "BOT", "error", "interleaved"),
    ("Canada", "ALB", "error", "interleaved"),
    ("Bahrain", "ALO", "error", "NoneType"),
    ("Bahrain", "HAM", "error", "NoneType"),
    ("Canada", "HUL", "error", "NoneType"),
    ("Japan", "SAR", "no_laps", None),
]

YEAR = 2023
SES = "Q"


def round_of(gp):
    cal = get_calendar(YEAR)
    for i, name in enumerate(cal, start=1):
        if name == gp:
            return i
    return None


def main():
    # Cache loaded sessions per GP (one load, reuse across that GP's drivers).
    sess_cache = {}
    results = []
    for gp, drv, old_status, old_pat in CASES:
        t0 = time.time()
        try:
            if gp not in sess_cache:
                session, rho, rho_fb = load_quali_session(YEAR, gp, SES)
                sess_cache[gp] = (session, rho, rho_fb)
            session, rho, rho_fb = sess_cache[gp]
            ridx = round_of(gp)
            # constructor: look it up from list_drivers
            cons = "Unknown"
            for abbr, team in _list_drivers(session):
                if abbr == drv:
                    cons = team
                    break
            rec = fit_driver(
                session, drv, year=YEAR, gp_name=gp, round_idx=ridx,
                session_type=SES, constructor=cons, rho=rho,
            )
            dt = time.time() - t0
            results.append((gp, drv, old_status, old_pat, rec.fit_status,
                            rec.error, rec.n_flying_laps, rec.n_samples_used, dt))
            print(f"[{rec.fit_status}] {gp} {drv} (old={old_status}/{old_pat}) "
                  f"n_fly={rec.n_flying_laps} n_samp={rec.n_samples_used} err={rec.error!r} {dt:.1f}s",
                  flush=True)
        except Exception as exc:
            dt = time.time() - t0
            tb = traceback.format_exc()
            results.append((gp, drv, old_status, old_pat, "RAISED",
                            str(exc), None, None, dt))
            print(f"[RAISED] {gp} {drv} (old={old_status}/{old_pat}) {exc!r} {dt:.1f}s",
                  flush=True)
            print(tb, flush=True)

    print("\n=== SUMMARY TABLE ===")
    print(f"{'GP':<14}{'DRV':<5}{'OLD':<9}{'NEW_STATUS':<18}{'NFLY':<6}{'NSAMP':<8}NEW_ERROR")
    for gp, drv, old_s, old_p, new_s, new_e, nfly, nsamp, dt in results:
        print(f"{gp:<14}{drv:<5}{old_s:<9}{new_s:<18}{str(nfly):<6}{str(nsamp):<8}{new_e!r}")

    # status histogram
    from collections import Counter
    hist = Counter(r[4] for r in results)
    print("\n=== NEW STATUS HISTOGRAM ===")
    for k, v in sorted(hist.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
