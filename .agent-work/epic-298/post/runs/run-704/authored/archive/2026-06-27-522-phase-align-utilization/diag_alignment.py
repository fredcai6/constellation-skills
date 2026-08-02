"""Diagnostic: discriminate (a) misregistration vs (b) under-called caps.

Issue #522 — Gate g1-implement.

Runs with:
    py .agent-work/522-phase-align-utilization/diag_alignment.py

from repo root C:/Programs/f1Brainz.

What this does
--------------
1. Load store + Monaco 2023-Q RBR ceiling + VER best-lap ribbon.
2. Compute three speed grids on true ribbon distance:
   - v_ideal        : nominal ideal lap from PhysicsSimulator (already on grid_dist via np.interp)
   - v_real_progress: current approach — real lap resampled by PROGRESS FRACTION
   - v_real_truedist: new approach — real lap resampled by TRUE DISTANCE via np.interp
3. Identify 2 corners: steepest braking knee + fast_corner apex.
4. Compute per-corner speed ratios under BOTH registrations.
5. Produce ≥1 PNG figure.
6. Print per-corner table used in DIAGNOSIS.md.

Verdict logic
-------------
- If true-dist ratios fall to ≤ ~1 → (a) misregistration dominates.
- If true-dist ratios remain > 1 (while apex speed stays physically below real) → (b) under-called caps.
"""
from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")

# Force UTF-8 on Windows stdout so Unicode chars in print() don't crash
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Path setup — make repo root the first import path
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

WORK_DIR = os.path.join(REPO_ROOT, ".agent-work", "522-phase-align-utilization")
CACHE = os.path.join(REPO_ROOT, "data", "telemetry")
STORE_PATH = os.path.join(REPO_ROOT, "data", "physics_estimates.db")
FIGURE_OUT = os.path.join(WORK_DIR, "fig_alignment_monaco_ver.png")

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.physics.layer2.estimate_store import EstimateStore
from src.physics.utilization.characterize import (
    _build_ceiling,
    _resolve_round_idx,
    _load_lap_and_ribbon,
)
from src.physics.physics_simulator import PhysicsSimulator
from src.physics.sim_evaluator import resample_by_progress
from src.physics.session_fit import load_quali_session
from src.physics.utilization.regime_utilization import (
    _build_regime_masks,
    BRAKING_DECEL_THRESHOLD,
    FAST_CORNER_ALAT_THRESHOLD,
    CURVATURE_THRESHOLD,
    U_CLIP_MAX,
)

# ---------------------------------------------------------------------------
# Load store
# ---------------------------------------------------------------------------
print("Loading store ...")
store = EstimateStore(STORE_PATH)
store_df = store.load(year=2023, status="ok")
print(f"  store_df shape: {store_df.shape}")
print(f"  available gp_names: {sorted(store_df['gp_name'].unique())}")
print(f"  available constructors (sample): {sorted(store_df['constructor'].unique())[:10]}")

# ---------------------------------------------------------------------------
# Identify the case: Monaco / VER / Red Bull Racing
# ---------------------------------------------------------------------------
YEAR = 2023
GP_NAME = "Monaco"
DRIVER = "VER"
CONSTRUCTOR = "Red Bull Racing"

# Verify Monaco is in the store
available_gps = set(store_df["gp_name"].unique())
if GP_NAME not in available_gps:
    # Try alternate names
    candidates = [g for g in available_gps if "monaco" in g.lower() or "mon" in g.lower()]
    if candidates:
        GP_NAME = candidates[0]
        print(f"  [fallback] Using GP_NAME={GP_NAME!r}")
    else:
        print(f"ERROR: Monaco not found in store. Available: {sorted(available_gps)}")
        print("Falling back to Bahrain or first available RBR 2023-Q entry ...")
        rbr_rows = store_df[
            (store_df["year"] == YEAR) & (store_df["constructor"] == CONSTRUCTOR)
        ]
        if rbr_rows.empty:
            rbr_rows = store_df[(store_df["year"] == YEAR)]
        GP_NAME = rbr_rows.sort_values("round_idx").iloc[0]["gp_name"]
        print(f"  [fallback] Using GP_NAME={GP_NAME!r}")
        print(f"  NOTE: primary Monaco/VER case not available; results may differ")

