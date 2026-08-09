# Harvest before sweep — epic-418-redux closeout, 2026-08-09

Ran `bash .agent-work/epic-418-redux/closeout/harvest_probe.sh` (v4, exit 0) across all sixteen
registered worktrees, then re-checked its findings by content before removing anything.

## Verdict: the durable trio was already on main. This is a real null.

All three channels were queried for each of the seven sweep-eligible worktrees — uncommitted,
branch-only, and ignored — and after content verification, **nothing needed harvesting**. Stated as a
null with its channels, not as "nothing found".

| worktree | uncommitted | branch-only (probe) | branch-only (measured) | ignored |
|---|---|---|---|---|
| `epic418-a2-467` | none | none | none | 9 — `gauge.json`, `__pycache__` |
| `epic418-w5-addressing` | none | none | none | 1 — `gauge.json` |
| `epic418-w5-docs` | **3 files** | none | none | 1 — `gauge.json` |
| `epic418-w5-engine` | none | 1 file | **0 — already on main** | 2 |
| `epic418-w5-gates` | 4 files | **~240 files** | **3 — all transients** | 2 |
| `epic418-w5-gauge` | none | none | none | none |
| `epic418-w5-readiness` | none | none | none | 1 — `gauge.json` |

### What was actually preserved

`w5-docs-uncommitted/` — the three uncommitted engine-state files from
`epic418-w5-docs/.agent-work/impl-w5-docs-496-411/`. Real content changes (`plan.json` +30/-8,
`plan.json.journal` +4/-0, `mechanical/m3-artifact-and-pr.json` +3/-3, confirmed under
`--ignore-cr-at-eol`): the implementer's engine state advanced past its last commit. Run bookkeeping
rather than learning, but removal would have destroyed it and copying cost nothing.

Everything else was verified present on main by content comparison, not by ancestry.

## Two probe channels disagreed with the filesystem. Both were checked, not trusted.

**`epic418-w5-gates` — the probe reported ~240 branch-only files; 241 of 244 are on main.**
Measured by `find | sort` + `comm -23` between the worktree and the main checkout. The only three
absent are `g2-review/repro/__pycache__/*.pyc` (2) and `gauge.json` — the disposable transients the
sweep list already judged.

Mechanism: `harvest_probe.sh:80` computes the channel as
`git diff --name-only main...HEAD -- .agent-work/`. The **three-dot** form diffs against the
merge-base. PR #516 was **squash-merged**, so main's copy of those files arrived in a commit that is
not an ancestor of the branch, the merge-base stays at the old fork point, and every file the branch
ever added still reads as branch-only.

This is the same defect the sweep list warns about in prose at its own head — *"Never use an ancestry
test to decide whether anything merged. Squash-merge returns the same answer for merged and
abandoned"* — committed in code by the tool that list gates. It fails **safe** (over-reporting means
you decline to sweep), which is the opposite polarity from this epic's usual finding, but it buried
the one file that looked like real signal under 240 lines of noise.

**`epic418-w5-engine/.agent-work/w5c4-engine/IMPLEMENTER_RESULT.md` — reported branch-only, identical
on main.** `diff` reported the files differ; `diff --strip-trailing-cr` returned zero lines. CRLF, not
content. Same trap as the ` M` phantom in `git status`.

## Sweep order followed

1. Harvest (this file).
2. Forge state verified for all seven branches with `gh pr list --head <branch> --state all`, never by
   ancestry: #505, #509, #511, #513, #514, #516, #517 — **all MERGED**.
3. `git worktree remove` then `git worktree prune`.

`epic418-w5-gauge` was **added to `SWEEP_LIST.md` at closeout** — the list was built 2026-08-08 and
#477 was dispatched after it. Same omission class as the wave's own #477/#478 miss: a list derived by
command still needs a total to check against, and this one had none.
