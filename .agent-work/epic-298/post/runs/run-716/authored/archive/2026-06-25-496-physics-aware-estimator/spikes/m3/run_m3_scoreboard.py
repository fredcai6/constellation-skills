"""M3 spike scoreboard run — G2 filter-rebuild measurement.

Run from the main checkout directory:
    cd C:/Programs/f1Brainz
    py C:/Programs/f1Brainz/.claude/worktrees/agent-aff9de88b4e6d6d6c/scripts/run_m3_scoreboard.py

Outputs:
- Scoreboard table (markdown) to stdout
- Full JSON to stdout
- Synthetic sanity check result
- Jerk-process-variance sweep summary
"""
from __future__ import annotations

import importlib.util
import json
import sys

# Main checkout supplies scoreboard and all existing physics modules.
# filter_m3 is loaded directly from the worktree (does not shadow any existing module).
WT = "C:/Programs/f1Brainz/.claude/worktrees/agent-aff9de88b4e6d6d6c"
MC = "C:/Programs/f1Brainz"
# Insert MC first so existing src.physics.layer2.* resolve from the feat branch.
sys.path.insert(0, WT)
sys.path.insert(0, MC)

# Load filter_m3 directly (lives only in worktree)
spec = importlib.util.spec_from_file_location(
    "filter_m3", f"{WT}/src/physics/layer2/filter_m3.py"
)
filter_m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(filter_m3)

from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS  # noqa: E402

CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [(2023, "Bahrain", "VER"), (2023, "Monaco", "VER"), (2023, "Belgium", "VER")]


# ---------------------------------------------------------------------------
# Step 1: Synthetic sanity check
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 1: Synthetic sanity check (known sharp decel step)")
print("=" * 70)
r = filter_m3.synthetic_sanity_check()
print(f"  True knee:         {r['true_knee_ms2']:.1f} m/s2")
print(f"  Recovered knee:    {r['recovered_knee_ms2']:.2f} m/s2")
print(f"  Recovered plateau: {r['recovered_plateau_ms2']:.2f} m/s2")
print(f"  Error (recov-true):{r['error_ms2']:.2f} m/s2")
print(f"  PASS (|error|<5):  {r['pass']}")


# ---------------------------------------------------------------------------
# Step 2: Jerk-process-variance sweep on Bahrain
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 2: Jerk-process-variance sweep (Bahrain 2023 VER)")
print("         sig_a_brake values, comparing knee vs raw -52.13 m/s2")
print("=" * 70)

sig_a_sweep = [5.0, 10.0, 20.0, 35.0, 50.0, 80.0]

sweep_results = {}
for sig_a in sig_a_sweep:
    name = f"m3_sab{sig_a:.0f}"
    _, vfn = filter_m3.make_variant_m3(
        sig_v=0.15,
        sig_a_brake=sig_a,
        sig_a_other=4.0,
        a_soft_obs_weight=3.0,
        name=name,
    )
    variants = {name: vfn}
    tbl = run_scoreboard([(2023, "Bahrain", "VER")], variants, cache=CACHE)
    if tbl.cases:
        sc = tbl.cases[0].scores[name]
        sweep_results[sig_a] = {
            "knee": sc.knee,
            "ringing": sc.ringing,
            "knee_gap_vs_raw": sc.knee_gap_vs_raw,
            "ringing_over_ceiling": sc.ringing_over_ceiling,
            "ringing_ok": sc.ringing_ok,
        }
        print(
            f"  sig_a_brake={sig_a:5.0f}: knee={sc.knee:7.2f} m/s2  "
            f"gap_vs_raw={sc.knee_gap_vs_raw:+7.2f}  "
            f"ringing={sc.ringing:6.2f}  ring_ok={sc.ringing_ok}"
        )
    else:
        print(f"  sig_a_brake={sig_a:.0f}: SKIPPED (load error)")

# ---------------------------------------------------------------------------
# Step 3: Full scoreboard — m3 + baselines on all 3 circuits
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 3: Full scoreboard (m3 + gaussian + kind3, all 3 circuits)")
print("=" * 70)

_m3_name, variant_m3_fn = filter_m3.make_variant_m3(
    sig_v=0.15,
    sig_a_brake=35.0,
    sig_a_other=4.0,
    a_soft_obs_weight=3.0,
    name="m3",
)

variants = dict(BUILTIN_VARIANTS)
variants["m3"] = variant_m3_fn

table = run_scoreboard(CASES, variants, cache=CACHE)

print("\n-- Markdown table (knee m/s² per variant) --")
print(table.markdown_table())

print("\n-- Full per-circuit per-variant detail --")
for cr in table.cases:
    print(f"\n{cr.gp} {cr.year} {cr.driver}  lap={cr.lap_no}  best={cr.best_s:.3f}s  "
          f"n_brake={cr.n_brake}  n_coast={cr.n_coast}")
    print(f"  {'Variant':<12} {'knee':>8} {'raw_knee':>9} {'gap_vs_raw':>11} "
          f"{'ringing':>9} {'raw_ring':>9} {'ring_gap':>9} {'ring_ok':>8}")
    for name, vs in cr.scores.items():
        print(
            f"  {name:<12} {vs.knee:>8.2f} {vs.raw_knee:>9.2f} {vs.knee_gap_vs_raw:>+11.2f} "
            f"{vs.ringing:>9.2f} {vs.raw_ring:>9.2f} {vs.ringing_over_ceiling:>+9.2f} "
            f"{'YES' if vs.ringing_ok else 'NO':>8}"
        )

print("\n-- JSON --")
print(json.dumps(table.to_json(), indent=2))
