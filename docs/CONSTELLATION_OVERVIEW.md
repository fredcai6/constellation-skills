# Constellation Overview

```text
Charter      -> interrogates engineering doctrine and compiles agent-operable context
Admiral      -> runs an epic as the human's delegate; dispatches Commanders in waves; adjudicates, merges, and harvests at closeout
Commander    -> runs one bounded issue end to end; owns spine, interrogation, and execute checklists; dispatches crew
Explorer     -> shapes a raw idea upstream of any issue: exploration cycles, excursions, cold critique, human-confirmed spec; never cuts work
Workbench    -> manages recoverable workflow state and drives the checklist engine
Interrogator -> questions request/design ambiguity as a survey probe
Cartographer -> maintains current-only structural map
Scout        -> audits map-first architecture pressure
Implementer  -> implements a bounded change from a handoff
Reviewer     -> independently verifies a bounded change
Triage       -> classifies and writes issue-ready recommendations; no checklist
Prototyper   -> answers one named question with throwaway code (logic/UI/measurement); handoff-driven, no checklist
Lessons-auditor -> distills scoped, grounded lesson candidates from run artifacts with fresh context (Admiral closeout / Commander feedback subagent)
Docent       -> generates a stamped static HTML explainer site from Cartographer map truth; read-only map consumer
Curator      -> periodically measures the skills corpus (curate_corpus.py), mends mechanical drift in place, routes design decisions to Triage; human-invoked, no checklist
```

The checklist engine (`scripts/checklist_engine.py`, schema `docs/CHECKLIST_SCHEMA.md`, model `docs/CHECKLIST_ENGINE_DESIGN.md`) is the substrate every role drives: a `gated` (execution) or `survey` (verification/inquiry) plan worked one step at a time, with the human as the top tier surfacing decisions at Commander checkpoints.

