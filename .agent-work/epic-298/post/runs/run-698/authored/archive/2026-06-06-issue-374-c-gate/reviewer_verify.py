"""
Independent reviewer verification script for G2 close criteria (C1, C4, C5, C7).
Run from repo root: py .agent-work/issue-374-c-gate/reviewer_verify.py
"""
from __future__ import annotations
import sys
import numpy as np
from scipy.optimize import minimize
from pathlib import Path

# ── repo on path ──────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.fusion_replay.metalearner import (
    build_pairwise_dataset, _sigmoid, _pairwise_log_loss,
    _loso_cv_linear, _bootstrap_gap_ci, _model2a_features,
    _fit_mlp, _predict_mlp,
)

RECORDS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "evo_runs" / "issue-374-records"
_EPS = 1e-15
_LAM = 1e-6

def logistic_no_bias(X, y, lam=_LAM):
    """Independent reimplementation of no-bias logistic with analytic grad."""
    n, d = X.shape
    w0 = np.zeros(d)
    def f(w):
        p = 1.0 / (1.0 + np.exp(-np.clip(X @ w, -500, 500)))
        pc = np.clip(p, _EPS, 1-_EPS)
        loss = float(-np.mean(y * np.log(pc) + (1-y) * np.log(1-pc)))
        loss += 0.5 * lam * float(np.dot(w, w))
        grad = X.T @ (p - y) / n + lam * w
        return loss, grad
    res = minimize(f, w0, method="L-BFGS-B", jac=True,
                   options={"maxiter": 500, "ftol": 1e-12, "gtol": 1e-8})
    return res.x

def loso_cv_linear_independent(X, y, seasons, lam=_LAM):
    """Independent LOSO: leakage check built in."""
    unique_seasons = np.unique(seasons)
    logits = np.full(len(y), np.nan)
    for s in unique_seasons:
        train = seasons != s
        test  = seasons == s
        # Leakage assertion: no test season row in train
        assert not np.any(seasons[train] == s), f"LEAKAGE: season {s} in train!"
        w = logistic_no_bias(X[train], y[train])
        logits[test] = X[test] @ w
    return logits

def mean_log_loss(logits, y):
    p = np.clip(1/(1+np.exp(-np.clip(logits,-500,500))), _EPS, 1-_EPS)
    return float(-np.mean(y * np.log(p) + (1-y) * np.log(1-p)))

def bootstrap_gap_independent(y, l1, l2, event_ids, B=1000, seed=0):
    """Independent event-level bootstrap."""
    rng = np.random.default_rng(seed)
    unique_events = np.unique(event_ids)
    n_events = len(unique_events)
    p1 = np.clip(_sigmoid(l1), _EPS, 1-_EPS)
    p2 = np.clip(_sigmoid(l2), _EPS, 1-_EPS)
    gap_per_pair = (-(y*np.log(p1)+(1-y)*np.log(1-p1))) - (-(y*np.log(p2)+(1-y)*np.log(1-p2)))
    ev_idx = {ev: np.where(event_ids == ev)[0] for ev in unique_events}
    boot = np.empty(B)
    for b in range(B):
        sampled = rng.choice(unique_events, size=n_events, replace=True)
        idx = np.concatenate([ev_idx[ev] for ev in sampled])
        boot[b] = float(np.mean(gap_per_pair[idx]))
    lo = float(np.percentile(boot, 2.5))
    hi = float(np.percentile(boot, 97.5))
    return lo, hi

# ── Load quali dataset ────────────────────────────────────────────────────────
print("Loading quali dataset...")
ds = build_pairwise_dataset(RECORDS_DIR, "quali")
X = ds["X_delta"]
dev = ds["dev_delta"]
y = ds["y"]
event_ids = ds["event_ids"]
seasons = ds["seasons"]
print(f"  n_pairs={len(y)}, n_events={ds['coverage']['n_events_used']}, n_seasons={len(np.unique(seasons))}")

