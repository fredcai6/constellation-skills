"""G7 feasibility probe: time session-load + per-driver apex extraction to size the LOWO fold count."""
import sys, time
sys.path.insert(0, "C:/Programs/f1-513")
import numpy as np
from src.physics.session_fit import load_quali_session, DEFAULT_CACHE
from src.physics.layer2.session_braking import _driver_samples
from src.physics.apex_extract import extract_apex_observations

YEAR, GP, STYPE = 2023, "Hungary", "FP2"
t0 = time.time()
session, rho, fb = load_quali_session(YEAR, GP, STYPE, DEFAULT_CACHE)
t_load = time.time() - t0
print(f"LOAD {YEAR} {GP} {STYPE}: {t_load:.1f}s  rho={rho:.3f} fallback={fb}", flush=True)

# time per-driver smoothing + apex extraction for up to 3 drivers
drivers = ["VER", "NOR", "HAM"]
per = []
for drv in drivers:
    t1 = time.time()
    try:
        out = _driver_samples(session, drv)
        if out is None:
            print(f"  {drv}: no samples", flush=True); continue
        processed_df = out[0]
        # extract apexes per lap group
        n_apex = 0
        if processed_df is not None and "lap_number" in processed_df.columns:
            for lap, g in processed_df.groupby("lap_number"):
                try:
                    obs = extract_apex_observations(g)
                    n_apex += len(obs)
                except Exception:
                    pass
        dt = time.time() - t1
        per.append(dt)
        print(f"  {drv}: {dt:.1f}s  apexes={n_apex}", flush=True)
    except Exception as e:
        print(f"  {drv}: ERR {type(e).__name__}: {e}", flush=True)

if per:
    mean = np.mean(per)
    print(f"MEAN per-driver: {mean:.1f}s  => ~20 drivers/session ~ {mean*20:.0f}s"
          f"  => 6 weekends x4 sessions x20 drv ~ {mean*20*24/60:.0f} min", flush=True)