print(f"\nCase: year={YEAR}  gp={GP_NAME!r}  driver={DRIVER}  constructor={CONSTRUCTOR!r}")

# ---------------------------------------------------------------------------
# Resolve round_idx and build ceiling
# ---------------------------------------------------------------------------
round_idx = _resolve_round_idx(store_df, YEAR, GP_NAME, CONSTRUCTOR)
print(f"  round_idx = {round_idx}")

if round_idx is None:
    print("ERROR: could not resolve round_idx for this case.")
    sys.exit(1)

print("Building car ceiling ...")
ceiling = _build_ceiling(store_df, YEAR, CONSTRUCTOR, round_idx)
print(f"  ceiling.n_sessions = {ceiling.n_sessions}")
print(f"  ceiling.params = {ceiling.params}")

# ---------------------------------------------------------------------------
# Load best lap + ribbon
# ---------------------------------------------------------------------------
print(f"\nLoading lap + ribbon for {DRIVER} @ {GP_NAME} {YEAR}-Q ...")
full, track_df = _load_lap_and_ribbon(
    YEAR, GP_NAME, DRIVER, CACHE, load_quali_session, session_type="Q"
)
print(f"  best_lap_s      = {full.best_lap_s:.3f} s")
print(f"  best_distance   shape {full.best_distance.shape}  range [{full.best_distance[0]:.1f}, {full.best_distance[-1]:.1f}] m")
print(f"  best_speed_real shape {full.best_speed_real.shape}  range [{full.best_speed_real.min():.1f}, {full.best_speed_real.max():.1f}] m/s")
print(f"  track_df columns: {list(track_df.columns)}  rows: {len(track_df)}")
print(f"  track ribbon distance range: [{track_df['distance_m'].min():.1f}, {track_df['distance_m'].max():.1f}] m")

# ---------------------------------------------------------------------------
# Simulate ideal lap
# ---------------------------------------------------------------------------
print("\nSimulating ideal lap ...")
sim = PhysicsSimulator()
nominal_lap = sim.simulate_lap(track_df, ceiling.params, sample=False)
print(f"  sim distance range: [{nominal_lap.distance_profile.min():.1f}, {nominal_lap.distance_profile.max():.1f}] m")
print(f"  sim speed range:    [{nominal_lap.speed_profile.min():.1f}, {nominal_lap.speed_profile.max():.1f}] m/s")

# ---------------------------------------------------------------------------
# Three registration approaches
# ---------------------------------------------------------------------------
grid_dist = track_df["distance_m"].to_numpy(dtype=float)
grid_curv = track_df["curvature"].to_numpy(dtype=float)

# 1. Ideal lap on grid via true distance (how the production code already does it)
v_ideal = np.interp(grid_dist, nominal_lap.distance_profile, nominal_lap.speed_profile)

# 2. Real lap via PROGRESS FRACTION (current production approach = the suspect)
v_real_progress = resample_by_progress(grid_dist, full.best_distance, full.best_speed_real)

# 3. Real lap via TRUE DISTANCE (the (a) test — direct distance alignment)
v_real_truedist = np.interp(grid_dist, full.best_distance, full.best_speed_real)

print(f"\nSpeed grids on ribbon distance ({len(grid_dist)} points):")
print(f"  v_ideal range:         [{v_ideal.min():.2f}, {v_ideal.max():.2f}] m/s")
print(f"  v_real_progress range: [{v_real_progress.min():.2f}, {v_real_progress.max():.2f}] m/s")
print(f"  v_real_truedist range: [{v_real_truedist.min():.2f}, {v_real_truedist.max():.2f}] m/s")

