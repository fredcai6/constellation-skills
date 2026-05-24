# Cartographer Map Model

Cartographer maintains a current-only structural map with sparse purpose and constraint overlays. Architecture and code are one hierarchy, not separate dimensions.

## Doctrine

- Architecture and code are one hierarchy.
- Intent is not isomorphic to structure.
- Purpose usually stays as local packet prose.
- Promote purpose only when shared or cross-cutting.
- Constraints are sparse and used only when they materially govern structure.
- Everything is current-only; future work routes to Triage.

## Structural Levels

Use C4-style levels in one hierarchy:

```text
system-context
container
component
code-path
module/file
function-or-method
```

`module/file` is the default minimum map level. `function-or-method` is optional, generated, and light.

Structural node shape:

```yaml
id: struct:<stable-id>
level: system-context | container | component | code-path | module | function-or-method
parent: struct:<parent-id> | null
path: <repo path, if applicable>
symbol: <symbol, if applicable>
purpose: <short local purpose, optional>
status: current | partial | stale | disputed
confidence: high | medium | low | unknown
```

Store only `parent`. Descendants, breadcrumbs, ownership views, and inverse views are derived.

Scan-only module nodes are still real map nodes. Default `status: current`; use `confidence: medium` when parent is derivable and `confidence: low` under `struct:unmapped_modules`.

## Relationships

Allowed relationship types:

```text
depends-on
serves
constrained-by
```

`depends-on` direction is consumer -> provider. `serves` links `struct:*` to `purpose:*`. `constrained-by` links `struct:*` to `constraint:*`.

Relationship metadata:

```yaml
source: struct:<id>
target: struct:<id> | purpose:<id> | constraint:<id>
type: depends-on | serves | constrained-by
provenance: curated | generated
evidence:
  - <path, command, or scanner note>
confidence: high | medium | low | unknown
```

Relationship provenance is metadata, not a separate model. Generated dependency evidence may live in `map.json`; do not create additional relationship types for imports or call detail.

## Overlay Schema

Durable overlays live in `docs/architecture/overlays/*.yml`.

```yaml
purposes:
  - id: purpose:<stable-id>
    kind: purpose
    parent: purpose:<parent-id> | null
    label: <short label>

constraints:
  - id: constraint:<stable-id>
    kind: constraint
    parent: purpose:<id> | constraint:<id> | null
    label: <short label>

relationships:
  - source: struct:<id>
    type: serves | constrained-by
    target: purpose:<id> | constraint:<id>
    provenance: curated
    evidence:
      - <path>
```

Do not add other overlay kinds. Status is metadata only. Tests/checks are evidence inputs and packet context only; they are not durable map nodes.

## Packet Role

Architecture packets are dense agent pages for structural nodes. They are current-only, Markdown-first, and optimized for information density over prose polish.

Packets may cover system-context, container, component, code-path, or significant module nodes. Most module/file leaves can remain generated source-scan nodes until they need curated responsibility, constraints, or trust limits.

## Generated Map Contract

When configured, generated map artifacts combine packets, overlays, and repo source tree into:

```text
docs/architecture/generated/map.json
docs/architecture/generated/nodes/
docs/architecture/generated/index.md
```

Validation must report duplicate IDs, missing parents, stale structural node references, unmapped modules, disallowed relationship types, purpose without structural anchor, constraint without structural anchor, and stale generated map artifacts.

If parent resolution fails for a source file, include it under `struct:unmapped_modules` with low confidence and record the mismatch.

## Out Of Scope

Cartographer does not maintain requirement, use case, invariant, failure mode, event, actor, consumer, status, test, or evidence node kinds. It does not maintain future architecture plans, migration diaries, backlog, review proof, runtime behavior, or formal traceability. Current code/constraint violations are recorded as current truth and routed to Triage when remediation is future work.
