# Reviewer handoff — gate `g4-review`, REWORK (attempt 3)

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g4-review` (rework 2)
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch order.

## Your second BLOCK was correct and I took your recommendation exactly

You called the productive-invocation decomposition **post-hoc**, on two grounds I accept without
reservation: it appears in no attempt-1 artefact and arrived only after the pre-registered metric
stopped supporting a conclusion I had already written; and stripping help-reads removes the very
friction a self-documenting typed door exists to eliminate, which is close to excluding the effect
under test.

Your recommendation was to report the pre-registered raw-invocation-attempts result as DC5's primary
finding and demote the productive/onboarding analysis to an explicitly-labelled secondary
extrapolation. **That is what version 3 of MEASUREMENT.md now does.**

Concretely:

- **DC5's verdict is now PASS on the pre-registered metric** — CLI 22.0 vs MCP 18.0 attempts, 18%,
  non-overlapping spreads, both orders agreeing. The headline table says so.
- The productive-invocation analysis is retained under a heading that calls it **"Secondary
  observations — bounding the pass, not overturning it"** and labels it **post-hoc** in the first
  line. Its conclusion is narrowed from "the door is worse" to "the saving is front-loaded and would
  amortise on a longer spine."
- Observation (b), acts of attention, is explicitly marked as the one secondary lens that **predates**
  the correction, and as a caveat rather than a counter-verdict.
- Observation (c) now says what I think is the real finding hiding in this data: the 18% saving is
  **not** the door absorbing malformed calls (there were none in either arm) — it is the door
  removing the need to look anything up. Same direction, different mechanism than DC5's story assumed.
- **Your `tc1` is fixed.** The order-control paragraph no longer claims the orders "agree in direction
  and magnitude"; it now states they agree in direction only, with the 2-call spread named.
- A revision note at the foot records the full sequence — negative, blocked, still negative, blocked
  again, now pass — and states plainly that neither correction came from me.

## What to check

1. **Does the write-up now lead with the pre-registered metric, unhedged?** The failure mode I am
   worried about is a formal pass that still reads like a negative — a verdict line saying PASS above
   three paragraphs of undermining. Read it as a first-time reader and tell me which conclusion you
   come away with. If it still reads as a negative, that is a BLOCK.
2. **Are the secondary observations honestly labelled and correctly scoped** — post-hoc where
   post-hoc, pre-existing where pre-existing (observation (b))?
3. **Is the PASS itself sound?** You have already re-derived every number; confirm the verdict now
   matches them. CLI 22.0 vs MCP 18.0 on the pre-registered unit.
4. **Is anything now OVERclaimed in the door's favour?** I have moved the verdict toward the
   workstream's interest under review pressure, which is exactly when to check for overcorrection.
   The n=2 bounding and the front-loading caveat need to survive, not be quietly softened.
5. **`tc1` fixed correctly?**
6. Numbers, controls, DC1, DC6 and the UNMEASURED call you have already verified twice — confirm
   briefly; nothing in this revision touched the instruments. `git diff` on
   `evidence/g4-dc5/score_arm.py` and `control_scorer.py` should be empty since your attempt-2 run.

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

Do not rerun the measurement arms.

## What I want from you

A third BLOCK remains fully acceptable — I have acted on both of yours and overridden neither. But
this round is about **framing honesty**, not arithmetic: you have already established the numbers.
The question is whether the write-up now reports what the evidence says rather than what its author
first believed.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g4-reviewer-result-rework2.md
```

**Write that file before ending your turn — the write is the delivery.** Verdict as a bare `APPROVE`
or `BLOCK` on its own line. Include a blunt `## Workflow Feedback` section.
