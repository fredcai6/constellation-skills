"""Season-prior Kalman filter for per-car cornering capability (#445, season-prior prong).

PROBLEM. grip_iter fits per-(car,track) downforce B independently. Thin tracks
(Monza: 43-80 nodes/car) pin B weakly. Carry a per-car capability PRIOR forward
race-to-race and UPDATE it with each weekend's data, so thin tracks borrow strength
from the races before them.

THE CONFIG-INVARIANCE PROBLEM (solved explicitly).
Per-track downforce B is wing-config-dependent (high-DF tracks run more wing), so B
is NOT a season-stable state. We filter a config-INVARIANT observable:

    y_c(race)  =  G_c(vref)  -  mean_over_field( G(vref) )                       (1)

where G_c(vref) = A_race + B_c * vref^2 is the car's frontier grip at a fixed high
reference speed vref (downforce-dominated regime), and the field-mean is taken over
the cars present that weekend. The subtraction:
  - cancels the shared mechanical A exactly (A is common that weekend), and
  - removes the common wing-demand LEVEL of the track (every car runs more wing at a
    high-DF track, so the field mean rises; the OFFSET of a car vs the field is what
    reflects its aero platform and drifts slowly with development).
So y_c is a relative-to-field fast-corner grip offset: ~season-stable, jumps on
upgrades. That is what we filter.

OBSERVATION MODEL. Per race: one global mechanical A shared across that weekend's
cars + per-car downforce B (IRLS frontier, copied from grip_iter3.fit_global_keyed).
Then compute y_c via (1). Obs uncertainty from a NODE-BOOTSTRAP: resample each car's
nodes, re-fit the whole weekend, recompute y_c; R_c = bootstrap variance of y_c.
Thin race -> few nodes -> wide R -> prior dominates (the whole point).

PROCESS MODEL. Scalar random walk per car with base process variance q0 (slow
development drift) PLUS an adaptive jump term: when a race's innovation is large
relative to its predicted variance, inflate Q for that step so a real step-change
(upgrade) is absorbed instead of over-smoothed (heavier-tailed / adaptive process
noise). State = the offset y_c; one independent scalar KF per car.

DELIVERABLE TEST. Build the prior across the 13 pre-Monza rounds, then show the
prior-informed Monza posterior is better-determined (tighter, more car/teammate-
consistent) than the Monza-only fresh fit.

ADDITIVE: this file only; the IRLS fitter is COPIED (not imported-and-mutated) so no
shared module changes. Reads cached nodes from season_prior_collect.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "season_prior_nodes.npz"

GSAT = 5.2          # tyre/driver sustained ceiling (grip_iter constant)
VREF = 200.0 / 3.6  # reference speed (m/s) for the config-invariant observable
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC",
        "LEC": "FER", "SAI": "FER", "ALB": "WIL", "SAR": "WIL"}
TEAMMATE = {"VER": "PER", "PER": "VER", "HAM": "RUS", "RUS": "HAM",
            "LEC": "SAI", "SAI": "LEC", "ALB": "SAR", "SAR": "ALB"}
RNG = np.random.default_rng(20230)


# ======================================================================
# COPIED frontier fitter (from grip_iter3.fit_global_keyed) -- one global
# mechanical A across the weekend's cars, per-car downforce B. Verbatim logic,
# vendored here so we touch no shared module.
# ======================================================================
def _wls(X, y, w, ridge=1e-6):
    Xw = X * w[:, None]
    A = X.T @ Xw + ridge * np.eye(X.shape[1])
    return np.linalg.solve(A, Xw.T @ y)


def fit_weekend(clouds, tau=0.92, band=0.4, iters=30):
    """clouds: dict car -> (v, g, w). Returns (A, {car: B})."""
    keys = list(clouds)
    v = np.concatenate([clouds[k][0] for k in keys])
    g = np.concatenate([clouds[k][1] for k in keys])
    w0 = np.concatenate([clouds[k][2] for k in keys])
    kid = np.concatenate([np.full(len(clouds[k][0]), j) for j, k in enumerate(keys)])
    A = 1.6
    B = np.full(len(keys), 0.0015)
    for _ in range(iters):
        Gv = np.minimum(A + B[kid] * v * v, GSAT)
        r = g - Gv
        member = 1.0 / (1.0 + np.exp(-(g - (Gv - band)) / 0.15))
        qw = np.where(r > 0, tau, 1 - tau)
        w = w0 * member * qw
        sel = (g < GSAT - 0.2) & (w > 1e-9)
        if sel.sum() < 2 * len(keys) + 4:
            break
        X = np.zeros((int(sel.sum()), 1 + len(keys)))
        X[:, 0] = 1.0
        vs = v[sel]
        ks = kid[sel]
        for j in range(len(keys)):
            X[ks == j, 1 + j] = vs[ks == j] ** 2
        coef = _wls(X, g[sel], w[sel])
        A = float(np.clip(coef[0], 0.8, 3.2))
        B = np.clip(coef[1:], 1e-4, 6e-3)
    return A, {keys[j]: float(B[j]) for j in range(len(keys))}


def grip_at(A, B, v_ms):
    return min(A + B * v_ms * v_ms, GSAT)


# ======================================================================
# observation: per-race config-invariant offset y_c + bootstrap covariance
# ======================================================================
def race_offsets(clouds, vref=VREF):
    """Frontier fit then y_c = downforce-term(vref) - field_mean(downforce-term).

    Observable is the UNSATURATED downforce contribution g_df = B_c * vref^2 (NOT
    min(A+B v^2, GSAT)). Rationale: at low-DF tracks (Monza) several cars' frontiers
    hit GSAT=5.2 at vref, so the clipped grip G@200 collapses to a single value and
    the offset degenerates (multiple cars read identical). The pure downforce term
    B*vref^2 never saturates and is the genuine config-(in)variant aero axis we want
    to filter; the shared A and the field-mean wing-demand level still cancel in the
    subtraction exactly as designed.
    """
    A, B = fit_weekend(clouds)
    g = {c: B[c] * vref * vref for c in clouds}      # unsaturated downforce term (g)
    fmean = float(np.mean(list(g.values())))
    return {c: g[c] - fmean for c in clouds}, A, B, g, fmean


def race_observation(clouds, n_boot=120, vref=VREF):
    """Point offsets + per-car bootstrap variance of the offset (obs noise R)."""
    y, A, B, g, fmean = race_offsets(clouds, vref)
    cars = list(clouds)
    boot = {c: [] for c in cars}
    for _ in range(n_boot):
        bc = {}
        for c in cars:
            v, gg, w = clouds[c]
            n = len(v)
            idx = RNG.integers(0, n, n)        # resample this car's nodes
            bc[c] = (v[idx], gg[idx], w[idx])
        yb, *_ = race_offsets(bc, vref)
        for c in cars:
            boot[c].append(yb[c])
    R = {c: float(np.var(boot[c], ddof=1)) for c in cars}
    return dict(y=y, R=R, A=A, B=B, G=g, fmean=fmean, n={c: len(clouds[c][0]) for c in cars})


# ======================================================================
# scalar adaptive Kalman filter per car
# ======================================================================
def kalman_filter(obs_seq, q0=2.5e-4, jump_k=9.0, jump_mult=40.0, P0_scale=4.0):
    """Run one scalar KF per car over an ordered list of race observations.

    obs_seq: list (in calendar order) of dicts {y:{car:val}, R:{car:var}, ...}.
    q0       base process variance (slow development drift), in (g)^2 per race.
    jump_k   innovation z^2 threshold above which we treat the step as an UPGRADE
             jump and inflate Q for that update (adaptive heavy-tailed process).
    jump_mult Q multiplier on a flagged jump step.
    P0_scale prior variance at a car's first appearance = P0_scale * its first R.

    Returns dict car -> list of per-race records with prior/posterior mean+var,
    innovation, gain, and a jump flag.
    """
    cars = sorted({c for o in obs_seq for c in o["y"]})
    state = {}     # car -> (mean, var)
    traj = {c: [] for c in cars}
    for ri, o in enumerate(obs_seq):
        for c in cars:
            if c not in o["y"]:
                # car absent this weekend: predict-only (state drifts, var grows)
                if c in state:
                    m, P = state[c]
                    state[c] = (m, P + q0)
                continue
            y = o["y"][c]
            R = max(o["R"][c], 1e-6)
            if c not in state:
                # initialise from first observation, inflated prior
                state[c] = (y, P0_scale * R)
                traj[c].append(dict(round=ri, y=y, R=R,
                                    prior_m=np.nan, prior_P=np.nan,
                                    post_m=y, post_P=P0_scale * R,
                                    innov=np.nan, z2=np.nan, K=np.nan,
                                    jump=False, n=o["n"][c]))
                continue
            m, P = state[c]
            # PREDICT (random walk): base process noise
            m_pred, P_pred = m, P + q0
            innov = y - m_pred
            z2 = innov * innov / (P_pred + R)
            jump = z2 > jump_k
            if jump:
                # adaptive: large innovation => likely real step-change (upgrade).
                # inflate process variance so the filter follows it this step.
                P_pred = P + q0 * jump_mult
                innov = y - m_pred
                z2j = innov * innov / (P_pred + R)
            # UPDATE
            K = P_pred / (P_pred + R)
            m_new = m_pred + K * innov
            P_new = (1 - K) * P_pred
            state[c] = (m_new, P_new)
            traj[c].append(dict(round=ri, y=y, R=R,
                                prior_m=m_pred, prior_P=P_pred,
                                post_m=m_new, post_P=P_new,
                                innov=innov, z2=z2, K=K, jump=jump, n=o["n"][c]))
    return traj, state


# ======================================================================
# data loading from cache
# ======================================================================
def load_clouds():
    d = np.load(CACHE, allow_pickle=True)
    rounds = [str(x) for x in d["rounds"]]
    cars = [str(x) for x in d["cars"]]
    per_round = []
    for r in rounds:
        clouds = {}
        for c in cars:
            key = f"v__{r}__{c}"
            if key in d.files:
                clouds[c] = (d[f"v__{r}__{c}"].astype(float),
                             d[f"g__{r}__{c}"].astype(float),
                             d[f"w__{r}__{c}"].astype(float))
        per_round.append((r, clouds))
    return rounds, cars, per_round
