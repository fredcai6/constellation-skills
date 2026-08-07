---
name: constellation-how-to-talk
description: Keep an agent's prose clear, concise, and grounded — each sentence one point in the plainest words — so meaning stays consistent across artifacts, agents, and sessions. Use when writing or revising any report, review comment, design note, PR body, doc, or internal note.
invoker: agent
---

# Constellation How-to-Talk

Make each sentence carry one grounded point in the plainest words that fit — in anything you write, whether a human reads it, another agent does, or a later session does. Clarity, concision, and grounded meaning are the whole job.

**No checklist. Apply the discipline directly** — it runs on *every* artifact you write, not as a workflow you start and finish. The predictable procedure is one pass over your own draft against the rules below before you return it.

## The rules

**Words carry meaning.**

1. Use the plainest word that carries the exact meaning.
2. Use one name for one thing, and keep it the same throughout (`docs/agents/GLOSSARY.md` is the source of truth — see below).
3. Prefer the verb to its noun form — *decide*, not *make a decision*.
4. Choose each word for what it means, not the register it signals. Every word should be one the reader could act on.

**Sentences point at one thing.**

5. Write in the active voice and name who acts.
6. Give each sentence one main idea; start a new sentence at the second claim.
7. State it positively — *runs only when X*, not *fails unless X*.
8. Make every sentence advance a fact, a claim, or a next step.
9. Say what a thing *is*, not what it is "responsible for."

**Claims are grounded.**

10. Ground each claim in the thing itself — the number, the log, the benchmark, the diff. Show it rather than assert it.
11. When it is your judgment, say so plainly instead of borrowing vague authority.
12. State your confidence once, then commit. When the evidence points one way, make the call — no false balance, no flattery.

**Structure serves the reader.**

13. Open on the substance and lead with the point when the reader needs it fast; let the context follow.
14. Give the background that helps; cut what only repeats.

## Dials, not laws

These rules illuminate the point of a sentence; they do not build an austere language. Active voice (rule 5) is the default, but the passive is right when the actor is unknown or beside the point. Break any rule here sooner than write something stilted.

## One name for one thing — the glossary

Rule 2 holds only if names stay fixed across artifacts, agents, and sessions, so it is backed by the project glossary rather than memory. `docs/agents/GLOSSARY.md` — compiled and confirmed by `constellation-charter`, read by every role — is that source of truth. Consult it before naming a concept; when a term is missing, propose a canonical one rather than coining a synonym.
