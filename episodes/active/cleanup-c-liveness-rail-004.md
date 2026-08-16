<!-- episode-state: schema=1 id=cleanup-c-liveness-rail-004 status=active -->

# episode: cleanup-c-liveness-rail-004

## Mechanical
- run: cleanup-c-liveness-rail
- project: constellation-skills
- role: commander
- spine-step: g1-implement
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement-handoff.md
- artifact-ref: .agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement-result.md

## Agent-supplied

### assertion:cleanup-c-liveness-rail-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: The g1-implement handoff specified entry_liveness's exact signature literally, including 'alive=process_alive' as a default parameter value, to remove ambiguity about how the three-bucket rule should be wired.

### assertion:cleanup-c-liveness-rail-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The literal signature text in the handoff was directly implementable as written.

### assertion:cleanup-c-liveness-rail-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The implementer found that 'alive=process_alive' as a literal default value is invalid at the position the handoff specified: default parameter values bind at def-time, and process_alive is defined roughly 600 lines later in the same module, so that exact text would raise NameError at import. The implementer verified this with a minimal repro before treating it as a real constraint, then substituted a None-sentinel resolved inside the function body (the same pattern the handoff's own 'now=None' already used), preserving identical externally observable default behavior.

### assertion:cleanup-c-liveness-rail-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: No rework or stop condition resulted -- the implementer correctly classified this as a Python-semantics fix, not a re-derivation of the three-bucket rule, the 8h window, or the fail-toward-active mapping, and proceeded without pausing for clarification.

### assertion:cleanup-c-liveness-rail-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Implementer substituted a None-sentinel pattern already modeled elsewhere in the same handoff (the now=None convention), rather than treating the literal-but-invalid text as a stop condition.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
