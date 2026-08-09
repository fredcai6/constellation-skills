# Triage Recommendation: `<title>`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

## Classification
`bug | cleanup | missing test | missing doc | missing architecture packet | missing structural node | missing capability anchor | architecture weakness | structure/constraint mismatch | stale generated map | ungrounded claim/decision | bad map edge | feature | tooling | unresolved decision | research hardening | dependency cleanup | security/privacy | performance/resource`

## Source checklist/artifact
- `<cartographer finding | review finding | plan | user note | evidence path>`

## Structural anchor
`struct:<id> | path | none`

## Cartographer mismatch class
`<Cartographer mismatch class or none>`

## Observations
> **For defects.** Record what you saw, not what should be built. One block per occurrence — repeat the block; do not merge two occurrences into one summary. Delete this section for a pure enhancement and fill *Desired behavior* instead.

### Observation 1
- **What's wrong:** `<the undesirable behavior specific to THIS observation>`
- **Expected:** `<what the behavior should have been — the other half of the discrepancy>`
- **Conditions:** `<feeding conditions that enable the bad state, including which environment>`
- **Type:** `measured | inferred` — `<how>`
- **Rev:** `<what state this was true of>`

### Observation 2
- **What's wrong:** `<...>`
- **Expected:** `<...>`
- **Conditions:** `<...>`
- **Type:** `measured | inferred` — `<how>`
- **Rev:** `<...>`

**Field notes**

- **Type — the "how" is mandatory for both values.** `measured` carries the command or harness that produced the result. `inferred` carries what it was read off ("read off the check text, not executed"). A bare `inferred` with no source is the exact failure this field exists to catch.
- **Conditions — which environment is part of locating the observation, not optional colour.** Wave 5 of epic #418 produced three test failures that were green in a local worktree and red only on the CI runner, on the same tree, with a different pass/skip split.
- **Rev — finding a defect before committing is the normal case, not an exception.** Legitimate values: a commit; a commit plus uncommitted worktree state; or a hash of an installed artifact, since some observations are made against an installed skill bundle that no repo commit locates. If the baseline lives on a branch that will be squash-merged, pin it: issue #411 found its baseline commits already GC-eligible after a squash-merge deleted the branch, and had to mint annotated tags to recover them.

**Worked example** — the `archive.c2b` defect (issues #439 / #484 / #446, fixed in PR #516):

- **What's wrong:** the reachability gate never invoked `gh` in any PR state. Its check text was `gh pr list --head <branch> --state open --json number --jq 'length > 0'`; the engine runs check text through `sh -c`, where the unquoted `<` is input redirection, so the shell tried to open a file named `branch` and exited 1.
- **Expected:** exit 0 when the branch has an OPEN or MERGED pull request, nonzero otherwise.
- **Conditions:** any PR state; the gate is unconditional. Reproduced locally against four fixtures — no PR, OPEN, MERGED, CLOSED-unmerged.
- **Type:** `measured` — ran the check text under `sh -c` against all four fixtures: exit 1 every time.
- **Rev:** as observed, the uncommitted crew worktree at branch commit `84d1e998` — which is *not* reachable from `main` today, because PR #516 squash-merged and its branch was deleted. Retroactively this is `f9945286^`, the fix's parent. Write the rev you actually observed at; add the retroactive pin later if one becomes available.

Contrast this with issue #446, which claimed the same gate "accepts only an OPEN PR". Nobody ran it — that was read off the check text by eye, and it was wrong: the gate accepted nothing. An `inferred` claim written as if measured is what sends the next run at the wrong target.

## Desired behavior
> **For enhancements.** Delete this section for a pure defect.

- **Desired:** `<the behavior you want that does not exist today>`
- **Today instead:** `<what actually happens now — an enhancement with no current-behavior statement cannot be distinguished from something that already works>`
- **Type:** `measured | inferred` — `<how the "today instead" claim was established>`
- **Rev:** `<what state the "today instead" claim was true of>`

## Possible fix
> **Optional, and a hypothesis — never a spec.** A top-level sibling of *Observations*: one per issue, not one per observation. Delete the section if you do not have one.

`<hypothesis, and what would have to be true for it to work>`

A suggested fix is evidence that *a* fix is feasible; it is not the fix. Issue #484 — the issue that coined "a check that cannot pass" for this repo — carried a suggested fix that itself measured exit 0 in all four PR states. Following it would have converted a check that cannot pass into a check that cannot fail.

## Open questions

> **Optional, and a place to get thoughts out — not a commitment and not a work item.** A top-level sibling of *Possible fix*. Record what is unresolved or in dispute, and what would settle it. Delete the section if you have none.

- `<the question, and what evidence or ruling would settle it>`

*Observations* is the load-bearing half of this template: recorded with a baseline, it is what survives to inform a future reader. *Possible fix* and *Open questions* are thinking out loud for whoever picks this up, and a later reader should feel free to discard them.

## Impact
`<Why this matters. What future work or correctness does it affect?>`

## Suggested scope
`<The boundary of the work — what it may touch, not the method for fixing it. The method, if you have one, is a hypothesis and belongs in Possible fix.>`

## Non-goals
`<What this issue should not include.>`

## Acceptance criteria
- [ ] `<criterion>`
- [ ] `<criterion>`

## Recommended priority
`low | medium | high | urgent`

**Reason:** `<why>`

## Related artifacts
- `<architecture packet / handoff / evidence / file path>`

## Disposition
`fixed-now | filed | recommend-and-defer`

**Detail:** `<fixed-now: fix commit sha | filed: issue number | recommend-and-defer: reason filing authority was unclear or unavailable this run>`

## Issue creation authority
`create issue directly | ask user | issue-ready only`
