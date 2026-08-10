<!-- episode-state: schema=1 id=epic-418-followon-commander-424-001 status=active -->

# episode: epic-418-followon-commander-424-001

## Mechanical
- run: epic-418-followon-commander-424
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/commander-424/execute.json
- refusals: 12
- reopens: 0
- rework-count: 5
- failed-commands: 4
- artifact-ref: .agent-work/epic-418-followon/commander-424/MEASUREMENT.md
- artifact-ref: .agent-work/epic-418-followon/commander-424/evidence/g4-dc5/score_arm.py
- artifact-ref: .agent-work/epic-418-followon/commander-424/evidence/g4-dc5/control_scorer.py
- artifact-ref: .agent-work/epic-418-followon/commander-424/crew-handoffs/g4-reviewer-result.md

## Agent-supplied

### assertion:epic-418-followon-commander-424-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Measure DC5 -- whether spine-management cost falls attributably to the MCP door -- by running two arms over a real role spine and counting invocation attempts from the driving agent's own call record.

### assertion:epic-418-followon-commander-424-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The scorer counts one invocation attempt per attempt to invoke the engine, identically across both arms, so the two arms are comparable.

### assertion:epic-418-followon-commander-424-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The scorer was wrong four separate times, each time in a way that biased the comparison. It counted one Bash tool call as one attempt, when the CLI arm batched three or four engine invocations per command. It scored a --help invocation's usage block as five malformed calls, because help output matches the argparse-error signature. It counted static occurrences of the string checklist_engine.py in the command text, so a shell for-loop that ran the engine six times scored as one -- rep2-cli was published as 18 attempts / 2 fumbles and was truly 23 / 7. It scored one argparse rejection as two shape errors, because such a rejection prints both a usage block and an error line. I found the first two myself before scoring; the third was found by the gate's reviewer, which hand-parsed the raw record rather than re-running the scorer; the fourth was found by positive controls I only wrote because of that block.

### assertion:epic-418-followon-commander-424-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The third defect alone flipped DC5's verdict. Under it the per-arm spreads overlapped and the measurement read as a negative; corrected, the spreads separated and the pre-registered metric read as a pass. A published measurement was wrong by 5 invocation attempts and 5 fumbles on one of only four data points, and the error was in the direction that made the door look worse.

### assertion:epic-418-followon-commander-424-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Static command text became a floor rather than the count, with the actual count taken as the larger of static occurrences and engine-output marks (RAIL: / usage:) in the result. A control_scorer.py was added exercising every counter that reports zero in the real arms; the reviewer then broke two of those controls in scratch copies and confirmed they fail when the counter is broken.

## Diagnosis (optional)

### assertion:epic-418-followon-commander-424-001.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Every one of the four defects made the instrument harder to lose with, not easier: three inflated the CLI arm's counts and one inflated its error counts. The scorer was written by the party with an interest in the outcome and was checked by reading it, which cannot detect a counter that is simply never exercised. Re-running the scorer proves determinism, not correctness -- the one defect that changed a published number was found by parsing the raw record independently.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
