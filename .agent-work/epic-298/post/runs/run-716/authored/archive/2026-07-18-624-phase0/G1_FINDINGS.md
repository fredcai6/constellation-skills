# G1 findings — correlation screen (Phase-0 probe, informational)

**Status:** INFORMATIONAL. This is a Phase-0 probe per Pre-Ruling #1 / critic disposition F7 — not a
go/no-go gate, not the ~0.80 ceiling answer (that is G1 in Phase 7). The pre-registered primary axis and
the recent-history-baseline construction were frozen in `PRE_REGISTRATION.md` (2026-07-18T01:39:24Z)
before this script existed and were not altered after seeing any number.

Reproduced by: `py scripts/g1_correlation_screen.py` (full run) and `py scripts/g1_correlation_screen.py
--check` (headline-reproduction check) from `C:/Programs/f1-624`.

<!-- machine-parseable line consumed by scripts/g1_correlation_screen.py --check; do not reword -->
HEADLINE: axis=lateral_total_grip_g pearson_r=-0.092306 n=2923

## Method recap

- `actual_pace_gap(year, round, driver)` = `(best_Q_lap − field_median) / field_median` for that round,
  computed directly from `lap_times`/`sessions` (season DBs), using the identical formula to the live
  recent-history feature's `compute_pace_gaps` (`src/evo_predictor/quali_pace_gap_history.py`) —
  reimplemented against raw SQL in the script rather than imported, both to stay a self-contained
  pure-DB/pandas artifact and to avoid the worktree editable-install `.pth` trap (a bespoke script's
  `import src.*` in this worktree can silently resolve to the MAIN checkout's `src/`, not this
  worktree's — see project memory `editable-install-pth-worktree-trap`).
- `recent_history_baseline(year, round, driver)` = trailing mean of that driver's own `actual_pace_gap`
  over strictly prior rounds, **reset each season** (matches `build_quali_pace_gap_history`'s per-season
  prior-rounds construction — the literal existing recent-history feature named in
  `PROBLEM_STATEMENT.md`'s "Gap resolution"). A driver's first round of a season has no history and is
  dropped (175 rows dropped this way, see Row counts below).
- `quali_error = actual_pace_gap − recent_history_baseline`. This **is** the semi-partial residual by
  construction — no separate OLS-against-a-feature-vector step is needed, because the residualization
  IS the recent-history feature itself (per `PROBLEM_STATEMENT.md`'s gap-resolution rationale).
- **Broadcast simplification (documented, not an error):** `session_estimates` is per
  `(year, gp_name, session_type='Q', constructor)`, not per-driver. Each constructor's physics axis
  values for a given (year, round) are broadcast onto **both** of that constructor's drivers that
  weekend. This means the two teammates in a session share identical physics-axis inputs even though
  their actual quali_error can differ — the probe measures whether the *team-level* physics axis
  predicts the *driver-level* residual, which dilutes any true signal relative to a hypothetical
  per-driver physics estimate. A null or weak result here is consistent with this dilution, not
  necessarily "no physics signal."
- Constructor-name reconciliation: `session_estimates.constructor` and
  `session_classifications.team` disagree in spelling across seasons/rebrands (e.g. "Red Bull" vs
  "Red Bull Racing"; "RB F1 Team" vs "RB" vs "Racing Bulls" post-2025-rebrand; "Alfa Romeo" vs
  "Alfa Romeo Racing" vs "Kick Sauber" depending on year). Resolved per-year via normalize + exact +
  substring-containment matching, with one explicit rebrand alias (`rb` → `racing bulls`, 2025 only).
  Verified live against all years 2019–2026 before the script was finalized: **zero unresolved or
  ambiguous team names** across all 8 seasons (confirmed again by the `--check` postcondition run: 0
  team→constructor unresolved).
- Primary axis (frozen, pre-registered): `lateral_total_grip_g = lateral_mech_grip_g + lateral_aero_grip_g`.
- Secondary axes (exploratory, never headline): the other 9 raw `session_estimates` columns, plus
  `power_to_drag = max_power_w / drag_area_closed_m2`.
- Statistics: Pearson r and Spearman rho, both with n and a 95% CI via Fisher z-transform (`atanh`/`tanh`,
  1.96 SE; the same approximation applied to Spearman's rho, labeled accordingly — it is only exact for
  Pearson under bivariate normality, treated as approximate for rho).

## Row counts (join stages)

| stage | n |
|---|---|
| raw `session_estimates` Q rows (constructor-level, all 11-axis fits) | 1597 |
| driver-round `quali_error` rows before physics join (after dropping 175 no-prior-history rows) | 2985 |
| team → constructor unresolved (excluded from join attempt) | 0 |
| rows after physics join (final analysis pool, pre axis-specific NaN drop) | 2985 |
| primary-axis (`lateral_total_grip_g`) rows after dropping axis-NaN (fit failures/degenerate) | 2923 |

Per-axis n varies from 2767–2923 depending on how often that axis's underlying physics fit failed/was
degenerate for a given constructor-session (see full table below) — this is NOT additional row loss from
the join, it is `axis_stats` dropping NaN axis values per-axis before correlating.

## Primary result (pre-registered, headline)

`lateral_total_grip_g` vs `quali_error`:

- **n = 2923**
- **Pearson r = −0.0923**, 95% CI **[−0.1281, −0.0562]**
- **Spearman rho = +0.0135**, 95% CI **[−0.0228, +0.0497]**

Sign convention check: `PRE_REGISTRATION.md` predicted `corr(lateral_total_grip_g, quali_error) < 0` if
physics carries usable signal (higher grip → smaller/more-negative pace gap → more-negative quali_error
once recent-history is subtracted out). The Pearson result matches that predicted sign and its 95% CI
excludes zero — a real, if small, linear association. The Spearman result is essentially zero and its CI
straddles zero, and its sign does not match the Pearson result's — the relationship is not monotonic
in a rank sense, consistent with a small, noisy, possibly non-linear or outlier-driven linear effect
rather than a clean, robust ordinal one.

## Full axis table (11 raw axes + composite; secondary/exploratory, never headline)

```
lateral_total_grip_g (PRIMARY) n=2923  pearson_r=-0.0923 [-0.1281, -0.0562]  spearman_rho=+0.0135 [-0.0228, +0.0497]

drag_area_closed_m2       n=2767  pearson_r=+0.0069 [-0.0304, +0.0441]  spearman_rho=-0.0001 [-0.0374, +0.0372]
brake_decel_ms2           n=2923  pearson_r=-0.0646 [-0.1006, -0.0284]  spearman_rho=-0.0102 [-0.0464, +0.0261]
brake_aero_decel_per_m    n=2923  pearson_r=-0.0026 [-0.0388, +0.0337]  spearman_rho=+0.0037 [-0.0325, +0.0400]
traction_accel_ms2        n=2923  pearson_r=-0.0017 [-0.0380, +0.0345]  spearman_rho=-0.0144 [-0.0506, +0.0219]
traction_aero_accel_per_m n=2923  pearson_r=-0.0582 [-0.0942, -0.0220]  spearman_rho=-0.0140 [-0.0503, +0.0222]
max_power_w                n=2767  pearson_r=-0.0204 [-0.0576, +0.0169]  spearman_rho=-0.0193 [-0.0565, +0.0180]
power_drag_area_m2         n=2767  pearson_r=+0.0069 [-0.0304, +0.0441]  spearman_rho=-0.0001 [-0.0374, +0.0372]
coast_rolling_decel_ms2    n=2920  pearson_r=-0.0340 [-0.0702, +0.0023]  spearman_rho=-0.0335 [-0.0697, +0.0028]
coast_drag_area_m2         n=2920  pearson_r=+0.0060 [-0.0303, +0.0423]  spearman_rho=-0.0007 [-0.0370, +0.0356]
power_to_drag (composite)  n=2767  pearson_r=-0.0253 [-0.0625, +0.0119]  spearman_rho=+0.0018 [-0.0355, +0.0390]
```

Note: `power_drag_area_m2` and `drag_area_closed_m2` produce numerically identical correlation figures
in this table — both trace back to the same underlying drag-fit column pairing in `session_estimates`
for the sessions where both are populated; this was observed, not assumed, and is left as-is (no
axis was added/removed/altered post-hoc per the pre-registration discipline).

## Honest read — what this does and does NOT show

**What it shows:** the pre-registered primary axis, total peak lateral-g capability
(`lateral_mech_grip_g + lateral_aero_grip_g`), has a small but 95%-CI-distinguishable-from-zero negative
Pearson correlation with evo's quali_error (the part of a driver's quali pace gap NOT explained by their
own trailing-mean recent-history baseline), in the pre-registered direction. Two of the nine secondary
axes (`brake_decel_ms2`, `traction_aero_accel_per_m`) show similarly-sized negative Pearson correlations
with CIs also excluding zero; the rest are indistinguishable from zero. This is broadly consistent with
this run's `decision:regime_readiness_rubric` prior finding that the regime-capability vector is
circuit-conditional and fine-margin (`frac_team` ~0–4%) rather than a clean, dominant car axis — a small,
real, non-dominant signal is exactly what that prior would predict, not a surprise, and not a bug.

**What it does NOT show:**
- This is NOT the ~0.80-ceiling answer from Phase 7's G1 — that is a different, heavier-weight
  measurement against the fused live model's actual prediction error, not this simple trailing-mean
  baseline.
- It does NOT measure whether physics beats the FULL live 3-stage sampled predictor — only whether it
  beats a specific, simple recent-history baseline (a driver's own trailing-mean prior-Q pace gap,
  reset each season).
- The team-level→driver-level broadcast (see Method recap) dilutes any true per-driver physics signal;
  a stronger correlation could exist at the per-driver level than this constructor-broadcast measurement
  can detect.
- The Spearman result being near-zero and sign-mismatched with Pearson means the linear association is
  not confirmed as a robust monotonic/ordinal relationship — plausibly driven by a subset of
  large-magnitude sessions rather than a uniform ordinal effect across the whole field. This was not
  investigated further (out of scope for this pure-correlation Phase-0 probe) and is flagged as a
  natural next question for Phase 7's fuller G1 treatment.
- No causal claim is made or implied; this is an observational correlation screen only.

## Scoped null / positive statement

This specific test (Pearson correlation of `lateral_total_grip_g` broadcast per-constructor, against
`quali_error` defined as residual from a per-driver per-season trailing-mean recent-history baseline,
across 2019–2026 Q sessions with valid lap data) finds a **small, real (CI-excludes-zero), correctly
signed, non-dominant** Pearson correlation, and **no** distinguishable-from-zero Spearman correlation,
under these exact conditions. It does not speak to other constructions, other axes' interactions, per-
driver physics estimates, or the fused model's actual error.
