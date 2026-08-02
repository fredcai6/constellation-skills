"""Pointwise capability-envelope harvest with carried uncertainty (epic #445).

First probe of the "usable range / ceiling" idea: for each car, build the
ceiling of capability over CONTINUOUS state space (speed x lateral/longitudinal
demand) -- no regime buckets, no lap boundaries. Every quantity is carried with
its uncertainty, propagated from the Kalman-RTS smoother's state covariance.

Pipeline per driver:
  raw streams -> per-stint windowless smoother -> smoothed (m_s, P_s) at the
  ~4.2 Hz speed-obs nodes -> MC-propagate the [vx,vy,ax,ay] covariance through
  v = |vel|, a_long = (a.v)/|v|, a_lat = (a x v)/|v| -> (mean, sigma) per node.

Ceiling estimator: precision-weighted upper quantile per speed bin, with a
weighted-bootstrap band. Cornering ceiling = high quantile of |a_lat|;
traction ceiling = high quantile of +a_long; braking ceiling = high quantile
of -a_long.

LIGHT: one session, ~5 drivers, HP fit ONCE and reused (HPs are ~global for a
session). Foreground-safe; writes JSON + PNG under this dir.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, "C:/Programs/f1Brainz")

from src.preprocessing.trajectory.calibration import fit_stint_hp, session_offset  # noqa: E402
from src.preprocessing.trajectory.loaders import (  # noqa: E402
    driver_num,
    driver_streams,
    load_session,
    stint_span,
)
from src.preprocessing.trajectory.smoother import StintSmoother  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
YEAR = 2023
GP = "Japan"
SES = "Q"
DRIVERS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}
K_MC = 128
SPEED_LO, SPEED_HI, SPEED_BW = 15.0, 90.0, 3.0  # m/s bins
MIN_OCC = 20
Q_CEIL = 0.92  # upper-quantile level for the ceiling
N_BOOT = 200
RNG = np.random.default_rng(7)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run_intervals(tp, gap_s=18.0):
    """Split a time series into continuous-running intervals by large gaps.

    A garage return / between-runs idle shows as a >gap_s hole in the ~4.2 Hz
    position stream; each continuous block (out-lap -> flying -> in-lap) becomes
    one smoother segment, avoiding the giant Q1-Q3 'stint' and garage bridging.
    """
    if len(tp) < 2:
        return []
    gaps = np.where(np.diff(tp) > gap_s)[0]
    starts = np.concatenate([[0], gaps + 1])
    ends = np.concatenate([gaps, [len(tp) - 1]])
    return [(float(tp[s]), float(tp[e])) for s, e in zip(starts, ends)]


def driver_runs(session, abbr, min_pos=60, min_spd=60, min_meanv=20.0):
    """Continuous on-track running blocks for a driver (quali-safe segmentation)."""
    num = driver_num(session, abbr)
    pos_d, spd_d = driver_streams(session, num)
    runs = []
    # Segment on the SPEED stream: garage idle (V<=0) is filtered out of spd_d,
    # so its gaps mark real on-track runs. The position stream broadcasts a
    # constant non-zero GPS fix in the garage, so it has NO gap there.
    for t0, t1 in run_intervals(spd_d["t"]):
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
        mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < min_pos or mc.sum() < min_spd:
            continue
        if float(np.mean(spd_d["V"][mc])) < min_meanv:
            continue
        runs.append(dict(
            t0=t0, t1=t1,
            tp=pos_d["t"][mp], X=pos_d["X"][mp], Y=pos_d["Y"][mp],
            tc=spd_d["t"][mc], V=spd_d["V"][mc],
        ))
    return runs


def harvest_driver_states(session, abbr, hp, delta):
    """Run the per-run smoother and return propagated (v,a_long,a_lat,sigmas).

    Returns dict of stacked arrays, or None if no usable run.
    """
    runs = driver_runs(session, abbr)
    chunks = []
    for i, r in enumerate(runs):
        try:
            ss = StintSmoother(hp["ell"], hp["sf"], hp["sig_pos"], delta, iters=2)
            ss.fit(r["tp"], r["X"], r["Y"], r["tc"], r["V"])
        except Exception as exc:
            log(f"    {abbr} run {i}: smoother failed ({exc})")
            continue
        chunks.append(geom_kinematics(ss))
    if not chunks:
        return None
    out = {k: np.concatenate([c[k] for c in chunks]) for k in chunks[0]}
    return out


def _propagate_nodes(ss):
    """MC-propagate the smoothed covariance at the speed-obs nodes (kind==1)."""
    mask = ss.kind == 1
    m = ss.m_s[mask]                     # (N,6) residual-frame
    P = ss.P_s[mask]                     # (N,6,6)
    n = m.shape[0]
    vx = m[:, 1] + ss._vtrend_x
    vy = m[:, 4] + ss._vtrend_y
    ax = m[:, 2]
    ay = m[:, 5]
    mu = np.column_stack([vx, vy, ax, ay])         # (N,4)
    sel = np.array([1, 4, 2, 5])
    cov = P[:, sel][:, :, sel]                      # (N,4,4)
    cov = 0.5 * (cov + np.transpose(cov, (0, 2, 1)))
    L = _batched_chol(cov)
    z = RNG.standard_normal((n, K_MC, 4))
    samp = mu[:, None, :] + np.einsum("nij,nkj->nki", L, z)   # (N,K,4)
    sx, sy, sax, say = samp[..., 0], samp[..., 1], samp[..., 2], samp[..., 3]
    v = np.hypot(sx, sy)
    v = np.maximum(v, 1e-3)
    along = (sax * sx + say * sy) / v
    lat = (sax * sy - say * sx) / v                  # signed normal accel
    latm = np.abs(lat)
    return dict(
        v=v.mean(1), v_sd=v.std(1),
        along=along.mean(1), along_sd=along.std(1),
        latm=latm.mean(1), latm_sd=latm.std(1),
    )


def _batched_chol(cov):
    """Cholesky of a stack of small SPD matrices with escalating jitter."""
    n = cov.shape[0]
    eye = np.eye(4)
    jit = 1e-9
    out = np.empty_like(cov)
    done = np.zeros(n, bool)
    for _ in range(8):
        idx = np.where(~done)[0]
        if idx.size == 0:
            break
        try_cov = cov[idx] + jit * eye
        for j, i in enumerate(idx):
            try:
                out[i] = np.linalg.cholesky(try_cov[j])
                done[i] = True
            except np.linalg.LinAlgError:
                pass
        jit *= 10
    out[~done] = 0.0
    return out


def geom_kinematics(ss, W=4):
    """Lateral (v^2 * d theta/ds) and longitudinal (dv/dt) from the WELL-CONSTRAINED
    velocity state, sidestepping the ell-dominated acceleration state.

    a_lat  = v^2 * kappa,  kappa = local weighted slope of heading theta vs arc s.
    a_long = dv/dt        = local weighted slope of measured speed v vs time t.
    Uncertainty carried from the velocity covariance through both regressions.
    """
    mask = ss.kind == 1
    m = ss.m_s[mask]
    P = ss.P_s[mask]
    t = ss.ts[mask]
    vx = m[:, 1] + ss._vtrend_x
    vy = m[:, 4] + ss._vtrend_y
    v = np.maximum(np.hypot(vx, vy), 1e-3)
    svx2 = np.clip(P[:, 1, 1], 0, None)
    svy2 = np.clip(P[:, 4, 4], 0, None)
    cvxy = P[:, 1, 4]
    theta = np.unwrap(np.arctan2(vy, vx))
    sth2 = np.clip((vy**2 * svx2 + vx**2 * svy2 - 2 * vx * vy * cvxy) / v**4, 1e-10, None)
    sv2 = np.clip((vx**2 * svx2 + vy**2 * svy2 + 2 * vx * vy * cvxy) / v**2, 1e-10, None)
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    n = len(v)
    kappa = np.full(n, np.nan)
    skap = np.full(n, np.nan)
    along = np.full(n, np.nan)
    salong = np.full(n, np.nan)
    wth = 1.0 / sth2
    wv = 1.0 / sv2
    for i in range(n):
        a, b = max(0, i - W), min(n, i + W + 1)
        if b - a < 3:
            continue
        ssl, w = s[a:b], wth[a:b]
        wsum = w.sum()
        dsx = ssl - (w * ssl).sum() / wsum
        denom = (w * dsx * dsx).sum()
        if denom > 1e-9:
            th = theta[a:b]
            tbar = (w * th).sum() / wsum
            kappa[i] = (w * dsx * (th - tbar)).sum() / denom
            skap[i] = np.sqrt(1.0 / denom)
        tt, wl = t[a:b], wv[a:b]
        wlsum = wl.sum()
        dtx = tt - (wl * tt).sum() / wlsum
        denomt = (wl * dtx * dtx).sum()
        if denomt > 1e-9:
            vv = v[a:b]
            vbar = (wl * vv).sum() / wlsum
            along[i] = (wl * dtx * (vv - vbar)).sum() / denomt
            salong[i] = np.sqrt(1.0 / denomt)
    latm = np.abs(v**2 * kappa)
    slat = np.sqrt((2 * v * np.abs(kappa)) ** 2 * sv2 + v**4 * skap**2)
    good = (np.isfinite(latm) & np.isfinite(slat)
            & np.isfinite(along) & np.isfinite(salong))
    return dict(
        v=v[good],
        latm=latm[good], latm_sd=np.clip(slat[good], 1e-6, None),
        along=along[good], along_sd=np.clip(salong[good], 1e-6, None),
    )


def _weighted_quantile(vals, w, q):
    """Weighted q-quantile of vals (weights w)."""
    order = np.argsort(vals)
    v = vals[order]
    cw = np.cumsum(w[order])
    cw /= cw[-1]
    return float(np.interp(q, cw, v))


def build_envelope(v, val, sigma):
    """Precision-weighted upper-quantile ceiling per speed bin, with bootstrap band.

    Returns list of dicts: {v_mid, ceil, lo, hi, n}.
    """
    w_all = 1.0 / np.maximum(sigma, 1e-6) ** 2
    edges = np.arange(SPEED_LO, SPEED_HI + SPEED_BW, SPEED_BW)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v >= lo) & (v < hi)
        nb = int(b.sum())
        if nb < MIN_OCC:
            continue
        vb = val[b]
        wb = w_all[b]
        ceil = _weighted_quantile(vb, wb, Q_CEIL)
        boots = np.empty(N_BOOT)
        pw = wb / wb.sum()
        for k in range(N_BOOT):
            samp = RNG.choice(nb, size=nb, replace=True, p=pw)
            boots[k] = _weighted_quantile(vb[samp], wb[samp], Q_CEIL)
        rows.append(dict(
            v_mid=float(0.5 * (lo + hi)),
            ceil=ceil,
            lo=float(np.percentile(boots, 16)),
            hi=float(np.percentile(boots, 84)),
            n=nb,
        ))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    log(f"loading {YEAR} {GP} {SES} ...")
    session = load_session(YEAR, GP, SES)
    log("session loaded")

    # global inter-stream offset from a few drivers' continuous runs
    streams = []
    for abbr in DRIVERS[:3]:
        for r in driver_runs(session, abbr)[:3]:
            streams.append((r["tp"], r["X"], r["Y"], r["tc"], r["V"]))
    delta, ddiag = session_offset(streams)
    log(f"session offset delta={delta:.3f}s (nwin={ddiag['nwin']})")
    if delta <= 0.0:
        delta = 0.09
        log(f"  offset at grid floor -> using nominal delta={delta}")

    # Fixed HP in the geom-stable regime. The acceleration STATE is ell-dominated
    # (sweep: cornering ceiling 135g->2.3g across ell), so we do NOT trust the
    # auto-calibration's railed ell. Lateral/longitudinal are taken from the
    # velocity GEOMETRY (heading-rate, speed-slope), which is ~ell-invariant.
    hp = dict(ell=2.0, sf=100.0, sig_pos=0.3)
    log(f"fixed HP (geom regime): ell={hp['ell']} sf={hp['sf']} sig_pos={hp['sig_pos']}")

    results = {}
    for abbr in DRIVERS:
        log(f"harvesting {abbr} ...")
        h = harvest_driver_states(session, abbr, hp, delta)
        if h is None:
            log(f"  {abbr}: no usable stint")
            continue
        log(f"  {abbr}: {len(h['v'])} nodes  "
            f"(median sigma a_lat={np.median(h['latm_sd']):.2f} m/s^2)")
        env_lat = build_envelope(h["v"], h["latm"], h["latm_sd"])
        env_acc = build_envelope(h["v"], np.maximum(h["along"], 0), h["along_sd"])
        env_brk = build_envelope(h["v"], np.maximum(-h["along"], 0), h["along_sd"])
        results[abbr] = dict(
            team=TEAM[abbr],
            n_nodes=int(len(h["v"])),
            v_max=float(np.percentile(h["v"], 99)),
            cornering=env_lat,
            traction=env_acc,
            braking=env_brk,
        )

    payload = dict(
        year=YEAR, gp=GP, session=SES, delta=delta,
        method="geom_velocity (a_lat=v^2 dtheta/ds, a_long=dv/dt, local W=4)",
        hp={k: float(v) for k, v in hp.items() if isinstance(v, (int, float))},
        q_ceil=Q_CEIL, k_mc=K_MC, drivers=results,
        elapsed_s=round(time.time() - t_start, 1),
    )
    out_json = OUT / "envelope_suzuka2023q.json"
    out_json.write_text(json.dumps(payload, indent=2))
    log(f"wrote {out_json}  (elapsed {payload['elapsed_s']}s)")
    _summary_table(results)
    _plot(results)


def _interp_ceil(env, v_query):
    if not env:
        return None
    vs = np.array([r["v_mid"] for r in env])
    cs = np.array([r["ceil"] for r in env])
    if v_query < vs.min() or v_query > vs.max():
        return None
    return float(np.interp(v_query, vs, cs))


def _summary_table(results):
    log("=== cornering ceiling |a_lat| (m/s^2) at speed slices — uncategorized ===")
    log(f"{'drv':>4} {'team':>5} {'25m/s':>8} {'45m/s':>8} {'70m/s':>8}  (slow->fast)")
    for abbr, r in results.items():
        c25 = _interp_ceil(r["cornering"], 25)
        c45 = _interp_ceil(r["cornering"], 45)
        c70 = _interp_ceil(r["cornering"], 70)
        def f(x):
            return f"{x:8.1f}" if x is not None else f"{'--':>8}"
        log(f"{abbr:>4} {r['team']:>5} {f(c25)} {f(c45)} {f(c70)}")


def _plot(results):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        log(f"plot skipped (matplotlib: {exc})")
        return
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharex=True)
    titles = [("cornering", "|a_lat| ceiling (m/s^2)"),
              ("traction", "+a_long ceiling (m/s^2)"),
              ("braking", "-a_long ceiling (m/s^2)")]
    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))
    for ax, (key, ylab) in zip(axes, titles):
        for (abbr, r), col in zip(results.items(), colors):
            env = r[key]
            if not env:
                continue
            vs = np.array([e["v_mid"] for e in env])
            cs = np.array([e["ceil"] for e in env])
            lo = np.array([e["lo"] for e in env])
            hi = np.array([e["hi"] for e in env])
            ax.plot(vs, cs, "-o", ms=3, color=col, label=f"{abbr} ({r['team']})")
            ax.fill_between(vs, lo, hi, color=col, alpha=0.18)
        ax.set_title(key)
        ax.set_xlabel("speed (m/s)")
        ax.set_ylabel(ylab)
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Capability ceilings — {YEAR} {GP} {SES} (uncertainty-banded, uncategorized)")
    fig.tight_layout()
    png = OUT / "envelope_suzuka2023q.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
