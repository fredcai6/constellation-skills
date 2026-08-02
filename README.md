# Constellation Skills

Constellation Skills is a **team-rigor system for solo engineering with agents**. Its premise: a *team* of agents catches what any one agent misses — the way a human team does — while the human holds the vision and the high-level context. Rigor is the **default, not a knob**: if you don't want rigor, you don't reach for constellation.

Core doctrine:

```text
Humans own intent, values, priorities, and authority transfer.
Agents organize, interrogate, execute, verify, and preserve recoverable work state.
```

## What makes it a team, not a checklist

Every skill is a scaffold that keeps a human's standards intact while agents do the work. Three mechanisms carry the rigor so you don't have to:

- **An independent reviewer, every time.** Confidence does not come from the author grading its own work — it comes from a *fresh-context reviewer* (a distinct agent) that validates intent and implementation. That second agent is the concrete embodiment of the thesis: it is what makes "trust the agent" safe.
- **Mechanically-enforced rails.** The checklist engine, the `verify_*` scripts, and per-skill rails are machinery, not exhortation — a script exit code or a required field that *refuses* rather than reminds. A rail exception requires the independent reviewer's co-sign and a log entry; self-assertion never passes.
- **An architecture network that keeps *why* hooked to *what*.** The Cartographer map, its overlays, and the retired-spec rationale keep intent connected to the code as it changes.

Delegation is first-class, not a fallback: every tier can ask up the chain, and delegated commanders run under an Admiral's waves.

## Positioning (vs. superpowers / Matt Pocock)

Constellation deliberately holds native, rigor-flavored versions of the capabilities you would otherwise reach into the **superpowers** plugin or **Matt Pocock** skills for — so those externals can be removed from the box without losing a capability. The one-line difference: superpowers ships reusable *technique* skills and Pocock ships grilling-led "real engineer" skills, while constellation is **rigor-first, engine-enforced, and delegation-native** — a coordinated team with an independent-reviewer safety net and hard rails.

- The full seat-by-seat comparison and the workflow chains are in [`docs/POSITIONING.md`](docs/POSITIONING.md).
- The external → constellation-home coverage record (what replaces each external skill, and what is deliberately declined) is the **removability ledger**: [`docs/REMOVABILITY_LEDGER.md`](docs/REMOVABILITY_LEDGER.md), machine-checked by [`scripts/verify_coverage_ledger.py`](scripts/verify_coverage_ledger.py).

## Skill set

The corpus is **19 skills**. `skills/_shared/` is **not a skill** — it is shared doctrine (e.g. `skill-goodness.md`, deep-module notes) that multiple skills consume.

| Skill | Purpose |
|---|---|
| `constellation-explorer` | Shape a raw idea into an interrogated, critically reviewed, human-confirmed design spec before any work is cut; convergence is human-only. |
| `constellation-to-issues` | Cut a confirmed design spec into a dependency-ordered, HITL/AFK-typed issue set and file it (GitHub-first, tracker-pluggable). |
| `constellation-admiral` | Run an epic as the human's delegate: latitude contract, Commander waves, adjudication, lessons-and-architecture closeout. |
| `constellation-commander` | Run one bounded issue end to end for a live human as the human's rigor scaffold. |
| `constellation-commander-delegated` | Run one bounded issue end to end under a frozen Admiral launch order with no reachable human, citing the order and escalating genuine gaps. |
| `constellation-interrogator` | Run a question survey and consolidate a resolved understanding; resolve facts by exploring code, block on genuine human decisions, and hold a no-quit-early finish gate. |
| `constellation-implementer` | Implement a bounded change from a handoff, driving its own gated TDD plan through the engine. |
| `constellation-reviewer` | Independently verify a bounded change as a survey, including a Fowler code-smell / refactoring pass, and consolidate a verdict. |
| `constellation-diagnose` | Reproduce-before-you-claim debugging: one evidence loop for runtime bugs and intent/execution disconnects. |
| `constellation-write-a-skill` | Author a new skill — classify, scaffold, draft — gated by an install-and-corpus-correct rail and the shared skill-goodness criteria. |
| `constellation-cartographer` | Maintain the current-only multidimensional map: structural hierarchy plus sparse capability/event/constraint/assumption/decision/claim overlays. |
| `constellation-scout` | Audit map-first architecture pressure and package improvement candidates. |
| `constellation-triage` | Turn findings, gaps, drift, and future work into issue-ready recommendations. |
| `constellation-prototyper` | Build a throwaway prototype that answers one named question (logic / UI / measurement), with a mandatory disposition at closeout. |
| `constellation-charter` | Interrogate engineering doctrine and compile Orchestrator, Crew, Glossary, and engine config. |
| `constellation-curator` | Periodic human-run maintenance of the skills corpus: measure, mend mechanical issues in place, route design decisions to Triage. |
| `constellation-lessons-auditor` | Fresh-context Reflector at closeout: distill scoped, grounded lesson candidates from run artifacts; nominate, never apply. |
| `constellation-docent` | Generate a self-contained static HTML explainer site for humans from Cartographer map truth, stamped with the source-map digest so a stale site is visibly flagged. |
| `constellation-workbench` | Manage local workflow files and drive the checklist engine (gated/survey); the substrate every other skill uses. |

## Repo layout vs. installed layout

Constellation is developed and installed from two different shapes — knowing which you are looking at avoids confusion:

