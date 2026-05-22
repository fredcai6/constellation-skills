# Constellation Overview

```text
Charter      → establishes project ground rules
Workbench    → manages recoverable workflow state
Cartographer → verifies current architecture truth
Conductor    → shapes work and delegates execution
Crew         → implements and reviews bounded changes
Triage       → packages future work as issue-ready recommendations
```

## Context separation

High-level agents use project purpose, user intent, architecture packets, glossary, routing rules, and workflow artifacts.

Low-level agents receive a bounded task, allowed scope, critical rules, relevant architecture packet, required evidence, and stop conditions.

## Truth layers

```text
Code, tests, configs, generated behavior:
  dense truth

Architecture packets, agent context, glossary:
  compressed durable truth

Framing notes, gated plans, handoffs, local todos:
  workflow-local truth

Issues:
  future work
```

## Authority transfer

Agent action should trace to one of:

- explicit user decision
- existing project ground rule
- task-specific delegation
- named conservative default
- unresolved assumption

Only the first three are strong authority.
