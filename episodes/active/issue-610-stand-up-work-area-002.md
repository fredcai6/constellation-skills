<!-- episode-state: schema=1 id=issue-610-stand-up-work-area-002 status=active -->

# episode: issue-610-stand-up-work-area-002

## Mechanical
- run: issue-610-stand-up-work-area
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: n/a -- no context-manifest artifact produced this run
- refusals: 2
- reopens: 0
- rework-count: 2
- failed-commands: 2
- artifact-ref: scripts/install_constellation.py
- artifact-ref: .agent-work/issue-610-stand-up-work-area/execute.json

## Agent-supplied

### assertion:issue-610-stand-up-work-area-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author command-check postconditions for two gates (g2: SKILL_REFERENCE_BUNDLES wiring; g7: check_skill_freshness.py sweep) that verify the underlying edit correctly.

### assertion:issue-610-stand-up-work-area-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Running the check commands as authored would exit 0 once the corresponding edit was correct.

### assertion:issue-610-stand-up-work-area-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: g2's check crashed with an unrelated AttributeError (importing install_constellation.py via importlib.util without registering the module in sys.modules first breaks its @dataclass(frozen=True) decorators) -- the underlying edit was already correct. g7's check ran check_skill_freshness.py's raw exit code, which could never pass: 7 unrelated templates are intentionally left stale (out of scope) and the resynced template correctly reads 'both-changed' rather than 'up-to-date' since updating .baseline/ was explicitly out of scope.

### assertion:issue-610-stand-up-work-area-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Two advance attempts refused on postconditions that were bugs in the CHECK, not the work. Both fixed in-flight via the engine's own amend --delta retext-check verb (authority human), no rework of the actual edits.

### assertion:issue-610-stand-up-work-area-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: amend --delta <file> --reason ... --authority human with a retext-check op, per gate, correcting the check command text without marking the condition satisfied by the amendment itself.

## Diagnosis (optional)

### assertion:issue-610-stand-up-work-area-002.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A postcondition check authored and then never dry-run before being wired into the gate plan can encode an authoring bug (importlib module registration) or an over-broad success criterion (a tool's whole-repo exit code standing in for one file's correctness) that only surfaces at advance time.

### assertion:issue-610-stand-up-work-area-002.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: Run a postcondition's command by hand once, against the pre-edit state, before wiring it into execute.json -- a check that already fails for reasons unrelated to the work it's meant to gate is cheaper to catch before the gate closes on it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
