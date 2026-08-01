# Implementer Handoff

## Gate
`g1`

## Task
Create solution.py (computes and prints the sum of all multiples of 3 or 5 below 1000) and test_solution.py (pytest test asserting the computed answer equals the expected value).

## Protected Intent
Correctly solve Project Euler Problem #1: the sum must be accurate (233168).

## Test Mode
test-after allowed — straightforward math problem with deterministic answer, TDD not required.

## Close Criteria
- solution.py exists in workspace root
- solution.py computes the sum correctly (233168)
- solution.py prints the answer when run
- test_solution.py exists in workspace root
- test_solution.py contains a pytest test that asserts the correct answer
- pytest passes

## Allowed Scope
Create two new files in workspace root: solution.py, test_solution.py

## Specific Exclusions
Do not create files under .claude/ or .agent-work/

## Constraints
- Files must be in workspace root, not under .claude/ or .agent-work/
- solution.py must print the answer (not just return it)
- The algorithm must correctly identify multiples of 3 or 5 below 1000 (exclusive)

## Map Anchors (inbound)
- **Structural:** none — new files
- **Capability:** compute sum of multiples of 3 or 5 below 1000
- **Constraints/assumptions:** files must be in workspace root; solution.py must print the answer
- **Decision anchors:** none
- **Evidence expectations:** pytest test must pass
- **Map confidence flags:** none

## Deliverable Path Check
- **Committed** — solution.py; will be untracked until staged (git status will show it)
- **Committed** — test_solution.py; will be untracked until staged (git status will show it)

Note: This is not a git repo, so files will simply exist in the workspace root.

## Required Evidence
- Run `python solution.py` and verify it prints "233168" (or the correct sum)
- Run `pytest test_solution.py -v` and verify it passes
- List the created files with `ls -la solution.py test_solution.py`

## Verification Commands

```bash
python solution.py
pytest test_solution.py -v
ls -la solution.py test_solution.py
```

## Suggested Model Tier
simple bounded — straightforward math problem, no ambiguity

## Authority
The expected answer (233168) is the correct solution to Project Euler Problem #1, verified by the problem statement.

## Stop Conditions
Stop and return if: workspace root is not writable, pytest is not available, cannot compute the correct answer.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
