# Launch order — C3: the work lifecycle is one thing, and it is currently three

**Work id:** `epic-559/c3-lifecycle` · **Role:** Commander · **Model:** Opus (your crews: Sonnet)
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (branch `epic-559/c3-lifecycle`, base `293b7721` = current `main`)
**Spine:** `.agent-work/epic-559/c3-lifecycle/execute.json` — bound to you at launch, already instantiated
**Parent:** the Admiral, `admiral-epic-418-followon`. You are the reachable tier for your crews; I am yours.
**Deliverable:** `.agent-work/epic-559/c3-lifecycle/COMMANDER_RETURN.md`

## The mission in one sentence

An agent creates work the same way it drives work — through the door, in one call — and the
closing advance puts the work away and says it is ready to PR.

## Why now, measured rather than asserted

**Nothing in this corpus provisions a worktree.** `grep -rl "worktree add" scripts/ skills/` returns
five files: two after-the-fact verifiers (`verify_worktree_isolation.py`,
`verify_worktree_precondition_coverage.py`) and three paragraphs of prose
(`LAUNCH_ORDER.template.md`, `fleet-doctrine.md`, `_shared/windows.md`). Two checks and three
paragraphs. **The act itself is unautomated**, so it is typed by hand every time, and the spine is
then created by a second, unrelated command. Seven worktrees were provisioned that way in wave 5
alone, and this launch order was written after I provisioned an eighth by hand and instantiated your
spine with a third command.

**Because creation is manual, close has to rediscover what creation did**: which worktree, which
branch, and where `.agent-work/` actually landed. That last one is genuinely hard.
`durable_root()` (`scripts/agent_work_root.py:110`) returns the **main** checkout root for a linked
worktree — **except** while an Admiral epic lease is held, when it deliberately returns the
**worktree** root instead, because the main checkout is fenced read-only. The same path resolves to
two different places depending on run state, and the close step has to know which. Bind creation to
the spine and none of that needs discovering: the spine records where it was opened, and close reads
it.

**The human's directive, verbatim (2026-08-11):**

> *"we should mechanise worktree management at the start and end. worktrees and spines should be
> completely connected, there's no reason why those should be spawned separately. also the archiving
> step usually requires a little bit of a shell game, especially since the last step involves closing
> out the spine. I think that spine close out is where we can automate moving everything to archive
> and the last step will say 'we're good to PR!' effectively"*

**And the standing ruling that makes the door mandatory, verbatim:**

> *"anything that we want to do for the spine needs to be accessible via mcp. the agents should not
> know about the cli. period. anything that we can only do via the cli is a defect."*

`scripts/generate_spine.py` shipped last wave and is reachable only from a shell. By that ruling it
is a defect today.

## The three pieces

### 1. Open — one call creates the spine and its worktree

One operation takes a work id and a spec and produces: the branch, the worktree, the scaffolded work
area, the spine compiled into it, and the environment a crew binds to (`SPINE_FILE`,
`SPINE_SESSION`, `SPINE_PARENT`). It **verifies its own result** with
`scripts/verify_worktree_isolation.py` rather than trusting that `git` returned 0.

Required properties:

- **Refuse rather than half-succeed.** A worktree without a spine, or a spine without a worktree, is
  the state that produces every mismatch this epic has chased. Roll back on failure.
- **Record where it opened.** The spine carries its own worktree path and branch, so close needs no
  archaeology and `durable_root`'s two-answer behaviour stops being close's problem.
- **Never silently reuse a worktree another crew is in.** *"Never two crews in one worktree"* is
  prose in five places and enforced nowhere. Refuse with a legible reason.
- **Reachable through the door.** This is the piece that makes the generator reachable at all.

There is a chicken-and-egg here you should name in your plan rather than trip over: the door server
reads `SPINE_FILE` **at import time** and raises `KeyError` without it (`scripts/mcp_spine_server.py`).
A tool whose job is to create the spine cannot presuppose a bound spine. Your spine was instantiated
by me and bound with `--spine` for exactly this reason. Whether the open tool lives on the same
server, on a differently-bound instance, or somewhere else is your design call — but say how you
solved it, because it is the reason this could not simply have been added to C2.

### 2. Close — the terminal advance archives, and says it is ready

When the closeout gate advances and the lease releases, the same operation moves
`.agent-work/<work-id>/` to `.agent-work/archive/<work-id>/`, stages **by name**, commits the move,
and prints a readiness verdict naming the branch, the commit, and what remains: **"ready to PR."**

