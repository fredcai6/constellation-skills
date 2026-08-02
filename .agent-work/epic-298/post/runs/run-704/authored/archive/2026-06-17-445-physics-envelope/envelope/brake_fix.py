"""Fix the braking (deceleration) measurement (epic #445 substrate).

Straight-line slope over a window assumes constant deceleration -> averages away
the sharp braking bite -> under-reads (~2.85g vs real ~5g). Compare methods on
the RAW speed sensor (native rate, no re-sampling) and pick the one that recovers
physical braking while still rising with speed:
  - linear slope +-2 (current substrate)
  - 3-point central difference (+-1)
  - local QUADRATIC fit (deceleration may curve in-window -> preserves the peak)
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

G = 9.81


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def deriv_linear(t, v, W):
    n = len(v)
    a = np.full(n, np.nan)
    for i in range(n):
        c, d = max(0, i - W), min(n, i + W + 1)
        if d - c >= 3:
            tb = t[c:d] - t[i]
            den = (tb * tb).sum()
            if den > 1e-12:
                a[i] = (tb * (v[c:d] - v[c:d].mean())).sum() / den
    return a


def deriv_quad(t, v, W):
    """Local quadratic fit; derivative at the center node (peak-preserving)."""
    n = len(v)
    a = np.full(n, np.nan)
    for i in range(n):
        c, d = max(0, i - W), min(n, i + W + 1)
        if d - c >= 4:
            x = t[c:d] - t[i]
            A = np.column_stack([np.ones_like(x), x, x * x])
            try:
                coef, *_ = np.linalg.lstsq(A, v[c:d], rcond=None)
                a[i] = coef[1]      # db/dt at x=0
            except Exception:
                pass
    return a


def collect(session, driver, method):
    runs = H.driver_runs(session, driver)
    vv, aa = [], []
    for ls, le in flying_windows(session, driver):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        sel = (run["tc"] >= ls) & (run["tc"] <= le)
        t, v = run["tc"][sel], run["V"][sel]
        o = np.argsort(t)
        t, v = t[o], v[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9])
        t, v = t[keep], v[keep]
        if len(t) < 50:
            continue
        a = method(t, v)
        ok = np.isfinite(a)
        vv.append(v[ok])
        aa.append(a[ok])
    return np.concatenate(vv), np.concatenate(aa)


def brake_curve(v, a):
    edges = np.arange(20, 92, 8)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v >= lo) & (v < hi)
        if b.sum() < 15:
            out.append(np.nan)
            continue
        seg = a[b]
        out.append(-np.percentile(seg[seg < 0], 5) / G if (seg < 0).any() else np.nan)
    return edges, out


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")

    # native speed-sensor sample spacing
    runs = H.driver_runs(session, "VER")
    dts = np.diff(runs[0]["tc"])
    log(f"native speed-sensor dt: median {np.median(dts)*1000:.0f} ms "
        f"({1/np.median(dts):.1f} Hz)")

    methods = {
        "linear +-2 (current)": lambda t, v: deriv_linear(t, v, 2),
        "central +-1": lambda t, v: deriv_linear(t, v, 1),
        "quad +-2": lambda t, v: deriv_quad(t, v, 2),
        "quad +-3": lambda t, v: deriv_quad(t, v, 3),
    }
    edges = np.arange(20, 92, 8)
    mids = 0.5 * (edges[:-1] + edges[1:])
    curves = {}
    for name, m in methods.items():
        v, a = collect(session, "VER", m)
        _, c = brake_curve(v, a)
        curves[name] = c

    print("\n--- strongest braking (g) vs speed, by method ---")
    print(f"{'km/h':>6} | " + " ".join(f"{n:>20}" for n in methods))
    for k, mid in enumerate(mids):
        row = f"{mid*3.6:6.0f} | "
        row += " ".join(
            (f"{curves[n][k]:20.2f}" if np.isfinite(curves[n][k]) else f"{'--':>20}")
            for n in methods
        )
        print(row)
    print("\n(real F1 peak braking ~4-5g; want physical magnitude AND rising with speed)")


if __name__ == "__main__":
    main()
