# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g1`

## Task
Implement solution for Project Euler Problem #1 (sum of all multiples of 3 or 5 below 1000) and pytest test verifying the answer.

## Protected Intent
Produce correct, testable solution that prints the expected answer when run. Test must be independently reproducible.

## Test Mode
TDD required — test-first approach for verifiable correctness of algorithm.

## Close Criteria
- `solution.py` exists in workspace root, computes correct sum, prints the answer
- `test_solution.py` exists in workspace root with passing pytest test(s)
- pytest runs green with all tests passing
- solution.py when run directly prints only the numeric answer (233168)

## Allowed Scope
- Create `solution.py` in workspace root
- Create `test_solution.py` in workspace root
- No other files

## Specific Exclusions
None — this is a greenfield implementation.

## Constraints
- Files must be in workspace root, NOT under `.claude/`
- Must use pytest for testing
- Solution must print the answer when run (not just return it)
- Algorithm: sum multiples of 3 or 5 below 1000

## Map Anchors (inbound)
- **Structural:** None — greenfield
- **Capability:** None — standalone algorithm
- **Constraints/assumptions:** Files in workspace root; pytest testing; solution prints answer
- **Decision anchors:** None
- **Evidence expectations:** pytest passes; solution.py prints correct answer (233168)
- **Map confidence flags:** None

## Deliverable Path Check
- **Committed** — `solution.py`; verified via `git check-ignore solution.py` → exit 1 (not ignored)
- **Committed** — `test_solution.py`; verified via `git check-ignore test_solution.py` → exit 1 (not ignored)
Note: Both files are new and untracked until staged. `git diff` will show 0 files; files appear in `git status` as untracked.

## Required Evidence
- pytest output showing all tests pass
- Output of running `py solution.py` showing the answer: 233168
- Confirmation that both files exist in workspace root via `ls -la solution.py test_solution.py`

## Verification Commands

Exact commands to run.

```bash
pytest test_solution.py -v
py solution.py
ls -la solution.py test_solution.py
```

## Suggested Model Tier
Simple bounded — straightforward algorithm with clear correctness criteria.

## Authority
Launch order specifies deliverables and location. Algorithm is standard Project Euler #1 (publicly documented, answer is 233168).

## Stop Conditions
Stop and return if: files cannot be created in workspace root, pytest framework unavailable, Python runtime unavailable.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
