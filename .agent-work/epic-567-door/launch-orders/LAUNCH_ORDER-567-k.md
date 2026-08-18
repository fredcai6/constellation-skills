# Launch Order: `cmdr-567-k` — one spine per agent — frozen bookends, mutable middle, for every planning role (#634)

Epic **#567** ("the door is the interface"), **wave 3**, lane **K**. Two lanes run: J and K.
You start cold; everything you need is pasted here, not linked.

## Mission

**#634.** A run's plan should be frozen at its bookends and mutable in its middle, and it should
live in **one spine per agent**.

Today every planning role keeps its middle somewhere else:

- A **Commander** authors its work gates at `plan` into a **second file**, `execute.json`, and
  drives them there — outside the door, under a session id it invents.
- An **Admiral** keeps its middle outside the spine entirely: a two-wave, nine-lane epic ran inside
  a single `execute` gate, with its real structure in `ADMIRAL_LOG.md` and `transitions/`.

**This is the one exception epic #567 could not sweep.** The doctrine sweep removed every
agent-facing CLI reference except the ones describing this path, because the path is real and the
door does not reach it.

The human's direction, verbatim:

> "I regret freezing gates, if anything I want to make the gates a little looser so we can step back
> more frequently and update them. there should likely be frozen required gates at the start and
> finish, but what we do in the middle is squishy and is totally reasonable to change as we're
> executing and understanding the problem better"

and on scope:

> "this isn't only a commander thing, admirals also should be able to mutate the middle of their
> plan… let's not over design this for commanders. heck, I wouldn't be mad at a crew updating its
> plan along the way too. it'd probably be good for us to be able to capture 'the plan changed,
> here's how' though"

## Prior-Wave Verdicts (pasted)

**The investigation that produced this issue went wrong three times, and the corrections are the
most useful thing to carry.**

**Wrong once:** the Admiral framed it as *a Commander needs to drive its crew's spine.* The journals
say otherwise — every crew plan is driven under the **crew's own** identity:

```
IMPLEMENTER_PLAN.json  <- 26 entries  constellation/567-e/g1-implement/implementer/attempt-1
IMPLEMENTER_PLAN.json  <- 27 entries  constellation/567-d1-g2-implementer-attempt-1
```

The Commander **populates** the handoff; the crew **drives** it. That part already works.

**Wrong twice:** the Admiral then framed it as a parent/child ownership problem. The human
corrected it — *"the spine is supposed to be one agent's work. if another agent pre populates it,
great, but that parent does not own that work… maybe we say that spines are only mutable by their
owners once they're actually started. before then, whatever, it's just an input."*

**What is actually left** is narrow: a Commander's `execute.json` is **the Commander's own work in a
second file**, driven off-door under a hand-invented id. Two lanes, two formats, invented
independently:

```
execute.json  <- 83 entries  commander-567-d1-execute
execute.json  <- 16 entries  constellation/567-e/execute
```

**Wrong three times:** the Admiral cited `checklist_engine.py:3188` (`append only on survey
checklists`) as the blocker. That governs a **different verb**. `spine_amend` already exists and is
described as *"deliberate, validated re-planning of a GATED checklist under a named authority:
add/drop/rescope pending gates, or retext-check a pending/in-progress gate's check text."* **Gated
plans can already be re-planned.** The roles simply put their middle elsewhere instead.

