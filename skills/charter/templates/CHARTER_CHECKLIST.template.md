# Charter Checklist: `<work title>`

This file is the live Charter driver, local todo, and decision record. It is retained for human traceability, not future runtime context.

## Allowed writes

```text
.agent-work/<work-id>/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
.agent-work/archive/<date>-<work-id>/
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
.agent_work/templates/*.template.md
```

All other writes are out of Charter scope.

## Project Template Catalog

Charter seeds and updates project templates.

**Lookup rule:** prefer `.agent_work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

**Seed status:** `<missing | current | updated this run>`  
**Template changes needed:** `<none | list>`  
**Template update evidence:** `<paths and decision IDs>`

## Run state

**Work ID:** `<work-id>`  
**Charter scope:** `<whole repo | subsystem | refresh scope>`  
**Compile mode:** `checkpoint | provisional | final`  
**Current gate:** `<gate number/name>`  
**Current next question:** `<one decision question or reference bundle request>`  
**Why this question matters:** `<what future agent behavior it affects>`  
**Recommendation/default:** `<recommended answer or rigorous default>`  
**Waiting on user:** `yes | no`

## Repo Action Authority

**Commit sensitivity:** `<ask always | commit local ok | push ok | PR only | direct main allowed | custom>`  
**Pilot may open PRs directly:** `yes | no | ask first`  
**Pilot may merge to main:** `yes | no | ask first`  
**Commit archived work packages:** `yes | no | ask each closeout`  
**Archived package commit decision:** `<decision source and evidence>`

## Scales

**Quality:** `strong | usable | weak | unresolved | not-material`  
**Authority:** `user decision | accepted default | unconfirmed default | repo artifact | assumption`  
**Posture:** `rigorous-default | relaxed | strengthened | mixed | not-applicable`
**Projection:** `orchestrator | crew | both | glossary | checklist-only`
**Projection reason:** `planning/framing | gating/evidence | authority/scope | implementation | verification | review/blocking | stop/report | terminology | local traceability`

Material decisions affect future agent behavior, allowed scope, evidence, failure behavior, interfaces/contracts, canonical inputs, documentation duties, dependency policy, security/privacy/publicness, performance/resource posture, generated artifacts, compromise policy, or stop/report conditions.

## Context Density

Generated context is agent-facing. Minimize tokens and maximize information per token. Sacrifice grammar for brevity when meaning stays clear. Prefer bullets, tables, and fragments. Omit prose that does not change agent action.

For each material decision use:

```text
Default -> Cost -> Relaxation -> Scenario -> Decision -> Evidence -> Projection
```

Shared project invariants default to `both` unless clearly role-specific. Architecture and scope policy is usually Orchestrator-only; Crew receives its consequences through the handoff.

## Gate 0: Bootstrap

**Purpose:** Establish scope and positive references before doctrine questions.

**Required prompts:**
- What is the Charter scope: whole repo, subsystem, or refresh?
- Provide best available positive exemplars for code shape, test style, documentation, workflow, and review evidence. Use `none yet` explicitly for missing categories.
- Which existing `docs/agents/*`, `AGENTS.md`, README/equivalent, philosophy/process docs, or user-provided references are authoritative?
- Should agents commit archived work packages, and what commit sensitivity governs Pilot repo actions?

**Completion criteria:**
- Scope recorded.
- Each exemplar category answered or marked `none yet`.
- Prior context imported as material decisions where relevant.
- `.agent_work/templates` exists with default templates or an explicit skip reason.
- Repo action authority recorded for Pilot PR/direct main behavior.

**Stop conditions:**
- Scope is unclear.
- Existing context and user intent conflict in a way that affects generated context.

## Gate 1: Operating Context

**Purpose:** Classify use, output authority, failure consequence, execution context, and subsystem profile.

**Required prompts:**
- Who uses the outputs, and what decisions/actions do outputs influence?
- What is output authority: advisory, diagnostic, canonical record, user-facing claim, automated action, or mixed?
- What failure is costly: wrong, stale, missing, slow, misleading, unreproducible, unsafe, privacy leak, or maintenance erosion?
- What execution contexts exist: runtime/operational, analysis, test infrastructure, reporting, exploratory, generated artifact pipeline?
- Start the subsystem table with at least `whole repo`.

**Completion criteria:**
- Project-level rigor profile selected.
- Execution context distinguished from rigor profile.
- Failure consequence understood.
- Subsystem table exists and may be refined later.

**Stop conditions:**
- Subsystem rules diverge so far that one context set would be unclear.

| Subsystem | Rigor profile | Execution context | Relaxed rules | Strengthened rules | Reason |
|---|---|---|---|---|---|
| whole repo | `<profile>` | `<context>` | `<none/list>` | `<none/list>` | `<reason>` |

## Gate 2: Engineering Rubric

**Purpose:** Touch every doctrine axis from `references/engineering-rubric.md`.

**Required prompts:**
- Do you accept, relax, or strengthen the rigorous default for this axis?
- What cost does the rigorous default impose here?
- If material, what scenario proves the rule?
- What evidence shows the scenario was handled correctly?

**Completion criteria:**
- Every rubric axis has a decision.
- Material decisions have scenario and evidence.
- `not-material` decisions have user agreement and reason.

## Gate 3: Implementation Conventions

**Purpose:** Convert doctrine into concrete implementation/review rules where needed.

**Required prompts:**
- Function/module size and complexity expectations.
- Interface shape and config representation.
- Status/error return convention.
- Event/log/reporting convention where relevant.
- Runtime call model, allocation/resource constraints, or determinism/randomness.
- Units, frames, identity, and naming conventions.
- Generated artifact mechanics only if project-specific.
- Testing/evidence levels by change type where project-specific.

**Completion criteria:**
- Each convention is marked `rule`, `tradeoff-tested`, or `not-material`.
- Crew-facing conventions are ready to compile.

## Gate 4: Contradiction Pass

**Purpose:** Resolve conflicts before durable context.

**Required prompts:**
- Do any decisions conflict across subsystems, failure policy, evidence, docs, dependencies, or generated artifacts?
- Are any decisions weak or unresolved?
- Is subsystem divergence too high for one context set?

**Completion criteria:**
- Contradiction register resolved or carried to Charter open questions.
- No hidden weak answer is promoted as final context.

## Gate 5: Context Compile

**Purpose:** Compile decisions into operational context, not history.

**Required prompts:**
- What belongs in Orchestrator context for planning/framing, gating/evidence, authority/scope, or stop/ask?
- What belongs in Crew context for implementation, verification, review/blocking, or stop/report?
- What terms belong in Glossary?
- Are shared decisions role-phrased instead of mechanically duplicated?
- Are handoff-only details kept out of durable Crew context?
- Which weak/unresolved items remain in `.agent-work/CHARTER_OPEN_QUESTIONS.md`?

**Completion criteria:**
- Durable context has decisions only, no debate history.
- Context density checked: brief, clear, true, no filler.
- Project templates updated when Charter decisions change workflow interfaces.
- Scope/exceptions appear only if needed.
- No links to workflow-local files in generated context.
- Crew context contains every project invariant that can change implementation, verification, review/blocking, or stop/report behavior.
- Orchestrator context contains every project invariant that changes framing, gate design, authority/scope decisions, evidence selection, or stop/ask behavior.
- Shared decisions use role-specific wording.
- Crew context contains only universal verification rules; area-specific commands are represented as handoff requirements.
- Workflow selection and coordination consequences reach Crew through the handoff.

## Gate 6: Closeout

**Purpose:** Finish honestly.

**Final compile checklist:**
- [ ] All gates complete.
- [ ] No `weak` or `unresolved` material decisions remain.
- [ ] Contradiction pass complete.
- [ ] `docs/agents/ORCHESTRATOR_CONTEXT.md` updated.
- [ ] `docs/agents/CREW_CONTEXT.md` updated.
- [ ] `docs/agents/GLOSSARY.md` updated.
- [ ] `.agent_work/templates` seeded and project-specific template changes applied or explicitly skipped.
- [ ] Shared project invariants default to `both` unless clearly role-specific.
- [ ] Every `both` decision has non-empty Orchestrator and Crew forms with role-specific wording.
- [ ] Crew context contains every project invariant that can change implementation, verification, review/blocking, or stop/report behavior.
- [ ] Orchestrator context contains every project invariant that changes framing, gate design, authority/scope decisions, evidence selection, or stop/ask behavior.
- [ ] Crew context contains only universal verification rules; area-specific commands are represented as handoff requirements.
- [ ] Handoff-only details are not placed in durable Crew context.
- [ ] `.agent-work/CHARTER_OPEN_QUESTIONS.md` deleted or absent.
- [ ] Move the entire `.agent-work/<work-id>/` package to `.agent-work/archive/<date>-<work-id>/`, including `INTERROGATOR_QUESTIONS.md`.
- [ ] No loose work-id artifacts remain.

## Material Decisions

| ID | Gate | Decision | Quality | Authority | Posture | Projection | Projection reason |
|---|---|---|---|---|---|---|---|
| D-001 | `<gate>` | `<decision>` | `<quality>` | `<authority>` | `<posture>` | `<orchestrator | crew | both | glossary | checklist-only>` | `<reason>` |

### D-001: `<short title>`

**Default:** `<rigorous default>`  
**Cost:** `<cost of default>`  
**Relaxation:** `<looser/faster version>`  
**Scenario:** `<specific conflict>`  
**Decision:** `<chosen rule>`  
**Evidence:** `<what proves compliance>`  
**Projection:** `orchestrator | crew | both | glossary | checklist-only`  
**Projection reason:** `<controlled reason plus optional note>`  
**Orchestrator form:** `<planning/framing/gating/authority/evidence/stop-ask wording or n/a>`  
**Crew form:** `<implementation/verification/review/blocking/stop-report wording or n/a>`  
**Glossary form:** `<term/meaning or n/a>`  
**Projection note:** `<only when the projection could be ambiguous>`  
**Notes:** `<decision traceability only, not transcript>`

## Informational Notes

- `<note that does not become runtime context unless converted into a material decision>`

## Contradiction Register

| ID | Conflict | Status | Resolution |
|---|---|---|---|
| C-001 | `<conflict>` | `open | resolved` | `<decision or open question>` |

## Compile History

| Date | Mode | Outputs touched | Remaining weak/unresolved |
|---|---|---|---|
| `<date>` | `<checkpoint | provisional | final>` | `<files>` | `<none/list>` |
