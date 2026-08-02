"""Run M1 variant against gaussian + kind3 on the G2 scoreboard cases.

Usage:
    py scripts/run_m1_scoreboard.py

Prints the scoreboard table and full JSON.
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS
from src.physics.layer2.variant_m1 import (
    variant_m1_tight,
    variant_m1_moderate,
    variant_m1_loose,
)

CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [(2023, "Bahrain", "VER"), (2023, "Monaco", "VER"), (2023, "Belgium", "VER")]

variants = dict(BUILTIN_VARIANTS)   # gaussian + kind3 baselines
variants["m1_tight"] = variant_m1_tight      # sigma=0.5
variants["m1_moderate"] = variant_m1_moderate  # sigma=1.0
variants["m1_loose"] = variant_m1_loose      # sigma=2.0

print("Running G2 M1 scoreboard (sigma sensitivity: tight=0.5, moderate=1.0, loose=2.0)")
print("Cases:", CASES)
print()

table = run_scoreboard(CASES, variants, cache=CACHE)

print("=== MARKDOWN TABLE ===")
print(table.markdown_table())

print()
print("=== FULL JSON (knee / ringing / gaps) ===")
print(json.dumps(table.to_json(), indent=2))

# Also print per-case detail
print()
print("=== PER-CASE DETAIL ===")
for cr in table.cases:
    print(f"\n--- {cr.gp} {cr.year} {cr.driver} (lap {cr.lap_no}, {cr.best_s:.2f}s) ---")
    print(f"  n_brake={cr.n_brake}, n_coast={cr.n_coast}")
    for name, vs in cr.scores.items():
        print(f"  {name:15s}: knee={vs.knee:7.2f}  ringing={vs.ringing:6.2f}  "
              f"knee_gap={vs.knee_gap_vs_raw:+7.2f}  ring_over={vs.ringing_over_ceiling:+6.2f}  "
              f"ringing_ok={vs.ringing_ok}")
    if cr.scores:
        ref = next(iter(cr.scores.values()))
        print(f"  {'raw_ref':15s}: knee={ref.raw_knee:7.2f}  ringing={ref.raw_ring:6.2f}")
