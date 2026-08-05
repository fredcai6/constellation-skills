# Roll-up: the multi-geometric graph substrate

**Provenance:** brought back by the human (Tommy) on 2026-08-04, summarizing a conversation held with a different agent outside this session. Preserved here as *input* — the board's Verdicts and Open threads record what this session then did with it, including where it conflicts with an earlier recorded verdict.

---

## Starting architecture

The substrate begins with:

- Topics as uniquely identified nodes
- Explicit properties attached to topics
- Named relationships between topics
- Queries and traversal over both properties and graph structure

The central question was whether conceptual spaces, embeddings, reasoning trails, and related theories require additional representational layers or merely describe capabilities already available in this substrate.

## 1. Conceptual spaces — Peter Gärdenfors

**Initial confusion.** Conceptual spaces initially sounded equivalent to a property table: assign dimensions to an object, then group objects according to their values. That interpretation is substantially correct for Gärdenfors's original theory. His dimensions are generally meaningful quality dimensions — hue, weight, pitch, temperature. He was not originally describing modern neural-network embeddings with opaque dimensions.

**What conceptual spaces add.** The contribution is not primarily "store vectors." It is:

- Define a distance metric over properties.
- Treat concepts as regions rather than labels.
- Allow graded membership, prototypes, centers, boundaries, and betweenness.
- Evaluate whether categories form coherent or convex regions.

A normal property table does not automatically provide geometry. Geometry appears only after defining how values differ and how distances across dimensions combine.

Categorical properties can also participate. For example, engineering disciplines could have a manually defined distance matrix or their own relationship graph. This creates a named, interpretable embedding space even when the values are not naturally continuous.

**Resulting position.** Maintain both:

1. Named geometric spaces, derived from explicit properties and explicitly defined metrics.
2. Unnamed neural embedding spaces, derived from content and used to detect relationships along dimensions nobody modeled in advance.

The named space offers interpretability and control. The unnamed space offers coverage and vocabulary-independent pattern detection. Do not collapse the two prematurely.

## 2. Formal Concept Analysis

FCA derives groupings from an object–attribute table. Because the substrate already contains topics and properties, this does not appear to require a distinct architectural layer. It is best treated as a query or analysis over the property database. Potential uses: deriving implied categories; identifying shared property sets; detecting redundant or inconsistent facets.

Reaction: useful analytical machinery, but not a new substrate.

## 3. Memex trails and reasoning traces

A Memex-style trail records not merely which nodes are connected, but the path followed during an investigation. The important extension is to record each traversal decision:

- Source node
- Destination node
- Relationship used
- Reason the relationship was selected
- Evidence or context
- Alternatives considered or rejected
- Outcome of the traversal

A complete reasoning episode becomes an ordered sequence of these decisions. This is not an ordinary semantic embedding. It is trajectory data: a record of how agents moved through the knowledge substrate and why.

Repeated useful trajectories can become: suggested routes; reusable reasoning macros; learned policies; warnings about known dead ends; context-specific "superhighways" through the graph. This adds experience on top of static structure.

## 4. Traversal-derived weights

The strongest new synthesis is that reasoning traces can supply empirical evidence for graph weighting. An edge may begin with an a priori weight, based on authored judgment. Subsequent traversal data can modify its effective value according to:

- How often the edge is selected
- Which task contexts select it
- Whether traversals using it succeed
- Whether it shortens or improves reasoning
- What evidence or rationale supported its use
- Whether competing paths performed better

This turns agent reasoning into training data for the graph.

However, a single global scalar weight would discard too much information. An edge may be useful for one goal and harmful for another. The learned object should therefore be closer to:

> «utility of this relationship, given the task, context, agent state, and desired outcome»

The system can still expose scalar weights for efficient routing, but those weights should be projections of richer contextual statistics.

The traversal system could generate several distinct representations:

- Edge-use weight: how much reasoning load an edge carries
- Success-conditioned weight: how often its use contributes to a successful outcome
- Contextual weight: value under a particular task or domain
- Traversal embedding: a vector describing how a node or edge functions across observed reasoning paths
- Path embedding: a representation of an entire reasoning trajectory

