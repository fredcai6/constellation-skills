"""Mandatory pre-flight: ONE weekend (Hungary), fastest-K=3, FULL FIELD, FP1-3 + Q,
at the exact powered-run config, to completion. Times it for the 16-weekend extrapolation.
Writes PREFLIGHT_RESULT.txt ending in DONE/FAILED."""
import sys, time, traceback
sys.path.insert(0, "C:/Programs/f1-fp-powered")
from src.physics.layer2.fp_gate_real_extractor import make_extractor

OUT = "C:/Programs/f1-fp-powered/.agent-work/PREFLIGHT_RESULT.txt"
def log(m):
    with open(OUT, "a", encoding="utf-8") as f: f.write(m + "\n")
    print(m, flush=True)

open(OUT, "w").close()
t0 = time.time()
log("PRE-FLIGHT slice: Hungary 2023, FP1+FP2+FP3, FULL FIELD, fastest-3-laps")
try:
    ex = make_extractor(
        year=2023, weekends=["Hungary"],
        db_path="C:/Programs/f1-fp-powered/data/f1_data_2023.db",
        sessions=("FP1", "FP2", "FP3"), max_drivers=None, max_laps_per_driver=3,
    )
    fp = ex.fp_observations("Hungary")
    t_fp = time.time() - t0
    log(f"fp_observations: {len(fp)} real RawFpObservation in {t_fp:.0f}s")
    for o in fp[:6]:
        log(f"  FP car={o.car_id} sess={o.session_type} grip={o.grip_value:.4f} h2q={o.hours_to_q} "
            f"trk_evo={o.track_evolution} fp_mass_sig={o.fp_mass_sigma_kg}")
    t1 = time.time()
    q = ex.q_targets("Hungary")
    t_q = time.time() - t1
    log(f"q_targets: {len(q)} real RawQTarget in {t_q:.0f}s")
    for t in q[:6]:
        log(f"  Q car={t.car_id} grip_capability={t.grip_capability:.4f}")
    total = time.time() - t0
    log(f"PRE-FLIGHT DONE in {total:.0f}s (fp={t_fp:.0f}s, q={t_q:.0f}s) for ONE weekend, FULL FIELD, FP1-3+Q")
    log(f"EXTRAPOLATION: 16 weekends approx {total*16/3600:.2f}h (linear; LOWO refits are cheap vs extraction)")
except Exception as e:
    log(f"PRE-FLIGHT FAILED in {time.time()-t0:.0f}s: {type(e).__name__}: {e}")
    log(traceback.format_exc())
