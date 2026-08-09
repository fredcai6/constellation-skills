<!-- episode-state: schema=1 id=epic-418-redux-006 status=active -->

# episode: epic-418-redux-006

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: origin-run:epic-418-redux
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-redux-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Establish a green baseline on main before merging any wave-5 pull request, so every merge is gated against a known-good reference rather than a remembered one.

### assertion:epic-418-redux-006.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The suite would pass, since the only commits since the last green run touched work-area documents and a tracked episode path.

### assertion:epic-418-redux-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It exited nonzero with 'No module named pytest'. The `py` and `python` tokens resolve to different interpreters under this tool -- 3.12.13 and 3.14.3 -- and only one has pytest. The whole epic had been driven with `py`, which runs every stdlib script in the repo without complaint.

### assertion:epic-418-redux-006.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The failure exits nonzero, so it reads as a red suite rather than as an absent test runner. It surfaced only because the tree was known-green; on a tree where a red was plausible it would have been attributed to the code under change. A crew reported afterwards that the spine's own command postconditions already invoke `python`, so gate verification and hand verification had been running on different interpreters throughout.

### assertion:epic-418-redux-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: All five crews were sent a correction mid-flight with the instruction to re-derive any red, green, or exit code that came from a `py` invocation. Every verifier result asserted earlier in the session was then re-run under `python` and compared; all five agreed.

## Diagnosis (optional)

### assertion:epic-418-redux-006.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: An interpreter that starts, and runs scripts, and cannot run the suite passes every probe short of running the suite. The two interpreters also differ by two minor versions, so agreement on stdlib scripts is a property of this moment rather than of the arrangement.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
