# Reviewer Handoff — G3 Validation

## Gate
g3 (execute.json `g3-review`)

## Survey State Location
`.agent-work/issue-495-fit-robustness/g3-review/review.json`.

## What Was Implemented
Real-data validation of the G2 fix (no dashboard). The implementer re-fit the 19
previously-failing 2023-Q cases and a 24-case no-regression sample on current code,
and wrote `reports/physics/495_fit_robustness_validation.md`. Headline: 18 `error`
→ 0; final 2023-Q = 438 ok / 1 no_laps / 1 no_speed_stream (Saudi DEV).

## How to Inspect
- Note: `reports/physics/495_fit_robustness_validation.md`
- Result: `.agent-work/issue-495-fit-robustness/g3_implementer_result.md`
- No `src/` change in G3 — confirm `git status --short src/` shows only the G2 files
  (fit_store.py, session_fit.py, calibration.py + 2 test files), nothing new.

## Task Statement
Validate the fix on real telemetry and accurately account before/after — no
fabricated numbers; honest no-regression framing.

## Close Criteria (each a review check)
- **Re-run a SAMPLE yourself** (≥3 of the 19, MUST include Saudi Arabia DEV) via
  `load_quali_session` + `fit_driver` and confirm: Saudi DEV → `no_speed_stream`; ≥2
  recovered cases → `ok`. Numbers must match the note.
- **Before/after counts honest:** the OLD baseline (421 ok / 18 error / 1 no_laps)
  is the pre-#548 store; the NEW counts are current code. Confirm the note does not
  overclaim G2's share (the 17 interleaved/NoneType recoveries are #548's; G2's
  specific contribution is Saudi DEV error→no_speed_stream). The note should make
  this honest.
- **No-regression framing is correct:** G2's diff does NOT touch any successful-fit
  numeric path (only adds early-return guards on empty streams) — so the 2–20%
  param drift between OLD store and NEW is attributable to **#548** (already on
  main, engine_sha changed), NOT this run's G2. Verify by inspecting the G2 diff
  (`git diff src/`) that no numeric/estimation code changed, and that the 24
  previously-ok sample all still return `ok`. Flag if the note misattributes drift.
- **Note is text-only** (no binary/PNG/SVG) and reproducible-in-spirit.
- **No `src/` change in G3.**

## Allowed Scope
Read/run `src/physics`, `src/preprocessing`; write only your survey +
`.agent-work/issue-495-fit-robustness/g3_review_result.md` + throwaway probes.

## Specific Exclusions
No src/ edits; no fixes.

## Constraints
- `py` launcher; `constraint:physics_region_no_evo_import`.
- Do not overwrite `data/physics_fits.db` (the baseline).

## Map Anchors (inbound)
- **Structural:** `session_fit.fit_driver` / `load_quali_session`;
  `fit_store.session_fits` table (baseline `data/physics_fits.db`).
- **Capability:** batch fit-store population; fit evidence reporting.
- **Constraints:** physics_region_no_evo_import; markdown-only.
- **Evidence expectations:** 18 error → 0; Saudi DEV → no_speed_stream; no status
  regression on previously-ok fits.
- **Map confidence flags:** param drift OLD↔NEW is a #548 effect (already merged),
  not a G2 regression — confirm this attribution, don't accept it on trust.

## Evidence Produced
Implementer reports: 19-case table (17 ok / SAR no_laps / DEV no_speed_stream);
24/24 no-regression sample ok; before/after counts; note written. Also flagged: the
report path is under gitignored `/reports` so it needs `git add -f` at commit
(consistent with the already-tracked P0/P1a siblings) — note for the Commander.

## Suggested Model Tier
simple bounded — re-run a sample + read the note + inspect the G2 diff.

## Stop Conditions
Return BLOCK if: Saudi DEV does not return `no_speed_stream`; a sampled recovered
case does not match the note; the note misattributes the param drift as a G2
regression (or claims G2 fixed all 18); or a `src/` change appears in G3.

## Return Format
Return REVIEW_RESULT (write to
`.agent-work/issue-495-fit-robustness/g3_review_result.md`): verdict (APPROVE/BLOCK),
per-check findings WITH your independent re-run output, blockers, out-of-scope
observations, workflow feedback.
