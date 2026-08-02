# Implementer Handoff — Config C Parity Comparison

## Context
Issue #523 produced an honest-null result (all three views HOLD under the decoupled estimator). The Admiral identified a confound: the original comparison used smoothed trajectory speed (`s.speed`) as the frontier v-axis in the decoupled path, while the incumbent uses raw-sensor-interpolated speed from `spd_d["V"]`. This conflates two changes.

**Config C (parity)** isolates the `a_long` contribution: decoupled `a_long` + incumbent's raw `v_at`. The coast path is ALREADY parity (both use `car["Speed"]/3.6`); only Traction/PowerDrag need Config C.

## Task
Extend `scripts/characterize_decoupled_views.py` in worktree `C:\Programs\f1Brainz-509w3-views` to add Config C for TractionView and PowerDragView, run it on Belgium/Monaco/Bahrain 2023 Q RBR, and capture the table.

## Exact Changes

### 1. Update `FINDINGS_PATH` (line 39-41)

Change:
```python
FINDINGS_PATH = Path(
    r"C:\Programs\f1Brainz\.agent-work\523-decoupled-views\crew-handoffs\g1-characterization-table.md"
)
```

To:
```python
FINDINGS_PATH = Path(
    r"C:\Programs\f1Brainz\.agent-work\509-w3\crew-handoffs\cmdr-V-configC-table.md"
)
```

### 2. Add `run_parity_throttle` function after line 298 (`return traction, power_drag`), before the coast functions

This function is identical to `run_decoupled_throttle` EXCEPT for the v-axis source. Key difference: instead of line 230 `v_arr.append(s.speed)` (smoothed), use raw-sensor-interpolated v from `clean_longitudinal_from_raw`.

Insert this complete function after the `run_decoupled_throttle` function and before `run_incumbent_coast`:

