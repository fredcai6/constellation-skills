"""Two-track grip model: shared mechanical grip + per-track downforce (#445).

Teams reconfigure per track (wing level, setup), so a slow track is the same
chassis in a DIFFERENT configuration. Model that honestly:
    grip = A + B_track * v^2
  A       = mechanical grip  (shared across tracks; slow corners measure it ~directly,
                              downforce ~0 at 50-80 km/h regardless of wing)
  B_track = downforce        (per track / per configuration)

Suzuka (fast, lower wing) + Monaco (slow, max wing). Monaco's ~47 km/h hairpin
anchors the mechanical end that Suzuka alone could not reach.
CAVEAT: compound allocation differs by track, so A also absorbs some compound
difference (not pure mechanical). Flagged, not hidden.
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

G = 9.81
DRIVERS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}
TRACKS = [("Suzuka", "Japan"), ("Monaco", "Monaco")]
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def binned(apex, lo=15, hi=95, w=9):
    """Upper-grip (capability) per speed bin -> (v, grip) points."""
    if len(apex) == 0:
        return np.empty((0, 2))
    v, a = apex[:, 0], apex[:, 1]
    edges = np.arange(lo, hi, w)
    out = []
    for a0, a1 in zip(edges[:-1], edges[1:]):
        m = (v >= a0) & (v < a1)
        if m.sum() >= 2:
            out.append((np.mean(v[m]), np.percentile(a[m], 75)))
    return np.array(out)


def fit_shared(pts_by_track):
    """grip = A + sum_track B_track v^2 [track]. Shared A, per-track B."""
    tracks = [t for t in pts_by_track if len(pts_by_track[t])]
    rows_v, rows_g, rows_t = [], [], []
    for t in tracks:
        p = pts_by_track[t]
        rows_v.append(p[:, 0])
        rows_g.append(p[:, 1])
        rows_t += [t] * len(p)
    v = np.concatenate(rows_v)
    g = np.concatenate(rows_g)
    rows_t = np.array(rows_t)
    X = np.zeros((len(v), 1 + len(tracks)))
    X[:, 0] = 1.0
    for j, t in enumerate(tracks):
        X[:, 1 + j] = (v**2) * (rows_t == t)
    coef, *_ = np.linalg.lstsq(X, g, rcond=None)
    A = coef[0]
    B = {t: coef[1 + j] for j, t in enumerate(tracks)}
    return A, B, tracks


def main():
    sessions = {}
    for name, gp in TRACKS:
        log(f"loading 2023 {name} Q ...")
        sessions[name] = H.load_session(2023, gp, "Q")

    apex = {d: {} for d in DRIVERS}
    for d in DRIVERS:
        for name, _ in TRACKS:
            try:
                ap = collect_apexes(sessions[name], d)
            except Exception as exc:
                log(f"  {d} {name}: {exc}")
                ap = np.empty((0, 2))
            apex[d][name] = ap
        ns = {t: len(apex[d][t]) for t in apex[d]}
        log(f"{d}: apexes {ns}")

    # corner-speed coverage check (does Monaco anchor the slow end?)
    for name, _ in TRACKS:
        allv = np.concatenate([apex[d][name][:, 0] for d in DRIVERS
                               if len(apex[d][name])]) * 3.6
        log(f"{name}: corner apex speed range {allv.min():.0f}-{allv.max():.0f} km/h")

    print("\n--- shared-mechanical + per-track-downforce fit ---")
    print(f"{'drv':>4} {'team':>5} | {'mech grip(g)':>12} "
          f"{'DF Suzuka@250':>14} {'DF Monaco@150':>14}")
    fits = {}
    for d in DRIVERS:
        pts = {t: binned(apex[d][t]) for t in apex[d]}
        if sum(len(p) for p in pts.values()) < 4:
            continue
        A, B, tracks = fit_shared(pts)
        fits[d] = (A, B, pts)
        mech = A / G
        df_suz = B.get("Suzuka", np.nan) * (250 / 3.6) ** 2 / G
        df_mon = B.get("Monaco", np.nan) * (150 / 3.6) ** 2 / G
        print(f"{d:>4} {TEAM[d]:>5} | {mech:11.2f}  {df_suz:13.2f}  {df_mon:13.2f}")
    print("\n(mech grip now anchored by Monaco slow corners; DF = downforce grip "
          "added at that track's typical fast-corner speed)")
    print("CHECKS: teammates agree on mechanical now? Monaco downforce > Suzuka "
          "(max wing)? Williams mechanical vs others?")
    _plot(fits)


def _plot(fits):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    tcol = {"Suzuka": "navy", "Monaco": "firebrick"}
    vv = np.linspace(40, 320, 60) / 3.6
    for ax, d in zip(axes.flat, fits):
        A, B, pts = fits[d]
        for t, p in pts.items():
            if len(p):
                ax.scatter(p[:, 0] * 3.6, p[:, 1] / G, color=tcol[t], s=25, label=t)
                if t in B:
                    ax.plot(vv * 3.6, (A + B[t] * vv**2) / G, color=tcol[t], lw=1.2)
        ax.axhline(A / G, color="gray", ls="--", lw=0.8)
        ax.set_title(f"{d} ({TEAM[d]}) — mech {A/G:.2f}g")
        ax.set_xlabel("corner speed (km/h)")
        ax.set_ylabel("cornering grip (g)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    for ax in axes.flat[len(fits):]:
        ax.axis("off")
    fig.suptitle("Two-track grip model: shared mechanical (dashed) + per-track downforce")
    fig.tight_layout()
    png = OUT / "grip_two_track.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
