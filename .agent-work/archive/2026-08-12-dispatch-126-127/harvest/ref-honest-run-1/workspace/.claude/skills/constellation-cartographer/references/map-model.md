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

Each overlay node anchors to at least one `struct:` through an edge (below). This skeleton fixes the kinds and minimal shape only. The deep capability/event capture model is the Capability Model (below); deep decision-anchor fields live in the decision template.

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

## Capability Model

The `capability:` node is the primary durable behavior abstraction. It is the behavior-facing anchor in the map: planning, ambiguity resolution, and review all frame behavior as capabilities, not as loose requirements or use cases. A capability is a current, observable thing the system does, named once and reused. Structure (`struct:`) answers *where*; the capability answers *what the system does* there.

### What a capability captures

A capability node carries a `label` and a short present-tense `summary` describing what the system does now. Everything else hangs off it through edges and child overlays, kept only when it earns its place:

- **Examples / use cases** — concrete instances of the capability in use, recorded under the capability (below), never as standalone requirements.
- **Important events** — `event:` nodes the capability emits, via `emits`, only when architecturally meaningful (below).
- **Supporting structures** — `struct:` (or sub-capability) nodes that contribute, via `supports`.
- **Governing constraints/assumptions** — via `constrained-by`.
- **Decision / rationale anchors** — via `explained-by` to a `decision:`.
- **Claims / evidence** — via `verified-by` to a `claim:`.
- **Trust limitations** — recorded as packet `Trust limitations` prose or a `claim:`, not as a new kind.

The capability adds no new fields beyond the overlay shape; the richness lives in the edges and the examples-under-capability prose. Keep the description present-tense and observable ("validates and persists the order"), never future or aspirational ("will support batch orders").

### Examples under capabilities

Use-case examples are allowed only as examples *under* a capability, never as unanchored requirements or a standalone scenario catalog. An example is concrete behavior prose attached to its capability — in the owning packet's capability context or as a short note on the overlay node — that makes the capability's scope or an edge case legible for planning or review.

- Record an example only when it sharpens what the capability does or does not cover; drop it once the capability description makes it obvious.
- An example never becomes its own durable node and never anchors structure by itself. If an example implies future behavior, it routes to Triage, not the map.
- This is not a Gherkin/Cucumber workflow and not an exhaustive scenario matrix (see Out Of Scope).

### When an event is architecturally meaningful

An `event:` anchor is allowed only when the event is architecturally meaningful — not for every runtime event, log line, or internal call. An event earns a durable node only when it passes the Inclusion Rule through one of:

- it **crosses a boundary** (container/component/ownership) such that a consumer depends on it, or
- it is a **named contract** other structures observe or react to, or
- it **materially shapes planning** because work must account for who emits or consumes it.

Ordinary intra-struct events, transient signals, and incidental logging stay as packet prose. When in doubt, leave the event out; promote it only when a consumer or planning step would otherwise miss it.

### Promotion: when capability/event context becomes durable map truth

Most behavior context stays as local packet prose. It becomes a durable `capability:` or `event:` node only when it is current and crosses the Inclusion Rule:

- **Promote a capability** when the behavior is shared or cross-cutting — referenced by more than one struct, planned against, or governing a constraint/decision. A behavior local to one struct stays as that packet's `Purpose`/responsibility prose until it is reused.
- **Promote an event** when it is architecturally meaningful by the test above.
- **Keep examples as prose** under the owning capability; never promote an example to a node.
- **Reject or route** behavior that is obvious from structure (leave as prose), historical (drop it), or about future behavior (route to Triage). This keeps the behavior overlay sparse.

Promotion records current truth only. A capability or event node is reconciled like any node: when the behavior changes, update or retire the node; when it becomes future work, route it to Triage rather than leaving stale behavior on the map.

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

### Candidate vs Anchor

A decision **candidate** is a why-context signal raised during a run — by Commander when it forces a choice to the human, or returned as decision pressure or evidence from Implementer/Reviewer. A candidate is not yet durable; it is a claim that a decision may govern current structure. A durable decision **anchor** is the promoted subset: only candidates that govern current structure, capabilities, constraints, or future planning behavior become anchor files. Most candidates resolve into packet prose or a `claim:` overlay and never become anchors.

### Promote, Reject, or Route

When reconciling decision candidates, the Cartographer does exactly one of:

- **Promote** to a decision anchor when the rationale governs current structure/capabilities/constraints, carries authority, and would be costly to rediscover from code, packets, and overlays. Author it from the decision template and link it via `explained-by`.
- **Reject** (do not durably record) when the rationale is obvious from current structure, is short and verifiable — capture it as a `claim:` instead — or is merely historical. Rejection keeps the map sparse.
- **Route to Triage** when the candidate is about future work, an unresolved decision, or a structure/constraint mismatch rather than current rationale. It leaves the map as an `unresolved decision` triage candidate, not an anchor.

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
