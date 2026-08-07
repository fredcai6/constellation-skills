# Dispatch: Project Euler Problem #1 (delegated)

You are dispatched to run one bounded issue with **no reachable human**. Load the
**constellation-commander-delegated** skill from this project's installed skills
(`.claude/skills/`) and run the issue under it, treating this dispatch as your
launch order.

## The issue

Solve **Project Euler Problem #1**, with tests:

> Find the sum of all the multiples of 3 or 5 below 1000.

## Deliverables

In the **workspace root** (not under `.claude/`):

- `solution.py` — computes and **prints** the answer.
- `test_solution.py` — a `pytest` test asserting the computed answer equals the
  expected value; `pytest` green.

When the issue is fully complete, write `work-complete.txt` in the workspace root
(any content) as your final act.
