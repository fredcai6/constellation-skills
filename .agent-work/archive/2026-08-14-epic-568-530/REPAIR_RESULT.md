# Repair result — epic-568-530 (wave-2 repair, resolved worktree binding)

**Crew session:** `constellation/epic-568-530/g2-repair/commander/attempt-1`
**Branch:** `epic-568/530-binding` · **Worktree:** `.worktrees/epic-568-530`
**Repair commit:** `adeb1cd6`
**Status:** GREEN and parked at `archive`. Publication is all that remains.

## Verdict

The lane is green on its own cache-clean full Linux suite, without weakening anything it proved.
All three pasted failures are cleared by one reworded sentence and one mechanical map rebuild.

## Suite counts, cache-clean, full Linux suite

Every run below was preceded by
`find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`.

| | failed | passed | skipped | subtests |
|---|---|---|---|---|
| Before (Admiral's pasted wave-2 gate, this commit) | 3 | 2979 | 7 | 1130 |
| After (measured by me at `adeb1cd6`) | **0** | **2982** | 7 | 1130 |
| `main` baseline at `0448275e` (pasted) | 0 | 2980 | 7 | — |

Totals reconcile: 3+2979 = 0+2982 = 2982 collected. The lane runs 2 net tests above `main`,
which is the `spine_rail.py` red/green guard the issue closes on. Nothing was deleted or weakened.

Runner note: `python3` on this box has no pytest. The suite runs under `python`
(`/home/tommy/.local/share/pyfix-venv/bin/python`, pytest 9.1.1). A gate measured with `python3`
will report "No module named pytest" rather than a count.

## What I reworded, and why

`episodes/active/epic-568-530-001.md`, statement `a5`, kind `workaround`.

- Was: `Use the approved escalated TTY apply_patch executable with patch text on stdin and EOF, and retain the incident in the work artifacts.`
- Now: `The run applied its patches through the approved escalated TTY apply_patch executable, with patch text on stdin terminated by EOF, and the incident stayed recorded in the work artifacts.`

`scripts/verify_episode_observations.py` scopes its imperative rule to the `workaround` and
`proposed-remedy` kinds, and within those only flags a clause-OPENING bare verb. `Use` opened the
clause, so the guard correctly read a record of what happened as an instruction to a future reader.

The reword changes grammatical mood and nothing else. Every claim survives intact: the escalated TTY
`apply_patch` route, the stdin patch text, the EOF terminator, and the retained work artifacts. Per
pre-ruling 1 I rewrote rather than adding an exception entry -- the exception list is for statements
that genuinely must stay imperative, and this one carries no instruction at all. The exception list
is unchanged at 11 entries.

Guard after: `806 statements examined, 0 unlisted offenders, 11 on the exception list`. The
statement count is identical to the failing run's 806, so the scan still examines the same records
-- which is what `test_the_real_store_scan_actually_examined_the_records` exists to prove.

## Decision on the uncommitted `tests/test_spine_rail.py` change

**There was none.** The order's note is wrong on this point, and I am reporting that rather than
manufacturing a decision to match it.

On arrival `git status --porcelain` showed exactly `?? .agent-work/epic-568-530/`.
`git diff HEAD -- tests/test_spine_rail.py` was empty and `git stash list` was empty. The 93 lines
of tests are already committed at `97eb5d34`, inside the implementation diff that was independently
APPROVEd. I did not touch the file. See F2.

## Map freshness

Fresh. Regenerated mechanically per pre-ruling 3 with `python3 -m scripts.code_map build --root .`.
`map/INDEX.md` moved 7 insertions / 7 deletions and nothing else changed.
`test_map_tree_freshness_root_index_matches_a_fresh_build` passes.

## File ownership honoured

Commit `adeb1cd6` touches exactly two files, both mine:
`episodes/active/epic-568-530-001.md` and `map/INDEX.md`.
`scripts/checklist_engine.py` was never edited -- #510 holds that lane. `scripts/hooks/spine_rail.py`
and `tests/test_spine_rail.py` are untouched by this repair; the production change stands as APPROVEd.

## Spine state — parked at `archive`, lease deliberately still held

`.agent-work/epic-568-530/spine.json`: `init` through `feedback` all `complete`; `archive` `blocked`.
The recorded blocker is that archive postconditions `c2`/`c2b` require the branch pushed and a PR
open or merged. I am fenced from push, PR, and merge, so archive cannot advance. Parking here is the
order's instructed outcome, not a failure.

I did **not** release the engine lease. Doctrine releases the lease as the last action AFTER the
closing advance on a terminal archive; releasing a non-terminal spine would leave the remaining
closeout entries outside any lease and fail the terminal provenance check. The lease is left live
for the authorised session that pushes and closes.

I also could not take the lease over, for the reason in F1: this session's MCP door is bound at
launch to a foreign scratch spine and, by a deliberate test-pinned property, cannot be redirected.
I did not hand-edit spine state and did not substitute the engine CLI for the door.

## Remaining work for the Admiral

1. Push `epic-568/530-binding` and open its PR.
2. Resume `archive` from a session whose `SPINE_FILE` points at this lane's spine (see F1), take over
   the lease from `constellation/epic-568-530`, satisfy `c2`/`c2b`, advance `archive`, release last.

## Floated

- **F1 (blocking):** "Spine interaction is MCP-only" is not executable from this session. Needs a
  relaunch with `SPINE_FILE` bound to this lane's spine.
- **F2:** the order's uncommitted-`test_spine_rail.py` premise is false.
- **F3:** episode repairs are only measurable once committed; a mid-edit suite run always shows
  `test_canon_episode_store_untouched` red.

Findings detail: `.agent-work/epic-568-530/FINDINGS-wave2-repair.md`.
