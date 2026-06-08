# Cartographer Map Model

Cartographer maintains a current-only, multidimensional map of how the system works now. It is a sparse graph: a structural hierarchy plus capability, event, constraint, assumption, decision, and claim overlays. Architecture and code are one hierarchy; the other dimensions hang off it so Commander can plan from the map before spelunking code.

## Doctrine

- Architecture and code are one hierarchy; everything else anchors to it.
- The map is current-only; future work routes to Triage.
- The map is sparse. Every durable node and edge has a maintenance cost; it earns its place only when it helps future planning, boundary correctness, rule preservation, or trust.
- Intent is not isomorphic to structure. Most purpose stays as local packet prose; promote it to a `capability:` only when shared or cross-cutting.
- Constraints and assumptions are kept only when they materially govern current structure.
- Rationale is captured as `claim:` overlays for short verifiable assertions, or `decision:` anchors when it needs authority, consequence, and a review trigger.

## Inclusion Rule

Add a durable node or edge only when it helps at least one of:

- **Planning** — Commander can scope or sequence work from the map without reading the code first.
- **Boundary correctness** — keeps ownership, dependency direction, or a non-owner boundary right.
- **Rule preservation** — keeps a constraint, assumption, or decision from being silently violated.
- **Trust** — records what is verified, by what, and how far it can be trusted.

If a candidate node/edge serves none of these, leave it as local packet prose or route it to Triage.

## Node Kinds

Durable node kinds:

```text
struct:       a structural node in the one hierarchy (system down to function)
capability:   a current, observable thing the system does
event:        a current, named signal/message a struct or capability emits
constraint:   a rule that materially governs current structure
assumption:   a relied-upon current condition that, if false, breaks structure
decision:     an authoritative rationale anchor (see decision template)
claim:        a short, verifiable assertion about current behavior or trust
```

`struct:` is the spine. The others are overlays that anchor to structs (directly or through each other). Keep all kinds sparse.

### Structural Levels

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

### Overlay Node Shape

`capability:`, `event:`, `constraint:`, `assumption:`, `decision:`, and `claim:` nodes share a minimal shape:

```yaml
id: <kind>:<stable-id>
kind: capability | event | constraint | assumption | decision | claim
parent: <same-kind id> | null
label: <short label>
summary: <why this matters now, optional; required for claim/decision>
```

Each overlay node anchors to at least one `struct:` through an edge (below). This skeleton fixes the kinds and minimal shape only. The deep capability/event capture model is defined elsewhere (capability authoring + Interrogator wiring); deep decision-anchor fields live in the decision template.

## Edge Types

Durable edge types:

```text
supports        capability/struct -> capability     (this helps provide that capability)
depends-on      struct -> struct                    (consumer -> provider)
emits           struct/capability -> event          (this produces that event)
constrained-by  node -> constraint | assumption     (this is governed by that rule/assumption)
explained-by    node -> decision                    (this is explained by that decision anchor)
verified-by     node | claim -> claim               (this is backed by that verifiable claim/evidence)
```

Edge semantics:

- `supports` — a struct or another capability contributes to a capability. Direction is contributor -> capability.
- `depends-on` — consumer -> provider structural dependency. Generated dependency evidence may live in `map.json`; do not add edge types for imports or call detail.
- `emits` — a struct or capability produces a named event. Direction is producer -> event.
- `constrained-by` — a node is governed by a constraint or assumption. Direction is governed node -> constraint/assumption.
- `explained-by` — a node's current shape is explained by a decision anchor. Direction is node -> decision.
- `verified-by` — a node or claim is backed by a claim that points at evidence. Direction is subject -> claim. This is the trust dimension; it is not formal traceability.

Edge metadata:

```yaml
source: <node id>
target: <node id>
type: supports | depends-on | emits | constrained-by | explained-by | verified-by
provenance: curated | generated
evidence:
  - <path, command, or scanner note>
confidence: high | medium | low | unknown
```

Provenance is metadata, not a separate model.

## Overlay Schema

Durable overlays live in `docs/architecture/overlays/*.yml`. Each section holds nodes of one kind; the `relationships` section holds edges.

