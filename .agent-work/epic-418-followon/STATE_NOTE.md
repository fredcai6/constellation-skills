# Crash-resume state note — epic-418-followon (Admiral)

## ACTIVE DISPATCH (rewritten 2026-08-12 before the C3 Commander launch)

- **step:** execute (in-progress) · MERGED+PUSHED through `293b7721`: M1, M2, M3, N1, A (`9a056105`), B (`90b39e2b`), D1 (`3c0fc7d2`), E1 (`094f573a`), C1 (`0ab7ecab`), G1 (`2a22c00a`), C2 (`e4c80f85`) · wave `w7-lifecycle` launching **C3 as a Commander**
- **slug:** `epic-559/c3-lifecycle` · branch of the same name off `main`@`293b7721` · worktree `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
- **next command:** poll `/home/tommy/projects/constellation-skills-wt/c3-lifecycle/.agent-work/epic-559/c3-lifecycle/COMMANDER_RETURN.md` **inside the turn**; approve its gate plan when it floats (`plan.c3` pre-empted to the Admiral); cold-review; merge locally on green; **then dispatch R1 (#559, CLI residue) off the merged base** — C3 blocks R1 by design so R1 also cleans whatever C3 adds
- **pid:** see `.agent-work/epic-418-followon/c3-lifecycle.pid`
- **expected artifact:** `COMMANDER_RETURN.md` carrying a verdict, a spine opened through the door in one call and archived by its own closing advance, and the honest answer to whether a generated dispatch is data the engine consults or prose a crew retypes

## What C3 is, in one line

One door call opens a spine **and** its worktree; the closing advance archives the work area and says
"ready to PR"; and the dispatch itself moves into the spec so parent and model are emitted rather
than remembered. Full spec: `.agent-work/epic-418-followon/context/lifecycle-spec.md`, copied into
the worktree.

## The ordering hazard a successor must not re-derive

Closeout moves the work area that contains the spine driving the closeout. Required order, fixed:
satisfy postconditions → **final `advance`** → **`release`** the lease → move the work area with the
spine file **last** → commit → report. Release before the closing advance and the journal carries
entries after the release, failing the terminal provenance check.

## Wave 7 is two issues, deliberately sequenced

- **C3** (Commander, Opus; crews Sonnet) — the lifecycle. Running now.
- **R1** (#559, implementer-with-plan, Sonnet) — the CLI residue: **15 `CLI fallback` clauses across
  11 files and 9 `<engine>` tokens across 5 files** on `293b7721`. Two clauses
  (`skills/workbench/SKILL.md:37`, `skills/workbench/references/checklist-engine.md:5`) call the CLI
  *"the only path for an in-session dispatched crew member"*, which wave 5 disproved by dispatching
  one. **Runs after C3 merges**, so it also cleans anything C3 introduces. `tests/test_mcp_adoption.py`
  and `tests/data/store_mentions.approved.txt` pin the exact removed text and must move with it.

**A successor must not read the surviving `<engine>` tokens as sanctioned.** C3's own spine carries
them in its `init` and `archive` imperatives; its launch order tells it to use the door instead.

## The human's rulings, current as of 2026-08-11

1. **Agents must not know about the CLI. Period.** *"anything that we want to do for the spine needs
   to be accessible via mcp ... anything that we can only do via the cli is a defect."*
2. **Hardcoding the interpreter for this host is allowed**, provided every hardcode is recorded on
   **#539**. Three sites recorded, including the installer's rewrite of the tracked `.mcp.json`.
3. **Beliefs, concerns and open questions get gate slots.** *"there should be plenty of room into a
   template for beliefs, highlighting concerns, posing open questions ... hand off content should
   still be possible."*
4. **Judgment goes up.** *"as a general rule, judgement should be highlighted and brought to the
   higher level. greater claim requires greater review."*
5. **Crews fail up, one rung at a time.** Shipped as E1: `blocked` is a recorded outcome and
   `SPINE_PARENT` is bound. Measured: a headless crew **cannot** reach a parent by descriptive name,
   so nothing may depend on messaging.
6. **Tool consolidation is deferred** to a round at the end. *"we don't have to be perfect now."*
7. **Prefer Sonnet crews.** The Commander runs on Opus; its crews run on Sonnet. The escalation is
   the Admiral's and is logged.
8. **Don't narrate mistake lists back to the human.**

## Two Admiral rulings this wave, which C2 is built against

- **A placeholder is a slot in a template and a fault in an instance.** B's allowlist and C1's lint
  disagreed; both were right about different objects. The generator refuses an instance carrying one.
  This retires B's two-item allowlist, which had no test on its own growth.
- **A gate with no checkable postcondition must state that it is qualitative.** Nine of twelve shipped
  templates carry the silent default on their context gate and none states the choice.

Both are wave-level design rulings inside delegated latitude. The prelaunch verifier correctly refused
an attempt to write them into `fixed_decisions`, which would have been a fixed-boundary change
requiring `applicable=false`; they live in the wave's exit criteria and C2's hard constraints instead.

## Root cause a successor must not re-derive

**Nine of ten dispatch scripts in this epic never set `SPINE_FILE`.** Every crew that "reached for
the CLI" had a door bound to a wave-1 scratch demo spine — the CLI was the only path to its own
spine. Those crews were correct; the environment was broken. This corrects an earlier claim that
binding is "necessary and not sufficient"; that claim rested on crews having a working door, and they
did not. Owed as an episode at closeout.

## Operating facts that have already cost time once each

- **Run crew commands FROM THE WORKTREE.** `run_crew.py` never sets the child's cwd, and
  `recover_crews.py` reports a false all-clear from the main checkout.
- **`.claude/settings.local.json` in each worktree must be the 15-allow file**, not a copy of the
  main checkout's (`permissions: null` kills a crew on arrival).
- **Never `git add -A`.** `.agent-work/` is tracked here.
- **Run the suite as `python -m pytest`**, not `python3`.
- **Never collide two crews in one worktree.**
- **The installer rewrites the tracked `.mcp.json`** from `python3` to a probed `py` every run. Revert
  it (`git checkout .mcp.json`) after every install. Recorded on #539.
- **`verify_iterative_role_artifacts.py` writes CURRENT_TRUTH.md and WAVE_REVIEW.md into the
  transition directory only.** The top-level copies are written by nothing and go stale; copy them up
  by hand after each verified transition.

## Closeout still owed

Episodes (including the nine-of-ten binding root cause, the four defective Admiral-authored checks,
and the Commander-vs-implementer right-sizing failure), cartographer reconcile, harvest each
worktree's `CONSTELLATION_FEEDBACK.md` **before** `git worktree remove`, archive the ADMIRAL_LOG,
user acceptance, release the lease last. The Admiral lease is
`717403d3-70be-436f-bc06-ce9ac3e34e05`.