**The ordering hazard, which any implementation must sequence around.** Closeout moves the work area
that contains the spine driving the closeout. The spine file, its `.journal`, and the lease all live
under `.agent-work/<work-id>/`. Move that directory naively and the engine loses the file it is
mid-operation on. The required order is fixed and is **not** your latitude:

1. satisfy the closeout gate's postconditions
2. **final `advance`** on the closeout gate — this is what marks the spine done
3. **`release`** the lease — after the closing advance, never before, or the journal carries entries
   after the release and the terminal provenance check fails
4. **then** move the work area, spine file **last**
5. commit the move
6. report readiness

Steps 2 and 3 are already doctrine and already get fumbled. Steps 4–6 are what you mechanize.

**What close does NOT do, deliberately:**

- **It does not open the PR.** Outward-facing acts stay explicit.
- **It does not remove the worktree.** Deleting a directory is not something a terminal advance does
  as a side effect. `git worktree remove` stays a separate, named step.
- **It does not decide the work was good.** Terminal means driven to the end, not approved.

One measurement that simplifies this. The closeout **harvest** step exists to rescue a worktree-local
`CONSTELLATION_FEEDBACK.md` before `git worktree remove` destroys it. Measured on 2026-08-11 across
all 20 standing worktrees: **not one carries an untracked export.** Every crew in this epic wrote its
feedback into a committed result artifact. A mechanized close does not need to guess what to rescue —
it created the work area, so archiving all of it is correct whether or not anything was exported.

### 3. The dispatch is emitted, not remembered

Last wave, six sub-crews were dispatched naming the Admiral as parent rather than the dispatching
Commander, and none carried an explicit `--model`. **Both instructions were in the launch order**,
and one of them appeared nine more times in the Commander's own frozen `execute.json`. The mechanisms
exist, work, and are documented. `parent` reaches the registry only from `args.parent`
(`run_crew.py:1629` → `874`) with no environment fallback, and `_crew_door_env`'s docstring states the
rule directly: a dispatching crew's own `SPINE_PARENT` *"names the grandparent, not the dispatcher."*
The guard works. The human's read of the remedy, verbatim:

> *"the regressions are disappointing, that's literally point of having a template, once it's there
> it takes effort to remove, not effort to remember"*

So: **a spec declares the crews a gate dispatches, and the generator emits the dispatch with parent
and model already in it.** Removing them then requires editing a committed file and shows up in a
diff. Forgetting them stops being a possible failure mode. A declared dispatch missing either is
refused at generation, the same way the generator already refuses a check that cannot fail.

The open uncertainty, and I want your answer in the plan: **can a generated dispatch be data the
engine consults, or only an imperative a crew must retype?** If it renders as prose a crew must
retype, the defect has moved rather than gone, and I would rather know that at plan time.

## Carried findings — yours to fix, both small

- **`not_yet_written` is read with bare truthiness.** `cond.get("not_yet_written")` in
  `generate_spine.py` means a TOML string `"false"` is truthy and misread as a declaration. C2's crew
  found this in its own new code, named it, and argued out of scope; its cold reviewer judged it
  acceptable-not-blocking. It is a footgun on a field that exists to make a check *not* run. Add the
  `isinstance` guard and a VIOLATING fixture.
- **`DESIGN_NOTE.md` §4, §7 and §10 are stale** against shipped behaviour. Reconcile them to what the
  code does, or delete the stale claims. The note is the generator's frozen contract and a wrong
  contract is worse than none.

## Hard constraints — no-gos

- **`checklist_engine.py`'s on-disk format is not changed.** The door and the generator emit what the
  engine already reads.
- **The close ordering above is fixed.** It is not a design choice.
- **Close archives and reports. It never opens a PR and never removes a worktree.**
- **Stage by name.** `.agent-work/` is tracked in this repo. **Never `git add -A`.**
- **`settings.json`, `.mcp.json` and `docs/agents/*` untouched.** The harness refuses `Edit`/`Write`
  on `.mcp.json` for headless crews and **that guard is deliberate** — an agent must not silently
  expand its own MCP-server trust. A crew must not route around a permission refusal with a `Bash`
  write; if it needs something there, it blocks and asks you, and you ask me.
- **`skills/**` untouched.** The CLI residue cleanup is R1's exclusively and runs after you merge; a
  second writer would collide with you. If you find a `skills/` file that must change for your work,
  float it — do not take it.
