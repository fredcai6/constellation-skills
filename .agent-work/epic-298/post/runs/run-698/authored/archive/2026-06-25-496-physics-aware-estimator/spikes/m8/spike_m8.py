"""M8 spike v2: semi-parametric onset mean function for trajectory filter rebuild (#496/#507).

THESIS
------
A smoothness prior cannot represent a sharp step without either rounding it (braking
knee) or ringing (short straights). M8 removes the step from what the smoother must
represent: model each brake-onset with a parametric mean function (sigmoid keyed to the
brake-apply transition time), fit to RAW a_long only, then compose with the Gaussian
smoother for the residual. The sharp step lives in the mean; the Kalman/RTS never has
to represent it.

v2 CHANGES (after failure analysis)
-------------------------------------
Key finding from v1: the window post-onset extends into corner/throttle recovery, so
a_post estimation was contaminated (saw +65 depth when braking events are SHORT 0.1-1s).
With 18 brake samples across 6 events and 4 Hz data, each event has 1-4 samples.

REVISED APPROACH:
- Use a_post estimated from THE BRAKING REGIME SAMPLES ONLY (not the tail of the window)
- The sigmoid fit window: t_win_start to t_win_end where t_win_end = t_brake_end (NOT +1.2s)
- The composition: replace Gaussian a_long in braking regions with the mean function
  ONLY where the mean is DEEPER than the Gaussian (i.e., only when the mean adds
  depth, not when it adds spurious positive accel)
- Cap the blend so it never creates MORE positive a_long than the Gaussian baseline

OPERATING SPACE
---------------
Direct a_long output composition. The sigmoid fits the transition from pre-brake (corner
decel) to braking plateau (deeper decel). We composite in output space, preserving the
Gaussian as a floor for ringing.

INVARIANT NOTE
--------------
The mean is fit from RAW a_long only (external, un-biased of smoothed trajectory).
Extends decision:two_cycle_external_anchor_design (raw-only source) via a structurally
different mechanism: MEAN-DECOMPOSITION rather than Kalman update.
"""
from __future__ import annotations

import sys
_MAIN = "C:/Programs/f1Brainz"
if _MAIN not in sys.path:
    sys.path.insert(0, _MAIN)

import numpy as np
from scipy.optimize import curve_fit

from src.physics.layer2.scoreboard import CaseInputs, _long_accel


# ---------------------------------------------------------------------------
# Sigmoid onset shape
# ---------------------------------------------------------------------------

def _sigmoid(t: np.ndarray, t0: float, k: float, depth: float, offset: float) -> np.ndarray:
    """Logistic sigmoid in a_long space (signed m/s²; decel negative).

    shape: offset + depth / (1 + exp(-k*(t - t0)))
    For braking: depth < 0 (deeper decel onset), offset = pre-brake a_long level.
    """
    z = np.clip(-k * (t - t0), -200, 200)
    return offset + depth / (1.0 + np.exp(z))


def fit_onset_sigmoid(
    t_win: np.ndarray,
    a_win: np.ndarray,
    t_onset: float,
    a_pre: float,
    a_post: float,
) -> tuple[np.ndarray | None, dict]:
    """Fit a sigmoid to a braking-onset window of raw a_long.

    Uses externally-supplied a_pre and a_post (estimated from regime-aware samples,
    not from the window tails) to initialize the sigmoid parameters correctly.

    Parameters
    ----------
    t_win    : time array for the window (s)
    a_win    : raw a_long in the window (m/s², signed; decel negative)
    t_onset  : estimated onset time (regime transition time)
    a_pre    : pre-brake a_long level (estimated from pre-onset samples)
    a_post   : braking plateau a_long (estimated from brake-regime samples)

    Returns (params, info) where params = (t0, k, depth, offset) or None on failure.
    """
    if len(t_win) < 4:
        return None, {"reason": f"too few samples in window ({len(t_win)})"}

    depth_init = a_post - a_pre   # typically negative (deeper decel during braking)
    offset_init = a_pre

    # k: steepness — estimate from transition width (~0.1-0.3s onset time)
    t_range = float(t_win[-1] - t_win[0])
    k_init = 4.0 / max(t_range * 0.25, 0.05)

    p0 = [t_onset, k_init, depth_init, offset_init]

    t_lo = float(t_win[0]) - 0.1  # allow t0 slightly outside window
    t_hi = float(t_win[-1]) + 0.1
    # Depth: allow any direction but constrain to physically reasonable range
    d_lo = min(depth_init * 2.0, -200.0) if depth_init < 0 else -200.0
    d_hi = max(depth_init * 2.0, 200.0) if depth_init > 0 else 200.0
    bounds = (
        [t_lo, 0.5,  d_lo, -150.0],
        [t_hi, 500.0, d_hi,  150.0],
    )

    try:
        popt, _ = curve_fit(
            _sigmoid, t_win, a_win, p0=p0, bounds=bounds,
            maxfev=3000, ftol=1e-6, xtol=1e-6,
        )
        a_pred = _sigmoid(t_win, *popt)
        residual_rms = float(np.sqrt(np.mean((a_win - a_pred) ** 2)))
        quality = "clean" if residual_rms < 3.0 else "poor"
        return popt, {"residual_rms": residual_rms, "quality": quality}
    except (RuntimeError, ValueError) as e:
        return None, {"reason": str(e)}


