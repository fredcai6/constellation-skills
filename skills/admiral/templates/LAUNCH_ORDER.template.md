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
NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

## Inherited Context
`<Active lessons from .agent-work/LESSONS.md relevant to this mission; platform/technical invariants from the project playbook (encodings, shell quirks, crew-launch rules)>`
**Charter-lite carrier:** when the target project has no `docs/agents/` overlay, this block doubles as the doctrine carrier — the thin doctrine deltas the Commander would otherwise read from `docs/agents/*` ride inline here.

## Pre-empted Steps
`<spine steps the Admiral has already performed or ratified this wave — so the Commander cites this launch order rather than redoing them (e.g. context already established, plan already frozen); omit a step you have not pre-empted>`

## Data Locations
`<absolute paths into the main checkout for untracked inputs (DBs, model artifacts) — worktrees do not contain them>`

## Budget
- **Model tier (required):** `<the model tier this dispatch runs at — every dispatch names one, never left unset>`. Pick the least-powerful model that can do the job; escalate the tier only when complexity, ambiguity, or risk demands it.
- **Compute/time, session-window:** `<compute/time budget, session-window notes>`

## Stop Conditions
Stop and return when: `<conditions — scope exceeded, decision outside inherited latitude needed, budget crossed, evidence impossible>`, or when you need **context the launch order does not cover and cannot safely proceed without** — return-and-query the Admiral (it answers and continues you). Asking up is always sanctioned.

## Return Shape
`<the required form of the final report: verdict + evidence + map impact + triage candidates + workflow feedback; where the verdict gets posted. Include your "verify_worktree_isolation.py --here" confirmation (the matched worktree path) as evidence you worked in isolation.>`
Write your result artifact and send your verdict **before** going idle: an idle notification with no artifact reads as stalled, not done, so deliver first — the Admiral judges completion from what you produced, not from a message that arrives after you've already gone quiet.
When you open the PR on Windows, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc or a PowerShell `@'...'@` here-string `--body` (both fail for PR bodies; here-strings work for `git commit -m` only). See `references/fleet-doctrine.md`, "Windows shell hazards".
