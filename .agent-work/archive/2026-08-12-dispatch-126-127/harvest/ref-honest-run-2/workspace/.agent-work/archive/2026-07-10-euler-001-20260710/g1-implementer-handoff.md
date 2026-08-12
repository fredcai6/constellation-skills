# Implementer Handoff

## Gate
`g1`

## Task
Implement Project Euler Problem #1: compute the sum of all multiples of 3 or 5 below 1000. Create `solution.py` that computes and prints the answer, and `test_solution.py` with pytest tests asserting correctness.

## Protected Intent
Produce a working, tested solution that correctly solves the stated problem and serves as a demonstration of the constellation workflow on a bounded computational task.

## Test Mode
Test-after allowed — straightforward computational problem with deterministic output; the correct answer is verifiable via independent computation.

## Close Criteria
- `solution.py` exists in workspace root and contains computation logic
- `solution.py` prints the correct answer (233168) to stdout when executed
- `test_solution.py` exists in workspace root and contains pytest tests
- `pytest test_solution.py` runs green
- Test asserts the computed answer equals 233168

## Allowed Scope
- Create `solution.py` in workspace root
- Create `test_solution.py` in workspace root
- No other files

## Specific Exclusions
None — clean slate implementation.

## Constraints
- Deliverables in workspace root (NOT under `.claude/`)
- `solution.py` must print to stdout (not just return a value)
- Must use pytest for testing (not unittest or other frameworks)
- Solution must handle the exact problem: multiples of 3 OR 5 below 1000 (not inclusive of 1000)

## Map Anchors (inbound)
- **Structural:** None — greenfield implementation
- **Capability:** None — no existing capabilities
- **Constraints/assumptions:** Deliverables in workspace root; solution.py prints to stdout; pytest test must pass
- **Decision anchors:** None
- **Evidence expectations:** pytest runs green; solution.py prints correct answer
- **Map confidence flags:** None

## Deliverable Path Check
- **Committed** — `solution.py`; verified via `git check-ignore solution.py` (exit 1 expected — not ignored)
- **Committed** — `test_solution.py`; verified via `git check-ignore test_solution.py` (exit 1 expected — not ignored)

Note: These are new untracked files until staged. `git diff` will show 0 files; both appear in `git status` as untracked.

## Required Evidence
- Output of `pytest test_solution.py -v` showing all tests passing
- Output of `python solution.py` showing the correct answer (233168)
- Brief verification that the computation logic is correct (e.g., manual spot-check or explanation)

## Verification Commands

```bash
pytest test_solution.py -v
python solution.py
```

## Suggested Model Tier
Simple bounded — straightforward computational problem with well-defined requirements and deterministic verification.

## Authority
Launch order specifies the deliverables and acceptance criteria. No structural or design decisions needed.

## Stop Conditions
Stop and return if: workspace root is not writable, pytest is not available, or the computation produces an unexpected result that cannot be reconciled.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed (solution.py, test_solution.py created), test mode satisfied, evidence produced (pytest output, solution.py output), assumptions used, stop conditions hit (if any), out-of-scope observations, workflow feedback.
