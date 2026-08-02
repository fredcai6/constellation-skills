"""Is peak power readable at low speed (where drag is negligible)? (#445)

The one untested lever for a CLEAN power axis: read P where ½ρCdA v³ is small, so CdA error can't
leak in. It only works if the car is at PEAK power there. Reconstruct delivered power
P(v) = m·a·v + ½ρ·CdA·v³ (CdA from the joint fit) on full-throttle points, binned by speed. If P(v)
RISES with speed (car torque/traction-limited low, power-limited only high), then peak power is a
HIGH-speed-only observable — exactly where drag co-dominates → the degeneracy is fundamental.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session, MASS  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from drs_joint_fit import fit_drs_joint  # noqa: E402
from air_density import air_density  # noqa: E402

PROBES = [(14, "Italian", ["VER", "PER"]), (21, "Las Vegas", ["VER", "PER"])]


def main():
    for rnd, name, cars in PROBES:
        q = load_session(2023, rnd, "Q")
        rho = air_density(2023, rnd, "Q")
        v, a, op = throttle_av(q, cars)
        res = fit_drs_joint(v, a, op, rho)
        CdA_c, CdA_o, Pfit = res["CdA_c"], res["CdA_o"], res["P"]
        # delivered power per point: closed uses CdA_c, open uses CdA_o
        CdA = np.where(op, CdA_o, CdA_c)
        Pv = MASS * a * v + 0.5 * rho * CdA * v ** 3       # W
        print(f"\n=== {name} (RBR)  joint-fit peak P={Pfit/1e3:.0f} kW, CdA_c={CdA_c:.2f} ===")
        print(f"  {'speed kmh':>10}{'delivered P kW':>16}{'n':>6}")
        for lo in range(100, 340, 30):
            m = (v * 3.6 >= lo) & (v * 3.6 < lo + 30) & (a > -1)
            if m.sum() >= 10:
                print(f"  {lo:>4}-{lo+30:<4}{np.percentile(Pv[m], 90)/1e3:>15.0f}{m.sum():>6}")
        print("  (90th-pct delivered power per speed bin; rising ⇒ not at peak power until high speed)")


if __name__ == "__main__":
    main()
