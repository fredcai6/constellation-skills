---
name: constellation-reviewer
description: Independently verify a bounded change. Use when a handoff provides a diff, evidence, and review criteria.
---

# Constellation Reviewer

Verify one bounded change independently.

Start from the given criteria in `templates/REVIEW_SURVEY.template.json` and append checks the context warrants (one per inherited rule). Drive it as a `survey` through the engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): visit every check, record pass or fail with a finding, then consolidate to a verdict.

The verdict is APPROVE or BLOCK with findings; an open fail cannot consolidate to APPROVE. Keep blockers separate from observations. Flag out-of-scope finds as triage candidates.

Report a proof-of-life as soon as you start and report each check as you record it. Return the verdict in `REVIEW_RESULT`.

Templates: `templates/REVIEW_SURVEY.template.json`, `templates/REVIEW_RESULT.template.md`. Reference: workbench `references/checklist-engine.md`.