```python
# ---------------------------------------------------------------------------
# Parity Traction + PowerDrag (Config C: decoupled a_long + incumbent raw v)
# ---------------------------------------------------------------------------

def run_parity_throttle(year, gp, drivers, session, rho, sample_cache):
    """Config C: decoupled a_long + incumbent's raw v_at from spd_d["V"].

    Isolates the a_long contribution from the v-source confound.
    Compares: incumbent (raw v + FD a_long) vs parity (raw v + decoupled a_long).
    Coast is already parity; this is only needed for throttle views.
    """
    from src.physics.layer2.session_braking import _driver_samples, _to_kinematic_samples
    from src.physics.layer2.decoupled_braking_input import (
        split_samples_by_lap, estimate_lap_longitudinal
    )
    from src.physics.layer2.braking_view import clean_longitudinal_from_raw
    from src.physics.terrain import build_terrain_profile
    from src.physics.layer2.traction_view import TractionView
    from src.physics.layer2.power_drag_view import PowerDragView
    from src.physics.layer2.frontier_fit import ridge_peak
    from src.physics.layer2.params import GaussianPrior2, ParamPrior
    from src.physics.constants import GRAVITY_MS2
    from src.physics.longitudinal_fit import MASS_KG

    _THETA_R0 = 0.15
    m = MASS_KG

    # Build pooled terrain profile (same as run_decoupled_throttle)
    all_xyz_pool: list = []
    for drv in drivers:
        out = _driver_samples(session, drv, refine=False, cache=sample_cache)
        if out is None:
            continue
        _, _, xyz, _ = out
        all_xyz_pool.extend(xyz)

    profile = None
    if len(all_xyz_pool) >= 3:
        try:
            profile = build_terrain_profile(all_xyz_pool, min_laps=3)
        except Exception as e:
            print(f"  [terrain parity] build_terrain_profile failed: {e}; using flat fallback")

    v_parts, al_parts, sk_parts, th_parts, drs_parts = [], [], [], [], []
    used: list[str] = []

    for drv in drivers:
        out = _driver_samples(session, drv, refine=False, cache=sample_cache)
        if out is None:
            print(f"  [parity skip {drv}] no driver samples")
            continue
        processed, control, xyz, spd_d = out
        samples = _to_kinematic_samples(processed, control)
        if not samples:
            print(f"  [parity skip {drv}] no kinematic samples")
            continue

        lap_numbers = (
            processed["lap_number"].to_numpy()
            if "lap_number" in processed.columns
            else np.zeros(len(samples), dtype=int)
        )

        # Run decoupled estimator per lap (same as Config B)
        ts_to_adc: dict[int, tuple[float, float, float]] = {}
        for i, j in split_samples_by_lap(samples, lap_numbers):
            lap_samps = samples[i:j]
            try:
                a_long_lap, _fv, sigma_a_lap, theta_lap, _regime, _flat = \
                    estimate_lap_longitudinal(lap_samps, spd_d, profile)
            except Exception as e:
                print(f"  [parity skip lap {lap_numbers[i]} drv={drv}] estimate_lap_longitudinal: {e}")
                continue
            for k, s in enumerate(lap_samps):
                ts_to_adc[s.timestamp_ms] = (float(a_long_lap[k]), float(sigma_a_lap[k]),
                                              float(theta_lap[k]))

        # Extract throttle-on samples
        cand = [s for s in samples if s.regime in _TRACTION_REGIMES]
        if not cand:
            print(f"  [parity skip {drv}] no throttle-on samples")
            continue

        # === CONFIG C: get raw-sensor v at sample timestamps (incumbent v-axis) ===
        t_s = np.array([s.timestamp_ms / 1000.0 for s in cand])
        v_raw_at_ts, _, _ = clean_longitudinal_from_raw(spd_d["t"], spd_d["V"], t_s)

        # Get decoupled a_long from lookup; use raw v for v-axis
        a_long_arr, sigma_arr, theta_arr, v_arr = [], [], [], []
        skipped_ts = 0
        for idx, s in enumerate(cand):
            if s.timestamp_ms not in ts_to_adc:
                skipped_ts += 1
                continue
            al, sig, th = ts_to_adc[s.timestamp_ms]
            a_long_arr.append(al)
            sigma_arr.append(sig)
            theta_arr.append(th)
            v_arr.append(float(v_raw_at_ts[idx]))  # RAW v, not s.speed

        if skipped_ts:
            print(f"  [parity {drv}] {skipped_ts} throttle samples missing from decoupled lookup")

        if len(a_long_arr) < 10:
            print(f"  [parity skip {drv}] too few parity throttle-on samples ({len(a_long_arr)})")
            continue

        a_long_arr = np.array(a_long_arr)
        sigma_arr = np.array(sigma_arr)
        theta_arr = np.array(theta_arr)
        v_arr = np.array(v_arr)

        # DRS from control df (same logic as run_decoupled_throttle)
        ct = control["session_time_ms"].to_numpy(dtype=float)
        cd = control["drs"].to_numpy(dtype=float) if "drs" in control.columns else np.zeros(len(ct))
        sm = np.array([s.timestamp_ms for s in cand if s.timestamp_ms in ts_to_adc], dtype=float)
        j_idx = np.clip(np.searchsorted(ct, sm, side="right") - 1, 0, len(ct) - 1)
        drs_open = cd[j_idx] >= 10.0

        v_parts.append(v_arr)
        al_parts.append(a_long_arr)
        sk_parts.append(sigma_arr)
        th_parts.append(theta_arr)
        drs_parts.append(drs_open)
        used.append(drv)

    if not v_parts:
        raise RuntimeError(f"no parity throttle samples at {gp} {year}")

    v_all = np.concatenate(v_parts)
    a_long_all = np.concatenate(al_parts)
    sigma_all = np.concatenate(sk_parts)
    theta_all = np.concatenate(th_parts)
    drs_all = np.concatenate(drs_parts)

    # Physical glitch rejection (same ceiling as run_decoupled_throttle)
    from src.physics.constants import GRAVITY_MS2 as _G
    _ACCEL_CEILING = 3.5 * _G
    keep = a_long_all < _ACCEL_CEILING
    v_all = v_all[keep]; a_long_all = a_long_all[keep]
    sigma_all = sigma_all[keep]; theta_all = theta_all[keep]; drs_all = drs_all[keep]

    if v_all.size < 20:
        raise RuntimeError(f"too few parity throttle samples after cleaning ({v_all.size}) at {gp}")

    # Fit views (same structure as run_decoupled_throttle)
    theta_R = ParamPrior(_THETA_R0, 0.30)
    acc = a_long_all > 0.0
    if int(acc.sum()) < 20:
        raise RuntimeError(f"too few parity accelerating samples at {gp}")
    y_raw = a_long_all[acc] + theta_R.mu + GRAVITY_MS2 * np.sin(theta_all[acc])
    cross = ridge_peak(v_all[acc], y_raw)

    power_drag = PowerDragView.fit(
        v_all, a_long_all, theta_all, drs_all,
        theta_R=theta_R, mass_kg=MASS_KG, rho=rho,
        prior=GaussianPrior2.cold(), v_crossover=cross,
    )
    cda_prior = (power_drag.cda_prior_closed if power_drag is not None
                 else ParamPrior(1.2, 0.5 * 1.2))
    traction = TractionView.fit(
        v_all, a_long_all, sigma_all, theta_all,
        cda=cda_prior, theta_R=theta_R, mass_kg=MASS_KG, rho=rho,
        prior=GaussianPrior2.cold(), v_crossover=cross,
    )
    return traction, power_drag
```

