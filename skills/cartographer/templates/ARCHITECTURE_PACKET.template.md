# Architecture Packet: `<structural node label>`

Dense current-only agent context. Omit optional sections when empty.

## Status

**Structural node:** `struct:<id>`  
**Level:** `system-context | container | component | code-path | module`  
**Parent:** `struct:<parent-id> | none | struct:unmapped_modules`  
**Status:** `current | partial | stale | disputed`  
**Confidence:** `high | medium | low | unknown`  
**Last reconciled:** `<YYYY-MM-DD>`

## Purpose

`<short local purpose; present tense>`

## Current responsibility

- `<owned responsibility>`

## Does not own

- `<explicit non-owner boundary>`

## Primary users/callers

- `<struct:<id> or caller label>`

## Inputs

- `<input>`

## Outputs

- `<output>`

## Canonical data/control path

```text
<dense current flow>
```

## Dependencies

Direction: consumer -> provider. Relationship type: `depends-on`.

- `struct:<consumer>` -> `struct:<provider>`; provenance `<curated | generated>`; confidence `<level>`; evidence `<path/note>`

## Forbidden or suspicious dependencies

- `<dependency direction and why suspicious>`

## Primary code paths

- `<path>`

## Primary tests/checks

- `<local checks that help verify this structural node; no durable test nodes>`

## Primary configs

- `<path>`

## Purpose / constraint anchors

**Serves:**
- `purpose:<id>`

**Constrained by:**
- `constraint:<id>`

## Generated map links

- `docs/architecture/generated/map.json`
- `<generated node page, if configured>`

## Trust limitations

- `<current caveat affecting trust; route action to Triage>`

## Notes

- `<current-state clarification only>`
