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
| Fix-now triage (bounded fix applied immediately, not filed as an issue) | `surfaced | delegated` |
| Spend / budget / model tier | `surfaced | delegated` |
| Production defaults / user-visible behavior | `surfaced | delegated` |
| `<project-specific class>` | `surfaced | delegated` |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — may the fleet apply a ripe lesson to a project doc/template (and export constellation debt) without surfacing, or must each apply be surfaced? Default: surface. When delegated, applies are logged as rulings in ADMIRAL_LOG; constellation lessons are always exported, never silently confirmed.

## Permission prerequisites
A `delegated` disposition above settles who decides, not what the harness permission classifier will let through — it can veto the concrete action at runtime regardless of the ruling. For each **delegated** class in Decision Classes, fill one row before wave 1: the external actions it implies, and either a pre-clearance (settings allowlist entry, granted now) or a recorded fallback (what happens when the classifier vetoes anyway).

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| `<delegated class from above>` | `<e.g. merge, issue create/comment, push, cross-repo write>` | `<allowlist entry pre-cleared | fallback: <ruling to make when vetoed>>` |

**Worked example.** The classifier refused a delegated `gh pr merge` mid-run; nothing here had recorded that this could happen. The human ruled live: "approve now; batch the rest" — logged in ADMIRAL_LOG. Absent a pre-clearance, that is the default fallback shape: one human approval in the moment, remaining equivalent actions batched to the next checkpoint instead of re-litigated one at a time.

## Float-Up Routing
When a Commander floats — a `user-decision` **or a context query**: for a decision, adjudicate inside delegated classes and log a RULING, escalate surfaced classes and out-of-taxonomy to the human. For a **context query** (the Commander needs a fact or clarification it lacks), answer from epic knowledge and continue it; reach the human out-of-band when the answer is beyond your knowledge or latitude — a delegate is not a replacement, so "I need to talk to my human" is always available. `<any per-class nuance>`

## Comms
`<plain English by default, technical depth on demand | other>`

## Budget / Model Parameters
`<commander model tier(s), crew model tier(s), compute/time budgets per issue, session-window awareness>`
**Usage-limit budget.** Treat the account session pool (the shared usage-limit window) as a **wave-sizing input**, not merely a per-issue budget: size each wave to what the pool can carry, and when a limit **reset** is near, **defer the next wave's dispatch past the reset rather than launching into it** — a wave that trips the limit mid-flight strands its Commanders worse than one that waited.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by the human at any checkpoint.
Grade each pre-ruling with an `@grade` child line so a Commander inheriting it knows whether it may
revisit it freely or must float back (see `references/global-everyone.md`, "Decision fixedness"):
```
- decision:wave-0-is-five-wide — launch all five wave-0 issues concurrently.
  @grade: settled/human · leans wave-0
- decision:coverage-floor — the engine coverage floor is 85%.
  @grade: guess · leans c-ci · settle: measure current coverage once, set the floor just under it
```
- `<pre-ruling>`
  `@grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]`

## Expiry
`<time (e.g. 48h) or event (e.g. "after wave 2 merge") — crossing it forces a contract-refresh decision before further dispatch>`

## Confirmation
`<date — confirmed by user; record as user-decision evidence on the latitude step>`
