# Ideas Board — `explore-grander-scale`

The living record of shared understanding and the source of truth for this exploration.

## The point

Constellation began as a rigor system for coding agents, but its architecture network, deterministic checklist engine, recursive learning loop, and recent Context Governor work are converging on a broader question: whether Constellation should become a durable coordination and knowledge substrate in which agents are replaceable workers, rather than remaining a corpus of instructions each agent carries and interprets.

The itch is cumulative: supervision, graph coherence, ontological structure, and awareness of external ideas all contribute. The center is **knowledge representation that can actually be used**. Better reasoning and moving beyond coding-first assumptions are the driving motivations for addressing it now.

This is a personal experimentation project for Fred, not a team product. Its purpose is to **enable ideas**: help ideas acquire useful structure, interact, and become actionable. The graph is shared cognitive infrastructure for Fred **and agents working with him**, not merely a private visualization. Code is the first executable medium, not the boundary. Philosophy is an adjacent proving ground because representing concepts, arguments, implications, and tensions is part of the desired capability and part of the fun.

A successful session lets a raw thought connect to prior thinking; makes assumptions, contradictions, implications, and alternatives visible; and leaves behind a sharper belief, valuable question, or executable artifact. This is conceptually an extension of the existing architecture graph, not a replacement: code and architecture remain graph-connected material, but the graph's theoretical reach expands.

There is no utility-based kill condition. Experimentation, learning, and enjoyment are sufficient value; the framework does not need to outperform ordinary notes or justify itself as a product. Fred may deliberately shelve or redirect it, but lack of conventional ROI does not invalidate it.

The immediate purpose now has five explicit parts: Fred should build it himself as a learning playground rather than directly reuse another system; project frames should provide an honest current map for both agent action and human understanding; a cross-project knowledge network should help accumulated material form unexpected ideas and approaches; autonomous agents should be able to work over the substrate without displacing Fred from the hard thinking or overriding human direction; and the authored representation should remain naturally revision-controllable so graph history is easy to inspect and manage.

## Current candidates

