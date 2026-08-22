<!-- episode-state: schema=1 id=w2-basis-001 status=active -->

# episode: w2-basis-001

## Mechanical
- run: w2-basis
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: none -- no context-manifest artifact produced this run
- refusals: 10
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w2-basis/spine.json

## Agent-supplied

### assertion:w2-basis-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: This run's spine tripped the engine's HARD context-gauge band four separate times (at plan, execute, reconcile, review), each time refusing the guarded `start` verb with 'context at N% is at/over the hard limit'.

### assertion:w2-basis-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The launch order's own Stop Conditions section pre-authorized exactly this scenario in writing: 'attach the refresh-request against the current why-record, THEN start, THEN do the work... Do not read a HARD advisory as licence to advance and hand off on turn one -- that produces an infinite handoff chain.'

### assertion:w2-basis-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Every one of the four trips resolved cleanly with the exact same three-call sequence (attach refresh-request -> start -> continue working in the same turn), with no idle hand-off and no relaunch. The engine's own rail text at each trip also confirmed this was the sanctioned path ('the refresh for <gate> is already requested... close THIS gate carrying your handoff' only applies to a genuine mid-gate exhaustion, not this pattern of a fresh gate refusing `start` at turn one).

### assertion:w2-basis-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Zero -- each trip cost exactly one extra pair of tool calls (attach + retry start) with no lost work. Without the launch order's explicit pre-authorization of this exact sequence, a Commander following the generic HARD-band rail text literally ('close THIS gate... a fresh agent picks up from your DIGEST') at turn one of a fresh gate would have gone idle four separate times across one run, each requiring an external relaunch that may not have been forthcoming.

### assertion:w2-basis-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Followed the launch order's explicit override verbatim at each trip: attach the refresh-request citing the current why-record id, retry `start` (which then succeeds because a keyed request is pending), and continue the gate's real work in the same turn rather than advancing-and-idling.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
