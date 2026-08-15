# Launch Order: `epic-568-codex-tier-local — archive resume`

**Issued:** 2026-08-14 by `admiral-epic-568` · **Boundary:** `wave-2-gate-refusal` · **Launch:** `epic-568-wave-2-repair`
**Frozen.** Read it as written. Where it is wrong, say so and float rather than quietly working around it.

## Mission

Your lane is finished and published. Its only remaining step is `archive`, which you correctly
refused to advance because its `c2`/`c2b` postconditions require a pushed branch and an OPEN or
MERGED pull request, and your launch order fenced you from creating either. The Admiral has now
cleared that. Complete `archive` and release your lease last.

## Prior-Wave Verdicts (pasted)

Your blocker, verbatim from your own spine:

```
The frozen launch order expressly forbids push, PR, and merge, while archive requires a pushed
branch and an OPEN or MERGED PR before terminal advance. Commit 247ffa1f and all required capture
evidence are local and verified; publication authority is the only remaining blocker.
```

That refusal was correct. Publication is the Admiral's delegated `merge-to-main` class, not yours
and not a human escalation. It has been exercised:

- Branch `epic-568-codex-tier-routing` is pushed and tracked on `origin`.
- **PR #579 is OPEN**, base `main`, head `a34cf500`, verified at source via `gh pr view 579`.
- One commit was added on top of your `247ffa1f` by the Admiral: `a34cf500`, a mechanical
  `map/INDEX.md` regeneration (4543 → 4544 entities). Your `run_crew.py` change had added one entity
  and left the generated map stale, which was the lane's only remaining test failure.
- Gate measured at that exact head, cache-clean: **2986 passed, 7 skipped, 1130 subtests, 0 failed**,
  against a freshly re-measured `main` baseline of 2980 passed / 0 failed at `0448275e`.

## Pre-Rulings

1. **`decision:publication-is-done` — settled.** Do not push, open, or modify any PR. It exists.
   Verify it at source if your postcondition needs to, then proceed.
2. **`decision:admiral-map-commit-stands` — settled.** `a34cf500` is a legitimate part of your
   branch. Reconcile it into your record as an Admiral-authored mechanical commit; do not revert,
   rewrite, or re-attribute it.
3. **`decision:clear-caches-before-measuring` — settled.** If you re-measure anything, clear
   `__pycache__` first. A stale `.pyc` carrying the pre-relocation path `constellation-skills-wt/`
   fabricated a phantom failure in this very worktree earlier in the wave; it was attributed by
   falsification and is not a defect in your change.
4. **`decision:release-is-last` — settled.** Terminal advance does not auto-release. Complete the
   archive, then explicitly release your lease as the final act.

## Honest-Null Clause

If `archive` still refuses after publication for a reason this order has not anticipated, that is a
real finding. Report it plainly and stop; do not force the gate or hand-edit spine state to satisfy
a postcondition.

## Inherited Latitude

None beyond completing `archive`. The implementation is closed, reviewed, APPROVEd twice, and
published. This is a closeout, not an opportunity to revise the change.

## File Ownership

Yours: your own work-area records under `.agent-work/epic-568-codex-tier-local/` and your episode
files. Do not touch `scripts/checklist_engine.py` or `scripts/hooks/spine_rail.py` — two other
Commanders hold those serialized lanes concurrently.

## Workspace

Worktree `.worktrees/epic-568-codex-tier-routing`, branch `epic-568-codex-tier-routing`, spine
`.agent-work/epic-568-codex-tier-local/spine.json`. It is yours alone. Spine interaction is MCP-only.
Your lease is live but held by your predecessor's dead session: take it over, do not recreate it.

## Pre-empted Steps

Every step through `feedback` is complete. Do not re-run them. Start at `archive`.

## Data Locations

Findings file: `.agent-work/epic-568-codex-tier-local/FINDINGS-archive.md`.

## Budget

One closeout. If it grows beyond archiving, stop and float.

## Stop Conditions

- `archive` refuses for any reason other than the now-cleared publication postconditions.
- Completing it would require hand-editing spine state or bypassing the engine.
- You find the published head does not match what you expect.

## Return Shape

Report: whether `archive` completed, whether the lease is released, what the archive verification
showed, and anything floated. Note explicitly that PR #579 remains OPEN and unmerged — the merge
decision is the Admiral's separate act, gated on the PR's own CI run, and is not yours.