```yaml
capabilities:
  - id: capability:<stable-id>
    kind: capability
    parent: capability:<parent-id> | null
    label: <short label>

events:
  - id: event:<stable-id>
    kind: event
    parent: null
    label: <short label>

constraints:
  - id: constraint:<stable-id>
    kind: constraint
    parent: capability:<id> | constraint:<id> | null
    label: <short label>

assumptions:
  - id: assumption:<stable-id>
    kind: assumption
    parent: null
    label: <short label>
    summary: <what is relied on, and what breaks if false>

claims:
  - id: claim:<stable-id>
    kind: claim
    parent: null
    label: <short label>
    summary: <the verifiable assertion and how it is checked>

relationships:
  - source: struct:<id>
    type: supports | emits | constrained-by | explained-by | verified-by
    target: capability:<id> | event:<id> | constraint:<id> | assumption:<id> | decision:<id> | claim:<id>
    provenance: curated
    evidence:
      - <path>
```

`decision:` nodes are authored as decision anchor files (below), not overlay sections; overlays reference them via `explained-by` edges. Status is metadata only. Tests/checks are evidence inputs and feed `claim:` nodes; they are not their own durable node kind.

## Migration From Prior Ontology

The prior model used `purpose:` and `rationale:` overlay kinds with `serves` edges. This model replaces them:

- `purpose:` -> `capability:`. The `purposes:` overlay section becomes `capabilities:`, and `serves` edges become `supports`.
- `rationale:` folds into `decision:` and `claim:`. Short verifiable rationale becomes a `claim:` (reached via `verified-by` or `explained-by`); authoritative rationale becomes a `decision:` anchor reached via `explained-by`. The `rationales:` overlay section and `rationale:` ids are removed.

Existing overlays that still use `purpose:`/`rationale:`/`serves` must be migrated before validation passes. No such overlays exist in this repo yet, so there is nothing to migrate here; downstream repos adopting this model rename their sections and edges as above.

## Packet Role

Architecture packets are dense agent pages for structural nodes. Packets are the primary durable agent pages. They are current-only, Markdown-first, and optimized for information density over prose polish.

Manual packets are authoritative agent context, but they are not mechanically trusted unless validation/generation is configured and passing. Record manual traceability as drift risk, not as proof that code and map cannot diverge.

Spec replacement is conditional. Packets can replace specs only when duplicate module READMEs/spec docs are retired or explicitly demoted. If another document remains canonical for the same node, record `parallel canonical docs` and hand retirement or merge decisions to Triage unless the user delegated that authority.

Packets may cover system-context, container, component, code-path, or significant module nodes. Most module/file leaves can remain generated source-scan nodes until they need curated responsibility, constraints, or trust limits.

Work packet-first: when mapping a scope, reconcile packets for touched structural nodes before expanding index and overlay ceremony. Index and overlays support navigation, shared anchors, and map consistency; they should not become a second packet registry or narrative work log.

## Decision Anchors

Decision anchors live in `docs/architecture/decisions/*.md` and back `decision:` nodes. They are not a history log, ADR archive, migration diary, or backlog. Use them only for key rationale that materially governs current structure and would be costly to rediscover from code, packets, and overlays.

Decision anchors are sparse durable context. Link them from packets and overlays via `explained-by`. Short rationale should usually be captured as `claim:` overlays; use a decision file only when the rationale needs authority, consequence, and review-trigger fields. Each decision must name structural anchors, current structural consequence, authority, and a review trigger. Detailed decision-anchor capture is defined in the decision template.

## Generated Map Contract

When configured, generated map artifacts combine packets, overlays, and repo source tree into:

```text
docs/architecture/generated/map.json
docs/architecture/generated/nodes/
docs/architecture/generated/index.md
```

Validation must report duplicate IDs, missing parents, stale structural node references, unmapped modules, disallowed node kinds, disallowed edge types, overlay nodes without a structural anchor, and stale generated map artifacts.

If parent resolution fails for a source file, include it under `struct:unmapped_modules` with low confidence and record the mismatch.

## Out Of Scope

Cartographer maps current capabilities, events, and the use cases the system supports now. It does not map unanchored requirements, future use cases, exhaustive scenario or failure-mode matrices, historical logs, migration diaries, or backlog. It does not maintain future architecture plans, review proof archives, or formal traceability. Current code/constraint violations are recorded as current truth and routed to Triage when remediation is future work.
