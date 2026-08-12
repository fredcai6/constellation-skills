# Excursion Brief: `<short title>`

The single dispatch template for all three excursion types. One excursion answers **one named question** — if you have two questions, write two briefs. Record this brief on the ideas board **before** dispatch, then dispatch as a **background** subagent through `run_crew.py` (run `recover_crews.py <work-id>` before dispatch and before consolidation). Either side may initiate — human or agent proposal — same brief either way.

## The one named question

`<the ONE question this excursion exists to answer. Not a topic — a question with an answerable shape.>`

## Type

`research | prototype | design-it-twice`

**Why this type:** `<one line — research for facts/prior art, prototype to feel out a shape in code, design-it-twice to compare interfaces under constraints>`

## What "answered" looks like

`<the concrete finding that ends this excursion — a cited fact, a working spike verdict, a recommended interface. State it as the on-ramp deliverable that lands on the board before consolidation.>`

## Budget / stop conditions

- `<budget: time / attempts / variant count before reporting back, even inconclusive>`
- `<what NOT to build or touch>`
- **Scoped nulls:** a null verdict states what was and what was **NOT tested** — it kills *this test under these conditions*, never the idea class. Default next move after a null is another variant.

---

Fill exactly ONE of the three type sections below — the one named in **Type**.

## Research excursion

- **Sources:** `<primary sources required — web, academia, codebase; name where to look first>`
- **Findings format:** `<cited findings; each claim carries its source; contradictions surfaced, not smoothed>`

## Design-it-twice excursion

This type is the **design-phase form** of the shared parallel-alternatives standard — the reusable contract lives at `references/design-it-twice-brief.md`, including the not-a-proposal framing block and the untaken-road / panel-vs-single records.

- **Parallel agents:** `<3+ agents design the SAME module's interface, each under a distinct constraint: minimal-interface / max-flexibility / common-caller-first / ports-and-adapters>`
- **Compared on:** `<depth, locality, seam placement, testability>`
- **Output:** `<an opinionated recommendation or a named hybrid — not a menu>`

## Prototype excursion

Dispatches **constellation-prototyper**. The six fields below are **identical to `PROTOTYPE_HANDOFF`'s** so nothing is typed twice — copied verbatim from `skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md`. Fill every field; a missing question or branch sends this back.

## Question
`<the ONE named design question this prototype exists to answer. If there are two questions, write two handoffs.>`

## Branch
`logic | ui | measurement`

**Why this branch:** `<one line — which decision rule in the prototyper SKILL.md put it here>`

## Host-project conventions
- **Runtime / language:** `<e.g. Node 20 + TypeScript | Python 3.12 | Go>`
- **Task runner:** `<how the one command is invoked — npm script, make target, just recipe, bare command>`
- **Routing:** `<ui only: how routes/query params work in this app; else n/a>`
- **Other conventions the prototype must match:** `<framework, package manager, dir layout — or none>`

## Location
`in-repo | worktree`

**Driver:** `<human-driven → in-repo, marked, one command | agent-driven → throwaway worktree>`

## Stop conditions
- `<what "answered" looks like — the condition that ends the prototype>`
- `<budget: time / attempts / variant count before reporting back inconclusive>`
- `<any exclusion — what NOT to build or touch>`

## Return format
`PROTOTYPE_RESULT` — the answer, what was tested and what was NOT tested, what it taught, any surviving module, and the disposition. The result lands in the cycle record and on the ideas board before consolidation.
