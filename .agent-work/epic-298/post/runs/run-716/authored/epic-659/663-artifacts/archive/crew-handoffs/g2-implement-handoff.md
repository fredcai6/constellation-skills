# Implementer Handoff

## Gate
g2-implement

## Task
Create `src/physics/layer2/grip_baseline.py`: the FIT logic for grip-baseline module G (issue #663). This produces the values that populate the `GripEstimateRecord` fields already frozen in `src/physics/layer2/grip_store.py` (g1, complete — read it first, it defines the exact target field shape).

Build, in order:

**(a) Cumulative-track-laps helper.** A vectorized, per-session replication of `src/physics/layer2/session_race.py:268` `compute_cumulative_track_laps`'s EXACT counting convention: for a given `session_id`, count of (driver,lap) pairs in `lap_times` with `lap_number < X`, for ALL cars, regardless of `valid_lap`/`track_status`. Read `session_race.py:268-303` in full first — you are matching its definition exactly, not inventing a new one. Implement as ONE SQL query per session (e.g. `SELECT lap_number, COUNT(*) OVER (ORDER BY lap_number) ...` or an equivalent single-query/pandas-groupby approach) returning a per-lap cumulative count — NOT N separate calls to `compute_cumulative_track_laps` per lap (that function itself is fine to import and reuse for the regression-test comparison, just not as your hot-path implementation). Required evidence: a small regression test comparing your vectorized helper's output to `compute_cumulative_track_laps`'s own output on a handful of real `(session_id, lap_number)` pairs from `data/f1_data_2023.db` (main checkout path, pass explicitly) — they must match exactly.

**(b) Generalize the compound/tyre-age/fuel correction.** `src/physics/layer2/tyre_supplant.py`'s `race_degradation_slopes` function implements the OLS design you need (stint-ordinal fixed effects + standardized `fuel*lap_number` term + per-compound `tyre_life` slope) — read `tyre_supplant.py` in full. Its `_read_clean_race_laps` function hardcodes `session_type='R'` in its SQL filter. Add a `session_type: str = "R"` parameter to a NEW function in `grip_baseline.py` that reads laps for ANY session type (mirror `_read_clean_race_laps`'s query, parameterized) and feeds them to `race_degradation_slopes` UNCHANGED (import and call it directly — do not reimplement its regression body). Prefer keeping this generalized reader local to `grip_baseline.py` rather than editing `tyre_supplant.py`; if you find you genuinely must touch `tyre_supplant.py`, the edit must be additive-only (a new optional parameter defaulting to `"R"`, zero behavior change for existing callers) — state clearly in your result which path you took and why.

**(c) Saturating intra-session curve + free per-session offset.** Field-pooled per session: fit `grip(cumulative_track_laps) = asymptote * (1 - exp(-rate * cumulative_track_laps)) + session_offset` (or an equivalent saturating form — your choice of exact functional form, state it) against the session_type-generalized, tyre_supplant-corrected residual pace. Student-t residuals: use `src/common/student_t.py`'s `predictive_t(mu, sigma, n_eff, *, nu_loss, rule)` (read the file — it is the canonical Student-t seam already used 3 places in this repo; do not hand-roll a t-distribution). Output: `curve_asymptote(+sigma)`, `curve_rate(+sigma)`, `session_offset(+sigma)`, and `curve_offset_correlation` (the estimated/posterior correlation between the curve's initial value and the offset — this is the T2 separability diagnostic g5 will test against; a plain OLS/least-squares covariance matrix off-diagonal element, or a bootstrap/jackknife estimate, is an acceptable way to get this — state which you used).

