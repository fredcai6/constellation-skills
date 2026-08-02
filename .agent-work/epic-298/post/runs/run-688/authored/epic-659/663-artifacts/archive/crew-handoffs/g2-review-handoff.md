# Reviewer Handoff

## Gate
g2-implement (reviewing for g2-review)

## Survey State Location
`.agent-work/663-grip-g/g2-review/review.json`

## What Was Implemented
`src/physics/layer2/grip_baseline.py`: G's fit logic (issue #663). (a) a vectorized cumulative-track-laps helper claimed to match `session_race.compute_cumulative_track_laps` exactly; (b) a LOCAL session_type-generalized clean-lap reader that feeds `tyre_supplant.race_degradation_slopes` unchanged (tyre_supplant.py NOT touched, per the implementer's own reported choice); (c) a saturating curve `session_offset + curve_asymptote*(1-exp(-curve_rate*x))` fit with `predictive_t`-derived sigmas and a `curve_offset_correlation` diagnostic; (d) a thin-session wide-sigma fallback (named constant `THIN_SESSION_SIGMA_INFLATION=3.0`); (e) a rain-flag wide-sigma re-estimation (separate named constant `RAIN_SIGMA_INFLATION=4.0`).

## How to Inspect the Diff
Uncommitted working tree, linked worktree `C:/Programs/f1brainz-wt/epic659-663` (branch `epic659/663-grip-g`).
```bash
cd /c/Programs/f1brainz-wt/epic659-663
git status --porcelain
```
Both new files are untracked (`??`); read `src/physics/layer2/grip_baseline.py` and `tests/unit/physics/layer2/test_grip_baseline.py` directly. **Critically confirm `src/physics/layer2/tyre_supplant.py` shows NO modification marker at all** (not even `M`) — the implementer reports choosing the local-reader path specifically to avoid touching it; this is the single most important scope-integrity check for this gate.

## Task Statement
Build G's fit logic reusing `compute_cumulative_track_laps`'s convention and `race_degradation_slopes`'s regression design unmodified, implementing the FROZEN thin-session and rain-flag wide-sigma rules (not open to redesign), using `predictive_t` for Student-t residuals.

## Close Criteria
- Cumulative-laps helper: read the regression test (`test_grip_baseline.py`) and confirm it actually calls `session_race.compute_cumulative_track_laps` and compares against real DB data (not synthetic-only, not a self-referential tautology) — re-run it yourself.
- The generalized reader's SQL/filter genuinely mirrors `tyre_supplant._read_clean_race_laps` (compare them side by side) and calls `race_degradation_slopes` (imported, not copy-pasted/reimplemented) — grep for `race_degradation_slopes` import + call site in `grip_baseline.py`.
- `predictive_t` is genuinely called for the residual/sigma model — grep for the exact import and call, confirm it's not a `scipy.stats.norm`/Gaussian dressed up.
- Thin-session fallback: read the synthetic 2-lap-stint test, confirm `fit_status="thin_fallback"` is set, sigma is inflated by the named constant, and NO record is silently dropped (a record always exists, even in the degenerate all-thin-in-weekend case).
- Rain-flag fallback: read the rain-fit-vs-dry-fit sigma comparison test, confirm the reported 4.0x ratio is REAL (re-run it, don't trust the pasted number) and that `RAIN_SIGMA_INFLATION` is a genuinely distinct constant from `THIN_SESSION_SIGMA_INFLATION` (not the same value coincidentally, check the source).
- `tyre_supplant.py` shows zero diff (see How to Inspect the Diff above) — this is a BLOCK-worthy finding if violated in any way beyond a sanctioned additive optional-parameter change.

## Allowed Scope
New files only: `src/physics/layer2/grip_baseline.py`, `tests/unit/physics/layer2/test_grip_baseline.py`. `tyre_supplant.py` ONLY if additive (see above — implementer reports NOT touching it at all; verify this).

## Specific Exclusions
Must NOT modify `grip_store.py` (g1) or write batch-driver code (g3's job — check nothing named like `run_grip_batch`/`GripStore` write-orchestration crept in here).

## Constraints the Implementation Must Respect
- Student-t residuals (no-baked-normality).
- Reuse not reimplement: `compute_cumulative_track_laps`, `race_degradation_slopes`.
- Frozen thin-session rule (floor=2 stints of 4 laps) and rain-flag rule — implemented as specified, not redesigned.
- DB-only analysis (`data/f1_data_2023.db`, main checkout, explicit path).

## Map Anchors (inbound)
Same as `g2-implement-handoff.md`'s Map Anchors section — `struct:physics.layer2`; `assumption:student-t-residuals`; `decision:thin-session-explicit` @grade: settled/measured; `decision:session-scope-uniform` @grade: settled/measured; `claim:cumulative-track-laps-reuse`, `claim:tyre-supplant-correction-reused`.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/663-grip-g/crew-handoffs/g2-implement-result.md` — 12/12 tests, simplification PASS, rain sigma ratio 4.000x, tyre_supplant.py reportedly untouched. Also two out-of-scope findings worth confirming are genuinely out-of-scope, not silently-swallowed defects: (1) fuel not fully removed from the residual because `race_degradation_slopes` doesn't expose its internal fuel coefficient for subtraction — confirm this is a real, honestly-scoped limitation (not a bug) and worth a triage candidate; (2) `sessions.rainfall` is declared REAL in schema.sql but stored as an int64 blob wet-sample-count — confirm the decode is correct on real data (spot-check one known-wet 2023 session if you can identify one) and that this mismatch is also triage-worthy, not silently wrong.

**IMPORTANT:** use `"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe"` for every command — plain `py` resolves to a broken shim.

## Suggested Model Tier
Stronger — reason: real statistical code, the reuse-not-reimplement claims need genuine verification (not just "tests pass"), and the fuel/rain findings need judgment about scope-honesty.

## Stop Conditions
Stop and return BLOCK if: `tyre_supplant.py` was touched beyond a sanctioned additive change, `predictive_t` isn't genuinely used, either fallback silently drops a record, or the rain sigma ratio doesn't reproduce.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g2-review-result.md`, and return as final message text): verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations (confirm/reject the implementer's two flagged findings as triage candidates), workflow feedback.
