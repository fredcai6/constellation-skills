# Constellation Overview

```text
Charter      -> interrogates engineering doctrine and compiles agent-operable context
Workbench    -> manages recoverable workflow state
Cartographer -> maintains current-only structural map
Conductor    -> shapes work and delegates execution
Crew         -> implements and reviews bounded changes
Triage       -> packages future work as issue-ready recommendations
```

## Context separation

High-level agents use project purpose, user intent, structural map packets, glossary, and workflow artifacts.

Low-level agents receive a bounded task, allowed scope, critical rules, relevant structural packet, required evidence, and stop conditions.

## Truth layers

```text
Code, tests, configs, generated behavior:
  dense truth

Structural map packets, agent context, glossary:
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