### 3. Update `main()` to call `run_parity_throttle`

After the decoupled throttle block (after the except block that ends around line 674), add this block:

```python
        try:
            print(f"  Running parity throttle views (Config C: decoupled a_long + raw v)...")
            traction_par, pd_par = run_parity_throttle(
                year, gp, drivers, session, rho, sample_cache
            )
            if traction_par is not None:
                print(f"  Parity TractionView: a_t={traction_par.traction_accel_ms2:.3f} "
                      f"b_t={traction_par.traction_aero_accel_per_m:.5f} "
                      f"n={traction_par.n_samples}")
                sig_at = float(np.sqrt(max(traction_par.covariance[0, 0], 0.0)))
                sig_bt = float(np.sqrt(max(traction_par.covariance[1, 1], 0.0)))
                traction_rows.append(TractionRow(
                    circuit=gp, path="parity",
                    traction_accel_ms2=traction_par.traction_accel_ms2,
                    sigma_traction_accel=sig_at,
                    traction_aero_accel_per_m=traction_par.traction_aero_accel_per_m,
                    sigma_traction_aero=sig_bt,
                    n_samples=traction_par.n_samples,
                ))
            else:
                traction_rows.append(TractionRow(
                    circuit=gp, path="parity",
                    traction_accel_ms2=float("nan"), sigma_traction_accel=float("nan"),
                    traction_aero_accel_per_m=float("nan"), sigma_traction_aero=float("nan"),
                    n_samples=0, note="TractionView returned None"
                ))

            if pd_par is not None:
                print(f"  Parity PowerDragView: P_max={pd_par.max_power_w/1e6:.3f} MW "
                      f"CdA={pd_par.drag_area_closed_m2:.4f} n_closed={pd_par.n_closed}")
                sig_p = float(np.sqrt(max(pd_par.covariance[0, 0], 0.0)))
                sig_c = float(np.sqrt(max(pd_par.covariance[1, 1], 0.0)))
                pd_rows.append(PowerDragRow(
                    circuit=gp, path="parity",
                    max_power_w=pd_par.max_power_w,
                    sigma_max_power=sig_p,
                    drag_area_closed_m2=pd_par.drag_area_closed_m2,
                    sigma_drag_area=sig_c,
                    degenerate=pd_par.degenerate,
                    n_closed=pd_par.n_closed,
                ))
            else:
                pd_rows.append(PowerDragRow(
                    circuit=gp, path="parity",
                    max_power_w=float("nan"), sigma_max_power=float("nan"),
                    drag_area_closed_m2=float("nan"), sigma_drag_area=float("nan"),
                    degenerate=False, n_closed=0, note="PowerDragView returned None"
                ))
        except Exception as e:
            print(f"  [ERROR] parity throttle: {e}")
            traceback.print_exc()
            traction_rows.append(TractionRow(
                circuit=gp, path="parity",
                traction_accel_ms2=float("nan"), sigma_traction_accel=float("nan"),
                traction_aero_accel_per_m=float("nan"), sigma_traction_aero=float("nan"),
                n_samples=0, note=f"ERROR: {e}"
            ))
            pd_rows.append(PowerDragRow(
                circuit=gp, path="parity",
                max_power_w=float("nan"), sigma_max_power=float("nan"),
                drag_area_closed_m2=float("nan"), sigma_drag_area=float("nan"),
                degenerate=False, n_closed=0, note=f"ERROR: {e}"
            ))
```

### 4. Update `build_findings_markdown` to show Config C shifts

In the Traction shift table (around line 793-812), update to show BOTH the confounded (B) and parity (C) shifts:

Replace the existing shift table header + loop with:
```python
    lines.append("")
    lines.append("**Shift table (Traction) — Config B = confounded (smoothed v); Config C = parity (raw v + decoupled a_long)**")
    lines.append("")
    lines.append("| Circuit | Config | delta `traction_accel_ms2` | d/sigma | delta `traction_aero_accel_per_m` | d/sigma |")
    lines.append("|---------|--------|---------------------------|---------|-----------------------------------|---------|")
    circuits = list(dict.fromkeys(r.circuit for r in traction_rows))
    for circ in circuits:
        inc_rows = [r for r in traction_rows if r.circuit == circ and r.path == "incumbent"]
        if not inc_rows:
            continue
        inc = inc_rows[0]
        for config_label, path_name in [("B (confounded)", "decoupled"), ("C (parity)", "parity")]:
            other_rows = [r for r in traction_rows if r.circuit == circ and r.path == path_name]
            if not other_rows:
                lines.append(f"| {circ} | {config_label} | — | — | — | — |")
                continue
            other = other_rows[0]
            d_at, r_at = _shift_sigma(inc.traction_accel_ms2, other.traction_accel_ms2, inc.sigma_traction_accel)
            d_bt, r_bt = _shift_sigma(inc.traction_aero_accel_per_m, other.traction_aero_accel_per_m, inc.sigma_traction_aero)
            def fmt(x):
                return f"{x:+.4f}" if not np.isnan(x) else "n/a"
            def fmt6(x):
                return f"{x:+.6f}" if not np.isnan(x) else "n/a"
            lines.append(
                f"| {circ} | {config_label} | {fmt(d_at)} | {fmt(r_at)} | {fmt6(d_bt)} | {fmt(r_bt)} |"
            )
```

