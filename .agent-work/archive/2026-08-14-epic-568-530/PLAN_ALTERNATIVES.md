# Plan alternatives — #530

## Candidate A — recommended: one resolved-spine ownership helper

Derive a normalized worktree root from the already validated `abs_spine` path,
then use it in both the claim writer and SessionStart's fallback binding writer.
Prove the behavior with one real linked-worktree topology that runs production
claim, Stop, release, and SessionStart paths.

## Candidate B — untaken road: inline derivation at each writer

This duplicates path-shape logic in two writers and risks claim/SessionStart
drift. It is rejected in favor of Candidate A.

## Parallel comparison

Two independent candidates ran before plan approval:

- `plan-alternatives/smallest-diff.md` chose the one-helper/two-writer seam.
- `plan-alternatives/most-testable.md` independently chose the same seam and
  required a real main-plus-linked-worktree production-handler regression.

Both converge on Candidate A. A cold critic ran in `plan-critic.md` and BLOCKed
the first draft until the plan explicitly refused malformed paths without cwd
fallback and included production SessionStart bind-on-resume proof. Those
repairs are incorporated below; no #441 expansion is admitted.

## Panel-vs-single record

This is a two-candidate plan panel, appropriate for a bounded hook correction.
The Admiral’s frozen launch order remains the delegated approval authority.
