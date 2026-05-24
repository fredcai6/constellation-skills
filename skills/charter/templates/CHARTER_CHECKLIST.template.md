# Charter Checklist: `<work title>`

This file is the live Charter driver, local todo, and decision record. It is retained for human traceability, not future runtime context.

## Allowed writes

```text
.agent-work/<work-id>/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
```

All other writes are out of Charter scope.

## Run state

**Work ID:** `<work-id>`  
**Charter scope:** `<whole repo | subsystem | refresh scope>`  
**Compile mode:** `checkpoint | provisional | final`  
**Current gate:** `<gate number/name>`  
**Current next question:** `<one decision question or reference bundle request>`  
**Why this question matters:** `<what future agent behavior it affects>`  
**Recommendation/default:** `<recommended answer or rigorous default>`  
**Waiting on user:** `yes | no`

## Scales

**Quality:** `strong | usable | weak | unresolved | not-material`  
**Authority:** `user decision | accepted default | unconfirmed default | repo artifact | assumption`  
**Posture:** `rigorous-default | relaxed | strengthened | mixed | not-applicable`

Material decisions affect future agent behavior, allowed scope, evidence, failure behavior, interfaces/contracts, canonical inputs, documentation duties, dependency policy, security/privacy/publicness, performance/resource posture, generated artifacts, compromise policy, or stop/report conditions.

For each material decision use:

```text
Default -> Cost -> Relaxation -> Scenario -> Decision -> Evidence
```

## Gate 0: Bootstrap

**Purpose:** Establish scope and positive references before doctrine questions.

**Required prompts:**
- What is the Charter scope: whole repo, subsystem, or refresh?
- Provide best available positive exemplars for code shape, test style, documentation, workflow, and review evidence. Use `none yet` explicitly for missing categories.
- Which existing `docs/agents/*`, `AGENTS.md`, README/equivalent, philosophy/process docs, or user-provided references are authoritative?

**Completion criteria:**
- Scope recorded.
- Each exemplar category answered or marked `none yet`.
- Prior context imported as material decisions where relevant.

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
- What belongs in Orchestrator context?
- What belongs in Crew context?
- What terms belong in Glossary?
- Which weak/unresolved items remain in `.agent-work/CHARTER_OPEN_QUESTIONS.md`?

**Completion criteria:**
- Durable context has decisions only, no debate history.
- Scope/exceptions appear only if needed.
- No links to workflow-local files in generated context.

## Gate 6: Closeout

**Purpose:** Finish honestly.

**Final compile checklist:**
- [ ] All gates complete.
- [ ] No `weak` or `unresolved` material decisions remain.
- [ ] Contradiction pass complete.
- [ ] `docs/agents/ORCHESTRATOR_CONTEXT.md` updated.
- [ ] `docs/agents/CREW_CONTEXT.md` updated.
- [ ] `docs/agents/GLOSSARY.md` updated.
- [ ] `.agent-work/CHARTER_OPEN_QUESTIONS.md` deleted or absent.
- [ ] This checklist retained.

## Material Decisions

| ID | Gate | Decision | Quality | Authority | Posture | Output target |
|---|---|---|---|---|---|---|
| D-001 | `<gate>` | `<decision>` | `<quality>` | `<authority>` | `<posture>` | `<orchestrator | crew | glossary | checklist only>` |

### D-001: `<short title>`

**Default:** `<rigorous default>`  
**Cost:** `<cost of default>`  
**Relaxation:** `<looser/faster version>`  
**Scenario:** `<specific conflict>`  
**Decision:** `<chosen rule>`  
**Evidence:** `<what proves compliance>`  
**Role implication:** `<orchestrator/crew/glossary implication>`  
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
