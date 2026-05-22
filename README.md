# Constellation Skills

Constellation Skills is a lightweight agent workflow system for repo-based development.

Core doctrine:

```text
Humans own intent, values, priorities, and authority transfer.
Agents organize, interrogate, execute, verify, and preserve recoverable work state.
```

## Skill set

| Skill | Purpose |
|---|---|
| `constellation-charter` | Elicit project ground rules and produce standalone agent context docs. |
| `constellation-workbench` | Manage local todos, workflow artifacts, evidence, closeout, and archive. |
| `constellation-cartographer` | Verify and document current architecture truth. |
| `constellation-conductor` | Orchestrate problem interrogation, framing, gated planning, handoffs, and evidence integration. |
| `constellation-crew` | Execute bounded implementation and independent review. |
| `constellation-triage` | Turn findings, gaps, drift, and future work into issue-ready recommendations. |

## Baseline assumptions

Constellation assumes a Git repo, Markdown documentation, and file-based workflow artifacts. Issue tracker, docs explorer, diagramming, CI, and runtime commands are project-specific and should be clarified by Charter.

## Recommended durable artifacts

```text
docs/
  agents/
    GROUND_RULE_DECISIONS.md
    ORCHESTRATOR_CONTEXT.md
    IMPLEMENTER_REVIEWER_CONTEXT.md
    OPEN_QUESTIONS.md
    GLOSSARY.md

  architecture/
    index.md
    packets/
      <region>.md
    diagrams/
      *.mmd
    EXPLORER_BUILD.md
```

## Recommended workflow artifacts

```text
.agent-work/
  <work-id>/
    LOCAL_TODO.md
    FRAMING_NOTE.md
    GATED_PLAN.md
    handoffs/
    evidence/
    issue-recommendations/

  archive/
    <date>-<work-id>/
      ...
```

Rules:

- If it is in `docs/`, it is meant to guide future workflows.
- If it is in `.agent-work/`, it is temporary workflow state or archived history.
- Archived workflow artifacts are historical context only.
- Agents should not read archived workflow artifacts unless the user explicitly points to them.
- Anything future agents should rely on must be promoted to durable artifacts.
