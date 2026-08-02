"""Per-car (driver-isolated) utilization at Suzuka (epic #445).

Each car vs its OWN physics ideal -> removes the car, leaving how well the driver
extracts THEIR car. A slow car maxed out can show high utilization; a fast car
left on the table, low. This is the driver probe the common-reference backtest
could not give.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

G, RHO, MASS = 9.81, 1.2, 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
LEN = 5807
# per-car params (grip A,B,Gsat ; power P ; drag CdA closed/open) + actual quali
CARS = {
    "VER": dict(team="RBR", A=1.90, B=0.00177, Gsat=4.95, P=525e3, cc=1.53, co=0.97, actual=88.88),
    "HAM": dict(team="MERC", A=1.84, B=0.00186, Gsat=5.10, P=529e3, cc=1.55, co=1.09, actual=89.91),
    "ALB": dict(team="WIL", A=1.74, B=0.00192, Gsat=4.84, P=547e3, cc=1.49, co=0.99, actual=90.54),
}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def ideal_time(s, kappa, p):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    A, B, GS, P, cc, co = p["A"], p["B"], p["Gsat"], p["P"], p["cc"], p["co"]

    def Gv(v):
        return min(A + B * v * v, GS)

    def drag(v, k):
        cda = co if (abs(k) < 8e-4 and v > 200 / 3.6) else cc
        return 0.5 * RHO * cda * v * v / MASS
    vg = np.sqrt(GS * G / np.maximum(kappa, 1e-6))
    for _ in range(10):
        vg = np.minimum(np.sqrt(np.array([Gv(x) for x in vg]) * G / np.maximum(kappa, 1e-6)), 100.0)
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G
            tr = np.sqrt(max(Gv(v[i]) ** 2 - al ** 2, 0)) * G
            a = min(tr, P / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)), vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G
            tr = np.sqrt(max(Gv(v[i + 1]) ** 2 - al ** 2, 0)) * G
            a = tr + drag(v[i + 1], kappa[i + 1])
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * a * ds[i], 1.0)), vg[i])
    t = float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))
    return t * LEN / s[-1]


def main():
    d = np.load(OUT / "ribbon_suzuka.npz")
    s, kappa = d["s"], d["kappa"]
    print("\n=== driver-isolated utilization (each vs OWN car ideal), Suzuka ===")
    print(f"{'drv':>4} {'team':>5} {'car ideal':>10} {'actual':>8} {'util(own car)':>14}")
    for drv, p in CARS.items():
        t_id = ideal_time(s, kappa, p)
        u = t_id / p["actual"]
        print(f"{drv:>4} {p['team']:>5} {t_id:9.2f}s {p['actual']:7.2f}s {100*u:13.1f}%")
    print("\n(util = own-car ideal / actual. Differences here are DRIVER (car removed). "
          "Same-reference field util put VER 93.9 / HAM 92.8 / ALB 92.2.)")


if __name__ == "__main__":
    main()
