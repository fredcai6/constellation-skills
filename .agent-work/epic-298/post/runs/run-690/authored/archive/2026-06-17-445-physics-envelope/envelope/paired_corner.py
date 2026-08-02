"""Paired same-corner cornering-capability comparison (epic #445, option 1).

The speed-bin envelope overlapped because corner-to-corner variance dominated.
Pair WITHIN each matched corner: subtract the field mean per corner, so each car's
capability is measured against the same corner the others drove. This cancels
corner difficulty and should resolve the front cars the binned envelope couldn't.

Capability index (field-relative, paired):
  ceiling[car,corner] = high quantile grip over race laps (best ~ approaching capability)
  delta[car,corner]   = ceiling[car,corner] - mean_over_cars ceiling[*,corner]
  capability[car]      = mean_corner delta ; SE = std_corner(delta)/sqrt(n_corner)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER", "NOR": "MCL"}
QCEIL = 0.80
MIN_LAPS = 8   # per (car,corner) to trust a ceiling


def main():
    df = pd.read_csv(OUT / "compound_physics.csv").dropna(subset=["grip"])
    cars = [c for c in df["car"].unique()]

    # ceiling per (car, corner)
    ceil = {}
    for (car, corner), g in df.groupby(["car", "corner"]):
        if len(g) >= MIN_LAPS:
            ceil[(car, corner)] = np.quantile(g["grip"], QCEIL)
    corners = sorted(df["corner"].unique())

    # field mean per corner (only cars with a ceiling there)
    field = {}
    for c in corners:
        vals = [ceil[(car, c)] for car in cars if (car, c) in ceil]
        if len(vals) >= 3:
            field[c] = np.mean(vals)

    # capability index per car (paired, field-relative)
    print("=== paired same-corner capability index (field-relative, g) ===")
    print(f"{'car':>4} {'team':>4} {'cap index':>10} {'SE':>6} {'n_corners':>10}")
    rows = []
    for car in cars:
        deltas = [ceil[(car, c)] - field[c] for c in corners
                  if (car, c) in ceil and c in field]
        if len(deltas) < 4:
            continue
        cap = float(np.mean(deltas))
        se = float(np.std(deltas, ddof=1) / np.sqrt(len(deltas)))
        rows.append((car, cap, se, len(deltas)))
    rows.sort(key=lambda r: -r[1])
    for car, cap, se, n in rows:
        star = "*" if abs(cap) > 2 * se else " "
        print(f"{car:>4} {TEAM.get(car,'?'):>4} {cap:+10.3f} {se:6.3f} {n:10d} {star}")

    # pairwise separation matrix (sigma)
    print("\n=== pairwise separation (sigma of difference) ===")
    capd = {car: (cap, se) for car, cap, se, n in rows}
    order = [r[0] for r in rows]
    print("      " + " ".join(f"{c:>6}" for c in order))
    for a in order:
        line = f"{a:>4}: "
        for b in order:
            if a == b:
                line += f"{'--':>6} "
            else:
                d = capd[a][0] - capd[b][0]
                sed = np.sqrt(capd[a][1] ** 2 + capd[b][1] ** 2)
                line += f"{d/sed:+6.1f} "
        print(line)
    print("\n(|sigma|>2 => resolved. Compare to the binned envelope where bands overlapped.)")

    # also report the per-corner SE source: within-corner ceiling noise
    print("\n(paired SE comes from corner-to-corner consistency of each car's edge;"
          " teammates should land close.)")


if __name__ == "__main__":
    main()
