<!-- episode-state: schema=1 id=epic-567-door_cmdr-g-006 status=active -->

# episode: epic-567-door_cmdr-g-006

## Mechanical
- run: epic-567-door/cmdr-g
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-g/context/feedback.json
- refusals: 0
- reopens: 1
- rework-count: 0
- failed-commands: 0
- artifact-ref: PR #622
- artifact-ref: tests/test_spine_lifecycle.py

## Agent-supplied

### assertion:epic-567-door_cmdr-g-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Fixed a Windows-CI-only test failure (result['refusal'] == expected comparing unequal despite printing identically) by normalizing \r\n to \n in the subprocess-captured comparison value, on the assumption the mismatch was a line-ending difference.

### assertion:epic-567-door_cmdr-g-006.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The newline normalization would make both previously-failing tests pass on the next Windows CI run, since the truncated pytest diff ('...e the engine.' == '...e the engine.') looked consistent with two texts differing only in invisible characters.

### assertion:epic-567-door_cmdr-g-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The re-run Windows CI failed the identical two tests again, with the identical error signature. Reading the FULL diff this time (not the truncated summary) showed the real difference: 'the JSON â€” use' vs 'the JSON — use' -- a UTF-8 em-dash mis-decoded as cp1252 (mojibake), not a newline difference at all. The root cause was subprocess.run(text=True) decoding the child's stdout using the Windows runner's default locale encoding (cp1252) because PYTHONIOENCODING=utf-8 in the child's env governs only the child's write side, never this process's read side.

### assertion:epic-567-door_cmdr-g-006.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A second full reopen-fix-rearchive cycle (identical mechanical shape to the first) was needed because the first fix, while reasonable-looking from the truncated diff alone, did not address the actual cause. The corrected fix (encoding="utf-8" passed explicitly to subprocess.run) was verified against the actual Windows CI run before being reported as done, rather than trusted from local (Linux) test output, which cannot exercise this failure mode at all.

### assertion:epic-567-door_cmdr-g-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Did not report the first fix as confirmed-working without checking the actual CI result -- re-ran CI, read the full failure log (not just the truncated assertion summary pytest prints by default), diagnosed the real cause from the literal mojibake bytes, and fixed the actual mechanism rather than re-guessing. Kept the (harmless, and independently defensible) newline normalization in place alongside the encoding fix, since a genuine newline difference remains a real possibility for a different comparison even though it was not the cause here.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
