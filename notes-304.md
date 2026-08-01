# notes-304 — Commander map-input contract (issue #304, epic 298)

Sole writer: commander-304. Working notes, not a report.

## Isolation

```
py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/e298-304"
worktree OK: in C:/Programs/constellation-skills-wt/e298-304
EXIT=0
```

## Context step — what the repo actually carries

Recorded substitutions (context imperative requires it):

| path | present? | substitution |
|---|---|---|
| `docs/agents/ORCHESTRATOR_CONTEXT.md` | YES | read |
| `docs/agents/GLOSSARY.md` | NO | none available; global `_shared/` doctrine only |
| `docs/agents/engine-config.json` | NO | engine degraded to built-in defaults |
| `docs/architecture/` | **NO** | no packet map at all — substituted README/docs/CONSTELLATION_OVERVIEW.md |
| `.agent-work/LESSONS.md` | YES | Active section at 20/20 cap |

**`docs/agents/` EXISTS in this repo** (holds ORCHESTRATOR_CONTEXT.md). This directly falsifies the
shipped claim that "a skill-source repo has no docs/agents/ overlay at all". Confirmed at the very first
gate of this run, by the run itself.

**`docs/architecture/` does NOT exist here.** This repo is itself a degraded-mode repo. Confirms
`decision:degraded-mode-is-the-common-case` for at least this repo.

## Launch-order claims checked against the code

The order says: if something here does not match what you find, **the code wins**.

| order claim | verdict | evidence |
|---|---|---|
| `commander-core.md:142` is the absent-map fallback at reconcile | **CONFIRMED** | line 142, under "## Architecture bookend", reconcile-time |
| `COMMANDER_SPINE.template.json:75` is the absent-map fallback at reconcile | **CONFIRMED** | line 75, `tasks.reconcile.imperative` |
| context + plan carry *pathless* map imperatives | **CONFIRMED** | SPINE:22 "Read the current map (packets, overlays, decision anchors)"; SPINE:48 "Map-first: BEFORE authoring execute.json, produce a mission frame from the current map". Neither names a path. |
| "Every shipped checklist template carries `config_ref` **plus several hundred words** of prose explaining the path is dead" | **WRONG — corrected** | see below |

### Correction: the dead-path prose is 2 templates, not 11; ~112 words, not "several hundred"

Derived from a command (`py` walk over `skills/*/templates/*.json`, sentence-extracting on `engine-config`):

- **11 of 11** shipped templates carry the bare line `"config_ref": "docs/agents/engine-config.json"`.
  (admiral, cartographer, charter, commander SPINE, commander EXECUTE_PLAN, implementer, interrogator,
  lessons-auditor, reviewer, scout, workbench DEFAULT)
- **2 of 11** carry the do-not-create imperative prose:
  - `skills/commander/templates/COMMANDER_SPINE.template.json` → `tasks.context.imperative` (57 words)
  - `skills/commander/templates/EXECUTE_PLAN.template.json` → `tasks.e0-context.imperative` (55 words)
- Total engine-config prose across all shipped templates: **126 words** (112 of it the two dead-path blocks).

The scope of #317 is therefore materially smaller than the order assumed. The `config_ref` *line* is
corpus-wide (11 files); the *wrong prose* is Commander-local (2 files).

### NEW contradiction the order did not know about

`skills/charter/templates/CHARTER.template.json` ships a task `engine-config` whose imperative is:

> "Write docs/agents/engine-config.json (rework cap, rigor checkpoints, rules root, repo guidance).
> Confirm it with the user."

and `skills/charter/templates/ENGINE_CONFIG.template.json` exists to be written there.
`skills/charter/SKILL.md:23` lists the path as a Charter output.

So the corpus ships **two roles with opposite instructions about the same path**: Charter's job is to
create `docs/agents/engine-config.json`; Commander's context step says the path is dead and the reader
must **not** create it. Both shipped, both current. This is the corpus-internal defect behind #317, and
it is a *contradiction*, not merely staleness.

### The pathless problem is corpus-wide, not Commander-only

Same pathless "the current map" phrasing at:
- `skills/cartographer/templates/CARTOGRAPHER.template.json:10,12,20`
- `skills/scout/templates/SCOUT.template.json:10,12,20`
- `skills/explorer/templates/EXPLORER_SPINE.template.json:24`
- `skills/commander/references/commander-core.md:122`
- `skills/_shared/global-orchestrator.md:13` ("Map-first: frame every ask against ... before shaping work")

