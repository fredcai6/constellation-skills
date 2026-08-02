#!/usr/bin/env python3
"""Walk-forward linear (logistic) probe on head's own feature differences.

Gate g1, issue #451.  Read-only scratch script — do NOT add to scripts/ or src/.

Strategy:
- For each headline year in LOSO fashion (train on all OTHER headline years,
  score on target year), build the probe features.
- Each scored pair comes from the EXACT shared non-tie pair set the harness uses
  (imported, never forked).
- The feature for each undirected pair (i,j): features_diff[pair_i_to_j] from
  the record's npz (antisymmetric, so direction is consistent within an event).
- Logistic regression (sklearn or hand-rolled with numpy) fit on train pairs,
  signed accuracy on test pairs.

No scored pair appears in the fit — guaranteed by LOSO year split.
Standardize features on train-year data only (no leakage).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Make repo importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Reuse harness primitives — import, never fork.
import scripts.diagnose_quali_same_pairs as dqsp
import scripts.diagnose_quali_evidence as dqe
from src.evo_predictor.module_record import load_module_record

RECORDS_DIR = Path(__file__).parent / "records"
EVIDENCE_DIR = Path(__file__).parent / "evidence"

HEADLINE_YEARS = dqsp.HEADLINE_YEARS   # (2018..2024)
OOS_YEARS = dqsp.OOS_YEARS             # (2025,)
RW_STEM = "rw"

# --------------------------------------------------------------------------- #
# Utilities to extract features for the SHARED pairs
# --------------------------------------------------------------------------- #

def _load_rw_events(year: int) -> list:
    """Load race-weekend record events for a given year."""
    path = RECORDS_DIR / f"rw_{year}.record.json"
    rec = load_module_record(path)
    return rec["events"]


def _build_pair_index_map(ev: dict) -> dict[tuple[int, int], int]:
    """Map (i_idx, j_idx) -> row index in the directed pair array.

    pair_index stores directed pairs as entity indices (not driver ids).
    Returns a dict from (left_entity_idx, right_entity_idx) -> row.
    """
    pair_index = ev["pair_index"]  # shape (n_pairs, 2)
    return {(int(pair_index[r, 0]), int(pair_index[r, 1])): r
            for r in range(len(pair_index))}


def _get_shared_pair_features(
    ev: dict,
    shared_pairs_driverids: list[tuple[str, str]],
    target: dict[str, float],
) -> tuple[np.ndarray, np.ndarray] | None:
    """Extract (features_diff, outcomes) for the harness-shared undirected pairs.

    shared_pairs_driverids: list of (di, dj) undirected driver-id pairs
      (from _shared_nontie_pairs, which returns them in sorted entity order).
    Returns (X, y) where X[k] = feature diff for pair k, y[k] = 1 if di beat dj.
    """
    entity_ids = list(ev["entity_ids"])
    id_to_idx = {did: i for i, did in enumerate(entity_ids)}
    pair_map = _build_pair_index_map(ev)
    features = ev["features"]  # (n_directed_pairs, 23)

    X_rows = []
    y_rows = []
    for di, dj in shared_pairs_driverids:
        if di not in id_to_idx or dj not in id_to_idx:
            continue
        i_idx = id_to_idx[di]
        j_idx = id_to_idx[dj]
        # Use directed pair i->j; if not found, use j->i with negated features
        if (i_idx, j_idx) in pair_map:
            row = pair_map[(i_idx, j_idx)]
            feat = features[row].copy()
        elif (j_idx, i_idx) in pair_map:
            row = pair_map[(j_idx, i_idx)]
            feat = -features[row].copy()  # antisymmetric
        else:
            continue
        # outcome: 1 if di beats dj (lower Q position = better)
        y = 1.0 if target[di] < target[dj] else 0.0
        X_rows.append(feat)
        y_rows.append(y)

    if not X_rows:
        return None
    return np.array(X_rows, dtype=np.float32), np.array(y_rows, dtype=np.float32)


# --------------------------------------------------------------------------- #
# Per-event: gather features on the harness-shared pairs
# --------------------------------------------------------------------------- #

def collect_event_features_on_shared_pairs(
    ev: dict,
    yr: int,
    rnd: int,
    con,
    ev_meta: dict,
) -> tuple[np.ndarray, np.ndarray] | None:
    """For one event, collect (features, outcome) on the harness-shared pairs.

    Returns None if event is sprint / missing FP / no shared pairs.
    """
    stypes = ev_meta.get(rnd, set())
    if dqe.is_sprint_weekend(stypes):
        return None
    if not ({"FP1", "FP2", "FP3"} <= stypes) or "Q" not in stypes:
        return None

    # Build all three sources (same as harness) to determine SHARED non-tie pairs
    target = dqe.classification_order(con, yr, rnd, "Q")
    baf = dqe.best_across_fp_source(con, rnd, dqe.agg_theoretical_best, ("FP1", "FP2", "FP3"))
    blr = dqe.session_blend_rank_source(con, rnd, dqe.agg_theoretical_best, ("FP1", "FP2", "FP3"))
    model_src = dqsp._model_source(ev)

    common_set = set(model_src) & set(baf) & set(blr) & set(target)
    if len(common_set) < 2:
        return None
    common = sorted(common_set)
    m_src = dqsp._restrict(model_src, common_set)
    b_src = dqsp._restrict(baf, common_set)
    r_src = dqsp._restrict(blr, common_set)
    tgt = dqsp._restrict(target, common_set)

    shared = dqsp._shared_nontie_pairs(common, tgt, [m_src, b_src, r_src])
    if not shared:
        return None

    # Extract features for those shared pairs
    ev_restricted = dict(ev)
    result = _get_shared_pair_features(ev_restricted, shared, tgt)
    return result


def collect_year_features(year: int) -> tuple[np.ndarray, np.ndarray] | None:
    """Collect all (features, outcomes) for a year on harness-shared pairs."""
    try:
        events = _load_rw_events(year)
    except Exception as e:
        print(f"  [year={year}] FAILED to load records: {e}")
        return None

    con = dqe.open_db(year)
    if con is None:
        print(f"  [year={year}] FAILED to open DB")
        return None

    ev_meta = {rnd: stypes for rnd, _gp, stypes in dqe.events_for_year(con, year)}
    X_all, y_all = [], []
    for ev in events:
        yr, rnd = dqsp._parse_event_id(ev["event_id"])
        result = collect_event_features_on_shared_pairs(ev, yr, rnd, con, ev_meta)
        if result is None:
            continue
        X_ev, y_ev = result
        X_all.append(X_ev)
        y_all.append(y_ev)

    con.close()
    if not X_all:
        return None
    return np.concatenate(X_all, axis=0), np.concatenate(y_all, axis=0)


# --------------------------------------------------------------------------- #
# Logistic regression (numpy-only, no sklearn dependency)
# --------------------------------------------------------------------------- #

def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def logistic_fit(X: np.ndarray, y: np.ndarray, n_iter: int = 500, lr: float = 0.1) -> np.ndarray:
    """Fit logistic regression via gradient descent. Returns weight vector (n_features+1,) with bias."""
    n, d = X.shape
    w = np.zeros(d + 1, dtype=np.float64)
    Xb = np.hstack([X, np.ones((n, 1), dtype=X.dtype)]).astype(np.float64)
    y = y.astype(np.float64)
    for _ in range(n_iter):
        p = sigmoid(Xb @ w)
        grad = Xb.T @ (p - y) / n
        w -= lr * grad
    return w


def logistic_predict(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Predict logits (not probabilities)."""
    Xb = np.hstack([X, np.ones((len(X), 1), dtype=X.dtype)]).astype(np.float64)
    return Xb @ w