**And both roles already have the human's shape.** Commander: `init · context · understand · plan ·
execute · reconcile · triage · review · feedback · archive` — frozen bookends around **one** middle
step. Admiral: `init · latitude · execute · closeout` — four steps, **one** middle. The structure is
already right; the file boundary is wrong.

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — **say so in your return** when
you override one.

### Mission-specific

- `decision:every-planning-role` — **settled/human.** Build this for **Admiral, Commander and
  crew**, not for Commanders with a note to generalise later. He said so directly.
  `@grade: settled/human · leans k`
- `decision:frozen-means-frozen` — the bookend steps stay fixed. Only the middle is mutable. A
  design that lets a role rewrite its own opening or closing steps is not what was asked for.
  `@grade: settled/human · leans k`
- `decision:establish-from-child-first` — **`spine_advance --from_child` consumes a child
  checklist's consolidation as evidence, so someone deliberately built a parent/child seam. Read it
  at source and in its tests before proposing to remove or reshape it.** If it exists so a
  *different* agent's plan can feed a parent gate, it survives this change and constrains your
  design. If it exists only to work around gated-can't-grow, it goes with the file boundary. **The
  Admiral does not know which, and your answer changes your own scope.**
  `@grade: guess · leans k · settle: read the verb and its tests`
- `decision:self-hosting-proof` — **settled/doctrine, and sharper here than in wave 1.** This changes
  the rule the Admiral's own live spine runs under — a rule the Admiral exercised today by reopening
  its `execute` step. Before merging: a **read-only** status on the live spine must exit 0, and a
  **mutating** verb must be proven against a **COPY** of a spine, never the live file.
  `@grade: settled/doctrine · leans k`
- `decision:design-it-twice` — #634 is a load-bearing interface change, so generate **N≥2** candidates
  under distinct named constraints before converging. **Convergence is human-only:** return a
  comparison and a recommendation; the Admiral surfaces it. `@grade: settled/doctrine · leans k`
- `decision:plan-change-is-legible` — *"the plan changed, here's how"* must be reconstructable after
  the fact: what was added, dropped or rescoped, when, and why. `spine_amend`'s named authority and
  the append-only `why_trail` are existing scaffolding — prefer using them to inventing a third
  record. `@grade: settled/human · leans k`

### Standing, this epic

- `decision:reduce-complexity` — judge a change by the human's test: **does this reduce work on
  agents by moving it into mechanisms?** `@grade: settled/human`
- `decision:honest-null-is-complete` — a measured negative on the stated question is a complete,
  successful deliverable, reported with the same rigor as a win. `@grade: settled/human`
- `decision:no-issue-filing-mid-run` — **file no issue.** Stage candidates under
  `.agent-work/567-k/triage-candidates/`. His reason: *"we've been ballooning out tracking."*
  `@grade: settled/human`
- `decision:no-doctrine-promotion` — do not promote an observation into `docs/agents/*`. That is
  the human's call. `@grade: settled/project`
- `decision:in-session-hook-observation-is-not-evidence` — hooks execute from the **main checkout**
  regardless of worktree (`CLAUDE_PROJECT_DIR` resolves once at session launch, #269). Validate
  engine, door or hook behaviour in a **fresh process** with explicit paths.
  `@grade: settled/project`
- `decision:map-index-is-admiral-owned` — do not regenerate or hand-edit `map/INDEX.md` (#544).
  Your branch is accepted green **except** `tests/test_code_map.py::MapTreeFreshnessTests`.
  `@grade: settled/doctrine`
- `decision:no-fork-for-design` — helpers are **fresh** agents, never a `fork`. A fork inherits its
  dispatcher's context and believes it *is* the Commander. `@grade: settled/doctrine`
- `decision:pass-model-explicitly` — **pass `--model sonnet` on every `run_crew.py` dispatch you
  make.** `run_crew.py` inherits this host's `settings.json` default (`opus`) when `--model` is
  unset, which cost the previous wave 15 unintended Opus crew sessions, 6 of them abandoned and
  retried. The human ruled Sonnet for all remaining work. **This is the defect lane J is fixing —
  do not rely on the fix while building it.** `@grade: settled/human`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with
the same rigor as a win. Do **not** substitute your own judgement for a measurement your mission
calls for and present the result as measured.

## Inherited Latitude

| Class | Your disposition |
|---|---|
| Implementation choices inside your own files | **yours** |
| The mechanism, and whether `spine_amend` is the seam | **yours** |
| How the plan-change record is expressed | **yours** |
| Convergence between your candidates | **human-only** — return a comparison |
| Changing `run_crew.py` or the installer | **fenced** — lane J |
| Architecture / structural change | **float to the Admiral** |
| Scope change | **float to the Admiral** |
| Issue filing | **ruled: none** |
| Promoting doctrine into `docs/agents/*` | **forbidden** — human's call |
| Anything fitting no class above | **float**, with one line on why |

Float by writing the question into your return **and** ending your turn with it stated plainly.
The Admiral answers and continues you. Asking up is always sanctioned.

## File Ownership

**You are sole writer this wave of:** `scripts/checklist_engine.py`; `scripts/mcp_spine_server.py`; every `*SPINE*.template.json` under `skills/*/templates/`; `specs/`; tests covering those.

**Fenced — the other lane owns it:**

| Path | Owner |
|---|---|
| `scripts/install_constellation.py`; `scripts/run_crew.py`; `skills/admiral/templates/LAUNCH_ORDER.template.md`; `.agent-work/templates/LAUNCH_ORDER.template.md`; tests covering those | lane J |
| `map/INDEX.md` | the Admiral |

Your working-notes file is `.agent-work/567-k/notes-1.md`. Name it exactly that — **never**
`findings-<n>.md`; the harness `Write` tool refuses any basename containing "findings".

## Workspace

- **Spine (yours, provisioned):** `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle/.agent-work/567-k/spine.json`
- **Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
- **Branch:** `feat/567-k-one-spine-mutable-middle` · **Base:** `9b38b9d9`
- **Merge position:** **last.** Rebase on lane J's merged `main` before your final gate.

Your first command is `spine_lease` with `action=claim, claimed_by=commander, worktree=.`.

**Your door is bound to your own spine.** You were launched by `run_crew.py --backend cli --spine`,
which set `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` in your environment and started you
in your own worktree. Drive every gate through the MCP verbs. **If you find yourself reaching for
`checklist_engine.py` on the command line, stop and record it** — this epic exists to remove that
path, and a place where it is still needed is worth more than the workaround.

**Isolation is git-only.** `CLAUDE_PROJECT_DIR` resolves once at session launch, so hook code runs
from the **main checkout** even inside your worktree (#269). Validate in a fresh process.

## Inherited Context

- **The merge gate is the full suite green on Linux**, run in a **clean detached worktree of your
  branch**, never your working copy. *A check that runs against your own working copy is not a check
  on the world.* Windows CI is red on a pre-existing ~122-failure path-casing baseline and is **not**
  the yardstick (#575 deferred).
- **Unset four variables for your suite run:** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT
  -u CREW_SCRATCH_DIR`. A dispatched crew's own `CREW_SCRATCH_DIR` leaks into an assertion built on
  `os.environ` and reds
  `tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
  — a test your change does not touch. Confirmed four independent ways, including on an untouched
  base commit. **Do not "fix" `run_crew.py` to satisfy it**; that is a real regression introduced to
  silence a false one.
- **A headless `claude -p` launched in this worktree inherits `SPINE_*` and the Stop hook.** Strip
  `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT` and `CREW_SCRATCH_DIR` from every helper you launch.
  In the previous wave one lane's probe agent began driving that lane's own spine, and a cold
  subagent read a session id out of a journal and drove a live run under it. Add `< /dev/null` —
  helpers hit `Warning: no stdin data received in 3s` without it.
- **A failing subtest is greppable.** The root `conftest.py` restates each failed subtest as a line
  beginning `FAILED `. Grep for `^FAILED` and trust it.
- **`episodes/` has one write path**, `scripts/apply_episode_delta.py`, always `--store-root
  episodes`. Order is **write → `git add` → suite → commit**. The observation guard cannot tell a
  past-tense verb from an imperative; rephrase rather than growing its exception list.
- **GitHub returns intermittent 503s.** Retry `gh pr create` and `gh pr merge`, and **gate each
  retry on whether the world actually changed**, never on the command's own output.
- **`.agent-work/` is tracked deliberately**, so your work area, return and triage candidates reach
  `main` with your branch.

## Pre-empted Steps

- **Work-area stand-up is done.** Worktree, `.agent-work/567-k/` and `spine.json` were provisioned
  by the Admiral per `skills/_shared/stand-up-work-area.md`. Your `init` step means one thing: claim
  the lease.
- **The `--here` arrival check is retired** (#610). Isolation was gated across both worktrees before
  dispatch.
- **The wave-3 transition is authored and verified** — `transitions/w3/`, `admiral-prelaunch` exit 0.
  You deliver; you do not replan the wave.

## Local Unknowns

Named so you do not mistake them for settled:

- **What `spine_advance --from_child` was built for.** Your first unknown, and it changes your scope.
- Whether gated spines carry invariants — the `why_trail`, the trip ledger, how postconditions are
  evaluated across a grown step — that appending to the middle would break. The `append only on
  survey checklists` refusal may be protecting something the error message does not name.
- Whether the Admiral spine's single `execute` gate should grow gates per wave, or whether an epic's
  waves are a different shape from a Commander's work gates.
- Whether "only the owner mutates once started" needs enforcement, given ownership is currently a
  session-id string the caller supplies — the same string a cold subagent read out of a journal and
  reused (#632).

## Budget

- **Model tier (required):** **Opus** for you.
- **Crew model tier (required):** **Sonnet** for every crew you dispatch — pass `--model sonnet`
  explicitly. This slot exists because the previous wave had none, and 15 crew sessions silently ran
  a tier above their lane.
- **Compute/time:** One extended session. This is the epic's remaining deliverable and the design is unsettled; the comparison is worth more of your budget than a fast implementation.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is needed, budget is
crossed, the evidence is impossible to obtain, or you need context this order does not cover.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap
(150K on a 1M-window model), not a share of your window, so you can be over it on turn one having
done no work. The engine refuses only `start` and `reopen`, and only until a refresh-request exists.
The legal sequence is **attach the refresh-request, then `start`, then do the work.**

Do not read a HARD advisory as an instruction to `advance --why` and hand off on turn one. A fresh
agent that closes its gate before doing the gate's work produces an infinite handoff chain. **The
previous wave's D1 lane refused exactly that and left its gate pending with a refresh-request
attached — copy that behaviour.** Hand off when you have spent the context, not when you inherit
the reading.

**Do not end your turn with an engine gate open.** The Stop hook refuses it and outranks the
context-trip advisory (#595). The sanctioned exit is `spine_halt` with `action=block`, naming what
you cannot satisfy and the next action.

## Return Shape

Write your result to **`.agent-work/epic-567-door/results/lane-k-RETURN.md`** — that
exact path, in your own worktree, committed on your branch. Write it **before** going idle.

Include:

1. **Verdict** — delivered, or an evidenced honest null.
2. **What `from_child` is for** — read at source, stated plainly, with what it means for your design.
3. **The design-it-twice comparison** — N≥2 candidates under named constraints, each attacking
   itself, and your recommendation. **Do not converge; the human does.**
4. **The mechanism**, if you built one: how a role's authored gates land in its own spine, and how
   the bookends stay frozen while the middle moves.
5. **The self-hosting proof** — read-only status on the live spine exiting 0, and a mutating verb
   against a **copy**, with commands and output.
6. **Suite result** — full suite on Linux in a clean detached worktree of your branch, with the
   tally, the `^FAILED` grep, and the commit sha. `MapTreeFreshnessTests` may fail; nothing else may.
7. **Touched paths** — every file, and anything you wanted to touch but did not because it is fenced.
8. **Triage candidates** — as files under `.agent-work/567-k/triage-candidates/`, listed. None filed.
9. **Workflow feedback** — what helped, what got in the way, and **your own mistakes**. The previous
   wave's most useful returns were the ones that indicted their own author.
10. **PR** — opened against `main` from `feat/567-k-one-spine-mutable-middle`, with the number and head sha.
