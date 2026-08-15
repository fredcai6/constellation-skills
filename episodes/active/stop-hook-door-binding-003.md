<!-- episode-state: schema=1 id=stop-hook-door-binding-003 status=active -->

# episode: stop-hook-door-binding-003

## Mechanical
- run: stop-hook-door-binding
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/stop-hook-door-binding/crew-handoffs/g1-review-reviewer-result.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 2
- artifact-ref: scripts/install_constellation.py
- artifact-ref: tests/test_install_constellation.py

## Agent-supplied

### assertion:stop-hook-door-binding-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Ran the full clean-env suite after the door-binding fix landed, per the launch order's evidence bar.

### assertion:stop-hook-door-binding-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The three named files (spine_rail.py, test_spine_rail.py, the PostToolUse block of settings.json) were expected to be sufficient for a 0-failed suite.

### assertion:stop-hook-door-binding-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Adding a second PostToolUse entry for spine_rail.py -- a new matcher, an identical command string to the existing Bash-matcher entry -- broke two things outside the named file-ownership fence. install_constellation.HOOK_SPECS, a hand-maintained table a drift-detector test holds byte-identical to .claude/settings.json, had no entry for the new matcher. add_hook_entry's dedup-on-write, scoped to command-string-alone across an entire event, silently dropped the second registration during --wire-hooks, because both entries built the identical command string. Two further tests carried hardcoded literal counts that the fifth spec broke.

### assertion:stop-hook-door-binding-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Five tests failed on the first full-suite run after the door-binding fix landed clean at the targeted-suite level; a second full-suite run after the cascading fix confirmed 0 failed, at exactly baseline plus the sixteen new door-path tests.

### assertion:stop-hook-door-binding-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The fix added the missing HookSpec entry, rescoped add_hook_entry's dedup key from command-alone to the (matcher, command) pair, and updated the two hardcoded counts to the dynamic len(installer.HOOK_SPECS) pattern the same file already used elsewhere -- mechanical and minimal, and floated explicitly at this run's review step rather than left implicit in the diff.

## Diagnosis (optional)

### assertion:stop-hook-door-binding-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A settings.json hook table and its installer-side mirror were held together by a test that compares full entries, while the installer's own write path deduplicated by a narrower key (command text alone) that happened to be sufficient for every spec that existed before this run added a second spec sharing a script and event.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
