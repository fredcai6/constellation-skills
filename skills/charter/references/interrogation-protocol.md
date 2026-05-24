# Charter Interrogation Protocol

Charter exists to turn engineering doctrine into usable Orchestrator, Crew, and Glossary context. It is a relentless interrogation pass, not a setup wizard.

## Core rule

Do not accept a material rule until it has been tested against cost and a concrete scenario.

A usable material decision names:

- subsystem or artifact type
- output or behavior
- canonical input/data source if relevant
- failure consequence
- evidence expectation
- generated context target

If any are missing, continue drilling.

Ask one question at a time when pursuing decisions. Gate 0 may request reference and exemplar paths together.

## First action

Create or resume `.agent-work/<work-id>/CHARTER_CHECKLIST.md` before Gate 0. The checklist is the live todo, gate tracker, and decision record.

Use `.agent-work/CHARTER_OPEN_QUESTIONS.md` only when provisional durable context exists and weak or unresolved Charter questions remain. It is not a backlog.

## Decision pattern

For every material decision:

```text
Default:
Cost:
Relaxation:
Scenario:
Decision:
Evidence:
Quality:
Authority:
Posture:
Output target:
```

Quality values:

```text
strong | usable | weak | unresolved | not-material
```

Authority values:

```text
user decision | accepted default | unconfirmed default | repo artifact | assumption
```

Posture values:

```text
rigorous-default | relaxed | strengthened | mixed | not-applicable
```

## Follow-up ladder

When the user answers broadly, move down the ladder:

```text
Broad claim
-> subsystem/artifact
-> concrete scenario
-> unacceptable outcome
-> evidence requirement
-> generated context rule
```

Example:

```text
User: "Tests should be good enough."
Charter: "For a behavior change in the promoted library path, the rigorous default is test-led evidence. Cost: slower implementation and more up-front test design. Relaxation: review-only or test-after. Scenario: a small parser change fixes one input but breaks a documented edge case. Should this project accept the default, relax it for this subsystem, or strengthen it with regression fixtures? What evidence would make the change acceptable?"
```

## Shallow answer triggers

Drill again when the user says:

- "be careful"
- "use judgment"
- "ask when unsure"
- "write tests"
- "move fast"
- "don't overcomplicate it"
- "depends"
- "reasonable defaults"
- "just follow the docs"
- "do it right"

These can be valid preferences only after conversion into a scenario-tested decision.

## Gate pressure

Gate 0 focuses on positive references, not bad examples. Ask for best available examples of desired code shape, test style, documentation, workflow, and review evidence. Require `none yet` when missing.

Operating context must identify output authority, execution context, failure consequence, and subsystem rigor before detailed doctrine.

Every rubric axis must be touched. Non-material axes need user agreement and a reason.

Implementation conventions are separate from doctrine. Use structured options only for consequential tradeoffs; otherwise record direct rules or `not-material`.

## Compile modes

Checkpoint:

- only workflow-local Charter files updated

Provisional:

- durable context may be generated
- weak or unresolved items remain in `.agent-work/CHARTER_OPEN_QUESTIONS.md`

Final:

- no weak or unresolved material decisions
- contradiction pass complete
- Orchestrator context, Crew context, and Glossary updated
- `.agent-work/CHARTER_OPEN_QUESTIONS.md` deleted or absent

Generated context contains decisions only. Do not include Charter process history, compile state, role manuals, or workflow-local links.

## Completion test

Before final compile, check:

```text
Could Orchestrator shape work without re-asking basic project doctrine?
Could Crew know what evidence and review blockers apply?
Could the glossary prevent key term ambiguity?
Could agents recognize when to stop and ask?
Are all weak/unresolved Charter questions gone?
```

If any answer is no, continue Charter or keep provisional state.
