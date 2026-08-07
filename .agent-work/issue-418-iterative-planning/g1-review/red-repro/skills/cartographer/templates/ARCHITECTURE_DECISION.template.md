# Architecture Decision: `<short current-structure decision>`

Use only when the decision materially explains current structure and would be costly to rediscover. Prefer `claim:<id>` overlays for short rationale. Omit optional sections when empty.

## Status

**Decision id:** `decision:<stable-id>`  
**Status:** `current | superseded | disputed`  
**Date decided:** `<YYYY-MM-DD>`  
**Authority:** `user decision | delegated | repo artifact | accepted default`  
**Structural anchors:** `struct:<id>[, struct:<id>]`  
**Capability anchors:** `capability:<id>[, capability:<id>]` (optional; the current capabilities this decision shapes)

## Question Resolved

`<the open question this decision closes — what was in contention>`

## Decision

`<chosen rule, boundary, parent, dependency, ownership, or constraint>`

## Rationale

- `<why this choice governs current structure>`

## Current Structural Consequence

- `<what agents should do differently because this decision exists>`

## Constraint Impact

- `constraint:<id>` (optional): `<constraint this decision creates, relaxes, or is bound by>`

## Rejected Alternatives

Preserve an alternative ONLY when a future agent is likely to rediscover or re-propose it, or to violate this decision by reaching for it. Omit obvious or merely-historical roads not taken.

- `<alternative>`: `<why not current, and why it would otherwise be re-reached for>`

## Review Trigger

- `<code/doc/constraint change that should reopen this decision>`
