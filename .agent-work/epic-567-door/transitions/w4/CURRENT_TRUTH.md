# Epic #567 -- the door is the interface

**Status at the w4 boundary: complete, pending human acceptance.** Three waves, twelve lanes, eight PRs merged. origin/main at c30ef5ae, 3431 passed / 0 failed in a clean detached worktree.

## Definition of done

1. A fresh door reaches an existing spine without the CLI -- **met** (spine_bind, wave 1, proven by the Admiral it first blocked).
2. No agent-facing file teaches the CLI as a path for agents -- **met** (zero `CLI fallback` clauses in skills/, specs/ and the tracked overlay; a 718-line guard fails if any returns; a cold cartographer confirmed 'no CLI fallback used or needed at any gate').
3. The regrowth mechanism is understood and stopped -- **met** (test_mcp_adoption.py had been *mandating* the CLI text across nine assertions; inverted).
4. A launcher takes declared defaults, not machine-local ones -- **met** (#619 and #633, plus the commander-delegated repair and its doctrine-scanning guard).

## Open deliberately, each with its diagnosis filed

- **#634** the crew half of one-spine-per-agent, the execute.json migration, and that the freeze protects a run's completion but not its acceptance.
- **#638** the door's path, identity and spine fixed at process start -- one defect behind both the self-waive refusal and the archive-move deadlock, and behind an implementer having no door for its own plan.
- **#639** the installer can only ship skills, so the checklist engine must wear a SKILL.md.
- **#632** helper environment inheritance. **#636** the registry losing concurrent dispatches. **#575** parked.

## Closed this epic

#559, #535, #611, #619, #633, #565. #442 the human closed directly.

Next: closeout -- episodes, the feedback sweep, hygiene, summary, acceptance.
