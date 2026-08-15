## Wave review — wave 2, gate refusal

Three Commanders finished, each with an independent reviewer APPROVE, and each parked correctly at `archive` because their launch orders fence them from publishing. Publication is the Admiral's delegated class, not the human's, and clearing that was mine to do.

It is as well that they parked. Re-measuring the baseline at gate time rather than reusing it, `main`'s Linux suite is green at 2980 passed / 0 failed — so every failure below belongs to the lane that produced it.

| Lane | Result | Nature |
|---|---|---|
| Codex tier | 1 failed | Stale generated map; change itself clean under 2,985 passing tests |
| #510 | 4 failed | Three inside the advisory text its own diff rewrote, plus the map |
| #530 | 3 failed | Its own episode record trips the episode-observation guard, plus the map |

The wave-2 gate makes any local Linux failure block merge outright, so none of this reaches the CI set-difference step. Nothing is published.

Two findings outlive the repair. First, a phantom: the Codex lane failed a test whose file is byte-identical to `main`, and it took four falsifications to attribute — reverting the lane's code, deleting its episodes, and moving `.agent-work` aside all left it red. The `.pyc` embedded `constellation-skills-wt/epic-568-codex-tier-routing`, the path the worktrees occupied before wave 1 relocated them, so `inspect.getsource` resolved to a dead file. Any gate measured in a relocated worktree before today is suspect. Second, and more costly: all three reviewers APPROVEd on targeted tests alone. Review depth, not implementation quality, is what let three red lanes reach the merge gate believing they were done.
