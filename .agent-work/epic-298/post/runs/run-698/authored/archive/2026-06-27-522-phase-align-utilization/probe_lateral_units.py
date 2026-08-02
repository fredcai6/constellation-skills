"""Throwaway probe (#522 review): run LateralView.fit directly on VER Monaco 2023-Q
and compare the measured frontier to the stored/pooled A0. Determines whether the
A0~2.64 under-call is a units bug, a measurement under-call, or pooling dilution.

READ-ONLY. No store writes. Run from repo root:
    py .agent-work/522-phase-align-utilization/probe_lateral_units.py
"""
from __future__ import annotations
import os, sys, warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
CACHE = os.path.join(REPO_ROOT, "data", "telemetry")

import numpy as np
from src.physics.layer2.session_lateral import run_lateral_view_on_session

G = 9.81

print("Running LateralView.fit directly on VER Monaco 2023-Q (single car) ...")
res = run_lateral_view_on_session(year=2023, gp="Monaco", drivers=("VER",), cache=CACHE)
r = res.result
print(f"\nDirect single-session (VER-only) measured frontier:")
print(f"  A0 = {r.A0:.4f}   (units per LateralView docstring: g-coefficient mu)")
print(f"  A2 = {r.A2:.6e}")
print(f"  n_samples = {r.n_samples}")
print(f"  raw p99 grip (g-units) = {res.raw_p99_grip_g:.3f} g")
print()
print("Interpretation A -- A0/A2 are g-coefficients (mu); a_lat = (A0 + A2 v^2) * g :")
for v in [20, 40, 60, 63]:
    mu = r.A0 + r.A2 * v * v
    print(f"  v={v:>3}: mu={mu:5.2f}  -> a_lat = {mu*G:6.2f} m/s2 ({mu:.2f}g)")
print()
print("Interpretation B -- A0/A2 are already m/s2 (the consumer's reading) :")
for v in [20, 40, 60, 63]:
    a = r.A0 + r.A2 * v * v   # no rho, no g
    print(f"  v={v:>3}: a_lat = {a:6.2f} m/s2 ({a/G:.2f}g)")
print()
print(f"Stored Monaco session A0 (from earlier DB pull) = 2.626")
print(f"Direct VER-only fit A0 = {r.A0:.3f}  -> {'MATCHES stored ~2.6' if abs(r.A0-2.6)<1.0 else 'DIFFERS from stored'}")
print()
print("CONCLUSION CHECK:")
print(f"  - If direct fit A0 ~ 2.6 AND interpretation A gives physical ~3-5g -> the")
print(f"    MEASUREMENT is correct in g-units; the consumer misreads g-coeff as m/s2 = UNITS BUG.")
