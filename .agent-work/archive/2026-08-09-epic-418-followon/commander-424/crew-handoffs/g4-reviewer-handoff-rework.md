# Reviewer handoff — gate `g4-review`, REWORK (attempt 2)

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g4-review` (rework)
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch order.

## Your BLOCK was correct and was acted on, not overridden

You hand-parsed `rep2-cli/record.jsonl` and found a shell `for` loop that ran the engine six times
but scored as one, because the scorer counted static occurrences of `checklist_engine.py` in the
command text. You were right. `rep2-cli` is **23 attempts / 7 fumbles**, not the published 18 / 2.
I reproduced your finding directly against the raw record before changing anything.

What changed since:

1. **The loop undercount is fixed.** Static text is now a floor; the count is the larger of the
   static occurrences and the engine-output marks (`RAIL:` / `usage:`) in the result. Re-scoring
   reproduces **your** numbers for `rep2-cli` exactly: 23 / 7.
2. **Your second triage candidate is fixed too** — the far-side detector now counts non-engine `Bash`
   calls, closing the blind spot on the arm most likely to recover that way.
3. **New: `evidence/g4-dc5/control_scorer.py`**, positive controls proving every counter that reports
   zero in the real arms can report non-zero. Writing them surfaced a **fourth** scorer defect you did
   not find and neither did I by reading: one argparse rejection scored as two shape errors. Fixed.
4. **MEASUREMENT.md is rewritten where it was wrong.** The old basis for the DC5 negative — "the
   spreads overlap completely" — is **false** after your correction and has been removed. The
   corrected totals (CLI 22.0 vs MCP 18.0, non-overlapping) make the raw-total comparison look like a
   win for the door. The verdict is still a measured negative, but it now rests on a decomposition:
   strip the one-off `--help` reads and the CLI arm is **cheaper on productive invocations, 16 vs 18**
   (16 in both replicates), and cheaper still on acts of attention, 10 vs 18.
5. A revision note at the foot of MEASUREMENT.md records all of this, including that correcting your
   finding moved the raw numbers **toward** the door.

## What to check this time

1. **Re-derive `rep2-cli` again** and confirm it now reads 23 / 7 — your own numbers.
2. **Check the other three arms did not move**, and that the loop fix did not over-correct anything
   into existence. `rep1-cli` 21/5, `rep1-mcp` 19/0, `rep2-mcp` 17/0.
3. **Audit `control_scorer.py` itself.** Positive controls that pass vacuously would be worse than
   none. Confirm each control would fail if the counter it exercises were broken — break one and see.
4. **The verdict now rests on the productive-invocation decomposition** (attempts minus help reads).
   Check that arithmetic against the raw records, and say plainly whether you think the decomposition
   is legitimate or whether it is post-hoc reasoning reached for once the raw totals stopped
   supporting the original conclusion. **That is the question I most want answered, and "it is
   post-hoc" is an answer I will accept and act on.**
5. **Re-check the honest-null clause against the new text**, including whether n=2 claims are now
   correctly bounded (the file explicitly declines to claim a confidence interval and rests on
   direction plus exact-tie replicates).
6. Everything you already verified and found clean — DC1's assertion, the MCP counts, the
   corroboration-only server log, order control, the `dc6-mcp` UNMEASURED call, DC6's arrival/action/
   stop-ignored split — you may confirm briefly rather than re-derive from scratch, **except** where
   the loop fix could have touched it.

## Verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-mcp
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-mcp
python3 evidence/g4-dc5/assert_dc1.py evidence/g4-dc5/rep1-mcp evidence/g4-dc5/rep2-mcp
python3 evidence/g4-dc5/control_scorer.py
```

Do not rerun the measurement arms. If you believe a re-run is required to settle something, say so
and block.

## What I want from you

Same standing rule: **a measured negative that re-derives cleanly is an APPROVE, not a BLOCK**, and a
second BLOCK is fully acceptable — I acted on your first one rather than overriding it and I will act
on another. A number that does not re-derive, a vacuous control, or a decomposition you judge
post-hoc are all blocking findings.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g4-reviewer-result-rework.md
```

**Write that file before ending your turn — the write is the delivery.** Verdict as a bare `APPROVE`
or `BLOCK` on its own line. Include a blunt `## Workflow Feedback` section. Log out-of-scope finds as
triage candidates.
