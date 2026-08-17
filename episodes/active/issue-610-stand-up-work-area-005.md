<!-- episode-state: schema=1 id=issue-610-stand-up-work-area-005 status=active -->

# episode: issue-610-stand-up-work-area-005

## Mechanical
- run: issue-610-stand-up-work-area
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: n/a -- no context-manifest artifact produced this run
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/commander/
- artifact-ref: skills/admiral/
- artifact-ref: skills/commander-delegated/

## Agent-supplied

### assertion:issue-610-stand-up-work-area-005.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Note that this run's shipped skill-source edits do not automatically reach the INSTALLED skill copy at ~/.claude/skills that actually drives agents dispatched in this repo.

### assertion:issue-610-stand-up-work-area-005.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: Merging the PR would be sufficient for the fix to take effect for future agents in this repo.

### assertion:issue-610-stand-up-work-area-005.a3
- kind: observed-behavior
- strength: medium
- lifecycle-standing: active
- statement: docs/agents/ORCHESTRATOR_CONTEXT.md's own 'dogfooding' section documents this gap: the installed copy is a snapshot taken at install time, and this repo dogfoods itself via .agent-work/ regardless of which worktree an agent stands in (CLAUDE_PROJECT_DIR resolves once at session launch).

### assertion:issue-610-stand-up-work-area-005.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: None to this run -- purely a follow-on reminder.

### assertion:issue-610-stand-up-work-area-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none -- a reinstall (install_constellation.py) after merge is the known remedy, just easy to forget.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
