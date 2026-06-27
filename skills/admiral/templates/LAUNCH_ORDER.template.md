# Launch Order: `<commander id — issue>`

Commanders start cold. Paste, don't point.

## Mission
`<the issue, the verdict or deliverable required, and how it serves the epic intent>`

## Prior-Wave Verdicts (pasted)
`<full verdict text from prior waves/issues this mission depends on — never a bare link or issue number>`

## Pre-Rulings
Ruled in advance, each overridable if evidence contradicts it — say so when overriding.
- `<ruling>`

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

## Inherited Latitude
`<decision classes this Commander may exercise vs must float to the Admiral; from the latitude contract>`

## File Ownership
`<assigned findings file — sole writer this wave; any shared-file fences>`

## Workspace
`<absolute worktree path, provisioned for you via "git worktree add" — branch name, base commit, and the exact add command that created it. Verify main freshness before dispatch. Worktrees lack untracked inputs; see Data Locations.>`
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here <absolute worktree path>` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

## Inherited Context
`<Active lessons from .agent-work/LESSONS.md relevant to this mission; platform/technical invariants from the project playbook (encodings, shell quirks, crew-launch rules)>`

## Data Locations
`<absolute paths into the main checkout for untracked inputs (DBs, model artifacts) — worktrees do not contain them>`

## Budget
`<model tier, compute/time budget, session-window notes>`

## Stop Conditions
Stop and return when: `<conditions — scope exceeded, decision outside inherited latitude needed, budget crossed, evidence impossible>`, or when you need **context the launch order does not cover and cannot safely proceed without** — return-and-query the Admiral (it answers and continues you). Asking up is always sanctioned.

## Return Shape
`<the required form of the final report: verdict + evidence + map impact + triage candidates + workflow feedback; where the verdict gets posted. Include your "verify_worktree_isolation.py --here" confirmation (the matched worktree path) as evidence you worked in isolation.>`
