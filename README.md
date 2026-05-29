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
| `constellation-charter` | Interrogate engineering doctrine and compile Orchestrator, Crew, Glossary, and engine config. |
| `constellation-commander` | Run one bounded issue end to end as the human's rigor scaffold. |
| `constellation-workbench` | Manage local workflow files and drive the checklist engine (gated/survey). |
| `constellation-interrogator` | Run a question survey and consolidate a resolved understanding. |
| `constellation-cartographer` | Maintain the current-only structural map and sparse purpose/constraint overlays. |
| `constellation-scout` | Audit map-first architecture pressure and package improvement candidates. |
| `constellation-pilot` | Execute a frozen gate plan gate by gate, dispatching implementer and reviewer. |
| `constellation-implementer` | Implement a bounded change from a handoff, driving its own gated plan. |
| `constellation-reviewer` | Independently verify a bounded change as a survey and consolidate a verdict. |
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
- Required helper scripts are bundled into each installed skill under `scripts/`.
- `checklist_engine.py` is shared workflow infrastructure and is intentionally bundled with every checklist-driving skill that needs it.
- Existing skill folders fail fast unless `--force` is set.
- `--force` removes all existing `constellation-*` entries in the target skills directory before copying the requested skills.
- Restart Codex after installing or refreshing Codex skills.
- Claude Code picks up changes in existing skill directories during the current session; restart it if the install created a top-level skills directory.
- Restart Cursor or Gemini CLI if new or updated skills are not listed in the current session.

## Baseline assumptions

Constellation assumes a Git repo, Markdown docs, and file-based workflow state. Charter clarifies issue tracker, structural map generation, CI, and runtime commands.

## Structural map validation

Build or check Cartographer map artifacts:

```powershell
python scripts/build_architecture_map.py --root . --source-root src
python scripts/build_architecture_map.py --root . --source-root src --check
```

## Recommended durable artifacts

Decision anchors live in `docs/architecture/decisions/` when current-structure rationale is worth preserving.

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
.agent-work/
  templates/
    *.template.json
    *.template.md

  CHARTER_OPEN_QUESTIONS.md
  SCOUT_REPORT.md

  <work-id>/                       # one work-id holds the whole tree
    spine.json                     # commander
    interrogation.json
    execute.json                   # gate plan; g<N>-review.json per gate
    charter.json                   # when charter runs
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      ...
```

Rules:

- If it is in `docs/`, it is meant to guide future workflows.
- If it is in `.agent-work/templates/`, it is the project-owned template catalog. Agents prefer `.agent-work/templates/<template-name>` and fall back to bundled `templates/<template-name>`.
- If it is in `.agent-work/`, it is temporary workflow state or archived history.
- Workflow status language follows `skills/workbench/references/status-model.md`.
- Pilot Checklist = single execution controller for Pilot work; implementation gates and per-gate evidence live in its Implementation Gates section.
- Default Checklist = fallback controller when a role does not ship its own checklist (e.g. Crew multi-step recovery). Never both a role checklist and Default Checklist for the same work.
- Charter seeds and updates project templates when project doctrine changes checklist or handoff interfaces.
- Charter and Pilot closeout move the complete `.agent-work/<work-id>/` package to `.agent-work/archive/<date>-<work-id>/`, including interrogation sessions.
- Archived workflow artifacts are historical context only.
- Do not read archived workflow artifacts unless the user points there.
- Future-agent truth must be promoted to durable artifacts.
