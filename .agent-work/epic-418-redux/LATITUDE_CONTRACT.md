# Latitude Contract: `epic-418-redux`

**STATUS: CONFIRMED by Tommy, 2026-08-07.** The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

Relaunch of epic #418 after waves 0 and 1 merged. Predecessor contract (`epic-418`, confirmed
2026-08-05) expired by its own terms at the wave-1 checkpoint. Archived at
`.agent-work/archive/2026-08-07-epic-418-waves-0-1/epic-418/LATITUDE_CONTRACT.md`.

## What changed since the last contract, and why this one is looser

The spec of record was rewritten and re-confirmed on 2026-08-07 specifically to stop
pre-committing to mechanism. It says so directly:

> **What the Admiral is not given:** a wave plan, a per-issue dispatch script, or a prescribed
> interface for any section. The order above plus each section's fixed boundaries is the whole
> course. Wave composition is the Admiral's call under the standing latitude contract, and the
> iterative-planning flow is how it revises between waves.

Three of the original spec's "by construction" claims were falsified by this epic's own
execution — each caught by a Commander departing from the spec and saying so. So departure is
the expected mode, not the exception. This contract is written to match that.

## Standing rulings carried forward

**Scope discipline (Tommy, 2026-08-05)** — still binding, still a mandatory clause in every
launch order:

> *"this is not a final step in a process. lets do what we need to do and no more. this doesn't
> mean be sloppy, but i am explicitly allowing you to not chase down every corner case. make the
> thing that needs to work, and if you have any concerns, just note it locally in comments and
> pass it up the chain"*

**Appetite (Tommy, 2026-08-07)** — rigor scales with cost-to-undo, not uniformly. Cheap to
reverse, move fast. A claim about what happened still brings its evidence. This does **not**
license unevidenced claims, silent scope cuts, or checks that cannot register their own failure.

**Standing obligation (spec)** — each workstream retires the findings it subsumes, measured
against a candidate set it declares **before** it starts, drawn from existing theme labels.
Closing 0 of 11 is a visible number; declining a candidate is fine, declining it silently is not.

**The retired learning playbook (`docs/agents/ORCHESTRATOR_CONTEXT.md`)** — `LESSONS.md` and
`AGENT_FEEDBACK.md` are retired. `episodes/` replaces both. An episode is a record, never read
back as a rule. Promoting anything to `docs/agents/*` is a human's call. No successor playbook.

## Epic Intent

Finish epic #418's remaining course. Execution order is a **dependency** order, not a schedule —
a Commander that finds a link is not real should say so rather than honour it.

| # | Section | Issues | Why here |
|---|---|---|---|
| 1 | **B extended** — the agent can see the whole gate | #433 + carried #460 #461 #464 #465 | everything reads through the projection; `directives` is inert until it renders |
| 2 | **A2** — trip semantics | *needs cutting — no issue exists yet* | F cannot type a verb whose meaning is unsettled |
| 3 | **F** — MCP front door | #424 | verbs go where verbs belong, before content is written around them |
| 4 | **C** — relocation | #421 | relocate against a settled **verb contract** |
| 5 | **E** — backlog re-cut | #423 | runs on what *survives* the redux, not on today's backlog |

Off-chain, runnable at any point, each with its own success criterion:

| Item | Done when |
|---|---|
| **#452** multi-spine attribution | a session holding several spines produces an attributed reading, **or** it is recorded as out of reach with the reason — an honest null is permitted here |
| **#458** ship the gauge writer (workstream R) | a fresh clone produces a reading with no machine-local config |
| **#436** D's falsification debt | the enumeration check is observed refusing a genuinely new worktree-entering template |

## Success Shape

The epic's five done-conditions as the revised spec marks them: #1 revised (readings keep
arriving on a *shipped* config), #2 unchanged and not yet met (B), #3 substantially met (D,
#436 gap stands), #4 **retired** and replaced by the standing obligation, #5 untouched (F).

