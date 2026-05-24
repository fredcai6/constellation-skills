---
name: constellation-triage
description: Create issue-ready recommendations. Use when Conductor, Cartographer, Crew, or the user finds future work outside implementation.
---

# Constellation Triage

## Purpose

Write issue-ready recommendations for follow-up work. Triage does not implement, keep a backlog, or pull work into current scope unless asked. Persist future-work packaging in issues or workflow-local text.

## Use When

- Cartographer finds out-of-scope mismatch.
- Reviewer finds out-of-scope test/doc/contract gaps.
- Conductor finds future work during planning.
- Implementation exposes deferred debt.
- The user wants issue-ready text.

## Inputs

Consume `.agent-work/CARTOGRAPHER_CHECKLIST.md` candidates, review findings, plans, user notes, or implementation evidence. Preserve structural anchor, mismatch class, current truth, desired/future concern, evidence, and action.

## Classify

Use one or more: bug, cleanup, missing test, missing doc, missing architecture packet, missing structural node, architecture weakness, structure/constraint mismatch, stale generated map, feature, tooling, unresolved decision, research hardening, dependency cleanup, security/privacy, performance/resource.

## Issue Authority

Ground rules govern direct issue creation. If unclear, produce recommendations and ask.

## Questions

What is this? How important? Who owns it? Why future work? What evidence supports it? What makes it done? What is out of scope?
