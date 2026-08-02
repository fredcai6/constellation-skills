"""Multi-track grip exploration — is 'mechanical' really compound? (#445)

Throw in more tracks and watch where things align vs disagree. Key confound:
Pirelli brings SOFTEST compounds to SLOWEST tracks, and slow corners are the
only place we measure mechanical grip -> mechanical anchor is always softest
compound. Tests:
  (A) does low-speed (mechanical) grip track COMPOUND (higher at C5 tracks)?
      -> if yes, 'mechanical' is compound, not a car property (user's wariness).
  (B) does DOWNFORCE hold as a CAR property (RBR top across tracks/configs)?
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from grip_model import collect_apexes  # noqa: E402
from multitrack_grip import binned, fit_shared  # noqa: E402

G = 9.81
DRIVERS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}
# (label, FastF1 gp, qualifying-soft compound C-number 2023)
TRACKS = [
    ("Monaco", "Monaco", 5),
    ("Singapore", "Singapore", 5),
    ("Hungary", "Hungary", 5),
    ("Spain", "Spain", 3),
    ("Britain", "Great Britain", 3),
    ("Suzuka", "Japan", 3),
]


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def grip_at(apex_all, ref_kmh, halfwidth=18.0):
    """Median cornering grip near a reference speed (km/h) from pooled apexes."""
    if len(apex_all) == 0:
        return np.nan, 0
    vk = apex_all[:, 0] * 3.6
    m = np.abs(vk - ref_kmh) < halfwidth
    if m.sum() < 3:
        return np.nan, int(m.sum())
    return float(np.median(apex_all[m, 1]) / G), int(m.sum())


def main():
    sessions = {}
    apex = {d: {} for d in DRIVERS}
    for label, gp, _C in TRACKS:
        log(f"loading 2023 {label} Q ...")
        try:
            sessions[label] = H.load_session(2023, gp, "Q")
        except Exception as exc:
            log(f"  load failed: {exc}")
            continue
        for d in DRIVERS:
            try:
                apex[d][label] = collect_apexes(sessions[label], d)
            except Exception:
                apex[d][label] = np.empty((0, 2))

    # (A) per-track LOW-SPEED grip vs compound (pool cars)
    print("\n=== (A) low-speed (mechanical) grip vs compound, per track ===")
    print(f"{'track':>10} {'C#':>3} {'range(km/h)':>12} {'grip@90':>8} {'grip@130':>9} {'grip@230':>9}")
    for label, gp, C in TRACKS:
        if label not in sessions:
            continue
        pooled = np.concatenate([apex[d][label] for d in DRIVERS if len(apex[d].get(label, []))]) \
            if any(len(apex[d].get(label, [])) for d in DRIVERS) else np.empty((0, 2))
        if len(pooled) == 0:
            continue
        vk = pooled[:, 0] * 3.6
        g90 = grip_at(pooled, 90)[0]
        g130 = grip_at(pooled, 130)[0]
        g230 = grip_at(pooled, 230)[0]
        def f(x):
            return f"{x:8.2f}" if np.isfinite(x) else f"{'--':>8}"
        print(f"{label:>10} {C:>3} {vk.min():5.0f}-{vk.max():<6.0f} "
              f"{f(g90)} {f(g130):>9} {f(g230):>9}")
    print("  -> if grip@90 is higher on C5 tracks than C3, 'mechanical' = compound.")

    # (B) shared-mechanical + per-track-downforce per car
    print("\n=== (B) per-car: shared mechanical grip + per-track downforce ===")
    print(f"{'drv':>4} {'team':>5} | {'mech(g)':>8} | downforce grip @230km/h per track")
    tcols = [t for t, _, _ in TRACKS]
    print(f"{'':>4} {'':>5} | {'':>8} | " + " ".join(f"{t[:7]:>8}" for t in tcols))
    df_by_track = {t: {} for t in tcols}
    for d in DRIVERS:
        pts = {t: binned(apex[d].get(t, np.empty((0, 2)))) for t in tcols}
        pts = {t: p for t, p in pts.items() if len(p) >= 2}
        if len(pts) < 2:
            continue
        A, B, tracks = fit_shared(pts)
        vref = (230 / 3.6) ** 2
        cells = []
        for t in tcols:
            if t in B:
                dfg = B[t] * vref / G
                df_by_track[t][d] = dfg
                cells.append(f"{dfg:8.2f}")
            else:
                cells.append(f"{'--':>8}")
        print(f"{d:>4} {TEAM[d]:>5} | {A/G:7.2f}  | " + " ".join(cells))

    # (B) summary: is RBR top on downforce across tracks?
    print("\n  downforce ordering per track (team avg @230km/h):")
    for t in tcols:
        if not df_by_track[t]:
            continue
        teamavg = {}
        for tm in ["RBR", "MERC", "WIL"]:
            vals = [df_by_track[t][d] for d in DRIVERS if TEAM[d] == tm and d in df_by_track[t]]
            if vals:
                teamavg[tm] = np.mean(vals)
        order = sorted(teamavg, key=lambda k: -teamavg[k])
        print(f"    {t:>10}: " + "  ".join(f"{tm} {teamavg[tm]:.2f}" for tm in order))


if __name__ == "__main__":
    main()
