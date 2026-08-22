<!-- episode-state: schema=1 id=w2-reindex-003 status=active -->

# episode: w2-reindex-003

## Mechanical
- run: w2-reindex
- project: constellation-skills
- role: commander
- spine-step: execute:g3-implement
- context-manifest-ref: none -- no context_manifest.py invocation recorded this session
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 1
- artifact-ref: crew-handoffs/g3-implement-handoff.md
- artifact-ref: crew-handoffs/g3-implement-handoff-relaunch.md
- artifact-ref: tests/test_code_map_precommit_e2e.py

## Agent-supplied

### assertion:w2-reindex-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: g3-implement's first attempt was dispatched to write and verify the end-to-end proof suite, including running the full local pytest suite as its final regression check.

### assertion:w2-reindex-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The crew would run the full suite to completion inside its own turn and write IMPLEMENTER_RESULT before ending.

### assertion:w2-reindex-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The crew's own stdout showed it launched the full suite in the background and ended its turn stating it would 'pick this back up automatically when it finishes' -- the CLI process then exited, killing the backgrounded pytest run with it, and no IMPLEMENTER_RESULT was ever written. recover_crews.py classified the attempt NEEDS-ABANDON. The actual substantive work (the 519-line, 7-method end-to-end test file covering all 8 required cases) was already complete and correct at the moment the crew wait-by-ended its turn -- confirmed by directly running the file after the fact -- so the failure was purely in the final verification step, not the implementation.

### assertion:w2-reindex-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One abandon+relaunch cycle (attempt-2) to re-verify rather than rewrite, plus a second relaunch (attempt-3) after the Commander separately fixed an unrelated map-staleness gap attempt-2 correctly found and could not fix within its own tests/-only scope.

### assertion:w2-reindex-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Abandoned the dead attempt via scripts/run_crew.py --abandon, then relaunched with a handoff that named the already-complete work explicitly (so it was verified, not redone) and gave the exact foreground nohup+until polling idiom to use instead of backgrounding the suite run.

## Diagnosis (optional)

### assertion:w2-reindex-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A ~3.5-minute full-suite pytest run is long enough that a crew's own harness may auto-background a bare Bash invocation of it, and the crew's own instructions (the g3-implement handoff) named the required evidence but did not explicitly forbid ending the turn on a backgrounded long-running command, which this project's own doctrine names as a known failure shade ('wait-by-ending-turn').

### assertion:w2-reindex-003.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: Any handoff whose Required Evidence includes a full-suite run should name the foreground nohup+until polling idiom explicitly, not just the bare command, given this failure mode is already documented doctrine but was not spelled out in the first g3-implement handoff.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
