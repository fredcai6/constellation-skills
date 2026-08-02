"""Run M8 scoreboard measurement vs gaussian + kind3 baselines.

Usage:
    cd C:/Programs/f1Brainz/.claude/worktrees/agent-ae3f316be91bb25e3
    py run_m8_scoreboard.py
"""
import sys
import json

# Add main checkout to path (feat/physics-aware-estimator-496 branch has scoreboard)
_MAIN = "C:/Programs/f1Brainz"
if _MAIN not in sys.path:
    sys.path.insert(0, _MAIN)

from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS, CaseInputs
from spike_m8 import variant_m8, variant_m8_diagnostic, build_mean_and_blend

CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [(2023, "Bahrain", "VER"), (2023, "Monaco", "VER"), (2023, "Belgium", "VER")]

print("=== M8 Spike Scoreboard ===")
print(f"Cache: {CACHE}")
print(f"Cases: {CASES}")
print()

variants = dict(BUILTIN_VARIANTS)
variants["m8"] = variant_m8

table = run_scoreboard(CASES, variants, cache=CACHE)

print("=== MARKDOWN TABLE ===")
print(table.markdown_table())

print()
print("=== DETAILED JSON ===")
print(json.dumps(table.to_json(), indent=2))

# Also run diagnostic to count onset fit quality
print()
print("=== ONSET FIT QUALITY DIAGNOSTICS ===")
from src.physics.layer2.scoreboard import run_case, _build_case_inputs
from src.physics.session_fit import load_quali_session

for year, gp, driver in CASES:
    print(f"\n--- {gp} {year} {driver} ---")
    try:
        result = load_quali_session(year, gp, "Q", CACHE)
        session = result[0]
        inp, meta = _build_case_inputs(session, driver)
        _, onset_reports = variant_m8_diagnostic(inp)
        n_clean = sum(1 for r in onset_reports if r.get("quality") == "clean")
        n_poor = sum(1 for r in onset_reports if r.get("quality") == "poor")
        n_failed = sum(1 for r in onset_reports if r.get("quality") == "fit_failed")
        n_skipped = sum(1 for r in onset_reports if r.get("quality", "").startswith("skipped"))
        print(f"  Total onsets detected: {len(onset_reports)}")
        print(f"  Clean fits (RMS < 3 m/s²): {n_clean}")
        print(f"  Poor fits (RMS >= 3 m/s²): {n_poor}")
        print(f"  Failed fits: {n_failed}")
        print(f"  Skipped (short/few samples): {n_skipped}")
        for rep in onset_reports:
            q = rep.get("quality", "?")
            t0 = rep.get("t_onset", "?")
            if "residual_rms" in rep:
                rms = rep["residual_rms"]
                depth = rep.get("params", {}).get("depth", "?")
                k_val = rep.get("params", {}).get("k", "?")
                print(f"    t={t0:.2f}s  q={q}  rms={rms:.2f} m/s²  depth={depth:.2f} m/s²  k={k_val:.1f} /s")
            else:
                reason = rep.get("reason", rep.get("quality", "?"))
                print(f"    t={t0:.2f}s  q={q}  reason={reason}")
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        import traceback
        traceback.print_exc()
