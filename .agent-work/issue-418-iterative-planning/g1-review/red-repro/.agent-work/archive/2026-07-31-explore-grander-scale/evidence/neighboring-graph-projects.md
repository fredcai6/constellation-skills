# Neighboring graph-substrate projects

Checked against primary project documentation and papers on 2026-07-30.

## Verdict

No surveyed project combines the target shape. The closest useful architecture is a deliberate composite:

- AutoGen Core's runtime-created agent identities suggest how a home frame can parameterize an agent at instantiation without placing it in the graph.
- Blackboard systems supply the organizational lineage: specialists coordinate through shared representations without every caller knowing every specialist.
- GraphRAG and KAG demonstrate the map-first pattern: high-level graph structure or logical indexes orient a query, while source chunks remain available for local evidence.
- Graphiti demonstrates temporal validity and episode provenance, but its mixed temporal graph should become separate current and history views here.
- OpenCog Hyperon explores the maximal version, where the graph also represents procedures and supports inference. It is more useful as a boundary warning than a near-term blueprint.

The important result is architectural orthogonality: agent lifecycle, semantic representation, temporal provenance, and coordination may meet at explicit interfaces, but should not be made one mechanism.

## Comparators by design axis

### 1. Microsoft GraphRAG — graph as a navigational compression layer

