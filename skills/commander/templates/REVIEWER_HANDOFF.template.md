# Reviewer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Concise fragments. Omit filler.

> **Targeted authoring:** distill. This handoff is the complete packet: carry the operative scope, constraints and authority the reviewer must check against. Name the selected source evidence under Required Inputs so the reviewer can check scope, sufficiency and relevant omissions against it, not only against this handoff's own summary. Equivalent concise formulations are sufficient when they unambiguously preserve meaning; verbatim repetition is not required. Authoring approval does not authorize implementation; carry unapproved requests as unresolved authority.

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

For a **doc-diet or register-rewrite** gate, a structural/JSON test suite does NOT guard prose invariants (pointer-name presence, forbidden-signature absence, meaning preservation). Carry the operative invariants and selected source evidence; the Reviewer independently chooses and runs the checks, including required signature checks. Never read suite-green as assurance for meaning preservation.

When the gate carries an expected transient failure set, scope it **by root cause** (the failing mechanism, wherever it surfaces — e.g. "the installer's discovery refusal, in any test whose setUp runs the installer"), never by file name alone, and reproduce the distribution yourself: a failure matching the named root cause outside the listed file is the waiver working, not a blocker; a failure outside the root-cause class is a BLOCK.

## Allowed Scope
`<what the implementation was permitted to touch>`

## Specific Exclusions
`<anything that was off-limits; flag if touched>`
For an exclusion outside the Reviewer's accessible worktree, supply evidence from an authorized role that can inspect it. The Reviewer records that evidence's provenance and limits; it does not claim direct verification it could not perform. If the exclusion is required and adequate evidence is unavailable, return the gap for routing rather than silently accepting it. The Commander obtains access or dispatches the responsible role; it does not become the technical verifier.

## Constraints the Implementation Must Respect
`<rules inherited from the gate plan; each becomes a review check>`
- `<rule>`

## Map Anchors (inbound)
Map context this gate inherits from the mission frame; review the change against these so it lands on the right structure and honors recorded rules. Omit a line when the gate carries nothing for it.
Carry each decision anchor's `@grade` tag across from the mission frame on its own child line — the tier is what tells you whether a contradiction you find is the implementer's to have revised in place or a decision candidate to float back (see `references/global-everyone.md`, "Decision fixedness").
- **Structural:** `<struct:id — path/symbol, level — where the work lands or depends>`
- **Capability:** `<capability:id — behavior this gate changes or relies on>`
- **Constraints/assumptions:** `<constraint:id | assumption:id — verify it was not silently violated>`
- **Decision anchors:** `<decision:id — governs this structure; flag any contradiction as a decision candidate>`
  `@grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]`
- **Evidence expectations:** `<claim:id or check this gate must re-confirm>`
- **Map confidence flags:** `<node id — low-confidence/stale/disputed area; confirm rather than trust; omit if none>`

## Evidence Produced
`<test output, command results, artifacts from IMPLEMENTER_RESULT — include pass/fail>`
When a gate requires evidence attached to or referenced by a specific engine postcondition, name the **exact target postcondition id** (e.g. `g2-integrate.c1`) so the reviewer checks the right slot.

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Stop Conditions
Record failed criteria and absent/unverifiable evidence as findings; finish the remaining independent, permitted checks and consolidate BLOCK. Halt and report unfinished coverage when inaccessible context, the engine state or a required policy/authority decision prevents continued review. Never take an excluded action or waive a required check to continue. A finished BLOCK returns status `complete`; use `blocked` when the review itself could not be finished.

## Required Inputs
For re-review, include the latest review result (the current finding index), implementation repair responses and the changed revision/diff. The Reviewer owns the full assessment and disposition; Commander leads do not limit the review.

`<optional — selected source evidence paths the reviewer should read to check scope, sufficiency and omissions; omit if none>`

## Provenance
`<optional — source artifacts for audit or conflict resolution. Not required reading and not authority; open only for ambiguity, conflict or missing evidence. Omit if none>`

## Result Artifact
`<exact project-relative or absolute output path; normally .agent-work/<work-id>/crew-handoffs/<gate>-reviewer-result.md; use a fresh round path for re-review>`

This file is the delivery. Put all task-specific instructions in this handoff or its referenced artifacts; the invocation only names this handoff. Do not send a second prose explanation of the assignment.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the review harder than it needed to be). The returned `REVIEW_RESULT` is recorded as the engine `review-result` evidence artifact (the `evidence_type` the integrate gate matches on) — the human-facing document name and the engine artifact type refer to the same object.

**Delivery.** Write the full `REVIEW_RESULT` to the Result Artifact path above before ending your turn — that write is the delivery, and it is what a resumed or relaunched Commander finds regardless of which instance dispatched you. `SendMessage` an announcement to the dispatching Commander too, but treat it as a best-effort courtesy ping, not the delivery itself: the instance you address may have relaunched or handed off in the meantime and no longer resolve, or (dispatched as a subagent) may not be addressable from your thread at all — a missing ping is not a missing result.
