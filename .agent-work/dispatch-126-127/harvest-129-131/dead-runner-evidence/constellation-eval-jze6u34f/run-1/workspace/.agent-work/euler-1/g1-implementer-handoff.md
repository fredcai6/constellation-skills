# Implementer Handoff

## Gate
`g1`

## Task
Implement solution.py (computes sum of multiples of 3 or 5 below 1000, prints the answer) and test_solution.py (pytest test asserting correct answer equals expected value); both at workspace root.

## Protected Intent
Demonstrate working code with test coverage for a bounded mathematical problem.

## Test Mode
test-after allowed — straightforward algorithm, test verifies correctness

## Close Criteria
- solution.py exists at workspace root
- solution.py correctly computes sum of multiples of 3 or 5 below 1000
- solution.py prints the answer when executed
- test_solution.py exists at workspace root
- test_solution.py contains pytest test
- pytest test_solution.py passes (green)
- Test asserts correct answer value

## Allowed Scope
- solution.py at workspace root
- test_solution.py at workspace root

## Specific Exclusions
None

## Constraints
- Python 3
- pytest for testing
- Solution must print answer (not just return it)
- Files at workspace root (not under .claude/ or .agent-work/)

## Map Anchors (inbound)
- **Structural:** none — greenfield workspace
- **Capability:** none
- **Constraints/assumptions:** Python 3, pytest available, solution prints answer
- **Decision anchors:** none
- **Evidence expectations:** pytest green, correct mathematical answer (233168)
- **Map confidence flags:** none

## Deliverable Path Check
- **Committed** — `solution.py`; `git check-ignore solution.py` exits 1 (not ignored). NOTE: workspace not yet initialized as git repo, but path will not be ignored.
- **Committed** — `test_solution.py`; `git check-ignore test_solution.py` exits 1 (not ignored). NOTE: workspace not yet initialized as git repo, but path will not be ignored.

## Required Evidence
- solution.py file content
- test_solution.py file content
- `python solution.py` output showing the printed answer
- `pytest test_solution.py` output showing green/passed

## Verification Commands

```bash
python solution.py
pytest test_solution.py
```

## Suggested Model Tier
simple bounded — straightforward mathematical problem with clear correct answer

## Authority
LAUNCH_ORDER:Mission — scope and deliverables fixed by dispatch

## Stop Conditions
Stop and return if: deliverable paths must change, additional files needed, external dependencies beyond pytest required, scope ambiguity discovered.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed (solution.py, test_solution.py), test mode satisfied (test-after, pytest green), evidence produced (solution output, pytest output), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
