"""G7 pre-measurement: single FP smoke fit — validates G5 wiring live + measures single-fit ETA.
Run with PYTHONPATH=C:/Programs/f1-513 and OMP/OPENBLAS threads set in ENV."""
import sys, time
sys.path.insert(0, "C:/Programs/f1-513")
from src.physics.layer2.session_estimator import estimate_session
from src.physics.mass_model import fp_mass, quali_mass

DB = "C:/Programs/f1-513/data/f1_data_2023.db"
YEAR, GP = 2023, "Hungary"
print(f"quali_mass({YEAR})={quali_mass(YEAR):.1f}  fp_mass({YEAR}).mean={fp_mass(YEAR).mass_kg:.1f} sigma={fp_mass(YEAR).sigma_kg:.1f}", flush=True)

for stype in ("Q", "FP2"):
    t0 = time.time()
    try:
        est = estimate_session(year=YEAR, gp=GP, drivers=("VER", "PER"),
                               session_type=stype, db_path=(DB if stype.startswith("FP") else None),
                               with_lateral=True, with_coast=True)
        dt = time.time() - t0
        print(f"[{stype}] OK in {dt:.1f}s  mass_kg={est.mass_kg}  mass_sigma_kg={getattr(est,'mass_sigma_kg',None)}  "
              f"CdA={est.power_drag.drag_area_closed_m2:.3f}  P_max={est.power_drag.max_power_w:.0f}", flush=True)
    except Exception as e:
        print(f"[{stype}] FAILED in {time.time()-t0:.1f}s: {type(e).__name__}: {e}", flush=True)
