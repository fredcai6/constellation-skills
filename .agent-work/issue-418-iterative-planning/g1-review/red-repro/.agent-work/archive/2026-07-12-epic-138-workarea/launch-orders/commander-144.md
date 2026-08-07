# Launch Order: `commander-144 — issue #144 (warm-register pass, exploration prose)`

Right-sized dispatch: this is a bounded implementer-with-plan mission, not a full Commander spine — the plan is below; execute it directly.

## Mission
Implement https://github.com/fredcai6/constellation-skills/issues/144 — a deliberate warm, joyful-optimistic register for exploration-facing doctrine prose in `skills/explorer/SKILL.md` and `skills/prototyper/SKILL.md` (in-repo paths may differ slightly — locate the explorer and prototyper skills in `skills/`). Deliverable: a green, reviewed PR on branch `issue-144`.

## Prior-Wave Verdicts (pasted)
From the CONFIRMED #138 spec (§D4 disposition half): exploration-facing doctrine gets a warm register — shotgun framing, excursion framing, scoped-nulls-as-invitation ("the default next move after a null is another variant" should feel like an invitation, not a citation). Honestly weakly evidenced (recorded as accepted-untested in the spec; EmotionPrompt-class gains are largest on generative tasks and fragile) and equally justified by maintainability: doctrine that is pleasant to inhabit gets maintained. HARD BOUNDARY (spec + critic-review settled): the warm register never enters rails, gates, engine strings, eval-adjacent text, templates' contractual language, or `_shared/` enforcement doctrine. Flat register stays flat everywhere enforcement lives.

## Plan (execute directly)
1. Read the explorer and prototyper SKILL.md files; identify exploration-stance prose (the *why* and *spirit* passages) vs procedural/contract text (steps, gates, templates, marker rules).
2. Rewrite only the stance prose warm — same facts, same procedure, same headings, zero contract changes. Joy about exploring, optimism about nulls ("a cull can come back"), zero exclamation-mark inflation, zero all-caps.
3. Diff-check: no template file, no `_shared/` file, no engine string, no gate/precondition text, no headline-doctrine rule altered in meaning.
4. PR with the register boundary stated in the body for reviewer verification (human-reviewed by design; no machine check).

## Pre-Rulings
- Procedural content is untouchable: every gate, marker rule (e.g. the standalone `UNCONFIRMED — DO NOT CUT` mechanics), template contract, and script invocation stays byte-identical in meaning.
- Warmth is tone, not volume: no exclamatory/all-caps styling (x3 research-settled).
- If warm and flat collide in one passage (e.g. scoped-nulls doctrine that is both stance and enforcement), flat wins and you note the collision in the PR.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

## Inherited Latitude
You may: word-level choices inside the boundary. You must float: any procedural-meaning change, any file outside the two skills, anything eval-adjacent. Merges are the human's — open the PR, never merge.

## File Ownership
Sole writer of: the explorer + prototyper SKILL.md prose and `.agent-work/epic-138/verdicts/commander-144.md` (MAIN checkout, absolute path below). Note: commander-142 also edits skill files this wave but ONLY enforcement clamp text — if your two skills receive a clamp/pointer from #142, do not touch those sentences at all (they are spec-frozen flat); mention the adjacency in your PR body.

## Workspace
`C:/Programs/constellation-wt-144` — branch `issue-144`, base commit 93f38505 (main), created via `git worktree add ../constellation-wt-144 -b issue-144 main`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-144` — must exit 0; paste output into your report.
NOTE: PR integration defaults to **server-side merge**.

## Inherited Context
- Windows/py launcher conventions; UTF-8 writes; `gh pr create -F <tempfile>` for PR bodies.
- Superpowers is a competitor — never cite or import its doctrine.
- Source repo is authority: edit `skills/` in-repo; NEVER touch installed copies at `~/.claude/skills`.

## Pre-empted Steps
All design pre-empted; this order carries the full plan.

## Data Locations
- Confirmed spec: `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`

## Budget
- **Model tier (required):** sonnet (bounded prose work; least-powerful that works).
- **Compute/time, session-window:** target ≤ 30 min.

## Stop Conditions
Stop and return when: the boundary between stance and enforcement is genuinely ambiguous in a passage, budget crossed, or context missing — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict + evidence to `C:/Programs/constellation-skills/.agent-work/epic-138/verdicts/commander-144.md`: PR URL, the boundary statement, isolation-check output, any flat-wins collisions noted, workflow feedback. Deliver artifacts **before** going idle.
