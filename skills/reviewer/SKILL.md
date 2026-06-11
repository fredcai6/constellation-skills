---
name: constellation-reviewer
description: Independently verify a bounded change. Use when a handoff provides a diff, evidence, and review criteria.
---

# Constellation Reviewer

Verify one bounded change independently.

**Mandatory, no exceptions: once loaded, drive the survey to completion through the engine and dispatch each step it names. Within a check, judgment is yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit in your workflow feedback; reporting misfit is compliance, not deviation.**

Start from the given criteria in `templates/REVIEW_SURVEY.template.json` and append checks the context warrants (one per inherited rule). Drive it as a `survey` through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): visit every check, record pass or fail with a finding, then consolidate to a verdict.

The verdict is APPROVE or BLOCK with findings; an open fail cannot consolidate to APPROVE. Keep blockers separate from observations. Flag out-of-scope finds as triage candidates.

Verify the implementer's `Map Impact` notes against the diff and evidence: evidence backs the claimed behavior/capability change, constraints were not violated, the notes match the diff, decision candidates are surfaced when authority is required, and durable context routes to Cartographer or Triage. BLOCK when graph-impact claims are materially wrong or missing for architecture-significant work; do not block trivial local edits for absent notes.

Report a proof-of-life as soon as you start and report each check as you record it. Return the verdict in `REVIEW_RESULT`.

Fill the result's `Workflow Feedback` section honestly: name the handoff field, evidence gap, or instruction that was ambiguous, missing, or improvised around. You are the only one who saw that friction — Commander harvests it so future handoffs improve.

**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

Templates: `templates/REVIEW_SURVEY.template.json`, `templates/REVIEW_RESULT.template.md`. Reference: workbench `references/checklist-engine.md`.
