# Crash-resume state note — epic-418-redux

**WAVE 2 IS COMPLETE AND MERGED. Nothing is in flight. The latitude contract has EXPIRED by its
own terms and the `execute` gate is BLOCKED awaiting Tommy's refresh. Do not dispatch anything.**

- **step:** `execute` — **blocked** on contract expiry. Remaining after `execute`: `closeout` only.
- **slug:** `epic-418-redux` · main checkout `C:/Programs/constellation-skills` · `main` at
  **`0cb9ca2a`** (= `origin/main`, pushed, working tree clean)
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
  — then get the contract refreshed before anything else
- **pid:** none — no agents in flight
- **expected artifact:** a refreshed latitude contract, then a `w2-to-w3` replan packet

**Green main: `476e044d` → 1782 passed, 2 skipped, 683 subtests, exit 0** (real exit code captured).

## Wave 2 — all four issues merged

| Issue | PR | What landed |
|---|---|---|
| #433 | #485 | `directives` renders; naive fix would have been a check that cannot fail (2955 gates scanned, 8 populated) |
| #436 | #472 | enumeration check observed REFUSING a new entry; count added to its failure output |
| #460 | #487 | episode records restated as observations; guard caught 4 real offenders on first live run |
| #464 | #473 | `Lesson` → `Episode`, with the legacy fallback and hash prefix deliberately preserved |
| — | #470 | the Admiral's own fixture-path breakage |

## NOT done — carried

- **#461** (negative control fails between `git add` and `git commit`) — **reproduced first-hand
  during #460's merge and evidenced on the issue**; deliberately not fixed, held to wave 3.
- **#465** (reviewer r6-fowler placeholder + CRLF) — held to wave 3, touches `checklist_engine.py`.
- **#433, #436, #460, #464 are MERGED BUT NOT CLOSED** on the tracker — issue closing is a
  `surfaced` class and Tommy has not been asked.
- ~~Worktrees pending sweep~~ — **DONE**: all four harvested (nothing to harvest; their exports were
  behind main, not ahead) and swept. `r418-460`'s orphaned lease released first.
- **`governor-264` still holds a live lease with a 2026-07-28 heartbeat** — an unrelated issue's
  abandoned Commander. Left alone, but it is a standing #457 rail-capture hazard for whoever runs next.

## Landed so far

| PR | Issue | State |
|---|---|---|
| #470 | Admiral's own fixture-path breakage | **MERGED** `e8c735af` |
| #472 | #436 enumeration falsification | **MERGED** `7bc3f8c2` |
| #469 | #436, original | closed — superseded by #472 (squash-orphan, not rework) |
| #473 | #464 rename (replant of #471) | **MERGED** `0b4a11a7` |
| #485 | #433 render directives (replant of #483) | **MERGED** `538d5fd7` |
| #483 | #433, original | closed — superseded by #485 |
| #471 / #483 / #486 | originals | closed — all superseded by replants (squash-orphan, not rework) |
| — | #433, #460 | agents still working in their worktrees |

## THE REPLANT RECIPE — read this before touching any wave-2 PR

**Every wave-2 branch is based on `73b4517`, which is NOT an ancestor of main.** Squash-merging
#470 collapsed `8de91de`+`73b4517`+`fb7edfd` into one commit, orphaning that base. So
`gh pr update-branch` reports CONFLICTING on all of them. **The work is fine; only its base moved.**
Do not ask the agent to redo anything.

```bash
# 1. fresh branch off current main
git checkout -b epic-418/<slug>-replant origin/main
# 2. take ONLY that branch's own delta, against its real base
git diff 73b4517 origin/<their-branch> -- <their changed paths> > /tmp/x.patch
git apply --3way /tmp/x.patch
# 3. verify, commit, push, PR, then close the original as superseded
```
Get the changed-path list with `git diff --name-only 73b4517 origin/<their-branch>`.
Worked cleanly four times: #436→#472, #464→#473, #433→#485, #460→#487.

**Never use an ancestry test to decide whether a wave-2 branch merged** — under squash-merge it
returns the same answer for merged and abandoned. Ask the forge (`gh pr view <n> --json state`).

## Settled — do NOT re-derive

- **Green baseline is now `476e044d`: 1782 passed, 2 skipped.** Expect **1726 passed, 2 skipped** (1723/2 after #470's fix,
  plus #436's 3 new tests). The earlier "1721 passed, 4 skipped" was **my own breakage**, not
  environment-conditional: archiving the run moved `REVISED_SPEC.md` out from under a hardcoded
  fixture path. Fixed in #470 (fixture now found by glob).
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py` for pytest** (#454).
- **The installed corpus was stale and is now SYNCED.** Remaining diffs are the installer's own
  `python`→`py` rewrite and path resolution — verified benign, zero non-launcher differences.
- **#468 (filed):** the repo's vendored `verify_iterative_role_artifacts.py` cannot run from this
  repo — its installed-skill guard passes by accident because the repo is named
  `constellation-skills`. **Use the installed copy** under
  `C:/Users/fredc/.claude/skills/constellation-admiral/scripts/`.
- **`verify_worktree_isolation.py` has two modes.** Bare paths = Admiral pre-wave gate;
  `--here <path>` = the Commander's check and it tests **cwd**.
- **`git cat-file -e origin/main:<path>` is broken in Git Bash here** — it path-converts to
  `origin\main;<path>` and reports MISSING for files that exist. Compare trees with
  `git diff --name-only` instead. This nearly made me believe a merge had eaten the work area.
- **The governor HARD-trips agents at ~17–21% context fill.** All three wave-2 agents tripped at the
  plan seam and were relaunched fresh from `current` alone. Budget **two dispatches per issue**.
  Open question for Tommy: whether that band is where we want it. Not retuned mid-wave.
- **#447 CLOSED** with a per-done-condition accounting; condition 4 recorded **partial**, not done.
  **#418's body pointer corrected** to `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`.
- **#457 — never obey a spine rail naming a spine another agent drives.**

## Still held to the wave's second half, deliberately

- **#461** (episode-store negative control) — sits in #460's area
- **#465** (reviewer r6-fowler placeholder + CRLF) — touches `checklist_engine.py`, #433's area

## Owed to Tommy at the next checkpoint

1. The governor trip band at 17–21%. **Measured cost: 3 dispatches for #433, 4 (so far) for #460**, 2 for #436, 1 for #464. This is the single largest drag on the wave.
2. Two reviewer dispatches stalled with no artifacts; #470 merged on self-verified falsification
   evidence instead of independent review. He should know the review never landed.
3. #460 will return **doctrine candidates** — records that look like real rules. Promoting any of
   them into `docs/agents/*` is his call, always.

_Updated: 2026-08-08T02:50:00Z_
