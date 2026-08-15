# Archive result — `epic-568-530`

Dispatch: `.agent-work/epic-568/LAUNCH_ORDER-wave2-archive-530.md` (frozen) · session
`constellation/epic-568-530/archive/commander/attempt-1` · worktree
`.worktrees/epic-568-530`, branch `epic-568/530-binding`.

## Door verification (stop condition, checked first)

`spine_status` resolved to **`epic-568-530`** — lease `constellation/epic-568-530`, digest naming
episode `epic-568-530-001`. Not `scratch-mcp-424`, not any interactive-demo spine. The `cli` backend
with `--spine` bound `SPINE_FILE` correctly, which is what the predecessor could not get
(`FINDINGS-wave2-repair.md` F1). Proceeding was authorized only by that result.

Lease taken over per pre-ruling 3: forced claim with reason, recorded as
`constellation/epic-568-530 -> constellation/epic-568-530/archive/commander`. Takeover, not
recreation; no new spine.

## Publication reconciled at source (pre-rulings 1 and 2)

Everything below was verified in this worktree, not accepted from the order:

| Claim | Verification | Result |
|---|---|---|
| Branch pushed | `git ls-remote --heads origin epic-568/530-binding` | `4ceace75` |
| Local head matches published head | `git rev-list --left-right --count HEAD...origin/…` | `0 0` |
| PR reachable | `gh pr list --head epic-568/530-binding --state all` | #580, `MERGED` |
| Merge landed | `git log --oneline -1 c23c3d0f` | squash merge of #580 |
| Guard genuinely on `main` | `git cat-file -e origin/main:tests/test_spine_rail.py` | present |
| Episode genuinely on `main` | `git cat-file -e origin/main:episodes/active/epic-568-530-001.md` | present |

The Admiral's rebase onto `e0c998b6` and the regenerated `map/INDEX.md` are reconciled as legitimate
integration acts and left alone (pre-ruling 2). The squash means branch commits are not ancestors of
`main`; `c23c3d0f` is the citation. Nothing was pushed, opened, modified, or merged by this session.

## Archive postconditions

- **`c1` — work area archived, episode captured AND tracked by git.** Command check
  `python scripts/verify_episode_captured.py epic-568-530 --store-root episodes --phase archive`
  exits 0: *"1 episode(s) recorded for run 'epic-568-530' in episodes/active (145 scanned, phase
  archive)"* → `epic-568-530-001`. Run cache-clean per pre-ruling 5. The `archive` phase is the one
  that additionally demands git tracking, and the episode is not only tracked but merged to
  `origin/main`, so the record already outlives this worktree.
- **`c2` — branch committed and pushed.** Attested: head `4ceace75` is identical to
  `origin/epic-568/530-binding`, with no unpushed or uncommitted work in the branch.
- **`c2b` — work is REACHABLE.** Command check satisfied by PR #580 in state `MERGED`.
- **`c3` — engine session lease released.** Attested as the closing act, then performed: the engine's
  final `advance` on `archive` runs first, and `release` is the last journal entry (pre-ruling 4,
  and the rail's own sequencing).
- **`c4` — staged diff carries no suspicious artifacts.** Nothing is staged; the branch is exactly
  the published, merged head. No waiver requested and none needed.

## Work-area archival

`.agent-work/epic-568-530/` was moved to `.agent-work/archive/2026-08-14-epic-568-530/` **after** the
release (done; old path gone, branch still `0 0` against origin), because `SPINE_FILE` is an absolute path into that directory and moving it while the spine
is live breaks the MCP door mid-gate. `c1` does not depend on the work-area path, and a filesystem
move is not a journaled action, so this ordering satisfies both the archive imperative and
release-is-last. See `FINDINGS-archive.md` F3.

## Floated (not worked around)

**This run's work-area records cannot reach history from this lane.** `.agent-work/` is tracked in
this repo by policy, but this work area was never tracked, and the squash merge plus pre-ruling 1
leave no path for me to publish it. The archived directory stays local to this worktree. The durable
record — episode `epic-568-530-001` — is on `main` regardless. If the work-area records are wanted in
history, that is an act for whoever holds publication authority. Full statement in
`FINDINGS-archive.md` F2.

## Status

Lane complete. Implementation merged, archive closed through the engine, nothing forced, no spine
state hand-edited, no shared config touched.
