"""Admiral gate: a MINIMAL COMPLETED real-telemetry pass through RealGateExtractor.
ONE weekend (Hungary), ~8 drivers, fastest-2-laps, FP2 + Q — produces real RawFpObservation/RawQTarget
end-to-end. Writes MINIMAL_PASS.txt ending in DONE/FAILED."""
import sys, time, traceback
sys.path.insert(0, "C:/Programs/f1-513")
from src.physics.layer2.fp_gate_real_extractor import make_extractor

OUT = "C:/Programs/f1-513/.agent-work/513-fp-followup/MINIMAL_PASS.txt"
def log(m):
    with open(OUT, "a", encoding="utf-8") as f: f.write(m + "\n")
    print(m, flush=True)

open(OUT, "w").close()
t0 = time.time()
log("MINIMAL real-telemetry pass: Hungary 2023, FP2, 8 drivers, fastest-2-laps")
try:
    ex = make_extractor(year=2023, weekends=["Hungary"],
                        db_path="C:/Programs/f1-513/data/f1_data_2023.db",
                        sessions=("FP2",), max_drivers=8, max_laps_per_driver=2)
    fp = ex.fp_observations("Hungary")
    log(f"fp_observations: {len(fp)} real RawFpObservation in {time.time()-t0:.0f}s")
    for o in fp[:4]:
        log(f"  FP car={o.car_id} sess={o.session_type} grip={o.grip_value:.4f} h2q={o.hours_to_q} "
            f"trk_evo={o.track_evolution} fp_mass_sig={o.fp_mass_sigma_kg} compound={o.latent.compound} "
            f"run_purpose={o.latent.run_purpose}")
    t1 = time.time()
    q = ex.q_targets("Hungary")
    log(f"q_targets: {len(q)} real RawQTarget in {time.time()-t1:.0f}s")
    for t in q[:4]:
        log(f"  Q car={t.car_id} grip_capability={t.grip_capability:.4f}")
    log(f"MINIMAL PASS DONE in {time.time()-t0:.0f}s — RealGateExtractor produced real observations end-to-end")
except Exception as e:
    log(f"MINIMAL PASS FAILED in {time.time()-t0:.0f}s: {type(e).__name__}: {e}")
    log(traceback.format_exc())