- **Harden the existing coding system** — keep Constellation coding-specific; replace Markdown-only map storage with a traceable graph projection and move runtime enforcement outside the acting agent.
- **Domain-neutral kernel with coding pack** — extract a small event/knowledge/policy kernel; preserve today's skills as the first domain pack and adapter.
- **Personal idea-enabling substrate** — join engineering workflow, journal, and philosophical exploration around shared representations of concepts, claims, evidence, implications, and provenance.
- **Globally networked, locally structured** — the wider knowledge network has no mandatory spine; bounded subnetworks may declare a local spine, schema, invariants, and completion rules when their purpose earns that rigor (for example software architecture or a book manuscript).
- **Declared frames with overlapping membership** — a frame is deliberately named; membership and other participation are explicit relationships, never exclusive containment. Inferred clusters may reveal natural groupings, but do not replace declared frames.
- **History plus projections** — preserve append-only source events and artifacts as history; build graph relationships and frame-specific current views as projections. Some deliberately declared relationships may themselves be canonical events.
- **Lifecycle is explicit and frame-sensitive** — nodes and relationships may be persistent, transient, derived, or retired. The current graph can add and delete connections as relevance changes; append-only history is required for source artifacts and selectively for relationships whose frame, authority, or provenance rules earn it.
- **Epistemic authority as structure** — observed, inferred, proposed, ratified, disputed, rejected, and superseded knowledge must remain distinguishable; agent interpretations never silently become human-owned belief.
- **Research radar** — ingest external AI developments into a quarantined candidate lane, with explicit comparison and promotion rather than direct adoption.
- **Evidence-backed assertion multigraph** - represent every truth claim as an assertion with a stable identity, source, supporting and challenging evidence, and a qualitative current support assessment (`weak`, `medium`, or `strong`). Strength says how safe the assertion is to rely on now and where verification attention may be valuable; it creates no inertia against decisive new evidence. Preserve assessment changes and assertion lifecycle in revision history; rebuild a current attributed graph projection for fast crawling.
- **One crawl contract, backend adapters** - agents and Fred use bounded neighborhood, path, explanation, and suggestion operations rather than unrestricted database queries. The contract names relation/frame/status filters, cycle policy, traversal budget, ordering, and explanation requirements.
- **Markdown-first map, upgraded by pressure** - keep Markdown as the near-term representation and test the important behavior first: whether agents use high-level architecture connections to orient themselves before inspecting targeted code. Watch navigation, maintenance, and traversal friction; revisit a graph backend only when observed pressure earns it.
- **Three information planes** - keep the default navigation map strictly current-state; keep possibilities in a separate exploratory plane and history/provenance in a separate historical plane. Both remain available from the current context, but neither participates in ordinary traversal unless deliberately requested. Selectively attach present necessity or purpose when it helps explain why a current element must exist; explanations of why it has its particular form belong only to history.
- **ActiveGraph as conceptual foil only** - use ActiveGraph to expose alternate conceptualizations of shared state, history, possibility, scoped context, and behavioral relations. It is not an implementation candidate. Its value here is the question it sharpens: whether a network merely represents a world, has deterministic mechanics, or itself possesses agency.
- **Confederated agent instantiation with home frames** - preserve Constellation's agents-on-agents recursive delegation rather than placing persistent agents at graph locations. When an agent is instantiated, its home frame supplies its starting context, purpose, vocabulary, protocol, tools, and authority. It may traverse beyond that frame to understand connections and explore; home is an initialization and jurisdictional anchor, not a fixed position.
- **Project truth federated into an idea commons** - project frames own honest, operational descriptions of what currently exists; a wider cross-project network connects those grounded maps with notes, concepts, questions, and proposed relationships. The two regions may share graph mechanics without sharing the same epistemic or mutation rules.
- **Git-native authored truth, generated projections** - keep the human-reviewable, diffable representation canonical enough to understand and recover directly through revision control. Derived indexes, visualizations, and database projections may accelerate crawling but must be reproducible rather than becoming an opaque second truth.
- **Human-directed autonomy** - give agents genuine room to traverse, propose, verify, delegate, and act inside explicit authority envelopes while reserving human intent, value judgments, architectural direction, and promotion of consequential beliefs or possibilities for deliberate human participation.
- **Unified assertion truth model** - frames select, organize, and provide jurisdiction over assertions; they do not define separate kinds of truth. Code structure, historical fact, personal belief, philosophical argument, and cross-project analogy all use the same assertion/evidence/strength mechanics. Differences arise from their evidence and current assessment, not frame-specific epistemologies.
- **Support-system-first reorientation** - stop elaborating detailed assertion and agent behavior until current architectural pressure earns it. The next altitude is whether a representative map exists, whether agents actually use it to find seams before source crawling, whether drift is visible, and how local project maps could eventually federate without losing their useful structure.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| The generalized network needs no universal spine; structure is local to declared, overlapping frames. | Tested through the existing architecture frame, the journal system's daily/theme/ledger/values regions, and the book/philosophy examples. NOT tested against an implemented general graph. | cycle 1 |
| The graph is shared cognitive infrastructure for Fred and collaborating agents; it is not a team product. | Human-owned purpose decision. NOT a claim about future external users. | cycle 1 |
| Journal System and Constellation are compatible domain frames over common principles: durable external state, provenance, deterministic seams, additive interpretation, and human authority. | Grounded in current main of both repositories. NOT runtime-verified and did not inspect the private journal vault. | journal-system convergence excursion |
| No utility-based kill condition applies; experimentation and learning are sufficient value. | Human-owned purpose decision. Shelving remains available by choice. | cycle 1 |
| A relationship need not be universally event-canonical or projection-only; its lifecycle depends on its meaning and frame. Current relevance may be represented directly by adding or deleting graph connections. | Human design direction after cycle 1. NOT yet tested against concrete relationship classes or storage mechanisms. | inter-cycle discussion |
| Meaningful connections should be individually identified attributable statements; append-only events preserve their history, while the active crawl graph is a rebuildable current projection. | Tested through standards/model analysis across property graphs, RDF, SHACL/PROV-O, and normalized relational projections. NOT runtime-tested. | cycle 2 graph-model excursion |
| Explainable crawling requires a stable traversal contract: bounded depth, typed relation allow-lists, frame/status/authority filters, explicit cycle and path-selection modes, deterministic ordering, and returned provenance for every hop. | Grounded in current GQL/Cypher, SPARQL, recursive SQL, and TinkerPop semantics. NOT usability- or performance-tested on Fred's corpus. | cycle 2 graph-model excursion |
| Storage and crawling are separate interfaces; database-neutral IDs and logical exports prevent a tool experiment from becoming the architecture. | Tool comparison across Neo4j, LadybugDB, Oxigraph, Jena, TypeDB, and SQLite. NOT migration-tested. | cycle 2 tooling excursion |
| Neo4j Community Edition is the best first disposable experiment for learning valuable crawls, not a commitment to canonical storage. LadybugDB is the leading embedded contrast and SQLite is the minimal control. | Current primary documentation/repositories checked on 2026-07-29. No product was installed or benchmarked. | cycle 2 tooling excursion |
| Markdown is sufficient for the near term; adopting a graph database now would add weight before the central map-first hypothesis is tested. Future storage architecture remains an observation thread, not current implementation work. | Human direction after sleeping on cycle 2. This supersedes the cycle 2 recommendation to run Neo4j first; it does not reject graph storage permanently. | inter-cycle direction after cycle 2 |
| A good network primarily accelerates exploration of existing high-level connections compared with crawling low-level source material. For code, the proof is that agents use architecture documentation as a map and inspect code selectively; the same standard should generalize to complex ideas. | Human-owned success criterion. NOT yet tested through controlled agent tasks. | inter-cycle direction after cycle 2 |
| Map-first means architectural seams are answerable representationally before code is opened. Code is then targeted verification of the represented boundary and the place where problem-specific context is spent, not the mechanism used to discover the system's shape. | Human clarification of the trust-but-verify boundary. NOT yet tested against actual agent behavior or documentation coverage. | inter-cycle refinement after cycle 2 |
| The operational map describes only what is. Possibilities and history are separate available layers, excluded from default navigation. A concise current rationale may accompany a destination, but traversing the current network must not require reconstructing its history. | Human-owned separation rule. NOT yet tested against existing architecture-doc organization or agent retrieval behavior. | inter-cycle refinement after cycle 2 |
| Current necessity and historical explanation are different information. The current map may selectively answer "why must this exist?"; "why is it this way?" is exclusively historical and must not leak into the navigation plane. | Human clarification of the rationale boundary. NOT yet tested against existing documentation categories or terminology. | inter-cycle refinement after cycle 2 |
| ActiveGraph validates the mechanics of separating a current graph, append-only history, and isolated possibility branches, but it solves live agent execution and coordination rather than high-level navigation. It is a reference and possible future execution plane, not a reason to replace the near-term Markdown map. | Grounded in current ActiveGraph v1.10 official docs, repository, and paper. NOT installed or runtime-tested. | ActiveGraph comparison excursion |
| ActiveGraph's bounded views and opt-in context-read tracing offer a concrete analogue for measuring whether agents actually use the map to allocate context. Its run-local frames are behavior-dispatch contexts, not the overlapping semantic frames defined here. | Documentation comparison only. NOT tested against Constellation tasks or agents. | ActiveGraph comparison excursion |
| The emerging system is a confederation of agents over a shared graph. Behavior and authority are locally grounded in an agent's home frame; the wider network is shared territory for cross-frame understanding and exploration rather than one globally acting agent. | Human-owned conceptual direction. NOT yet tested against concrete cross-frame read, proposal, or mutation rules. | inter-cycle refinement after ActiveGraph comparison |
| Agents are not persistent occupants of graph locations. Constellation's agents-on-agents delegation remains the execution shape; a home frame is assigned at instantiation to establish initial context and authority, after which the agent may traverse the shared substrate. | Human correction of the confederation model. NOT yet compared against other agent runtimes or implemented. | inter-cycle refinement after ActiveGraph comparison |
| No surveyed project owns the whole target architecture. The nearest composite is: AutoGen-like runtime instantiation, blackboard-like shared coordination, GraphRAG/KAG-style map-to-source navigation, and Graphiti-like temporal provenance, held apart by explicit interfaces rather than collapsed into one system. | Comparison of current primary documentation and papers for seven distinct projects/lineages. NOT an implementation or interoperability test. | neighboring graph-substrate excursion |
| A home frame should be an explicit input to agent instantiation, not the agent's location in the knowledge graph. Agent identity/lifecycle and semantic knowledge storage are orthogonal concerns. | AutoGen Core demonstrates runtime-created identities and factory-selected construction parameters, but does not provide semantic home-frame authority or recursive Constellation delegation. | neighboring graph-substrate excursion |
| The strongest map-first precedent keeps high-level graph structure mutually linked to source material: use the graph to orient and broaden, then spend detailed context on source-backed verification. | GraphRAG and KAG documentation comparison. Their LLM extraction, community summarization, and domain reasoning pipelines were NOT run or evaluated on this corpus. | neighboring graph-substrate excursion |
| Temporal validity and provenance are worth borrowing without adopting a temporally mixed default view: current truth remains the ordinary traversal contract, while source episodes and superseded facts are deliberately requested history. | Graphiti model comparison only. Its ingestion pipeline, backends, retrieval quality, and governance were NOT tested. | neighboring graph-substrate excursion |
| The shared substrate should remain representational and constitutional at the global level. Blackboard systems validate shared work by specialists; OpenCog shows the power and cost of making the graph itself executable. Local frame protocols and agents should own behavior unless an invariant clearly earns global mechanics. | Architectural lineage comparison. NOT a claim that executable graphs or global controllers are universally wrong. | neighboring graph-substrate excursion |
| Workflow graphs are not knowledge graphs. Making agents nodes in a control-flow graph would freeze the topology and contradict runtime instantiation with a home frame. | Conceptual contrast with workflow runtimes; NOT a performance or capability judgment about those tools. | neighboring graph-substrate excursion |
| The system has five immediate purposes: personal experimentation; honest project maps; cross-project idea formation; useful autonomy under human primacy; and revision-controllable graph history. Direct reuse of another project would frustrate the first purpose even when its concepts are instructive. | Human-owned purpose statement. NOT an implementation choice or a complete purpose inventory. | inter-cycle purpose refinement |
| Project truth and the cross-project idea commons should be connected but epistemically distinct. Operational maps answer what exists; the commons may contain looser notes, analogies, questions, and proposed connections without contaminating project truth. | Design inference from the human-owned purposes and existing three-plane rule. NOT yet tested against concrete node and relationship examples. | inter-cycle purpose refinement |
| Revision control favors authored text or similarly diffable files as the durable representation, with graph indexes and visualizations treated as rebuildable projections unless future pressure disproves that boundary. | Design inference, consistent with the current Markdown-first verdict. NOT a permanent storage decision and NOT tested at scale. | inter-cycle purpose refinement |
| Human primacy must be represented as authority, not reduced to a universal approval gate. Agents need meaningful delegated autonomy, while human intent and hard design judgments must remain explicitly human-owned and visible in provenance. | Human-owned governance direction plus design inference. Concrete action classes and escalation boundaries remain untested. | inter-cycle purpose refinement |
| Agent promotion is not inherently suspect. Authority to promote a claim follows its source, evidence, derivation, and assessed strength rather than a special frame-local definition of truth. Because code is the present reality of a software project, agents may substantially own descriptive architectural assertions that faithfully follow it. | Human clarification grounded in current Constellation architecture practice. Ambiguous derivations and non-code evidence standards remain untested. | inter-cycle authority refinement |
| Human primacy governs intent, values, contested interpretation, and future direction; it does not require humans to manually ratify every well-evidenced statement about present reality. | Human clarification of governance. The exact boundary between conclusive description and interpretation remains open. | inter-cycle authority refinement |
| All truth claims use one assertion model: identify the assertion and its source, attach evidence that supports or challenges it, and maintain a qualitative `weak`/`medium`/`strong` assessment that can change as evidence arrives. Numerical probability is unnecessary for the initial model. | Human-owned epistemic model. NOT yet tested against contradictory sources, scoped claims, or actual graph authoring ergonomics. | inter-cycle assertion refinement |
| Belief strength and lifecycle standing remain separate dimensions. A superseded assertion is not merely weak, a disputed assertion may have strong evidence on multiple sides, and rejected or historical claims must remain queryable without participating in ordinary current reasoning. | Design inference preserving the existing current/history and authority rules. Terminology and concrete transitions remain untested. | inter-cycle assertion refinement |
| `Weak`/`medium`/`strong` describes present support and safe provisional reliance, never resistance to revision or permission to skip verification. Its operational purpose is to allocate trust-but-verify effort: expose weak links and other possible holes in the reasoning supporting a task, while allowing even a strong assertion to be overturned immediately by decisive new evidence. | Human clarification of assertion-strength semantics. NOT yet tested through an agent traversal or verification task. | inter-cycle assertion refinement |
| Verification priority cannot come from strength alone. Agents should first identify assertions that are relevant and load-bearing for the current task, then use weakness, dispute, staleness, and evidence quality to decide where deeper verification context is worth spending. | Design inference connecting assertion strength to the map-first success criterion. The priority policy and vocabulary remain untested. | inter-cycle assertion refinement |
| The current Cartographer ontology is not the main demonstrated weakness. It already represents structures, capabilities, events, constraints, assumptions, decisions, claims, confidence, provenance, and evidence. Adding more tags before a real dogfood corpus and use evidence would optimize an unproven representation. | Map-first Scout audit of current doctrine, templates, builder, tests, and run feedback. The ontology has NOT been tested against the proposed cross-project idea commons. | graph support-system Scout audit |
| The intended map-use path is tiered: Commander/orchestrator reads the map and creates a mission frame; Implementer and Reviewer receive only scoped anchors and return map-impact evidence; Cartographer owns reconciliation. The gap is that orchestrator consumption and benefit are mostly attested rather than observed: the system cannot show whether the map found the seam, reduced code crawling, or merely received backfilled anchors. | Scout audit of Commander, Implementer, Reviewer, Cartographer, and Admiral workflow surfaces plus run feedback. NOT tested through a controlled mapped-project task. | graph support-system Scout audit |
| Four support pressures outrank detailed truth behavior: establish a representative dogfood map; make map consumption observable and anchors resolvable; surface semantic drift/staleness; and add federation above local project maps only after local use is proven. | Ranked Scout candidates. No issues were created and no architecture map was changed. | graph support-system Scout audit |
| The "three planes" framing over-commits twice. First, the layer count: history and possibility sit outside the map, but their organization is unfixed (separate layers, a combined timeline view of past-and-future, or finer-grained) — do not shoehorn to three. Second, the map's scope: a map is a frame-local construct for tracking existing artifacts that change over time (code, a book manuscript), tuned to the present; the wider network organizes ideas in many ways and is not map-shaped. The current-truth invariant binds maps specifically, not the network at large. | Human corrections during spec review, 2026-07-31. Supersedes the three-plane phrasing in earlier verdicts; the separation of current from history/possibility in default traversal stands for mapped frames. | spec review |
| "Review possible, not required" understates the norm: rigorous agentic review (cold reviewer, critic panel) is the standing floor — very little that changes how anything works should land wholly unreviewed. The variable is whether *human* eyes engage, which scales with consequence; human review is often mediated through conversation with an orchestrator (editing on the go without reading the artifact directly), and that counts. | Human clarification during spec review, 2026-07-31. | spec review |
| The move from one monolithic skill per role to a slim always-loaded kernel plus just-in-time skill fragments selected by the active spine step is a deliberate, headline architectural break — not an implementation detail of projections. The spec must state it loudly; jargon-dense phrasing that presumes the reader already holds the concept is a defect. | Human direction during spec review, 2026-07-31. | spec review |
| Lessons and Curator sweeps are one framework, not two: both collect what/why/impact observations — lessons post-fact from real runs, Curator predictively from hypothetical bad decisions — and both consolidate into either mechanization changes or instruction changes. The historical failure mode is reacting to a single observation in a vacuum; collate before overreacting. | Human reframing in inter-cycle tension discussion, 2026-07-31. NOT yet reflected in lesson/Curator contracts. | inter-cycle tension discussion |
| Pre-learning makes deletion safe: a simplification that removes doctrine files a predictive lesson naming the possible failure mode and the impact judged acceptable. The lesson is the tripwire — observed worse impact is pre-attributed evidence for rework. This replaces numeric instruction budgets: pressure against overgrowth comes from collation discipline plus fearless tripwired deletion, not caps. | Human design move in inter-cycle tension discussion, 2026-07-31. NOT yet tested on a real simplification. | inter-cycle tension discussion |
| Two-bin rule for doctrine items: can we afford to observe this failing once? Yes — prose, always eligible for experimental pruning with a predictive tripwire lesson. No — mechanize it (validator, hook, gate) and delete the prose version because the mechanism owns it. Rarity then only ever attaches to survivable rules, so "is this rarely-exercised rule dead?" stops needing an answer. Confirmed as the starting point for reworking the lessons framework. | Human confirmation in inter-cycle tension discussion, 2026-07-31. NOT yet applied to any real invariant inventory. | inter-cycle tension discussion |
| Projection timing is the wrong axis; the real rule is no stochastic step between canonical truth and the active surface. Ahead-of-time generation for slow-changing role-shaped doctrine (a diffable projection in git means human review is *possible*, not required — consistent with authority-not-approval-gate); deterministic per-run assembly keyed by spine node for task working sets; a manifest of what was loaded at which revision exists in all cases. Stochastic summarization in the load path is the forbidden move. | Human decision in inter-cycle tension discussion, 2026-07-31. NOT yet implemented; recipe format and manifest shape undefined. | inter-cycle tension discussion |
| Coherence ownership splits by strength. Semantic coherence is verified stochastically: through use (lessons expose incoherence after the fact) and through Curator-dispatched opinionated subagents with specific adversarial viewpoints (the cold-critic-panel pattern pointed at the corpus, producing proposals, never direct edits). Corpus coherence belongs to Curator. Everything between canonical truth and the active surface — assembly, routing, enforcement — is mechanical: LLMs detect, mechanisms enforce, because LLMs are not strong in repeatability (the spine's founding logic). | Human decision in inter-cycle tension discussion, 2026-07-31. Accepted cost: use-based detection pays for each incoherence with one degraded run. NOT yet implemented; sweep lenses and cadence undefined. | inter-cycle tension discussion |
| Commander is explicitly told to work map-first, but the input contract is scattered and underbound: its context step says "current map" without naming `docs/architecture/index.md` or a resolved alternative, and `MISSION_FRAME.template.md` is the output shape rather than the source. The canonical entrypoint appears in a separate Charter-generated `AGENT_GUIDE`. Density and indirection make the central map-first behavior easy to infer incorrectly or backfill after code reading. | Direct doctrine/template trace across Commander and Charter. NOT tested in a consuming repository with customized context paths. | graph support-system Scout audit refinement |

## Open threads

### Current high-level orientation

- Which real project and task set should serve as the representative dogfood corpus for proving map-first value?
- What is the lightest evidence that an agent used the map to choose a seam before opening source?
- What is the smallest canonical map-input contract the orchestrator can consume directly: resolved entrypoint, explicit absent state, and source anchors used?
- What map-health signal would reveal likely drift without pretending a changed file proves a claim false?
- What is the smallest federation seam that connects project-owned maps without weakening their local structural spines?

The more detailed assertion-strength, verification-order, and cross-frame mutation questions below remain preserved, but should not drive the next pass until these support-system pressures are exercised.

- Should Fred experience a statement primarily as a direct edge, an assertion node, or a single `connect` command that hides both representations?
- Which five to ten traversal questions should define the first corpus and reveal whether the graph actually accelerates thought?
- What semantic-cost and hub-penalty rules make bridge discovery surprising but not noisy?
- Which observable pressures would show that Markdown is no longer sufficient: authoring friction, broken links, traversal latency, maintenance drift, or inability to answer map-level questions?
- Which architectural questions must the representation answer without code for an agent to locate the right seam reliably?
- How should an agent explicitly request possibility or history context from a current node without those layers leaking into ordinary traversal?
- What threshold makes present necessity worth stating rather than leaving it implicit in the current structure?
- When an agent crosses out of its home frame, what may it do beyond reading and exploring: propose foreign connections, create possibility-layer material, or mutate another frame's current truth?
- Can an agent have more than one home frame, or does multiple standing jurisdictions imply a different kind of agent?
- Should a home frame be immutable for the lifetime of an instantiated agent, with a changed home requiring a new agent, so authority and provenance remain legible?
- What is the cross-frame mutation rule: read globally, write locally, and propose changes to foreign frames; or something looser?
- How should an agent combine task relevance, load-bearingness, assertion strength, staleness, dispute, and source quality into a simple explainable verification order without inventing a false numerical score?

### Excursion Brief: recursive agent learning without instruction accretion

#### The one named question

How do active agent-learning and self-improvement systems convert experience into reusable capability without appending every lesson to the runtime instruction context?

#### Type

research

**Why this type:** the relevant projects, papers, and implementation boundaries are current external facts, while their failures expose direct analogues for Constellation's layered-doctrine density.

#### What answered looks like

A comparison of 5-8 distinct systems or research lines across what is learned, where it is stored, how it is retrieved or compiled into behavior, how conflicts/staleness are handled, what gets deleted or demoted, and whether improvement is evaluated globally rather than only on the triggering task. End with transferable mechanisms and attractive traps.

#### Budget / stop conditions

- Use primary papers, official repositories, and official project documentation.
- Prefer systems with concrete memory, skill, prompt, policy, or optimization mechanics.
- Do not recommend adopting a framework or equate benchmark improvement with durable system improvement.
- Stop when mechanisms repeat: append, retrieve, compile, distill, replace, prune, or evaluate.

#### Research excursion

- **Handoff:** `crew-handoffs/recursive-agent-learning.md`
- **Findings target:** `evidence/recursive-agent-learning.md`

### Excursion Brief: institutional learning without doctrine overload

#### The one named question

How do safety-critical or knowledge-intensive human organizations retain lessons while preventing checklists, procedures, and doctrine from becoming too dense to use?

#### Type

research

**Why this type:** recursive learning and instruction accretion predate AI agents; mature organizational practices may expose governance, expiry, consolidation, and usability mechanisms that software analogies miss.

#### What answered looks like

A primary-source-grounded comparison across 4-7 lineages such as aviation/checklist design, incident and postmortem systems, standard work, military or emergency doctrine, safety management, or knowledge governance. Separate durable principles from domain-specific regulation. Identify how lessons enter, who owns consolidation, how usability is tested, and how instructions are retired.

#### Budget / stop conditions

- Prefer regulator, standards-body, institutional handbook, and primary research sources.
- Avoid inspirational management summaries and loose checklist folklore.
- Do not import safety-critical ceremony wholesale into a personal experimentation project.
- Stop when the same lifecycle mechanisms recur.

#### Research excursion

- **Handoff:** `crew-handoffs/institutional-doctrine-learning.md`
- **Findings target:** `evidence/institutional-doctrine-learning.md`

### Excursion Brief: software policy systems that resist layering

#### The one named question

Which software architecture patterns keep recursively edited policy, configuration, documentation, or rules understandable as exceptions and lessons accumulate?

#### Type

research

**Why this type:** Constellation's problem is partly a declarative-system architecture problem: defaults, deltas, overrides, compilation, validation, ownership, and removability all have established software precedents.

#### What answered looks like

An opinionated comparison of patterns such as canonical normalized models with generated projections, defaults-plus-deltas, policy compilation, modular rule ownership, decision records, usage telemetry, expiry/review triggers, and corpus linting. Ground patterns in official specifications, mature projects, or primary research; identify when each reduces reader burden versus merely moving complexity.

#### Budget / stop conditions

- Compare mechanisms, not product feature lists.
- Use primary specifications, official design documentation, or strong research sources.
- Include deletion/removability and conflict handling, not only composition.
- Stop after 5-8 distinct mechanisms and their failure modes are grounded.

#### Research excursion

- **Handoff:** `crew-handoffs/policy-architecture-accretion.md`
- **Findings target:** `evidence/policy-architecture-accretion.md`

### Excursion Brief: neighboring graph-substrate projects

#### The one named question

Which active projects or architectural lineages are exploring shared graphed substrates for agent understanding, memory, coordination, or cognition, and what do their differing boundaries teach us about home-framed, recursively instantiated agents over a shared network?

#### Type

research

**Why this type:** project capabilities, maintenance, and architectural claims are current external facts, while blackboard and cognitive-architecture precedents provide important conceptual lineage.

#### What answered looks like

A comparison of 5-8 genuinely distinct projects or lineages across graph purpose, agent identity/instantiation, current/history treatment, traversal/context assembly, behavior location, authority, and operational weight; explicit near-term lessons and attractive traps; primary-source citations and tested/NOT-tested scope.

#### Budget / stop conditions

- Prioritize current official documentation, repositories, and primary papers.
- Include projects that expose different conceptualizations, not six interchangeable graph-memory libraries.
- Do not install or prototype anything.
- Stop once the main design axes and transferable lessons repeat.

#### Research excursion

- **Candidate families:** GraphRAG-style map/retrieval, temporal agent memory graphs, cognitive hypergraph substrates, multi-agent runtimes with scoped identity, and blackboard/shared-workspace architectures.
- **Findings target:** `evidence/neighboring-graph-projects.md`
- Would recording which map nodes and relationships an agent read provide a useful first measure of map-first behavior without changing the Markdown substrate?

### Excursion Brief: ActiveGraph comparison

#### The one named question

How does the current navigation-first knowledge-network direction compare with ActiveGraph's event-sourced reactive graph runtime, and which similarities are genuine architectural through-lines versus terminology or purpose mismatches?

#### Type

research

**Why this type:** ActiveGraph is a current external project whose implemented concepts, runtime contract, and status must be grounded in primary sources.

#### What answered looks like

A concept-by-concept mapping of current graph, history, possibility, frames, relations, context scoping, authority, and runtime behavior; a clear boundary between useful reference ideas and premature adoption; and explicit tested/NOT-tested scope.

#### Budget / stop conditions

- Use the current official repository, documentation, and paper.
- Do not install ActiveGraph or build a prototype.
- Stop once the model, strongest overlaps, load-bearing differences, and near/future relevance are grounded.

#### Research excursion

- **Sources:** official ActiveGraph repository, docs, and `The Log is the Agent` paper.
- **Findings:** [ActiveGraph comparison](C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/activegraph-comparison.md)
- Which relationship classes need retained assertion/retirement history, and which may simply appear or disappear from the current graph?
- What epistemic statuses and authority rules are universal enough for the kernel?
- Which invariants must live outside the agent process?
- What is the smallest domain-neutral ontology that still earns its interface?
- Which current concepts belong in a generic kernel, and which remain coding-domain policy?
- What evidence would show that genericization is unnecessary or actively harmful?
- How should external novelty enter without producing trend-driven architectural churn?
- Where should informal ambiguity remain welcome rather than being forced prematurely into logic?
- Which frame relationships are universal enough to standardize, and which should remain frame-specific vocabulary?

### Excursion Brief: graph models and traversal

#### The one named question

Which graph data models and traversal patterns best support rapid connection creation, explainable crawling, evolving schemas, overlapping frames, provenance, and long-term maintenance?

#### Type

research

**Why this type:** this requires comparison of established graph models and query/traversal semantics before choosing implementation tooling.

#### What answered looks like

A recommendation-led comparison of property graphs, RDF/semantic graphs, and plausible hybrid or relational approaches; concrete traversal behaviors; maintenance implications; and a scoped recommendation for this personal, agent-shared system.

#### Budget / stop conditions

- Use current primary standards, official documentation, or research papers; stop after the main model families and traversal patterns are compared.
- Do not build a prototype or modify repositories.
- Report exactly what was and was not tested; distinguish source facts from design inference.

#### Research excursion

- **Sources:** current ISO GQL/openCypher material where accessible, W3C RDF/SPARQL/SHACL specifications, official graph-model documentation, and relevant primary papers.
- **Findings format:** cited findings, concrete query/traversal examples, opinionated recommendation or hybrid, tensions preserved.

### Excursion Brief: current tooling alternatives

#### The one named question

Which currently maintained graph tools are credible for a personal, local-first, agent-accessible knowledge network, and what are their tradeoffs for embedding, querying, schema evolution, provenance, traversal, visualization integration, and operational burden?

#### Type

research

**Why this type:** tool maintenance, capabilities, licensing, APIs, and deployment shapes are current external facts.

#### What answered looks like

A short-list comparison grounded in current official documentation, including at least an embedded/local option, a mature graph server, a semantic/RDF option, and a minimal relational baseline; explicit exclusions; and a recommended first experiment rather than a permanent commitment.

#### Budget / stop conditions

- Use current primary documentation and repositories; do not rely on remembered project status.
- Stop after 4-7 credible alternatives and major exclusions are grounded.
- Do not install dependencies or create a prototype.

#### Research excursion

- **Sources:** official documentation/repositories for candidate tools; current standards documentation for their query languages.
- **Findings format:** concise comparison, citations per claim, recommendation, tested/NOT-tested scope.

### Excursion Brief: `journal-system convergence`

#### The one named question

What representation, interaction, and reasoning patterns already exist in Fred's journal-system work that should inform the generalized knowledge network?

#### Type

`research`

**Why this type:** the answer should come from the existing journal repository and its durable artifacts, not from speculative redesign.

#### What "answered" looks like

A cited account of the journal system's current conceptual model, data/knowledge representation, agent interaction model, and intended reasoning behavior; a comparison to Constellation's current architecture network; and a short list of genuine convergences, tensions, and open questions.

#### Budget / stop conditions

- Inspect the most likely local and GitHub repository plus directly relevant current docs/code; stop after the conceptual model and important seams are grounded.
- Do not modify the journal repository, file issues, or design a replacement.
- **Scoped nulls:** if the journal repository cannot be found or lacks durable design artifacts, report exactly where and how it was searched and what was not tested.

#### Research excursion

- **Sources:** the explicitly identified primary repository, `https://github.com/fredbuilds/journal-system`, including its current README, design, architecture, schema, and code artifacts. `thinking-out-loud` was inspected briefly due to mistaken identification and is excluded from all findings.
- **Findings format:** cited repository paths/URLs; separate observed behavior from inference; contradictions surfaced; explicit tested/NOT-tested scope.

## Excursion findings: recursive learning without instruction accretion

### Evidence-backed convergence

Three independent excursions found the same missing boundary from different directions:

- **Recursive agent systems:** experience should move through candidate, validation, durable capability, task projection, and retirement. GRASP is the closest direct precedent: a bounded library accepts `add` / `modify` / `remove` changes only after testing both prior failures and prior successes. Retrieval and progressive disclosure reduce runtime load but do not by themselves create coherence.
- **Institutional doctrine:** mature organizations keep observations/history, proposed interventions, rationale/training, and current operative procedure as different artifacts. Promotion is selective and owned; procedures are tested in realistic use; revision and rescission are normal lifecycle outcomes.
- **Software policy architecture:** an accumulating canonical corpus should compile or resolve into a small reader-facing projection. Composition must be explicit—constraint, selection, default, or authority-bearing exception—rather than "read all layers and reconcile mentally." History stays adjacent to the current interface, not inline with it.

The local corpus already has partial defenses: lesson `ADD / AMEND / RETIRE`, scoped injection, hard lesson caps and dormancy, Git history, progressive skill disclosure, Curator size/duplication checks, and reproduction drills. The seam is that most lifecycle pressure stops at promotion into permanent skills, shared doctrine, templates, and references. The Curator can observe sprawl and sediment, but is human-only and advisory; it explicitly lacks baseline drift and portfolio evaluation. On 2026-07-30 its current measurement returned 55 flagged findings.

### Density is at least three different problems

- **Runtime density:** too much material is loaded for the present task. Retrieval, progressive disclosure, and task-specific projection address this.
- **Structural density:** one operative contract is scattered across several sources. Canonical concern ownership and a resolved interface address this.
- **Evolutionary density:** each correction appends a clause while superseded concepts remain active. Replacement, compilation, regression tests, and rescission address this.

Shorter prose or richer tags do not solve all three. Shared references can reduce literal duplication while worsening structural density; retrieval can reduce tokens while leaving conflicts and stale rules intact.

### Candidate support-system boundary (not yet a design)

Treat accumulated learning and active doctrine as separate products. A proposed doctrine change should identify a named current contract and state whether it will:

- add a genuinely new contract;
- replace or merge existing guidance;
- localize it to a role, frame, project, or workflow step;
- compile it into a tool, template, validator, or other mechanism;
- move rationale/history out of the operative path; or
- remove a superseded rule.

The active result should be an inspectable, provenance-bearing projection for the agent's role and current step. Representative scenarios should test both the triggering failure and previously successful behavior. Git can retain removed history without requiring old instructions to remain active.

### Both modules and projections

Concern-owned modules and task projections solve different problems and appear jointly necessary:

- **Modules preserve semantic integrity.** The architecture map is itself a concern-owned module: it owns the current structural view and exposes a small navigation interface without forcing every consumer to rediscover code structure.
- **Projections preserve attention.** A role/frame/task view selects the few modules and contracts relevant now; it does not become their new canonical home.
- **The substrate preserves recoverability.** A projection must carry provenance and remain openable back into its source modules. If it is absent, stale, contradictory, or incomplete, the agent enters an explicit degraded mode: report the failure, verify against primary sources, and reconstruct only the local context needed for the task.

This is not repeated compaction if projections are regenerated from full current modules rather than summarized from prior projections. Consolidation changes the canonical model by replacing or removing obsolete doctrine; projection leaves the model intact and selects a working set. History stays available outside both through Git and linked evidence.

The resulting safety property is important: the map and other modules should accelerate and orient cognition, not be the sole place cognition is possible. A broken interface should make work slower and visibly less certain, not silently lobotomize the agent.

### Concern ownership is broader than skill ownership

Prior art suggests that "concern-owned module" should not imply "independently triggered agent skill." At least four module shapes are present:

- **Knowledge module:** owns a current model and query/navigation interface. The architecture map is this shape; Cartographer is its maintainer, while many roles consume it.
- **Policy/aspect module:** constrains several roles but has no meaningful standalone workflow. Authority, evidence, and completion invariants often have this shape and need explicit composition rather than another router target.
- **Capability/subskill:** owns reusable behavior with a describable initiation set, procedure, termination/result, and failure mode. Map intake may be this shape even though the map itself is not.
- **Role/orchestrator:** owns authority, a long-lived control loop, and composition of multiple capabilities toward an outcome. Commander and Admiral are this shape.

The strongest boundary criteria found in prior art are complementary:

- Parnas information hiding: group around a design decision likely to change; expose an interface that shields consumers from that change.
- DDD bounded contexts: split where vocabulary or the internally consistent model changes; make cross-context relationships explicit.
- Reinforcement-learning options: a behavioral unit has an initiation set, internal policy, and termination condition.
- Aspect-oriented modularity: genuinely crosscutting concerns require configuration-aware interfaces; forcing them under one primary module only hides global coupling.
- Evolutionary coupling: use change history as evidence—material that repeatedly changes together may share an owner, while a change that repeatedly fans across modules exposes a bad boundary. Co-change is diagnostic, not automatic proof.

A candidate concern earns an independently loadable subskill only if its trigger, output/termination, failure behavior, canonical owner, and independent behavioral evaluation can be stated without replaying the parent role. Otherwise it likely belongs as a reference inside a skill, a shared policy/rail, or a knowledge interface. Extraction that creates only a pointer and still requires the caller's whole internal model is a shallow split.

### Role continuity does not require one undivided skill or context

A role may legitimately own and compose several concerns. Splitting its doctrine into subskills does not require splitting the acting agent at every boundary. Keep three boundaries independent:

- **Module boundary:** where knowledge, policy, or behavior has a canonical owner and testable interface.
- **Context boundary:** where enough state has been externalized that work could continue after compaction or in a fresh context.
- **Agent boundary:** where an independently instantiated worker is useful for parallelism, cold review, specialization, or isolation.

The same capability can therefore execute in-process by Commander when conversational or reasoning continuity matters, in a subagent when fresh/independent context matters, or mechanically when its behavior is decidable. Its artifact contract stays the same across modes.

Commander can remain the durable human-facing role: it owns protected intent, authority, end-to-end coherence, and permission to advance or reopen the run. `understand`, `specify`, `plan`, `execute`, and `evaluate` become candidate transformations over shared run state, not necessarily a fixed chain of separate agents.

The durable run graph is the defense against a lossy bucket brigade. Each stage writes an attributed current artifact linked to evidence, assumptions, open questions, and upstream artifacts; downstream work references those nodes instead of copying a progressively compressed summary. A later discovery may reopen an upstream assertion rather than being forced through a one-way baton pass.

Failure modes to preserve as open pressure: premature freezing of intent, local optimization by specialist stages, responsibility diffusion, handoffs that reproduce the entire context, and so much transition ceremony that one coherent agent would have been cheaper.

### Spine nodes as deterministic context selectors

The existing spine gives concern-specific loading a natural selection mechanism. The workflow state already knows which job is active, so a node can declare the capability module(s) required for that job; no general semantic router needs to infer the primary skill from a vague request.

Candidate separation:

- The **spine node** owns purpose, timing, required inputs, expected output, authority/checkpoint, and postconditions—the `what` and `when`.
- The **loaded capability module** owns how to perform that job—the `how`—and can evolve independently.
- The **Commander kernel** owns the human relationship, protected intent, state transitions, dispatch choice, integration, reopening, and terminal accountability.
- The **run graph/artifacts** carry accumulated state between nodes, preventing just-in-time instruction loading from becoming just-in-time amnesia.

This is progressive disclosure keyed by explicit workflow state rather than only by natural-language similarity. It could substantially shrink the always-loaded Commander surface while preserving one Commander identity. A node capability may run in the same agent context; node-local loading does not imply subagent dispatch.

The likely always-on minimum is small but nonzero: how to drive/recover the spine, how authority and human escalation work, how to verify a node result, and how to find/load the node's capability contract. Crosscutting invariants should be compiled into this kernel or the node projection, never copied independently into every job note.

Open failure tests: missing or wrong capability binding must fail visibly; later nodes must be able to reopen upstream artifacts; node notes must not accrete restated global doctrine; and the system must demonstrate that total active context falls rather than merely moving text behind more pointers.

### Skills and architecture as one operational graph

The prior separation between "how to work" skills and "how the world works" architecture appears artificial. They are different modalities in one connected substrate:

- descriptive/current assertions: components, capabilities, interfaces, dependencies, and current structural truth;
- normative assertions: authority, invariants, constraints, and human decision boundaries;
- procedural nodes: roles, skills, spine steps, tools, templates, and execution transitions;
- epistemic/evidence nodes: sources, tests, confidence, disputes, and verification paths;
- history and possibility remain separate frames linked to, but not traversed as, current truth by default.

A skill need not be a self-contained prose island. It can be an entry node plus a traversal contract. For example, Commander `context` can link directly to the canonical architecture index; the current spine node can link to its capability contract; that capability can follow typed edges to relevant map regions, evidence, templates, and mechanisms. The spine itself is already a workflow subgraph embedded in the larger project graph.

Candidate relations include `ORIENTS_WITH`, `APPLIES_TO`, `GOVERNS`, `CONSUMES`, `PRODUCES`, `VERIFIES`, `MAINTAINS`, `IMPLEMENTS`, `DEPENDS_ON`, and `SUPERSEDES`. Their value is not ontology completeness but explicit multi-hop traversal such as:

`plan node -> map-intake capability -> architecture index -> affected capability -> structural anchors -> governing constraints -> verification surfaces`.

The CrabRAG talk supplied a directly analogous retrieval demonstration: with the same home-network facts, vector similarity could not reliably answer which end-of-life software was exposed to the internet, while the graph agent followed explicit multi-hop relationships and identified the relevant server and exposed management paths. The demonstrated lesson is that similarity is not relationship and that hybrid vector seeding plus graph traversal can produce precise, explainable context. It does **not** establish that Neo4j, CrabRAG, or any particular database is necessary for this project.

This unified view may reduce instruction density: skills link to canonical world/policy nodes instead of restating them, and spine state supplies the traversal seed. It also raises sharper controls: traversal must be typed and budgeted; descriptive `is`, normative `should`, and procedural `do` cannot be flattened; write authority must differ by node/frame; broken links or stale projections must fail visibly; and current/history/possibility separation remains essential even inside one substrate.

Video and corroborating material: [CrabRAG talk](https://www.youtube.com/watch?v=Q0VkgCyNVUg), [timestamped episode description](https://www.ivoox.com/crabrag-why-automated-assistants-need-graph-memory-not-audios-mp3_rf_177763681_1.html), and [OpenClaw memory model](https://github.com/openclaw/openclaw/blob/main/docs/concepts/memory.md).

Primary references: [Parnas on decomposition](https://doi.org/10.1145/361598.361623), [DDD bounded contexts](https://martinfowler.com/bliki/BoundedContext.html), [Sutton, Precup, and Singh on options](https://www.cis.upenn.edu/~mkearns/papers/barbados/sps-macro.pdf), [Kiczales et al. on aspect-aware modular reasoning](https://www.cs.ubc.ca/~gregor/papers/kiczales-icse05-aopmr.pdf), and [co-change clustering study](https://doi.org/10.1016/j.jss.2019.03.014).

### Tool-mediated traversal, not document hopping

The graph should be **queried, not manually read**. A role or spine node supplies intent, known anchors, allowed relation types, and a traversal budget; a retrieval component computes a relevant neighborhood or path and returns a bounded, ordered, provenance-bearing context packet. The agent reasons over the revealed hops and selectively verifies their sources instead of repeatedly opening documents and deciding each next link itself.

SkillGraph demonstrates this separation directly. Its retrieval procedure selects task-relevant seed skills, recovers incoming prerequisites with bounded breadth-first search, explores outgoing relations with weighted beam search, topologically orders the resulting subgraph, caps it, and only then places that working set in the policy prompt. This is closer to a domain-specific **context compiler** than to ordinary semantic document retrieval.

GraphRAG is an umbrella rather than one behavior. Microsoft GraphRAG local search uses semantically matched entities as graph entry points and gathers connected entities, relationships, community reports, and linked source chunks; global search primarily reasons over precomputed community reports; DRIFT iteratively mixes community context with local follow-up search. Neo4j's VectorCypher and HybridCypher retrievers provide the more literal primitive: find seed nodes by semantic/full-text retrieval, then execute a declared graph traversal around them. Text-to-Cypher can invent traversal queries, but moves query correctness back into probabilistic model behavior.

A candidate Constellation query result should expose the route, not merely an answer or opaque bundle: selected seeds; each typed hop; included nodes and source excerpts; ordering and exclusion reasons; confidence/authority; revision identity; and any unresolved or broken edges. Traversal tooling solves context selection and relationship navigation. It does not establish truth, authority, or normative relevance; those remain properties of the graph contract and human/agent governance.

This does not require abandoning Markdown. Authored Markdown can remain canonical and revision-controlled while a generated adjacency index plus a small CLI/MCP-like query surface performs traversal. Neo4j or a richer GraphRAG stack remains a future implementation option if scale or query pressure earns it.

The useful Neo4j/Cypher decomposition is more precise than database/query-engine. Neo4j provides persistent graph storage, indexes, transactions, graph algorithms, and an engine that executes graph queries. Cypher is the declarative query language: it describes node/edge patterns, filters, variable-length paths, and returned projections, but does not itself execute them. In a Markdown-first version, Markdown is the authored source of record; a generated node/edge index is the database-like projection; a deterministic traversal library is the query engine; and an optional small agent translates conversational intent into a strict query request. The agent may choose anchors and traversal recipes, but should not perform the hop-by-hop crawl itself.

A minimal query pipeline is therefore: `natural-language need -> strict query plan -> deterministic graph traversal -> visible paths and bounded source-backed context -> agent interpretation`. Fixed named recipes such as `orient-to-capability`, `find-governing-policy`, `recover-prerequisites`, and `find-verification-surfaces` may provide most early value without implementing a general Cypher-like language. Semantic retrieval or a small agent is useful when the starting anchor is vague; exact anchors, traversal, filtering, ordering, and budget enforcement should remain mechanical wherever possible.

Sources: [SkillGraph](https://arxiv.org/html/2605.12039v1), [Microsoft GraphRAG query modes](https://microsoft.github.io/graphrag/), [Microsoft local search](https://microsoft.github.io/graphrag/query/local_search/), [Microsoft global search](https://microsoft.github.io/graphrag/query/global_search/), and [Neo4j GraphRAG retrievers](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html).

### SkillGraph lessons beyond traversal

SkillGraph's more consequential contribution is not merely storing skills in a graph; it closes the loop between use, evaluation, topology, and future retrieval. Its skill records are compact and operational (`title`, `principle`, `when_to_apply`, `category`), its ontology is deliberately small and retrieval-serving (`prerequisite`, `enhancement`, `co-occurrence`), and its retrieval output is an ordered working set rather than a bag of relevant documents.

Its maintenance vocabulary directly addresses instruction accretion: failure can insert a missing skill; overlapping neighborhoods can nominate a merge; high-use/low-success skills can be split; consistently failing skills can be deprecated; successful paths reinforce edge weights; co-use can nominate relationships; and unused edges decay. Total knowledge may continue growing while the active set and retrieved context remain bounded. Graph topology therefore becomes evidence about module granularity and retrieval utility, not merely a navigation display.

Several separations are required before translating this into Constellation. Retrieval weight is evidence of present usefulness, not truth; co-occurrence is a candidate connection, not a semantic claim; task reward is not a sufficient proxy for human intent; and agent-generated insert/merge/split proposals cannot silently alter human-owned doctrine. Semantic truth/authority and empirical retrieval utility need distinct edge or metadata channels. Candidate topology changes should remain proposals until the relevant authority promotes them, while low-risk derived ranking signals may evolve mechanically.

The paper's ablations also argue against one universal retrieval policy. Dependency ordering mattered most in rigid multi-step ALFWorld tasks, while graph quality and evolution mattered more in flexible WebShop navigation. Constellation's spine, architecture orientation, philosophical exploration, and cross-project analogy may therefore need different named traversal recipes over the same graph substrate.

`failure -> lesson` remains a valid observation path; the mistake is treating the lesson as a direct instruction patch. SkillGraph adds a second loop that asks what the accumulated failure evidence means for the capability structure. In the paper, graph evolution runs at validation checkpoints: rollout success/usage statistics and fixed thresholds select candidates, while a strong teacher model authors insert, merge, and split mutations; deprecation, path reinforcement, co-occurrence discovery, decay, and pruning are driven more mechanically.

For Constellation, this suggests two distinct compilation concerns. An **evolution curator** consumes lessons, run evidence, existing skill neighborhoods, and retrieval traces, then proposes the appropriate mutation class: `NO_CHANGE`, `INSERT`, `AMEND`, `MERGE`, `SPLIT`, `RELINK`, `RETUNE_RETRIEVAL`, or `RETIRE`. A **context compiler** subsequently projects the resulting current capability graph into the bounded instruction set for a particular role and spine node. Lessons are durable evidence and diagnostic input; they are not themselves the active doctrine. Validation and authority decide which structural proposals become current, especially where human-owned normative guidance is involved.

Current Constellation only partially supplies the evolution curator's input. `.agent-work/AGENT_FEEDBACK.md` is append-only and the fresh-context Lessons Auditor separates `Observed`, `Cost`, `Proposal`, grounding, and corroboration. However, the feedback itself is free-form prose, Commander is encouraged to immediately apply an understood fix, and `.agent-work/LESSONS.md` is deliberately a transitory inbox whose audited entries graduate and disappear. The durable structured object is therefore often the locally diagnosed remedy, while the underlying episode remains difficult to query and compare across runs.

A stronger learning substrate would preserve an immutable **feedback episode** before diagnosis: run/project/frame, role and spine step, task intent, active skill/context projection and revision, expected behavior, observed behavior, impact/cost, recovery or workaround, and artifact/telemetry references. Suspected cause and proposed remedy are separate, optional assertions. A lesson then generalizes across one or more episodes; a mutation proposal cites the lesson and affected graph neighborhood; an accepted mutation changes current capability truth. The lineage is `episode -> supports/challenges lesson -> motivates mutation -> changes active graph`, preserving local observations even when later evidence overturns the original diagnosis.

Much of episode capture can be mechanical from existing engine state: work-id, role, active spine node/gate, loaded context manifest, refusals/BLOCKs/waives/reopens, failed commands, rework counts, and artifact paths. Agent-authored fields can stay small: expected, observed, impact, workaround, and optional hypothesis. Success/clean-use telemetry is also needed as a denominator; a failure-only database cannot distinguish an intrinsically bad instruction from a generally effective one that met an exceptional case.

The current Curator is the natural conceptual owner but not yet the implemented semantic owner: its live contract measures and mechanically mends the finished corpus, routes semantic redesign to Triage, and leaves portfolio analysis dormant. Broadening it into graph evolution—or pairing it with a concern that prepares structured evolution proposals—remains an open boundary rather than an assumed role change.

Transfer is suggestive, not demonstrated. SkillGraph is an arXiv v1 evaluated in simulated, single-environment settings, uses a strong teacher model for graph operations, and explicitly leaves cross-environment transfer and broader scaling open. Its mechanisms are useful design evidence; its reported performance does not validate a human-governed, cross-project knowledge network.

### Consolidated next-step roadmap

The immediate objective is not a universal knowledge platform or graph database. It is one closed vertical slice proving that Constellation skills can natively enter, consume, and improve a shared graph.

1. **Name the minimum graph contract.** Keep Markdown/Git as authored truth. Give current architecture, skill/capability, spine-node, policy/constraint, verification, and evidence nodes stable IDs; use only relation types needed by the tracer; preserve current/history/possibility separation and authority/provenance. Compile and validate a generated adjacency projection rather than hand-maintaining a second truth.
2. **Make one skill path graph-native.** Use Commander `context -> plan` as the tracer. Keep a small Commander kernel, bind the active spine node to a map-intake capability/query recipe, and link that capability to the architecture index, affected capabilities, governing constraints, and verification surfaces. Replace duplicated Commander prose only after the linked path proves it can carry the behavior.
3. **Provide deterministic context queries.** Implement named, bounded traversal recipes before a general query language: orient to capability, recover prerequisites, find governing policy, and find verification surfaces. Return visible paths, source excerpts, revision/provenance, omissions, and broken links. A model may resolve vague natural-language anchors; traversal, filtering, ordering, and budget enforcement remain mechanical.
4. **Make graph use observable.** Every produced context packet gets an identity/manifest recording graph revision, seeds, recipes, nodes, edges, and source sections. Representative Commander tasks measure whether the map finds the seam before broad source crawling, whether targeted code verification remains correct, and whether active context shrinks without losing critical constraints. Missing/stale graph paths enter explicit degraded mode rather than silently blocking cognition.
5. **Capture structured feedback episodes.** Before local diagnosis, preserve expected/observed behavior, task intent, role/spine step, active context manifest, impact, workaround, and evidence. Keep hypothesis and proposed remedy separate. Mechanically capture blocks, waives, retries, reopens, commands, artifacts, and success/use denominators where practical.
6. **Turn Curator into the evolution boundary.** Let Curator—or a preparation concern it owns—query episodes, lessons, retrieval traces, and graph neighborhoods, then propose `NO_CHANGE`, `INSERT`, `AMEND`, `MERGE`, `SPLIT`, `RELINK`, `RETUNE_RETRIEVAL`, or `RETIRE`. Validate proposals against triggering failures and prior successes. Derived retrieval utility may update mechanically; human-owned doctrine and consequential semantic changes retain their authority gates.
7. **Generalize only after the loop works.** Expand to other spine nodes and roles, then project/frame types such as the idea commons, journal, and philosophy. Revisit Neo4j/Cypher or another backend only when the generated Markdown projection exhibits real query, maintenance, concurrency, or scale pressure.

The closed-loop success criterion is: `graph-authored current truth -> skill-native bounded traversal -> targeted work -> structured episode evidence -> Curator mutation proposal -> improved future traversal`, with every transition inspectable and revision-controlled.

### High-value tracer question

Can Commander map-first intake be expressed as one canonical concern-owned contract, projected into Commander `context` / `plan`, while deleting the scattered prose it supersedes—and can representative tasks show that agents use `docs/architecture/` before broad code exploration without regressing other intake behavior?

This would test the lifecycle boundary without committing to a graph database, policy language, new ontology, or corpus-wide rewrite.

### Open tensions

- ~~Instruction-surface budget~~ — resolved 2026-07-31 (see verdicts: collation discipline + tripwired deletion replace numeric budgets).
- ~~Who owns coherence after promotion~~ — resolved 2026-07-31 (see verdicts: sensors/actuators split). Residual: which adversarial viewpoints the coherence-hunting subagents should take, and on what cadence.
- ~~Behavioral probes~~ — resolved 2026-07-31: probes are not separate machinery; every change posts its expectation (predicted failure mode or expected improvement) and the ordinary lesson stream supports or challenges it. Undetectable-plus-catastrophic already routes to mechanization via the two-bin rule. Humans adjudicate observed-vs-predicted impact.
- ~~Projection timing~~ — resolved 2026-07-31 (see verdicts: no-stochastic-load-path rule; split by change rate). Residual: concrete recipe format and manifest shape.
- ~~Telemetry~~ — resolved 2026-07-31: honest telemetry is a byproduct of mechanisms already running (projection manifests, engine refusals/reopens/rework counts, failed commands). New watching infrastructure must earn its way in via a specific question someone is actually asking.
- ~~Dead-looking invariants~~ — resolved 2026-07-31 (see verdicts: two-bin rule; catastrophic-class invariants get mechanized, prose is survivable by construction). Residual, explicitly deferred as an implementation detail to try something on: how to mechanize collation — ensuring observations that rhyme get grouped toward a single solution rather than each triggering its own patch.

### Durable reports

- [Recursive agent learning](C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/recursive-agent-learning.md)
- [Institutional doctrine learning](C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/institutional-doctrine-learning.md)
- [Software policy architecture](C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/policy-architecture-accretion.md)

## Rejected ideas (with reasons)

- **Immediate Neo4j crawl experiment** - deferred, not permanently rejected. It adds a server and storage decision before testing whether a high-level Markdown map already changes agent behavior. Revisit only after observed navigation, maintenance, or connection-building pressure.
- **Adopting ActiveGraph** - rejected for this exploration. ActiveGraph is being used only as an external conceptual comparison; no implementation or future-runtime presumption should be carried forward.

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun | Purpose, users, successful use, global-vs-local structure, declared frames, and convergence with Journal System. | The project is a personal, agent-shared idea-enabling network: globally unstructured, locally rigorous through declared overlapping frames. Journal System and Constellation already supply two compatible domain frames and reveal history/current-view plus epistemic-authority seams as the next questions. |
| 2 | compare | Graph structure, crawling behavior, connection creation, maintenance, and current tooling alternatives. | Use an event-backed statement multigraph with a rebuildable attributed property-graph crawl view. Keep traversal behind a bounded, provenance-bearing contract. Learn the crawl language in a disposable Neo4j CE fixture, then test one contrasting backend based on observed friction; preserve database-neutral IDs and exports throughout. |
