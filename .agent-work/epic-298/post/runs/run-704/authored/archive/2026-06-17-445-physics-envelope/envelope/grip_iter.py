"""Iterative grip-frontier estimation (epic #445).

Attack the grip-fit noise three ways at once:
  (1) FRONTIER not central tendency -- grip capability is the UPPER edge of the
      (v, g) cloud; most corner nodes are sub-limit. Iteratively reweight toward
      the top edge (quantile IRLS) and EM-PEEL: use the current G(v) to score
      each node's friction-circle utilization, keep the grip-limited nodes,
      re-fit, repeat.
  (2) ALL cornering nodes (friction-circle magnitude g=sqrt(a_lat^2+a_long^2),
      the quantity G(v) actually bounds) instead of sparse apexes -> far more
      data, fixes thin-corner tracks.
  (3) SHARED mechanical grip A across constructors (tyre x surface, common on the
      day), per-car downforce B. Frees the real car-difference axis (downforce)
      to separate.

Compare INDEPENDENT (A,B per car) vs SHARED-A (A common, B per car). Does the
per-car downforce B separate consistently and order the same across tracks?
Quali only (fresh tyres at the limit; race adds fuel/wear/deg confounds to grip).
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
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
VMAX = 160.0          # reliable cornering regime (v^2/R noise dominates above)
GSAT = 5.2            # tyre/driver sustained ceiling (common, derived earlier)
TEAMS = {"RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"], "WIL": ["ALB", "SAR"]}
TRACKS = {"Monza": "Italy", "Hungary": "Hungary", "Suzuka": "Japan"}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


# --------------------------------------------------------------------------
# node extractor: friction-circle magnitude at each cornering node of one lap
# --------------------------------------------------------------------------
def emit_nodes(t, X, Y, v, base_w=1.0):
    n = len(v); pts = []
    for i in range(n):
        a, b = max(0, i - 5), min(n, i + 6)
        if b - a < 5:
            continue
        xx, yy = X[a:b], Y[a:b]
        M = np.column_stack([xx, yy, np.ones_like(xx)])
        sol, *_ = np.linalg.lstsq(M, -(xx**2 + yy**2), rcond=None)
        cx, cy = -sol[0] / 2, -sol[1] / 2
        r2 = cx**2 + cy**2 - sol[2]
        if r2 <= 9:
            continue
        R = np.sqrt(r2)
        resid = np.sqrt(np.mean((np.hypot(xx - cx, yy - cy) - R) ** 2))
        q = resid / R
        if q > 0.03 or v[i] * 3.6 > VMAX:
            continue
        alat = v[i] ** 2 / R / G
        if alat < 0.6:
            continue
        c, dd = max(0, i - 1), min(n, i + 2)
        dt = t[dd - 1] - t[c]
        along = (v[dd - 1] - v[c]) / dt / G if dt > 0 else 0.0
        gtot = np.hypot(alat, along)
        w = base_w / (q + 0.005) ** 2           # circle-fit quality -> precision
        pts.append((v[i], gtot, w))
    return pts


# --------------------------------------------------------------------------
# collect cornering nodes: (v m/s, g_tot in g, weight) per constructor, quali
# --------------------------------------------------------------------------
def collect_nodes(session, car):
    runs = H.driver_runs(session, car)
    fits, pts = {}, []
    for ls, le in flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"]); fits[key] = ss
        mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
        t = ss.ts[mask]; o = np.argsort(t); t = t[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
        X, Y = ss.pos_at(t); v = np.interp(t, run["tc"], run["V"])
        pts += emit_nodes(t, X, Y, v, base_w=1.0)
    return pts


# --------------------------------------------------------------------------
# weighted least squares with a tiny ridge
# --------------------------------------------------------------------------
def wls(X, y, w, ridge=1e-6):
    Xw = X * w[:, None]
    A = X.T @ Xw + ridge * np.eye(X.shape[1])
    bvec = Xw.T @ y
    return np.linalg.solve(A, bvec)


def Gmodel(v, A, B):
    return np.minimum(A + B * v * v, GSAT)


# --------------------------------------------------------------------------
# iterative frontier: quantile IRLS + EM peel, INDEPENDENT (A,B) per cloud
# --------------------------------------------------------------------------
def fit_independent(v, g, w0, tau=0.9, band=0.5, iters=15):
    A, B = 1.8, 0.0018
    for _ in range(iters):
        Gv = Gmodel(v, A, B)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))   # soft: near/above frontier
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        uns = g < GSAT - 0.2                                       # linear part only
        sel = uns & (w > 1e-9)
        if sel.sum() < 8:
            break
        X = np.column_stack([np.ones(sel.sum()), v[sel] ** 2])
        A, B = wls(X, g[sel], w[sel])
        A = float(np.clip(A, 0.8, 3.2)); B = float(np.clip(B, 1e-4, 6e-3))
    return A, B


# --------------------------------------------------------------------------
# iterative frontier: SHARED A across teams, per-team B (joint IRLS)
# --------------------------------------------------------------------------
def fit_shared(clouds, tau=0.9, band=0.5, iters=20):
    teams = list(clouds)
    v = np.concatenate([clouds[t][0] for t in teams])
    g = np.concatenate([clouds[t][1] for t in teams])
    w0 = np.concatenate([clouds[t][2] for t in teams])
    tid = np.concatenate([np.full(len(clouds[t][0]), k) for k, t in enumerate(teams)])
    A = 1.8; B = {t: 0.0018 for t in teams}
    for _ in range(iters):
        Bv = np.array([B[teams[k]] for k in tid])
        Gv = np.minimum(A + Bv * v * v, GSAT)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        uns = g < GSAT - 0.2
        sel = uns & (w > 1e-9)
        if sel.sum() < 20:
            break
        # design: shared intercept + per-team v^2 column (block)
        ncol = 1 + len(teams)
        X = np.zeros((sel.sum(), ncol))
        X[:, 0] = 1.0
        vs = v[sel]; ts = tid[sel]
        for j in range(len(teams)):
            X[ts == j, 1 + j] = vs[ts == j] ** 2
        coef = wls(X, g[sel], w[sel])
        A = float(np.clip(coef[0], 0.8, 3.2))
        for j, t in enumerate(teams):
            B[t] = float(np.clip(coef[1 + j], 1e-4, 6e-3))
    return A, B


def run_track(name, gp):
    log(f"==== {name} ({gp}) quali ====")
    q = H.load_session(2023, gp, "Q")
    clouds = {}
    for team, drvs in TEAMS.items():
        pts = []
        for car in drvs:
            try:
                pts += collect_nodes(q, car)
            except Exception as e:
                log(f"  {team}/{car}: {e}")
        if len(pts) < 80:
            log(f"  {team}: thin ({len(pts)} nodes), skip")
            continue
        p = np.array(pts)
        clouds[team] = (p[:, 0], p[:, 1], p[:, 2])
        log(f"  {team}: {len(pts)} cornering nodes")

    # independent fits
    indep = {}
    for t, (v, g, w) in clouds.items():
        A, B = fit_independent(v, g, w)
        indep[t] = (A, B)
    # shared-A fit
    A_sh, B_sh = fit_shared(clouds)
    return dict(clouds=clouds, indep=indep, A_shared=A_sh, B_shared=B_sh)


def fit_global(out, tau=0.92, band=0.4, iters=30):
    """One mechanical-grip A shared across ALL tracks+cars (pool slow corners to
    pin v->0 intercept once), per-(track,team) downforce B on top."""
    keys, vlist, glist, wlist, klist = [], [], [], [], []
    for name, r in out.items():
        for t, (v, g, w) in r["clouds"].items():
            k = len(keys); keys.append((name, t))
            vlist.append(v); glist.append(g); wlist.append(w)
            klist.append(np.full(len(v), k))
    v = np.concatenate(vlist); g = np.concatenate(glist)
    w0 = np.concatenate(wlist); kid = np.concatenate(klist)
    A = 1.6; B = np.full(len(keys), 0.0015)
    for _ in range(iters):
        Gv = np.minimum(A + B[kid] * v * v, GSAT)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        sel = (g < GSAT - 0.2) & (w > 1e-9)
        ncol = 1 + len(keys)
        X = np.zeros((int(sel.sum()), ncol)); X[:, 0] = 1.0
        vs = v[sel]; ks = kid[sel]
        for j in range(len(keys)):
            X[ks == j, 1 + j] = vs[ks == j] ** 2
        coef = wls(X, g[sel], w[sel])
        A = float(np.clip(coef[0], 0.8, 3.2))
        B = np.clip(coef[1:], 1e-4, 6e-3)
    return A, {keys[j]: float(B[j]) for j in range(len(keys))}


def gat(A, B, kmh):
    return min(A + B * (kmh / 3.6) ** 2, GSAT)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, gp in TRACKS.items():
        try:
            out[name] = run_track(name, gp)
        except Exception as e:
            log(f"  {name} FAILED: {e}")

    print("\n" + "=" * 72)
    print("INDEPENDENT (A,B per car)  vs  SHARED-A (A common, B per car)")
    print("G at 120 km/h (g) is the reportable grip; B is the downforce axis.")
    print("=" * 72)
    for name, r in out.items():
        print(f"\n--- {name} ---")
        print(f"{'':>5} | {'INDEP A':>7} {'B':>8} {'G120':>6} || "
              f"{'SHARED A':>8} {'B':>8} {'G120':>6}")
        A_sh, B_sh = r["A_shared"], r["B_shared"]
        for t in r["clouds"]:
            Ai, Bi = r["indep"][t]
            gi = gat(Ai, Bi, 120)
            gs = gat(A_sh, B_sh[t], 120)
            print(f"{t:>5} | {Ai:7.2f} {Bi:8.5f} {gi:6.2f} || "
                  f"{A_sh:8.2f} {B_sh[t]:8.5f} {gs:6.2f}")
        # spreads
        ai = np.array([r["indep"][t][0] for t in r["clouds"]])
        print(f"   indep A spread = {ai.max()-ai.min():.2f} g  "
              f"(should be ~0 if A is really a common tyre property)")

    # cross-track consistency of the per-car DOWNFORCE ordering (shared-A model)
    print("\n" + "=" * 72)
    print("CROSS-TRACK: per-car downforce B rank (shared-A model), 1=most downforce")
    print("consistent ranking down each column = revealed car signal;")
    print("scrambled = still below the floor.")
    print("=" * 72)
    teams = sorted({t for r in out.values() for t in r["clouds"]})
    cols = list(out)
    print(f"{'team':>5} | " + " ".join(f"{c:>9}" for c in cols) + "   | B values (1e-3)")
    for team in teams:
        rankrow, valrow = [], []
        for c in cols:
            B_sh = out[c]["B_shared"]
            if team in B_sh:
                order = sorted(B_sh, key=lambda k: -B_sh[k])
                rankrow.append(f"{order.index(team)+1:>9}")
                valrow.append(f"{B_sh[team]*1e3:.2f}")
            else:
                rankrow.append(f"{'--':>9}"); valrow.append("--")
        print(f"{team:>5} | " + " ".join(rankrow) + "   | " + " ".join(valrow))

    # ---- iteration 2: ONE global mechanical-grip A across all tracks ----
    A_g, B_g = fit_global(out)
    print("\n" + "=" * 72)
    print(f"GLOBAL-A iteration: one mechanical A={A_g:.2f}g across ALL tracks+cars,")
    print("per-(track,car) downforce B on top. B now reads on a common baseline.")
    print("=" * 72)
    print(f"{'team':>5} | " + " ".join(f"{c:>10}" for c in cols) + "   (B 1e-3, rank in track)")
    for team in teams:
        cells = []
        for c in cols:
            present = {(cc, t): B_g[(cc, t)] for (cc, t) in B_g if cc == c}
            key = (c, team)
            if key in B_g:
                order = sorted(present, key=lambda k: -present[k])
                rk = order.index(key) + 1
                cells.append(f"{B_g[key]*1e3:5.2f}(#{rk})")
            else:
                cells.append(f"{'--':>10}")
        print(f"{team:>5} | " + " ".join(f"{c:>10}" for c in cells))
    print(f"\nG at 120 km/h with global A: " +
          ", ".join(f"{c}:{gat(A_g, np.mean([B_g[(c,t)] for (cc,t) in B_g if cc==c]),120):.2f}g"
                    for c in cols))

    _plot(out)


def _plot(out):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    COL = {"RBR": "navy", "MERC": "teal", "FER": "firebrick", "WIL": "darkorange"}
    n = len(out)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5.5), squeeze=False)
    vv = np.linspace(40, VMAX, 60)
    for ax, (name, r) in zip(axes[0], out.items()):
        for t, (v, g, w) in r["clouds"].items():
            ax.scatter(v * 3.6, g, s=4, alpha=0.12, color=COL.get(t, "gray"))
        A_sh, B_sh = r["A_shared"], r["B_shared"]
        for t in r["clouds"]:
            ax.plot(vv, [gat(A_sh, B_sh[t], x) for x in vv], color=COL.get(t, "gray"),
                    lw=2, label=f"{t} (B={B_sh[t]*1e3:.2f})")
        ax.set_title(f"{name}: shared-A={A_sh:.2f}g frontier")
        ax.set_xlabel("speed (km/h)"); ax.set_ylabel("grip g_tot (g)")
        ax.set_ylim(0, GSAT + 0.5); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout()
    png = OUT / "grip_iter.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