# Total lap length comparison
real_lap_length = float(full.best_distance[-1])
ribbon_length = float(grid_dist[-1])
print(f"\nLength comparison:")
print(f"  real best lap arc length : {real_lap_length:.1f} m")
print(f"  ribbon arc length        : {ribbon_length:.1f} m")
print(f"  difference               : {ribbon_length - real_lap_length:.1f} m  ({(ribbon_length/real_lap_length - 1)*100:.2f}%)")

# ---------------------------------------------------------------------------
# Point-wise ratios
# ---------------------------------------------------------------------------
safe_ideal = np.where(np.abs(v_ideal) > 1e-6, v_ideal, 1e-6)
ratio_progress = np.clip(v_real_progress / safe_ideal, 0.0, U_CLIP_MAX)
ratio_truedist = np.clip(v_real_truedist / safe_ideal, 0.0, U_CLIP_MAX)

# ---------------------------------------------------------------------------
# Regime masks (use v_real_progress as in production to match regime assignment)
# ---------------------------------------------------------------------------
m_brk, m_slow, m_fast, m_str = _build_regime_masks(
    grid_dist, grid_curv, v_real_progress,
    decel_threshold=BRAKING_DECEL_THRESHOLD,
    alat_threshold=FAST_CORNER_ALAT_THRESHOLD,
    curvature_threshold=CURVATURE_THRESHOLD,
)

print(f"\nRegime point counts (of {len(grid_dist)} total):")
print(f"  braking     : {m_brk.sum()} ({100*m_brk.mean():.1f}%)")
print(f"  slow_corner : {m_slow.sum()} ({100*m_slow.mean():.1f}%)")
print(f"  fast_corner : {m_fast.sum()} ({100*m_fast.mean():.1f}%)")
print(f"  straight    : {m_str.sum()} ({100*m_str.mean():.1f}%)")

# Regime means
def regime_mean_ratio(ratio, mask, label):
    if mask.sum() < 2:
        print(f"  {label}: <2 points (skip)")
        return float("nan")
    pts = ratio[mask]
    raw_mean = float(np.mean(pts))
    clipped_mean = float(np.clip(raw_mean, 0.0, U_CLIP_MAX))
    return clipped_mean

print("\nRegime-mean ratios (PROGRESS registration — current production):")
u_brk_prog   = regime_mean_ratio(ratio_progress, m_brk,  "braking    ")
u_fast_prog  = regime_mean_ratio(ratio_progress, m_fast, "fast_corner")
print(f"  braking     U_progress = {u_brk_prog:.4f}")
print(f"  fast_corner U_progress = {u_fast_prog:.4f}")

print("\nRegime-mean ratios (TRUE DISTANCE registration — (a) test):")
u_brk_true   = regime_mean_ratio(ratio_truedist, m_brk,  "braking    ")
u_fast_true  = regime_mean_ratio(ratio_truedist, m_fast, "fast_corner")
print(f"  braking     U_truedist = {u_brk_true:.4f}")
print(f"  fast_corner U_truedist = {u_fast_true:.4f}")

# ---------------------------------------------------------------------------
# Corner 1: Fast-corner apex — highest a_lat point in fast_corner regime
# ---------------------------------------------------------------------------
print("\n--- Corner 1: Fast-corner apex ---")
abs_kappa = np.abs(grid_curv)
a_lat = v_real_progress**2 * abs_kappa
if m_fast.sum() >= 2:
    fast_indices = np.where(m_fast)[0]
    apex_idx = fast_indices[np.argmax(a_lat[fast_indices])]
    c1_dist = float(grid_dist[apex_idx])
    c1_kappa = float(grid_curv[apex_idx])
    c1_v_ideal = float(v_ideal[apex_idx])
    c1_v_real_prog = float(v_real_progress[apex_idx])
    c1_v_real_true = float(v_real_truedist[apex_idx])
    c1_ratio_prog = float(ratio_progress[apex_idx])
    c1_ratio_true = float(ratio_truedist[apex_idx])
    c1_alat = float(a_lat[apex_idx])
    print(f"  apex at dist        = {c1_dist:.1f} m")
    print(f"  curvature (1/m)     = {c1_kappa:.6f}")
    print(f"  a_lat (m/s²)        = {c1_alat:.2f}")
    print(f"  v_ideal (m/s)       = {c1_v_ideal:.2f}  ({c1_v_ideal*3.6:.1f} km/h)")
    print(f"  v_real_progress(m/s)= {c1_v_real_prog:.2f}  ({c1_v_real_prog*3.6:.1f} km/h)")
    print(f"  v_real_truedist(m/s)= {c1_v_real_true:.2f}  ({c1_v_real_true*3.6:.1f} km/h)")
    print(f"  ratio_progress      = {c1_ratio_prog:.4f}")
    print(f"  ratio_truedist      = {c1_ratio_true:.4f}")