def sign_accuracy(logits: np.ndarray, y: np.ndarray) -> float:
    """Sign accuracy: fraction where sign(logit) == sign(y - 0.5)."""
    pred = (logits > 0).astype(float)
    return float(np.mean(pred == y))


# --------------------------------------------------------------------------- #
# Walk-forward LOSO probe
# --------------------------------------------------------------------------- #

def run_loso_probe() -> dict:
    """Leave-one-year-out walk-forward probe over headline years.

    For each target year t in HEADLINE_YEARS:
      - train on all other headline years (no overlap with t)
      - standardize features using train-set stats ONLY
      - score on t's shared pairs
    Pool all test-year results.
    """
    print("\n=== Loading per-year features on harness-shared pairs ===")
    year_data: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for yr in HEADLINE_YEARS:
        print(f"  Loading year {yr}...", end=" ", flush=True)
        result = collect_year_features(yr)
        if result is None:
            print("SKIP (no data)")
        else:
            X, y = result
            print(f"ok ({len(X)} pairs, {y.mean():.3f} pos rate)")
            year_data[yr] = (X, y)

    available_years = sorted(year_data.keys())
    print(f"\nAvailable years for probe: {available_years}")
    if len(available_years) < 2:
        print("ERROR: need >= 2 years for LOSO")
        return {"error": "insufficient years", "acc": float("nan")}

    print("\n=== LOSO walk-forward probe ===")
    all_pred_correct = []
    all_n_pairs = []

    for target_yr in available_years:
        train_years = [yr for yr in available_years if yr != target_yr]
        X_train = np.concatenate([year_data[yr][0] for yr in train_years], axis=0)
        y_train = np.concatenate([year_data[yr][1] for yr in train_years], axis=0)
        X_test, y_test = year_data[target_yr]

        # Standardize on train only (no leakage)
        mu = X_train.mean(axis=0)
        sd = X_train.std(axis=0) + 1e-8
        X_train_z = (X_train - mu) / sd
        X_test_z = (X_test - mu) / sd

        # Fit logistic regression
        w = logistic_fit(X_train_z, y_train)
        logits = logistic_predict(X_test_z, w)
        acc = sign_accuracy(logits, y_test)
        n = len(y_test)
        print(f"  LOSO target={target_yr}: n_train={len(y_train)}, n_test={n}, sign_acc={acc:.4f}")
        all_pred_correct.append(int(round(acc * n)))
        all_n_pairs.append(n)

    total_correct = sum(all_pred_correct)
    total_pairs = sum(all_n_pairs)
    pooled_acc = total_correct / total_pairs if total_pairs > 0 else float("nan")
    print(f"\nPooled LOSO sign accuracy on headline shared pairs: {pooled_acc:.4f} ({total_pairs} pairs)")

    return {
        "acc": pooled_acc,
        "total_pairs": total_pairs,
        "method": "LOSO (leave-one-year-out) logistic regression on head's features",
        "leakage_control": "train_years != test_year; standardize on train only; no scored pair in fit",
        "years_used": available_years,
        "per_year": [
            {"year": yr, "n_test": n, "correct": c}
            for yr, n, c in zip(available_years, all_n_pairs, all_pred_correct)
        ],
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    probe_result = run_loso_probe()

    print("\n=== LINEAR PROBE SUMMARY ===")
    print(f"Pooled sign accuracy (LOSO, headline 2018-2024): {probe_result.get('acc', float('nan')):.4f}")
    print(f"Total pairs scored: {probe_result.get('total_pairs', 0)}")
    print(f"Method: {probe_result.get('method', 'N/A')}")
    print(f"Leakage control: {probe_result.get('leakage_control', 'N/A')}")

    # Write probe result
    probe_out = EVIDENCE_DIR / "linear_probe_result.json"
    probe_out.write_text(json.dumps(probe_result, indent=2), encoding="utf-8")
    print(f"\n[wrote] {probe_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
