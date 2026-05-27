# Cartographer Checklist

Work file: `.agent-work/CARTOGRAPHER_CHECKLIST.md`

Status values follow `skills/workbench/references/status-model.md`. Each gate closes only when its listed fields are populated and decision rationale is recorded. Skipped gates require `skipped because <reason>`.

## Target

**Structural scope:** `struct:<id> | repo region`  
**Requested outcome:** `<current-only map/packet/index/overlay reconciliation>`  
**Authority:** `<user request | existing rule | assumption needing confirmation>`  
**User intent ambiguity:** `none | resolved | unresolved`

## Scope Gate

**Status:** `pending`  
**Node level:** `system-context | container | component | code-path | module`  
**Parent candidate:** `struct:<id> | none | unclear`  
**Decision rationale:** `<why proceeding, asking, or stopping>`  
**Stop condition:** `<scope cannot map to structural level or user intent ambiguity affects durable docs>`

## Evidence Gate

**Status:** `pending`

- Code paths: `<paths>`
- Configs/runtime entries: `<paths>`
- Tests/checks: `<local checks only; no durable test node>`
- Packets/overlays: `<paths>`
- User clarification: `<decision or none>`

## Model Gate

**Status:** `pending`

| Field | Value |
|---|---|
| Structural node | `struct:<id>` |
| Level | `<level>` |
| Parent | `struct:<id> | none | struct:unmapped_modules` |
| Path | `<repo path or omit>` |
| Symbol | `<symbol or omit>` |
| Status | `current | partial | stale | disputed` |
| Confidence | `high | medium | low | unknown` |

**Decision rationale:** `<evidence supporting model choice>`

## Relationship Gate

**Status:** `pending`

| Source | Type | Target | Provenance | Confidence | Evidence |
|---|---|---|---|---|---|
| `struct:<id>` | `depends-on | serves | constrained-by` | `<id>` | `curated | generated` | `<confidence>` | `<path/note>` |

**Decision rationale:** `<why relation is current truth or why question is needed>`

## Packet Gate

**Status:** `pending`

- Packet path: `<docs/architecture/packets/*.md>`
- Current-only sections reconciled: `<yes | no>`
- Future/history/backlog removed: `<yes | no | none found>`
- Key decisions/rationale: `<decision anchors created/updated or none>`
- Dense agent context pass: `<yes | no>`

## Map Contract Gate

**Status:** `pending`

- Traceability mode: manual | validated | generated
- Drift risk: low | medium | high
- Parallel canonical docs: <paths or none>
- `MAP_BUILD.md`: `<configured | not configured>`
- Command: `<command or none>`
- Result: `<pass | fail | skipped>`
- Generated map artifacts: `<paths or none>`

## Mismatches

- `<class>: <current truth + evidence>`

## Triage Gate

**Status:** `pending`

### Triage candidate: `<short title>`

**Reason:** `future intent | missing implementation | desired redesign | stale future doc | unresolved architecture decision`  
**Structural anchor:** `struct:<id>`  
**Mismatch class:** `<Cartographer mismatch class>`  
**Current truth:** `<what exists now>`  
**Desired/future concern:** `<outside Cartographer>`  
**Evidence:** `<paths/commands reviewed>`  
**Recommended Triage action:** `<issue-ready recommendation scope>`

## Closeout Gate

**Status:** `pending`

- Files changed: `<paths>`
- Status/confidence changes: `<nodes>`
- Unresolved questions: `<questions or none>`
- Triage handoff: `<candidates or none>`
