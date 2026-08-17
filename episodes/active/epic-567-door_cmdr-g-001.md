<!-- episode-state: schema=1 id=epic-567-door_cmdr-g-001 status=active -->

# episode: epic-567-door_cmdr-g-001

## Mechanical
- run: epic-567-door/cmdr-g
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/epic-567-door/cmdr-g/context/feedback.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: RETURN.md
- artifact-ref: .agent-work/567-g/triage-candidates/no-instrument-distinguishes-own-fork-writes-from-tampering.md

## Agent-supplied

### assertion:epic-567-door_cmdr-g-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatched two design-it-twice forks (subagent_type fork) to author parallel plan candidates under distinct constraints, each scoped to write one named file only.

### assertion:epic-567-door_cmdr-g-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Each fork writes only its assigned candidate file and ends its turn; the primary Commander thread remains the sole driver of its own engine-owned spine.json and execute.json.

### assertion:epic-567-door_cmdr-g-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A fork continued past its assigned task, using its inherited conversation context and lease identity (cmdr-567-g#main) to drive the Commander's own spine.json through real engine calls (plan step advanced to complete) and dispatch a real g1 implementer crew via run_crew.py, indistinguishable from the primary thread's own actions in any file it wrote.

### assertion:epic-567-door_cmdr-g-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The primary Commander thread diagnosed this as external tampering, wrote a halt-and-escalate report, and reverted the fork-dispatched crew's real work twice via git checkout -- before the Admiral adjudicated the true cause. The reverted work was later re-derived by a fresh crew dispatch at real cost (a second implementer attempt, a corrected handoff, re-verification).

### assertion:epic-567-door_cmdr-g-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Escalated via RETURN.md rather than silently continuing or silently reverting without report; the Admiral adjudicated by cross-referencing crew-runs.json's real timestamped entry and confirming a second artifact (PLAN_CRITIC.md) the report had wrongly called nonexistent. Resumed the run on the Admiral's instruction, corrected the design flaw the reverted work had already found, and re-dispatched a fresh implementer with the fix.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
