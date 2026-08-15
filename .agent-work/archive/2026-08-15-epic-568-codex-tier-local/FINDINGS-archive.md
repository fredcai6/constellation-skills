# Findings — `archive` on `epic-568-codex-tier-local`

**Session:** `constellation/epic-568-codex-tier-local/archive/commander/attempt-2`
**Launch order:** `.agent-work/epic-568/LAUNCH_ORDER-wave2-archive-codex-attempt2.md` (frozen)
**Date:** 2026-08-14

## Door binding — the point of attempt 2

`spine_status` resolved to **`epic-568-codex-tier-local`**, not `scratch-mcp-424`. Checked before any
mutating call, two independent ways:

- The status lease line reads `constellation/epic-568-codex-tier-local`, and the active gate is
  `archive [blocked]` with the archive imperative — matching the spine on disk (9 of 10 gates
  complete).
- `SPINE_FILE` in this process points at
  `.worktrees/epic-568-codex-tier-routing/.agent-work/epic-568-codex-tier-local/spine.json`, and that
  file's `work_id` is `epic-568-codex-tier-local`.

The `cli` backend with `--spine` bound the door as the order said it would. Attempt 1's diagnosis of
the failure was exact, and the fix it asked for worked.

## Postcondition verification

Every condition was measured at source in this session, not inherited.

| Cond | Statement | Measured | Result |
|---|---|---|---|
| `p1` | workflow feedback recorded | already satisfied in spine | met |
| `c1` | episode captured AND tracked by git | `verify_episode_captured.py epic-568-codex-tier-local --store-root episodes --phase archive` → exit 0, 3 episodes (`-001`, `-002`, `-003`), 144 scanned | **pass** |
| `c2` | branch committed and pushed | `HEAD == origin/epic-568-codex-tier-routing == a34cf500`; nothing unpushed | **attested** |
| `c2b` | PR OPEN or MERGED | check command run verbatim → exit 0; PR #579 `state: MERGED` | **pass** |
| `c3` | engine session lease released | attested as commitment, released immediately after the closing advance | **met in order** |
| `c4` | staged diff carries no suspicious artifacts | staged diff empty; only untracked paths are work-area dirs under `.agent-work/**`, an allow_glob | **pass** |

## The blocker dissolved rather than being overridden

The gate was `blocked` on publication authority: archive wants a pushed branch and an OPEN or MERGED
PR, and the previous frozen order forbade push, PR, and merge. That tension is gone because the
publication already happened before this session started:

```
PR #579   state: MERGED   mergedAt: 2026-08-14T23:32:12Z   mergeCommit: e0c998b6
git merge-base --is-ancestor e0c998b6 origin/main  →  YES
```

So `resume` was honest: nothing was forced, nothing waived. `c4` never needed its human waiver — the
staged diff was empty, so the git-change-policy check had nothing to object to.

**Cite `e0c998b6` for this work, not `a34cf500`.** The merge was a squash, so `a34cf500` is not itself
an ancestor of `main`.

## What I did not do

No push, no PR creation, no PR modification, no merge — pre-ruling `decision:publication-is-done`. No
edit to `.mcp.json`, `scripts/checklist_engine.py`, or `scripts/hooks/spine_rail.py`. No engine CLI
fallback: the door was genuinely bound, so MCP was available and a fallback would have hidden a real
signal. No hand-edit of spine state. `a34cf500` was reconciled and left alone, not reverted or
re-attributed.

## Floated to the Admiral

**1. The archived work area is committed locally but cannot be pushed.** `spine_close` moved this
directory to `.agent-work/archive/2026-08-15-epic-568-codex-tier-local/` (the engine stamps the UTC
date, one day ahead of the local date on this record) and committed it as `1a314a70`, which is the
repo convention (8345 tracked files already live under `.agent-work/archive/`). That commit sits on
top of `a34cf500` and stays local, because `decision:publication-is-done` forbids pushing and the
branch is already squash-merged. **The Admiral must decide whether this archive commit reaches
`main`**; pushing it to an already-merged branch would reopen divergence, so a cherry-pick onto a
fresh branch off `main` is the cleaner route if the record is wanted in history. The durable evidence
does not depend on this: the three episodes under `episodes/` are already tracked and already merged.

**2. A second work area exists at the repo root and I left it alone.**
`/home/tommy/projects/constellation-skills/.agent-work/epic-568-codex-tier-local/` (holding
`crew-runs.json` and `crew-runs/`, written at 17:45 today) belongs to the live dispatch launcher in
the main checkout, not to this worktree. My Workspace is the worktree alone, so moving it could have
broken a running launcher. It needs a sweep by whoever owns that checkout.

**3. Attempt 1's record is preserved.** Its verdict is at `ARCHIVE_RESULT-attempt-1.md`, verbatim.
`ARCHIVE_RESULT.md` now carries attempt 2's outcome so the current truth is what a reader finds first.
