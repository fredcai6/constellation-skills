<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-001 status=active -->

# episode: epic-567-door_cmdr-a-001

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: init
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 2
- artifact-ref: .agent-work/epic-567-door/cmdr-a/PROBLEM_STATEMENT.md

## Agent-supplied

### assertion:epic-567-door_cmdr-a-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Claim the engine lease as the first command, using the engine path the launch order named.

### assertion:epic-567-door_cmdr-a-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The path in the order would resolve to a runnable engine.

### assertion:epic-567-door_cmdr-a-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The path did not exist: the installed constellation-commander-delegated skill ships only SKILL.md, interpreter.json and references/ -- no scripts/ and no templates/. Its own SKILL.md says it depends on the constellation-commander skill for both.

### assertion:epic-567-door_cmdr-a-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Two failed commands and a detour at the step the order calls the first command, before any mission work.

### assertion:epic-567-door_cmdr-a-001.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Used /home/tommy/.claude/skills/constellation-commander/scripts/checklist_engine.py instead and recorded the substitution.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The order template names a path by the skill the commander loads rather than by the skill that ships the engine.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
