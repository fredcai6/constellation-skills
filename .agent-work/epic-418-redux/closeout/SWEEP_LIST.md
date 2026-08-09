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
| `epic418-a2-467` | `epic-418/a2-467-trip-semantics` | **ELIGIBLE** — `ahead=0`, PR **#505 MERGED**, clean on all three probe channels. Its 9 **ignored** paths were inspected and judged disposable (`gauge.json` transients and `__pycache__`). **Not swept during the wave**: keeping it costs nothing and a premature sweep is unrecoverable, so it goes at closeout with the rest. |
| `epic418-w5-gates` | `epic-418/w5-bookend-gates` | after merge |
| `epic418-w5-readiness` | `epic-418/w5-readiness-458` | after merge |
| `epic418-w5-addressing` | `epic-418/w5-crew-addressing` | after merge |
| `epic418-w5-engine` | `epic-418/w5-engine-internals` | after merge |
| `epic418-w5-docs` | `epic-418/w5-docs` | after merge (PR #509) |
| `epic418-w5-gauge` | `epic-418/w5-gauge-477` | **ADDED 2026-08-09 at closeout — this list was built 2026-08-08 and #477 was dispatched after it.** PR **#517 MERGED**. The omission is the same class as the wave's own #477/#478 miss: a list derived by command still needs a total to check against, and this one had none. |

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
| `agent-a247f573f8ff07d25`, `agent-adbe19c21cc561d95` | Harness-created under `.claude/worktrees/`. Not this run's to dispose of. `a247…` holds an uncommitted `.agent-work/issue-454-force-color/`. |
| `clean` (`%TEMP%/ctx-skew-d4sqs6ee/clean`) | **Added 2026-08-09 — this list missed it entirely until the v4 probe flagged it UNCLASSIFIED.** A **locked**, detached-HEAD worktree at `29acf140` under Windows Temp, holding **3566 uncommitted and 496 branch-only** `.agent-work` paths — mostly staged *deletions*, i.e. a stripped-`.agent-work` fixture for a context-skew measurement. Not this epic's, explicitly `locked` by whoever made it, and **the lock is the owner's stated intent** — do not sweep, do not unlock, do not prune. Flagged here for one further reason: **it lives in `%TEMP%`, which Windows clears**, so its registration can rot into a broken entry through no action of ours. That is the owner's problem to know about, not ours to fix. |

**The three `.proto-*` trees are load-bearing for work that has not happened yet.** exc9 in particular
is the prototype for the very next effort. They read as stale leftovers and are not.

## Before any removal

1. `bash .agent-work/epic-418-redux/closeout/harvest_probe.sh` — collect every **UNCOMMITTED**,
   **ON THIS BRANCH ONLY**, and **IGNORED** line it reports. Presence of a tracked file proves
   nothing (the probe's v1 defect); and neither of the first two channels can see an ignored file
   (its v2 defect, found when a worktree held 379 files against main's 371 while both channels
   reported clean). The probe **reports** ignored paths and does not judge them — that is yours.
2. Confirm the PR is **MERGED on the forge** (`gh pr view`), not merged-looking by ancestry.
3. `git worktree remove <path>` then `git worktree prune`.
