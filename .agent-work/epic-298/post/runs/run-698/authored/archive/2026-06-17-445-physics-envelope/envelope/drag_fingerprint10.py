"""Drag character across ALL 10 constructors — does the channel generalize? (#445).

The fused fingerprint recovered the 4 'interesting' teams' known character. Cheap
generalization test: run the season drag filter for the WHOLE 2023 grid and check the
slippery<->draggy ordering against known straightline-speed rankings (Williams/McLaren
fast in a straight line; Aston/Mercedes draggy). car_data only -> light.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import harvest_envelope as H  # noqa: E402
from drag_prior import collect_team, robust_joint_fit, kalman_1d  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "drag_fingerprint10_fits.json"
CAL = list(range(1, 23))
TEAMS10 = {
    "RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"],
    "MCL": ["NOR", "PIA"], "AMR": ["ALO", "STR"], "ALP": ["GAS", "OCO"],
    "WIL": ["ALB", "SAR"], "ATR": ["TSU", "DEV", "RIC", "LAW"],
    "ALF": ["BOT", "ZHO"], "HAA": ["MAG", "HUL"],
}
ENGINE = {"RBR": "Honda", "ATR": "Honda", "MERC": "Merc", "MCL": "Merc", "AMR": "Merc",
          "WIL": "Merc", "FER": "Ferrari", "ALF": "Ferrari", "HAA": "Ferrari", "ALP": "Renault"}
# known 2023 straightline tier (FIA speed traps): F=fast-straight/slippery, D=draggy
KNOWN = {"WIL": "F (fastest straightline all year)", "MCL": "F (low-drag, esp. 2nd half)",
         "RBR": "F (efficient)", "FER": "~ (powerful, mid-high top speed)",
         "ALF": "~ (Ferrari power)", "HAA": "~ (draggy, midfield)",
         "ALP": "D (Renault, draggy-ish)", "MERC": "D (draggy W14)",
         "AMR": "D (high-DF AMR23, slow straights)", "ATR": "~ (midfield)"}


def per_race_fits():
    if CACHE.exists():
        print(f"loading cached {CACHE.name}")
        return {int(k): v for k, v in json.loads(CACHE.read_text()).items()}
    out = {}
    for rd in CAL:
        try:
            q = H.load_session(2023, rd, "Q")
        except Exception:
            continue
        row = {}
        for team, drvs in TEAMS10.items():
            d = collect_team(q, drvs)
            if len(d) < 40:
                continue
            try:
                f = robust_joint_fit(d)
            except Exception:
                continue
            row[team] = {"CdA_c": f["CdA_c"], "sCc": f["sCc"], "n": f["n"]}
        if row:
            out[rd] = row
            print(f"  round {rd:>2}: {len(row)} teams")
    CACHE.write_text(json.dumps(out, indent=1))
    return out


def main():
    data = per_race_fits()
    rounds = sorted(data)
    # relative CdA per team per race, then season filter
    rel = {t: [] for t in TEAMS10}
    for rd in rounds:
        fits = data[rd]
        present = list(fits)
        if len(present) < 4:
            continue
        fld = np.mean([fits[t]["CdA_c"] for t in present])
        for t in present:
            rel[t].append((rd, fits[t]["CdA_c"] - fld, fits[t]["sCc"]))
    final = {}
    for t in TEAMS10:
        if len(rel[t]) >= 6:
            final[t] = kalman_1d(rel[t], q_proc=0.03, r_floor=0.05)[-1]

    print("\n" + "=" * 70)
    print("SEASON DRAG CHARACTER — all 10 constructors (relative CdA, m²)")
    print("slippery (low drag) -> draggy (high drag); known tier in () ")
    print("=" * 70)
    print(f"{'team':>5} {'engine':>8} {'relCdA':>8} {'±':>6} {'races':>6} | known straightline")
    for t in sorted(final, key=lambda k: final[k][1]):
        rd, m, sd = final[t]
        tag = "LOW-drag" if m < -0.01 else ("HIGH-drag" if m > 0.01 else "mid")
        print(f"{t:>5} {ENGINE[t]:>8} {m:+8.3f} {sd:6.3f} {len(rel[t]):6d} | {tag:>9}  {KNOWN[t]}")
    print("\n(check: do WIL/MCL/RBR land low-drag and AMR/MERC/ALP land high-drag, "
          "matching known 2023 straightline-speed order?)")


if __name__ == "__main__":
    main()