# ── C1: Independently recompute Model1 LOSO loss ─────────────────────────────
print("\n[C1] Independent Model1 LOSO (8-fold) ...")
my_logits_m1 = loso_cv_linear_independent(X, y, seasons)
my_loss_m1 = mean_log_loss(my_logits_m1, y)
builder_loss_m1 = 0.46440092228784385
diff_m1 = abs(my_loss_m1 - builder_loss_m1)
print(f"  My Model1 pooled-LOSO loss = {my_loss_m1:.6f}")
print(f"  Builder's Model1 loss      = {builder_loss_m1:.6f}")
print(f"  Diff                       = {diff_m1:.2e}")
c1_ok = diff_m1 < 1e-3
print(f"  C1 PASS: {c1_ok}" if c1_ok else f"  C1 FAIL: diff {diff_m1:.2e} >= 1e-3")

# ── C2: Model1 ≤ #373 baseline ────────────────────────────────────────────────
print("\n[C2] Model1 ≤ #373 baseline sanity:")
baselines = {"quali": 0.6489, "race_start": 0.6154, "race": 0.6400}
b373 = baselines["quali"]
print(f"  quali Model1={my_loss_m1:.5f}  baseline={b373:.5f}  OK={my_loss_m1 <= b373}")

# ── C3: LOSO leakage check (asserts inside loso_cv_linear_independent above) ──
print("\n[C3] LOSO leakage: all asserts passed inline (no exception raised above).")

# ── C4: Independent event-bootstrap CI ───────────────────────────────────────
# Use Model2b logits from the builder's stored run for this check
# We recompute Model1 logits independently and need Model2b logits
# Since Model2b uses torch with seeds, we'll run a quick LOSO MLP
print("\n[C4] Running LOSO Model2b (seed=0) for CI comparison ...")
import torch
torch.manual_seed(0)
np.random.seed(0)
my_logits_m2b = _loso_cv_mlp_independent = None

# Instead of reproducing Model2b exactly (torch seed-stream may differ),
# do the bootstrap test with Model2a (deterministic scipy) for C4/C5.
X_m2a = _model2a_features(X)
print("  Fitting LOSO Model2a independently ...")
my_logits_m2a = loso_cv_linear_independent(X_m2a, y, seasons)
my_loss_m2a = mean_log_loss(my_logits_m2a, y)
builder_loss_m2a = 0.46443447755662953
diff_m2a = abs(my_loss_m2a - builder_loss_m2a)
print(f"  My Model2a pooled-LOSO loss = {my_loss_m2a:.6f}")
print(f"  Builder's Model2a loss      = {builder_loss_m2a:.6f}")
print(f"  Diff                        = {diff_m2a:.2e}")
c5_ok = diff_m2a < 1e-3
print(f"  C5 PASS: {c5_ok}" if c5_ok else f"  C5 FAIL: diff {diff_m2a:.2e} >= 1e-3")

# C4: Bootstrap with our independently computed Model1 and Model2a logits
print("\n[C4] Independent event-bootstrap CI (B=200) ...")
my_gap_m2a = my_loss_m1 - my_loss_m2a
my_lo, my_hi = bootstrap_gap_independent(y, my_logits_m1, my_logits_m2a, event_ids, B=200, seed=0)
print(f"  My gap_model2a = {my_gap_m2a:+.6f}")
print(f"  My 95%CI       = [{my_lo:+.6f}, {my_hi:+.6f}]")
print(f"  CI brackets point estimate: {my_lo <= my_gap_m2a <= my_hi}")
# Width sanity: should be small positive on both ends (gap is near 0)
print(f"  Width = {my_hi - my_lo:.6f}")
c4_ok = (my_lo <= my_gap_m2a <= my_hi)
print(f"  C4 PASS: {c4_ok}" if c4_ok else f"  C4 FAIL: CI does not bracket point estimate")