else:
    print("  WARNING: no fast_corner regime points — skip")
    apex_idx = None
    c1_dist = c1_kappa = c1_v_ideal = c1_v_real_prog = c1_v_real_true = float("nan")
    c1_ratio_prog = c1_ratio_true = c1_alat = float("nan")

# ---------------------------------------------------------------------------
# Corner 2: Braking knee — steepest dv/ds point in braking regime
# ---------------------------------------------------------------------------
print("\n--- Corner 2: Braking knee ---")
dv_ds = np.gradient(v_real_progress, grid_dist)
if m_brk.sum() >= 2:
    brk_indices = np.where(m_brk)[0]
    knee_idx = brk_indices[np.argmin(dv_ds[brk_indices])]
    c2_dist = float(grid_dist[knee_idx])
    c2_kappa = float(grid_curv[knee_idx])
    c2_v_ideal = float(v_ideal[knee_idx])
    c2_v_real_prog = float(v_real_progress[knee_idx])
    c2_v_real_true = float(v_real_truedist[knee_idx])
    c2_ratio_prog = float(ratio_progress[knee_idx])
    c2_ratio_true = float(ratio_truedist[knee_idx])
    c2_dvds = float(dv_ds[knee_idx])
    print(f"  knee at dist        = {c2_dist:.1f} m")
    print(f"  curvature (1/m)     = {c2_kappa:.6f}")
    print(f"  dv/ds at knee(1/s)  = {c2_dvds:.4f}")
    print(f"  v_ideal (m/s)       = {c2_v_ideal:.2f}  ({c2_v_ideal*3.6:.1f} km/h)")
    print(f"  v_real_progress(m/s)= {c2_v_real_prog:.2f}  ({c2_v_real_prog*3.6:.1f} km/h)")
    print(f"  v_real_truedist(m/s)= {c2_v_real_true:.2f}  ({c2_v_real_true*3.6:.1f} km/h)")
    print(f"  ratio_progress      = {c2_ratio_prog:.4f}")
    print(f"  ratio_truedist      = {c2_ratio_true:.4f}")
else:
    print("  WARNING: no braking regime points — skip")
    knee_idx = None
    c2_dist = c2_kappa = c2_v_ideal = c2_v_real_prog = c2_v_real_true = float("nan")
    c2_ratio_prog = c2_ratio_true = c2_dvds = float("nan")

# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
THRESHOLD_A = 1.15   # If true-dist ratio falls below this → consistent with (a)
print("\n=== VERDICT ===")
fast_a = c1_ratio_true <= THRESHOLD_A
brk_a  = c2_ratio_true <= THRESHOLD_A
if fast_a and brk_a:
    verdict = "(a) misregistration"
elif not fast_a and not brk_a:
    verdict = "(b) under-called caps"
else:
    # Mixed
    verdict = "(mixed) — likely (a) dominates with residual cap softness"
print(f"  fast_corner true-dist ratio = {c1_ratio_true:.4f}  -> {'consistent with (a)' if fast_a else 'REMAINS HIGH -> (b) signal'}")
print(f"  braking knee true-dist ratio= {c2_ratio_true:.4f}  -> {'consistent with (a)' if brk_a else 'REMAINS HIGH -> (b) signal'}")
print(f"\n  VERDICT: {verdict}")

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
print(f"\nProducing figure → {FIGURE_OUT}")

fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.suptitle(
    f"Alignment Diagnostic — {YEAR} {GP_NAME} Q / {DRIVER} ({CONSTRUCTOR})\n"
    f"Ribbon length {ribbon_length:.0f} m vs real lap {real_lap_length:.0f} m "
    f"(Δ={ribbon_length-real_lap_length:+.0f} m, {(ribbon_length/real_lap_length-1)*100:.1f}%)",
    fontsize=11,
)

ax0, ax1, ax2 = axes

# ---- Panel 0: Speed profiles ----
ax0.plot(grid_dist, v_ideal, "k-",  lw=1.5, label="v_ideal (sim ceiling)")
ax0.plot(grid_dist, v_real_progress, "b--", lw=1.2, label="v_real (progress reg — current)", alpha=0.8)
ax0.plot(grid_dist, v_real_truedist,  "r:",  lw=1.2, label="v_real (true-dist reg — (a) test)", alpha=0.8)
if apex_idx is not None:
    ax0.axvline(c1_dist, color="orange", lw=0.8, ls="--", alpha=0.7)
    ax0.annotate(f"C1 fast apex\n{c1_dist:.0f}m", (c1_dist, c1_v_ideal),
                 xytext=(c1_dist+50, c1_v_ideal+3), fontsize=7, color="orange",
                 arrowprops=dict(arrowstyle="-", color="orange", lw=0.7))
if knee_idx is not None:
    ax0.axvline(c2_dist, color="purple", lw=0.8, ls="--", alpha=0.7)
    ax0.annotate(f"C2 brake knee\n{c2_dist:.0f}m", (c2_dist, c2_v_ideal),
                 xytext=(c2_dist+50, c2_v_ideal-8), fontsize=7, color="purple",
                 arrowprops=dict(arrowstyle="-", color="purple", lw=0.7))
ax0.set_ylabel("Speed (m/s)")
ax0.legend(fontsize=8, loc="upper right")
ax0.set_title("Speed profiles — three registrations")
ax0.grid(True, alpha=0.3)

# ---- Panel 1: Point-wise ratio v_real/v_ideal ----
ax1.plot(grid_dist, ratio_progress, "b-",  lw=1.0, label="ratio_progress (current)", alpha=0.85)
ax1.plot(grid_dist, ratio_truedist, "r--", lw=1.0, label="ratio_truedist (true-dist)", alpha=0.85)
ax1.axhline(1.0, color="k", lw=0.8, ls="-")
ax1.axhline(THRESHOLD_A, color="green", lw=0.6, ls=":", label=f"threshold {THRESHOLD_A}")
if apex_idx is not None:
    ax1.scatter([c1_dist], [c1_ratio_prog], c="blue",  s=50, zorder=5)
    ax1.scatter([c1_dist], [c1_ratio_true], c="red",   s=50, zorder=5,
                label=f"C1: prog={c1_ratio_prog:.2f} true={c1_ratio_true:.2f}")
if knee_idx is not None:
    ax1.scatter([c2_dist], [c2_ratio_prog], c="blue",  marker="^", s=50, zorder=5)
    ax1.scatter([c2_dist], [c2_ratio_true], c="red",   marker="^", s=50, zorder=5,
                label=f"C2: prog={c2_ratio_prog:.2f} true={c2_ratio_true:.2f}")
ax1.set_ylabel("v_real / v_ideal (ratio)")
ax1.set_ylim(0, U_CLIP_MAX + 0.1)
ax1.legend(fontsize=7, loc="upper right")
ax1.set_title("Point-wise utilization ratio (clipped at U_CLIP_MAX=2.0)")
ax1.grid(True, alpha=0.3)

# ---- Panel 2: Curvature + regime shading ----
ax2.plot(grid_dist, np.abs(grid_curv) * 1000, "k-", lw=0.8, label="|κ| ×1000 (1/m)")
ax2.fill_between(grid_dist, 0, 1, where=m_brk,  alpha=0.25, color="purple",  label="braking")
ax2.fill_between(grid_dist, 0, 1, where=m_fast, alpha=0.25, color="orange",  label="fast_corner")
ax2.fill_between(grid_dist, 0, 1, where=m_slow, alpha=0.25, color="cyan",    label="slow_corner")
if apex_idx is not None:
    ax2.axvline(c1_dist, color="orange", lw=0.8, ls="--", alpha=0.7)
