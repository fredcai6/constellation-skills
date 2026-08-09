# Epic #418 — post-phase-1 hardening. Summary for acceptance.

**Closed 2026-08-09.** Main green at `c9f894f4` (1943 passed, 2 skipped, 884 subtests, real exit 0),
plus closeout commits on top.

## What shipped

22 issues dispatched across five waves. **19 closed**, each verified individually on the forge rather
than inferred from a merge.

| PR | commit | closes |
|---|---|---|
| #516 | `f9945286` | #439 #446 #468 #484 #501 #506 |
| #514 | `b2f33603` | #474 #475 #476 #427 #479 #480 #493 |
| #517 | `c9f894f4` | #477 |
| #505 #509 #511 #513 | earlier waves | — |

**Open by ruling, not by omission:** #413 (a genuinely different defect — never-valid-from-the-start),
#503 and #495 (reopened floats). **#478 carried deliberately** with its disposition posted on the issue
itself: it relocates directories the closeout tooling walks, with no forcing function to make the move
safe mid-run.

## Did the epic's thesis hold?

The through-line was **a check must be able to fail**. Several shipped gates could not:
`archive.c2b` never invoked `gh` in any PR state — its unquoted `<branch>` is shell input redirection,
so the shell tried to open a file named `branch` and exited 1 before `gh` started. Measured across four
PR-state fixtures: exit 1 every time. #484's *own suggested fix* measured exit 0 in all four states —
the mirror defect, a check that cannot fail.

The thesis then held under its own weight at the end. This Admiral tripped the HARD context band trying
to `start closeout`, was refused, and **did not override it**. On the epic whose subject is unfailable
checks, an Admiral waiving its own governor would have falsified the instrument. The gate stayed
blocked with a written handoff until a real context refresh cleared it (gauge `0.075289` against a hard
band of `150000/1000000`), then ran with **no waiver and no override**.

## The one recurring weakness, three times

Not a bad check — **a derived population with no total to check against**:

1. You named "the 474-480 group" — seven issues. The launch order named **five**. #477 and #478 were
   never assigned, never worked, and nothing downstream could see it because the order *was* the
   definition of the group. #477 was the very defect that cost this run four crew relaunches. Found by
   auditing issue states before the close; **no gate caught it**.
2. `SWEEP_LIST.md` was derived by command and covered **14 of 16** worktrees. `epic418-w5-gauge` was
   caught only at closeout — the list predated #477's dispatch.
3. The harvest probe reported ~240 branch-only files for one worktree; **241 of its 244 files were
   already on main**. It uses `git diff main...HEAD`, a merge-base test, against a squash-merged branch.
   `SWEEP_LIST.md` opens by warning about exactly this in prose, and the tool it gates does it in code.

A contiguous range carries its own count. Nothing compared the five written rows to the seven.

## Issue quality — the epic's own blind spot

#439, #484 and #446 all filed against the same postcondition, **all reached the right verdict, and all
three described a mechanism they had not measured**. Two published repros that *quoted* the
placeholder, exercising a different command than the one that shipped. Nothing in the issue format
asked how a claim was established, so inferred and measured claims were written in the same voice.

Fixed both ways: the three bodies corrected in place with originals preserved as comments, and
`skills/triage/` reshaped so an issue records **observations with baselines** — what's wrong, expected,
conditions, `type` (`measured | inferred`, and *how*), `rev` — with the suggested fix demoted to an
optional hypothesis and open questions beside it. Filed under the new template: **#528**.

## Closeout ledger

| substep | state |
|---|---|
| Episodes | **8 written**, applied via `apply_episode_delta.py` → `007`–`014`; capture gate real exit 0, 14 total |
| Lessons audit | dispatched fresh-context, with the `collect_feedback.py --mark` dogfood sweep |
| Cartographer reconcile | dispatched, carrying crew 1's `tc4` float (template → script → installed-bundle seam has no map id) |
| Harvest | probe v4 exit 0; every line re-checked by content; **real null** naming all three channels |
| Worktrees | all 7 `epic418-*` swept + pruned; protected set intact |
| Branches | 11 dispositioned by forge state; **11 baseline tags minted before any deletion** (#411 applied prospectively) |
| ADMIRAL_LOG | archived under `.agent-work/archive/2026-08-09-epic-418-redux/` |
| Retrospective | appended to `.agent-work/AGENT_FEEDBACK.md` |

## What is still open for you

- **Reinstall of the skill bundles** — deliberately held at your instruction pending the large update to
  main. The installed `constellation-triage` is stale by the six template commits.
- **Remote branch heads** — all 11 still exist on `origin`; deleting them is outward-facing and was not
  assumed. The 4 closed-unmerged branches carry **36 commits not on main**.
- **#528, #518–#526** — filed, unstarted.
- The harvest probe's merge-base test is recorded as episode `epic-418-redux-008` and is not yet filed
  as an issue.
