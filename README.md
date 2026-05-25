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
| `constellation-interrogator` | Run relentless one-question interrogation with a traceable question queue. |
| `constellation-cartographer` | Maintain the current-only structural map and sparse purpose/constraint overlays. |
| `constellation-scout` | Audit map-first architecture pressure and package improvement candidates. |
| `constellation-pilot` | Coordinate checklist-driven problem interrogation, gated planning, Crew handoffs, evidence integration, reconciliation, and closeout. |
| `constellation-crew` | Execute bounded implementation and independent review. |
| `constellation-triage` | Turn findings, gaps, drift, and future work into issue-ready recommendations. |

## Install

Preview first:

```powershell
python scripts/install_constellation.py --agent codex --scope user --dry-run
```

Install for the current Codex user:

```powershell
python scripts/install_constellation.py --agent codex --scope user
```

Install for the current Claude Code user:

```powershell
python scripts/install_constellation.py --agent claude --scope user
```

Install for Cursor or Gemini CLI:

```powershell
python scripts/install_constellation.py --agent cursor --scope user
python scripts/install_constellation.py --agent gemini --scope user
```

Install for every supported agent:

```powershell
python scripts/install_constellation.py --agent all --scope user
```

Install into a Codex project:

```powershell
python scripts/install_constellation.py --agent codex --scope project --project C:\path\to\repo
```

Install into a Claude Code project:

```powershell
python scripts/install_constellation.py --agent claude --scope project --project C:\path\to\repo
```

Install into every supported project agent root:

```powershell
python scripts/install_constellation.py --agent all --scope project --project C:\path\to\repo
```

Install selected skills:

```powershell
python scripts/install_constellation.py --agent codex --scope project --project C:\path\to\repo --skills charter pilot
```

Refresh an existing install:

```powershell
python scripts/install_constellation.py --agent codex --scope user --force
```

Rules:

- `--agent` is required and must be `codex`, `claude`, `cursor`, `gemini`, or `all`.
- Codex user scope installs to `$CODEX_HOME/skills`, or `~/.codex/skills` when `CODEX_HOME` is unset.
- Codex project scope installs to `<project>/.codex/skills`.
- Claude Code user scope installs to `~/.claude/skills`.
- Claude Code project scope installs to `<project>/.claude/skills`.
- Cursor user scope installs to `~/.cursor/skills`.
- Cursor project scope installs to `<project>/.cursor/skills`.
- Gemini CLI user scope installs to `~/.gemini/skills`.
- Gemini CLI project scope installs to `<project>/.gemini/skills`.
- `--dest` can point at a skills directory directly when installing for one agent.
- `--agent all` installs to each supported agent's native skills directory and rejects `--dest`.
- Installed folder names use each skill's frontmatter name, such as `constellation-charter`.
- Existing skill folders fail fast unless `--force` is set.
- `--force` removes all existing `constellation-*` entries in the target skills directory before copying the requested skills.
- Restart Codex after installing or refreshing Codex skills.
- Claude Code picks up changes in existing skill directories during the current session; restart it if the install created a top-level skills directory.
- Restart Cursor or Gemini CLI if new or updated skills are not listed in the current session.

## Baseline assumptions

Constellation assumes a Git repo, Markdown documentation, and file-based workflow artifacts. Issue tracker, structural map generation, CI, and runtime commands are project-specific and should be clarified by Charter.

## Structural map validation

Build or check Cartographer map artifacts:

```powershell
python scripts/build_architecture_map.py --root . --source-root src
python scripts/build_architecture_map.py --root . --source-root src --check
```

## Recommended durable artifacts

Decision anchors live in `docs/architecture/decisions/` when sparse current-structure rationale is worth preserving.

```text
docs/
  agents/
    ORCHESTRATOR_CONTEXT.md
    CREW_CONTEXT.md
    GLOSSARY.md

  architecture/
    index.md
    packets/
      <structural-node>.md
    decisions/
      <decision>.md
    overlays/
      *.yml
    MAP_BUILD.md
    generated/
      map.json
```

## Recommended workflow artifacts

```text
.agent_work/
  templates/
    *.template.md

.agent-work/
  CHARTER_OPEN_QUESTIONS.md

  <work-id>/
    CHARTER_CHECKLIST.md
    CARTOGRAPHER_CHECKLIST.md
    INTERROGATOR_QUESTIONS.md
    SCOUT_REPORT.md
    LOCAL_TODO.md
    PILOT_CHECKLIST.md
    GATED_PLAN.md
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      ...
```

Rules:

- If it is in `docs/`, it is meant to guide future workflows.
- If it is in `.agent_work/templates/`, it is the project-owned template catalog. Agents prefer `.agent_work/templates/<template-name>` and fall back to bundled `templates/<template-name>`.
- If it is in `.agent-work/`, it is temporary workflow state or archived history.
- When a role-specific checklist exists, use it as the execution controller. Local Todo should index that controller, track recovery state, and keep completed milestones visibly checked.
- Charter seeds and updates project templates when project doctrine changes checklist or handoff interfaces.
- Archived workflow artifacts are historical context only.
- Agents should not read archived workflow artifacts unless the user explicitly points to them.
- Anything future agents should rely on must be promoted to durable artifacts.
