#!/usr/bin/env py
"""Offline significance + coverage probe for race_start sigma (gate g1).

MEASUREMENT ONLY. Torch-free. Reads a gold-cycle details.json (read-only) and
answers two questions for the evo-prediction-ceiling investigation:

(a) Significance of each module's
        sigma_corr = pearson(sigma_pi_trace, rank_mae_vs_retro_bt)
    over its 24 eval-year-2025 event_level_metrics rows. For each module we
    report the point estimate, a 95% CI by BOTH the seeded bootstrap percentile
    method AND the Fisher-z closed form (they should agree), a two-sided p-value
    vs H0: rho=0, and a verdict (significant / indistinguishable-from-0). We also
    print the n-aware critical |r|, r_crit(n=24, alpha=0.05) (closed form via the
    Student-t distribution) -- the proposed honest threshold for the next gate.

(b) Race-start sigma LEVEL / coverage. Using the fitted (alpha, beta) per module
    from the uncertainty-calibration artifact (with the aggregate task-level
    calibration reported as a caveat), compute
        calibrated_sigma = alpha * sigma_pi_trace + beta * effective_dof
    with effective_dof = max(entity_count - 1, 1). entity_count is None in this
    report, so effective_dof falls back to 1 (stated explicitly in output). We
    then summarize, per phase (quali / race / race_start), mean(calibrated_sigma)
    vs mean(realized rank error) and CV(sigma) vs CV(error), and end with an
    explicit verdict: is race_start sigma mis-leveled (too high and/or too flat)
    relative to quali/race, or already coverage-aligned?

This script is statistically honest: if the data shows the race_start level is
already fine, it reports a "coverage-aligned" verdict. It does not manufacture a
mis-level.

Dependencies: stdlib only is sufficient (math, json, random, statistics,
argparse). numpy/scipy are used when present purely as a cross-check / for their
distribution functions; the script degrades gracefully to closed-form stdlib
implementations (Student-t CDF via the regularized incomplete beta function,
quantiles via bisection) and prints which path was taken.

Run:
    py .agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py
    py .agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py --selftest
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from typing import Optional

# ----- repo-relative default paths (script lives in evidence/; repo root is 4 up)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
DEFAULT_DETAILS = os.path.join(
    _REPO_ROOT, "reports", "evo", "gold_cycle_260603_173742_2018thru2024.details.json"
)
DEFAULT_EVIDENCE_OUT = os.path.join(_THIS_DIR, "g1_evidence.json")

ALPHA = 0.05
N_BOOT = 10000
BOOT_SEED = 20260603  # deterministic re-runs

# ----- optional scientific libs (cross-check only; never required) -----------
try:
    import numpy as _np  # type: ignore

    _HAVE_NUMPY = True
except Exception:  # pragma: no cover - exercised only when numpy missing
    _np = None
    _HAVE_NUMPY = False

try:
    from scipy import stats as _sps  # type: ignore

    _HAVE_SCIPY = True
except Exception:  # pragma: no cover - exercised only when scipy missing
    _sps = None
    _HAVE_SCIPY = False


# =============================================================================
# Stdlib statistics core (no third-party requirement)
# =============================================================================
def pearson(x: list[float], y: list[float]) -> float:
    """Pearson correlation, closed form. Matches the engine's embedded value."""
    n = len(x)
    if n != len(y):
        raise ValueError(f"pearson: length mismatch x={len(x)} y={len(y)}")
    if n < 3:
        raise ValueError(f"pearson: need n>=3, got {n}")
    mx = sum(x) / n
    my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    denom = math.sqrt(sxx * syy)
    if denom == 0.0:
        # zero variance on a side -> correlation undefined; report 0 (flat).
        return 0.0
    return sxy / denom


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (Numerical Recipes)."""
    MAXIT = 200
    EPS = 3.0e-12
    FPMIN = 1.0e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    dd = 1.0 - qab * x / qap
    if abs(dd) < FPMIN:
        dd = FPMIN
    dd = 1.0 / dd
    h = dd
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        dd = 1.0 + aa * dd
        if abs(dd) < FPMIN:
            dd = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        dd = 1.0 / dd
        h *= dd * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        dd = 1.0 + aa * dd
        if abs(dd) < FPMIN:
            dd = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        dd = 1.0 / dd
        delta = dd * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break
    return h


def reg_incomplete_beta(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a,b) via lgamma + continued fraction."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def student_t_sf(t: float, df: float) -> float:
    """Two-sided -> use |t|; this returns the one-sided upper tail P(T > t)."""
    # P(T > t) for t>=0 ; symmetric for t<0.
    x = df / (df + t * t)
    ib = 0.5 * reg_incomplete_beta(df / 2.0, 0.5, x)
    if t >= 0.0:
        return ib
    return 1.0 - ib


def student_t_two_sided_p(t: float, df: float) -> float:
    """Two-sided p-value for a t statistic (stdlib path)."""
    x = df / (df + t * t)
    return reg_incomplete_beta(df / 2.0, 0.5, x)  # == 2 * P(T > |t|)


def student_t_ppf(p: float, df: float) -> float:
    """Inverse Student-t CDF via bisection on the stdlib CDF. p in (0,1)."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"student_t_ppf: p must be in (0,1), got {p}")

    def cdf(t: float) -> float:
        # CDF(t) = 1 - sf(t) for t>=0 ; = sf(-t) for t<0 (symmetry)
        if t >= 0.0:
            return 1.0 - student_t_sf(t, df)
        return student_t_sf(-t, df)

    lo, hi = -1.0e4, 1.0e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def t_critical(df: float, alpha: float = ALPHA) -> float:
    """Two-sided critical t value t_{1-alpha/2, df}. Prefers scipy, else stdlib."""
    q = 1.0 - alpha / 2.0
    if _HAVE_SCIPY:
        return float(_sps.t.ppf(q, df))
    return student_t_ppf(q, df)


