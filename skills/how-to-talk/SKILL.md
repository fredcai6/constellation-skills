---
name: constellation-how-to-talk
description: Keep prose clear, concise, and grounded in real meaning — every sentence carrying one point in the plainest words that fit. Use when composing or revising any human-facing text an agent produces: reports, review comments, design notes, PR bodies, docs. Not a banned-word list (it prescribes what to do, never words to avoid) and not skill-goodness (which judges a skill's design, not its prose).
invoker: agent
---

# Constellation How-to-Talk

Before you hand any prose to a human, make each sentence carry one grounded point in the plainest words that fit. Clarity, concision, and grounded meaning are the whole job; the slop everyone complains about is just their absence.

**No checklist. Apply the discipline directly** — it runs on *every* prose artifact you write, not as a workflow you start and finish. The predictable procedure is one pass over your own draft against the rules below before you return it.

## The rules

**Words carry meaning.**

1. Use the plainest word that carries the exact meaning.
2. Use one name for one thing, and keep it the same throughout (the project `GLOSSARY.md` is the source of truth — see below).
3. Prefer the verb to its noun form — *decide*, not *make a decision*.
4. Choose each word for what it means, not the register it signals. Every word should be one the reader could act on.

**Sentences point at one thing.**

5. Write in the active voice and name who acts.
6. Give each sentence one main idea; start a new sentence at the second claim.
7. State it positively — *runs only when X*, not *fails unless X*.
8. Make every sentence advance a fact, a claim, or a next step.
9. Say what a thing *is*, directly.

**Claims are grounded.**

10. Ground each claim in the thing itself — the number, the log, the benchmark, the diff. Show it rather than assert it.
11. When it is your judgment, say so plainly instead of borrowing vague authority.
12. State your confidence once, then commit. When the evidence points one way, make the call — no false balance, no flattery.

**Structure serves the reader.**

13. Open on the substance.
14. Lead with the point when the reader needs it fast; let the context follow.
15. Give the background that helps; cut what only repeats.

## Dials, not laws

These rules illuminate the point of a sentence; they do not build an austere language. Passive voice is right when the actor is unknown or beside the point. Adverbs that carry information stay — cut only the empty intensifier. An em-dash or a genuine three-item list is fine; the tell is reflex, not the mark. There is no word-count cap on a sentence. Break any rule here sooner than write something stilted.

## You may

The myths below are not rules — following them produces worse prose, so ignore them: you *may* use the passive voice, split an infinitive, end a sentence with a preposition, begin one with *And* or *But*, and write *I* or *we* when that is who acted.

## One name for one thing — the glossary

Rule 2 is enforced by the project glossary, not by memory. `templates/GLOSSARY.template.md` is the shape: **Term · Short · Definition · Instead of**. The *Instead of* column is one-way by construction — it names a variant only to point away from it, never as a synonym to swap in. Consult the glossary before naming a concept; add a row when you coin one.

## The one rail

`py scripts/verify_skill_registered.py --skill how-to-talk` proves this skill is well-formed and installed — nothing more. There is no linter over the prose: whether a draft is clear, concise, and grounded is the writer's judgment and, for a shipped artifact, the independent reviewer's. Fix the writing, never lower the bar to pass.
