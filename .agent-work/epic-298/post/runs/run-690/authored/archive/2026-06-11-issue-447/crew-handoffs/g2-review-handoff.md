# Reviewer Handoff

## Gate
g2 (g2-review)

## What Was Implemented
`scripts/characterize_timetag_jitter.py` — read-only, over the same 6 sessions as G1: measures
time-tag jitter per stream (vs cadence fit AND DB sector-crossing truth), classifies the
time-tag error-model class, characterizes inter-stream offset stability (reusing 0a
`diagnose_cross_residual`), and computes the reduced chi-square the 0a covariance gate would
see. Emits `jitter_offset_*.json` to `.agent-work/issue-447/evidence/`.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
git status
git diff --stat
git diff -- scripts/characterize_timetag_jitter.py    # untracked: use `git status` then read the file
py -c "import glob,json; [print(f) for f in sorted(glob.glob('.agent-work/issue-447/evidence/*jitter*'))]"
```
Implementer result: `.agent-work/issue-447/crew-handoffs/g2-implement-result.md`.

## Task Statement
Quantify (per session, with distributions): (1) time-tag jitter per stream; (2) error-model
class in {bias, random-walk, per-batch} WITH discriminating evidence; (3) inter-stream offset
stability — estimable stable bias vs per-lap wander (resolves 0a F2); (4) the reduced chi-square
the 0a covariance gate would compute. Reuse 0a primitives (import, no fork). Characterization
ONLY — no estimator. Raw streams only, offline, pos_data decimetres.

## The implementer's headline verdicts (VERIFY, do not rubber-stamp)
- ERROR MODEL: **white-jitter** (no bias/random-walk/per-batch). Discriminators: dt-deviation
  lag-1 autocorr ~0; per-Source eta²=0; |mean|/std ~1e-4. (NB it flags the SG-residual
  autocorr ~0.6 as a smoothing artifact, using the dt-deviation series as the honest one.)
- OFFSET STABILITY: **STABLE-ESTIMABLE on all 6 sessions**: |session mean offset| ≤ 0.08 s;
  median per-lap std 0.084–0.129 s; per-lap range 0.32–0.50 s; low per-lap autocorr/drift.
- JITTER: car/pos cadence-residual IQR ~0.128–0.141 s; sector-crossing |median| 0.10–0.16 s.
- CHI-SQUARE: **78.7–3292** (vs 0a's 0.60–11.14), explained as dominated by the unremoved
  inter-stream offset's arc term (not positional noise) — routed to G3 for the F1 band call.

## Close Criteria (each a review check)
- Raw streams only; NO `get_telemetry` (AST-check); offline; no network; no evo imports; no DB
  writes; no estimator deliverable; 0a primitives imported not forked.
- pos_data decimetre handling correct in the arc-length construction.
- Jitter measured against BOTH a cadence fit AND DB sector-crossing truth, with a distribution.
- Error-model classification is EVIDENCE-BACKED (the discriminating statistics actually
  distinguish the classes) — not asserted. Sanity-check: does "white-jitter" + the SG-autocorr
  caveat hold up? Re-compute the dt-deviation autocorrelation on ONE session/driver yourself.
- Offset stability correctly distinguishes estimable bias from wander, is consistent with 0a's
  reported per-lap ranges, and the stable verdict follows from the numbers. Spot-check ONE
  session's per-lap offset spread independently.
- The chi-square computation is sound and the "offset-dominated" interpretation is correct
  (verify: is the residual genuinely the offset-inclusive speed_arc − position_arc, and would
  removing the per-lap offset bring chi-square down? A quick check on one session is enough).
- Numbers traceable to the JSON.

## Allowed Scope
`scripts/characterize_timetag_jitter.py`; `.agent-work/issue-447/evidence/*.json`; read-only
reuse of 0a primitives. You MAY write throwaway verification scripts (not in scripts/; clean up).

## Specific Exclusions (flag if touched)
`get_telemetry`/merged; network; estimator/filter as deliverable; evo imports; DB writes;
forking 0a primitives; any GO/NO-GO decision.

## Constraints the Implementation Must Respect
- Raw streams only via offline_loader; offline cache; pos_data DECIMETRES.
- Sector truth via db_truth_loader (`file:?mode=ro`); `py` not `python`.
- Characterization only.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing` — `trajectory_grading/{cross_residual,db_truth_loader}`; `scripts/`.
- **Capability:** inter-stream correlatability characterization — the GO/NO-GO core.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; characterization-only.
- **Decision anchors:** F2 (stable bias vs wander); error-model class; 0a's diagnostic-not-gate split.
- **Evidence expectations:** jitter distribution, evidence-backed error-model class, offset
  stability verdict, chi-square — all traceable to script + session. These feed the human's
  GO/NO-GO; the stable-vs-wander call and error-model class are the load-bearing ones.

## Evidence Produced
6 per-session `jitter_offset_*.json` + summary. Implementer reports 0a primitive tests green
(47 trajectory_grading + 129 physics). Script is 1240 lines (over the <1000 ADVISORY; it is a
`scripts/` file, not `src/`; function-level limits satisfied) — note it but it is not a `src/`
gate violation. Verify that judgement.

## Suggested Model Tier
stronger — reason: the stable-vs-wander verdict and error-model classification drive the epic
GO/NO-GO; the chi-square interpretation is subtle. Needs independent re-computation of at least
one discriminator.

## Stop Conditions
BLOCK if: diff/evidence inaccessible; the stable-vs-wander verdict or error-model class is not
supported by the data (give your corrected finding); the chi-square interpretation is wrong; a
constraint was violated; an estimator was built.

## Return Format
Return REVIEW_RESULT to
`C:/Programs/f1Brainz-worktrees/cmdr-447/.agent-work/issue-447/crew-handoffs/g2-review-result.md`:
verdict (APPROVE or BLOCK), per-check findings INCLUDING your independent re-computation(s),
blockers, out-of-scope observations, workflow feedback. Then a concise final message with the
verdict.
