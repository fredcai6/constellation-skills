<!-- episode-state: schema=1 id=crew-verdict-and-door-001 status=active -->

# episode: crew-verdict-and-door-001

## Mechanical
- run: crew-verdict-and-door
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/crew-verdict-and-door/MISSION_FRAME.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/crew-verdict-and-door/execute.json

## Agent-supplied

### assertion:crew-verdict-and-door-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a gate plan for Task 2 (external-backend door hardening) whose imperative said to state the hazard 'in the external-backend crew prompt AND its run_crew.py registry entry.'

### assertion:crew-verdict-and-door-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The gate plan's own anchors and imperative would name real, editable code inside the file-ownership fence (scripts/run_crew.py) for both halves of the ask.

### assertion:crew-verdict-and-door-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A cold plan critic (a fresh subagent given only the mission frame and execute.json, no authoring context) read ExternalBackend.dispatch directly and reported that it builds no prompt at all -- its own docstring says the out-of-band caller does that, outside scripts/run_crew.py. Half the g2 deliverable as originally planned targeted a file the plan itself fenced off from the implementer.

### assertion:crew-verdict-and-door-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Caught before any implementer dispatch: the plan's g2 anchors, imperative, and postconditions were corrected (to the registry-entry field plus ExternalBackend.dispatch's own stderr banner, both genuinely inside the fence) in a few minutes of editing, versus what would otherwise have been an implementer either violating scope to edit an out-of-fence file, silently dropping half the ask, or returning blocked on a real-looking but wrong contradiction.

### assertion:crew-verdict-and-door-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Re-read the flagged function directly before editing the plan, confirmed the critic's claim against the actual source rather than trusting it on report alone, then rewrote the affected gate's anchors/imperative/postconditions in execute.json before any crew was dispatched.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
