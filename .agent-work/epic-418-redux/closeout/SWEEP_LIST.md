# Worktree sweep list — decided BEFORE the close, while nothing is urgent

`git worktree remove` is the one destructive step in closeout. This file decides it in advance so the
decision is not made under time pressure at the end of a long run. **Derived by command 2026-08-08,
not from memory.**

## The classification trap, found while building this list

The obvious eligibility test — *"is the branch merged into main?"* — is **a check that cannot fail on
an empty branch.** `git branch --merged main` reports `epic-418/w5-crew-addressing`,
`…/w5-engine-internals` and `…/w5-readiness-458` as **merged**. They are not. They have **zero
commits**, so they are trivially ancestors of main, and a branch with no work is indistinguishable
from a branch whose work landed.

**Correct test: `ahead` count AND forge state, together.** `ahead=0 AND pr=MERGED` is landed;
`ahead=0 AND pr=none` is *empty*, which on a live crew means **work in progress that has not been
committed yet** — the single most destructive thing to sweep.

## SWEEP — only these, and only after their PR is MERGED and the harvest probe is clean

| worktree | branch | state now |
|---|---|---|
| `epic418-a2-467` | `epic-418/a2-467-trip-semantics` | **ELIGIBLE NOW** — `ahead=0`, PR **#505 MERGED**, harvest probe returns a genuine null on both channels |
| `epic418-w5-gates` | `epic-418/w5-bookend-gates` | after merge |
| `epic418-w5-readiness` | `epic-418/w5-readiness-458` | after merge |
| `epic418-w5-addressing` | `epic-418/w5-crew-addressing` | after merge |
| `epic418-w5-engine` | `epic-418/w5-engine-internals` | after merge |
| `epic418-w5-docs` | `epic-418/w5-docs` | after merge (PR #509) |

**Order is mandatory: harvest → verify merged on the forge → remove → `git worktree prune`.** Never
close an issue or sweep a tree on an ancestry test; squash-merge makes ancestry return the same answer
for merged and abandoned.

## DO NOT SWEEP — none of these belong to this epic

| worktree | why it stays |
|---|---|
| `governor-264` | **PROTECTED. Never sweep.** Carries #264's unmerged 1144-line branch, `ahead=3`. Landing it is a scope change that was deliberately declined; destroying it would delete the work that decision preserved. |
| `explore-code-map` | **`ahead=36`, unmerged.** Belongs to the code-map effort (#456), not to #418. |
| `issue-456` | **`ahead=134`, unmerged.** Same effort. Sweeping this would be the worst single action available in this repo. |
| `.proto-exc6-governor-subagent-identity` | `ahead=1`, unmerged. Prototype evidence from the `explore-post-phase1` run — the governor identity demo this epic's workstream A was cut from. |
| `.proto-exc8-spine-instructions` | `ahead=1`, unmerged. The spine-relocation prototype workstream C rests on. |
| `.proto-exc9-mcp-front-door` | `ahead=1`, unmerged. **The MCP prototype F (#424) will be built from** — and F is the next effort after this epic closes. |
| `agent-a247f573f8ff07d25`, `agent-adbe19c21cc561d95` | Harness-created under `.claude/worktrees/`. Not this run's to dispose of. |

**The three `.proto-*` trees are load-bearing for work that has not happened yet.** exc9 in particular
is the prototype for the very next effort. They read as stale leftovers and are not.

## Before any removal

1. `bash .agent-work/epic-418-redux/closeout/harvest_probe.sh` — collect every **UNCOMMITTED** and
   **ON THIS BRANCH ONLY** line it reports. Presence of a tracked file proves nothing (that was the
   probe's own v1 defect).
2. Confirm the PR is **MERGED on the forge** (`gh pr view`), not merged-looking by ancestry.
3. `git worktree remove <path>` then `git worktree prune`.
