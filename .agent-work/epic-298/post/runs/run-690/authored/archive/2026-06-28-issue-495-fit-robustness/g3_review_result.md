# Review Result — G3 Validation (attempt-2)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3-review` — validate G2 fix on real telemetry; verify before/after accounting and attribution

## Result
`APPROVE`

**Attempt-1 BLOCK (B1: validation note conflated G2 with #548) is RESOLVED. All 11 checks
now pass.**

This attempt-2 pass is a B1-only documentation-honesty re-check, as requested. The underlying
facts (independent re-runs of 5 cases, 24/24 no-regression, param-drift attribution, G2 diff
touches no numeric path) were independently verified in attempt-1 and remain valid — they were
not re-run.

---

## B1 resolution

The corrected `reports/physics/495_fit_robustness_validation.md` now cleanly separates the two
fixes' contributions. All four coordinator-requested criteria are present and accurate:

1. **Headline + Attribution split (PASS).** The headline (lines 18-23) states: PR #548
   (commit `1c501ccf`, already on main) recovered 17 of 18 cases to `ok`; this issue's G2 fix
   (the `no_speed_stream` guard) recovered exactly 1 — Saudi Arabia DEV (error→no_speed_stream),
   "which #548 did NOT fix." A new "Attribution: #548 vs this fix" section (lines 92-113) carries
   a per-fix table and the explicit statement: "this issue's actual code contribution to the
   headline is the 1 Saudi Arabia DEV case. The other 17 were already recovered by #548 on main
   before this run." The #548 share is broken out as 14 interleaved-origin + 3 NoneType-origin = 17.

2. **Tally check (PASS).** Line 79: "17 (`ok`) + 1 (`no_speed_stream`) + 1 (`no_laps`, unchanged)
   = **19**. ✓"

3. **Before/after table baseline annotation (PASS).** Lines 40-42 add a "Baseline note": the OLD
   column (engine_sha=6a051ff, built 2026-06-18) predates **both** fixes, so the table reflects
   their **combined** effect, with the per-fix split deferred to the Attribution section.

4. **Param-drift attribution unchanged-correct (PASS).** Lines 138-146 state the 2–20% drift is
   "caused by **PR #548** (not this issue's `no_speed_stream` guard)" and explicitly note "This
   issue's G2 fix only adds an early-exit guard for empty speed streams; it does not touch the
   numeric path of any `ok` fit." This matches my attempt-1 diff verification.

**No new misstatement introduced.** I checked the internal arithmetic for consistency: the
per-case table lists 15 rows with old error pattern "interleaved n=0" (including Saudi DEV).
The note reclassifies Saudi DEV as the 15th interleaved-origin case that #548 did NOT recover
(its surface error read "interleaved n=0" but the root cause is an empty session-wide speed
stream). That leaves 14 interleaved-origin cases recovered by #548, + 3 NoneType-origin = 17 → ok,
+ 1 Saudi DEV → no_speed_stream, + 1 Japan SAR → no_laps = 19. Consistent. The reclassification
is honest and matches what I verified in attempt-1: #548's `fit_stint_hp` guard returns
`None`→`no_accel_samples` for empty stints and would not produce an `ok` fit for a session-wide
empty stream, so DEV genuinely required G2's earlier empty-stream guard.

---

## Handoff compliance

All five close criteria now satisfied. G3 completed the 19-case re-fit, 24-case no-regression
sample, and the validation note. No src/ changes by G3.

---

## Scope drift

None. `git status --short src/ tests/` (re-confirmed at attempt-2) shows exactly the 5 G2 files
(fit_store.py, session_fit.py, calibration.py, test_475_validation_breadth.py,
test_calibration_robustness.py) — all `M` (modified), no untracked additions. The attempt-2 note
correction is in `reports/`, not `src/`. `data/physics_fits.db` not overwritten.

---

## Evidence verdict

The validation note is text-only (UTF-8 markdown). Reviewer's attempt-1 independent re-runs of 5
of the 19 cases all matched the note exactly:

```
Saudi Arabia DEV -> fit_status='no_speed_stream' n_fly=0 n_samp=0
Japan PIA        -> fit_status='ok'              n_fly=4 n_samp=1393
Bahrain ALO      -> fit_status='ok'              n_fly=5 n_samp=1796
Netherlands SAR  -> fit_status='ok'              n_fly=8 n_samp=2492
Canada HUL       -> fit_status='ok'              n_fly=8 n_samp=2591
```

These remain valid for attempt-2 (no code or note-data change affects them). Evidence now
satisfies the attribution-honesty criterion as well.

---

## Code/doc quality

G2 src changes remain minimal and guard-only (confirmed attempt-1): no numeric/estimation logic
changed. The corrected note is accurate, internally consistent, and reproducible-in-spirit.

---

## Map impact verdict

G3 is inspection-only; Map Impact correctly skipped. The new `no_speed_stream` sentinel (a G2
contribution) is a Cartographer reconcile candidate (tc2 below). No durable context dropped.

---

## Reconciliation check

No structural changes by G3. The `no_speed_stream` sentinel should reach the architecture map
(tc2). Not a blocker.

---

## Blockers

None. B1 resolved (see above).

---

## Out-of-scope observations

1. **tc1 — Full 440-case rebuild** to `data/physics_fits_495.db` deferred (~2.5h). The 19+24
   targeted re-fits validate the fix; the full rebuild establishes the new canonical store.

2. **tc2 — `no_speed_stream` sentinel** is documented in `fit_store.py`'s docstring comment but
   not in `docs/architecture/index.md`. Cartographer reconcile candidate.

3. **Note → `git add -f` needed:** The report is under gitignored `/reports/`; it needs
   `git add -f` at commit (consistent with already-tracked P0/P1a siblings). Carry-forward for
   Commander.

---

## Workflow Feedback

- **Handoff gaps:** The attempt-1 stop condition "claims G2 fixed all 18" was a count-framed
  proxy for an attribution problem. The real issue was that the note did not separately credit
  #548 (17) and G2 (1). The corrected note resolves it cleanly; the re-review handoff (from the
  coordinator) restated the criterion precisely as a per-fix split, which made the recheck
  unambiguous.

- **Context rediscovered:** None new in attempt-2. The attempt-1 git archaeology (`git show
  1c501ccf`) that established the #548-vs-G2 mechanism boundary was reused to confirm the
  corrected note's reclassification of Saudi DEV is honest.

- **Instructions improvised around:** The engine reference at
  `constellation-reviewer/references/checklist-engine.md` is still absent at the expected path;
  drove the survey via the template JSON structure (same as attempt-1).

- **What would have made this easier:** none — confirmed after review: the coordinator's
  re-review message enumerated the exact four criteria to check, the corrected note addresses
  all four, and I verified each against the file plus the internal arithmetic. The re-check was
  self-contained.

---

## Return status
`complete`
