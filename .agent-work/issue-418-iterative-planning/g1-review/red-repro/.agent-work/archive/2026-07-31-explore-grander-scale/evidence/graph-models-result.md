# Graph Models and Traversal Research

## Answer

Use an **event-backed statement multigraph**: stable entities plus individually identified statements are canonical; append-only events record assertion, ratification, dispute, supersession, and retirement; a current **attributed property-graph projection** makes those statements cheap to crawl. Declared frames are ordinary nodes with explicit participation statements, not physical graph partitions. Frame-owned shapes validate only the rigor that a local frame earns.

This is a deliberate hybrid at the logical-model level, not a recommendation to maintain an RDF store and a property-graph store in parallel:

- It takes relationship identity, properties, path values, and controllable path modes from the property-graph/GQL model. GQL's formal model gives nodes and edges identities, labels, and properties, and treats a path as an ordered alternating sequence of nodes and edges ([Francis et al., *A Researcher's Digest of GQL*, pp. 8-9](https://drops.dagstuhl.de/opus/volltexte/2023/17743/pdf/LIPIcs-ICDT-2023-1.pdf)).
- It takes globally stable predicate identity, statement-oriented semantics, and vocabulary evolution from RDF. RDF's core is a set of subject-predicate-object statements whose predicates are IRIs denoting binary relations ([RDF 1.2 Concepts, §§1.1-1.2](https://www.w3.org/TR/rdf12-concepts/#section-Graph-syntax)).
- It takes entity/activity/agent provenance and derivation vocabulary from PROV-O, which is a stable W3C Recommendation ([PROV-O](https://www.w3.org/TR/prov-o/)).
- It takes local, separately versioned validation shapes from SHACL rather than imposing a universal closed schema. SHACL can constrain cardinality, datatype, class, property paths, and closed shapes, and produces explicit validation reports ([SHACL Recommendation, §1.4](https://www.w3.org/TR/shacl/#shacl-example)).
- It permits a relational implementation or projection without changing the logical model. SQL/PGQ standardizes property-graph queries over relational representations, while GQL is the standalone property-graph language ([ISO/IEC 9075-16:2023](https://www.iso.org/standard/79473.html), [GQL/SQL-PGQ analysis](https://arxiv.org/abs/2409.01102)).

The crucial choice is not “property graph or RDF.” It is: **make each meaningful connection an attributable statement, preserve its history, and make every discovery traversal return the path that justified the result.** A pure labeled property graph is the best crawling surface but underspecifies shared semantics and provenance conventions. Pure RDF is the best interchange and semantic vocabulary surface, but SPARQL property paths hide intermediate bindings and do not return a first-class path, which is a poor default for agent explanations ([SPARQL 1.2 Query, §9.3](https://www.w3.org/TR/sparql12-query/#property-path-equivalent)). A normalized relational graph is the strongest conservative storage baseline, but should not dictate the conceptual or traversal interface.

## Required Traversal Behaviors

### One traversal contract

Every human or agent crawl should declare the same fields, whether translated to GQL-like patterns, SPARQL, recursive SQL, or an in-process traversal:

```yaml
start: [node-id]
direction: out | in | both
relations: [qualified-predicate-id]       # allow-list or regular expression
frames: [frame-id]                        # union by default; intersection explicit
epistemic_status: [ratified, observed]    # inferred/proposed lanes explicit
authority: [fred, agent-id, source-id]
as_of: timestamp | current
depth: {min: 1, max: 4}
path_mode: acyclic                        # walk | trail | acyclic | simple
selector: {kind: shortest-groups, k: 3}
stop_at: [node-kind or predicate]
order_by: [semantic-cost, path-length, recency, stable-id]
return: paths-with-explanations
```

The required defaults are `current`, bounded depth, an edge allow-list, `ACYCLIC`, and a deterministic order. Unbounded walks are opt-in. GQL distinguishes `TRAIL` (no repeated edge), `ACYCLIC` (no repeated node), `SIMPLE`, and unrestricted `WALK`, and supports shortest-path selectors; its formal restrictions explicitly avoid unbounded `ALL` output because it can be infinite ([GQL digest, pp. 6-7, 12, 17](https://drops.dagstuhl.de/opus/volltexte/2023/17743/pdf/LIPIcs-ICDT-2023-1.pdf)). Those distinctions should be part of Constellation's traversal API even if its first engine uses different syntax.

Each returned path must include:

- the ordered entity and statement IDs;
- predicate direction and frame participation;
- statement status, authority, confidence, and source artifact;
- the event or activity that created the statement;
- whether each step was explicit, inferred, or projected;
- the exact traversal specification and ranking components.

This makes “why did you show me this?” answerable without rerunning an opaque model. Path retention has a real space cost in procedural traversal engines, and result ordering is not necessarily implicit, so explanations and ordering must be requested deliberately ([Apache TinkerPop reference: traverser and `path()`](https://tinkerpop.apache.org/docs/current/reference/#_the_traverser)).

### Concrete idea-discovery traversals

1. **Connect a raw thought to nearby prior thinking.**

   Start at `thought:new`, traverse both directions over `expresses | questions | supports | contradicts | qualifies | implies | derived-from`, within the union of `journal` and `philosophy`, through active observed/ratified statements, maximum depth 3. Return the three lowest-cost path groups, where generic relations cost more than specific ones. The result is not merely “Concept X is similar”; it is a chain such as `thought:new -expresses-> claim:A <-objects-to- objection:B -belongs-to-> inquiry:C` with provenance for every step.

2. **Find a bridge between two apparently separate ideas.**

   Bind both endpoints, request up to three shortest acyclic paths, and require at least one intermediate node that participates in a frame not shared by both endpoints. This deliberately searches across overlapping frames without treating a frame as containment. GQL can bind whole paths and return paths as values; that is the behavior to preserve ([GQL digest, pp. 9, 12](https://drops.dagstuhl.de/opus/volltexte/2023/17743/pdf/LIPIcs-ICDT-2023-1.pdf)).

3. **Challenge a belief before acting on it.**

   From `claim:X`, traverse incoming `supports | derived-from | asserted-by` and both directions over `contradicts | qualifies | disputes`, then stop at source artifacts or agents. Return separate explicit and inferred lanes. This exposes the evidence, counterevidence, and authority chain rather than collapsing them into a confidence score.

4. **Trace an idea into executable consequences.**

   From a ratified claim, follow `implies | motivates | constrains | explained-by` for at most four steps until reaching an `artifact`, `decision`, `issue`, or `code-structure`. Return every terminating path plus the local frame validation state. This is the generalized form of following Cartographer's `explained-by`, `constrained-by`, and `supports` edges without making its structural hierarchy universal.

5. **Explain the current connection and its history.**

   Given two nodes and a predicate, first return active statement records, then traverse their `asserted`, `ratified`, `disputed`, `superseded`, and `retired` events in time order. Current relevance and historical truth are distinct queries over the same identities.

6. **Project a frame.**

   Select entities and statements that explicitly `participates-in` a frame, optionally include intersections with other frames, apply that frame's shapes, and return violations as data rather than silently dropping nodes. A software frame may require a structural parent; a philosophy frame may require claims to name their epistemic status; the global network requires neither.

SPARQL remains useful for endpoint reachability and regular path expressions: it supports sequence, alternatives, inverse direction, and arbitrary-length `*`/`+` paths ([SPARQL 1.2 Query, §9.2](https://www.w3.org/TR/sparql12-query/#propertypath-examples)). But its intermediate variables are hidden under property-path projection, so explainable discovery should expand bounded paths or use a path-valued traversal layer rather than returning endpoint reachability alone ([SPARQL 1.2 Query, §9.3](https://www.w3.org/TR/sparql12-query/#property-path-equivalent)).

## Model Comparison

| Model family | Rapid connection creation | Explainable paths | Overlapping frames | Provenance and epistemic plurality | Schema evolution and constraints | Maintenance fit |
|---|---|---|---|---|---|---|
| **Labeled property graph / GQL-style** | Excellent: an identified edge can carry labels and key/value properties; parallel edge identities preserve multiple assertions. | Excellent: paths are values and path modes/selectors are explicit. | Good when frames are nodes/edges; multiple physical graphs can overlap, but their cross-graph topology semantics need policy. | Good mechanically through edge identity/properties, but no universal provenance vocabulary; edge-only metadata becomes awkward when provenance itself must be traversed. | Flexible labels/properties favor experimentation; local constraints require an explicit type/validation layer. | Best interaction model. GQL is an ISO standard since 2024, but the ecosystem is newer than SQL/RDF ([ISO/IEC 39075:2024](https://www.iso.org/standard/76120.html)). |
| **RDF / semantic graph** | Good: adding a triple is minimal, predicates have stable IRI identity, and independent graphs can merge around shared names. | Mixed: SPARQL property paths express reachability well, but do not bind the path interior as a path value. | Good if participation is modeled explicitly. Named graphs are not enough: RDF formally leaves the relationship between a graph name and its graph unspecified ([RDF 1.2 Concepts, §4](https://www.w3.org/TR/rdf12-concepts/#section-dataset)). | Excellent vocabulary support through PROV-O. RDF 1.2 triple terms can refer to asserted or unasserted triples, including commentary on contradictions, but RDF 1.2 is currently a Candidate Recommendation, not yet the stable baseline ([RDF 1.2 Concepts, §3.6 and status](https://www.w3.org/TR/rdf12-concepts/#section-triple-terms)). | Excellent for additive vocabularies and monotonic entailment; SHACL supplies validation separately. Care is needed because RDF/RDFS entailment adds facts and cannot retract weaker entailments ([RDF 1.2 Semantics, §3](https://www.w3.org/TR/rdf12-semantics/#semantic-extensions)). | Strong semantic/interchange reference, but a pure RDF/SPARQL interaction layer makes path explanation and casual local use more ceremonial. |
| **Normalized relational + recursive SQL / SQL-PGQ projection** | Fair: strict statement/event tables make required inputs and uniqueness clear, but every novel field or relation convention needs a row/table policy. | Good through SQL/PGQ graph views or explicit recursive queries; raw recursive SQL is verbose, while implementation coverage of newer path features varies. | Excellent through membership tables and ordinary joins. | Excellent when assertion, actor, activity, source, and time are normalized and foreign-keyed. | Excellent fail-fast constraints and migrations; open-ended attributes need extension tables/JSON or schema changes. | Strongest conservative durable baseline and easiest projection audit. SQL/PGQ explicitly maps relational representations to a property-graph query surface ([Graph Pattern Matching in GQL and SQL/PGQ](https://arxiv.org/abs/2112.06217)). |
| **Dual canonical RDF + property-graph stores** | Initially attractive. | Excellent in the read model. | Potentially excellent. | Potentially excellent. | Two schema systems. | Reject for the first experiment: synchronization, identity mapping, divergent query semantics, and projection drift would become the project. One canonical statement/event model with rebuildable projections gives the benefit without dual authority. |

The property-graph model wins for human/agent crawling; RDF wins for shared semantic conventions; relational structure wins for conservative persistence and validation. The recommended model assigns each family the job it is best at instead of forcing one family to perform all three.

## Recommended Candidate

### Event-backed statement multigraph

The minimum universal kernel is:

```text
Entity(id, kind?, created_at, lifecycle)
Statement(id, subject_id, predicate_id, object_id|literal,
          authority_id, epistemic_status, confidence?, source_id,
          asserted_at, valid_from?, valid_to?)
Event(id, event_type, target_id, actor_id, occurred_at, source_id, payload)
Frame(id, name, vocabulary_version?, shape_version?)
FrameParticipation(subject_id, frame_id, role, authority_id, source_id)
```

`Statement` is the canonical relationship record. It is projected as an identified, directed property edge for crawling. Multiple statements with the same subject, predicate, and object are not deduplicated when authority, frame, status, or source differs: disagreement is knowledge. Literal values remain allowed, but anything that must carry its own relationships becomes an entity.

Connection creation should require only `subject`, `predicate`, `object`, `authority`, `epistemic_status`, and `source/context`; IDs and timestamps can be assigned deterministically. This keeps capture fast while failing clearly at the authority boundary. New predicates can appear without a global migration, but their qualified identifiers and declared inverses, symmetry, transitivity, and permitted endpoint kinds live in frame vocabulary. Semantic rules are data, versioned with the frame.

History and current truth are separated:

- events are append-only;
- statement identity survives status changes;
- the current graph contains active projections;
- supersession and retirement remove an edge from the current projection without erasing its event history;
- inferred statements are separately identified and link to the rule/model activity and supporting statements that produced them;
- ratification is a human-authored event, never a property silently overwritten by an agent.

RDF 1.2's distinction between a triple term and an asserted triple is a useful semantic precedent for representing proposed, quoted, or disputed propositions without asserting them as facts ([RDF 1.2 Schema, §5.2](https://www.w3.org/TR/rdf12-schema/#ch_reificationvocab)). Because RDF 1.2 and SPARQL 1.2 remain Candidate Recommendation/Working Draft work as of this research, the kernel should copy the distinction, not depend on draft syntax.

Frame structure remains explicit and overlapping. Never use a node label, RDF named graph, filesystem folder, or database graph as the sole meaning of frame participation. Those may be projections or indexes. A `participates-in` statement can itself name role, authority, provenance, lifecycle, and whether membership is declared or inferred.

Frame constraints should be SHACL-inspired and local:

- open by default;
- closed only at deliberate seams;
- severities distinguish violation, warning, and information;
- validation results name the focus entity, path, shape, and message;
- cross-frame consequences produce findings or proposed statements, not invisible mutation.

The first traversal surface should be declarative path patterns plus a small procedural “expand one hop” operation. Declarative patterns make repeatable agent questions auditable; one-hop expansion preserves the playful browsing loop. Full graph algorithms, embeddings, ontology reasoners, and unbounded agent-authored traversals are later projection capabilities, not kernel primitives.

## Failure Modes

- **Assertion-node ceremony overwhelms capture.** If every connection requires hand-authoring provenance objects, Fred will stop connecting ideas. Keep one minimal statement command; derive context fields deterministically and expose deeper provenance only when needed.
- **Projection drift creates two truths.** The current property graph must be wholly rebuildable from canonical events/statements, stamped with source position/hash, and rejected when stale.
- **Duplicate projection becomes duplicate authority.** A projected edge is not a separately editable record. Mutations go through statement events only.
- **Conflicting assertions are collapsed.** Never use `(subject, predicate, object)` alone as a uniqueness key. Preserve authority, source, frame, time, and status.
- **Frames become disguised containers.** Explicit participation must permit many frames and many roles. Physical partitions and labels are views, not membership truth.
- **Named graphs are mistaken for frame semantics.** RDF only pairs a name syntactically with a graph and deliberately does not define what the name denotes; an application policy would still be required ([RDF 1.2 Concepts, §4](https://www.w3.org/TR/rdf12-concepts/#section-dataset)).
- **Path explosion or cycles swamp discovery.** Bound depth, default to acyclic paths, allow-list predicates, cap path groups, and make unrestricted walk/all-path modes explicit. Never let an agent omit the traversal budget.
- **Shortest becomes synonymous with meaningful.** Rank by declared semantic cost, specificity, epistemic status, source quality, and recency after selecting bounded candidates; always show the components. Preserve alternative path groups rather than one “best” answer.
- **Inference launders agent guesses into belief.** Inferred/proposed statements occupy separate lanes, cite their generating activity and premises, and require explicit promotion or ratification where authority demands it.
- **Ontology gardening replaces thinking.** Keep the universal vocabulary tiny. Promote a predicate or shape only after repeated use; permit frame-local vocabulary and aliases.
- **Global constraints destroy experimentation.** Only kernel identity/authority/event invariants are universal. Frame shapes may be strict, but violations outside a deliberate write seam should remain visible findings, not data loss.
- **Semantic inference surprises users.** RDFS/OWL-style domain, range, subclass, or transitive inference must be an explicit projection with a named entailment regime. RDF semantics are monotonic, so inference is additive rather than a mechanism for dispute/retraction ([RDF 1.2 Semantics](https://www.w3.org/TR/rdf12-semantics/)).
- **Procedural traversals become irreproducible.** Persist the traversal request, engine/projection version, explicit ordering, and returned statement IDs. TinkerPop documents that traversal result order is not guaranteed unless explicitly ordered ([TinkerPop reference](https://tinkerpop.apache.org/docs/current/reference/#_the_traverser)).
- **A dual-store hybrid becomes permanent infrastructure.** Keep RDF export and property-graph/SQL views rebuildable from one model; do not add bidirectional synchronization until a concrete experiment proves it necessary.

## Open Questions

- Should the canonical statement be exposed to users as an edge, as a node, or only through a connection command? The projection can support all three views, but the interaction cost differs.
- Which kernel predicates are truly universal beyond `participates-in`, `derived-from`, `asserted-by`, `supersedes`, and lifecycle/provenance relations?
- Does a statement participate in frames independently of its endpoints, and what is the default frame inheritance rule?
- Which relation lifecycles require full assertion/retirement history, versus ordinary current-edge addition/removal?
- Is `valid_time` needed alongside event/transaction time for the first experiment, or is one timeline sufficient until contradictory historical claims appear?
- How are aliases, near-duplicates, and identity merges represented without erasing their former identities?
- What semantic-cost defaults make bridge discovery interesting without privileging generic hubs such as `related-to` or high-degree themes?
- Which inferred relations may be cached in the current projection, and which should be recomputed per traversal?
- How much of PROV-O should be adopted: the Entity/Activity/Agent core only, or qualified influence relationships as well?
- Is RDF export merely interoperability, or will philosophical work benefit enough from formal entailment to earn an RDF-native projection?
- What is the smallest human-readable frame-shape language that can compile to strict validators and, where useful, SHACL?

## Tested / NOT Tested

**Tested by document and standards analysis:** the current exploration decisions; Cartographer's current-only sparse map model; the Journal System convergence report; the ISO status and abstract model of GQL and SQL/PGQ; the formal GQL property-graph and path model described by members of the standards/research groups; current RDF 1.2 Concepts and Semantics Candidate Recommendations; current SPARQL 1.2 and SHACL 1.2 drafts where their status matters; the stable SPARQL 1.1, SHACL 1.0, and PROV-O Recommendations; and Apache TinkerPop's current traversal documentation. Sources were checked on 2026-07-29.

**NOT tested:** no database product was selected, installed, or benchmarked; no prototype, schema, migration, query, projection, or validator was executed; no corpus-scale path explosion, latency, concurrency, or recovery behavior was measured; no RDF-to-property-graph round trip was tested; no vendor's degree of GQL, SQL/PGQ, RDF 1.2, or SPARQL 1.2 support was compared; no UI or Fred/agent usability test was run; and no claim is made that the candidate is the final architecture.

## Sources

- [ISO/IEC 39075:2024 — GQL](https://www.iso.org/standard/76120.html)
- [ISO/IEC 9075-16:2023 — SQL/PGQ](https://www.iso.org/standard/79473.html)
- [Francis et al., *A Researcher's Digest of GQL*](https://drops.dagstuhl.de/opus/volltexte/2023/17743/pdf/LIPIcs-ICDT-2023-1.pdf)
- [Deutsch et al., *Graph Pattern Matching in GQL and SQL/PGQ*](https://arxiv.org/abs/2112.06217)
- [RDF 1.2 Concepts and Abstract Data Model — Candidate Recommendation](https://www.w3.org/TR/rdf12-concepts/)
- [RDF 1.2 Schema — Candidate Recommendation](https://www.w3.org/TR/rdf12-schema/)
- [RDF 1.2 Semantics — Candidate Recommendation](https://www.w3.org/TR/rdf12-semantics/)
- [SPARQL 1.2 Query Language — Working Draft](https://www.w3.org/TR/sparql12-query/)
- [SPARQL 1.1 Query Language — Recommendation](https://www.w3.org/TR/sparql11-query/)
- [SHACL — Recommendation](https://www.w3.org/TR/shacl/)
- [SHACL 1.2 Core — Working Draft](https://www.w3.org/TR/shacl12-core/)
- [PROV-O — Recommendation](https://www.w3.org/TR/prov-o/)
- [Apache TinkerPop Reference Documentation](https://tinkerpop.apache.org/docs/current/reference/)
- [Constellation Ideas Board](C:/Programs/constellation-skills/.agent-work/explore-grander-scale/IDEAS_BOARD.md)
- [Cartographer Map Model](C:/Programs/constellation-skills/skills/cartographer/references/map-model.md)
- [Journal-System Convergence Research](C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/journal-research-result.md)
