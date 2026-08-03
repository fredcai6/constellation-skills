# Prototype Handoff: `<short title>`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

One question in, one scoped answer out. Fill every field — a missing question or branch sends this handoff back.

## Question
`<the ONE named design question this prototype exists to answer. If there are two questions, write two handoffs.>`

## Branch
`logic | ui | measurement`

**Why this branch:** `<one line — which decision rule in SKILL.md put it here>`

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
`PROTOTYPE_RESULT` (see `templates/PROTOTYPE_RESULT.template.md`) — the answer, what was tested and what was NOT tested, what it taught, any surviving module, and the disposition.