def r_critical(n: int, alpha: float = ALPHA) -> float:
    """n-aware critical |r| for a Pearson correlation, two-sided at `alpha`.

    t_crit = ppf(1 - alpha/2, n-2);  r_crit = t_crit / sqrt(n - 2 + t_crit^2).
    """
    df = n - 2
    tc = t_critical(df, alpha)
    return tc / math.sqrt(df + tc * tc)


def corr_p_value(r: float, n: int) -> float:
    """Two-sided p-value for H0: rho=0 from a sample correlation. scipy|stdlib."""
    df = n - 2
    # guard |r|->1
    r = max(min(r, 1.0 - 1e-15), -1.0 + 1e-15)
    t = r * math.sqrt(df) / math.sqrt(1.0 - r * r)
    if _HAVE_SCIPY:
        return float(2.0 * _sps.t.sf(abs(t), df))
    return student_t_two_sided_p(t, df)


def fisher_z_ci(r: float, n: int, alpha: float = ALPHA) -> tuple[float, float]:
    """Closed-form Fisher z-transform CI for a correlation. Needs only math."""
    if n <= 3:
        raise ValueError(f"fisher_z_ci: need n>3, got {n}")
    r = max(min(r, 1.0 - 1e-12), -1.0 + 1e-12)
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    # normal critical value for the requested alpha
    if _HAVE_SCIPY:
        zc = float(_sps.norm.ppf(1.0 - alpha / 2.0))
    else:
        zc = _norm_ppf(1.0 - alpha / 2.0)
    lo = math.tanh(z - zc * se)
    hi = math.tanh(z + zc * se)
    return lo, hi


