<!-- episode-state: schema=1 id=epic-418-followon-014 status=active -->

# episode: epic-418-followon-014

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-014.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run every spine in this corpus against the engine, each declaring its own config_ref.

### assertion:epic-418-followon-014.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A spine naming docs/agents/engine-config.json would be driven under the configuration that file specifies.

### assertion:epic-418-followon-014.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The file does not exist. Every spine in the corpus names it, and the engine has been running on defaults throughout, with no refusal and no warning. A dispatched Commander found it while reading its own spine at the understand gate.

### assertion:epic-418-followon-014.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Unknown: no run in this epic can say whether it would have behaved differently under the named configuration, because the configuration has never existed to compare against.

### assertion:epic-418-followon-014.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: A missing config_ref was handled as a refusal rather than a silent default. This matched the known adjacent defect where a non-JSON config_ref crashes the engine outright: the same field was unchecked in both directions.
- history: restated — Restated as an observation. The original was written in the imperative and read as a rule for a future agent to follow; an episode records what happened, and a rule belongs in docs/agents/*. Caught by scripts/verify_episode_observations.py at the epic's closeout. — original statement was: Treat a missing config_ref as a refusal rather than a silent default, matching the known adjacent defect where a non-JSON config_ref crashes the engine outright -- the same field is unchecked in both directions.

## Diagnosis (optional)

### assertion:epic-418-followon-014.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A reference that silently falls back to a default cannot distinguish 'configured this way' from 'never configured', and every spine in the corpus inherited the reference by template copy.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
