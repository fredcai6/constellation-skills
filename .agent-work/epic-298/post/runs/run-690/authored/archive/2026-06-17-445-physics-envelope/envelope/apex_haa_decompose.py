"""HAA vs RBR: WHERE in the corner is the time lost? (#445)

Decompose each corner into entry (v_in), apex (v_apex), exit (v_out) and corner
time. At MATCHED radius bins, compare HAA vs RBR:
  - apex speed deficit  (mid-corner / mechanical+downforce grip)
  - entry speed deficit (braking / corner entry)
  - exit speed deficit  (traction / corner exit)
  - corner time deficit (the lap-time-relevant integral)

This pins the mechanism: is HAA's grip-vs-pace gap a min-speed (apex) problem, a
braking problem, or a traction-out problem?
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NPZ = OUT / "apex_corners.npz"


def main():
    d = np.load(NPZ, allow_pickle=True)
    car = d["car"]
    R = d["R_apex"].astype(float)
    va = d["v_apex"].astype(float) * 3.6
    vi = d["v_in"].astype(float) * 3.6
    vo = d["v_out"].astype(float) * 3.6
    ct = d["corner_dt"].astype(float)
    cds = d["corner_ds"].astype(float)
    invsp = np.where((cds > 0) & (ct > 0), ct / cds, np.nan) * 1000  # ms per m

    RBR = ["VER", "PER"]; HAA = ["MAG", "HUL"]
    edges = [20, 40, 70, 120, 200, 400]
    print("HAA vs RBR corner decomposition at matched radius (RBR - HAA, +=RBR better)")
    print(f"{'R bin':>10} | {'apexΔ':>7} {'entryΔ':>7} {'exitΔ':>7} {'timeΔ%':>7} | n R/H")
    print("           | (km/h faster at apex/entry/exit, % corner-time faster)")
    for lo, hi in zip(edges[:-1], edges[1:]):
        def sel(cars):
            return np.isin(car, cars) & (R >= lo) & (R < hi) & np.isfinite(va)
        mR, mH = sel(RBR), sel(HAA)
        if mR.sum() < 20 or mH.sum() < 20:
            print(f"  {lo:>3}-{hi:<4} | thin")
            continue
        dapex = np.median(va[mR]) - np.median(va[mH])
        dentry = np.median(vi[mR]) - np.median(vi[mH])
        dexit = np.median(vo[mR]) - np.median(vo[mH])
        # corner time: lower inv-speed = faster. % RBR faster:
        iR, iH = np.nanmedian(invsp[mR]), np.nanmedian(invsp[mH])
        dtime = (iH - iR) / iH * 100  # positive = RBR spends less time = faster
        print(f"  {lo:>3}-{hi:<4} | {dapex:+7.1f} {dentry:+7.1f} {dexit:+7.1f} "
              f"{dtime:+7.1f} | {mR.sum()}/{mH.sum()}")

    # Overall (radius-weighted) summary
    print("\nInterpretation key:")
    print("  apexΔ>0  : RBR carries more minimum (mid-corner) speed -> grip that translates")
    print("  entryΔ>0 : RBR brakes later / enters faster")
    print("  exitΔ>0  : RBR gets on power earlier -> better traction")


if __name__ == "__main__":
    main()
