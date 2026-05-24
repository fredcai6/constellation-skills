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
| `constellation-charter` | Interrogate engineering doctrine and compile Orchestrator, Crew, and Glossary context. |
| `constellation-workbench` | Manage local todos, workflow artifacts, evidence, closeout, and archive. |
| `constellation-cartographer` | Verify and document current architecture truth. |
| `constellation-conductor` | Orchestrate problem interrogation, framing, gated planning, handoffs, and evidence integration. |
| `constellation-crew` | Execute bounded implementation and independent review. |
| `constellation-triage` | Turn findings, gaps, drift, and future work into issue-ready recommendations. |

## Install

Preview first:

```powershell
python scripts/install_constellation.py --scope user --dry-run
```

Install for the current user:

```powershell
python scripts/install_constellation.py --scope user
```

Install into a project:

```powershell
python scripts/install_constellation.py --scope project --project C:\path\to\repo
```

Install selected skills:

```powershell
python scripts/install_constellation.py --scope project --project C:\path\to\repo --skills charter conductor
```

Refresh an existing install:

```powershell
python scripts/install_constellation.py --scope user --force
```

Rules:

- User scope installs to `$CODEX_HOME/skills`, or `~/.codex/skills` when `CODEX_HOME` is unset.
- Project scope installs to `<project>/.codex/skills`; `--dest` can point at a skills directory directly.
- Installed folder names use each skill's frontmatter name, such as `constellation-charter`.
- Existing skill folders fail fast unless `--force` is set.
- Restart Codex after installing or refreshing skills.

## Baseline assumptions

Constellation assumes a Git repo, Markdown documentation, and file-based workflow artifacts. Issue tracker, docs explorer, diagramming, CI, and runtime commands are project-specific and should be clarified by Charter.

## Recommended durable artifacts

```text
docs/
  agents/
    ORCHESTRATOR_CONTEXT.md
    CREW_CONTEXT.md
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
  CHARTER_OPEN_QUESTIONS.md

  <work-id>/
    CHARTER_CHECKLIST.md
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
