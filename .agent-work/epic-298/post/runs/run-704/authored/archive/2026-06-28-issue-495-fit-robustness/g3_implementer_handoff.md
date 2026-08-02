# Implementer Handoff — G3 Validation (real-data; dashboard dropped)

## Gate
g3 (execute.json `g3-implement`)

## Task
Validate the G2 fix on real telemetry and write a short before/after accounting note.
**No dashboard** (dropped by the user 2026-06-28). Validation only.

## Protected Intent
Honest accounting: prove the previously-failing cases now recover or skip cleanly,
prove the 421 previously-ok fits did not regress, and report the real before/after
counts. No fabricated numbers — every figure comes from an actual re-fit.

## Test Mode
inspection-only (real-data validation; the code+unit tests already landed in G2).

## Close Criteria (each proven with real output)
- **Re-fit the 19 previously-failing 2023-Q cases** on current (fixed) code and
  record per-case outcome (recovered-ok / clean-typed-skip / still-failing). Expected
  from the G1 diagnosis (confirm, don't assume): 17 → `ok`, Japan SAR → `no_laps`,
  **Saudi Arabia DEV → `no_speed_stream`** (was the lone `error`). If anything still
  raises or differs, report it.
- **No-regression check:** re-fit a representative sample of the 421 previously-ok
  2023-Q fits (≥20 across ≥5 circuits) and confirm each still returns `ok` with the
  same key params (within float tolerance) as the OLD store
  `data/physics_fits.db`. Report the comparison; note the sample size + cost. (A full
  440 re-run is OPTIONAL — note the cost if you skip it; full-store rebuild is a
  separate triage follow-up tc1.)
- **Before/after accounting note** written to
  `reports/physics/495_fit_robustness_validation.md` (markdown, text only, NO
  binary): old counts (421 ok / 18 error / 1 no_laps) → new counts by `fit_status`;
  the per-case table for the 19; the no-regression sample result; the one-line
  headline (live exception population 1 → 0).

## Allowed Scope
- Read/run `src/physics`, `src/preprocessing`, `scripts/build_physics_fit_store.py`.
- Write: `reports/physics/495_fit_robustness_validation.md` and
  `.agent-work/issue-495-fit-robustness/g3_implementer_result.md`. Throwaway probes
  under the work area. You MAY reuse the G1 probe scripts
  (`.agent-work/issue-495-fit-robustness/probe_repro.py` etc.).

## Specific Exclusions
- No `src/` changes (the fix is done + reviewed). No dashboard / HTML / SVG / PNG.
- Do NOT alter the 55 GB FastF1 cache or the telemetry store.
- Do NOT overwrite the OLD `data/physics_fits.db` (it's the before baseline). If you
  build a fresh store, use a NEW path (e.g. `data/physics_fits_495.db`) — and note
  it's untracked/regenerable, not committed.

## Constraints
- `py` launcher (never `python`). `constraint:physics_region_no_evo_import`.
- Data in THIS checkout: telemetry store `data/telemetry_store.db` (store-first),
  FastF1 cache `data/telemetry`, OLD fit store `data/physics_fits.db` (baseline).

## Map Anchors (inbound)
- **Structural:** `session_fit.load_quali_session(year, gp, session_type) ->
  (session, rho, rho_is_fallback)`; `session_fit.fit_driver(session, driver, *,
  year, gp_name, round_idx, session_type, constructor, rho, cfg=None) -> FitRecord`;
  `fit_batch.run_batch(store, seasons=, sessions=)` is the calendar looper;
  `scripts/build_physics_fit_store.py --seasons 2023 --sessions Q --db <path>
  --force`. (NOTE: `fit_session_full` is the single-driver P1 diagnostic, NOT the
  batch looper.)
- **Capability:** batch fit-store population; fit evidence reporting.
- **Constraints:** physics_region_no_evo_import; markdown-only; py launcher.
- **Evidence expectations:** per-case outcomes; no-regression sample; before/after
  counts; live exception population 1 → 0.

## The 19 cases (2023 Q)
interleaved-origin (15): Japan PIA/NOR/LEC/SAI/MAG, Netherlands SAR, Mexico ZHO,
Brazil PIA, Las Vegas BOT, Abu Dhabi VER, Saudi Arabia DEV, Azerbaijan GAS/DEV,
Miami BOT, Canada ALB. NoneType-origin (3): Bahrain ALO/HAM, Canada HUL.
no_laps (1): Japan SAR.

## Required Evidence
- The re-fit transcript for the 19 cases (status per case).
- The no-regression sample comparison (old vs new params).
- The committed `reports/physics/495_fit_robustness_validation.md`.

## Verification Commands
```bash
# per-case re-fit (reuse/adapt the G1 probe). Example:
py .agent-work/issue-495-fit-robustness/probe_repro.py
# (or scoped store build to a fresh DB, then read counts)
```

## Suggested Model Tier
simple bounded — re-run + tabulate + write a markdown note.

## Authority
Validation only; the fix + scope are already ratified. Report what you find; if a
case unexpectedly still fails, STOP and return (do not patch src/).

## Stop Conditions
Stop and return if: a previously-failing case still raises (other than the expected
Saudi DEV → no_speed_stream); a previously-ok fit regresses (status or params drift);
a fix would be needed to make a number come out right.

## Return Format
Return IMPLEMENTER_RESULT (write to
`.agent-work/issue-495-fit-robustness/g3_implementer_result.md`): validation summary,
the note path, per-case table, no-regression result + sample size/cost, before/after
counts, assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