An eval harness (`scripts/run_skill_eval.py`, scenarios under `evals/`) runs a candidate corpus through a real workflow and scores it with process checks (Curator's instrument). It is a repo tool, not a role, and nothing in the runtime or CI gates on it.

## Relationship Contract

Skill.md is trigger, boundary, and resource pointer. Templates are the interface. References hold doctrine/detail.

| Producer | Artifact/interface | Consumer | Contract |
|---|---|---|---|
| Skills (`_shared`, bundled at install) | `references/global-{everyone,orchestrator,crew}.md` | all roles | inherited approach doctrine read first at each checklist's context step; identical across projects; the home for general-workflow `constellation` lessons |
| Skills (`_shared`, bundled at install) | `references/design-it-twice-brief.md` | orchestrator tier (explorer excursions, Commander plan step) | shared parallel-alternatives fill-in contract (design-it-twice standard): distinct-constraint candidates, not-a-proposal human framing, untaken-road and panel-vs-single records; norm lives in global-orchestrator doctrine |
| Commander | `.agent-work/<work-id>/spine.json` (gated) | Cartographer, Interrogator, human | one bounded issue: understand/plan/execute/cleanup; drives interrogation and gate plan; human verifies at checkpoints |
| Commander | `.agent-work/<work-id>/execute.json` (gated) | Implementer, Reviewer | frozen gate plan authored at plan time; three tasks per gate (implement/review/integrate); not edited mid-run |
| Charter | `docs/agents/ORCHESTRATOR_CONTEXT.md` | Commander, Cartographer, Scout | project DELTAS over inherited global-orchestrator doctrine: planning, authority, evidence, stop/ask departures |
| Charter | engine config (rework cap, replan policy, human checkpoints) | Commander, Workbench engine | sets the mechanism limits the engine enforces |
| Charter | `docs/agents/CREW_CONTEXT.md` | Crew | project DELTAS over inherited global-crew doctrine: implementation/review rules usable inside a handoff |
| Charter | `docs/agents/GLOSSARY.md` | all roles | shared terms only; no workflow state |
| Charter | `docs/agents/AGENT_GUIDE.md` + root `AGENTS.md`/`CLAUDE.md` pointers | all agents (Constellation or external) | single repo-orientation guide: layout, documentation map, conventions; the shared middle of the two contexts, not how to approach the job |
| Commander, Admiral | `episodes/active/` via `scripts/apply_episode_delta.py` | future Charter refresh, maintainers | one episode per distinct thing that happened, written at closeout through the store's only write path; a record of what happened, never a rule to follow |
| Workbench | `templates/DEFAULT.template.json` | any role | generic gated controller for ad-hoc work; not durable truth |
| Role skills | role-specific checklist templates | owning role, Workbench | execution controller when role ships one; Workbench creates/archives files but does not own semantics |
| Workbench | closeout/archive rules | Commander, Cartographer | artifact hygiene; roles execute package movement at closeout |
| Interrogator | `.agent-work/<work-id>/interrogation.json` | Commander, Charter | survey of questions; consolidates to a resolved understanding |
| Cartographer | `docs/architecture/packets/` + `index.md` | Scout, Commander, Implementer, Reviewer, Docent | current structural truth and sparse purpose/constraint/rationale anchors |
| Cartographer | mismatch/Triage candidate | Commander, Triage | current-vs-future separation with structural anchor |
| Scout | `SCOUT_REPORT` | user, Commander, Triage | ranked architecture improvement candidates with map/code evidence |
| Commander | `IMPLEMENTER_HANDOFF` | Implementer | bounded task, authority, scope, exclusions, test mode, evidence requirements, stop conditions |
| Commander | `REVIEWER_HANDOFF` | Reviewer | task statement, diff access, close criteria, constraints, implementer evidence |
| Implementer / Reviewer | `IMPLEMENTER_RESULT` / `REVIEW_RESULT` | Commander | evidence, blockers, scope drift, assumptions, out-of-scope observations |
| Commander, Cartographer, Scout, Implementer, Reviewer, Curator | Triage candidate | Triage | future work package, not current-scope expansion |
| Triage | issue-ready recommendation | user / issue tracker | bounded future work with evidence and acceptance criteria |
| Curator | `CURATOR_REPORT` + `--json` record | human, Triage | periodic corpus-health pass: mechanical measurement (`curate_corpus.py`, flags-never-gates), in-place mechanical mends reviewed by git diff; design decisions routed to Triage, never silently applied |
| Explorer | `.agent-work/explore-<topic>/DESIGN_SPEC.md` (confirmed) or shaped-design issue | to-issues / Commander, human | hard gate: `verify_spec_confirmed.py` must pass before work is cut; an `UNCONFIRMED — DO NOT CUT` shaped-design issue is never cut |
| Explorer | `EXCURSION_BRIEF` | Prototyper, research agents, design-it-twice panels | one named question per excursion; prototype section fields identical to `PROTOTYPE_HANDOFF` |
| Anyone (human, Commander, Explorer) | `PROTOTYPE_HANDOFF` | Prototyper | one named question, branch, host conventions, location, stop conditions |
| Prototyper | `PROTOTYPE_RESULT` | dispatcher | scoped answer: what was tested AND what was NOT tested; mandatory disposition (deleted / absorbed / parked-with-owner / captured-to-worktree) |

## Context separation

Two orthogonal axes. **Audience:** high-level (orchestrator) agents use project purpose, user intent, structural map packets, glossary, and workflow state; low-level (crew) agents receive bounded task, allowed scope, critical rules, relevant structural packet, required evidence, and stop conditions. **Source:** each agent reads its inherited *global* doctrine (bundled with the skill at `references/global-{everyone,<tier>}.md`, identical across projects) first, then the project's thin *local* deltas (`docs/agents/*`, read if present) — layered, never merged. The global buckets hold the approach baseline; the project files hold only departures.

## Truth layers

```text
Code, tests, configs, generated behavior:
  dense truth

Structural map packets, agent context (docs/agents/*), glossary:
  compressed durable truth

episodes/active/ + episodes/retired/:
  raw observed history — what actually happened on real runs

Commander execute.json (frozen gate plan), crew handoffs, default checklists:
  workflow-local truth

Issues:
  future work
```

### The episode store, and what replaces the playbook

The episode store (`episodes/`, `docs/EPISODE_STORE.md`) is a layer the other four do not
cover: **raw observed history**. A packet says what the system *is*; an episode says what
happened *once*, on a named run, with the mechanical half captured from engine state at zero
agent effort and the agent-supplied half carrying what only an agent can assert. It is
tracked in git precisely so it outlives the worktree that wrote it.

**The flow, as ruled at issue #308.** Episodes accumulate. A periodic pass — the curator's
job — rhyme-searches them for recurring patterns, and a confirmed pattern is consolidated
into **doctrine that agents actually read**: `docs/agents/ORCHESTRATOR_CONTEXT.md`,
`docs/agents/CREW_CONTEXT.md`, the auto-loaded `CLAUDE.md`, or a role's own skill —
whichever tier matches the audience. Consolidated episodes are retired, which **moves** the
file into `episodes/retired/`; the archive stays reachable by id so a `consolidated-into:`
reference never dangles.

**`.agent-work/LESSONS.md` is not in this taxonomy, and that is the ruling, not an
omission.** It was a curated playbook sitting between those two useful things — an
accumulator and real doctrine updates — and it turned out to be a dead end: content parked
there was neither raw history nor doctrine anyone reads. Live agents no longer read it. The
accumulator is `episodes/`; the doctrine is `docs/agents/`; the middle is gone.

Its retention story is hygiene rather than a cap. The 20-entry hard cap was removed because
a cap does not cause cleanup — it causes *forgetting*, and then blocks capture outright.
Measured at issue #308 before the removal: the bank sat at 20/20, so the writer refused
every new entry, while 10 of those 20 had never once been reconfirmed. Regular curator
cleanup replaces it.

### Reaching the compressed layer: the map-input contract

The compressed layer only helps if an agent reads it **before** it starts building a picture from code.
Naming a map is not the same as orienting from one: five measured Commander runs against a repo whose
always-loaded bootstrap named an exact map path read source *first* in every run that read source at
all, reaching the map only to confirm a hypothesis they had already formed.

So Commander's `context` step carries a resolved contract rather than a pathless request. It resolves a
canonical entrypoint (`scripts/map_orient.py orient`), and when it cannot, it enters a **REPORTED
degraded mode**: the run records what it read *instead* of a map — hash-pinned, and labelled by whether
the file came from a fixed corpus-declared fallback set (verified by filesystem existence) or was merely
agent-declared — plus the unmapped gap and an escalation, before any source read. `verify-orientation`
enforces that record at `context`; `verify-frame` checks at `plan` that the mission frame cites anchors
which actually resolve, against that earlier committed declaration rather than a same-breath assertion.

**What this does and does not buy, stated plainly because the measurement says so.** The genuinely new
thing is the degraded arm: a repo with no map previously had *no contract at all* — a silent crawl and
no record. The citation check ships as a **regression floor** against map-*ignoring*; against the
baseline five its measured sensitivity is 0/4 and its specificity 0/1, so it is **not** the fix for
map-*lateness*. Ordering is not mechanizable by the corpus — enforcing "map before code" needs a
harness-level pre-tool hook this corpus does not own. The known bypass is measured, not hypothetical:
crawl source first, then write the anchors into the frame afterwards.

## Authority transfer

Agent action traces to one of:

- explicit user decision
- existing project ground rule
- task-specific delegation
- named conservative default
- unresolved assumption

Only the first three are strong authority.
