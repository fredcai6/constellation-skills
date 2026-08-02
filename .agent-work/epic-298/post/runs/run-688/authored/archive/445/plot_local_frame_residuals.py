"""Diagnostic plotter: trajectory-fit residuals in the LOCAL VELOCITY frame.

The StintSmoother uses an ISOTROPIC per-axis kernel (identical Matern SDE in X
and Y, independent).  But the position-measurement error is naturally in the CAR
frame:
  * ALONG-track (parallel to velocity) -- dominated by sample-to-sample
    interpolation of the 4-5 Hz position stream, so it should GROW with speed;
  * CROSS-track (perpendicular) -- the lateral road-position accuracy, roughly
    speed-independent.

This decomposes the fit residual ``r = obs - smooth`` into (along, cross) at
each position sample and plots it, so we can SEE whether the residuals are
isotropic (circular cloud, equal std) or anisotropic (elliptical -> the
isotropic-kernel assumption is being violated and an anisotropic kernel is
warranted).

Reusable:  local_frame_residuals(smoother, tp, Xobs, Yobs)
           plot_local_frame_residuals(smoother, tp, Xobs, Yobs, title, out_path)

Run (VER Monza 2023 Q flying lap, 5/2 vs 7/2):
    py .agent-work/445/plot_local_frame_residuals.py
"""
from __future__ import annotations

import sys
import warnings
import logging
from pathlib import Path

import numpy as np

sys.path.insert(0, "C:/Programs/f1Brainz/.agent-work/445/envelope")
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def local_frame_residuals(smoother, tp, Xobs, Yobs):
    """Decompose position residuals (obs - smoothed) into the local velocity frame.

    Returns (along, cross, speed, s) where:
      along : residual component parallel to velocity (m)
      cross : residual component perpendicular (left-normal) to velocity (m)
      speed : |v| at each sample (m/s)
      s     : cumulative arc length of the smoothed path (m)
    """
    Xs, Ys = smoother.pos_at(tp)
    vx, vy = smoother.vel_at(tp)
    speed = np.hypot(vx, vy)
    safe = np.maximum(speed, 1e-6)
    ex, ey = vx / safe, vy / safe          # along-track unit vector
    nx, ny = -ey, ex                       # cross-track (left-normal) unit vector
    rx, ry = Xobs - Xs, Yobs - Ys          # residual vector
    along = rx * ex + ry * ey
    cross = rx * nx + ry * ny
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(Xs), np.diff(Ys)))])
    return along, cross, speed, s


def _std_ellipse(ax, along, cross, n_std=1.0, **kw):
    """Draw the n-sigma covariance ellipse of the (along, cross) cloud."""
    cov = np.cov(np.vstack([along, cross]))
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    ang = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    w, h = 2 * n_std * np.sqrt(np.maximum(vals, 0))
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((along.mean(), cross.mean()), w, h, angle=ang,
                          fill=False, **kw))