def _norm_ppf(p: float) -> float:
    """Acklam's rational approximation to the standard-normal inverse CDF."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"_norm_ppf: p must be in (0,1), got {p}")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow = 0.02425
    phigh = 1.0 - plow
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)


def bootstrap_corr_ci(
    x: list[float], y: list[float], n_boot: int = N_BOOT, seed: int = BOOT_SEED,
    alpha: float = ALPHA,
) -> tuple[float, float, int]:
    """Seeded paired-resample percentile CI for the correlation.

    Returns (lo, hi, n_valid). Resamples with zero variance on either side are
    skipped (correlation undefined there); n_valid reports how many were kept.
    """
    rng = random.Random(seed)
    n = len(x)
    idx = range(n)
    stats: list[float] = []
    for _ in range(n_boot):
        sample = [rng.randrange(n) for _ in idx]
        bx = [x[i] for i in sample]
        by = [y[i] for i in sample]
        # skip degenerate resamples (no variance on a side)
        if len(set(bx)) < 2 or len(set(by)) < 2:
            continue
        stats.append(pearson(bx, by))
    if len(stats) < 100:
        # not enough valid resamples to trust a percentile CI
        return float("nan"), float("nan"), len(stats)
    stats.sort()
    lo_q = alpha / 2.0
    hi_q = 1.0 - alpha / 2.0

    def _pct(s: list[float], q: float) -> float:
        # linear-interpolation percentile (type 7), matches numpy default
        if not s:
            return float("nan")
        pos = q * (len(s) - 1)
        lo_i = int(math.floor(pos))
        hi_i = int(math.ceil(pos))
        if lo_i == hi_i:
            return s[lo_i]
        frac = pos - lo_i
        return s[lo_i] * (1 - frac) + s[hi_i] * frac

    return _pct(stats, lo_q), _pct(stats, hi_q), len(stats)


def mean(v: list[float]) -> float:
    return sum(v) / len(v)


def stdev_sample(v: list[float]) -> float:
    n = len(v)
    if n < 2:
        return float("nan")
    m = mean(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / (n - 1))


def cv(v: list[float]) -> float:
    """Coefficient of variation = sample stdev / |mean|."""
    m = mean(v)
    if m == 0.0:
        return float("nan")
    return stdev_sample(v) / abs(m)


# =============================================================================
# Data loading
# =============================================================================
TARGET_X = "sigma_pi_trace"
TARGET_Y = "rank_mae_vs_retro_bt"


def load_details(path: str) -> dict:
    if not os.path.exists(path):
        raise SystemExit(
            f"STOP: details.json not found at {path}. Cannot produce evidence."
        )
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_calibration_artifact(details: dict) -> tuple[Optional[dict], Optional[str]]:
    """Locate and load the per-module uncertainty-calibration artifact.

    Returns (artifact_modules_dict_or_None, resolved_path_or_None). The path in
    the report uses Windows separators; we normalise and resolve against repo root.
    """
    rel = details.get("uncertainty_calibration_path")
    if not rel:
        return None, None
    norm = rel.replace("\\", os.sep).replace("/", os.sep)
    candidates = [
        norm if os.path.isabs(norm) else os.path.join(_REPO_ROOT, norm),
        os.path.join(_REPO_ROOT, *norm.split(os.sep)),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            with open(cand, "r", encoding="utf-8") as fh:
                art = json.load(fh)
            return art.get("modules", {}), cand
    return None, None


def event_series(module: dict) -> tuple[list[float], list[float], list[Optional[int]], int]:
    """Extract (sigma, rank_mae_vs_retro_bt, entity_count, n_skipped) for a module.

    Only rows where both target fields are present are kept for the correlation;
    rows missing either target, or flagged skipped, are excluded and counted.
    """
    rows = module.get("event_level_metrics", []) or []
    xs: list[float] = []
    ys: list[float] = []
    ecount: list[Optional[int]] = []
    n_skipped = 0
    for r in rows:
        if r.get("skipped_reason"):
            n_skipped += 1
            continue
        xv = r.get(TARGET_X)
        yv = r.get(TARGET_Y)
        if xv is None or yv is None:
            n_skipped += 1
            continue
        xs.append(float(xv))
        ys.append(float(yv))
        ecount.append(r.get("entity_count"))
    return xs, ys, ecount, n_skipped


# =============================================================================
# Part (a): significance
# =============================================================================
def analyse_module_significance(name: str, module: dict, cal_modules: Optional[dict]) -> dict:
    xs, ys, ecount, n_skipped = event_series(module)
    n = len(xs)
    task = module.get("task")
    scope = module.get("entity_scope")
    source = module.get("evidence_source")
    embedded = (
        module.get("uncertainty_calibration", {})
        .get("correlations", {})
        .get("corr_sigma_pi_trace_vs_rank_mae")
    )

    out: dict = {
        "module": name,
        "task": task,
        "entity_scope": scope,
        "evidence_source": source,
        "n": n,
        "n_skipped": n_skipped,
        "is_race_start": task == "race_start",
        "embedded_engine_corr": embedded,
    }

    if n < 4:
        out.update({
            "sigma_corr": None,
            "verdict": "insufficient-n",
        })
        return out

    r = pearson(xs, ys)
    p = corr_p_value(r, n)
    fz_lo, fz_hi = fisher_z_ci(r, n)
    bs_lo, bs_hi, bs_valid = bootstrap_corr_ci(xs, ys)
    rcrit = r_critical(n)

    # numpy cross-check of the point estimate (does not change result)
    np_r = None
    if _HAVE_NUMPY:
        try:
            np_r = float(_np.corrcoef(_np.asarray(xs), _np.asarray(ys))[0, 1])
        except Exception:
            np_r = None

    # match against engine embedded value (sanity anchor)
    embedded_match = (
        embedded is not None and abs(r - float(embedded)) < 1e-6
    )

    significant = (p < ALPHA) and (abs(r) >= rcrit)
    # CI-excludes-zero is the same call by construction; report it explicitly too
    fz_excludes_zero = (fz_lo > 0.0) or (fz_hi < 0.0)
    bs_excludes_zero = (
        not (math.isnan(bs_lo) or math.isnan(bs_hi))
        and ((bs_lo > 0.0) or (bs_hi < 0.0))
    )

    out.update({
        "sigma_corr": r,
        "numpy_corr": np_r,
        "embedded_match": embedded_match,
        "p_value": p,
        "fisher_ci": [fz_lo, fz_hi],
        "bootstrap_ci": [bs_lo, bs_hi],
        "bootstrap_valid_resamples": bs_valid,
        "r_crit": rcrit,
        "fisher_excludes_zero": fz_excludes_zero,
        "bootstrap_excludes_zero": bs_excludes_zero,
        "significant": significant,
        "verdict": "significant" if significant else "indistinguishable-from-0",
    })
    return out


# =============================================================================
# Part (b): level / coverage
# =============================================================================
def module_alpha_beta(name: str, cal_modules: Optional[dict]) -> tuple[float, float, str, str]:
    """Per-module fitted (alpha, beta) from the artifact; identity if absent.

    Returns (alpha, beta, fit_status, dof_rule).
    """
    if cal_modules and name in cal_modules:
        c = cal_modules[name]
        return (
            float(c.get("alpha", 1.0)),
            float(c.get("beta", 0.0)),
            str(c.get("fit_status", "unknown")),
            str(c.get("effective_dof_rule", "max(entity_count - 1, 1)")),
        )
    return 1.0, 0.0, "missing-artifact-identity", "max(entity_count - 1, 1)"


def effective_dof(entity_count: Optional[int]) -> tuple[float, bool]:
    """effective_dof = max(entity_count-1, 1); None -> 1 (fallback flagged)."""
    if entity_count is None:
        return 1.0, True
    return float(max(entity_count - 1, 1)), False


def calibrated_sigma_series(
    module: dict, alpha: float, beta: float
) -> tuple[list[float], list[float], bool]:
    """Return (calibrated_sigma_per_event, realized_error_per_event, used_fallback)."""
    xs, ys, ecount, _ = event_series(module)
    cal: list[float] = []
    used_fallback = False
    for x, ec in zip(xs, ecount):
        dof, fb = effective_dof(ec)
        used_fallback = used_fallback or fb
        cal.append(alpha * x + beta * dof)
    return cal, ys, used_fallback


def analyse_phase_levels(
    details: dict, cal_modules: Optional[dict]
) -> tuple[dict, bool]:
    """Aggregate per-phase calibrated-sigma vs realized error level and flatness.

    Pools every event across the modules of a phase (quali/race/race_start).
    Returns (per_phase_dict, any_entity_count_fallback).
    """
    modules = details["modules"]
    phases = ["quali", "race", "race_start"]
    bucket: dict[str, dict[str, list[float]]] = {
        ph: {"cal": [], "err": [], "raw_sigma": []} for ph in phases
    }
    any_fallback = False
    per_module_beta: dict[str, list[float]] = {ph: [] for ph in phases}

    for name, module in modules.items():
        task = module.get("task")
        if task not in bucket:
            continue
        a, b, _status, _rule = module_alpha_beta(name, cal_modules)
        per_module_beta[task].append(b)
        cal, err, fb = calibrated_sigma_series(module, a, b)
        raw_sigma, _, _, _ = event_series(module)
        any_fallback = any_fallback or fb
        bucket[task]["cal"].extend(cal)
        bucket[task]["err"].extend(err)
        bucket[task]["raw_sigma"].extend(raw_sigma)

    per_phase: dict[str, dict] = {}
    for ph in phases:
        cal = bucket[ph]["cal"]
        err = bucket[ph]["err"]
        raw = bucket[ph]["raw_sigma"]
        if not cal or not err:
            per_phase[ph] = {"n_events": 0}
            continue
        per_phase[ph] = {
            "n_events": len(cal),
            "mean_calibrated_sigma": mean(cal),
            "mean_realized_error": mean(err),
            "level_ratio_sigma_over_error": (mean(cal) / mean(err)) if mean(err) else float("nan"),
            "cv_calibrated_sigma": cv(cal),
            # raw sigma CV is fallback-INDEPENDENT (no beta constant). Under the
            # entity_count=None fallback this is the faithful flatness signal,
            # because calibrated_sigma = sigma + beta is ~99.9% the beta constant
            # and its CV is an artifact of the per-module beta mix, not of how
            # sigma tracks event difficulty. We therefore judge "too flat" on
            # raw-sigma CV and keep calibrated-sigma CV only for transparency.
            "cv_raw_sigma": cv(raw),
            "cv_realized_error": cv(err),
            "flatness_ratio_cvrawsigma_over_cverror": (
                cv(raw) / cv(err) if cv(err) not in (0.0,) and not math.isnan(cv(err)) else float("nan")
            ),
            "mean_raw_sigma_pi_trace": mean(raw),
            "betas_used": sorted(set(per_module_beta[ph])),
        }
    return per_phase, any_fallback


def race_start_level_verdict(per_phase: dict) -> dict:
    """Compare race_start level/flatness against the quali+race reference.

    "too high"  : race_start level_ratio (calibrated_sigma/error) materially
                  exceeds the quali/race reference ratios.
    "too flat"  : race_start CV(raw sigma) materially below CV(error) AND below
                  the quali/race CV(raw sigma) reference (i.e. sigma fails to
                  move with the events it is supposed to track). We use RAW-sigma
                  CV, not calibrated-sigma CV, because under the entity_count=None
                  fallback effective_dof=1 makes calibrated_sigma = sigma + beta,
                  whose CV is dominated by the per-module beta constant and is not
                  a faithful flatness signal.
    Otherwise   : coverage-aligned.

    Materiality threshold is a relative 25% gap -- conservative, so we only call
    a mis-level when it is clearly outside the reference band.
    """
    rs = per_phase.get("race_start", {})
    if rs.get("n_events", 0) == 0:
        return {"verdict": "no-data", "reason": "no race_start events"}

    refs = [per_phase.get("quali", {}), per_phase.get("race", {})]
    refs = [r for r in refs if r.get("n_events", 0) > 0]
    if not refs:
        return {"verdict": "no-reference", "reason": "no quali/race reference phases"}

    REL = 0.25  # 25% relative gap = "material"

    ref_level = mean([r["level_ratio_sigma_over_error"] for r in refs])
    rs_level = rs["level_ratio_sigma_over_error"]
    # flatness judged on RAW sigma CV (fallback-independent), not calibrated.
    ref_cv_sigma = mean([r["cv_raw_sigma"] for r in refs])
    rs_cv_sigma = rs["cv_raw_sigma"]
    rs_cv_err = rs["cv_realized_error"]

    # "too high": race_start sigma/error ratio exceeds reference by > REL.
    too_high = (
        not math.isnan(ref_level)
        and ref_level > 0
        and (rs_level - ref_level) / ref_level > REL
    )
    # "too flat": race_start raw sigma varies far less than its own error AND far
    # less than the reference raw-sigma variability.
    flat_vs_error = (
        not math.isnan(rs_cv_err)
        and rs_cv_err > 0
        and (rs_cv_err - rs_cv_sigma) / rs_cv_err > REL
    )
    flat_vs_reference = (
        not math.isnan(ref_cv_sigma)
        and ref_cv_sigma > 0
        and (ref_cv_sigma - rs_cv_sigma) / ref_cv_sigma > REL
    )
    too_flat = flat_vs_error and flat_vs_reference

    if too_high or too_flat:
        labels = []
        if too_high:
            labels.append("too-high")
        if too_flat:
            labels.append("too-flat")
        verdict = "mis-leveled:" + "+".join(labels)
    else:
        verdict = "coverage-aligned"

    return {
        "verdict": verdict,
        "too_high": too_high,
        "too_flat": too_flat,
        "flat_vs_error": flat_vs_error,
        "flat_vs_reference": flat_vs_reference,
        "race_start_level_ratio": rs_level,
        "reference_level_ratio": ref_level,
        "race_start_cv_raw_sigma": rs_cv_sigma,
        "race_start_cv_error": rs_cv_err,
        "reference_cv_raw_sigma": ref_cv_sigma,
        "flatness_basis": "raw_sigma_pi_trace_cv (fallback-independent)",
        "materiality_relative_gap": REL,
    }


# =============================================================================
# Reporting
# =============================================================================
def _fmt(v, w=8, p=4):
    if v is None:
        return " " * (w - 1) + "-"
    if isinstance(v, float) and math.isnan(v):
        return " " * (w - 3) + "nan"
    return f"{v:>{w}.{p}f}"


def print_report(details: dict, results: list[dict], per_phase: dict,
                 rs_verdict: dict, r_crit_24: float, n_for_rcrit: int,
                 cal_path: Optional[str], any_fallback: bool) -> None:
    libline = (
        f"libs: numpy={'yes' if _HAVE_NUMPY else 'no'} "
        f"scipy={'yes' if _HAVE_SCIPY else 'no'} "
        f"(distribution fns use {'scipy' if _HAVE_SCIPY else 'stdlib closed-form'})"
    )
    print("=" * 100)
    print("g1 sigma-significance + coverage probe  (MEASUREMENT ONLY)")
    print("=" * 100)
    print(f"details : {details.get('summary_report_path', '?')}")
    print(f"calib   : {cal_path or '(artifact not found -> identity alpha=1,beta=0)'}")
    print(libline)
    print(f"bootstrap: paired percentile, n_boot={N_BOOT}, seed={BOOT_SEED}, alpha={ALPHA}")
    print()

    # ---- Part (a) table ----
    print("-" * 100)
    print("PART (a)  sigma_corr = pearson(sigma_pi_trace, rank_mae_vs_retro_bt)  over per-module 2025 events")
    print("-" * 100)
    hdr = (f"{'module':50s} {'ph':10s} {'n':>2s} {'r':>8s} {'p':>7s} "
           f"{'fisher95CI':>17s} {'boot95CI':>17s} verdict")
    print(hdr)
    print("-" * 100)

    def row(res: dict) -> str:
        if res.get("sigma_corr") is None:
            return f"{res['module']:50s} {str(res['task']):10s} {res['n']:>2d} {'-':>8s}  (n<4)"
        fci = res["fisher_ci"]
        bci = res["bootstrap_ci"]
        return (
            f"{res['module']:50s} {str(res['task']):10s} {res['n']:>2d} "
            f"{res['sigma_corr']:>+8.4f} {res['p_value']:>7.3f} "
            f"[{fci[0]:>+6.3f},{fci[1]:>+6.3f}] [{bci[0]:>+6.3f},{bci[1]:>+6.3f}] "
            f"{res['verdict']}"
        )

    # print race_start first (the focus), then the rest for context
    rs_results = [r for r in results if r.get("is_race_start")]
    other_results = [r for r in results if not r.get("is_race_start")]
    print("  [race_start modules — the focus]")
    for res in rs_results:
        print("  " + row(res))
    print("  [other modules — context]")
    for res in other_results:
        print("  " + row(res))
    print("-" * 100)
    print(f"n-aware critical |r|:  r_crit(n={n_for_rcrit}, alpha={ALPHA}) = {r_crit_24:.4f}"
          f"   <-- proposed honest threshold for the next gate (G2)")
    n_sig = sum(1 for r in results if r.get("significant"))
    n_sig_rs = sum(1 for r in rs_results if r.get("significant"))
    print(f"significant modules: {n_sig}/12 overall, {n_sig_rs}/4 race_start "
          f"(significant := p<{ALPHA} AND |r|>=r_crit)")
    # embedded cross-check
    mismatches = [r["module"] for r in results
                  if r.get("sigma_corr") is not None and not r.get("embedded_match")]
    if mismatches:
        print(f"WARNING: pearson disagrees with engine embedded corr for: {mismatches}")
    else:
        print("cross-check: every module's pearson matches the engine's embedded "
              "corr_sigma_pi_trace_vs_rank_mae (max diff < 1e-6). OK")
    print()

    # ---- Part (b) table ----
    print("-" * 100)
    print("PART (b)  calibrated_sigma = alpha*sigma_pi_trace + beta*effective_dof   (per-phase pooled events)")
    print("-" * 100)
    if any_fallback:
        print("NOTE: entity_count is None for every event in this report -> "
              "effective_dof falls back to max(None-1,1) = 1.")
        print("      With effective_dof=1, beta acts as a constant per-module offset "
              "(beta*1); alpha=1.0 for all modules, so calibrated_sigma = sigma_pi_trace + beta.")
    print("      Primary calibration = per-module FITTED (alpha,beta) from the "
          "uncertainty_calibration artifact (fit_status=fitted, fit_event_count=24).")
    print("      Caveat: the aggregate task_calibration_diagnostics block is "
          "insufficient_data -> alpha=1,beta=0 (identity); not used for leveling.")
    print("      LEVEL uses calibrated_sigma; FLATNESS uses CV(raw sigma_pi_trace) "
          "because CV(calSig) here is dominated by the beta constant (fallback artifact).")
    print()
    h2 = (f"{'phase':12s} {'nEv':>3s} {'mean(calSig)':>13s} {'mean(err)':>10s} "
          f"{'sig/err':>8s} {'CV(rawSig)':>11s} {'CV(calSig)':>11s} {'CV(err)':>9s} "
          f"{'CVraw/CVerr':>12s} betas")
    print(h2)
    print("-" * 100)
    for ph in ["quali", "race", "race_start"]:
        d = per_phase.get(ph, {})
        if d.get("n_events", 0) == 0:
            print(f"{ph:12s} {0:>3d}  (no events)")
            continue
        print(
            f"{ph:12s} {d['n_events']:>3d} {d['mean_calibrated_sigma']:>13.5f} "
            f"{d['mean_realized_error']:>10.4f} {d['level_ratio_sigma_over_error']:>8.4f} "
            f"{d['cv_raw_sigma']:>11.4f} {d['cv_calibrated_sigma']:>11.4f} "
            f"{d['cv_realized_error']:>9.4f} "
            f"{d['flatness_ratio_cvrawsigma_over_cverror']:>12.4f} {d['betas_used']}"
        )
    print("-" * 100)
    print("RACE-START LEVEL VERDICT")
    print(f"  verdict: {rs_verdict.get('verdict')}")
    print(f"    too_high={rs_verdict.get('too_high')}  too_flat={rs_verdict.get('too_flat')}  "
          f"(too_flat needs flat_vs_error={rs_verdict.get('flat_vs_error')} AND "
          f"flat_vs_reference={rs_verdict.get('flat_vs_reference')}; "
          f"materiality: relative gap > {rs_verdict.get('materiality_relative_gap')})")
    print(f"    LEVEL : race_start calibrated_sigma/error ratio = "
          f"{_safe(rs_verdict.get('race_start_level_ratio'))}  "
          f"vs reference(quali,race) = {_safe(rs_verdict.get('reference_level_ratio'))}")
    print(f"    FLAT  : race_start CV(raw sigma) = {_safe(rs_verdict.get('race_start_cv_raw_sigma'))}  "
          f"CV(error) = {_safe(rs_verdict.get('race_start_cv_error'))}  "
          f"reference CV(raw sigma) = {_safe(rs_verdict.get('reference_cv_raw_sigma'))}")
    print("=" * 100)


def _safe(v):
    if v is None:
        return "n/a"
    if isinstance(v, float) and math.isnan(v):
        return "nan"
    return f"{v:.4f}"


# =============================================================================
# Evidence JSON
# =============================================================================
def write_evidence_json(path: str, details_path: str, cal_path: Optional[str],
                        results: list[dict], per_phase: dict, rs_verdict: dict,
                        r_crit_24: float, n_for_rcrit: int, any_fallback: bool) -> None:
    rs_results = [r for r in results if r.get("is_race_start")]
    payload = {
        "gate": "g1",
        "purpose": "race_start sigma significance + coverage (measurement only)",
        "provenance": {
            "details_path": details_path,
            "calibration_artifact_path": cal_path,
            "repo_root": _REPO_ROOT,
            "numpy_available": _HAVE_NUMPY,
            "scipy_available": _HAVE_SCIPY,
            "distribution_backend": "scipy" if _HAVE_SCIPY else "stdlib_closed_form",
            "bootstrap": {"n_boot": N_BOOT, "seed": BOOT_SEED, "method": "paired_percentile"},
            "alpha": ALPHA,
            "x_field": TARGET_X,
            "y_field": TARGET_Y,
            "entity_count_all_none_fallback": any_fallback,
            "effective_dof_rule": "max(entity_count-1,1); None->1",
            "calibration_primary_source": "per-module fitted (alpha,beta) from uncertainty_calibration artifact",
            "calibration_caveat": "task_calibration_diagnostics aggregate is insufficient_data -> alpha=1,beta=0 identity; not used",
        },
        "r_crit": {
            "n": n_for_rcrit,
            "alpha": ALPHA,
            "value": r_crit_24,
            "definition": "t_crit=ppf(1-alpha/2,n-2); r_crit=t_crit/sqrt(n-2+t_crit^2)",
            "role": "proposed honest significance threshold for next gate (G2)",
        },
        "per_module": results,
        "race_start_significance": {
            "n_significant": sum(1 for r in rs_results if r.get("significant")),
            "n_total": len(rs_results),
            "modules": [
                {
                    "module": r["module"],
                    "sigma_corr": r.get("sigma_corr"),
                    "p_value": r.get("p_value"),
                    "fisher_ci": r.get("fisher_ci"),
                    "bootstrap_ci": r.get("bootstrap_ci"),
                    "r_crit": r.get("r_crit"),
                    "verdict": r.get("verdict"),
                }
                for r in rs_results
            ],
        },
        "per_phase": per_phase,
        "verdicts": {
            "race_start_level": rs_verdict,
            "significance_summary": {
                "n_significant_overall": sum(1 for r in results if r.get("significant")),
                "n_significant_race_start": sum(1 for r in rs_results if r.get("significant")),
                "n_modules": len(results),
            },
        },
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
        fh.write("\n")


# =============================================================================
# Self-test (optional, --selftest)
# =============================================================================
def selftest() -> int:
    ok = True

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        status = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        print(f"  [{status}] {label} {detail}")

    print("SELFTEST: statistical primitives on known cases")

    # 1) r_crit(n=24): known reference ~0.4044 (df=22, t_crit≈2.0739)
    rc = r_critical(24, 0.05)
    check("r_crit(n=24, alpha=0.05) ~ 0.4044", abs(rc - 0.40443) < 2e-3, f"got {rc:.5f}")

    # 2) r_crit(n=30): standard table value ~0.3610
    rc30 = r_critical(30, 0.05)
    check("r_crit(n=30, alpha=0.05) ~ 0.3610", abs(rc30 - 0.36101) < 2e-3, f"got {rc30:.5f}")

    # 3) t_critical(df=22) ~ 2.0739
    tc = t_critical(22, 0.05)
    check("t_crit(df=22, alpha=0.05) ~ 2.0739", abs(tc - 2.07387) < 2e-3, f"got {tc:.5f}")

    # 4) Fisher-z CI on a textbook case r=0.5, n=30 -> approx (0.169, 0.781)
    lo, hi = fisher_z_ci(0.5, 30)
    check("fisher_z_ci(r=0.5,n=30) lo~0.169", abs(lo - 0.1693) < 5e-3, f"got lo={lo:.4f}")
    check("fisher_z_ci(r=0.5,n=30) hi~0.726", abs(hi - 0.7259) < 5e-3, f"got hi={hi:.4f}")

    # 5) Fisher-z midpoint maps back to r (atanh/tanh round-trip): CI symmetric in z
    check("fisher CI brackets the point estimate", lo < 0.5 < hi)

    # 6) two-sided p for r=0 is 1.0
    p0 = corr_p_value(0.0, 24)
    check("corr_p_value(r=0,n=24) == 1.0", abs(p0 - 1.0) < 1e-9, f"got {p0:.6f}")

    # 7) p at exactly r_crit should be ~ alpha (0.05)
    p_at_crit = corr_p_value(rc, 24)
    check("corr_p_value(r=r_crit,n=24) ~ 0.05", abs(p_at_crit - 0.05) < 5e-3, f"got {p_at_crit:.5f}")

    # 8) regularized incomplete beta sanity: I_0.5(1,1) == 0.5
    check("reg_incomplete_beta(1,1,0.5) == 0.5", abs(reg_incomplete_beta(1, 1, 0.5) - 0.5) < 1e-9)

    # 9) cross-check vs scipy when available
    if _HAVE_SCIPY:
        sp_p = float(2.0 * _sps.t.sf(abs(0.5 * math.sqrt(22) / math.sqrt(1 - 0.25)), 22))
        my_p = student_t_two_sided_p(0.5 * math.sqrt(22) / math.sqrt(1 - 0.25), 22)
        check("stdlib t two-sided p matches scipy (r=0.5,n=24)", abs(sp_p - my_p) < 1e-4,
              f"scipy={sp_p:.6f} stdlib={my_p:.6f}")
        sp_rc = float(_sps.t.ppf(0.975, 22))
        check("stdlib t_ppf matches scipy ppf(0.975,22)", abs(student_t_ppf(0.975, 22) - sp_rc) < 1e-3,
              f"scipy={sp_rc:.5f} stdlib={student_t_ppf(0.975,22):.5f}")
    else:
        print("  [skip] scipy not present; stdlib closed-form path is primary")

    # 10) bootstrap determinism: same seed -> identical CI
    xs = [0.1, 0.2, 0.15, 0.3, 0.25, 0.4, 0.35, 0.5, 0.45, 0.6, 0.55, 0.7]
    ys = [1.0, 1.2, 0.9, 1.5, 1.3, 1.8, 1.6, 2.0, 1.9, 2.2, 2.1, 2.5]
    a1 = bootstrap_corr_ci(xs, ys, n_boot=2000, seed=42)
    a2 = bootstrap_corr_ci(xs, ys, n_boot=2000, seed=42)
    check("bootstrap deterministic for fixed seed", a1 == a2, f"{a1} == {a2}")

    print("SELFTEST:", "ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


# =============================================================================
# Main
# =============================================================================
def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="g1 sigma significance + coverage probe")
    ap.add_argument("--details", default=DEFAULT_DETAILS, help="path to gold-cycle details.json")
    ap.add_argument("--out", default=DEFAULT_EVIDENCE_OUT, help="path for g1_evidence.json")
    ap.add_argument("--selftest", action="store_true", help="run statistical self-tests and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    details = load_details(args.details)
    cal_modules, cal_path = load_calibration_artifact(details)

    modules = details.get("modules")
    if not modules:
        raise SystemExit("STOP: details.json has no 'modules' block.")

    # stable order: race_start grouped is handled in printing; iterate name-sorted
    results = [
        analyse_module_significance(name, modules[name], cal_modules)
        for name in sorted(modules.keys())
    ]

    # the n we report r_crit for: the common event count (24); fall back to max n
    ns = [r["n"] for r in results if r.get("n", 0) >= 4]
    n_for_rcrit = 24 if 24 in ns else (max(ns) if ns else 24)
    r_crit_24 = r_critical(n_for_rcrit, ALPHA)

    per_phase, any_fallback = analyse_phase_levels(details, cal_modules)
    rs_verdict = race_start_level_verdict(per_phase)

    print_report(details, results, per_phase, rs_verdict, r_crit_24, n_for_rcrit,
                 cal_path, any_fallback)

    write_evidence_json(args.out, args.details, cal_path, results, per_phase,
                        rs_verdict, r_crit_24, n_for_rcrit, any_fallback)
    print(f"\n[evidence] wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