- **Do not run `scripts/install_constellation.py`.** It rewrites the tracked `.mcp.json` interpreter
  (known defect, #539).
- **No merge or push to `main`.**
- **Never two crews in one worktree.** You are enforcing this in code; do not violate it while doing
  so.

## Pre-rulings — settled, so you do not have to ask

- **`init` is done.** Your work area is scaffolded and your spine is instantiated and bound. Attest
  and move.
- **`triage` files nothing.** No GitHub issues are cut this wave. A finding you cannot fix is recorded
  in your return and I file it at epic closeout, per the human's ruling. This is not permission to
  drop findings — it is permission to stop asking about the filing.
- **`review` escalates to me, not to a human.** I am your reachable tier for every decision your
  launch order does not settle.
- **Your crews run on Sonnet** (`decision:sonnet-crews`, `settled/human`, verbatim: *"prefer sonnet
  crews"*). Escalate one to Opus only after a Sonnet crew has failed the same task once, and say why.
- **Pass `--parent` naming your own session** on every crew you dispatch — not mine. You are the tier
  that briefed them, and the human's ruling is *"crew should fail up ... one rung at a time."*
- **Pass `--model` explicitly** on every dispatch. As of `2a22c00a` the registry finally records it,
  so this is now checkable after the fact — and I will check.
- **A greater claim requires greater review** (`settled/human`). Judgment is carried up, not buried
  in a gate nobody reads.
- **A crew that cannot satisfy a check blocks.** `spine_halt block`, naming its parent, and returns.
  Never a waive — the door denies a crew's waive on `spine_evidence` anyway, by a `PreToolUse` hook
  `run_crew.py` emits for every spawned crew.

## What I want in the plan you float

1. **How you solved the chicken-and-egg** — a tool that creates a spine cannot presuppose a bound one.
2. **Where the worktree record lives** — inside the spine the engine reads, or beside it — given that
   the engine's on-disk format is frozen and the engine must still load an archived spine afterward.
3. **Your answer on the dispatch**: data the engine consults, or an imperative a crew retypes.
4. **Whether open and close are one tool or two**, and why.

## The review standard this wave inherits

C2's branch was reviewed five times. The first four each ran real commands and each answered its own
questions correctly, and each missed something different: a field that was never quoted (invisible
because **absent**), a stale session id present on nine of nine gates (invisible because
**ubiquitous**), that same id written into a review's own evidence line as proof of completeness, and
a divergence one reviewer saw, described accurately, and then scoped away.

One sentence: **a review establishes that a mechanism operates and does not ask whether the value it
carries is right.** Absence and ubiquity both read as correct.

The fifth review broke the pattern by treating its own green results as questions, and found nine
stale session ids nobody had looked for. Carry that into every reviewer handoff you write: **for
every check, ask two questions — does this mechanism work, and is the value it carries correct?**

And a guard needs a violating case. The repo's pattern is
`tests/test_mcp_adoption.py::_cli_only_verb_violations` — VIOLATING / INNOCENT /
ACCEPTED_FALSE_ALARM. A test that exercises only the happy path measures the mechanism, not the
boundary.

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`. Unsetting the three spine variables matters: `mcp_spine_server.py` reads
`SPINE_FILE` at import time and raises `KeyError` without it. **Baseline on your base commit: 2824
passed, 3 skipped, 1121 subtests.**

The corpus sweep is a second baseline: `python scripts/validate_spine.py --sweep --root .` reports
exactly **23** fault lines. Any change to that number means a shipped template moved, which is a
no-go this wave. Check it before you return.

If you add modules, regenerate the code map: `python -m scripts.code_map build`. Never hand-edit
`map/INDEX.md`.

## Drive your own work through the door

Your dispatch binds `SPINE_FILE`/`SPINE_SESSION` and names your parent in `SPINE_PARENT`. Use
`mcp__spine__*`, found via `ToolSearch`. Do not use the engine CLI — you are building the reason it
should not exist.

## Honest null

A measured negative is a complete deliverable. If a piece of this turns out to be the wrong shape,
say so with the measurement that showed it and return. I would rather have three of these done
properly and one refuted than four half-built.

## Stop conditions

- A hard constraint above would have to be violated to proceed.
- The engine's on-disk format would have to change.
- A crew blocks twice on the same check.
- Your base moves under you (I will not rebase you mid-flight; if `main` moves I will stop and
  relaunch you rather than steer).

Write `COMMANDER_RETURN.md` including its **Workflow Feedback** section before ending your turn —
that write is the delivery.
