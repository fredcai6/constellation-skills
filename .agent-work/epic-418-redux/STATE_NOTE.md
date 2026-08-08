# Crash-resume state note — epic-418-redux

**WAVE 3 IS IN FLIGHT: three dispatches, four issues. Do not re-dispatch without checking the
worktrees first.**

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

1. **The governor trip band at 17–21%.** Cost 6 of wave 2's 10 dispatches. A production default and a
   threshold question, so surfaced, not mine. Wave 3 gives the first **uncontaminated** Admiral-side
   measurement, because #488's fix restores my own gauge — the wave-2 number was taken while I was blind.
2. **#457's lease-liveness defect** — evidenced and commented, deliberately **not** folded into wave 3.
   The amendment says *easy*; this one is not. Both readings of the field are uninformative, so fixing
   it means deciding how liveness is encoded at all, which ends at a load-bearing interface.
3. **#460's 22 doctrine candidates** — collected, nothing promoted. At
   `.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4". Promotion is always his call.

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

## Not swept — predecessor-run worktrees, deliberately left

`epic418-a-419`, `epic418-a2-440`, `epic418-b-420`, `epic418-d-422`, `epic418-g-425`, `epic418-h-447`,
plus `governor-264` and `verify-w0`. Sweep at closeout, **after** harvesting each one's durable trio —
a worktree swept before its trio is collected silently drops that run's learning.

_Updated: 2026-08-08T04:05:00Z_