def plot_local_frame_residuals(smoother, tp, Xobs, Yobs, title, out_path):
    along, cross, speed, s = local_frame_residuals(smoother, tp, Xobs, Yobs)
    sa, sc = float(np.std(along)), float(np.std(cross))
    spd_kmh = speed * 3.6

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(
        f"{title}\nLocal-frame residuals  |  std_along={sa:.2f} m  "
        f"std_cross={sc:.2f} m  ratio along/cross={sa / max(sc, 1e-9):.2f}",
        fontsize=12,
    )

    # (a) along-vs-cross scatter (equal aspect) + isotropy circle + std ellipse
    ax = axes[0, 0]
    sc_h = ax.scatter(along, cross, c=spd_kmh, s=12, cmap="viridis", alpha=0.7)
    lim = 1.1 * max(np.abs(along).max(), np.abs(cross).max())
    iso = max(sa, sc)
    th = np.linspace(0, 2 * np.pi, 100)
    ax.plot(iso * np.cos(th), iso * np.sin(th), "r--", lw=1, label=f"isotropy circle r={iso:.2f}")
    _std_ellipse(ax, along, cross, n_std=1.0, edgecolor="k", lw=1.5, label="1σ ellipse")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    ax.axhline(0, color="grey", lw=0.5); ax.axvline(0, color="grey", lw=0.5)
    ax.set_xlabel("along-track residual (m)"); ax.set_ylabel("cross-track residual (m)")
    ax.legend(loc="upper right", fontsize=8); ax.set_title("(a) residual cloud, colour=speed")
    fig.colorbar(sc_h, ax=ax, label="speed (km/h)")

    # (b) along & cross residual vs lap distance
    ax = axes[0, 1]
    ax.plot(s, along, lw=0.8, label="along", color="tab:blue")
    ax.plot(s, cross, lw=0.8, label="cross", color="tab:orange")
    ax.axhline(0, color="grey", lw=0.5)
    ax.set_xlabel("lap distance (m)"); ax.set_ylabel("residual (m)")
    ax.legend(fontsize=8); ax.set_title("(b) residual vs distance")

    # (c) histograms along vs cross
    ax = axes[1, 0]
    bins = np.linspace(-lim, lim, 50)
    ax.hist(along, bins=bins, alpha=0.55, label=f"along (σ={sa:.2f})", color="tab:blue")
    ax.hist(cross, bins=bins, alpha=0.55, label=f"cross (σ={sc:.2f})", color="tab:orange")
    ax.set_xlabel("residual (m)"); ax.set_ylabel("count")
    ax.legend(fontsize=8); ax.set_title("(c) residual distributions")

    # (d) THE isotropy test: binned RMS of |along| and |cross| vs speed
    ax = axes[1, 1]
    edges = np.linspace(spd_kmh.min(), spd_kmh.max(), 9)
    cen, rms_a, rms_c = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (spd_kmh >= lo) & (spd_kmh < hi)
        if m.sum() >= 4:
            cen.append(0.5 * (lo + hi))
            rms_a.append(np.sqrt(np.mean(along[m] ** 2)))
            rms_c.append(np.sqrt(np.mean(cross[m] ** 2)))
    ax.plot(cen, rms_a, "o-", label="along RMS", color="tab:blue")
    ax.plot(cen, rms_c, "s-", label="cross RMS", color="tab:orange")
    ax.set_xlabel("speed (km/h)"); ax.set_ylabel("RMS residual (m)")
    ax.legend(fontsize=8)
    ax.set_title("(d) RMS residual vs speed\n(along grows with speed => anisotropic / interpolation)")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return dict(std_along=sa, std_cross=sc, ratio=sa / max(sc, 1e-9))


def main():
    from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
    from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp
    from src.preprocessing.trajectory.smoother import StintSmoother

    q = load_session(2023, "Italy", "Q")
    num = driver_num(q, "VER")
    laps = q.laps.pick_drivers("VER")
    valid = laps[laps["LapTime"].notna()]
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    t0 = float(fast["LapStartTime"].total_seconds())
    t1 = float(fast["Time"].total_seconds())
    pos_d, spd_d = driver_streams(q, num)
    PAD = 2.0
    mp = (pos_d["t"] >= t0 - PAD) & (pos_d["t"] <= t1 + PAD)
    mc = (spd_d["t"] >= t0 - PAD) & (spd_d["t"] <= t1 + PAD)
    tp, X, Y = pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp]
    tc, V = spd_d["t"][mc], spd_d["V"][mc]
    delta, _ = session_offset([(tp, X, Y, tc, V)])

    out_dir = Path("C:/Programs/f1Brainz/.agent-work/445")
    for order in (3, 4):
        hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=order)
        ss = StintSmoother(hp["ell"], hp["sf"], hp["sig_pos"], hp["delta"], iters=3, order=order)
        ss.fit(tp, X, Y, tc, V)
        # interior only (drop the glitchy out-lap padding)
        interior = (tp >= t0 + 0.3) & (tp <= t1 - 0.3)
        lab = "Matern-5/2" if order == 3 else "Matern-7/2"
        out = out_dir / f"local_resid_monza_ver_order{order}.png"
        r = plot_local_frame_residuals(
            ss, tp[interior], X[interior], Y[interior],
            title=f"VER Monza 2023 Q flying lap — {lab} (ell={hp['ell']:.2f})",
            out_path=out,
        )
        print(f"order={order} {lab}: std_along={r['std_along']:.2f} m  "
              f"std_cross={r['std_cross']:.2f} m  ratio={r['ratio']:.2f}  -> {out.name}")


if __name__ == "__main__":
    main()
