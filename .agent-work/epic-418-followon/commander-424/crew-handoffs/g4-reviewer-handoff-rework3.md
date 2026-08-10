# Reviewer handoff — gate `g4-review`, REWORK (attempt 4) — two mechanical fixes only

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g4-review` (rework 3)
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`

You flagged both defects as one-edit-each and said a fourth round should be fast. Agreed. This round
is scoped to exactly those two edits plus a check that nothing else moved.

## Fix 1 — leftover duplicate paragraph, deleted

The unedited draft remnant that repeated secondary observation (c) in flatter, more negative,
unmitigated language is **gone**. Observation (c) now appears once, in its mitigated form.

## Fix 2 — `tc1`, properly this time

You were right that my replacement arithmetic did not support its own claim: quoting the within-arm
cross-order spread as "2 and 2" reads as agreement, and the evidence that actually motivated your
original finding — the per-order CLI-vs-MCP gap — had disappeared from the text.

It is back and it is now the load-bearing number. The order-control paragraph states the gap is
**2 attempts in rep1 (21 vs 19) and 6 in rep2 (23 vs 17)** — same direction, threefold difference in
size, on the very quantity the headline 18% averages. The paragraph now concludes that the order
control supports direction only and says nothing about effect size.

I propagated that consequence rather than leaving it in one paragraph:

- the **headline table** now reads "The 18% is a midpoint, not an estimate: the per-order gap is 2 and 6";
- the **DC5 PASS section** carries the same caveat immediately under the headline number, pointing
  back to the order-control paragraph.

## What to check

1. The duplicate paragraph is gone and observation (c) survives once, mitigated.
2. The order-control paragraph's arithmetic now supports its own claim, and the 2-vs-6 figures are
   correct against the raw scores.
3. The midpoint caveat is consistent in all three places it now appears (headline table, DC5 section,
   order control) and does not contradict itself.
4. **Nothing else moved.** No number changed, no verdict changed, no caveat was softened while I was
   in the file. DC5 is still PASS on the pre-registered metric; the secondary observations are still
   labelled as they were.
5. Instruments untouched: `git diff` on `evidence/g4-dc5/score_arm.py` and `control_scorer.py` empty.

## Verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-cli
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep1-mcp
python3 evidence/g4-dc5/score_arm.py evidence/g4-dc5/rep2-mcp
python3 evidence/g4-dc5/control_scorer.py
```

Do not rerun the measurement arms. You have re-derived every number three times; confirm the two
edits and the no-drift check rather than starting over.

## What I want from you

If these two edits land, **APPROVE**. If either is still wrong, block again and I will fix it again —
you have found something real in every round and I have overridden nothing.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g4-reviewer-result-rework3.md
```

**Write that file before ending your turn — the write is the delivery.** Verdict as a bare `APPROVE`
or `BLOCK` on its own line. Include a `## Workflow Feedback` section.
