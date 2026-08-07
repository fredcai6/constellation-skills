# Problem Statement

**Source**: Project Euler Problem #1

**Task**: Find the sum of all the multiples of 3 or 5 below 1000.

## Deliverables

1. `solution.py` — Python script that computes and **prints** the answer to stdout
2. `test_solution.py` — pytest test file that:
   - Imports/calls the solution logic
   - Asserts the computed answer equals the expected value
   - Passes when run with `pytest`
3. `work-complete.txt` — Completion signal file (any content)

## Scope

- **In scope**: Implement the computation logic, print the result, write tests
- **Out of scope**: Command-line arguments, configuration, optimization beyond correctness

## Success Criteria

- `pytest` runs green
- `solution.py` prints the correct answer when executed
- All deliverables present in workspace root (not under `.claude/`)
- `work-complete.txt` exists as the final completion signal

## Protected Intent

Solve this as a bounded constellation issue following the full Commander workflow, demonstrating:
- Clean separation of computation and presentation
- Test coverage asserting correctness
- Deterministic, reproducible output

## Baseline Verification

No existing `.py` files in the workspace (confirmed via README). Clean slate implementation.
