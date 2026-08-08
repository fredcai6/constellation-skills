# Crash-resume state note — epic-418-redux

**WAVE 4 IS LAUNCHING: one Commander on #467 (A2, trip semantics). Do not dispatch a second.**

- **step:** `execute` — in-progress (resumed 2026-08-08 on Tommy's *"keep rolling"*).
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
- **wave-4 dispatch:** one Commander, issue **#467**, worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`, branch `epic-418/a2-467-trip-semantics`,
  model **Opus**. Launch order: `launch-orders/LO-467.md`.
- **expected artifact:** a green, reviewed PR closing #467; then the wave-4 checkpoint to Tommy.

**GREEN MAIN BASELINE: `1793 passed, 2 skipped, 683 subtests, exit 0`** — carried from the wave-3
close, re-verified on merged main after PR #499.

## Contract state

**Addendum R2 (2026-08-08)** — refreshed on *"keep rolling"*. Expiry: **epic close, or 72h from
2026-08-08T07:00Z**. Grants: the closeout lessons-auditor dispatch, and wave 4 on #467.
**Still surfaced, NOT granted:** continuing past A2 into F (#424), C (#421), E (#423).

## The correction that set wave 4 — do not re-make this mistake

**A2 was never uncut.** For three waves this note said *"A2 has no issue cut"* and I twice told
Tommy that cutting it was a scope decision I would not take. **#467 is A2**, OPEN, carrying DC1-DC6
verbatim, a `Fixed` list, `Blocks: #424`, and its own evidence protocol. What I had been calling
"cutting A2" was **decomposing an already-cut issue into three**, which is the board clutter he has
warned against twice.

The cause is this epic's own defect family aimed at me: **a claim carried in this note across three
waves and a compaction, never re-derived from the tracker.** A stale note and a true note read
identically. Before relying on any status claim in this file, `gh issue view` it.

## Wave 3 — closed (all merged, closed, reviewed on the forge)

| Issue | PR | Merge | Review |
|---|---|---|---|
| #461 | #490 | `ad149283` | APPROVE, posted |
| #488 | #491 | `8b9330ea` | APPROVE, posted |
| #489 | #491 | `8b9330ea` | APPROVE, posted |
| #465 | #492 | `4da9bc9b` | APPROVE, posted |

Boundary `w3-to-w4` recorded, `decision=replan`, `launch_id=wave4-a2-trip-semantics`,
`admiral-prelaunch` **exit 0**.

## Remaining after wave 4

`execute` postconditions c1/c2/c3, then **`closeout`** only: lessons-auditor dispatch, cartographer
reconcile, harvest-before-sweep, repo hygiene, epic summary, user acceptance — then `release` the
lease as the **very last** action.

## Worktrees — sweep verdict

**`C:/Programs/constellation-skills-wt/governor-264` — DO NOT SWEEP.** 3 unmerged commits
(1144 lines, 13 tests) against **#264, still open**; absent from main (`git ls-files | grep
gauge_chain` returns nothing). Holds
`test_ladder_fill_series_is_non_decreasing_and_actually_moves` — the assertion that the gauge is
still *measuring*, the guard that would have caught this epic's dark governor — and
`test_chain_ambiguous_binding_writes_no_gauge_and_flags_every_candidate`, which uses **distinct
parent paths** and so specifies the negative direction #488's fix had to preserve.

**Harvested, sweep-safe at closeout:** `epic418-a-419`, `epic418-a2-440`, `epic418-b-420`,
`epic418-d-422`, `epic418-g-425`, `epic418-h-447`; `verify-w0` is a detached scratch tree.
Harvest output is at `.agent-work/harvest-418-redux/` (4 files that existed **nowhere in the git
object store**, identified by `h=$(git hash-object <f>); git cat-file -e "$h"`, not by filename).

**Order is not optional:** harvest each worktree's durable trio **before** `git worktree remove` —
under an epic lease `durable_root()` returns the **worktree** root, so the trio lands where the
sweep eats it.

## Still owed to Tommy at the wave-4 checkpoint

1. **Does the epic continue past A2** into F (#424), C (#421), E (#423)? Three workstreams.
2. **The governor thread as one piece:** #458 (wire the writer into *tracked* settings so it ships
   at all) · #264 (land the 1144 unmerged lines asserting it still measures) · #452 (attribution).
   #488 is done. Measured: tracked `.claude/settings.json` wires `spine_rail.py` only and the gauge
   writer on **nothing** — every governor observation this epic made came from untracked local
   config.
3. **The trip band is role-blind** — the recommendation CHANGED, don't re-ask the old question.
   Crews trip at 17-21%; I ran to 44% with no trip on the same machine and hook. And every trip
   this epic saw cost a relaunch at a seam, never lost work — A2's design working before A2 is
   built. Recommend: leave the band, ship A2, hand its Commander this run as a positive control.
4. **#493, #495, #496, #497, #498** — five, not six: **#494 is already CLOSED**. Keep-or-drop is an
   acceptance-time question; the closeout audit produces the evidence.
5. **#460's 22 doctrine candidates**, collected, nothing promoted, at
   `.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4". Promotion is his call.
6. **#439 / #484 — two template-instantiation defects of one family** (`execute.c2`'s relative
   script path; `archive.c2b`'s literal never-substituted `<branch>`). Two in one spine argues for a
   sweep of the class, not two point fixes. Closeout triage candidate.

## Settled — do NOT re-derive

- **The repo-vendored `verify_iterative_role_artifacts.py` REFUSES from this repo** (#468):
  `installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py`.
  Use the **installed** copy at
  `C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py`.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`** (#454).
- **A piped command's `$?` is the pipe's exit code.** Use `${PIPESTATUS[0]}`, or redirect to a file.
  This cost a false "verified" once already.
- **Never pass a markdown body to `gh` as a double-quoted bash string** — a backticked code span is
  executed as **command substitution**; the comment posts anyway, silently missing that phrase, with
  every success signal intact. Write to a file, use `-F`. Cost a corrupted comment on #264.
- **`gh issue close -F <file>`** accepts the flag, prints nothing, and does **not** close. Use
  `--comment "$(cat <file>)"`. And `--comment` is **silently discarded** if the issue was already
  closed by a PR body keyword — re-read the issue after closing, or the evidence evaporates.
- **`gh pr merge` can exit 1 on a merge that SUCCEEDED** (`--delete-branch` fails on a worktree-held
  branch). Ask the forge for state; never infer from the exit code.
- **`gh pr review --approve` is REFUSED** — "Can not approve your own pull request", because every
  agent authenticates as the same identity that authored the PR. Substitute:
  `gh pr review <PR> --comment -F <file>` with the verdict on the first line. This is **not**
  reviewer negligence, which is how I misread #470 three times.
- **Never use an ancestry test to decide whether anything merged.** Squash-merge returns the same
  answer for merged and abandoned. Ask the forge. Likewise `git diff origin/main..HEAD` in a
  worktree lists files where *main* is ahead — it reads like your branch reverted them.
- **The lease field is not a liveness signal in either direction** (147 tracked spines, 18 `active`,
  1 live). Nor is the heartbeat: a Commander read 27 minutes stale while actively journaling its
  inner checklist. What discriminates: `find <worktree> -newermt "-6 minutes" -type f`.
- **`git cat-file -e origin/main:<path>` is broken in Git Bash here** — use `git diff --name-only`.
- **`verify_worktree_isolation.py` has two modes.** Bare paths = Admiral pre-wave gate;
  `--here <path>` = the Commander's check, and it tests **cwd**.
- **Batch bookkeeping commits; push at boundaries.** `ci.yml` has no `paths-ignore`, so an
  `.agent-work`-only commit runs the full 8-minute suite. Pushing per log entry put **6 concurrent
  CI runs on main, all mine**, starving a PR's check ~25 minutes.

_Updated: 2026-08-08T07:20:00Z_
