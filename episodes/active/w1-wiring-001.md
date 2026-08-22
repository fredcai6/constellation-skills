<!-- episode-state: schema=1 id=w1-wiring-001 status=active -->

# episode: w1-wiring-001

## Mechanical
- run: w1-wiring
- project: constellation-skills
- role: commander
- spine-step: g1-census
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: docs/CHECK_SCRIPT_CENSUS.md

## Agent-supplied

### assertion:w1-wiring-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Classify every check-shaped script in scripts/ as live, unwired, or dead, redoing a crude skills/-only grep properly.

### assertion:w1-wiring-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A script's own dedicated pytest test file would be sufficient evidence to distinguish coverage from enforcement.

### assertion:w1-wiring-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It was not. The first census draft classified verify_retirement.py, verify_context_declaration.py, verify_coverage_ledger.py, verify_skill_registered.py, and check_template_overlay_freshness.py as unwired because each had only its own dedicated tests. Running the full suite against that first draft's own disposition changes tripped verify_retirement.py's unapproved-store-mention guard on a line the census itself had just written -- a live, suite-enforced check, in the act of catching a real thing, while the census still called it unwired.

### assertion:w1-wiring-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Five of twenty-six rows were misclassified until this was caught mid-run; the corrected classification changed the census from 12 live/13 unwired/1 dead to 17 live/8 unwired/1 dead, which is the difference between a marginal case for a mechanism and a clear one.

### assertion:w1-wiring-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: After the trip, re-checked every remaining unwired candidate's own test file for a test that calls the script's check/scan function unconditionally against the real repo (ROOT/REPO_ROOT), not a temp dir or authored fixture, and asserts pass/fail -- a fifth reachability category the original four-category method missed. Documented the correction in the census itself rather than silently fixing the numbers.

## Diagnosis (optional)

### assertion:w1-wiring-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: 'Has its own dedicated test' was treated as one signal (coverage) when it actually splits into two (coverage of the tool's own logic against synthetic input, vs. enforcement of the tool's verdict against the real repo), and only the second is 'live' in the two-bin-rule sense this census exists to measure.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
