# Triage Recommendation: `.spine-rail-binding.json.lock is not gitignored`

## Classification
`cleanup`

## Source checklist/artifact
- Independent reviewer finding (Agent-tool dispatch, engine evidence `e-g1-review-2`, verdict APPROVE with one non-blocking observation).

## Structural anchor
`path:.gitignore`

## Cartographer mismatch class
`none`

## Desired behavior
- **Desired:** `.agent-work/.spine-rail-binding.json.lock` (the new stable sibling advisory-lock file `spine_rail._binding_transaction` opens/creates, added in #441) is gitignored, matching its sibling `.agent-work/.spine-rail-binding.json` and `.agent-work/.spine-rail-nudges.json`.
- **Today instead:** the sibling registry and nudge-ledger files were gitignored; the new lock file sat outside `.gitignore` until this recommendation fixed it, so any worktree that ran the hook would show it as an untracked file in `git status`.
- **Type:** `measured` — read `.gitignore` directly before the fix; the lock file's own contents are a single placeholder NUL byte (see `spine_rail._open_lock_file`), never worth tracking.
- **Rev:** as observed 2026-08-15, this worktree, branch `epic-568/441-binding-store`, before this run's commit.

## Recommended priority
`low`

**Reason:** Pure hygiene — the file is never read for anything but advisory locking and carries no information worth tracking, so the only cost of leaving it untracked is `git status` noise.

## Related artifacts
- `.gitignore`
- `scripts/hooks/spine_rail.py` (`_open_lock_file`, `_lock_path`)

## Disposition
`fixed-now`

**Detail:** Added `.agent-work/.spine-rail-binding.json.lock` to `.gitignore` alongside its two siblings, in this run's own commit (bounded one-line diff, adjacent to the exact change that introduced the file, trivially verifiable by inspection, no architecture/production-default impact — clears all four Fix-Now Eligibility Ladder rungs).

## Issue creation authority
`issue-ready only`
