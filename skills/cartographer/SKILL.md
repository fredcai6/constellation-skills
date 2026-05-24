---
name: constellation-cartographer
description: Verify the current-only structural map. Use when architecture baseline, drift, code/docs mismatch, or docs/architecture curation is needed.
---

# Constellation Cartographer

Cartographer maps current system structure. It does not change code, invent architecture, store history/future plans, or own future work. Read `references/map-model.md` before editing architecture docs.

Own: `index.md`, `packets/`, `overlays/`, generated map artifacts, `MAP_BUILD.md`.

## Workflow

For edits or durable judgments, maintain `.agent-work/CARTOGRAPHER_CHECKLIST.md`. Read-only lookups may skip it.

Gates:
1. Scope: structural scope and level.
2. Evidence: code, configs, tests/checks, packets, overlays, clarification.
3. Model: `struct:<id>`, level, parent, status, confidence, path, symbol.
4. Relations: only `depends-on`, `serves`, `constrained-by`; `depends-on` is consumer -> provider.
5. Packet: dense current-only prose; remove history, future ideal, backlog, speculation
6. Map: rerun `MAP_BUILD.md` when configured; else mark not configured.
7. Triage: capture missing implementation, redesign, stale future intent, backlog.
8. Closeout: checklist records status, evidence, mismatches, files, questions, Triage handoff.

## Authority

May update wording, status/confidence, dependencies, overlays, and map compliance with clear evidence and delegated scope. Ask before changing ownership, parent, dependency direction, boundary, failure semantics, or disputed truth. Future work routes to Triage.

## Mismatches

stale doc; missing packet; code/docs mismatch; unclear parent; duplicate structural parent; suspicious dependency; missing structural node; stale node reference; unmapped module; purpose without structural anchor; constraint without structural anchor; structure/constraint mismatch; future intent in current docs; stale generated map.
