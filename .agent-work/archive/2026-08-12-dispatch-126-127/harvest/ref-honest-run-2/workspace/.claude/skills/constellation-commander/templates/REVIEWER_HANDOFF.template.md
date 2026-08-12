# Reviewer Handoff

Concise fragments. Omit filler.

Backtick `<...>` placeholder strings in this handoff are **illustrative**; the **contractual** criteria a verdict rests on are the Close Criteria and the Constraints sections.

## Gate
`<gate id from execute.json, e.g. g1>`

## Survey State Location
Create your review survey checklist at `.agent-work/<work-id>/<gate>-review/review.json` — under the issue workbench, **never at the worktree root** (illustrative: for gate `g1` of `issue-73` that resolves to `.agent-work/issue-73/g1-review/review.json`). This keeps the survey state with the run's artifacts so closeout leaves no orphan untracked scratch.

## What Was Implemented
`<brief description of the change>`

## How to Inspect the Diff
`<exact diff command, commit range, or branch — how to see what changed>`
For a change in a linked worktree, name the review target as the **UNCOMMITTED working tree**, NOT `git diff main...HEAD` (which shows unrelated merged-PR divergence, not this gate's change). Inspect with untracked-safe commands — `git status --porcelain` then `git diff` (not `git diff --name-only`, which hides untracked additions).
Check the handoff's Deliverable Path Check note before flagging an expected artifact as missing — a path marked Local-only is intentionally absent from this diff, not a defect.

## Task Statement
`<the original task the implementer was given — what it was supposed to build>`

## Close Criteria
`<conditions required for APPROVE; each becomes a review check>`
- `<criterion>`

For a **doc-diet or register-rewrite** gate, a structural/JSON test suite does NOT guard prose invariants (pointer-name presence, forbidden-signature absence, meaning preservation). Make each of those an explicit per-gate grep the reviewer runs and the Commander re-runs; never read suite-green as assurance for them.

When the gate carries an expected transient failure set, scope it **by root cause** (the failing mechanism, wherever it surfaces — e.g. "the installer's discovery refusal, in any test whose setUp runs the installer"), never by file name alone, and reproduce the distribution yourself: a failure matching the named root cause outside the listed file is the waiver working, not a blocker; a failure outside the root-cause class is a BLOCK.

## Allowed Scope
`<what the implementation was permitted to touch>`

## Specific Exclusions
`<anything that was off-limits; flag if touched>`
An exclusion that references a path **outside the reviewer's own worktree** is **Commander-verified, not reviewer-verified** — the reviewer cannot inspect it, so it must NOT be a BLOCK finding on grounds of un-inspectability; note it and move on.

## Constraints the Implementation Must Respect
`<rules inherited from the gate plan; each becomes a review check>`
- `<rule>`

## Map Anchors (inbound)
Map context this gate inherits from the mission frame; review the change against these so it lands on the right structure and honors recorded rules. Omit a line when the gate carries nothing for it.
- **Structural:** `<struct:id — path/symbol, level — where the work lands or depends>`
- **Capability:** `<capability:id — behavior this gate changes or relies on>`
- **Constraints/assumptions:** `<constraint:id | assumption:id — verify it was not silently violated>`
- **Decision anchors:** `<decision:id — governs this structure; flag any contradiction as a decision candidate>`
- **Evidence expectations:** `<claim:id or check this gate must re-confirm>`
- **Map confidence flags:** `<node id — low-confidence/stale/disputed area; confirm rather than trust; omit if none>`

## Evidence Produced
`<test output, command results, artifacts from IMPLEMENTER_RESULT — include pass/fail>`
When a gate requires evidence attached to or referenced by a specific engine postcondition, name the **exact target postcondition id** (e.g. `g2-integrate.c1`) so the reviewer checks the right slot.

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the review harder than it needed to be). The returned `REVIEW_RESULT` is recorded as the engine `review-result` evidence artifact (the `evidence_type` the integrate gate matches on) — the human-facing document name and the engine artifact type refer to the same object.
