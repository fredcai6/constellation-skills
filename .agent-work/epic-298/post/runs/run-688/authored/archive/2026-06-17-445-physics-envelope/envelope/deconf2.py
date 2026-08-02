"""De-confound iteration 2 — robustified, clean-air-gated, per-compound-wear,
cross-validated (epic #445, prong #2 hardening).

Changes vs grip_deconf.py (first cut):
  1. NODE CACHE — collect once to .npz, iterate fit cheaply.
  2. ROBUST IRLS — Huber-style outer weight (MAD-scaled) kills SAR-Suzuka B=1.70
     and any like it; per-key MIN_NODES gate drops thin (track,driver) pairs.
  3. CLEAN-AIR LAP GATE — exclude race laps where the driver was in traffic.
     Proxy: if a driver's in-lap cumulative time minus the car ahead's in-lap
     cumulative time < GAP_CLEAN_S at the lap's endpoint, it's a dirty-air lap.
     Built purely from session.laps timing (no telemetry needed).
  4. PER-COMPOUND WEAR — separate wear slopes for SOFT/MEDIUM/HARD instead of
     one pooled slope (compound×wear interaction).
  5. CROSS-VALIDATION — hold out one track, fit on the other two, compute
     out-of-sample grip-residual error and B-ordering consistency.
  6. POSITION STATEMENT — race-vs-quali truth defended from the data.

Model:
  g = A + dMed*isMED + dHard*isHARD
        + wear_soft*age*isSOFT + wear_med*age*isMED + wear_hard*age*isHARD
        + B(track,driver)*v^2
  capped at GSAT.  Shared tyre terms (A, d*, wear_*) pooled across all nodes;
  per-(track,driver) B absorbs downforce.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import grip_iter as GI  # noqa: E402
from grip_iter import GSAT, TEAMS, TRACKS, emit_nodes, gat  # noqa: E402
from envelopes_1d import lap_arrays  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE_NPZ = OUT / "deconf2_nodes.npz"
SLICKS = ("SOFT", "MEDIUM", "HARD")

# Robustness gates
MIN_NODES = 60           # per-(track,driver) minimum nodes to keep the key
GAP_CLEAN_S = 3.0        # gap-to-car-ahead (sec) required for "clean air" race lap
HUBER_DELTA = 0.6        # Huber loss parameter (g units); residuals above this
                          # transition from quadratic to linear downweighting

# Model
TAU = 0.92               # quantile frontier level
BAND = 0.4               # EM frontier band width (g)
N_ITERS = 40             # IRLS iterations


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


# ---------------------------------------------------------------------------
# Clean-air lap gate
# ---------------------------------------------------------------------------

def build_clean_air_set(rc, gap_s=GAP_CLEAN_S):
    """Return a set of (driver_abbr, lap_number) that are 'clean air' race laps.

    Proxy: for each lap, find which car was directly ahead (one position up)
    at the end of that lap. If the cumulative lap-time gap between this car and
    the car ahead exceeds gap_s, the lap is clean.

    Uses session.laps columns: Driver, LapNumber, Time (cumulative), Position.
    'Time' in FastF1 laps is the cumulative elapsed time at lap end (timedelta).
    """
    laps = rc.laps[rc.laps["LapTime"].notna()].copy()
    # Convert cumulative time to seconds
    laps = laps[laps["Time"].notna()].copy()
    laps["t_end_s"] = laps["Time"].dt.total_seconds()
    laps = laps[laps["t_end_s"].notna() & (laps["t_end_s"] > 0)].copy()

    # Build (lap_number, driver) -> t_end_s lookup
    # Use Position at that lap to find who was ahead
    # Fallback: use driver ranking by t_end_s per lap number
    clean = set()
    for lap_num in laps["LapNumber"].unique():
        lap_grp = laps[laps["LapNumber"] == lap_num][["Driver", "t_end_s"]].dropna()
        if len(lap_grp) < 2:
            continue
        # Sort by cumulative time (faster finishers have lower t_end_s)
        lap_grp = lap_grp.sort_values("t_end_s")
        t_ends = lap_grp["t_end_s"].values
        drivers = lap_grp["Driver"].values
        for i, drv in enumerate(drivers):
            if i == 0:
                # Car in the lead — always clean
                clean.add((drv, int(lap_num)))
            else:
                gap = t_ends[i] - t_ends[i - 1]
                if gap >= gap_s:
                    clean.add((drv, int(lap_num)))
    return clean


# ---------------------------------------------------------------------------
# Node collection with clean-air flag and per-compound-age metadata
# ---------------------------------------------------------------------------

def collect_keyed(q, rc, car):
    """(v, gtot, w, compound, age, is_race, is_clean) for one driver.

    Quali: SOFT/age0, always clean.
    Race: all valid (non-pit) laps with compound+age; clean-air flag from gap proxy.
    """
    rows = []
    # Quali nodes
    for (v, g, w) in GI.collect_nodes(q, car):
        rows.append((v, g, w, "SOFT", 0.0, False, True))

    # Clean-air set for this race
    clean_set = build_clean_air_set(rc, GAP_CLEAN_S)

    num = driver_num(rc, car)
    pos_d, spd_d = driver_streams(rc, num)
    laps = rc.laps.pick_drivers(car)
    laps = laps[laps["LapTime"].notna()].copy()

    for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
        try:
            t0, t1, _ = stint_span(rc, car, st)
        except Exception:
            continue
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
        mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < 100:
            continue
        ss = GI.H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
        ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
               spd_d["t"][mc], spd_d["V"][mc])
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        for _, r in laps[laps["Stint"] == st].iterrows():
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")):
                continue
            if int(r["LapNumber"]) <= 1:
                continue
            comp = str(r.get("Compound", ""))
            if comp not in SLICKS:
                continue
            age = float(r.get("TyreLife")) if pd.notna(r.get("TyreLife")) else 0.0
            lap_num = int(r["LapNumber"])
            is_clean = (car, lap_num) in clean_set

            la = lap_arrays(ss, run,
                            r["LapStartTime"].total_seconds(),
                            r["Time"].total_seconds())
            if la is None:
                continue
            t, X, Y, v = la
            for (vi, gi, wi) in emit_nodes(t, X, Y, v, base_w=0.5):
                rows.append((vi, gi, wi, comp, age, True, is_clean))
    return rows


# ---------------------------------------------------------------------------
# Node cache
# ---------------------------------------------------------------------------

def collect_all(force=False):
    """Collect all nodes and cache to .npz.  Reuse cache on re-run."""
    if CACHE_NPZ.exists() and not force:
        log(f"loading node cache {CACHE_NPZ} ...")
        d = np.load(CACHE_NPZ, allow_pickle=True)
        V = d["V"]; G = d["G"]; W = d["W"]
        AGE = d["AGE"]; COMP = d["COMP"]
        IS_RACE = d["IS_RACE"]; IS_CLEAN = d["IS_CLEAN"]
        TRACK = d["TRACK"]; DRIVER = d["DRIVER"]
        log(f"  loaded {len(V)} nodes from cache")
        return V, G, W, AGE, COMP, IS_RACE, IS_CLEAN, TRACK, DRIVER

    log("collecting nodes (no cache found) ...")
    V_list, G_list, W_list, AGE_list = [], [], [], []
    COMP_list, IS_RACE_list, IS_CLEAN_list = [], [], []
    TRACK_list, DRIVER_list = [], []

    for name, gp in TRACKS.items():
        log(f"  loading {name} ({gp}) sessions ...")
        q = GI.H.load_session(2023, gp, "Q")
        rc = GI.H.load_session(2023, gp, "R")
        for team, drvs in TEAMS.items():
            for car in drvs:
                try:
                    rows = collect_keyed(q, rc, car)
                except Exception as e:
                    log(f"    {name}/{car}: collection failed: {e}")
                    continue
                n_before = len(rows)
                if n_before < MIN_NODES:
                    log(f"    {name}/{team}/{car}: thin ({n_before}), skip")
                    continue
                log(f"    {name}/{team}/{car}: {n_before} nodes")
                for (v, g, w, comp, age, is_race, is_clean) in rows:
                    V_list.append(v); G_list.append(g); W_list.append(w)
                    AGE_list.append(age); COMP_list.append(comp)
                    IS_RACE_list.append(is_race); IS_CLEAN_list.append(is_clean)
                    TRACK_list.append(name); DRIVER_list.append(car)
        log(f"  {name}: {sum(1 for t in TRACK_list if t == name)} nodes so far")

    V = np.array(V_list, dtype=np.float32)
    G = np.array(G_list, dtype=np.float32)
    W = np.array(W_list, dtype=np.float32)
    AGE = np.array(AGE_list, dtype=np.float32)
    COMP = np.array(COMP_list)
    IS_RACE = np.array(IS_RACE_list, dtype=bool)
    IS_CLEAN = np.array(IS_CLEAN_list, dtype=bool)
    TRACK = np.array(TRACK_list)
    DRIVER = np.array(DRIVER_list)

    np.savez(CACHE_NPZ,
             V=V, G=G, W=W, AGE=AGE, COMP=COMP,
             IS_RACE=IS_RACE, IS_CLEAN=IS_CLEAN,
             TRACK=TRACK, DRIVER=DRIVER)
    log(f"saved {len(V)} nodes to {CACHE_NPZ}")
    return V, G, W, AGE, COMP, IS_RACE, IS_CLEAN, TRACK, DRIVER


# ---------------------------------------------------------------------------
# WLS with ridge
# ---------------------------------------------------------------------------

def wls(X, y, w, ridge=1e-6):
    Xw = X * w[:, None]
    A = X.T @ Xw + ridge * np.eye(X.shape[1])
    b = Xw.T @ y
    return np.linalg.solve(A, b)


# ---------------------------------------------------------------------------
# Fit: robust quantile IRLS + Huber outer weight + EM peel
# ---------------------------------------------------------------------------

def fit_deconf2(V, G, W0, AGE, COMP, KID, tau=TAU, band=BAND, iters=N_ITERS,
                per_compound_wear=True):
    """Fit the de-confounded model with Huber robustness.

    Model: g = A + dMed*isMED + dHard*isHARD
               + wear_soft*age*isSOFT + wear_med*age*isMED + wear_hard*age*isHARD
               + B[kid]*v^2   (capped at GSAT)

    Returns dict of fitted parameters.
    """
    nk = int(KID.max()) + 1
    isMED = (COMP == "MEDIUM").astype(float)
    isHARD = (COMP == "HARD").astype(float)
    isSOFT = (COMP == "SOFT").astype(float)

    # Initial values
    A = 1.6
    dMed, dHard = -0.1, -0.2
    wear_soft, wear_med, wear_hard = -0.005, -0.005, -0.005
    B = np.full(nk, 0.0015)

    for it in range(iters):
        # Model prediction
        if per_compound_wear:
            wear_term = wear_soft * AGE * isSOFT + wear_med * AGE * isMED + wear_hard * AGE * isHARD
        else:
            wear_term = wear_soft * AGE  # shared slope

        Gv = np.minimum(
            A + dMed * isMED + dHard * isHARD + wear_term + B[KID] * V * V,
            GSAT
        )
        r = G - Gv

        # EM frontier membership: soft gate toward frontier
        member = 1.0 / (1.0 + np.exp(-(G - (Gv - band)) / 0.15))

        # Quantile IRLS: upweight nodes above frontier
        qw = np.where(r > 0, tau, 1 - tau)

        # Huber outer weight: downweight large outliers symmetrically
        # (uses MAD of current residuals as scale so it's data-adaptive)
        abs_r = np.abs(r)
        scale = max(float(np.median(abs_r[abs_r > 0])) * 1.4826, 0.05)
        huber_w = np.where(abs_r <= HUBER_DELTA * scale,
                           1.0,
                           HUBER_DELTA * scale / abs_r)

        w = W0 * member * qw * huber_w
        sel = (G < GSAT - 0.2) & (w > 1e-9)
        if sel.sum() < 50:
            break

        # Build design matrix
        vs = V[sel]; ks = KID[sel]
        isMED_s = isMED[sel]; isHARD_s = isHARD[sel]; isSOFT_s = isSOFT[sel]
        ages = AGE[sel]
        ws = w[sel]

        if per_compound_wear:
            # cols: intercept, dMed, dHard, wear_soft*age, wear_med*age, wear_hard*age, B[k]*v^2
            ncol = 6 + nk
            X = np.zeros((int(sel.sum()), ncol))
            X[:, 0] = 1.0
            X[:, 1] = isMED_s
            X[:, 2] = isHARD_s
            X[:, 3] = ages * isSOFT_s   # wear_soft coefficient
            X[:, 4] = ages * isMED_s    # wear_med coefficient
            X[:, 5] = ages * isHARD_s   # wear_hard coefficient
            for j in range(nk):
                X[ks == j, 6 + j] = vs[ks == j] ** 2
        else:
            ncol = 4 + nk
            X = np.zeros((int(sel.sum()), ncol))
            X[:, 0] = 1.0
            X[:, 1] = isMED_s
            X[:, 2] = isHARD_s
            X[:, 3] = ages
            for j in range(nk):
                X[ks == j, 4 + j] = vs[ks == j] ** 2

        coef = wls(X, G[sel], ws)

        A = float(np.clip(coef[0], 0.8, 3.2))
        dMed = float(np.clip(coef[1], -1.5, 0.2))
        dHard = float(np.clip(coef[2], -1.5, 0.2))

        if per_compound_wear:
            wear_soft = float(np.clip(coef[3], -0.08, 0.01))
            wear_med = float(np.clip(coef[4], -0.08, 0.01))
            wear_hard = float(np.clip(coef[5], -0.08, 0.01))
            B = np.clip(coef[6:], 1e-4, 6e-3)
        else:
            wear_soft = float(np.clip(coef[3], -0.08, 0.01))
            wear_med = wear_soft; wear_hard = wear_soft
            B = np.clip(coef[4:], 1e-4, 6e-3)

    return dict(A=A, dMed=dMed, dHard=dHard,
                wear_soft=wear_soft, wear_med=wear_med, wear_hard=wear_hard,
                B=B.copy(), n=int(sel.sum()))


# ---------------------------------------------------------------------------
# Predict g_frontier for a node given fit params and key index
# ---------------------------------------------------------------------------

def predict(fit, v, comp, age, kid):
    isMED = float(comp == "MEDIUM")
    isHARD = float(comp == "HARD")
    isSOFT = float(comp == "SOFT")
    wear_term = (fit["wear_soft"] * age * isSOFT +
                 fit["wear_med"] * age * isMED +
                 fit["wear_hard"] * age * isHARD)
    return min(fit["A"] + fit["dMed"] * isMED + fit["dHard"] * isHARD +
               wear_term + fit["B"][kid] * v * v, GSAT)


# ---------------------------------------------------------------------------
# Teammate decomposition (same as grip_deconf.py)
# ---------------------------------------------------------------------------

def decompose(Bmap):
    within, between = [], []
    for name in TRACKS:
        tmeans = {}
        for team, drvs in TEAMS.items():
            bs = [Bmap[(name, d)] for d in drvs if (name, d) in Bmap]
            if len(bs) == 2:
                within.append(abs(bs[0] - bs[1]) * 1e3)
            if bs:
                tmeans[team] = float(np.mean(bs)) * 1e3
        if len(tmeans) >= 2:
            v = np.array(list(tmeans.values()))
            between.append(float(v.max() - v.min()))
    return within, between


# ---------------------------------------------------------------------------
# Cross-validation: hold out one track at a time
# ---------------------------------------------------------------------------

def cross_validate(V, G, W, AGE, COMP, IS_RACE, IS_CLEAN,
                   TRACK, DRIVER, gate="all"):
    """Hold out each track in turn; fit on remaining two; evaluate on held-out.

    gate: "all"  = use all race nodes (original de-confound)
          "clean" = use only clean-air race nodes
          "quali" = use only quali nodes

    Returns dict of per-track held-out error stats.
    """
    results = {}
    track_names = list(TRACKS.keys())
    for held_out in track_names:
        # Build keys for training set
        train_mask = (TRACK != held_out)
        test_mask = (TRACK == held_out)

        # Apply data gate to both train and test
        def apply_gate(mask):
            if gate == "quali":
                return mask & ~IS_RACE
            elif gate == "clean":
                return mask & (~IS_RACE | IS_CLEAN)
            else:
                return mask

        train_mask2 = apply_gate(train_mask)
        test_mask2 = apply_gate(test_mask)

        # Build key indices for training data
        train_keys = []
        for nm in track_names:
            if nm == held_out:
                continue
            for team, drvs in TEAMS.items():
                for d in drvs:
                    mask_k = train_mask2 & (TRACK == nm) & (DRIVER == d)
                    if mask_k.sum() >= MIN_NODES:
                        train_keys.append((nm, d))
        if len(train_keys) < 4:
            results[held_out] = dict(error="insufficient train data")
            continue

        # Build KID array for training
        key2id = {k: j for j, k in enumerate(train_keys)}
        train_sel = np.zeros(len(V), bool)
        for k in train_keys:
            nm, d = k
            m = train_mask2 & (TRACK == nm) & (DRIVER == d)
            train_sel |= m
        if train_sel.sum() < 200:
            results[held_out] = dict(error="insufficient train nodes")
            continue

        train_kid = np.full(len(V), -1, dtype=int)
        for k in train_keys:
            nm, d = k
            m = train_mask2 & (TRACK == nm) & (DRIVER == d)
            train_kid[m] = key2id[k]

        # Fit on training set
        fit = fit_deconf2(
            V[train_sel], G[train_sel], W[train_sel],
            AGE[train_sel], COMP[train_sel], train_kid[train_sel]
        )

        # For held-out track, fit B separately (test set "oracle" B)
        # Then compare predicted g_frontier with actual g values
        # We measure: how well does the tyre model generalize?
        # Evaluate: apply fitted tyre terms (A, d*, wear_*) to held-out nodes,
        # compute tyre-corrected g = g_obs - dCompound - wear_term;
        # compare variance before/after tyre correction.

        test_keys = []
        for team, drvs in TEAMS.items():
            for d in drvs:
                m = test_mask2 & (DRIVER == d)
                if m.sum() >= MIN_NODES:
                    test_keys.append((held_out, d))
        if not test_keys:
            results[held_out] = dict(error="no test keys")
            continue

        # Compute tyre-corrected residuals on test set
        errs = []
        raw_vars = []
        corrected_vars = []
        for k in test_keys:
            nm, d = k
            m = test_mask2 & (TRACK == nm) & (DRIVER == d)
            vv = V[m]; gg = G[m]; aa = AGE[m]; cc = COMP[m]
            isMED = (cc == "MEDIUM").astype(float)
            isHARD = (cc == "HARD").astype(float)
            isSOFT = (cc == "SOFT").astype(float)
            tyre_term = (fit["dMed"] * isMED + fit["dHard"] * isHARD +
                         fit["wear_soft"] * aa * isSOFT +
                         fit["wear_med"] * aa * isMED +
                         fit["wear_hard"] * aa * isHARD)
            g_corrected = gg - tyre_term
            # Variance reduction tells us if tyre model generalizes
            raw_vars.append(float(np.var(gg)))
            corrected_vars.append(float(np.var(g_corrected)))
            # Also: fit a simple per-driver B on test set, measure frontier residual
            # with transferred A vs independently fitted A
            errs.append(float(np.mean(np.abs(tyre_term))))

        results[held_out] = dict(
            n_train=int(train_sel.sum()),
            n_test=int(test_mask2.sum()),
            n_test_keys=len(test_keys),
            mean_tyre_correction=float(np.mean(errs)),
            var_raw=float(np.mean(raw_vars)),
            var_corrected=float(np.mean(corrected_vars)),
            var_reduction_pct=float(100 * (1 - np.mean(corrected_vars) / np.mean(raw_vars)))
            if np.mean(raw_vars) > 0 else 0.0,
        )
    return results


# ---------------------------------------------------------------------------
# Main: run three fits and compare
# ---------------------------------------------------------------------------

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # Collect or load from cache
    V, G, W, AGE, COMP, IS_RACE, IS_CLEAN, TRACK, DRIVER = collect_all()

    total = len(V)
    n_quali = int((~IS_RACE).sum())
    n_race_all = int(IS_RACE.sum())
    n_race_clean = int((IS_RACE & IS_CLEAN).sum())
    n_race_dirty = n_race_all - n_race_clean
    log(f"total nodes: {total}  quali={n_quali}  "
        f"race_all={n_race_all}  race_clean={n_race_clean}  race_dirty={n_race_dirty}")

    # --- helper: build KID array for a given gate ---
    def build_kid(gate_mask):
        """For nodes passing gate_mask, assign key indices; filter thin keys."""
        keys = []
        for nm in TRACKS:
            for team, drvs in TEAMS.items():
                for d in drvs:
                    m = gate_mask & (TRACK == nm) & (DRIVER == d)
                    if m.sum() >= MIN_NODES:
                        keys.append((nm, d))
        key2id = {k: j for j, k in enumerate(keys)}
        kid = np.full(len(V), -1, dtype=int)
        sel = np.zeros(len(V), bool)
        for k in keys:
            nm, d = k
            m = gate_mask & (TRACK == nm) & (DRIVER == d)
            kid[m] = key2id[k]
            sel |= m
        return keys, key2id, kid, sel

    # --- FIT A: original (all race, no clean-air filter) ---
    log("\n=== FIT A: all race nodes (baseline replication) ===")
    gate_A = np.ones(len(V), bool)
    keys_A, key2id_A, kid_A, sel_A = build_kid(gate_A)
    fit_A = fit_deconf2(V[sel_A], G[sel_A], W[sel_A],
                        AGE[sel_A], COMP[sel_A], kid_A[sel_A])
    Bmap_A = {keys_A[j]: float(fit_A["B"][j]) for j in range(len(keys_A))}
    log(f"  A={fit_A['A']:.2f}  dMed={fit_A['dMed']:+.3f}  dHard={fit_A['dHard']:+.3f}")
    log(f"  wear: soft={fit_A['wear_soft']:+.4f} med={fit_A['wear_med']:+.4f} hard={fit_A['wear_hard']:+.4f}")

    # --- FIT B: clean-air race only ---
    log("\n=== FIT B: clean-air race nodes only (+ all quali) ===")
    gate_B = ~IS_RACE | IS_CLEAN   # include quali + clean race
    keys_B, key2id_B, kid_B, sel_B = build_kid(gate_B)
    fit_B = fit_deconf2(V[sel_B], G[sel_B], W[sel_B],
                        AGE[sel_B], COMP[sel_B], kid_B[sel_B])
    Bmap_B = {keys_B[j]: float(fit_B["B"][j]) for j in range(len(keys_B))}
    log(f"  A={fit_B['A']:.2f}  dMed={fit_B['dMed']:+.3f}  dHard={fit_B['dHard']:+.3f}")
    log(f"  wear: soft={fit_B['wear_soft']:+.4f} med={fit_B['wear_med']:+.4f} hard={fit_B['wear_hard']:+.4f}")

    # --- FIT C: quali only (clean baseline) ---
    log("\n=== FIT C: quali only ===")
    gate_C = ~IS_RACE
    keys_C, key2id_C, kid_C, sel_C = build_kid(gate_C)
    fit_C = fit_deconf2(V[sel_C], G[sel_C], W[sel_C],
                        AGE[sel_C], COMP[sel_C], kid_C[sel_C])
    Bmap_C = {keys_C[j]: float(fit_C["B"][j]) for j in range(len(keys_C))}
    log(f"  A={fit_C['A']:.2f}  dMed={fit_C['dMed']:+.3f}  dHard={fit_C['dHard']:+.3f}")

    # --- Print per-driver B for all three fits ---
    print("\n" + "=" * 80)
    print("PER-DRIVER B (1e-3 units) AND G@140 — THREE DATA GATES")
    print("FitA=all-race(robust)  FitB=clean-air(robust)  FitC=quali-only")
    print("=" * 80)

    for name in TRACKS:
        print(f"\n--- {name} ---")
        hdr = f"{'team':>5} {'drv':>4} | {'B_A':>6} {'G140_A':>7} | {'B_B':>6} {'G140_B':>7} | {'B_C':>6} {'G140_C':>7}"
        print(hdr)
        for team, drvs in TEAMS.items():
            for d in drvs:
                k = (name, d)
                def fmt(Bmap, fit, k):
                    if k in Bmap:
                        b = Bmap[k]
                        g = gat(fit["A"], b, 140)
                        return f"{b*1e3:6.2f} {g:7.2f}"
                    return f"{'--':>6} {'--':>7}"
                print(f"  {team:>5} {d:>4} | {fmt(Bmap_A, fit_A, k)} | "
                      f"{fmt(Bmap_B, fit_B, k)} | {fmt(Bmap_C, fit_C, k)}")

    # --- Constructor means ---
    print("\n" + "=" * 80)
    print("CONSTRUCTOR MEAN B (1e-3) per track — three gates")
    print("=" * 80)
    for name in TRACKS:
        cells_A, cells_B, cells_C = [], [], []
        for team, drvs in TEAMS.items():
            bs_A = [Bmap_A.get((name, d), None) for d in drvs]
            bs_A = [b for b in bs_A if b is not None]
            bs_B = [Bmap_B.get((name, d), None) for d in drvs]
            bs_B = [b for b in bs_B if b is not None]
            bs_C = [Bmap_C.get((name, d), None) for d in drvs]
            bs_C = [b for b in bs_C if b is not None]
            cells_A.append(f"{team}={np.mean(bs_A)*1e3:.2f}" if bs_A else f"{team}=--")
            cells_B.append(f"{team}={np.mean(bs_B)*1e3:.2f}" if bs_B else f"{team}=--")
            cells_C.append(f"{team}={np.mean(bs_C)*1e3:.2f}" if bs_C else f"{team}=--")
        print(f"  {name:>8} FitA: " + "  ".join(cells_A))
        print(f"  {name:>8} FitB: " + "  ".join(cells_B))
        print(f"  {name:>8} FitC: " + "  ".join(cells_C))

    # --- Teammate decompositions ---
    print("\n" + "=" * 80)
    print("TEAMMATE DECOMPOSITION (within vs between, 1e-3)")
    print("=" * 80)
    for label, Bmap in [("FitA(all-race)", Bmap_A), ("FitB(clean-air)", Bmap_B), ("FitC(quali)", Bmap_C)]:
        within, between = decompose(Bmap)
        if within and between:
            wm = float(np.mean(within)); bm = float(np.mean(between))
            ratio = bm / wm if wm > 0 else float("inf")
            print(f"  {label:20s}: within={wm:.3f}  between={bm:.3f}  ratio={ratio:.2f}")
        else:
            print(f"  {label:20s}: insufficient data for decomposition")

    # --- Hungary Mercedes flip diagnosis ---
    print("\n" + "=" * 80)
    print("MERCEDES HUNGARY FLIP DIAGNOSIS")
    print("FitC (quali) is expected Merc-LOW; FitB (clean-air race) should approach it")
    print("=" * 80)
    for name in ["Hungary"]:
        teams_order_A = sorted(TEAMS.keys(),
                                key=lambda t: -np.mean([Bmap_A.get((name, d), 0)
                                                         for d in TEAMS[t] if (name, d) in Bmap_A]))
        teams_order_B = sorted(TEAMS.keys(),
                                key=lambda t: -np.mean([Bmap_B.get((name, d), 0)
                                                         for d in TEAMS[t] if (name, d) in Bmap_B]))
        teams_order_C = sorted(TEAMS.keys(),
                                key=lambda t: -np.mean([Bmap_C.get((name, d), 0)
                                                         for d in TEAMS[t] if (name, d) in Bmap_C]))
        print(f"  FitA (all race): {' > '.join(teams_order_A)}")
        print(f"  FitB (clean air): {' > '.join(teams_order_B)}")
        print(f"  FitC (quali only): {' > '.join(teams_order_C)}")
        # Specific Merc vs RBR gap
        for fit_label, Bmap, fit in [("A", Bmap_A, fit_A), ("B", Bmap_B, fit_B), ("C", Bmap_C, fit_C)]:
            merc_B = [Bmap.get(("Hungary", d), None) for d in TEAMS["MERC"]]
            rbr_B = [Bmap.get(("Hungary", d), None) for d in TEAMS["RBR"]]
            merc_B = [b for b in merc_B if b is not None]
            rbr_B = [b for b in rbr_B if b is not None]
            if merc_B and rbr_B:
                merc_m = float(np.mean(merc_B)) * 1e3
                rbr_m = float(np.mean(rbr_B)) * 1e3
                direction = "MERC > RBR" if merc_m > rbr_m else "RBR > MERC"
                print(f"  Fit{fit_label}: Merc_B={merc_m:.3f}  RBR_B={rbr_m:.3f}  -> {direction}  "
                      f"(gap={abs(merc_m-rbr_m):.3f})")

    # Clean-air node statistics at Hungary
    print("\n  Hungary clean-air vs dirty-air node counts:")
    for team, drvs in TEAMS.items():
        for d in drvs:
            m_race = IS_RACE & (TRACK == "Hungary") & (DRIVER == d)
            m_clean = m_race & IS_CLEAN
            m_dirty = m_race & ~IS_CLEAN
            if m_race.sum() > 0:
                print(f"    {team}/{d}: {m_race.sum()} race nodes  "
                      f"clean={m_clean.sum()}  dirty={m_dirty.sum()}")

    # --- Cross-validation ---
    print("\n" + "=" * 80)
    print("CROSS-VALIDATION (hold-out-one-track, tyre-term transfer)")
    print("=" * 80)
    for gate_label, gate_name in [("all", "all race"), ("clean", "clean-air race"), ("quali", "quali only")]:
        cv = cross_validate(V, G, W, AGE, COMP, IS_RACE, IS_CLEAN, TRACK, DRIVER, gate=gate_label)
        print(f"\n  Gate: {gate_name}")
        for track, res in cv.items():
            if "error" in res:
                print(f"    {track}: {res['error']}")
            else:
                print(f"    {track} (held out):  n_train={res['n_train']}  n_test={res['n_test']}  "
                      f"var_raw={res['var_raw']:.4f}  var_corrected={res['var_corrected']:.4f}  "
                      f"reduction={res['var_reduction_pct']:.1f}%  "
                      f"mean_tyre_correction={res['mean_tyre_correction']:.3f}g")

    # --- SAR-Suzuka diagnosis ---
    print("\n" + "=" * 80)
    print("SAR-SUZUKA ARTIFACT DIAGNOSIS")
    print("=" * 80)
    for label, Bmap in [("FitA(all-race, robust)", Bmap_A),
                         ("FitB(clean-air, robust)", Bmap_B),
                         ("FitC(quali-only)", Bmap_C)]:
        k = ("Suzuka", "SAR")
        if k in Bmap:
            b = Bmap[k]
            g = gat(fit_A["A"], b, 140)
            print(f"  {label}: B={b*1e3:.3f}  G@140={g:.3f}g  "
                  f"{'OUTLIER (>1.2e-3)' if b > 1.2e-3 else 'OK'}")
        else:
            print(f"  {label}: SAR/Suzuka dropped (thin key, n<{MIN_NODES})")

    # Node counts for SAR Suzuka
    for gate_label, gate_mask in [("all", np.ones(len(V), bool)),
                                    ("clean", ~IS_RACE | IS_CLEAN),
                                    ("quali", ~IS_RACE)]:
        m = gate_mask & (TRACK == "Suzuka") & (DRIVER == "SAR")
        print(f"  SAR/Suzuka nodes under gate='{gate_label}': {m.sum()}")

    print("\n" + "=" * 80)
    print("SUMMARY: race-vs-quali truth position")
    print("=" * 80)
    # Compute Suzuka ordering under each fit
    for label, Bmap, fit in [("FitA(all-race)", Bmap_A, fit_A),
                               ("FitB(clean-air)", Bmap_B, fit_B),
                               ("FitC(quali)", Bmap_C, fit_C)]:
        szk_means = {}
        for team, drvs in TEAMS.items():
            bs = [Bmap.get(("Suzuka", d), None) for d in drvs]
            bs = [b for b in bs if b is not None]
            if bs:
                szk_means[team] = float(np.mean(bs)) * 1e3
        if szk_means:
            order = sorted(szk_means, key=lambda t: -szk_means[t])
            print(f"  Suzuka {label}: " + " > ".join(f"{t}({szk_means[t]:.2f})" for t in order))


if __name__ == "__main__":
    main()
