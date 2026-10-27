# Implementer Handoff

## Gate
g1-fixture

## Task
Create answer.txt containing exactly 42 followed by a newline.

## Protected Intent
Exercise artifact delivery without touching any existing project or GPU workload.

## Test Mode
test-after allowed — this is a disposable text fixture.

## Close Criteria
answer.txt is exactly three bytes: 34 32 0a. The result records the observed check.

## Allowed Scope
Only answer.txt and result.md in this disposable fixture directory.

## Specific Exclusions
No network, dependency installation, GPU access, or changes outside this directory.

## Required Evidence
Read answer.txt as bytes and assert equality to b"42\n". Record the command and result.

## Verification Commands
Use /usr/bin/python3 to read answer.txt and assert its bytes are b"42\n".

## Authority
The human approved a bounded hosted validation of Constellation Pi artifact delivery.

## Stop Conditions
Missing permissions or inability to verify the bytes. Record a non-complete result.

## Result Artifact
`result.md`

## Return Format
Write a Markdown IMPLEMENTER_RESULT with headings Assigned gate, Completed slice,
Scope, Test mode, Evidence, Stop conditions hit, Workflow Feedback, and Return status.
Return status must be lowercase complete, partial, blocked, out-of-scope, or failed.
After writing the file call submit_result. Acknowledge delivery without explaining it.