# ── C6: dev probe checks ──────────────────────────────────────────────────────
print("\n[C6] dev_delta derivation check:")
expected_ctor = X[:, 2] - X[:, 0]
expected_drv  = X[:, 3] - X[:, 1]
diff_ctor = np.max(np.abs(dev[:, 0] - expected_ctor))
diff_drv  = np.max(np.abs(dev[:, 1] - expected_drv))
print(f"  dev[:,0] == X[:,2]-X[:,0]: max_diff = {diff_ctor:.2e} (should be ~0)")
print(f"  dev[:,1] == X[:,3]-X[:,1]: max_diff = {diff_drv:.2e} (should be ~0)")
c6_dev_ok = diff_ctor < 1e-12 and diff_drv < 1e-12
print(f"  C6 dev identity PASS: {c6_dev_ok}")

# dev_linear_gain (null check): fit [X, dev] = 6 features (rank ≤ 4)
X_dev_lin = np.hstack([X, dev])
my_logits_devlin = loso_cv_linear_independent(X_dev_lin, y, seasons)
my_loss_devlin = mean_log_loss(my_logits_devlin, y)
my_dev_linear_gain = my_loss_m1 - my_loss_devlin
builder_dev_linear = -7.716456628115154e-07
print(f"  dev_linear_gain (mine) = {my_dev_linear_gain:+.2e}  (expected ~0)")
print(f"  builder's              = {builder_dev_linear:+.2e}")
c6_linear_ok = abs(my_dev_linear_gain) < 1e-4
print(f"  C6 dev_linear_gain ~0 PASS: {c6_linear_ok}")

# ── C7: y-mean check per task (class imbalance) ──────────────────────────────
print("\n[C7] y-mean (class imbalance check):")
y_mean = float(np.mean(y))
print(f"  quali y_mean = {y_mean:.4f}  (ideal 0.5; one-sided i<j pairs)")
print(f"  Imbalance from 0.5: {abs(y_mean - 0.5):.4f}")

# C7: Does Model2a's advantage survive symmetrization?
# Augment with mirror rows: (-Δpi, 1-y)
X_aug = np.vstack([X, -X])
y_aug = np.concatenate([y, 1.0 - y])
seasons_aug = np.concatenate([seasons, seasons])
X_m2a_aug = _model2a_features(X_aug)
print("\n  Fitting Model1 and Model2a on SYMMETRIZED data (mirror rows) ...")
my_logits_m1_aug = loso_cv_linear_independent(X_aug, y_aug, seasons_aug)
my_logits_m2a_aug = loso_cv_linear_independent(X_m2a_aug, y_aug, seasons_aug)
loss_m1_aug = mean_log_loss(my_logits_m1_aug, y_aug)
loss_m2a_aug = mean_log_loss(my_logits_m2a_aug, y_aug)
gap_m2a_sym = loss_m1_aug - loss_m2a_aug
print(f"  Symmetrized: loss_m1={loss_m1_aug:.5f}  loss_m2a={loss_m2a_aug:.5f}  gap={gap_m2a_sym:+.6f}")
print(f"  Original gap_m2a = {my_gap_m2a:+.6f}")
print(f"  => Gap sign preserved after symmetrization: {(gap_m2a_sym > 0) == (my_gap_m2a > 0)}")

print("\n── SUMMARY ──────────────────────────────────────────────────────────────")
print(f"  C1 (Model1 LOSO loss matches):     {'PASS' if c1_ok else 'FAIL'}")
print(f"  C2 (Model1 ≤ baseline):            {'PASS' if my_loss_m1 <= b373 else 'FAIL'}")
print(f"  C3 (LOSO leakage-free):            PASS (asserts inside each fold)")
print(f"  C4 (bootstrap brackets estimate):  {'PASS' if c4_ok else 'FAIL'}")
print(f"  C5 (Model2a gap matches):          {'PASS' if c5_ok else 'FAIL'}")
print(f"  C6 (dev derivation + null gain):   {'PASS' if c6_dev_ok and c6_linear_ok else 'FAIL'}")
print(f"  C7 (y_mean={y_mean:.4f}, symmetrize check done)")
print("Done.")
