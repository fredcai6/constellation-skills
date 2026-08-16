<!-- episode-state: schema=1 id=cleanup-b-context-identity-003 status=active -->

# episode: cleanup-b-context-identity-003

## Mechanical
- run: cleanup-b-context-identity
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-b-context-identity/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 2
- artifact-ref: .agent-work/cleanup-b-context-identity/measurement/probe_cross_key.py
- artifact-ref: .agent-work/cleanup-b-context-identity/measurement/README.md

## Agent-supplied

### assertion:cleanup-b-context-identity-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Update measurement/probe_cross_key.py at g1-integrate so the archived artifact asserts the post-fix world, then confirm the new assertion is load-bearing by running it against a real pre-fix worktree at 3bc87e93 caret rather than trusting that it would fail.

### assertion:cleanup-b-context-identity-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The red-direction run would merely confirm the probe refuses on a tree that predates the fix, adding little beyond the green run already observed.

### assertion:cleanup-b-context-identity-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It exposed a real defect in the probe's own module loader: _load never registered the loaded module in sys.modules, which dataclass frozen field resolution requires, and it raised AttributeError NoneType object has no attribute __dict__ on the pre-fix tree while working fine on the post-fix tree because the post-fix hook loads gauge_reader first and registers it as a side effect.

### assertion:cleanup-b-context-identity-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The bug was invisible in exactly the world the probe was written for, so a green-only verification would have shipped a measurement artifact that breaks the first time anyone runs it anywhere else; catching it cost two failed runs and a three-line fix.

### assertion:cleanup-b-context-identity-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Registering the module in sys.modules before exec_module fixed the load, and a second observation followed: the probe then failed on the pre-fix tree for a different and legitimate reason, so it now detects the missing owner_key API and prints a refusal naming the pre-fix record instead of dying with a traceback.

## Diagnosis (optional)

### assertion:cleanup-b-context-identity-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A path-loaded module that is also loaded by something else in the same process inherits that other loader's sys.modules registration, so its own omission stays invisible until it runs somewhere that other loader does not.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
