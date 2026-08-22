<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-011 status=active -->

# episode: 20260820-deficiency-cleanup-011

## Mechanical
- run: 20260820-deficiency-cleanup
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/20260820-deficiency-cleanup/ADMIRAL_LOG.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-011.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Have an independent reviewer verify the follow-up commits on the A+B branch.

### assertion:20260820-deficiency-cleanup-011.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The reviewer runs its checks and returns a verdict.

### assertion:20260820-deficiency-cleanup-011.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It backgrounded its full-suite run, then ended its turn waiting for a Monitor completion notification that does not route back to a subagent. The lane stalled holding an unfinished verdict after 35 tool calls of completed review work.

### assertion:20260820-deficiency-cleanup-011.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: From outside, an agent waiting on a notification it cannot receive is indistinguishable from an agent thinking. It was caught only because the Admiral was watching that lane, which does not scale.

### assertion:20260820-deficiency-cleanup-011.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The lane was resumed with an instruction to run the suite in the foreground with an explicit long timeout and block on it directly, and to report a blocker rather than wait on one. It then completed, including a mutation test proving the regression under review would fail if enforcement moved into argparse.

## Diagnosis (optional)

### assertion:20260820-deficiency-cleanup-011.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The Stop hook's guidance covers the reverse case, that an agent must not end its turn waiting on a foreign gate, but nothing tells a crew not to wait on its own backgrounded command.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
