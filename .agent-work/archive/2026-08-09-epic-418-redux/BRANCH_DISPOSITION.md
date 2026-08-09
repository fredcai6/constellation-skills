# Branch disposition — epic-418-redux closeout, 2026-08-09

Every branch is dispositioned by **forge state**, never by ancestry. `gh pr list --head <branch>
--state all` was run for all eleven; a squash-merge returns the same ancestry answer for merged and
abandoned, so ancestry was not used to decide anything.

## Baselines preserved first

Eleven annotated tags `epic-418-baseline/<leaf>` were minted **before** any deletion, one per branch
tip. This is issue **#411**'s lesson applied prospectively rather than repaid: #411 found its baseline
commits already GC-eligible after a squash-merge deleted the branch, and had to mint tags to recover
them. Squash-merge leaves the branch's own commits unreachable from `main`, so deleting the branch is
what makes them collectable. Every observation in this epic that pins a rev on one of these branches
stays resolvable.

```
git tag -l 'epic-418-baseline/*'      # 11
```

## Merged — local branch deleted, remote left alone

| branch | PR | state | tip | tag |
|---|---|---|---|---|
| `epic-418/a2-467-trip-semantics` | #505 | MERGED | `bcb817b6` | `epic-418-baseline/a2-467` |
| `epic-418/w5-bookend-gates` | #516 | MERGED | `53f02ddd` | `epic-418-baseline/w5-gates` |
| `epic-418/w5-crew-addressing` | #511 | MERGED | `8f5c34a8` | `epic-418-baseline/w5-addressing` |
| `epic-418/w5-docs` | #509 | MERGED | `8f3a6f54` | `epic-418-baseline/w5-docs` |
| `epic-418/w5-engine-internals` | #514 | MERGED | `89ecbc65` | `epic-418-baseline/w5-engine` |
| `epic-418/w5-gauge-477` | #517 | MERGED | `62145a00` | `epic-418-baseline/w5-gauge` |
| `epic-418/w5-readiness-458` | #513 | MERGED | `010de2a8` | `epic-418-baseline/w5-readiness` |

**Remote heads were not deleted.** All seven still exist on `origin`. Deleting a remote branch is
outward-facing and was not asked for; the local deletion is the hygiene the postcondition wants, and
the tags make it reversible. Left for the repo owner.

## Closed unmerged — KEPT, local and remote

These four carry real work that is **not** on `main`. They are dispositioned as retained, not swept.

| branch | PR | state | commits not on main | tag |
|---|---|---|---|---|
| `epic-418/b-433-render-directives` | #483 | CLOSED | 9 | `epic-418-baseline/b-433` |
| `epic-418/b-460-episodes-observations` | #486 | CLOSED | 18 | `epic-418-baseline/b-460` |
| `epic-418/b-464-lesson-field-rename` | #471 | CLOSED | 5 | `epic-418-baseline/b-464` |
| `epic-418/d-436-enumeration-falsification` | #469 | CLOSED | 4 | `epic-418-baseline/d-436` |

Wave 1 ("B extended") branches whose PRs were closed rather than merged; the underlying issues were
re-approached in later waves. **36 commits of unmerged work total.** Deleting them is a judgement
about whether that work is worth keeping, which is the repo owner's call and not a hygiene step — so
closeout records them and leaves them in place.
