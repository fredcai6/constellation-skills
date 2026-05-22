---
name: constellation-triage
description: Convert findings, gaps, drift, and future work into issue-ready recommendations.
---

# Constellation Triage

## Purpose

Decide what needs to happen next and write issue-ready recommendations. Triage does not implement.

## Use when

- Cartographer finds mismatch outside current scope.
- Reviewer finds missing tests/docs/contracts outside current scope.
- Conductor identifies future work during planning.
- Implementation exposes technical debt that should not be fixed now.
- A human wants issue-ready text rather than direct issue creation.

## Classification

Classify work as one or more:

- bug
- cleanup
- missing test
- missing doc
- missing architecture packet
- architecture weakness
- feature
- tooling
- unresolved decision
- research hardening
- dependency cleanup
- security/privacy
- performance/resource

## Issue autonomy

Creating issues directly is governed by project ground rules. If issue-creation authority is unclear, produce issue-ready recommendations and ask.

## Triage questions

- What kind of follow-up is this?
- How important is it?
- Who should own it?
- Is it in scope now or future work?
- What evidence supports it?
- What would make it done?
- What is explicitly out of scope?
