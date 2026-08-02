# Triage Recommendations — issue #447 (Phase 0b)

Prepared for Admiral/human approval. NONE filed yet — issue creation awaits explicit
per-issue approval (spine triage c2 = user-decision). Authority per ORCHESTRATOR_CONTEXT:
issue creation is autonomous-for-non-trivial, but the spine gate forces human sign-off.

---

## TR-1: Phase 1 trajectory estimator — consume the measurement model (the GO fork)

### Classification
feature, research hardening

### Source
`docs/physics/measurement_model.md` §8 GO recommendation; epic #445 decision point.

### Problem / Desired
If the human ratifies GO, Phase 1 opens: build the trajectory estimator that fuses the two
raw streams using the measured model. This is the epic's next phase, not a standalone bug.

### Suggested scope
A Phase 1 estimator that (a) places both irregular ~4.2 Hz grids on a common time base;
(b) models the per-lap/per-session inter-stream offset as a first-class term (stable
estimable bias per §5); (c) assumes the white-jitter time-tag error model (§3); (d) uses
per-session per-channel noise covariances (§4); (e) is graded by the 0a harness with the
covariance gate applied to an OFFSET-REMOVED residual at band (0.5, 2.0) (F1, §9); (f)
adopts the free-`s_finish` anchor gauge (F3, §10).

### Acceptance criteria
- [ ] Estimator fuses car/pos into one trajectory on a common time base.
- [ ] Offset modeled explicitly; post-offset covariance chi-square enters (0.5, 2.0) on the 6 sessions.
- [ ] s_finish free-anchor implemented with a test (s3 no longer pins to track length).

### Recommended priority
high — **only if** the human ratifies GO. This IS the epic continuation.

### Issue creation authority
ask user — this is the epic's fork; the Admiral/human owns whether/when to open it.

---

## TR-2: F1 — covariance-gate contract: band + offset-removed residual (Phase 1 contract note)

### Classification
missing doc, cleanup (contract clarification)

### Source
`docs/physics/measurement_model.md` §9; 0a finding F1; `g2-review-result.md`.

### Problem / Current truth
The 0a covariance gate FUNCTION already defaults to band (0.5, 2.0), but the strawman RUNNER
applied a loose [0.01, 100]. The gate is only meaningful on an offset-removed residual; on the
offset-inclusive residual the chi-square is 78.7–3292 and no band discriminates.

### Suggested scope
When Phase 1 wires the gate into a runner/contract: document (in
`docs/report_schemas/trajectory_grading_report.md` and/or the Phase 1 contract) that the
covariance gate's residual MUST be offset-removed and the band is (0.5, 2.0), with per-session
per-channel variance (not a global constant). No code change needed today (default already matches).

### Acceptance criteria
- [ ] Phase 1 runner applies the gate to an offset-removed residual at band (0.5, 2.0).
- [ ] The report schema / Phase 1 contract states the residual definition explicitly.

### Recommended priority
medium — folds into TR-1; capture so it is not rediscovered.

### Issue creation authority
ask user (or fold into TR-1).

---

## TR-3: F3 — promote `s_finish` to a free co-estimated anchor in sector_anchor

### Classification
cleanup, missing test (design decision with code follow-up)

### Source
`docs/physics/measurement_model.md` §10; G2 sector-anchor fits.

### Problem / Current truth
`sector_anchor.py` fixes `s_finish = 0.0` and co-estimates only s1/s2/s3. Evidence: with
s_finish pinned, s3 is driven onto the track-length bound (Belgian Q: VER/NOR/GAS all fit
s3 = 7004.0 m) and sector-crossing residuals run 0.10–0.31 s (above the 0.050 s tolerance).

### Suggested scope
In Phase 1 sector-anchor work: free `s_finish` (fix lap-length scale to break gauge freedom),
co-estimate all four loop anchors. Land with a test confirming s3 no longer pins and
sector-crossing residuals decrease on the 6 sessions.

### Non-goals
Do not change 0a primitive behavior outside the sector-anchor gauge; not part of 0b.

### Acceptance criteria
- [ ] s_finish is a free parameter; lap-length scale fixed instead.
- [ ] Test: s3 unpins from track length; sector-crossing residuals drop toward 0.050 s.

### Recommended priority
medium — Phase 1 prerequisite for the sector-anchor gate to discriminate well.

### Issue creation authority
ask user (or fold into TR-1).

---

## TR-4 (tc1 forward half): characterize inter-stream timing structure for fusion

### Classification
research hardening

### Source
execute.json tc1 (from g1-review); `g2-implement-result.md`.

### Problem / Desired
The distinct base ticks (car ~40 ms, pos ~10–20 ms) and ~0.4%-overlapping irregular grids
ARE real inter-stream timing structure. 0b characterized the offset as a stable bias; a Phase 1
estimator may further exploit the sub-sample phase relationship for tighter fusion.

### Current truth (the docstring half of tc1 is DONE)
The offline_loader docstring "240Hz/10Hz" inaccuracy flagged in tc1 was CORRECTED in this run
(commit c56291a). Only the forward-looking fusion-characterization concern remains.

### Recommended priority
low — speculative tightening; only relevant inside TR-1.

### Issue creation authority
issue-ready only — likely fold into TR-1 rather than file standalone.

---

## Notes for the Admiral

- The F1 and F3 calls are RESOLVED as documented decisions in the deliverable; TR-2/TR-3 only
  exist to carry them into Phase 1 code. They are not open questions.
- TR-1 is the epic's GO fork — its creation/timing is the human's call, gated on ratifying GO.
- tc1's docstring half is already fixed in-run; not a follow-up.
- Recommendation: file TR-1 (and fold TR-2/TR-3/TR-4 into it as Phase 1 sub-tasks) IF and WHEN
  the human ratifies GO. If GO is deferred, hold all four. No issues should be filed before the
  GO/NO-GO ratification, since they all presuppose the estimator phase opening.
