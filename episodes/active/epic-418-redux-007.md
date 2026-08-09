<!-- episode-state: schema=1 id=epic-418-redux-007 status=active -->

# episode: epic-418-redux-007

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-418-redux/closeout/LO-w5-c4-engine.md

## Agent-supplied

### assertion:epic-418-redux-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch the issue group the human named as 'the 474-480 group' to a wave-5 crew, by writing the assignment into that crew's launch order.

### assertion:epic-418-redux-007.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The launch order should carry every issue in the named range, and the crew's return should therefore account for the whole group.

### assertion:epic-418-redux-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The range 474..480 has seven members. The launch order LO-w5-c4-engine.md named five. #477 and #478 were never assigned, so they were never worked. The crew delivered exactly what its order listed, and nothing downstream could catch the gap: the order was the only definition of 'the group' any later reader could see. The omission was found by auditing issue states one at a time before the close, not by any gate.

### assertion:epic-418-redux-007.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: #477 was the defect that cost this run four crew relaunches -- the gauge was read from the run root rather than per checklist directory, so a crew did not inherit its Commander's reading. It sat unassigned through the wave that was supposed to fix it. The wave believed it had covered the group; an unassigned issue a wave believes it covered is invisible debt of the same class as a closed float that was silently reopened.

### assertion:epic-418-redux-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: #477 was dispatched late as a bounded implementer into its own worktree and merged as PR #517. #478 was carried deliberately with its disposition posted on the issue itself rather than only in the run notes, because it relocates directories the closeout tooling walks and five live crew work areas sat in, with no forcing function to make the move safe mid-run.

## Diagnosis (optional)

### assertion:epic-418-redux-007.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The assignment was derived by command from the human's phrasing, but the derived population had no total to check against. A contiguous range carries its own count -- seven -- and nothing compared the five written rows to it. The same shape produced the sweep list's 14-of-16 on the same day.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
