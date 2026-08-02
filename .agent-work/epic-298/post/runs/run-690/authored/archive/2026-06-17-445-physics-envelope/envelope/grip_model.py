"""Grip model: split cornering grip into mechanical + downforce, per car (#445).

Physics: sideways grip a_lat = mu*(g + (k_df/m) v^2) = A + B*v^2, where
  A = mu*g           = MECHANICAL grip (tyres+weight, no wings) [m/s^2]
  B = mu*k_df/m      = DOWNFORCE coefficient (extra grip per speed^2)
Fit A,B to each car's corner-apex (speed, sideways-grip) points. Test that it
holds together: teammates should land together; low-downforce cars (Williams
2023) should show smaller B than Red Bull / Mercedes.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from envelopes_1d import corner_apexes, lap_arrays  # noqa: E402

G = 9.81
DRIVERS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_apexes(session, driver):
    runs = H.driver_runs(session, driver)
    fits = {}
    apex = []
    for ls, le in flying_windows(session, driver):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        la = lap_arrays(ss, run, ls, le)
        if la is None:
            continue
        t, X, Y, v = la
        apex += corner_apexes(t, X, Y, v)
    return np.array(apex)   # columns: apex speed (m/s), sideways grip (m/s^2)


def fit_grip(apex):
    """a_lat = A + B v^2 ; robust-ish via percentile-anchored bins to track the
    CEILING (best apex per speed), not the cloud mean."""
    v, a = apex[:, 0], apex[:, 1]
    # bin and take the upper grip per speed bin (the capability, not the average)
    edges = np.arange(15, 92, 9)
    vb, ab = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (v >= lo) & (v < hi)
        if m.sum() >= 2:
            vb.append(np.mean(v[m]))
            ab.append(np.percentile(a[m], 75))   # upper grip = capability
    vb, ab = np.array(vb), np.array(ab)
    if len(vb) < 3:
        return None
    coef, cov = np.polyfit(vb**2, ab, 1, cov=True)
    B, A = coef
    sB, sA = np.sqrt(np.diag(cov))
    return dict(A=A, B=B, sA=sA, sB=sB, vb=vb, ab=ab)


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    res = {}
    for d in DRIVERS:
        apex = collect_apexes(session, d)
        f = fit_grip(apex)
        if f:
            res[d] = f
            log(f"{d}: {len(apex)} apexes")

    print("\n--- grip model per car: mechanical grip + downforce ---")
    print(f"{'drv':>4} {'team':>5} | {'mech grip(g)':>13} {'aero@250(g)':>12} "
          f"{'total@250(g)':>13}")
    v250 = 250 / 3.6
    for d in DRIVERS:
        if d not in res:
            continue
        f = res[d]
        mech = f["A"] / G
        aero = f["B"] * v250**2 / G
        tot = mech + aero
        smech = f["sA"] / G
        print(f"{d:>4} {TEAM[d]:>5} | {mech:6.2f}±{smech:4.2f}   {aero:11.2f}  "
              f"{tot:12.2f}")
    print("\n(mech grip = grip with no wings; aero@250 = extra grip from downforce "
          "at 250 km/h)")
    print("HOLD-TOGETHER CHECKS: teammates close? Williams less aero than RBR/MERC?")
    _plot(res)


def _plot(res):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {"RBR": "navy", "MERC": "teal", "WIL": "darkorange"}
    vv = np.linspace(60, 320, 50) / 3.6
    for d, f in res.items():
        c = colors[TEAM[d]]
        ax.scatter(f["vb"] * 3.6, f["ab"] / G, color=c, s=20)
        ax.plot(vv * 3.6, (f["A"] + f["B"] * vv**2) / G, color=c,
                label=f"{d} ({TEAM[d]})")
    ax.set_xlabel("corner speed (km/h)")
    ax.set_ylabel("cornering grip (g)")
    ax.set_title("Grip model fit — mechanical + downforce, per car (Suzuka 2023 Q)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    png = OUT / "grip_model_fits.png"
    fig.tight_layout()
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
