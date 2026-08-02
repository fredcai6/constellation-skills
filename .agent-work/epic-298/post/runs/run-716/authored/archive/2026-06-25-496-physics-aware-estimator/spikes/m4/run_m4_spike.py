"""M4 spike runner — regime-gated process noise scoreboard sweep.

Usage:
    py scripts/run_m4_spike.py

Runs the common G1 scoreboard on Bahrain/Monaco/Belgium 2023 Q VER for:
  - gaussian baseline
  - kind3 baseline
  - m4 (several HP settings)

Writes raw JSON to stdout and a Markdown table to stdout.
"""
from __future__ import annotations

import json
import sys
import os

# Ensure repo root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS
from src.physics.layer2.m4_regime_gated import M4Params, make_m4_variant

CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [
    (2023, "Bahrain", "VER"),
    (2023, "Monaco", "VER"),
    (2023, "Belgium", "VER"),
]

# Sweep configurations
SWEEP = {
    "m4_default":   M4Params(gate_strength=6.0, lead_s=0.3, trail_s=0.5, thresh_g=1.5),
    "m4_tight":     M4Params(gate_strength=4.0, lead_s=0.15, trail_s=0.3, thresh_g=2.0),
    "m4_wide":      M4Params(gate_strength=8.0, lead_s=0.5, trail_s=0.8, thresh_g=1.0),
    "m4_strong":    M4Params(gate_strength=10.0, lead_s=0.3, trail_s=0.5, thresh_g=1.5),
    "m4_regime_only": M4Params(gate_strength=6.0, lead_s=0.3, trail_s=0.5, use_regime=True, use_dv=False),
    "m4_dv_only":   M4Params(gate_strength=6.0, lead_s=0.3, trail_s=0.5, use_regime=False, use_dv=True, thresh_g=1.5),
}

def main():
    variants = dict(BUILTIN_VARIANTS)
    for name, params in SWEEP.items():
        variants[name] = make_m4_variant(params)

    print(f"Running scoreboard on {len(CASES)} cases x {len(variants)} variants...")
    table = run_scoreboard(CASES, variants, cache=CACHE)

    print("\n=== MARKDOWN TABLE (knee m/s²) ===")
    print(table.markdown_table())

    print("\n=== FULL JSON ===")
    data = table.to_json()
    print(json.dumps(data, indent=2))

    # Print ringing table too
    print("\n=== RINGING TABLE (non-throttle ringing m/s²) ===")
    variant_names = ["gaussian", "kind3"] + list(SWEEP.keys())
    hdr = "| Circuit | " + " | ".join(f"{v}_ring" for v in variant_names) + " | raw_ring |"
    sep = "| --- |" + " --- |" * (len(variant_names) + 1)
    print(hdr)
    print(sep)
    for cr in table.cases:
        vals = []
        for v in variant_names:
            vs = cr.scores.get(v)
            vals.append(f"{vs.ringing:.2f}" if vs else "N/A")
        raw_ring = next(
            (f"{vs.raw_ring:.2f}" for vs in cr.scores.values() if vs.raw_ring == vs.raw_ring),
            "N/A"
        )
        print(f"| {cr.gp} | " + " | ".join(vals) + f" | {raw_ring} |")

    # Print gap vs raw table
    print("\n=== KNEE GAP VS RAW (knee - raw_knee; closer to 0 is better) ===")
    hdr2 = "| Circuit | " + " | ".join(f"{v}_gap" for v in variant_names) + " |"
    sep2 = "| --- |" + " --- |" * len(variant_names)
    print(hdr2)
    print(sep2)
    for cr in table.cases:
        vals = []
        for v in variant_names:
            vs = cr.scores.get(v)
            vals.append(f"{vs.knee_gap_vs_raw:.2f}" if vs else "N/A")
        print(f"| {cr.gp} | " + " | ".join(vals) + " |")

    # Print ringing_over_ceiling table
    print("\n=== RINGING OVER CEILING (ringing - raw_ring; <=0 is good) ===")
    hdr3 = "| Circuit | " + " | ".join(f"{v}_roc" for v in variant_names) + " |"
    sep3 = "| --- |" + " --- |" * len(variant_names)
    print(hdr3)
    print(sep3)
    for cr in table.cases:
        vals = []
        for v in variant_names:
            vs = cr.scores.get(v)
            vals.append(f"{vs.ringing_over_ceiling:.2f}" if vs else "N/A")
        print(f"| {cr.gp} | " + " | ".join(vals) + " |")

if __name__ == "__main__":
    main()
