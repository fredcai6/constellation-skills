# Crash-resume state note — epic-418-redux

**WAVE 3 IS COMPLETE AND MERGED. `execute` is BLOCKED on contract expiry. Do not dispatch anything.**

- **step:** `execute` — **blocked**. Remaining after `execute`: `closeout` only.
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
  — then get the contract refreshed before anything else. Resume with
  `resume execute --session-id admiral-epic-418-redux --reason "<why the blocker cleared>"`.
- **pid:** one agent still live — see "Still running" below. No other agents in flight.
- **expected artifact:** a refreshed latitude contract, then A2's cut, then `closeout`.

**GREEN MAIN: `1793 passed, 2 skipped, 683 subtests, exit 0`** (483s, real exit code captured) — the
wave-2 baseline of 1782 plus 11 new tests (7 from #491, 4 from #492). This is the closeout baseline.

## Wave 3 — all four merged, closed, and reviewed on the forge

| Issue | PR | Merge | Review |
|---|---|---|---|
| #461 | #490 | `ad149283` | APPROVE, posted |
| #488 | #491 | `8b9330ea` | APPROVE, posted |
| #489 | #491 | `8b9330ea` | APPROVE, posted |
| #465 | #492 | `4da9bc9b` | APPROVE, posted |

Boundary `w3-to-w4` recorded, `decision=replan`, `admiral-prelaunch` verifier **exit 0**.

## STILL RUNNING — do not sweep this worktree

**`C:/Programs/wt-w3a-465`** — W3-A's continuation Commander (`commander-w3a-465-b`) is still driving
its own spine's bookkeeping at gate `execute`. Its PR is **merged** and #465 is **closed**, so the
epic outcome is settled and nothing waits on it. But: **harvest its trio before sweeping**, and check
its lease is released or the agent confirmed dead first. All other wave-3 worktrees are harvested and
swept; their branches are deleted.

## Why blocked — three reasons, one refresh clears them

1. The contract expired at this boundary (Addendum R1: *"the wave-3 boundary, or 72h"*), and its own
   clause forbids further dispatch across the expiry.
2. **`closeout` itself needs a dispatch** — the lessons auditor — so this blocks the very next spine
   step, not just wave 4.
3. **A2 has no issue cut**, and cutting it is `scope change`, which the contract marks **surfaced**.

Deliberately NOT done: wave-4 launch orders, and A2's cut. Their content is the question the expiry
handed to Tommy.

## Still owed to Tommy at the wave-3 checkpoint

0. **RE-FRAME BEFORE ASKING: the governor does not ship, so the band question was mis-posed.**
   Measured: tracked `.claude/settings.json` wires `spine_rail.py` on `Stop`/`SessionStart`/
   `PostToolUse` and wires `gauge_writer_hook.py` on **nothing**; `git ls-files .claude/` returns
   `settings.json` only, so `settings.local.json` is untracked. **Every governor observation this
   epic has made came from machine-local config.** The spec already ruled on this (critic F2, Tommy
   2026-08-07: *"wire gauge_writer_hook into the TRACKED project settings so the governor ships like
   spine_rail already does"*) and it is **#458**, off-chain and not done.
   **The governor thread is four parts, three already written:** #458 (ships at all) · #264 (asserts
   it is measuring — 1144 lines, **unmerged**) · #488 (stops it silencing itself — in flight) ·
   #452 (attribution). Recommend landing them as one piece after wave 3.
1. **The trip band — RECOMMENDATION CHANGED, don't ask the old question.** W3-C tripped on its
   *wrap-up* gate with all work complete and verified; the trip cost a relaunch to open a PR and
   nothing else. Wave 2's 6-of-10 relaunches were the same shape. So a retuned band changes *when*
   the same relaunch happens, not what it costs. The trip was cheap because the crew wrote a
   `refresh-request` and handed off — **A2's design working before A2 is built**, and wave 3 has now
   run A2's DC5 round trip (trip → handoff → refresh → resume) by hand and successfully. Recommend:
   leave the band, ship A2, and hand its Commander this run as a positive control.
   *(Superseded framing, kept so it isn't re-asked:* **the governor trip band at 17–21%** *—)* Cost 6 of wave 2's 10 dispatches. A production default and a
   threshold question, so surfaced, not mine. Wave 3 gives the first **uncontaminated** Admiral-side
   measurement, because #488's fix restores my own gauge — the wave-2 number was taken while I was blind.
2. **#457's lease-liveness defect** — evidenced and commented, deliberately **not** folded into wave 3.
   The amendment says *easy*; this one is not. Both readings of the field are uninformative, so fixing
   it means deciding how liveness is encoded at all, which ends at a load-bearing interface.
3. **#264's unmerged gauge-chain tests — recommend landing them.** See the sweep verdict below. The
   epic's own dark-governor incident is the argument: an assertion that the gauge is still
   *measuring* has existed, written and unmerged, the entire time. Landing it is a **scope change**
   (surfaced), needs a rebase over 211 commits, and should wait until #488 merges so it lands on
   fixed ground rather than steering a running crew.
4. **#460's 22 doctrine candidates** — collected, nothing promoted. At
   `.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4". Promotion is always his call.

## Done this session, beyond the wave launch

- **Harvest before sweep — executed.** Four files existing **nowhere in the git object store** were
  collected to `.agent-work/harvest-418-redux/`: `RETURN.md` from `b-420`/`d-422`/`g-425`, and
  `h-447`'s **261 KB `AGENT_FEEDBACK.md`**. Identified by `h=$(git hash-object <f>); git cat-file -e
  "$h"`, not by filename — which spared `h-447/.agent-work/LESSONS.md`, already in git. Disposition
  (convert to episodes vs drop with a reason) is the closeout audit's call, deliberately open.
- **A2's cut is HELD, deliberately**, per my own pre-ruling: A2 is cut against what B extended
  *actually* leaves behind, and that is not known until wave 3 merges. Shape when its turn comes:
  ~three issues — DC1-3 (refusal→instruction, #431 dissolves), DC4+DC6 (per-gate override exercised
  once; the compliance signal), DC5 (the full trip→handoff→refresh→resume round trip) last.
- **The defect family has three independent sources in this epic**, so it is the spine, not a theme
  I proposed: critic **F8** (*"the purest check-that-cannot-fail in the document"* — *no absence is
  evidence*), **A2's DC6** pricing it as a deliberate design cost (*"an instruction is satisfied or
  ignored with identical traces"*), and wave 2's four field findings.

## Operating change made mid-wave — keep it

**Batch bookkeeping commits; push at boundaries, not after every log append.** `.github/workflows/
ci.yml` has no `paths-ignore`, so an `.agent-work/`-only commit runs the full 8-minute suite. Pushing
after every entry put **6 concurrent CI runs on `main`, all mine**, and PR #490's own check sat
`pending` ~25 minutes behind them. Push at natural boundaries (crew return, merge, checkpoint) — that
still satisfies crash-resume durability. Adding `paths-ignore` to the workflow is the source fix and
is a **closeout triage candidate**, deliberately not done while PRs are gating on CI.

## Settled — do NOT re-derive

- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`** (#454).
- **A piped command's `$?` is the pipe's exit code, not the command's.** Use `${PIPESTATUS[0]}`. This
  cost a false "verified" once already.
- **#468:** the repo's vendored `verify_iterative_role_artifacts.py` cannot run from this repo — its
  installed-skill guard passes by accident because the repo is named `constellation-skills`. Use the
  installed copy.
- **`verify_worktree_isolation.py` has two modes.** Bare paths = Admiral pre-wave gate; `--here <path>`
  = the Commander's check, and it tests **cwd**.
- **`git cat-file -e origin/main:<path>` is broken in Git Bash here** — path-converts and reports
  MISSING for files that exist. Use `git diff --name-only`.
- **The lease field is not a liveness signal in either direction.** 147 tracked spine files, 18
  `active`, exactly 1 live. `null` is equally produced by a crew releasing between gates. What
  discriminates: match the lease's `session_id` against **your own**.
- **My own gauge is dark** (`gauge-skip.json`, `reason: ambiguous-binding, candidate_count: 2`) until
  #488 lands. Watch context by judgement. Cause: my spine and my own `latitude-interrogation.json`
  resolve to one gauge path, and the writer counts bindings rather than distinct paths.
- **#447 CLOSED** with a per-done-condition accounting; condition 4 recorded **partial**, not done.
- **Never pass a markdown body to `gh` as a double-quoted bash string.** A backticked code span is
  executed as **command substitution**: it errors to stderr while the comment/PR **posts anyway**,
  silently missing that phrase, with every success signal intact. Write the body to a file and use
  `-F <file>` / `-F body=@<file>`. The launch orders already say this for PR bodies; it is equally
  true for `gh issue comment`. Cost me a corrupted comment on #264 this session.

## Stale worktrees — sweep verdict, surveyed 2026-08-08

**`C:/Programs/constellation-skills-wt/governor-264` — DO NOT SWEEP.** It is the only one holding
work that is not in main. Branch `governor/264-e2e-assertion`: **3 commits, 1144 lines, 13 tests,
211 behind main**, and `git ls-files | grep gauge_chain` returns **nothing** — absent from main.
**#264 is the only OPEN issue of the eight.** Includes
`test_ladder_fill_series_is_non_decreasing_and_actually_moves` (the assertion that the gauge is still
*measuring*, not merely producing records — the guard that would have caught my dark governor) and
`test_chain_ambiguous_binding_writes_no_gauge_and_flags_every_candidate`, which builds
`_ambiguous_work_trees` with **distinct parents** and therefore specifies the negative direction
**#488's fix must preserve**. Surfaced to Tommy at the wave-3 boundary; commented on #264.

**Sweep-safe after harvest:** `epic418-a2-440`, `epic418-b-420`, `epic418-g-425`, `epic418-h-447` —
zero non-`.agent-work` diffs vs main.

**`epic418-a-419` and `epic418-d-422`: flagged INSPECT by diff, then cleared by the forge.** Both
show ~9 non-`.agent-work` file diffs against main, which looks like unlanded code. It is not: their
branches are 200+ commits behind and their work was **squash-merged**, so a three-dot diff shows the
pre-squash form of work that did land. **#419, #420, #422, #425, #440 and #447 are all CLOSED** per
`gh issue view` — the diff was the misleading signal and the tracker was the reliable one, which is
this epic's own lesson applied to its own cleanup. Harvest, then sweep.

`verify-w0` is a detached HEAD scratch tree; no branch, nothing owed.

**Order is not optional:** harvest each worktree's durable trio **before** `git worktree remove` — and
under an epic lease the trio lands at `<worktree>/.agent-work/`, not the main checkout, because
`durable_root()` deliberately returns the worktree root while the main checkout is fenced. Sweeping
first silently drops that run's learning.

_Updated: 2026-08-08T04:05:00Z_
