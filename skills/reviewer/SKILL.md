---
name: constellation-reviewer
description: Independently verify a bounded change. Use when a handoff provides a diff, evidence, and review criteria.
---

# Constellation Reviewer

Verify one bounded change independently.

## Start here — drive the engine before you touch the diff

You were handed a bounded verification task, not a licence to skim it. The moment this skill loads — before you read the diff closely and before you record a single check — do this, in order:

1. **Build the survey and CLAIM the engine lease.** Instantiate your `survey` from `templates/REVIEW_SURVEY.template.json`, then `claim` the checklist lease with the engine. This is your **first command**, ahead of any verification.
2. **Ask the engine what to do next, at every check.** Run the engine's `current` verb, do exactly what the active check's imperative says, and `advance`/`record` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit the survey file — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the review was really driven.
3. **One finding is the MIDDLE of the review, not the end.** Recording a single check's pass/fail is not done — integrate it, `advance` that check, then drive every remaining check through the engine to a consolidated verdict. **Do not end your turn while any check is still `pending` or `in-progress`:** run the engine's `current` verb and keep going until it reports the survey is done. The single most common failure at this tier is stopping the moment one finding lands — resist it. Run the engine's final `advance`/`consolidate` first, and **only then** `release` the engine session lease as your very last action. Releasing before that closing advance fails the terminal provenance check — the lease must cover every journaled action.
4. **Reproducing a claimed side-effect is never a reason to end your turn.** If you must wait on a command you are re-running to verify a claim, wait **actively, inside your turn**: poll for its output in a loop until it lands, then integrate it and drive on. Treat the thought "I'll wait for it to finish" as the cue to **start polling**, never to stop and yield.

**Work the engine never saw did not happen.** A survey that records a verdict directly, or copies the survey template and never advances it, or hand-writes a survey that merely *looks* complete, or **drives the engine only as far as one finding and then stops**, has **failed this dispatch** no matter how correct the answer — the deliverable of a Reviewer run is a survey driven all the way to a consolidated verdict. Report a proof-of-life as soon as you start.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md` (report misfits in your workflow feedback).

Start from the given criteria in `templates/REVIEW_SURVEY.template.json` and append checks the context warrants (one per inherited rule). Drive it as a `survey` through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, and the constellation-workbench skill's bundled `references/checklist-engine.md` under the installed workbench skill directory): visit every check, record pass or fail with a finding, then consolidate to a verdict. Create the survey checklist at the path the handoff gives ("Survey State Location": `.agent-work/<work-id>/<gate>-review/review.json`) — under the issue workbench, never at the worktree root, so closeout finds no orphan untracked scratch.

The verdict is APPROVE or BLOCK with findings; an open fail cannot consolidate to APPROVE. Keep blockers separate from observations. Flag out-of-scope finds as triage candidates.

Verify the implementer's `Map Impact` notes against the diff and evidence: evidence backs the claimed behavior/capability change, constraints were not violated, the notes match the diff, decision candidates are surfaced when authority is required, and durable context routes to Cartographer or Triage. BLOCK when graph-impact claims are materially wrong or missing for architecture-significant work; do not block trivial local edits for absent notes.

Verify claimed side-effects against the world, not against the report, per inherited doctrine (`references/global-everyone.md` §"Verify claimed side-effects against the world"): confirm each claim at its source and independently reproduce it. Reviewer-specific: a claim you cannot reproduce is a **BLOCK finding**, not an accepted fact — the verdict cannot rest on an unreproduced assertion.

Report a proof-of-life as soon as you start and report each check as you record it. Return the verdict in `REVIEW_RESULT`.

Fill the result's `Workflow Feedback` section honestly: name the handoff field, evidence gap, or instruction that was ambiguous, missing, or improvised around. You are the only one who saw that friction — Commander harvests it so future handoffs improve.

Templates: `templates/REVIEW_SURVEY.template.json`, `templates/REVIEW_RESULT.template.md`. Reference: the constellation-workbench skill's bundled `references/checklist-engine.md` (under the installed workbench skill directory).
