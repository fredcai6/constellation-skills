# Agent Guide

Orientation for any agent working in this repository: **what this project is for, and where everything
lives.** Root pointer files (`AGENTS.md`, `CLAUDE.md`) redirect here so there is one guide, not many.

## Why This Exists

Constellation writes down how work gets done, so an agent follows a known sequence instead of deriving
one each run. A team catches what one agent misses, so it splits work across tiers: orchestrator roles
plan and dispatch, crew roles implement and verify, and the human sits at the top tier. No role verifies
its own work — review goes to a role with fresh context. Rigor is the default, not a knob.

Rigor costs ceremony. The return is consistency and traceability: an agent that knows where it is, what
it inherited, and what it hands off spends its attention on the development instead of on tracking.

Humans own intent, values, priorities, and authority. Agents settle intent and latitude with the human
rather than inferring it without asking.

- **Produces:** the skill corpus, the checklist engine it runs on, and the scripts that keep both honest.
- **For:** agents doing engineering work in other repos. `scripts/install_constellation.py` bundles each
  skill into an agent's skills root.
- **Not this:** a replacement for human judgment. Nor a guard against bad actors or unlikely events —
  mechanism here exists to save an agent effort, not to protect against rare failures.
- **Cardinal sin — ambiguity.** Conflicting instructions, and mechanism elaborate enough to need its own
  explanation. Every addition should make "here is how work is done" shorter to state, not longer.

## Repository Organization

Constellation has two shapes. **In this repo** a skill is `skills/<name>/` and the shared machinery sits
once at `scripts/`. **Installed**, `scripts/install_constellation.py` bundles each skill's `SKILL.md`,
`references/`, `templates/`, and `scripts/` into a self-contained `constellation-<name>/` under the
agent's skills root, copying shared machinery into every bundle. So `skills/diagnose/` becomes
`constellation-diagnose/` — same skill, two names.

| Path | Holds |
|---|---|
| `skills/` | the corpus: 20 skills, one directory each. `skills/_shared/` is **not** a skill — it is doctrine that several skills bundle. |
| `scripts/` | shared machinery: checklist engine, installer, verifiers, code-map builder. Installed skills get copies. |
| `tests/` | pytest suite over the machinery and the corpus |
| `evals/` | end-to-end skill runs with checkable answers |
| `specs/` | role spine definitions consumed by the engine |
| `examples/` | reference wiring: the MCP demo and the CI sync workflow |
| `episodes/` | continuous self-improvement. When a run hits a challenge, it records what happened — one file per record, written only through `scripts/apply_episode_delta.py`. A record, never a rule. |
| `map/` | the generated code map. Only `INDEX.md` and `ids.jsonl` are tracked; rebuild the rest with `python -m scripts.code_map build`. |
| `docs/` | durable documentation — see the map below |

New durable documentation goes in `docs/`. Root-level `notes-*.md` are working notes from past runs, not
guidance.

## Documentation Map

| Document | Source of truth for |
|---|---|
| `docs/agents/AGENT_GUIDE.md` | this guide — project purpose, repo layout, documentation map |
| `docs/agents/GLOSSARY.md` | project terms whose meaning here differs from the obvious reading |
| `docs/CONSTELLATION_OVERVIEW.md` | how the pieces fit: the layers and what each is for |
| `docs/CHECKLIST_SCHEMA.md` | the shipped checklist format the engine reads |
| `docs/CHECKLIST_ENGINE_DESIGN.md` | the engine's design model |
| `docs/EPISODE_STORE.md` | record grammar and store doctrine |
| `docs/GAUGE_WRITER_HOOK.md` | the context governor's write side |
| `docs/DEBT_SWEEP_CADENCE.md` | keeping the cross-project feedback sweep current |
| `docs/REMOVABILITY_LEDGER.md` | which installed externals are still load-bearing |
| `docs/architecture/` | generated structural map artifacts |
| `map/INDEX.md` | code-map entry point |

## Build, Test, and Run

Use `python`, not a versioned or platform-specific interpreter name.

```text
python -m pytest tests/                    # full suite
python scripts/install_constellation.py --agent claude --scope user --dry-run
python scripts/verify_retirement.py        # retirement + store-mention guards
python scripts/curate_corpus.py            # corpus health measurement
python -m scripts.code_map build           # rebuild the code map under map/
python scripts/build_architecture_map.py --root . --source-root src --check
```
