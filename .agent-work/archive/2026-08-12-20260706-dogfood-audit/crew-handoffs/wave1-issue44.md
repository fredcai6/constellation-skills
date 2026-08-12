# Launch Order: wave1-44 — Engine: accept attest for artifact checks (#44)

## Mission
Kill the highest-recurrence constellation defect in the dogfood corpus (`engine-artifact-attest`, 10 recurrences at f1Brainz): artifact-type postconditions refuse the `attest` verb, forcing agents to `attach` evidence to BOTH gN-review and gN-integrate as a re-derived workaround every run. Also: document the `attest --which {preconditions,postconditions}` distinction. Full issue: `gh issue view 44`.

Design intent (implementation is yours to shape after reading the engine): satisfying an artifact postcondition should not require double-attaching identical evidence to two tasks. Acceptable shapes include: `attest` referencing an existing attached evidence id; an attach that satisfies matching artifact postconditions on sibling tasks of the same gate; or a single-attach flow the docs bless. Pick the smallest change consistent with the engine's "enforces mechanism, never judges quality" doctrine, and say why in the PR.

## Prior-Wave Verdicts
None — wave 1.

## Pre-Rulings
- PR-3 applies: `global-everyone.md` doctrine (the "Engine verbs" section that codifies attach-to-both) must be updated in this same PR — doctrine follows mechanism. Locate the source file under `skills/` (it is bundled per-skill at install; update the source(s), not installed copies).
- Backward compatibility: existing spines/checklists in the wild must not break; the old attach-to-both flow may keep working.
- Regression test covering the previously-refused path is required.

## Workspace
Worktree: `C:/Programs/constellation-skills-worktrees/issue-44`, branch `constellation/issue-44`, base origin/main 363d27a, created via `git worktree add -b constellation/issue-44 <path> origin/main`. First step before any git operation: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-worktrees/issue-44` must exit 0; paste output in your verdict.

## File Ownership
`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, engine tests, and ONLY the engine-verbs/attest lines of the `global-everyone.md` source. Fence: do not touch `run_crew.py` (#46), install bundle tuples (#43, wave 2), Windows-hazards doctrine sections (#49).

## Budget
Model tier: opus-class. One implementer pass + one fresh-context reviewer subagent before the PR.

## Stop Conditions
Stop and query the Admiral if: the fix requires a breaking schema change to checklist JSON; or the engine's lease/session semantics need modification (that's #47, wave 2).