- **In this repo**, each skill lives under `skills/<name>/` (e.g. `skills/diagnose/`, `skills/write-a-skill/`), and the shared helper scripts live once at the repo root under `scripts/`.
- **When installed**, `scripts/install_constellation.py` bundles each skill's `SKILL.md`, its `scripts/`, `references/`, and `templates/` into a self-contained folder named `constellation-<name>/` under the agent's skills root (for Claude Code user scope, `~/.claude/skills/constellation-<name>/`). Shared infrastructure such as `checklist_engine.py` is copied into every checklist-driving skill's bundle so each installed skill is self-contained.

So `skills/diagnose/` in the repo becomes `~/.claude/skills/constellation-diagnose/` once installed; the short repo name and the `constellation-`-prefixed installed name are the same skill.

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

Every install also **reports** whether the Context Governor's `PostToolUse` hooks are wired into
your `settings.json` — `WIRED`, `STALE`, `UNWIRED`, or `CANNOT EVALUATE`. It only reports: nothing
is written to `settings.json` without the opt-in flag below, and it will not create that file.

To also wire the hooks (Claude Code only):

```powershell
python scripts/install_constellation.py --agent claude --scope user --wire-hooks
```

The entry is added alongside any `PostToolUse` matchers you already have. Prefer `--scope user`:
project scope writes a committable `settings.json`, and the path it carries is absolute and so
embeds your username. See [docs/GAUGE_WRITER_HOOK.md](docs/GAUGE_WRITER_HOOK.md).

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
python scripts/install_constellation.py --agent codex --scope project --project C:\path\to\repo --skills charter commander
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

## Keeping project installs fresh

Every install stamps a `CORPUS.json` provenance marker at the skills root (both user and project scope) recording the corpus content hash, the constellation `source_commit` it was built from, and the build date. A project-scope install is therefore a verifiable build artifact, not an unattributable fork — you can always tell which upstream commit a checked-in copy came from.

Check whether an installed corpus is behind upstream without a local constellation clone:

```powershell
python scripts/check_corpus_freshness.py --skills-root .claude/skills
```

It reads the installed `CORPUS.json`, fetches constellation `main` HEAD from GitHub (via `gh api`, falling back to plain HTTPS), and reports `current` / `behind` (with the commit count and subjects when behind). Exit codes: `0` current, `1` behind, `2` cannot-determine (missing marker, unknown commit, or unreachable remote — never a false "current"). This runs inside a cloud session on any consuming repo.

To keep a consuming repo's project install fresh automatically, copy [`examples/sync-constellation-skills.yml`](examples/sync-constellation-skills.yml) into `.github/workflows/`. It runs weekly (and on demand), rebuilds the project-scope skills from `main`, reports template reconciliation status with `check_skill_freshness.py`, and opens a PR only when something changed. It never runs `--update-baseline`: reconciling a customized template stays a human decision made on that PR.

## Baseline assumptions

Constellation assumes a Git repo, Markdown docs, and file-based workflow state. Charter clarifies issue tracker, structural map generation, CI, and runtime commands.

## This repo's own agent context

Constellation dogfoods itself. Agents working in **this** repo read these thin project deltas on top of their inherited global doctrine — layered, never merged. Each is tiered to its audience, and placing content at a broader tier than its audience is a defect rather than a delivery win.

- [docs/agents/ORCHESTRATOR_CONTEXT.md](docs/agents/ORCHESTRATOR_CONTEXT.md) — planning and gate authority (Admiral, Commander)
- [docs/agents/CREW_CONTEXT.md](docs/agents/CREW_CONTEXT.md) — implementation and review rules (Implementer, Reviewer, Prototyper)

## Structural map validation

Build or check Cartographer map artifacts:

```powershell
python scripts/build_architecture_map.py --root . --source-root src
python scripts/build_architecture_map.py --root . --source-root src --check
```

## Recommended durable artifacts

Decision anchors live in `docs/architecture/decisions/` when current-structure rationale is worth preserving.

```text
AGENTS.md                          # root pointer -> docs/agents/AGENT_GUIDE.md
CLAUDE.md                          # root pointer -> docs/agents/AGENT_GUIDE.md

docs/
  agents/
    AGENT_GUIDE.md                 # single repo-orientation guide (TOC, repo layout, doc map)
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

  AGENT_FEEDBACK.md                # unified run retrospective; persists across work-ids, never archived
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

- `docs/agents/AGENT_GUIDE.md` is the single repo-orientation guide (repo layout, documentation map, conventions) — the shared middle of Orchestrator and Crew context. Root `AGENTS.md` and `CLAUDE.md` are thin pointers to it; keep guidance in the guide, not the pointers.
- `.agent-work/AGENT_FEEDBACK.md` is the unified run retrospective. Commander appends one entry per run before archive; it persists across work-ids and is never moved into `archive/`. Use it to improve doctrine over time, not as project truth.
- If it is in `docs/`, it is meant to guide future workflows.
- If it is in `.agent-work/templates/`, it is the project-owned template catalog. Agents prefer `.agent-work/templates/<template-name>` and fall back to bundled `templates/<template-name>`.
- If it is in `.agent-work/`, it is temporary workflow state or archived history.
- Workflow status language follows `skills/workbench/references/status-model.md`.
- execute.json = Commander's frozen gate plan; three tasks per gate (implement/review/integrate); authored at plan time and never edited mid-run.
- Default Checklist = fallback controller when a role does not ship its own checklist (e.g. Crew multi-step recovery). Never both a role checklist and Default Checklist for the same work.
- Charter seeds and updates project templates when project doctrine changes checklist or handoff interfaces.
- Commander closes the complete `.agent-work/<work-id>/` package to `.agent-work/archive/<date>-<work-id>/` at archive, including interrogation sessions.
- Archived workflow artifacts are historical context only.
- Do not read archived workflow artifacts unless the user points there.
- Future-agent truth must be promoted to durable artifacts.
