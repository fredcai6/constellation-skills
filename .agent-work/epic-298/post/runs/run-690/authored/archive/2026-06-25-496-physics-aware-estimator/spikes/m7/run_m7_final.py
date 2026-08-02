"""M7 final measurement: best hyperparams on all 3 circuits."""
import sys
import json
import math
import numpy as np
sys.path.insert(0, ".")

from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS
from src.physics.layer2.m7_tv_filter import make_m7_variant

CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [(2023, "Bahrain", "VER"), (2023, "Monaco", "VER"), (2023, "Belgium", "VER")]

# Best candidates based on debug runs:
#  edge=0, sigma=0.3 looks best for Bahrain (knee -50.04)
#  But Monaco still has roc=+0.88 with edge=0, sigma=0.3
#  We need to check Belgium regression and also try sigma=0.2

# Update make_m7_variant to accept edge_margin parameter
# Need to update the factory function to support sigma/edge sweep
from src.physics.layer2.m7_tv_filter import _tv_denoise_irls, _emit_braking_arc_obs
from src.physics.layer2.scoreboard import _long_accel

def make_m7_full(lam=1.0, nu_proc=4.0, sigma=1.0, edge=0):
    """Full M7 variant with all hyperparams."""
    def variant(inp):
        sm1 = inp.make_smoother(nu_proc=nu_proc)
        sm1.fit(inp.t, inp.x, inp.y, inp.t, inp.v)
        vx, vy = sm1.vel_at(inp.t)
        a_long_tv = _tv_denoise_irls(inp.a_long_raw, lam=lam)
        obs = _emit_braking_arc_obs(inp.t, vx, vy, inp.regime, a_long_tv,
                                    sigma=sigma, edge_margin=edge)
        sm2 = inp.make_smoother(nu_proc=nu_proc)
        sm2.fit(inp.t, inp.x, inp.y, inp.t, inp.v, accel_obs=obs)
        return _long_accel(sm2, inp.t)
    variant.__name__ = f"m7_e{edge}_s{sigma:.2f}"
    return variant

# Primary candidate: edge=0, sigma=0.3 (best Bahrain)
# Secondary: edge=0, sigma=0.5 (compromise)
# Tertiary: edge=0, sigma=0.2 (push harder on Monaco)
variants = dict(BUILTIN_VARIANTS)
variants["m7_e0_s0.20"] = make_m7_full(lam=1.0, sigma=0.20, edge=0)
variants["m7_e0_s0.30"] = make_m7_full(lam=1.0, sigma=0.30, edge=0)
variants["m7_e0_s0.50"] = make_m7_full(lam=1.0, sigma=0.50, edge=0)
variants["m7_e0_s1.00"] = make_m7_full(lam=1.0, sigma=1.00, edge=0)

print("Running final M7 scoreboard (all 3 circuits)...")
table = run_scoreboard(CASES, variants, cache=CACHE)

# Detailed output
print(f"\n{'variant':20s} {'circuit':10s}  {'knee':>8s}  {'knee_gap':>10s}  {'ring':>8s}  {'roc':>8s}  {'ring_ok':>7s}")
print("-" * 80)
for cr in table.cases:
    first_vs = next(iter(cr.scores.values()))
    print(f"{'[RAW]':20s} {cr.gp:10s}  {first_vs.raw_knee:8.3f}  {'---':>10s}  {first_vs.raw_ring:8.3f}  {'---':>8s}  {'---':>7s}")
    for vname, vs in cr.scores.items():
        ok = "OK" if vs.ringing_ok else "RING!"
        print(f"{vname:20s} {cr.gp:10s}  {vs.knee:8.3f}  {vs.knee_gap_vs_raw:+10.3f}  {vs.ringing:8.3f}  {vs.ringing_over_ceiling:+8.3f}  {ok:>7s}")
    print()

# Lambda sweep for completeness (lam matters less, show it)
print("\n--- Lambda sensitivity at best config (edge=0, sigma=0.3, Bahrain only) ---")
lam_variants = {}
for lam in [0.1, 0.5, 1.0, 2.0, 5.0]:
    lam_variants[f"lam{lam:.1f}"] = make_m7_full(lam=lam, sigma=0.30, edge=0)
lam_table = run_scoreboard([(2023, "Bahrain", "VER")], lam_variants, cache=CACHE)
if lam_table.cases:
    cr = lam_table.cases[0]
    for vname, vs in cr.scores.items():
        print(f"  {vname}: knee={vs.knee:.3f} gap={vs.knee_gap_vs_raw:+.3f} roc={vs.ringing_over_ceiling:+.3f}")

print("\nDone.")
