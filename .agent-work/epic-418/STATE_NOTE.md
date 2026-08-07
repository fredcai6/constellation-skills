# Crash-resume state note — epic-418

**TWO Commanders running concurrently: `cmdr-440-binding-cwd` (#440, governor) and
`cmdr-447-episodes-retirement` (#447, workstream H). Wave 0 is complete and merged, four of four.**

- **step:** `execute` — in progress. `init` and `latitude` complete. Remaining after `execute`:
  `closeout` only.
- **slug:** `epic-418` · main checkout `C:/Programs/constellation-skills` · `origin/main` @ `cbd9aee`
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418/spine.json current --session-id admiral-epic-418` — then poll both worktrees below for their spine state and `RETURN.md`; adjudicate, gate on real check exit codes, merge sequentially
- **pid:** none — Commanders are harness subagents, not detached OS processes. Recover a dead one by relaunching a continuation into the same worktree, resuming from that worktree's own engine state.
- **expected artifact:** two merged PRs — `epic-418/a2-440-binding-cwd` (a HARD trip **firing** from a worktree-dispatched agent, two-arm with a control) and `epic-418/h-447-episodes-retirement` (both shared logs retired, with a **shipped guard** proven to fail on purpose)

## In flight — both launched off merged main `cbd9aee`

| Issue | Commander | Worktree | Branch | Tier |
|---|---|---|---|---|
| #440 | `cmdr-440-binding-cwd` | `constellation-skills-wt/epic418-a2-440` | `epic-418/a2-440-binding-cwd` | Opus |
| #447 | `cmdr-447-episodes-retirement` | `constellation-skills-wt/epic418-h-447` | `epic-418/h-447-episodes-retirement` | Opus |

Launch orders: `.agent-work/epic-418/launch-orders/A2-440.md` and `H-447.md` (+ `_COMMON.md`).

**Fence between them:** #440 owns `scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`,
`scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md`. #447 owns the lessons/feedback/episode
surface. Collisions float to the Admiral; **no commander-to-commander coordination**. Expect a merge
conflict in `.agent-work/LESSONS.md` / `AGENT_FEEDBACK.md` — Admiral resolves, and it is part of what
#447 is fixing.

## Wave 0 — complete, all merged, main green

| Issue | Verdict | Merge |
|---|---|---|
| A #419 governor per-agent identity | **WIN** — a HARD trip **fired** live (subagent ALPHA at 33%; engine refused its `advance`); control arm no reading | `cbd9aee` |
| B #420 engine channel | **WIN** — both fixes; `anchors`/`constraints` proved NOT vestigial (20+ archived gates), so C's targets exist | `c33d421` (+ #435) |
| D #422 wire prose-only invariants | **WIN** — #329 + #328 refuse instead of hoping; deliberate-breakage test passes | `e74fe55` |
| G #425 file triage-candidate defects | **WIN** — 9 tracker refs; no code change, correctly | n/a |

Merged main verified green: **1688 passed, 2 skipped, 550 subtests, real exit 0.** Tree hash of
`cbd9aee` equals the tree A tested, so that run *is* a run of merged main.

## Tommy's rulings — binding

1. **Wave 1 is #440, not C #421.** *"the goal was working governor asap… let's actually finish a."*
2. **Workstream H added and run in parallel** — *"I want to close out the episode switch right. can be
   in parallel with the governor work."* Filed as **#447**.
3. **Episodes are a record of what happened, NOT a playbook.** *"we shouldn't be reading the episodes
   like lessons, it's a store for things that happened to replace both feedback and lessons."* A
   retirement that re-points the read path at `episodes/` reproduces the defect and fails.
4. **K2 gets its own cluster.** The spec's "consumed by workstream A" claim is false today.
5. **#432's fix routes into F #424** (spine interface redesign), with per-step custom instructions on
   the spine replacing front-loaded launch orders. **C #421 is the mechanism for that**, so C is no
   longer mere corpus shrinkage.
6. **C #421 and F #424 are deferred, not cancelled.** F still needs A+B+C.
7. **E #423's batch confirm GIVEN and EXECUTED.** *"ok to hold 285 for 447. close 298"* then *"close
   the other 3."* **#131, #289, #298, #322 are CLOSED**, each with its own evidence comment; **#285 is
   HELD OPEN** and routed to #447 (its close rationale — "the playbook was deleted wholesale by #308"
   — is false). All five states verified at source after the fact. E's four closeout debts are filed:
   **#448** resolved-load-manifest, **#449** #298's item J, **#450** B1 first consolidation, **#451**
   23-of-32 unharvested episodes.
8. **E's remaining half is NOT done and is waiting on Tommy:** the theme-grouping labels. The repo has
   **no such labels at all** (only GitHub defaults plus `epic`/`afk`/`hitl`), so this means creating
   ~13 labels and applying them across ~108 open issues. Boundaries are marked costly-to-revert and
   only the K2 question was answered, so **do not apply the map without his go**. He may also
   legitimately rule the labelling not worth doing — record that as the answer and close E's sweep on
   it. Best executed by a dispatched subagent, not in the Admiral's own context.

## What is already settled — do NOT re-derive

- Latitude contract confirmed and refreshed. Subagent dispatch granted at every tier. **Scope
  discipline is a standing ruling** — narrows *breadth*, never *evidence*.
- **`py` is NOT the test runner on this box** — no pytest, produces fake failures. Use `python`.
- **`RETURN.md` and several `notes-*.md` are TRACKED on main** (A committed its return artifact), so
  every worktree off `cbd9aee` inherits A's. Existence of `RETURN.md` proves nothing — check that it
  names the right commander and is dirty vs HEAD. This produced one false positive; closeout hygiene
  should untrack them.
- **Standing constraint:** `governor-264`'s worktree and its three unmerged commits stay put —
  disposal blocked pending #412's orphan-risk read.
- **Worktrees NOT to sweep until closeout's harvest-before-sweep:** `epic418-a-419`, `epic418-b-420`
  (staged trio at `.agent-work/staged-feedback/b420-engine-channel/`), `epic418-d-422`,
  `epic418-g-425`, plus both in-flight ones. **A applied its lessons directly to `LESSONS.md`** —
  already carried onto main via the union merge, do **not** double-apply. `verify-w0` is a throwaway.
- **Uncommitted on the main checkout:** epic-267's closeout records in `.agent-work/AGENT_FEEDBACK.md`
  and `.agent-work/LESSONS.md`, plus this epic's work area. These block `git pull`. Commit at
  closeout; do not discard.

## Findings filed this run

#427–#431 (G) · **#432** a dispatched role can skip the engine and its return still reads clean ·
#433 render `directives` · **#440** wave-1 mission · **#446** archive gate `c2b` accepts only an OPEN
PR, so a well-run epic forces `--force` on the success path · **#447** workstream H.

**Disproved premise, material to E:** #285's proposed close says #308 deleted the playbook wholesale.
It did not — measured on `cbd9aee`, the file, its writer, its own read instruction, two skills
pointing at it, and the `AGENT_FEEDBACK` gate all still ship.

_Updated: 2026-08-06T08:45:00Z_
