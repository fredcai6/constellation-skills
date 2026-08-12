# Crash-resume state note — epic-418-followon (Admiral)

## ACTIVE DISPATCH (rewritten 2026-08-11 before the C2 Commander launch)

- **step:** execute (in-progress) · MERGED+PUSHED through `0ab7ecab`: M1, M2, M3, N1, A (`9a056105`), B (`90b39e2b`), D1 (`3c0fc7d2`), E1 (`094f573a`), C1 (`0ab7ecab`) · wave `w6-generator` launching **C2 as a Commander**
- **slug:** `epic-559/c2-generate-the-spine` · branch of the same name off `main`@`0ab7ecab` · worktree `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`
- **next command:** poll `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine/.agent-work/epic-559/c2-generate-the-spine/COMMANDER_RETURN.md` **inside the turn**; approve the Commander's gate plan when it floats it (`plan.c3` is pre-empted to the Admiral); cold-review its result; merge locally on green
- **pid:** see `.agent-work/epic-418-followon/c2-generate-the-spine.pid`
- **expected artifact:** `COMMANDER_RETURN.md` carrying a verdict, the generator's refusal control shown two-sided, and the honest answer to whether the role spec still makes its author type a shell command

## What this dispatch is testing, beyond its own task

**This is the first Commander dispatched in this epic.** Every prior workstream was an
implementer-with-plan whose spine the Admiral hand-authored. The human asked why, directly, and the
answer was that right-sizing was correct on each first pass and never revisited as three of the six
grew into multi-round workstreams.

So this run measures two things at once: whether the generator can be built, and whether the
**Commander path itself works** after wave 5's changes. Two known rough edges, recorded rather than
hidden:

- The Commander template's `g1-implement` gate could not fail until B fixed it on 2026-08-11.
- `child_checklist` is `null` on all four gates of `EXECUTE_PLAN.template.json`, and `--from-child`
  appears zero times under `skills/commander/`, so the parent-child link is hand-carried rather than
  engine-verified.

If the Commander path fails here, that is a finding of the same weight as the generator itself. Do
not rescue it by taking the work back in-session — record what broke.

## The Commander's own spine carries four `<engine>` tokens

`.agent-work/epic-559/c2-generate-the-spine/spine.json`, instantiated from
`COMMANDER_SPINE.template.json`, still has four unresolvable `<engine>` tokens in the `init` and
`archive` imperatives, instructing the CLI. Wave 5 removed the token from crew-facing skills and left
it in the orchestrator tier: `COMMANDER_SPINE`, `ADMIRAL_SPINE`, `EXPLORER_SPINE`, and
`commander-core.md`. The launch order tells the Commander to ignore them and use the door, and names
fixing them as in-scope-if-it-wants. **A successor must not read those tokens as sanctioned.**

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
