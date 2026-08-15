<!-- episode-state: schema=1 id=tc1-worktree-identity-003 status=active -->

# episode: tc1-worktree-identity-003

## Mechanical
- run: tc1-worktree-identity
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: tc1-worktree-identity-plan@453f8492
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/tc1-worktree-identity/execute.json

## Agent-supplied

### assertion:tc1-worktree-identity-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run a cold plan critic (a subagent with no authoring context, given only the ruling and the draft execute.json/MISSION_FRAME.md) before freezing the gate plan, per the design-it-twice/critical-spec-review standard.

### assertion:tc1-worktree-identity-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Given the ruling specifies the implementation in unusual detail (exact comparison operator, exact call-site line, an explicitly authorized test migration), the draft plan's constraints already looked complete, so the critic pass was expected to mostly confirm rather than surface new gaps.

### assertion:tc1-worktree-identity-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The critic found a genuine, load-bearing contradiction the draft plan had missed: the existing test fixtures in _SpineOnDisk (used by RefusesAGuardedVerbFromAForeignTree and TheInProcessMcpDoorShape) build plain non-git tempdirs, and the draft plan's constraint list would have left them ungitted while also requiring their same-worktree pass-path assertions to keep passing under the new fail-closed rule -- a contradiction that would have surfaced only as implementer confusion or a broken test, not as a plan defect visible on read. The critic also flagged that leaving `self.foreign` non-git would silently narrow coverage to the fail-closed path only, masking the equality-mismatch path the ruling actually cares about.

### assertion:tc1-worktree-identity-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Roughly 3 minutes of critic-agent time before any implementer dispatch, versus what would likely have been a rework round-trip (implementer hits the contradiction mid-task, returns confused or under-scoped, Commander re-plans) had the plan gone out as originally drafted.

### assertion:tc1-worktree-identity-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Folded both findings directly into execute.json's g1-implement constraints before dispatch: required _SpineOnDisk to git-init BOTH self.worktree and self.foreign as distinct real repos, and required a direct predicate-level cwd=None test alongside the main()-level one.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
