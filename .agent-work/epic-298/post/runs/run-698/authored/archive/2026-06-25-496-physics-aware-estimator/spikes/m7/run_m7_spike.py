"""M7 spike measurement script: TV-denoised raw-speed -> kind=3 anchor.

Usage:
  py scripts/run_m7_spike.py

Reports:
  - Scoreboard table (m7 + gaussian + kind3 baselines) on 3 circuits
  - Lambda sweep table on Bahrain (heaviest case)
  - Full JSON for archiving
"""
import sys
import json
import math

# Add repo root to path
sys.path.insert(0, ".")

from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS
from src.physics.layer2.m7_tv_filter import make_m7_variant

CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [(2023, "Bahrain", "VER"), (2023, "Monaco", "VER"), (2023, "Belgium", "VER")]

# ---------------------------------------------------------------------------
# Main scoreboard: gaussian + kind3 + m7 (lambda=1.0, the primary candidate)
# ---------------------------------------------------------------------------
print("=" * 70)
print("M7 Spike — TV-denoised raw-speed braking-arc anchor")
print("=" * 70)

variants = dict(BUILTIN_VARIANTS)
variants["m7"] = make_m7_variant(lam=1.0, sigma_anchor=1.0)

print("\n--- Running main scoreboard (gaussian + kind3 + m7 lam=1.0) ---")
table = run_scoreboard(CASES, variants, cache=CACHE)
print(table.markdown_table(["gaussian", "kind3", "m7"]))

# Print full details per case
print("\n--- Full detail per case ---")
for cr in table.cases:
    print(f"\n{cr.gp} 2023 {cr.driver}  (lap {cr.lap_no}, {cr.best_s:.2f}s)")
    print(f"  n_brake={cr.n_brake}, n_coast={cr.n_coast}")
    for vname, vs in cr.scores.items():
        knee_str = f"{vs.knee:.2f}" if math.isfinite(vs.knee) else "N/A"
        ring_str = f"{vs.ringing:.2f}" if math.isfinite(vs.ringing) else "N/A"
        gap_str = f"{vs.knee_gap_vs_raw:+.2f}" if math.isfinite(vs.knee_gap_vs_raw) else "N/A"
        roc_str = f"{vs.ringing_over_ceiling:+.2f}" if math.isfinite(vs.ringing_over_ceiling) else "N/A"
        ok = "OK" if vs.ringing_ok else "RING!"
        print(f"  [{vname:10s}] knee={knee_str:7s} ring={ring_str:7s} "
              f"knee_gap={gap_str:7s} roc={roc_str:7s} [{ok}]")
    # print raw reference
    first_vs = next(iter(cr.scores.values()))
    print(f"  [RAW       ] knee={first_vs.raw_knee:.2f}       ring={first_vs.raw_ring:.2f}")

print("\n--- JSON dump ---")
print(json.dumps(table.to_json(), indent=2))

# ---------------------------------------------------------------------------
# Lambda sweep on Bahrain (the hardest case)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Lambda sweep (Bahrain 2023 VER)")
print("=" * 70)

LAM_VALUES = [0.1, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0]
sweep_variants = {}
for lam in LAM_VALUES:
    sweep_variants[f"m7_lam{lam:.1f}"] = make_m7_variant(lam=lam, sigma_anchor=1.0)

# Add baselines for context
sweep_variants["gaussian"] = BUILTIN_VARIANTS["gaussian"]
sweep_variants["kind3"] = BUILTIN_VARIANTS["kind3"]

print("\nRunning lambda sweep on Bahrain only...")
bahrain_table = run_scoreboard([(2023, "Bahrain", "VER")], sweep_variants, cache=CACHE)

if bahrain_table.cases:
    cr = bahrain_table.cases[0]
    print(f"\nBahrain raw_knee={next(iter(cr.scores.values())).raw_knee:.2f}  "
          f"raw_ring={next(iter(cr.scores.values())).raw_ring:.2f}")
    print(f"\n{'variant':20s}  {'knee':>8s}  {'knee_gap':>10s}  {'ring':>8s}  {'roc':>8s}  {'ring_ok':>7s}")
    print("-" * 75)
    for vname, vs in cr.scores.items():
        knee_str = f"{vs.knee:.3f}" if math.isfinite(vs.knee) else "N/A"
        gap_str = f"{vs.knee_gap_vs_raw:+.3f}" if math.isfinite(vs.knee_gap_vs_raw) else "N/A"
        ring_str = f"{vs.ringing:.3f}" if math.isfinite(vs.ringing) else "N/A"
        roc_str = f"{vs.ringing_over_ceiling:+.3f}" if math.isfinite(vs.ringing_over_ceiling) else "N/A"
        ok = "OK" if vs.ringing_ok else "RING!"
        print(f"{vname:20s}  {knee_str:>8s}  {gap_str:>10s}  {ring_str:>8s}  {roc_str:>8s}  {ok:>7s}")

# ---------------------------------------------------------------------------
# Monaco ringing check for each lambda
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Lambda sweep on Monaco (ringing check)")
print("=" * 70)

monaco_table = run_scoreboard([(2023, "Monaco", "VER")], sweep_variants, cache=CACHE)
if monaco_table.cases:
    cr = monaco_table.cases[0]
    print(f"\nMonaco raw_ring={next(iter(cr.scores.values())).raw_ring:.2f}")
    print(f"\n{'variant':20s}  {'ring':>8s}  {'roc':>8s}  {'ring_ok':>7s}")
    print("-" * 45)
    for vname, vs in cr.scores.items():
        ring_str = f"{vs.ringing:.3f}" if math.isfinite(vs.ringing) else "N/A"
        roc_str = f"{vs.ringing_over_ceiling:+.3f}" if math.isfinite(vs.ringing_over_ceiling) else "N/A"
        ok = "OK" if vs.ringing_ok else "RING!"
        print(f"{vname:20s}  {ring_str:>8s}  {roc_str:>8s}  {ok:>7s}")

print("\nDone.")
