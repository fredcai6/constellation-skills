<!-- episode-state: schema=1 id=episode-guard-at-write-001 status=active -->

# episode: episode-guard-at-write-001

## Mechanical
- run: episode-guard-at-write
- project: constellation-skills
- role: commander
- spine-step: execute-g1-implement
- context-manifest-ref: ctx-egaw-g1@2c46cab8
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 0
- artifact-ref: scripts/apply_episode_delta.py
- artifact-ref: scripts/install_constellation.py
- artifact-ref: tests/test_episode_observation_guard_at_write.py

## Agent-supplied

### assertion:episode-guard-at-write-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Validate an instruction-shaped episode statement at write time, using the read-time guard's own triggers_for, so a lane's write could no longer pass and later red the closeout suite.

### assertion:episode-guard-at-write-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A create or restate-assertion op carrying an instruction-shaped statement was rejected by apply_episode_delta.py before anything was written, and a well-formed statement still wrote.

### assertion:episode-guard-at-write-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The guard fired correctly in both the create and restate-assertion paths once scoped to the real store; an unconditional first version broke 46 tests outside this lane's ownership, because tests/test_episode_observations.py and tests/test_episode_store.py write instruction-shaped statements through this same writer to test the read-time guard and the writer's own mechanics.

### assertion:episode-guard-at-write-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One additional design pass followed the first, unconditional implementation, after the full-suite run surfaced the fixture-building conflict.

### assertion:episode-guard-at-write-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The guard was scoped to the real store's own identity rather than to every store root, so a test fixture writing an instruction-shaped statement through this same writer into a throwaway root was unaffected.

## Diagnosis (optional)

### assertion:episode-guard-at-write-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: An unconditional write-time guard collides with test fixtures that must construct instruction-shaped records through the real writer to test something else.

### assertion:episode-guard-at-write-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: A future write-time guard should be scoped to the store's own identity before it is generalized to every root it might be pointed at.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