**(d) Thin-session rule — wide-sigma fallback (frozen decision, not open to revisit).** Floor: session fit proceeds normally only if it has >=2 usable driver-stints with >=`tyre_supplant.MIN_STINT_LAPS` (4) laps each. Below the floor: DO NOT drop the record. Instead, estimate `session_offset` via within-weekend nearest-neighbor extrapolation (the nearest OTHER session in the same weekend that had a normal fit, evaluated at this session's `cumulative_track_laps` position on ITS curve) with `session_offset_sigma` inflated by a NAMED constant multiplicative factor (e.g. `THIN_SESSION_SIGMA_INFLATION = 3.0` — pick and name a specific value, state your reasoning). Set `fit_status="thin_fallback"` and `fallback_reason` to a short string. If NO other session in the weekend has a normal fit either (all thin), fall back further to a field-wide prior (document this degenerate case explicitly — do not crash).

**(e) Rain-flag re-estimation (frozen Mission requirement — NOT optional, NOT an inert column).** When a session's rain flag is set (check `sessions.rainfall` or equivalent weather column in the schema — read `src/data/schema.sql` to confirm the exact column name), the offset fit MUST re-estimate with an explicitly inflated sigma — a SEPARATE named constant from the thin-session one (e.g. `RAIN_SIGMA_INFLATION = 4.0`, your choice, state reasoning) — because rain fundamentally changes track grip evolution vs. the dry-session model. This must have a REAL, TESTABLE fit-time effect (wider `session_offset_sigma` than the equivalent dry fit), not just a stored flag with no consequence.

## Protected Intent
Every consumer of G subtracts the SAME `session_offset`/`curve_*` values — the fit logic here is the single source of truth. A thin/rain session must NEVER silently produce a falsely-confident (small-sigma) estimate — that is the exact #560 failure this issue exists to fix.

## Test Mode
Test-after allowed (fit logic tested against synthetic + real-DB fixtures) — full test-after required before this gate closes.

## Close Criteria
- Cumulative-laps helper matches `compute_cumulative_track_laps` exactly on real data (regression test).
- Generalized session-type reader reuses `race_degradation_slopes` unchanged (no reimplementation).
- Curve+offset fit produces all required output fields, using `predictive_t` for the Student-t residual model.
- Thin-session fallback triggers on a synthetic 2-lap-stint fixture, produces `fit_status="thin_fallback"` with inflated sigma, never a dropped/NULL record.
- Rain-flag fallback triggers on a synthetic rain-flagged session, produces a demonstrably wider `session_offset_sigma` than the equivalent dry fit (a direct numeric comparison in the test, not just "it ran").
- Tests at `tests/unit/physics/layer2/test_grip_baseline.py` (this exact path — g2-integrate's postcondition hardcodes it).

## Allowed Scope
- New file: `src/physics/layer2/grip_baseline.py`.
- New file: `tests/unit/physics/layer2/test_grip_baseline.py`.
- Read-only reference: `src/physics/layer2/session_race.py`, `src/physics/layer2/tyre_supplant.py`, `src/common/student_t.py`, `src/data/schema.sql`, `src/physics/layer2/grip_store.py` (g1, for the target field shape).
- `src/physics/layer2/tyre_supplant.py` — ONLY if genuinely required, and ONLY an additive optional-parameter change (see task (b) above); prefer not touching it at all.

## Specific Exclusions
- Do NOT modify `grip_store.py` (g1, already APPROVED and complete).
- Do NOT write `grip_batch.py` — that is g3's job.
- Do NOT build the held-out (g4) or synthetic-recovery (g5) acceptance harnesses here — this gate is the fit function itself, which g4/g5 will import and call.
- Do NOT modify any part of `tyre_supplant.py`'s existing behavior for `session_type='R'` callers.

## Constraints
- Student-t residuals required (project standing principle, no-baked-normality) — use `predictive_t`, cite its exact call in your result.
- Reuse, do not reimplement, `race_degradation_slopes`'s regression design.
- Reuse, do not reimplement, `compute_cumulative_track_laps`'s counting convention (match it exactly, prove it via the regression test).
- Thin-session rule is FROZEN (wide-sigma fallback, floor = 2 stints of 4 laps) — implement exactly this, do not substitute a different rule.
- Rain-flag re-estimation is a FROZEN Mission requirement — must have a real, tested effect.
- DB-only analysis — read from `data/f1_data_2023.db` (main checkout path, passed explicitly), never live FastF1/Jolpica.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2`.
- **Capability:** new — G's fit logic.
- **Constraints/assumptions:** `assumption:student-t-residuals`.
- **Decision anchors:**
  - `decision:thin-session-explicit` — wide-sigma fallback, floor=2 stints of 4 laps.
    `@grade: settled/measured · leans g2-implement`
  - `decision:session-scope-uniform` — all session types, generalized session_type parameter.
    `@grade: settled/measured · leans g2-implement`
- **Evidence expectations:** `claim:cumulative-track-laps-reuse`, `claim:tyre-supplant-correction-reused`.
- **Map confidence flags:** none.

## Deliverable Path Check
- **Committed** — `src/physics/layer2/grip_baseline.py`; verify `git check-ignore` exit 1.
- **Committed** — `tests/unit/physics/layer2/test_grip_baseline.py`; verify `git check-ignore` exit 1.

## Required Evidence
- Cumulative-laps regression test output (load-bearing — paste it).
- Full `pytest tests/unit/physics/layer2/test_grip_baseline.py -q` output (load-bearing).
- The rain-flag sigma comparison numbers (dry-fit sigma vs rain-fit sigma, both printed/asserted) — load-bearing, this is the frozen Mission requirement's proof.
- Which path you took for task (b) — local generalized reader vs. additive `tyre_supplant.py` edit — one paragraph (confirmatory).
- `git check-ignore` outputs for both new files.

## Verification Commands
```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_baseline.py -q
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths src/physics/layer2/grip_baseline.py tests/unit/physics/layer2/test_grip_baseline.py
git status --porcelain src/physics/layer2/grip_baseline.py tests/unit/physics/layer2/test_grip_baseline.py
git check-ignore src/physics/layer2/grip_baseline.py; echo "exit=$?"
```
**IMPORTANT:** plain `py` on this sandbox's PATH resolves to a broken shim missing scipy/fastf1 — always use the full path above (`/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe`), confirmed working by g1's implementer/reviewer.

Also run `simplification_limits` yourself BEFORE returning — g1's reviewer BLOCKed once on this exact gate not being self-checked; do not repeat that.

## Suggested Model Tier
Stronger — reason: real statistical fit logic (OLS generalization, saturating-curve fit, Student-t residual model, two distinct fallback mechanisms), moderate ambiguity in exact functional-form/fallback-constant choices, real risk (this is the core of the module every later gate depends on).

## Authority
The thin-session rule, session-type scope, and rain-flag requirement are ALREADY DECIDED — implement them, do not redesign. The exact saturating curve functional form, the two sigma-inflation constants' numeric values, and the correlation-estimation method are yours to choose within the stated constraints — state your choices and reasoning in the result.

## Stop Conditions
Stop and return if: `race_degradation_slopes` cannot be reused without touching `tyre_supplant.py` in a non-additive way, the real 2023 DB lacks the rain/weather column you expected (check `schema.sql` first), or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g2-implement-result.md`, and return as your final message text): completed slice, files changed, test mode satisfied, evidence produced (paste command outputs), assumptions used, functional-form/constant choices + reasoning, stop conditions hit, out-of-scope observations, workflow feedback.
