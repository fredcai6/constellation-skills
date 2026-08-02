# Reviewer Handoff — G3 VERDICT composition review (issue #375)

You are a constellation-reviewer. INDEPENDENT verification of the final #375 verdict document and the
honest-null decision. Worktree root (cd here):
`C:\Programs\f1Brainz\.claude\worktrees\agent-a2d028d13259581aa`. Windows; `py` not `python`;
`PYTHONIOENCODING=utf-8` in shells that capture subprocess output. Branch
`constellation/issue-375-race-day-conditioned-net`.

## Gate
g3 VERDICT. The deliverable is the verdict section "# Issue #375 — G2/G3 VERDICT" appended to
`docs/evo/fusion_rework_findings.md` (commit bee18e7), plus the honest-null DECISION (no production
wiring; #375 not closed). This document is what the user reads to decide #375's fate, so its accuracy is
load-bearing. There is NO production code in G3 (honest-null ⇒ no wiring) — that ABSENCE is itself a
thing to verify.

## What to verify

1. **Every number in the verdict section matches the evidence JSON.** Open
   `.agent-work/issue-375-race-day-conditioned-net/evidence/g2_conditioned_net.json` and confirm the
   doc's race table is faithful:
   - pairwise-LL gap +0.00497, CI [+0.00203,+0.00775]
   - sign-acc delta +0.00140, CI [−0.00093,+0.00388] (includes 0)
   - Spearman delta +0.00008, CI [−0.00263,+0.00304] (includes 0)
   - Model1 LOSO LL ~0.47736; seed stability +0.00497/+0.00632/+0.00512; 173 events / 30149 pairs / 0 dropped
   - `win_null` == "NULL"
   Flag ANY mismatch or rounding that misleads.

2. **The two-part criterion is stated correctly and the NULL follows mechanically.** Criterion 1
   (ordering: sign-acc AND Spearman CI excluding 0) FAILS; therefore NULL even though criterion 2 (LL
   bar) passes. Confirm the doc says exactly this and does NOT overclaim the LL gain as an ordering win.

3. **The honest-null DECISION is correctly implemented (verify the ABSENCE of wiring).**
   - `git diff 3fbbc6f --stat -- src/evo_predictor/sampled_runtime.py` → MUST be empty (no production
     wiring for a losing net).
   - `git diff 3fbbc6f --stat -- src/evo_predictor/quali_pace_anchor.py docs/evo/prediction_ceiling_and_priorities.md`
     → MUST be empty (protected files untouched).
   - The full non-agentwork changeset (`git diff --stat 3fbbc6f -- ':!.agent-work'`) should be exactly:
     fusion_rework_findings.md, g1_ordering_reconcile.py, g2_conditioned_net.py, generate_records.py,
     fusion_conditioned_net.py, test_fusion_conditioned_net.py, test_g1_ordering_reconcile.py. Flag any
     extra/unexpected file.

4. **G1↔G2 narrative consistency.** The G2 verdict must be consistent with the G1 section: G1 said the
   prior-stage-order encoding was the untested lever; G2 added it and it was still flat on ordering. The
   doc should close that loop honestly (no contradiction between sections).

5. **Tests green (no regressions) — re-run yourself:**
   ```
   PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q
   ```
   Expect ~473 passed, 13 skipped, 0 failures. Flag any failure.

6. **Follow-ups are honest, not padding.** The doc lists triage candidates (calibration-only heads,
   uncertainty-head measurement). Confirm these are framed as DEFERRED/out-of-scope, not as work this PR
   did. Confirm the uncertainty head is honestly described as built-but-unmeasured.

7. **No "Closes #375" anywhere in the committed work** (that belongs only on a winning verdict; this is a
   null). Check the doc and commit messages do not imply closure.

## Specific Exclusions (flag if touched)
`quali_pace_anchor.py` + config keys, `prediction_ceiling_and_priorities.md`, `sampled_runtime.py`.

## Stop Conditions
BLOCK if: a verdict number is wrong or misleading; the NULL does not follow the stated criterion; ANY
production wiring or protected-file edit slipped in; tests fail; the doc overclaims or implies #375 is
closed; the G1/G2 narrative contradicts.

## Suggested Model Tier
standard — doc-vs-evidence verification + invariant checks.

## Return Format
REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings with the values you confirmed, any
mismatch, the git-stat confirmation of the honest-null absence-of-wiring, test output, blockers,
out-of-scope observations.