Similarly update the PowerDrag shift table to show both Config B and Config C:
```python
    lines.append("")
    lines.append("**Shift table (PowerDrag) — Config B = confounded; Config C = parity**")
    lines.append("")
    lines.append("| Circuit | Config | delta `max_power_w` (W) | d/sigma | delta `drag_area_closed_m2` | d/sigma |")
    lines.append("|---------|--------|-------------------------|---------|------------------------------|---------|")
    for circ in circuits:
        inc_rows = [r for r in pd_rows if r.circuit == circ and r.path == "incumbent"]
        if not inc_rows:
            continue
        inc = inc_rows[0]
        for config_label, path_name in [("B (confounded)", "decoupled"), ("C (parity)", "parity")]:
            other_rows = [r for r in pd_rows if r.circuit == circ and r.path == path_name]
            if not other_rows:
                lines.append(f"| {circ} | {config_label} | — | — | — | — |")
                continue
            other = other_rows[0]
            d_p, r_p = _shift_sigma(inc.max_power_w, other.max_power_w, inc.sigma_max_power)
            d_c, r_c = _shift_sigma(inc.drag_area_closed_m2, other.drag_area_closed_m2, inc.sigma_drag_area)
            def fmt(x):
                return f"{x:+.1f}" if not np.isnan(x) else "n/a"
            def fmt4(x):
                return f"{x:+.4f}" if not np.isnan(x) else "n/a"
            lines.append(
                f"| {circ} | {config_label} | {fmt(d_p)} | {fmt4(r_p)} | {fmt4(d_c)} | {fmt4(r_c)} |"
            )
```

For the Coast section, add a note that coast is already parity:
After the coast shift table entries, add:
```python
    lines.append("")
    lines.append("**Note on CoastView:** Coast uses raw CAN bus speed (`car[\"Speed\"]/3.6`) in BOTH the incumbent and decoupled paths. The decoupled coast comparison is already a parity (Config C) comparison — the v-axis is identical. The observed coast shifts (1.5-3.4σ, 23-33% sample loss) are from `a_long` alone, not the v-source confound.")
```

### 5. Update Notes section at the end

Add to the notes:
```python
    lines.append("- Config C (parity): decoupled a_long + incumbent's raw v_at from spd_d['V'] (throttle views only)")
    lines.append("- Coast path: both configs use raw car_data Speed (parity by construction)")
```

## Stop Conditions
- Stop if any import fails — return partial result with what ran
- Do NOT modify any src/ production files
- Do NOT touch `FINDINGS_PATH` directory creation if it already exists

## Allowed Scope
- EDIT: `C:\Programs\f1Brainz-509w3-views\scripts\characterize_decoupled_views.py`
- RUN: the updated script: `py scripts/characterize_decoupled_views.py` from worktree root
- WRITE: `C:\Programs\f1Brainz\.agent-work\509-w3\crew-handoffs\cmdr-V-configC-table.md` (the script writes this)

## Constraints
- Worktree: `C:\Programs\f1Brainz-509w3-views`; data at `C:\Programs\f1Brainz\data\`
- `py` not `python`
- No production src/ edits

## Required Evidence
- `cmdr-V-configC-table.md` contents (copy the table verbatim into the result)
- Stdout confirmation that Config C ran successfully (not just fell back to errors)
- No production files modified

## Return Format
Return IMPLEMENTER_RESULT:
```markdown
# IMPLEMENTER_RESULT — Config C Parity

## Status
DONE / PARTIAL / ERROR

## Files Changed
- scripts/characterize_decoupled_views.py

## Config C Table (verbatim from output)
[paste the full table here]

## Key observations
[any important notes from the run]
```

Write to: `C:\Programs\f1Brainz\.agent-work\509-w3\crew-handoffs\configC-implementer-result.md`
