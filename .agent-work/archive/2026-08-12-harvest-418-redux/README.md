# Harvest — epic-418 predecessor run (waves 0–1), collected 2026-08-08

These are **records, not doctrine**. Nothing here is read back as a rule.

Collected by the Admiral of `epic-418-redux` during wave 3, ahead of closeout, from the stale
worktrees of the archived predecessor run. The harvest-before-sweep rule exists because
`git worktree remove` destroys anything a run left uncommitted, and under an epic lease
`durable_root()` deliberately returns the **worktree** root rather than the main checkout — so a
crew's durable output lands where the sweep will eat it.

## What was actually at risk

Every file here was verified **absent from the git object store** before copying, by hashing it and
asking git whether it knew the blob:

```
h=$(git hash-object <file>); git cat-file -e "$h"   # non-zero => content exists nowhere in git
```

That check is the reason this directory exists. A survey by filename alone would have found five
candidates and been wrong about one of them: `epic418-h-447/.agent-work/LESSONS.md` **is** already in
git and was deliberately not copied.

| Source worktree | File | Size | Why it survived nowhere else |
|---|---|---|---|
| `epic418-b-420` | `RETURN.md` | 10 KB | crew return artifact, never committed |
| `epic418-d-422` | `RETURN.md` | 10 KB | crew return artifact, never committed |
| `epic418-g-425` | `RETURN.md` | 7.5 KB | crew return artifact, never committed |
| `epic418-h-447` | `AGENT_FEEDBACK.md` | 261 KB | run retrospective, written worktree-locally under the epic lease |

## The irony worth recording

`h-447` is the workstream that **retired** `AGENT_FEEDBACK.md` and `LESSONS.md` in favour of
`episodes/`. Its own run wrote a 261 KB retrospective into the very file it was removing, worktree-local
and untracked, where the sweep would have taken it. The retirement landed; its own record nearly didn't.

## Disposition — not settled here

These are pre-retirement formats. Under `docs/agents/ORCHESTRATOR_CONTEXT.md`, `episodes/` replaces
both and its only write path is `apply_episode_delta.py`. So the disposition of this content —
convert to episodes, or drop with a reason — belongs to the **lessons audit at closeout**, not to the
act of collecting it. Collecting is reversible; deciding is not, and the sweep was the only clock.

`governor-264` was **not** harvested and must **not** be swept: it holds 3 commits of unmerged code
against the one still-open issue of the eight. See the epic's `STATE_NOTE.md`.
