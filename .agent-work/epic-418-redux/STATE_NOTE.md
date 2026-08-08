# Crash-resume state note — epic-418-redux

**WAVE 3 IN FLIGHT. Four agents have run; two are live right now. Do not re-dispatch anything
without checking the worktrees and the forge first.**

| Dispatch | Issue(s) | State as of 05:35Z |
|---|---|---|
| W3-B | #461 | **DONE — PR #490 open.** Reviewer dispatched into `C:/Programs/wt-rev-461` (branch `review/w3-461`, at PR head `fa1378ed`). **LIVE** |
| W3-C | #488 + #489 | tripped the governor at 16% on `m3-verify`, filed `refresh-request`, **relaunched** into the same worktree + `IMPLEMENTER_PLAN.json`. Both fixes code-complete and verified; only PR + result artifact remain. **LIVE** |
| W3-A | #465 | 1 commit, still working, no PR yet |

**If you are resuming cold:** W3-C's lease `impl-w3c-488-489` is still held and its gate is still
`in-progress` — that is the **refresh** shape, not a dead crew. Do not force-claim it or restart it
from zero; read `current` on `C:/Programs/wt-w3c-488-489/.agent-work/w3c-488-489/IMPLEMENTER_PLAN.json`
and continue from there. Its PR body is already drafted at `.agent-work/w3c-488-489/pr-body.md`.

- **step:** `execute` — in-progress. Remaining after `execute`: `closeout` only.
- **slug:** `epic-418-redux` · main checkout `C:/Programs/constellation-skills` · `main` ==
  `origin/main`, pushed, working tree clean — verify with `git rev-parse --short HEAD` and
  `git rev-parse --short origin/main` as **separate** invocations (a compound one returns
  "fatal: Needed a single revision"). A literal hash in this field is wrong the moment this file is
  committed, since committing it advances main; it was stale twice for exactly that reason.
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
  — then poll the three worktrees below.
- **pid:** three background Agent dispatches; no OS pids to chase. Recover from their worktrees.
- **expected artifact:** one result artifact + PR per dispatch.

**Green main: `476e044d` → 1782 passed, 2 skipped, 683 subtests, exit 0** (real exit code captured).
Wave-3 branches are cut from `c0ad5ecd`, which adds only `.agent-work` records on top, so the
baseline holds.

## Wave 3 — in flight

| Dispatch | Issue(s) | Worktree | Branch | Shape / tier | Owns |
|---|---|---|---|---|---|
| W3-A | #465 | `C:/Programs/wt-w3a-465` | `epic-418/w3a-465` | full Commander / Opus | `skills/constellation-reviewer/**`, `scripts/checklist_engine.py` |
| W3-B | #461 | `C:/Programs/wt-w3b-461` | `epic-418/w3b-461` | implementer / Sonnet | `tests/test_episode_negative_control.py` |
| W3-C | #488 + #489 | `C:/Programs/wt-w3c-488-489` | `epic-418/w3c-488-489` | implementer / Sonnet | `scripts/hooks/gauge_writer_hook.py`, `tests/test_verify_spec_confirmed.py` |

Fences verified disjoint before launch. `verify_worktree_isolation.py` on all three: exit 0,
"3 distinct worktrees". Launch orders at `.agent-work/epic-418-redux/launch-orders/LO-465.md`,
`LO-461.md`, `LO-488-489.md`.

**The wave's single organizing instruction, in all three orders:** build the defective world and
observe the current code getting it wrong *before* fixing. Green alone is not evidence for any of
these four issues — green is what the broken version does too.

## Boundary w2-to-w3 — recorded and verified

`decision=replan`. Packets at `transitions/w2-to-w3/{REPLAN_INPUT,REPLAN_RESULT}.json`;
`CURRENT_TRUTH.md` and `WAVE_REVIEW.md` rendered by the verifier.
`verify_iterative_role_artifacts.py admiral-prelaunch` **exit 0** — run from the INSTALLED copy at
`C:/Users/fredc/.claude/skills/constellation-admiral/scripts/` per #468.

**Four shape errors it refused before passing**, all mine, all worth knowing next boundary:
1. `blocks` naming an issue outside the current wave's issue list.
2. `completed_outcomes` as strings — must be objects `{issue_id, outcome, evidence}`.
3. A non-wave issue (#470) in `completed_outcomes`: completed ∪ open must **exactly partition** the
   current wave's issue ids.
4. `material_changes` as strings — must be objects `{surface, before, after, reason}`, and a
   `surface` in `{intent_and_why, definition_of_done, good_enough, hard_constraints,
   fixed_decisions}` additionally demands `applicable: false` plus an escalation packet.

## Contract — refreshed AND amended, 2026-08-08

Base contract + **Addendum R1**. Two messages from Tommy, minutes apart:

> *"you can keep running, you're compacted. close the complete issues, and get on into wave 3.
> 461 & 465 is good"*

> *"woah, feel free to add easy or useful fixes to wave 3. id rather not clutter the issue board or
> delay fixes that are easy to just knock out now"*

- Issue closing: **delegated for #433/#436/#460/#464 only**; surfaced for everything else.
- Wave 3: **#461 + #465 + #488 + #489**. The second message reversed my own hold on the latter two.
- **Standing preference established: a genuinely cheap fix gets done in the current wave, not filed
  and deferred.** The board is for what needs deciding, not for what needs typing.
- **New expiry: the wave-3 boundary, or 72h from 2026-08-08T03:00Z.**

## Wave 2 — closed out

| Issue | PR | Merge | Tracker |
|---|---|---|---|
| #433 | #485 | `538d5fd7` | **CLOSED** |
| #436 | #472 | `7bc3f8c2` | **CLOSED** |
| #460 | #487 | `476e044d` | **CLOSED** |
| #464 | #473 | `0b4a11a7` | **CLOSED** |
| — | #470 | `e8c735af` | Admiral's own fixture-path repair |

All five confirmed MERGED via `gh pr view --json state`. **Never use an ancestry test** — squash-merging
#470 orphaned base `73b4517`, so ancestry returns the same answer for merged and abandoned.

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
