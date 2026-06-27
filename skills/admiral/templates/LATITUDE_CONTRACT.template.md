# Latitude Contract: `<epic-id>`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
`<what the epic is for; the outcome that must not be violated>`

## Success Shape
`<what done looks like — including whether a measured negative (honest null) is a complete, successful deliverable>`

## Checkpoint Protocol
`<stop-and-present at every wave boundary | cleared autonomous through checkpoint <N> | cleared to completion>`
`<what reaches the user at a checkpoint: plain-English summary, decision asks, evidence on demand>`

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | `surfaced | delegated` |
| Scope change (issue added/dropped/re-scoped) | `surfaced | delegated` |
| Merge to main | `surfaced | delegated` |
| Issue filing / closing | `surfaced | delegated` |
| Spend / budget / model tier | `surfaced | delegated` |
| Production defaults / user-visible behavior | `surfaced | delegated` |
| `<project-specific class>` | `surfaced | delegated` |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Float-Up Routing
When a Commander floats — a `user-decision` **or a context query**: for a decision, adjudicate inside delegated classes and log a RULING, escalate surfaced classes and out-of-taxonomy to the human. For a **context query** (the Commander needs a fact or clarification it lacks), answer from epic knowledge and continue it; reach the human out-of-band when the answer is beyond your knowledge or latitude — a delegate is not a replacement, so "I need to talk to my human" is always available. `<any per-class nuance>`

## Comms
`<plain English by default, technical depth on demand | other>`

## Budget / Model Parameters
`<commander model tier(s), crew model tier(s), compute/time budgets per issue, session-window awareness>`

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by the human at any checkpoint.
- `<pre-ruling>`

## Expiry
`<time (e.g. 48h) or event (e.g. "after wave 2 merge") — crossing it forces a contract-refresh decision before further dispatch>`

## Confirmation
`<date — confirmed by user; record as user-decision evidence on the latitude step>`
