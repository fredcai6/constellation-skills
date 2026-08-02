# Reviewer Handoff — G1 Diagnose (independent verification)

## Gate
g1 (execute.json `g1-review`)

## Survey State Location
Create your review survey at
`.agent-work/issue-495-fit-robustness/g1-review/review.json`.

## What Was Implemented
An EVIDENCE-ONLY diagnosis of issue #495 (no `src/` changes). The implementer
re-ran the 19 OLD-store failing 2023-Q fit cases on current `main` (HEAD bac0e96b,
post-PR #548) and concluded: **18 of 19 are already fixed by #548**; exactly **one**
live bug remains (Saudi Arabia DEV — empty session-wide speed stream → `tc.min()` on
an empty array at `calibration.py:879` in the `windows=` branch, before #548's guard
fires); 14/15 interleaved cases recover, 1 is genuinely unfittable (skip-clean);
`fit_store.py:34`'s fit_status comment is stale.

## How to Inspect the Diff
There is no `src/` diff (evidence-only). Inspect:
- Report: `.agent-work/issue-495-fit-robustness/g1_diagnosis.md`
- Result: `.agent-work/issue-495-fit-robustness/g1_implementer_result.md`
- Probe scripts + raw logs under `.agent-work/issue-495-fit-robustness/`
  (`probe_repro.py`/`repro_output.log`, `probe_nonetype.py`,
  `probe_overlap.py`, `probe_saudi_dev.py`, and their logs).
- Confirm no src/ modification: `git status --short src/` (must be empty).

## Task Statement
Verify the diagnosis is faithful and its conclusions are evidence-backed — because
the fix gate depends on it being correct (a wrong root cause ships the wrong fix).
Do NOT accept the conclusions on trust; independently reproduce a sample.

## Close Criteria (each becomes a review check)
- **Re-run a SAMPLE of the "already-fixed" cases yourself** (≥3, e.g. Bahrain ALO,
  Japan PIA, one Azerbaijan) via `load_quali_session` + `fit_driver` and confirm
  they return `fit_status="ok"` on current `main` — i.e. the "18/19 fixed" claim is
  real, not assumed.
- **Confirm the one live bug:** independently reproduce Saudi Arabia DEV → it raises
  / records `error` with `zero-size array to reduction operation minimum`; confirm
  the origin is `calibration.py:879` (`tc.min()` in the `windows=` branch) and that
  DEV's speed stream is genuinely **empty session-wide** (not merely a bad window) —
  so widening the window cannot help and skip-clean is the right call.
- **Confirm the from-source `fit_status` set** = `{ok, no_laps, no_accel_samples,
  error}` and that `fit_store.py:34` is stale.
- **Confirm the recover-vs-skip boundary** is evidence-backed: recoverable iff both
  streams have time-overlapping samples in the flying-lap windows (14/15); skip iff a
  required stream is empty session-wide (Saudi DEV).
- **No `src/` changes remain.**

## Allowed Scope
Read/run anything under `src/physics`, `src/preprocessing`, `scripts/`, and the
`.agent-work/issue-495-fit-robustness/` artifacts. You may write only your review
survey + `.agent-work/issue-495-fit-robustness/g1_review_result.md` (and throwaway
probes under the work area).

## Specific Exclusions
No `src/` edits; no fixes. This is a review of a diagnosis.

## Constraints the Implementation Must Respect
- `py` launcher (never `python`).
- `constraint:physics_region_no_evo_import`.
- Evidence-only (no src/ changes) — flag if violated.

## Map Anchors (inbound)
- **Structural:** `calibration.calibrate_session_hp` (`windows=` branch,
  lines ~877–891; `tc.min()` @ 879); `fit_stint_hp` (None-guard, len-guard);
  `session_fit.fit_driver` (`_err` mapping @ 308–314, `no_accel_samples` @ 310–312);
  `loaders.driver_streams` (`Vkmh>0` filter @ loaders.py:393);
  `fit_store.FitRecord.fit_status` (stale comment @ fit_store.py:34).
- **Capability:** per-session physics fit; HP calibration / held-out split.
- **Constraints:** physics_region_no_evo_import; evidence-only.
- **Map confidence flags:** the "18/19 already fixed" claim overturns the issue's
  premise — that is exactly why independent re-run is required, not optional.

## Evidence Produced
Per-case classification table (§2 of the report), NoneType root cause with
reproduced traceback (§3), per-case stream-overlap table (§4), Saudi DEV raw
traceback (§5), from-source fit_status enumeration (§6), failure counts (§7), fix
loci (§8), evidence index (§9).

## Suggested Model Tier
stronger — verifying a premise-overturning diagnosis by independent reproduction on
real telemetry.

## Stop Conditions
Return BLOCK if: a sampled "already-fixed" case does NOT return ok (the central claim
fails); the Saudi DEV root cause cannot be confirmed; evidence is unverifiable; or
any src/ change is found.

## Return Format
Return REVIEW_RESULT (write to
`.agent-work/issue-495-fit-robustness/g1_review_result.md`): verdict (APPROVE or
BLOCK), per-check findings (with the outputs of YOUR independent re-runs), blockers,
out-of-scope observations, workflow feedback.
