# Archive result — `epic-568-codex-tier-local`

**Session:** `constellation/epic-568-codex-tier-local/archive/commander/attempt-2`
**Launch order:** `.agent-work/epic-568/LAUNCH_ORDER-wave2-archive-codex-attempt2.md` (frozen, 2026-08-15)
**Date:** 2026-08-14
**Supersedes** attempt 1's refusal, preserved verbatim at `ARCHIVE_RESULT-attempt-1.md`.

## Verdict

**`archive` COMPLETE. The spine is terminal. The lease is released.** Nothing was forced, waived, or
hand-edited.

## What `spine_status` resolved to

**`epic-568-codex-tier-local`.** This is the whole point of attempt 2, so it was checked before any
mutating call and confirmed two ways: the status lease line reads
`constellation/epic-568-codex-tier-local` with `archive [blocked]` active, and `SPINE_FILE` resolves
to this worktree's `spine.json`, whose `work_id` is `epic-568-codex-tier-local`. **Not
`scratch-mcp-424`.** The `cli` backend with `--spine` bound the door as the order predicted. No stop
condition fired.

## The sequence, in order

1. `spine_lease claim force=true` — takeover of the dead predecessor lease (last heartbeat
   `17:39:45Z`), stamping `previous_session_id` and `takeover_reason`. A takeover of the same spine,
   not a recreation.
2. `spine_halt resume archive` — the publication blocker had dissolved on its own (below).
3. `spine_evidence attest c2`, `attest c3` — the two `null`-check conditions.
4. `spine_advance archive` → **`archive -> complete`**.
5. `spine_lease release` — the final journaled action, after the closing advance, never before it.
6. `spine_close` — the mechanical move of the work area into
   `.agent-work/archive/2026-08-15-epic-568-codex-tier-local/` (the engine stamps the UTC date, one
   day ahead of the local date on this record), run last because moving `spine.json` any earlier would
   have broken the bound door for the calls above. It committed as `1a314a70`: 38 files, every one of
   them inside that archive directory, nothing swept in from elsewhere.

## Archive verification

Measured at source this session, not inherited from attempt 1.

| Cond | Measured | Result |
|---|---|---|
| `c1` | `verify_episode_captured.py ... --phase archive` → exit 0; 3 tracked episodes `-001/-002/-003` | **pass** |
| `c2` | `HEAD == origin/epic-568-codex-tier-routing == a34cf500`, nothing unpushed | **attested** |
| `c2b` | check command run verbatim → exit 0; PR #579 `MERGED` | **pass** |
| `c3` | released immediately after the closing advance | **met in order** |
| `c4` | staged diff empty; untracked paths are work-area dirs under `.agent-work/**`, an allow_glob | **pass** |

`c4` never needed its human waiver. The staged diff was empty, so the git-change-policy check had
nothing to object to.

## Why the gate stopped refusing

It was `blocked` on publication authority — archive wants a pushed branch and an OPEN or MERGED PR,
while the previous order forbade push, PR, and merge. The tension is gone because publication had
already happened before this session began:

```
PR #579   state: MERGED   mergedAt: 2026-08-14T23:32:12Z   mergeCommit: e0c998b6
git merge-base --is-ancestor e0c998b6 origin/main  →  YES
```

**PR #579 is merged. It is not open.** Because the merge was a squash, `a34cf500` is not itself an
ancestor of `main` — **cite `e0c998b6` for this work.**

## What I did not do

No push, no PR creation, no PR modification, no merge (`decision:publication-is-done`). No edit to
`.mcp.json`, `scripts/checklist_engine.py`, or `scripts/hooks/spine_rail.py`. No engine CLI fallback —
the door was genuinely bound, so MCP was available and a fallback would have hidden a real signal. No
hand-edit of spine state. `a34cf500` reconciled and left alone, not reverted or re-attributed.

## Floated to the Admiral

Full detail in `FINDINGS-archive.md`. In short:

1. **The archive commit is local and unpushable.** `spine_close` committed the moved work area as
   `1a314a70` on top of `a34cf500`, but `decision:publication-is-done` forbids pushing and the branch
   is already squash-merged. The Admiral decides whether that record reaches `main`; a cherry-pick onto a fresh
   branch off `main` is cleaner than pushing an already-merged branch. Durable evidence does not
   depend on it — the three episodes under `episodes/` are tracked and already merged.
2. **A second work area at the repo root was deliberately left alone.**
   `constellation-skills/.agent-work/epic-568-codex-tier-local/` belongs to the live dispatch launcher
   in the main checkout, not this worktree. It needs a sweep by that checkout's owner.
3. **Attempt 1 earned this run.** Its refusal was correct and its diagnosis exact; the environment fix
   it asked for is the only reason attempt 2 could proceed.
