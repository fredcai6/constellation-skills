# Crash-resume state note — epic-418-redux

**Wave 2 ("B extended") is LAUNCHED, four-wide. If this session died, the four agents below may
still be working in their own worktrees — inspect their worktrees before assuming anything.**

- **step:** `execute` — in progress, wave 2 launched. Remaining after `execute`: `closeout` only.
- **slug:** `epic-418-redux` · main checkout `C:/Programs/constellation-skills` · branch `main`
  · latitude CONFIRMED · boundary `w1-to-w2` decided **replan**, prelaunch verifier exit 0
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
  — then poll the four worktrees below for PRs and adjudicate
- **pid:** four background subagent dispatches (harness-managed, no OS pids). Poll by worktree
  state and by `gh pr list`, never by waiting on a completion signal alone.
- **expected artifact:** four PRs against `main`, one per issue, each with a notes file at
  `.agent-work/epic-418-redux/notes-<issue>.md`

## Wave 2, launched 2026-08-07

| Issue | Dispatch | Tier | Worktree | Branch |
|---|---|---|---|---|
| #433 render `directives` + completeness property | Commander (delegated) | Opus | `C:/Programs/constellation-skills-wt/r418-433` | `epic-418/b-433-render-directives` |
| #460 episode records read as prescriptions | Commander (delegated) | Opus | `C:/Programs/constellation-skills-wt/r418-460` | `epic-418/b-460-episodes-observations` |
| #436 enumeration check must be seen refusing | implementer-with-plan | Sonnet | `C:/Programs/constellation-skills-wt/r418-436` | `epic-418/d-436-enumeration-falsification` |
| #464 rename the `Lesson:` field | implementer-with-plan | Sonnet | `C:/Programs/constellation-skills-wt/r418-464` | `epic-418/b-464-lesson-field-rename` |

Launch orders: `.agent-work/epic-418-redux/launch-orders/LO-<issue>.md`.
Isolation gate passed before launch: 4 distinct worktrees, exit 0.

**Held to the wave's second half, deliberately, by file overlap — not forgotten:**
- **#461** (episode-store negative control) — sits in #460's area
- **#465** (reviewer r6-fowler placeholder + CRLF) — touches `checklist_engine.py`, #433's area

## Settled this session — do NOT re-derive

- **Green baseline: `ca0e36a` → 1721 passed, 4 skipped, 643 subtests, exit 0.** The predecessor's
  note carries two other figures (1723/2 and 1764); they are not reconciled and this one governs.
- **The installed corpus was stale and is now SYNCED** (12 skills diverged, 6 in `SKILL.md`,
  including `commander-delegated` and `workbench`). Seven paths still differ and all seven are the
  installer's own transformations — path resolution plus a `python`→`py` rewrite. Verified benign:
  zero non-launcher differences. `py` is Python 3.12.13 and runs corpus scripts fine.
  **`py` is still wrong for pytest** (#454) — that is a separate, still-true rule.
- **The installed Admiral spine is unusable as-is** — its closeout calls `apply_lessons_delta.py`
  and `verify_agent_feedback.py`, both deleted by #447. This spine was built from the repo template.
- **#468 (filed today):** the repo's vendored `verify_iterative_role_artifacts.py` cannot run from
  this repo — its installed-skill guard passes by accident because the repo is named
  `constellation-skills`. **Use the installed copy** at
  `C:/Users/fredc/.claude/skills/constellation-admiral/scripts/`.
- **`verify_worktree_isolation.py` has two modes.** Bare paths = the Admiral's pre-wave gate;
  `--here <path>` = the Commander's in-worktree check and it tests **cwd**. I ran `--here` from the
  main checkout and got four false failures.
- **#447 is CLOSED** with a per-done-condition accounting. Condition 4 was recorded **partial**, not
  done — #460 is that remainder, and it is in this wave.
- **#418's body pointer is corrected** to `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`.
- **#457 — never obey a spine rail naming a spine another agent drives.** With four agents live this
  is now a live hazard, not a theoretical one: the rail attributes a descendant's gate to its
  ancestor, and a productive descendant resets its ancestor's strike counter forever.

_Updated: 2026-08-07T21:45:00Z_
