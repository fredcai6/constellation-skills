<!-- episode-state: schema=1 id=b433-render-directives-001 status=active -->

# episode: b433-render-directives-001

## Mechanical
- run: b433-render-directives
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/b433-render-directives/execute.json
- refusals: 2
- reopens: 0
- rework-count: 0
- failed-commands: 4
- artifact-ref: .agent-work/b433-render-directives/evidence/g2-r4-populated-field-flattens-to-nothing.txt
- artifact-ref: .agent-work/b433-render-directives/evidence/g2-integrate-successor-commander-verification.txt

## Agent-supplied

### assertion:b433-render-directives-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close the class of unrendered Task fields by un-excluding `directives` from the existing TaskFieldCompleteness property, which issue #420 had left excluded.

### assertion:b433-render-directives-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Removing `directives` from the exclusion set would put the field under the existing generic content-presence loop and guard it the same way `anchors` and `constraints` are guarded.

### assertion:b433-render-directives-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The un-excluded property reported green while asserting nothing about the field: `_flatten` returned an empty list for the nested-dict shape that every one of the 8 populated corpus `directives` blocks actually carries, so the inner loop body never executed, and a single `checked_any` flag for the whole loop let the other fields cover for it.

### assertion:b433-render-directives-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The cheap change would have shipped a check that cannot fail, closing the issue on paper while leaving the defect class open; catching it cost a total leaf extractor, a per-field ledger, a builder-superset assertion and an in-suite negative self-test instead of a one-line exclusion edit.

### assertion:b433-render-directives-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Deliberately break the world the check is supposed to catch and confirm the check goes red before trusting it green: nulling the `directives` passthrough in `state()` now fails the property by field name, and the same break left the pre-fix property passing.

## Diagnosis (optional)

### assertion:b433-render-directives-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A property whose extractor is partial can silently skip a field, and a single boolean success flag shared across a loop cannot distinguish 'every field checked' from 'at least one field checked'.

### assertion:b433-render-directives-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: A loop-based property needs a per-item ledger compared against the expected item set, and a total extractor, or it reports on its own coverage rather than on the code.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