# ---------------------------------------------------------------------------
# Detect braking onsets
# ---------------------------------------------------------------------------

def detect_braking_onsets(
    t: np.ndarray,
    regime: np.ndarray,
) -> list[dict]:
    """Return list of onset dicts for each straight_brake entry point."""
    onsets = []
    for i in range(1, len(regime)):
        if regime[i] == "straight_brake" and regime[i - 1] != "straight_brake":
            onsets.append({"idx": i, "t_onset": float(t[i])})
    return onsets


# ---------------------------------------------------------------------------
# Build mean + blend
# ---------------------------------------------------------------------------

def build_mean_and_blend(
    t: np.ndarray,
    regime: np.ndarray,
    a_long_raw: np.ndarray,
    *,
    pre_window_s: float = 0.5,
    min_brake_samples: int = 2,
) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """Fit a sigmoid to each braking onset; return mean m(t), blend weight, and reports.

    KEY FIX (v2): a_post is estimated from BRAKING REGIME SAMPLES ONLY, not window tail.
    The window end is set to t_brake_end (not extended into recovery), so the sigmoid
    captures only the onset-to-plateau transition.

    Returns
    -------
    m      : (len(t),) — parametric mean a_long in m/s² (zero outside onset windows)
    blend  : (len(t),) — [0,1] blend weight (1 = use mean, 0 = use Gaussian)
    reports: list of per-onset dicts (fit params, quality, window)
    """
    m = np.zeros(len(t), dtype=float)
    blend = np.zeros(len(t), dtype=float)
    onset_reports = []
    onsets = detect_braking_onsets(t, regime)

    for onset in onsets:
        idx_onset = onset["idx"]
        t_onset = onset["t_onset"]

        # Find the end of this braking phase (contiguous straight_brake run)
        j = idx_onset
        while j < len(regime) - 1 and regime[j] == "straight_brake":
            j += 1
        idx_brake_end = j - 1
        t_brake_end = float(t[idx_brake_end])
        brake_dur = t_brake_end - t_onset

        # Get braking plateau samples
        brake_mask_event = (t >= t_onset) & (t <= t_brake_end) & (regime == "straight_brake")
        n_brake_samples = int(brake_mask_event.sum())

        if n_brake_samples < min_brake_samples:
            onset_reports.append({
                "t_onset": t_onset,
                "quality": "skipped_too_few_brake_samples",
                "n_brake_samples": n_brake_samples,
            })
            continue

        # Pre-onset: samples just before onset (up to pre_window_s before)
        pre_mask = (t >= t_onset - pre_window_s) & (t < t_onset) & (regime != "straight_brake")
        if pre_mask.sum() == 0:
            # Fallback: use the first few non-brake samples in the window
            pre_mask = (t >= t_onset - pre_window_s) & (t < t_onset)

        if pre_mask.sum() > 0:
            a_pre = float(np.median(a_long_raw[pre_mask]))
        else:
            # No pre-onset samples in window; use first sample of window
            a_pre = float(a_long_raw[idx_onset - 1]) if idx_onset > 0 else 0.0

        a_post = float(np.median(a_long_raw[brake_mask_event]))

        depth_estimate = a_post - a_pre
        # depth SHOULD be negative for braking (deeper decel)
        # If depth is positive, the braking plateau is LESS decel than pre-onset (e.g. corner->straight)
        # This happens in slow-corner braking where the entry is from a higher-decel state.
        # In that case, the M8 mean should NOT amplify the knee — skip.
        if depth_estimate >= 0:
            onset_reports.append({
                "t_onset": t_onset,
                "quality": "skipped_positive_depth",
                "depth_estimate": depth_estimate,
                "a_pre": a_pre,
                "a_post": a_post,
            })
            continue

        # Build fit window: pre_onset region + braking region only (NOT recovery)
        t_win_start = t_onset - pre_window_s
        t_win_end = t_brake_end
        win_mask = (t >= t_win_start) & (t <= t_win_end)

        if win_mask.sum() < 4:
            onset_reports.append({
                "t_onset": t_onset,
                "quality": "skipped_few_samples_in_window",
                "n_samples": int(win_mask.sum()),
            })
            continue

        t_win = t[win_mask]
        a_win = a_long_raw[win_mask]

        params, info = fit_onset_sigmoid(t_win, a_win, t_onset, a_pre, a_post)
        if params is None:
            onset_reports.append({
                "t_onset": t_onset,
                "quality": "fit_failed",
                "reason": info.get("reason", "unknown"),
                "n_win_samples": int(win_mask.sum()),
            })
            continue

        t0, k, depth, offset = params

        # Build sigmoid mean at ALL times
        sigmoid_vals = _sigmoid(t, t0, k, depth, offset)

        # Mean contribution relative to pre-onset baseline:
        # m_contrib(t) = sigmoid(t) - offset
        # = 0 before onset (where sigmoid ~ offset)
        # = depth at braking plateau (where sigmoid ~ offset + depth)
        m_contrib = sigmoid_vals - offset

        # Build blend weight: ramp up approaching onset, hold at 1 through braking, taper off
        blend_i = np.zeros(len(t))

        # Ramp up: from t_win_start to t_onset
        ramp_up_mask = (t >= t_win_start) & (t <= t_onset)
        if ramp_up_mask.any():
            t_ramp = t[ramp_up_mask]
            blend_i[ramp_up_mask] = np.clip(
                (t_ramp - t_win_start) / max(pre_window_s, 1e-6), 0, 1
            )

        # Plateau: full weight through the braking region
        plateau_mask = (t > t_onset) & (t <= t_brake_end) & (regime == "straight_brake")
        blend_i[plateau_mask] = 1.0

        # Accumulate
        m += blend_i * m_contrib
        blend = np.maximum(blend, blend_i)

        onset_reports.append({
            "t_onset": t_onset,
            "brake_dur_s": brake_dur,
            "n_brake_samples": n_brake_samples,
            "n_win_samples": int(win_mask.sum()),
            "a_pre": a_pre,
            "a_post": a_post,
            "depth_estimate": depth_estimate,
            "params": {
                "t0": float(t0), "k": float(k),
                "depth": float(depth), "offset": float(offset),
            },
            "quality": info.get("quality", "unknown"),
            "residual_rms": info.get("residual_rms"),
        })

    return m, blend, onset_reports


