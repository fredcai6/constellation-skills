"""THIN ILLUSTRATIVE demo (Admiral-greenlit) — real telemetry end-to-end, NOT the F10 verdict.
4 cornering-dominated 2023 weekends, FP2+FP3+Q, fastest-3-laps. Underpowered by design (4 LOWO folds).
Writes a report to .agent-work/513-fp-followup/DEMO_RESULT.txt."""
import sys, time, traceback
sys.path.insert(0, "C:/Programs/f1-513")
from src.physics.layer2.fp_gate_real_extractor import make_extractor
from src.physics.layer2.fp_gate import (
    build_gate_observations, run_lowo, evaluate_gate, secondary_power_gate,
    emergence_audit, sandbagging_demo,
)
from scripts.fp_representativeness_gate import format_report

OUT = "C:/Programs/f1-513/.agent-work/513-fp-followup/DEMO_RESULT.txt"
WEEKENDS = ["Hungary", "Spain", "Singapore", "Netherlands"]
DB = "C:/Programs/f1-513/data/f1_data_2023.db"

def log(msg):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)

open(OUT, "w").close()
t0 = time.time()
log(f"THIN DEMO (illustrative-not-evidential) start; weekends={WEEKENDS}; fastest-3-laps FP2+FP3+Q")
try:
    ex = make_extractor(year=2023, weekends=WEEKENDS, db_path=DB,
                        sessions=("FP2", "FP3"), max_laps_per_driver=3)
    weekend_data = build_gate_observations(WEEKENDS, ex, quali_fuel_kg=15.0)
    log(f"built gate observations for {len(weekend_data)} weekends in {time.time()-t0:.0f}s")
    lowo = run_lowo(weekend_data)
    primary = evaluate_gate(weekend_data, lowo, n_resamples=10000, seed=0)
    secondary = secondary_power_gate(weekend_data, n_resamples=10000, seed=1000)
    emergence = emergence_audit()
    try:
        sandbag = sandbagging_demo(weekend_data)
    except ValueError:
        sandbag = None
    log("")
    log("=== DEMO REPORT (ILLUSTRATIVE-NOT-EVIDENTIAL; 4 folds; NOT the frozen F10 verdict) ===")
    log(format_report(primary, secondary, emergence, sandbag))
    log("")
    log(f"DEMO COMPLETE in {time.time()-t0:.0f}s")
except Exception as e:
    log(f"DEMO FAILED in {time.time()-t0:.0f}s: {type(e).__name__}: {e}")
    log(traceback.format_exc())
