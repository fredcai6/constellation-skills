# Dispatch: Project Euler Problem #2 (delegated)

You are dispatched to run one bounded issue with **no reachable human**. Load the
**constellation-commander-delegated** skill from this project's installed skills
(`.claude/skills/`) and run the issue under it, treating this dispatch as your
launch order.

## The issue

Solve **Project Euler Problem #2**, with tests:

> By considering the terms in the Fibonacci sequence whose values do not exceed four million, find the sum of the even-valued terms.

## Deliverables

In the **workspace root** (not under `.claude/`):

- `solution.py` — computes and **prints** the answer.
- `test_solution.py` — a `pytest` test asserting the computed answer equals the
  expected value; `pytest` green.

When the issue is fully complete, write `work-complete.txt` in the workspace root
(any content) as your final act.