GraphRAG indexes unstructured text into entities, relationships, claims, communities, and multilevel community reports. Its local search combines graph material with raw text chunks; global search map-reduces community reports; DRIFT uses community information to broaden a local starting point and form follow-up questions. Agents are external query consumers, and behavior lives in the indexing/query pipelines rather than in graph entities. See the [indexing overview](https://microsoft.github.io/graphrag/index/overview/) and [query overview](https://microsoft.github.io/graphrag/query/overview/).

**Transfer:** this is the strongest validation of the map-first thesis. A high-level structure can answer global orientation questions and choose where detailed source context should be spent. Retain graph-to-source links so the map accelerates understanding without replacing verification.

**Trap:** LLM-extracted relationships and generated summaries are useful retrieval artifacts, not automatically canonical truth. Expensive extraction and stale summaries would be poor foundations for the current architecture plane without validation.

### 2. OpenSPG KAG — mutual indexing between knowledge and evidence

KAG targets professional-domain knowledge bases. It combines schema-free extraction with schema-constrained expert knowledge, maintains mutual indexes between graph structure and original chunks, and uses logical-form-guided retrieval and reasoning. Agents are again external reasoners; behavior lives in a planner/retriever/reasoner stack. See the [KAG repository and architecture summary](https://github.com/OpenSPG/KAG) and [KAG paper](https://arxiv.org/abs/2409.13731).

**Transfer:** the mutual index is nearly the desired trust boundary: traverse high-level concepts and claims, then open the exact source when literal verification is required. Frames can also earn local schemas without forcing one global ontology.

**Trap:** KAG's domain schema and logical engine are appropriate to professional question-answering, but would over-formalize the wider play network if promoted to a universal requirement.

### 3. Graphiti — graph as temporal agent memory

Graphiti represents entities, relationship facts with validity windows, evolving summaries, and source episodes. It incrementally builds a temporal context graph and retrieves through semantic, keyword, and graph methods. The raw episodes supply provenance; agents are clients that read or add episodes rather than inhabitants of nodes. See the [Graphiti repository](https://github.com/getzep/graphiti) and the [Zep temporal knowledge graph paper](https://arxiv.org/abs/2501.13956).

**Transfer:** every derived assertion should retain source and temporal lineage; supersession should not erase history. Current truth can be implemented as a deliberate projection/query contract over retained events.

**Trap:** Graphiti's normal model makes current and historical facts co-resident and filterable. This project has a stronger cognitive requirement: ordinary traversal must show only what is, with history explicitly requested. Its database and LLM ingestion stack is also much heavier than the current Markdown need. Scoped cross-agent write authority is not inherent in a temporal graph.

### 4. AutoGen Core — runtime-created identity, separate from knowledge

AutoGen Core registers an agent type with a factory. The runtime creates and manages an instance on first delivery to an `AgentId`, whose type and key distinguish the factory and instance. Different factories may instantiate the same class with different constructor parameters. Communication and lifecycle live in the runtime; AutoGen does not supply the semantic knowledge graph described here. See [Agent and Agent Runtime](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html).

**Transfer:** make `home_frame` an explicit instantiation input alongside purpose, protocol, tools, and authority. It is an initial jurisdiction and context root, not a graph coordinate. Recursive agents-on-agents delegation can therefore remain the execution shape.

**Trap:** an agent address or message topic is only routing identity. Treating it as semantic authority would hide the very policy that a home frame is meant to declare.

### 5. Blackboard systems — shared substrate for specialists

The blackboard lineage separates a shared problem representation from specialized knowledge sources that contribute partial results. A recent LLM application has a central agent post requests while agents responsible for data partitions or general retrieval volunteer based on their capability; the reported gains are task-specific evidence that this communication pattern can outperform a rigid master–slave baseline. See [LLM-based Multi-Agent Blackboard System for Information Discovery in Data Science](https://arxiv.org/abs/2510.01285).

**Transfer:** this is the nearest organizational ancestor of a confederation over a shared substrate. A home frame resembles a declared specialist jurisdiction; agents can inspect shared state without the instantiating agent knowing every possible downstream capability.

**Trap:** classic blackboards often assume a global scheduler and broadly writable shared state. That can create a central bottleneck, obscure provenance, and allow one agent to poison shared truth. Shared visibility does not imply shared mutation authority.

### 6. OpenCog Hyperon / AtomSpace — graph as cognitive medium

Hyperon's AtomSpace is a weighted labeled hyper/metagraph intended to represent many kinds of declarative and procedural knowledge and mediate between AI algorithms. AtomSpace also supports graph pattern matching, rewriting, inference, and executable atoms. See the [Hyperon overview](https://hyperon.opencog.org/), [Hyperon AtomSpace notes](https://wiki.opencog.org/w/Hyperon%3AAtomspace), and [AtomSpace overview](https://wiki.opencog.org/w/AtomSpace).

**Transfer:** it demonstrates that code and procedures can be attached to the same representational fabric as ideas, and that a graph can be a genuine interoperability medium between reasoning processes.

**Trap:** once the substrate is knowledge store, programming language, query engine, rule engine, and cognition model, ontology/runtime design can swallow the original goal. Keep global behavior minimal and constitutional; put most behavior in agents and local frame protocols until repeated needs earn substrate mechanics.

### 7. A-MEM and LangGraph — two useful boundary contrasts

A-MEM creates atomic, Zettelkasten-inspired notes, links new memories to existing ones, and may update older memories' contextual representations as new information arrives. It is a strong precedent for rapid, agent-assisted connection formation. See [A-MEM](https://arxiv.org/abs/2502.12110).

**Transfer:** suggest connections at capture time and let the local neighborhood evolve. **Trap:** autonomous rewriting of prior representations blurs historical evidence, present interpretation, and human authority; suggestions should enter a proposed lane before ratification.

LangGraph, by contrast, uses nodes and edges to describe execution and state flow. It is valuable as a workflow runtime but is not the semantic substrate in question. See the [LangGraph overview](https://langchain-ai.github.io/langgraph/).

**Transfer:** little beyond persistence/checkpointing mechanics. **Trap:** drawing agents as fixed nodes would confuse control flow with knowledge structure and erase the user's runtime-instantiated-agent model.

## Resulting design principles

1. **Instantiate from a frame; do not locate the agent in the graph.** The frame seeds context, vocabulary, protocols, tools, and authority for one run.
2. **Read the map, verify the source.** Every useful high-level connection should retain a path to evidence or current implementation.
3. **Separate the planes at the interface.** Current is the default traversal; possibility and history require explicit requests even if one event store ultimately backs them.
4. **Federate authority.** A conservative first rule is read globally, write current truth locally, and propose across frame boundaries. Every assertion identifies its author, source, frame, status, and time.
5. **Keep behavior local until it repeats.** Agents and frame protocols act; the shared graph provides representation, traversal, provenance, and a few earned invariants.
6. **Use agent-assisted links as proposals.** Rapid connection formation matters, but automatic extraction must not silently become current truth.
7. **Measure map usefulness directly.** Record the map nodes and relationships used before source inspection, then ask whether they reduced low-level context and improved seam selection.

The unresolved design question is jurisdiction: whether an agent's home is immutable for its lifetime and whether cross-frame current-state writes must always be proposals. The cleanest initial answer is yes to both; instantiate a new agent when a new home is needed.

## Tested and not tested

**Tested:** current official documentation/repositories and primary papers for distinct architecture families; comparison of representation, lifecycle, behavior location, traversal, temporal model, provenance, and transferable lessons.

**Not tested:** no package was installed; no repository was executed; no benchmark result was independently reproduced; no interoperability, graph quality, latency, maintenance cost, or suitability on Fred's corpus was measured. Product self-descriptions and paper results are treated as scoped claims, not independent validation.