## CORRECTION to my own reported number (issued after the cold critic)

I reported "112 words" upward. **That was wrong. The correct figure is 172 words — 86 per template.**

My extraction regex counted only sentences literally containing `engine-config`, silently dropping each
block's trailing sentence ("If a run in such a repo needs non-default engine settings, inline a `config`
object..."). The cold critic caught it; I re-measured the full deletable block and the critic is right.

**The substance of the correction to the launch order is unaffected and still stands: 2 templates, not
11.** That was and remains the load-bearing part. Only the magnitude moves, and 172 is still nowhere
near "several hundred words on every shipped template."

Method note, and it is the launch order's own rule turned back on me: *derive distribution claims from a
command.* I did — but the command encoded my own assumption about sentence boundaries, so it inherited
my error rather than checking it. **A command is only as good as its predicate.** Deriving from a
command is necessary, not sufficient.

## decision:tripwires-are-episodes — AMENDED rationale (Admiral-approved)

The **ruling stands**: episodes remain the destination. `.agent-work/LESSONS.md` is at its 20/20 cap,
has no outcome field either, and is being retired by #308.

**The original rationale is withdrawn.** It claimed *"the episode record already carries a prediction
and an outcome slot."* The code says otherwise (issue #342): no `confirmed` lifecycle-standing;
`create` requires `observed-behavior`; `amend-assertion` writes only `lifecycle-standing`.

**Amended rationale, cited in place of the original:** episodes are the destination because
`LESSONS.md` is capped and being retired — **not** because the store carries an outcome slot. The
prediction/outcome shape this pathway needs is supplied by **git**, not by the store: pre-register
predictions in a committed `TRIPWIRES.md`, use commit history as the tamper-evident timestamp (the
episode writer is deliberately clock-free, so git supplies exactly what the store cannot), then file
episodes afterwards carrying a **real** `observed-behavior`. Never fabricates an observation.

## Triage filed to the tracker

| issue | finding |
|---|---|
| **#341** | engine command-kind checks inherit the launcher's cwd; 5 shipped relative checks silently fragile |
| **#342** | episode store has no `confirmed` standing; a held prediction is indistinguishable from an unchecked one |
| **#343** | pathless "current map" phrasing recurs in cartographer/scout/explorer — deliberately not fanned out |
| **#344** | installed corpus 18 commits stale; 3 of 11 commander scripts differ, incl. `checklist_engine.py` |

## Run state at return

| gate | state |
|---|---|
| init | complete |
| context | complete |
| understand | complete |
| plan | **in-progress — c3 "plan approved" deliberately NOT attested** |
| execute → archive | pending |

**Why the plan gate is open.** The cold critic returned DO NOT APPROVE with 5 BLOCKERs. Global doctrine:
*"Findings are triaged by the human, every one — edit the artifact / reopen exploration / reject with
reason — before the artifact is treated as confirmed. Acceptance is human-only; a critic never
self-triages."* I revised the plan against every finding, but I will not self-approve a plan a cold
critic blocked. That ruling is the Admiral's.

Everything upstream of it is driven through the engine with the lease held throughout.

## Post-return updates

- **Q1 RULED (Tommy): candidate B is OUT.** Bootstrap stanza and its install lifecycle dropped from
  scope entirely. Principle: placing content at a broader tier than its audience is a defect. The map is
  orchestrator content, not implementer content.
- **Zero-invocation reframed:** it was a defect in the measurement RIG (which launched generic agents),
  not a delivery defect in the product. A Commander run does invoke the Commander. Candidate As reach
  weakness largely evaporates.
- **Discriminated baseline (commander-299):** orientation 0/5, use 4/4, citation 4/5. The map was
  genuinely used - as verification after the seam was found, never as what found it. A SEQUENCING
  failure, precisely and only.
- **Necessity gate has zero discriminating power against the measured five**, and its only firing
  (#716) would have been a false positive. Ships as a floor, not as the fix. See the brief.

## The deficiency, restated for my own use

Not "no path exists." f1Brainz has an exact path in the always-loaded bootstrap. The gap is:
1. **primacy** — the map read is not ordered *before* source exploration; and
2. **contract** — nothing says what to do when the map cannot be resolved, so the silent fallback is
   code crawling, which is exactly what all five baseline runs did.
