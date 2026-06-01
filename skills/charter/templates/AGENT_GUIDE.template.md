# Agent Guide

Single entry point for any agent working in this repository — Constellation roles and external/general agents alike. Root pointer files (`AGENTS.md`, `CLAUDE.md`, and any tool-specific equivalents) redirect here so there is one guide, not many.

Scope is deliberately narrow: **how this repo is organized and where the important documentation lives** — the shared middle of Orchestrator and Crew context. It does *not* cover how to approach the job. For that:

- Planning, authority, gating, evidence, stop/ask → `docs/agents/ORCHESTRATOR_CONTEXT.md`
- Implementation, verification, review/blocking, stop/report → `docs/agents/CREW_CONTEXT.md`
- Shared terms → `docs/agents/GLOSSARY.md`

Agent-facing. Bullets, tables, fragments. Omit anything that does not help an agent find its way around.

## Table of Contents

1. [Repository Organization](#repository-organization)
2. [Documentation Map](#documentation-map)
3. [Conventions](#conventions)
4. [Build, Test, and Run](#build-test-and-run)
5. [Workflow State](#workflow-state)
6. [Where to Go Next](#where-to-go-next)

## Repository Organization

`<Top-level layout: what lives where. Keep to directories an agent must know to orient.>`

| Path | Holds |
|---|---|
| `<src/ or equivalent>` | `<production code>` |
| `<tests/>` | `<test suites>` |
| `docs/` | `<durable documentation; see Documentation Map>` |
| `<scripts/ or tooling>` | `<build/dev tooling>` |
| `.agent-work/` | `<workflow state; see Workflow State>` |

## Documentation Map

Where the important documents live and what each is the source of truth for.

| Document | Source of truth for |
|---|---|
| `README.md` | `<project overview, install, top-level usage>` |
| `docs/agents/AGENT_GUIDE.md` | this guide — repo orientation and the documentation map |
| `docs/agents/ORCHESTRATOR_CONTEXT.md` | planning, authority, gating, evidence, stop/ask |
| `docs/agents/CREW_CONTEXT.md` | implementation, verification, review/blocking, stop/report |
| `docs/agents/GLOSSARY.md` | shared terms |
| `docs/architecture/index.md` | current structural map entry point |
| `docs/architecture/packets/` | per-node structural truth and constraints |
| `docs/architecture/decisions/` | preserved architecture rationale |
| `<other canonical doc>` | `<what it owns>` |

## Conventions

`<Repo-wide conventions an agent must follow to fit in. Naming, formatting, where things go. Omit lines that do not change agent action.>`

- **Branching / commits:** `<branch off main; commit cadence; PR vs direct>`
- **Naming:** `<file, module, or work-id naming rules>`
- **Where new code goes:** `<placement rules by kind>`
- **Where new docs go:** `<durable vs workflow-local>`

## Build, Test, and Run

Universal commands only. Area-specific commands belong in handoffs, not here.

```text
<build command>
<test command>
<lint/format command>
<run/serve command>
```

## Workflow State

- Temporary workflow state and archived history live under `.agent-work/` (see `docs/agents/` skills for the full layout). Treat it as recoverable state, not project truth.
- The unified agent feedback log at `.agent-work/AGENT_FEEDBACK.md` accumulates run retrospectives across work-ids; it persists and is never archived with a single run.
- If it is in `docs/`, it is meant to guide future work. If it is in `.agent-work/`, it is temporary or historical.

## Where to Go Next

- Orienting / finding a file or doc → you are in the right place.
- Planning or shaping work → `docs/agents/ORCHESTRATOR_CONTEXT.md`.
- Implementing or reviewing a bounded change → `docs/agents/CREW_CONTEXT.md`.
- Understanding current structure before changing it → `docs/architecture/index.md`.