if knee_idx is not None:
    ax2.axvline(c2_dist, color="purple", lw=0.8, ls="--", alpha=0.7)
ax2.set_ylabel("|κ| ×1000 (m⁻¹)")
ax2.set_xlabel("True ribbon distance (m)")
ax2.legend(fontsize=7, loc="upper right")
ax2.set_title("Curvature + regime classification (using progress-reg v_real)")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(FIGURE_OUT, dpi=150, bbox_inches="tight")
print(f"  Saved → {FIGURE_OUT}")
plt.close()

# ---------------------------------------------------------------------------
# Summary table for DIAGNOSIS.md
# ---------------------------------------------------------------------------
print("\n=== PER-CORNER TABLE (for DIAGNOSIS.md) ===")
print(f"{'Corner':<20} {'v_ideal (m/s)':<16} {'v_real_prog (m/s)':<20} {'v_real_true (m/s)':<20} {'kappa (1/m)':<14} {'ratio_prog':<13} {'ratio_true':<13}")
print("-"*120)
c1_label = f"C1 fast apex {c1_dist:.0f}m"
c2_label = f"C2 brake knee {c2_dist:.0f}m"
print(f"{c1_label:<20} {c1_v_ideal:<16.3f} {c1_v_real_prog:<20.3f} {c1_v_real_true:<20.3f} {c1_kappa:<14.6f} {c1_ratio_prog:<13.4f} {c1_ratio_true:<13.4f}")
print(f"{c2_label:<20} {c2_v_ideal:<16.3f} {c2_v_real_prog:<20.3f} {c2_v_real_true:<20.3f} {c2_kappa:<14.6f} {c2_ratio_prog:<13.4f} {c2_ratio_true:<13.4f}")
print()
print(f"Regime means:")
print(f"  fast_corner: U_progress={u_fast_prog:.4f}  U_truedist={u_fast_true:.4f}")
print(f"  braking    : U_progress={u_brk_prog:.4f}  U_truedist={u_brk_true:.4f}")
print()
print(f"Lap length delta: real={real_lap_length:.1f}m  ribbon={ribbon_length:.1f}m  Δ={ribbon_length-real_lap_length:+.1f}m ({(ribbon_length/real_lap_length-1)*100:.2f}%)")
print()
print(f"VERDICT: {verdict}")
print("Done.")

# Store results for external use
_results = {
    "year": YEAR,
    "gp_name": GP_NAME,
    "driver": DRIVER,
    "constructor": CONSTRUCTOR,
    "real_lap_length_m": real_lap_length,
    "ribbon_length_m": ribbon_length,
    "c1_fast_apex": {
        "dist_m": c1_dist, "curvature_1pm": c1_kappa, "a_lat_ms2": c1_alat,
        "v_ideal_ms": c1_v_ideal, "v_real_progress_ms": c1_v_real_prog,
        "v_real_truedist_ms": c1_v_real_true,
        "ratio_progress": c1_ratio_prog, "ratio_truedist": c1_ratio_true,
    },
    "c2_braking_knee": {
        "dist_m": c2_dist, "curvature_1pm": c2_kappa, "dvds_1ps": c2_dvds,
        "v_ideal_ms": c2_v_ideal, "v_real_progress_ms": c2_v_real_prog,
        "v_real_truedist_ms": c2_v_real_true,
        "ratio_progress": c2_ratio_prog, "ratio_truedist": c2_ratio_true,
    },
    "regime_means": {
        "fast_corner_U_progress": u_fast_prog, "fast_corner_U_truedist": u_fast_true,
        "braking_U_progress": u_brk_prog, "braking_U_truedist": u_brk_true,
    },
    "verdict": verdict,
    "figure": FIGURE_OUT,
}
