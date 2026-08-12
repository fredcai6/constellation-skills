# Implementer Handoff

## Gate
`g1`

## Task
Implement solution.py (compute sum of all multiples of 3 or 5 below 1000, print the result) and test_solution.py (pytest test asserting the answer equals 233168).

## Protected Intent
Deliver a correct, verifiable solution to Project Euler Problem #1.

## Test Mode
TDD required — test must be written and green.

## Close Criteria
- solution.py exists in workspace root and computes the sum of multiples of 3 or 5 below 1000
- solution.py prints the computed answer to stdout
- test_solution.py exists in workspace root
- test_solution.py uses pytest
- test_solution.py asserts the computed answer equals 233168
- pytest test_solution.py passes

## Allowed Scope
- Create solution.py in workspace root
- Create test_solution.py in workspace root

## Specific Exclusions
None.

## Constraints
- Files must be in workspace root, not under .claude/ or any subdirectory
- The expected answer is 233168 (sum of multiples of 3 or 5 below 1000)
- solution.py must print output (requirement per dispatch)

## Map Anchors (inbound)
- **Structural:** None
- **Capability:** None
- **Constraints/assumptions:** None
- **Decision anchors:** None
- **Evidence expectations:** None
- **Map confidence flags:** None

## Deliverable Path Check
- **Committed** — `solution.py`; will be untracked until staged. Command: `git check-ignore solution.py` exits 1 (not ignored).
- **Committed** — `test_solution.py`; will be untracked until staged. Command: `git check-ignore test_solution.py` exits 1 (not ignored).

## Required Evidence
- Output of `pytest test_solution.py -v` showing test pass
- Output of `python solution.py` showing the answer

## Verification Commands

```bash
pytest test_solution.py -v
python solution.py
```

## Suggested Model Tier
simple bounded — straightforward computational problem

## Authority
Problem statement and expected answer (233168) are given by Project Euler Problem #1 definition.

## Stop Conditions
Stop and return if: files cannot be created in workspace root, pytest is not available.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