These learned traversal representations form another geometric space alongside semantic, property, and graph-structural spaces.

## 5. Affordances — James Gibson

Affordances describe what an entity makes possible: not merely what it is, but what can be done with it. In this substrate an affordance can be represented as a named relationship — method affords capability; tool enables operation; dataset supports analysis; concept permits inference.

This does not necessarily require a separate vector space. It can be modeled as ordinary typed graph structure. Its practical value is in routing: an agent with a goal can search for nodes that afford the required operation. Affordance relationships may receive initial authored weights and later be reinforced or weakened through traversal outcomes.

## 6. Analogical reasoning — structure mapping

Analogical reasoning compares relational patterns rather than surface similarity. The central form is «the relationship between A and B resembles the relationship between C and D», which differs from asking whether A resembles C.

Neural embeddings may sometimes encode relations as difference vectors, but a complex analogy usually involves multiple linked relations, role correspondences, and constraints. A single vector offset is therefore insufficient in many cases.

The graph substrate is well positioned for analogical reasoning because it can compare local graph shapes, typed relation patterns, multi-node structures, reasoning trajectories, and outcomes produced by structurally similar paths. Embeddings can generate candidate analogies; structural matching and reasoning traces can then test whether the analogy is defensible. Any inferred correspondence should remain a hypothesis until explicitly validated.

## 7. Prototype theory — Eleanor Rosch

Category membership is graded around representative examples rather than defined solely by crisp boundaries. The substrate may already generate prototypes through several mechanisms: centrality in a named property space; centrality in a neural embedding space; density of relationships; frequency of appearance in successful reasoning traces; familiarity or exposure; similarity to other category members.

A robin may be treated as a more prototypical bird than a penguin because it is more central across familiar behaviors, properties, and observed usage. No separate prototype layer is strictly required — prototype status can be computed.

A useful diagnostic is **disagreement among prototype measures**. A node may be geometrically central but rarely useful in reasoning, or frequently traversed while semantically atypical.

## 8. Hypergraphs and reified relationships

A hypergraph allows one relationship to connect more than two nodes — «method X solves problem Y under assumptions A and B using dataset C» — which cannot be faithfully reduced to one pairwise edge without losing the unity of the assertion.

The practical alternative is reification: make the relationship or event itself a node, then attach all participants and metadata to it.

This is directly relevant to reasoning traces. A reasoning step can itself be a node connected to source, destination, relationship invoked, one or more reasons, evidence, agent, task, outcome, and timestamp or version. Reasons do not need to remain unstructured text fields — each reason can itself be a node, with further relationships and provenance.

This leads naturally to "graphs all the way down," but with typed layers rather than an undifferentiated mass of nodes.

## Resulting synthesis — five separable but interacting layers

1. **Asserted knowledge graph** — directed, typed, provenance-bearing relationships representing claims someone or some process is willing to assert.
2. **Property system** — explicit, interpretable attributes used for filtering, classification, constraints, and named geometric spaces.
3. **Geometric spaces** — a *family* rather than one universal embedding: named property geometry; neural semantic embeddings; graph-structural embeddings; analogy/relation representations; traversal and reasoning-path embeddings. Each answers a different form of "nearby."
4. **Reasoning-trace graph** — first-class records of how agents traversed the substrate, including reasons, evidence, alternatives, and outcomes.
5. **Learned routing layer** — a policy that uses prior traces to estimate which edges or paths are useful in the present context.

The static graph describes what is connected. The traversal graph describes how the graph has actually been used. The routing layer predicts how it should be used next.

## Main architectural caution

Do not merge semantic similarity, graph proximity, property distance, traversal frequency, and successful utility into one number too early. They represent different claims: similar content; similar explicit properties; similar structural roles; frequently traveled; useful for a particular task; historically successful.

A combined score may eventually be useful for retrieval, but the component scores should remain available and named. Otherwise popularity can masquerade as truth, familiarity as prototypicality, and repeated agent behavior as evidence of correctness.

The main new direction is therefore not merely a weighted knowledge graph. It is a **multi-geometric graph substrate whose use generates additional graph structure and context-dependent routing weights**.