**A measured negative is a complete, successful deliverable.** An honest null states what was
tested and what was not. Falsification triggers rework of that element — never silent
continuation, never abandonment.

## Checkpoint Protocol

**Run ahead through wave boundaries; report, don't block.** At each boundary I write the replan
transition, present a short plain-English summary of what landed and what I intend next, and
proceed. I stop and wait only for a **surfaced** decision class below, or on contract expiry.

Rationale: the spec hands wave composition to the Admiral and gives the iterative-planning flow
as the revision mechanism. A stop-and-wait checkpoint at every boundary would put the decision
back where the spec just took it from. You can flip this to stop-and-wait at any time.

## Decision Classes

| Class | Disposition |
|---|---|
| Wave composition, width, and re-planning between waves | **delegated** — this is the point of the relaunch |
| Departing from the spec's stated execution order or method | **delegated**, logged as a RULING naming what was found untrue — the spec invites this |
| Architecture / structural change | delegated *(surfaced if it changes a load-bearing interface shape: the MCP tool surface, the gauge binding key, the gate schema)* |
| Scope change (issue added / dropped / re-scoped) | **surfaced** |
| Merge to main | delegated *(green + reviewed only)* |
| Issue filing / commenting | delegated |
| **Issue closing** | **surfaced** |
| **Promoting an observation into `docs/agents/*` doctrine** | **surfaced — always.** ORCHESTRATOR_CONTEXT makes this a human's call by name |
| Fix-now triage (bounded fix applied immediately) | delegated |
| Spend / budget / model tier | delegated *(within the table below; no Fable at any tier)* |
| Production defaults / user-visible behavior | **surfaced** |
| **A workstream cannot meet its stated obligation** | **surfaced — always** (the #308 failure shape) |
| Threshold regrade on a `guess`/`placeholder` | delegated: run the `settle:` experiment, log the ruling, regrade. **Surfaced exception:** C's tranche boundary, which the spec names as costly to revert |
| Design-it-twice convergence | **surfaced — always** (convergence is human-only) |
| **Out-of-taxonomy** | **always escalates**, with one line on why it fit no class |

## Permission Prerequisites — every row PRE-CLEARED by Tommy, 2026-08-07

A `delegated` disposition settles who decides, not what the harness permission classifier lets
through. Grounded in **#145**: leaving a mission's core mechanics unlisted vetoes the mission at
execute time, and the veto only surfaces after dispatch.

| Delegated class | External actions implied | Pre-clearance asked |
|---|---|---|
| **Subagent dispatch, all tiers** | this Admiral dispatching Commanders; Commanders dispatching crew; crew dispatching cold critic/tracer agents | **pre-clear** (carried from 2026-08-05) |
| Issue filing / commenting | `gh issue create`, `gh issue comment`, `gh issue edit` | **pre-clear** — grounded: #145, and the `gh issue create` gap has now recurred four times |
| Merge to main | `gh pr create`, `gh pr checks`, `gh pr merge`, `git push` to `epic-418/*` | **pre-clear** for green + reviewed |
| **Install sync** | re-running `install_constellation.py`, which **writes your global `~/.claude/skills/`** | **PRE-CLEARED** — 12 skills diverge, 6 in SKILL.md, incl. `commander-delegated` and `workbench` |
| **B extended #433/#461/#465** | editing `checklist_engine.py`, spine templates, tests; full suite | **pre-clear** |
| **#460 episode-store surgery** | rewriting records under `episodes/` via `apply_episode_delta.py` | **pre-clear the mechanics**; any promotion to `docs/agents/*` still surfaces |
| **#436 negative test** | deliberate invariant breakage in a scratch worktree | **pre-clear** — reverted by the same issue that induces it |
| **#452 / #458 governor work** | reading `~/.claude/projects/**` transcripts; mutating the live gauge binding store; writing whatever ships the hook | **pre-clear**, dry-run and before-state recorded first |
| **F #424 door mechanics** | writing project-scope `.mcp.json`; starting an MCP server process; per-dispatch config generation | **pre-clear**. `settings.json` is never touched — that boundary is in the spec |
| **C #421 measurement mechanics** | cold-agent tracer dispatches; corpus surgery on `COMMANDER_SPINE.template.json` and `commander-core.md`; re-running the installer | **pre-clear** — this is the mission's core loop (#145) |
| Fix-now triage | full test suite, local commits | **pre-clear** |

Test suite invocation, settled and not to be re-derived (#454):
`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`**, and `FORCE_COLOR=3`
produces false reds for `python` too.

## Float-Up Routing

A Commander floats a **decision**: I adjudicate inside delegated classes and log a RULING;
surfaced classes and out-of-taxonomy go to Tommy. A Commander floats a **context query**: I
answer from epic knowledge and continue it. A Commander files a **refresh-request**: I relaunch
a fresh Commander into the same worktree and spine file, cold-starting from `current` alone.

## Comms

Plain English by default; technical depth on demand. No invented project dialect in anything
user-facing. Decision asks in plain text, never question dialogs.

## Budget / Model Parameters

No Fable at any tier; explicit model on every dispatch.

| Work | Dispatch shape | Tier |
|---|---|---|
| #433 B-extended core | full Commander | Opus |
| #460 episode records read as prescriptions | full Commander | Opus |
| #461, #464, #465 carried findings | implementer-with-plan (small, bounded — the right-size rule) | Sonnet |
| #436 falsification debt | implementer-with-plan | Sonnet |
| A2 (once cut), F #424, C #421 | full Commander | Opus |
| E #423 | Admiral + Tommy | — |

If a usage-limit reset is near, the next wave waits past the reset rather than launching into it.

## Pre-Rulings

- `decision:honest-null` — a measured negative is a complete, successful deliverable; every
  verdict states what was tested and what was not. @grade: settled/inherited
- `decision:departure-is-the-mode` — a Commander that finds a spec link or specific untrue
  applies the governing rule, says so in its return, and proceeds. Five such departures last
  epic, all ratified. @grade: settled/human
- `decision:a2-cut-at-its-turn` — A2 has no issue yet. I cut it when the chain reaches it, not
  now, so it is cut against what B extended actually leaves behind. @grade: guess · leans A2
- `decision:spine-rail-misattribution` — **never obey a rail naming a spine another agent
  drives** (#457, ten firings last session; the three-strike escape hatch cannot save you
  because a productive descendant resets its ancestor's strikes forever). @grade: settled/observed
- `decision:drive-from-the-repo-copy` — under dogfooding, the repo's `skills/` is the governing
  copy, not the installed one; instantiate spines from the repo template with
  `--skill-dir C:/Programs/constellation-skills`. @grade: settled/observed this run

## Expiry

The **wave-2 boundary** (after the B-extended wave's PRs merge), or **72 hours**, whichever
comes first. Crossing it forces a contract-refresh decision before further dispatch.

## Confirmation

2026-08-07 — **CONFIRMED by Tommy in session**: *"yup, agree all. you can commit as needed to keep
things clean."* Recorded as `user-decision` evidence on the spine's `latitude` step, and as the
joint-understanding sign-off in `INTERROGATION_RECORD.json` (`verify_interrogation.py` exits 0).

He confirmed all five open decisions as drafted — install sync before wave 1, the wave-1
composition, run-ahead checkpoints, the expiry, and both surfaced tracker actions (#447 close,
#418 pointer fix) — and added a sixth grant:

- **Commit authority.** The Admiral may commit directly to `main` for workbench hygiene without
  asking each time. This matches `docs/agents/ORCHESTRATOR_CONTEXT.md` ("Local commits: allowed").
  **Unchanged:** pushes and merges to `main` still require explicit approval per that same overlay,
  and merge-to-main remains delegated only for green + reviewed PRs.