# ---------------------------------------------------------------------------
# M8 variant function (VariantFn seam)
# ---------------------------------------------------------------------------

def variant_m8(inp: CaseInputs) -> np.ndarray:
    """M8 variant v2: semi-parametric onset mean function + Gaussian residual smoother.

    Mechanism:
    1. Run Gaussian smoother on raw inputs -> a_long_gauss(t).
    2. Fit parametric sigmoid mean m(t) to raw a_long at each braking onset.
       Key: a_post estimated from BRAKE REGIME samples only; skip if depth >= 0.
    3. Compose safely:
       a_long_m8 = min(a_long_gauss, a_long_gauss*(1-blend) + (a_long_gauss + m)*blend)
       The min() ensures M8 can only DEEPEN the knee (add more decel), never add spurious
       positive accel above the Gaussian baseline.
    """
    # Step 1: Gaussian smoother baseline
    sm_gauss = inp.make_smoother(nu_proc=None)
    sm_gauss.fit(inp.t, inp.x, inp.y, inp.t, inp.v)
    a_long_gauss = _long_accel(sm_gauss, inp.t)

    # Step 2: Build parametric mean + blend
    m, blend, _onset_reports = build_mean_and_blend(
        inp.t, inp.regime, inp.a_long_raw,
        pre_window_s=0.5, min_brake_samples=2,
    )

    # Step 3: Compose with safety constraint
    # The mean contribution m(t) is negative at brake onset (deeper decel)
    # Adding m to a_long_gauss should only deepen (make more negative) at braking onsets
    a_long_candidate = a_long_gauss * (1.0 - blend) + (a_long_gauss + m) * blend
    # Safety: m8 can only deepen the knee (more negative), never add ringing
    # Take min (more negative = deeper decel) where blend > 0
    a_long_m8 = np.where(blend > 0.01,
                         np.minimum(a_long_gauss, a_long_candidate),
                         a_long_gauss)

    return a_long_m8


def variant_m8_diagnostic(inp: CaseInputs) -> tuple[np.ndarray, list[dict]]:
    """Same as variant_m8 but returns onset_reports for diagnosis."""
    sm_gauss = inp.make_smoother(nu_proc=None)
    sm_gauss.fit(inp.t, inp.x, inp.y, inp.t, inp.v)
    a_long_gauss = _long_accel(sm_gauss, inp.t)
    m, blend, onset_reports = build_mean_and_blend(
        inp.t, inp.regime, inp.a_long_raw,
        pre_window_s=0.5, min_brake_samples=2,
    )
    a_long_candidate = a_long_gauss * (1.0 - blend) + (a_long_gauss + m) * blend
    a_long_m8 = np.where(blend > 0.01,
                         np.minimum(a_long_gauss, a_long_candidate),
                         a_long_gauss)
    return a_long_m8, onset_reports
