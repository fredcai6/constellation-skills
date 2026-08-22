# Agent Guide

Orientation for any agent working in this repository: **what this project is for, and where everything
lives.** Root pointer files (`AGENTS.md`, `CLAUDE.md`, and any tool-specific equivalents) redirect here so
there is one guide, not many.

Scope is deliberately narrow. This guide does **not** cover how to approach the job — no planning,
evidence, verification, review, authority, or workflow doctrine. That arrives with whatever skills an
agent is running, and each skill routes its own role to its own context. Do not restate it here and do
not point at it; duplicated method is conflicting method.

Write it so an agent that has never seen this repo, running no particular workflow, can orient in one
read. Agent-facing: bullets, tables, fragments. Omit anything that does not help an agent find its way
around. Hold the prose to `constellation-how-to-talk` — plainest word that carries the meaning, one
point per sentence. Say more with less; a baggy guide stops getting read.

Every sentence must stand on its own. No allusions to books, methodologies, or other products: a
reader who does not catch the reference gets nothing, and a reader who does gets tone rather than
meaning. Name the thing you mean. Technical terms with a precise, findable definition are fine;
rhetorical shorthand is not.

## Why This Exists

`<What this project is for, in plain language — two or three sentences. Assume the reader knows the
technology but nothing about this project or its domain. Lead with the point, not the mechanism.>`

- **Produces:** `<the thing it actually makes>`
- **For:** `<who or what consumes the output, and what decision or action it feeds>`
- **Not this:** `<the adjacent things it is deliberately not. These are the boundaries that stop scope
  drift, so name the plausible mistakes, not implausible ones.>`
- **Measured by:** `<omit unless the project has a concrete bar it is judged against — the metric, the
  target, and where it currently stands.>`

## Repository Organization

`<Top-level layout: what lives where. Keep to directories an agent must know to orient. Where placement
is not obvious from the path, say what belongs there — and what does not.>`

| Path | Holds |
|---|---|
| `<src/ or equivalent>` | `<production code — and where a new module of each kind goes>` |
| `<tests/>` | `<test suites, and how they are divided>` |
| `docs/` | `<durable documentation; see Documentation Map>` |
| `<scripts/ or tooling>` | `<build and dev tooling>` |
| `<data/ or artifacts>` | `<what is generated vs committed, and which paths are canonical>` |
| `.agent-work/` | `<workflow state and archived history — temporary and historical, never project truth>` |

## Documentation Map

Where the important documents live and what each is the source of truth for. One row per document that
an agent could otherwise get wrong by guessing.

**This guide is for agents; `README.md` is for humans.** Do not route agents to the README — list the
docs an agent works from. The two overlapping on purpose is fine: same facts, different audience, each
written for its own reader.

| Document | Source of truth for |
|---|---|
| `docs/agents/AGENT_GUIDE.md` | this guide — project purpose, repo layout, documentation map |
| `docs/agents/GLOSSARY.md` | `<project terms — the ones whose meaning here differs from the obvious reading>` |
| `docs/architecture/index.md` | current structural map entry point |
| `docs/architecture/packets/` | per-node structural truth and constraints |
| `docs/architecture/decisions/` | preserved architecture rationale |
| `<other canonical doc>` | `<what it owns>` |

## Build, Test, and Run

**Portable entry points only.** Give the command that works on any machine this repo is worked on. Never
encode one operating system's invocation — no `py` vs `python3`, no shell-specific syntax, no
absolute paths. If a step has no portable entry point, that is a repo defect worth an issue, not a
caveat here.

Universal commands only. Area-specific commands belong in handoffs, not in this guide.

```text
<build command>
<test command>
<lint/format command>
<run/serve command>
```
