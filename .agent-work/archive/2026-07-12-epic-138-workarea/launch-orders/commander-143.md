# Launch Order: `commander-143 — issue #143 (fencing-aware feedback/archive gates, fixes #134)`

## Mission
Implement https://github.com/fredcai6/constellation-skills/issues/143 — the `feedback`/`archive` engine gate conditions accept a worktree-local staged trio under a launch-order fence, killing the mandatory waive. Closes #134. Deliverable: a green, reviewed PR on branch `issue-143`.

## Prior-Wave Verdicts (pasted)
From issue #134 (surfaced by the #129–#131 delegated commander closeout, 2026-07-11): the engine's `feedback` and `archive` gate conditions hard-require writes to the durable root's canonical `AGENT_FEEDBACK.md`/`LESSONS.md` (durable_root resolves to the MAIN checkout via git-common-dir), but Admiral launch-order fences forbid delegated commanders from writing to the main checkout — one-writer isolation with harvest-at-closeout is the point. Result: every fenced delegated commander must waive engine gates on Admiral authority to close out. A mandatory-waive gate is a broken gate.

From the CONFIRMED #138 spec (§D5), the chosen shape (option 1; option 2 — a new fencing-aware engine verb — was REJECTED as disproportionate): the gate passes if EITHER (a) the canonical durable-root files were written, OR (b) the worktree-local staging paths exist AND an evidence artifact attaches the staged path + a fence citation (launch-order reference). The Admiral's harvest-before-sweep substep remains the owner of the canonical write. Invariant preserved: a fence citation WITHOUT a staged trio still FAILS — learning cannot be silently dropped.

## Pre-Rulings
- Unfenced-run behavior is byte-for-byte unchanged — regression-test it.
- The staged-trio unit-test fixture is built from the ACTUAL worktree-local trio the #129–#131 delegated commander emitted at closeout (the run that surfaced #134) — not an invented shape. Hunt for it in the main checkout's `.agent-work/` archives and the merged PR history of that arc; if genuinely unrecoverable, reconstruct from the delegated-commander skill's staging instructions, record the provenance honestly in the PR, and flag it as a scoped null on the fixture-realism claim.
- Update the delegated-commander/admiral doctrine text that currently instructs the waive: it should now instruct staging + evidence attachment. (Doctrine text edits are in-scope ONLY where they name the waive workaround — do not wander into #142's clamp territory.)
- No new engine verbs (rejected at review). No schema changes beyond the gate-condition logic.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

## Inherited Latitude
You may: implementation-detail decisions (evidence field names, staging-path convention — document them). You must float: new verbs, schema changes, invariant weakening, anything touching eval task.md. Merges are the human's — open the PR, never merge.

## File Ownership
Sole writer of: the gate-condition logic in the engine templates/scripts this change requires, your tests, the waive-instruction doctrine lines it replaces, and `.agent-work/epic-138/verdicts/commander-143.md` (MAIN checkout, absolute path below). COORDINATION FENCE: #140 owns `scripts/checklist_engine.py`'s response/output surface this wave. If your gate change must touch `checklist_engine.py` itself (likely — gates live there), confine your diff to gate-evaluation logic, stay out of output/response formatting entirely, and note the shared-file fence in your PR body so the Admiral sequences the merges.

## Workspace
`C:/Programs/constellation-wt-143` — branch `issue-143`, base commit 93f38505 (main), created via `git worktree add ../constellation-wt-143 -b issue-143 main`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-143` — must exit 0; paste output into your report.
NOTE: PR integration defaults to **server-side merge**.

## Inherited Context
- Windows/py launcher conventions; UTF-8 writes; `gh pr create -F <tempfile>` for PR bodies.
- Superpowers is a competitor — never cite or import its doctrine.
- Engine reference: `skills/workbench/references/checklist-engine.md`. durable-root resolution: `scripts/agent_work_root.py`.

## Pre-empted Steps
Context and plan pre-empted: design confirmed through a full explorer pass; the two-option comparison is settled (option 1). Your understand step is the gate code + the #129–#131 closeout artifacts + this order.

## Data Locations
- Confirmed spec: `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`
- #129–#131 arc artifacts (fixture source hunt): `C:/Programs/constellation-skills/.agent-work/` (archives + `LAUNCH_ORDER-issue-129-continuation.md` at repo root) and the merged PR history of that arc.

## Budget
- **Model tier (required):** opus (gate logic with an invariant to preserve; human-capped at opus or lower).
- **Compute/time, session-window:** target ≤ 60 min.

## Stop Conditions
Stop and return when: the change demands a new verb/schema, the fence with #140 cannot be honored, budget crossed, or context missing — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict + evidence to `C:/Programs/constellation-skills/.agent-work/epic-138/verdicts/commander-143.md`: PR URL, test results (exit codes) incl. the three acceptance-criteria unit tests + unfenced regression, fixture provenance, isolation-check output, shared-file fence note, triage candidates, workflow feedback. Deliver artifacts **before** going idle.
