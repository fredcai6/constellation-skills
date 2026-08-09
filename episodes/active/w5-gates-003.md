<!-- episode-state: schema=1 id=w5-gates-003 status=active -->

# episode: w5-gates-003

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: archive
- context-manifest-ref: .agent-work/w5-gates/context/g4-review.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/spine.json

## Agent-supplied

### assertion:w5-gates-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close the run's own archive gate after fixing the archive-reachability defect.

### assertion:w5-gates-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The spine driving this run would carry the repair the run itself produced.

### assertion:w5-gates-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It does not. This spine was instantiated before g3 landed, so its archive.c2b still holds the pre-fix text with an unsubstituted <branch> placeholder. The engine runs check text through sh -c, where an unquoted < is input redirection: sh tries to open a file named 'branch', exits 1, and gh is never invoked. Always red, in every state of the world.

### assertion:w5-gates-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The final gate of the wave that fixed this defect is blocked BY that defect. Resolved by an Admiral waiver after the substance was real -- branch pushed, PR 516 open -- rather than by improvising.

### assertion:w5-gates-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Waive on named Admiral authority with the command text and measured exit code recorded verbatim, and state plainly that the check did not pass. Never hand-substitute the branch name to make it green.

## Diagnosis (optional)

### assertion:w5-gates-003.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A running spine is a snapshot taken at instantiation, so a fix to the template cannot reach instances already in flight.

### assertion:w5-gates-003.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: No remedy proposed -- retrofitting live instances may be worse than the problem. Recorded as an observation, not a rule.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
