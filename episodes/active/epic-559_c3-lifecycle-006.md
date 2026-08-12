<!-- episode-state: schema=1 id=epic-559_c3-lifecycle-006 status=active -->

# episode: epic-559_c3-lifecycle-006

## Mechanical
- run: epic-559/c3-lifecycle
- project: constellation-skills
- role: commander
- spine-step: g4-review
- context-manifest-ref: LAUNCH_ORDER-C3@293b7721
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/epic-559/c3-lifecycle/crew-runs.json

## Agent-supplied

### assertion:epic-559_c3-lifecycle-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch the g4 reviewer through run_crew.py and wait for its result artifact, polling the durable registry rather than ending the turn.

### assertion:epic-559_c3-lifecycle-006.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Expected run_crew.py to register a crew entry and spawn the reviewer, as it had for the eleven prior dispatches in this run.

### assertion:epic-559_c3-lifecycle-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The command produced no registry entry, no result artifact and no visible error; recover_crews.py reported no crew for that work-id/gate/role/worktree at all. The dispatch simply did not happen, silently.

### assertion:epic-559_c3-lifecycle-006.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Roughly ten minutes of waiting on a crew that was never launched. A dispatcher polling a clock, or trusting that it had run the command, would have waited indefinitely.

### assertion:epic-559_c3-lifecycle-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Noticed it because the wait loop polls the registry for a RUNNING entry rather than only the result path, so the absence surfaced as 'crew no longer running' with no artifact. Re-ran recover_crews.py to confirm no conflict, re-dispatched as a fresh attempt, and confirmed the new entry and its pid before waiting again.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
