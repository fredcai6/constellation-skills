# Excursion Result: Deleuze's machines and agent networks

Cycle 3 (refine), `explore-memory-graph`. Research excursion, one focused pass, 2026-08-04.

## Short answer

The intersection is **thin but not empty**, and it is thinner than the volume of citation suggests.

Across the searched literature, exactly **one** system turns a Deleuzian principle into running code with a measurable trigger (Serrano, Kevari & Narayan 2026 — a "Rupture Protocol" that watches a knowledge graph for edge-density concentration and injects heterodox material when it crosses a threshold). That system is a proof of concept with **no quantitative evaluation** and a threshold its own authors call heuristic and uncalibrated.

Exactly **one** research programme turns the surrounding apparatus into a modelling discipline rather than a metaphor: Manuel DeLanda's parametrized assemblage theory, taken up by F. LeRon Shults for multi-agent modelling. It yields named dials, not a formalism.

**Everything else found is interpretive** — it reads existing systems (swarms, hypertext, the web, code, protocol) through Deleuze rather than deriving anything from him. That is not worthless, but it is not prior art for building something.

One clean negative worth stating up front: the obvious hypothesis that someone built a "rhizomatic" knowledge store in the semantic-web lineage is **false as searched**. The one system literally named *Rhizome* (Souzis's Rx4RDF/Rhizome semantic wiki, IEEE Intelligent Systems 2005) does not cite Deleuze, the rhizome, or any Deleuzian concept. The name is the whole connection.

---

## 1. The prior art that exists

Sourced description of what each work claimed. Verdicts are held separately in §2.

### 1.1 Operational — a running system

**Serrano, J.C., Kevari, J. & Narayan, R. (2026), "A Multi-Agent Rhizomatic Pipeline for Non-Linear Literature Analysis," arXiv:2603.28336 (cs.AI), 31 March 2026.** University of Vaasa / LUT University.

The most operational item found, and the only one that is both recent and directly about agents plus a knowledge graph. It builds the "Rhizomatic Research Agent (V3)": twelve agents across a seven-phase pipeline, explicitly mapping each of the rhizome's six principles (connection, heterogeneity, multiplicity, asignifying rupture, cartography, decalcomania) onto a pipeline phase. It automates a manual rhizomatic literature method from Narayan's 2023 dissertation on energy system transitions. Concretely:

- **Rupture Protocol.** Monitors "centralization risk" in the emerging knowledge graph. Per the paper, when "a small number of nodes accumulate disproportionate edge density (>40%), the system triggers a 're-entry from the outside,' automatically fetching and integrating literature from heterodox traditions." This is their operationalization of *asignifying rupture*.
- **Three-way edge typology.** Inter-paper relations are classified as **constructive** (extensions, borrowed methods), **critical** (contradictions, challenges), or **rhizomatic** (paradigm ruptures introducing heterodox perspectives) — rendered as solid, dashed, and neon edges.
- **Semantic topography.** SciBERT embeddings → UMAP → HDBSCAN, used to detect semantic clusters, **semantic voids** (gaps), **orthogonal isolations** (separate semantic spaces sharing terminology), and a **marginalization index** (distance from corpus centroid).
- **Assemblage Builder.** Synthesizes findings written in the present-continuous tense "to reflect the ongoing nature of the phenomena under study."

Honesty of the source: **no quantitative evaluation, no baseline, no gold-standard dataset.** Three "preliminary observations" only, from unspecified deployments (e.g. the Rupture Protocol fires in "approximately 30–40% of analyses"). The authors state the 40% threshold is "heuristically set and requires empirical calibration," and that the observations "require systematic validation." Tested only on one domain (energy–information nexus), on metadata and abstracts rather than full text.

### 1.2 Operational-adjacent — a modelling discipline

**Manuel DeLanda**, *A New Philosophy of Society* (2006), *Philosophy and Simulation: The Emergence of Synthetic Reason* (2011), *Assemblage Theory* (2016); earlier "Virtual Environments and the Emergence of Synthetic Reason" (1998, in *Virtual Futures*), which engages artificial life and genetic algorithms directly.

DeLanda is the formalizing descendant and, as the brief anticipated, the best bridge to anything implementable. The load-bearing moves:

- **Relations of exteriority** — a component's identity does not depend on the whole it currently belongs to; it can be detached and plugged into another assemblage.
- **Properties vs capacities** — what a thing *is* versus what it can *do* when coupled to something else; capacities are open-ended and only actualized in interaction.
- **Parametrization.** DeLanda's own methodological claim, per the summaries retrieved: dichotomies in assemblage theory are replaced with "a single parametrized term capable of existing in different states — a concept with knobs that can be set to different values." Transformations are modelled by setting an assemblage's parameters, "a task that is greatly simplified if an assemblage's components have parameters of their own."

The two canonical knobs are **territorialization/deterritorialization** (how tightly components are bound together, spatially and by homogenization) and **coding/decoding** (how far membership and role are fixed by explicit rule versus left open).

**F. LeRon Shults (2022), "Progress in simulating human geography: Assemblage theory and the practice of multi-agent artificial intelligence modeling," *Progress in Human Geography*, doi:10.1177/03091325211059567.**

Argues that geographers embraced assemblage theory and computational simulation in the same period with almost no contact between the two, and that "more explicitly integrating assemblage theory and computer modeling can encourage a more robust philosophical understanding of both." The retrieved passages identify the operational hooks as exactly DeLanda's two axes — "the degree of territorialisation and deterritorialization; and the degree of coding and decoding" — and read **relations of exteriority** as the reason an agent-based model works at all: "Because the component parts of the computational architecture are characterized by 'relations of exteriority,' the programmed rules of interaction at a micro-level (e.g., agent attitudes and behaviors) can under the right conditions lead to the emergence of new macro-level wholes with qualities irreducible to the component parts."

**Confidence caveat, stated plainly:** the SagePub full text and PDF both returned HTTP 403 to this excursion, as did the ResearchGate copy and the De Gruyter PDF of Shults' related 2019 *Open Philosophy* article. The characterization above rests on the publisher abstract, the author's own blog summary, and quoted snippets surfaced in search — not on a full read. Treat the parameter attribution as well-supported but not personally verified.

Shults' group does build real models (the Artificial Society Analytics Platform; agent-based work with Wildman, Diallo and Puga-Gonzalez in *JASSS* and on minority integration in a Western city), so the programme is not vapour — but the 2022 article itself is a programmatic review arguing for a connection, not a paper presenting an assemblage-derived model.

### 1.3 Interpretive — reads systems through Deleuze

**Baron, A.M. (2026), "Representation and Interpretation of Multi-Agent Systems through Deleuzian Thought," *Journal of Computational Design* 7(1), doi:10.53710/jcode.1839208.** Builds animated swarm simulations in Processing/Java and analyzes flocking behaviour through machine, assemblage, rhizome and flow, concluding that agents can incorporate the philosophical concepts "within their working mechanisms." Computationally grounded but interpretive: it reads existing flocking algorithms as Deleuzian; it does not derive a new rule, metric, or architecture.

**Robinson, L. & Maguire, M. (2010), "The rhizome and the tree: changing metaphors for information organisation," *Journal of Documentation* 66(4), 604–613.** Reviews the rhizome as a model for information organisation. Concludes it "is a promising model for understanding hyperlinked information" and "may be of practical value, particularly if it can be integrated with more traditional forms" — then explicitly stops: "More research, conceptual and practical, is needed before this can be achieved." No operational proposal; the recommended next step is hybridization with established classification.

**Tredinnick, L. (2013), "Each One of us was Several: Networks, Rhizomes and Web Organisms," *Knowledge Organization* 40(6), 414–;** and **Tredinnick (2023), "The intricate web: network and rhizome metaphors in hypertext and the web and the epistemic challenge of fake news," *Journal of Documentation* 79(6), 1485–.** The sustained LIS engagement with the rhizome. Both are metaphor analyses — the 2023 piece explicitly treats network *and* rhizome as competing **metaphors** and asks what each hides. (Full texts not retrieved; the imrpress PDF redirected and was not followed within budget.)

**Galloway, A.R. (2004), *Protocol: How Control Exists After Decentralization*, MIT Press.** The most influential Deleuze-in-networks work. Takes "Postscript on the Societies of Control" and argues protocol is to control societies what the panopticon was to disciplinary societies: distributed networks with "no hubs" are not therefore free, and the protocols organizing them produce "the most highly controlled mass media hitherto known." Diagnostic, not constructive — it explains how control operates in an architecture, it does not tell you how to build one.

**Berry, D.M. & Pawlik, J. (2005), "What is code? A conversation with Deleuze, Guattari and code," *n.paradoxa* vol. 2.** Reads code through machine/assemblage, flow, deterritorialization, rhizome, and smooth/striated space. Representative line: "Code is production and as such is a machine. Every piece of code has components and is defined by them." Purely interpretive; asks who controls code and what its revolutionary potential is, and offers no design methodology.

**Cormier, D. (2008), "Rhizomatic Education: Community as Curriculum," *Innovate: Journal of Online Education* 4(5).** "The community is the curriculum." Proposes knowledge as negotiated by a community rather than validated against a canon, apt for "disciplines on the bleeding edge where the canon is fluid." A pedagogical stance, deliberately, with no mechanism.

**Guattari, "Machinic Heterogenesis" (in *Chaosmosis*, 1992).** The most developed statement of machines as a general category spanning technical, social, semiotic and axiological registers, including a direct engagement with Varela's autopoiesis — Guattari's complaint being that organizational closure lacks evolutionary and cognitive openness. Relevant because it is the closest the primary literature comes to a systems-theoretic statement, and it stays philosophical.

### 1.4 The adjacent tradition the brief asked about: ANT

**Müller, M. & Schurr, C. (2016), "Assemblage thinking and actor-network theory: conjunctions, disjunctions, cross-fertilisations," *Transactions of the Institute of British Geographers*, doi:10.1111/tran.12117.**

The direct answer to "say clearly where ANT is doing the work Deleuze is being credited for." The retrieved findings:

- John Law, an ANT founder, holds there is "little difference between Deleuze's *agencement* (awkwardly translated as 'assemblage' in English) and the term 'actor-network'." Latour compares the actor-network to the rhizome and endorses D&G's "very special brand of active and distributed materialism … to which we [ANT scholars] have always referred."
- Both traditions share a relational ontology (action results from linking initially disparate elements), emergence, and a topological view of space where distance is a function of relational intensity.
- But Müller & Schurr argue they are better treated as separate theoretical entities, and Graham Harman argues "Deleuze and Latour pursue irreconcilable projects." The ANT version "appears to have narrowed down the range of meanings found in Deleuze."

**This excursion's read:** in nearly all applied tech writing, the work being done is the *relational* claim — entities are constituted by their connections, wholes have capacities their parts lack. ANT says that plainly. So does graph theory. Deleuze is being credited for a claim that two plainer vocabularies already own.

### 1.5 Simondon — the direct-influence branch, and the surprise

The brief listed Simondon as background. He turned out to carry the single most usable design concept in the whole starting list, and it is **not** Deleuze's.

**Concretization**: technical objects mature through "the progressive convergence of separate functional structural units so that this convergence draws them into a single unit of operation which enhances their overall operation." A primitive (abstract) technical object has one part per function; a concretized one has parts that serve several functions at once, and it generates its own **associated milieu** — the local environment its operation both creates and depends on.

Applications found: Simon Mills, *Concrete Software: Simondon's mechanology and the techno-social* (proposes applying concretization to software studies, contrasting it with "hylomorphic and reductionist views of technical objects currently common in computer science"); "On the individuation of complex computational models: Gilbert Simondon and the technicity of AI," *AI & Society* (2024), doi:10.1007/s00146-024-02152-2; and a piece on concretization in cybersecurity in *Matter: Journal of New Materialist Research*.

These remain philosophy-of-technology papers. None presents a metric or a method. But concretization is at least a **criterion with a direction** — it says what a more mature technical object looks like — which is more than the Deleuzian vocabulary offers.

### 1.6 The self-criticism from inside the tradition

**Alexander Galloway** taxonomizes contemporary Deleuzianism and names the failure mode this excursion was asked to look for. His **"Google Deleuzians"** align Deleuze with Silicon Valley's data-driven vision, treating everything as interconnected networks and thereby "reinforcing market logic rather than challenging it." He is interested in how the rhizome *prefigures* the digitally-coordinated networks of exploitation behind Apple, Amazon and Google — i.e. that the emancipatory reading of the rhizome-as-network was, in practice, a description of platform capitalism. He links this to **"reticular pessimism"**: the belief that critique can only operate within networked systems, which confines resistance to the structures it opposes.

Also relevant: the information-systems field's own complaint that this family of concepts resists operationalization. Sociomateriality research reports that "operationalizing sociomateriality into a coherent analysis was deemed as demanding" and that examples "are too general, making it difficult to identify and understand the phenomenon" — with a 2021 paper proposing assemblage theory as the *fix*. Read that carefully: the field trying to use these concepts empirically says they are hard to use empirically.

### 1.7 Clean negatives

- **Souzis, A., "Building a Semantic Wiki," *IEEE Intelligent Systems* 20(5) (2005); Rx4RDF / Rhizome, SourceForge, 2004–2006.** Fetched and checked directly: the paper **does not cite Deleuze, the rhizome, or any Deleuzian concept.** Rhizome is an RDF content-management stack (RxPath, Raccoon app server, RhizML). If you were hoping a Deleuze-derived knowledge store already exists in the semantic-web lineage, it does not — at least not this one.
- **Swarm robotics / self-organizing MAS.** Searched for Deleuzian concepts (lines of flight, deterritorialization) applied in that literature. Nothing found. The swarm and self-organization papers do not cite Deleuze; the Deleuze papers on those concepts stay in politics and philosophy. Baron 2026 (§1.3) is the exception and it runs the other direction — philosophy reading swarms, not swarms using philosophy.
- **Deleuze applied to dataflow / stream processing / read-write boundaries.** Nothing found. See §4.2.

---

## 2. Load-bearing vs decorative — verdict per item

The test applied: **does the concept do work a plainer vocabulary could not do?** Plainer candidates on hand: graphs, degree distribution, emergence, modularity, dataflow, self-organization, ANT, schema-strictness, cohesion.

| Work | Verdict | Why |
|---|---|---|
| Serrano, Kevari & Narayan 2026 (Rupture Protocol) | **Load-bearing, weakly** | The mechanism — a negative feedback loop that fights hub formation in your own graph — is not something graph vocabulary suggests on its own. Graph theory *measures* centralization; nothing in it says "and therefore go fetch the opposite." The philosophy supplied the normative move. But the implementation is one unvalidated threshold, and everything else in the pipeline (SciBERT/UMAP/HDBSCAN, dedup by trigram Dice) is standard practice wearing a Deleuzian label. |
| DeLanda's parametrization | **Load-bearing** | Turning a dichotomy into a dial you can set is a real methodological instruction, and it is DeLanda's, not a relabeling. Whether the *specific* dials matter is separate (see below). |
| DeLanda's relations of exteriority | **Load-bearing** | It states a falsifiable structural constraint: component identity must not depend on the containing whole. "Modularity" gestures at this; relations of exteriority states it as an ontological requirement with a consequence (detachability). Closest thing in the corpus to a checkable invariant. |
| DeLanda's properties vs capacities | **Marginal** | A useful distinction, but "what it is vs what it affords" is well covered by affordance vocabulary and by interface-vs-implementation. |
| Shults 2022 | **Load-bearing as a bridge, not as a result** | It correctly identifies where the two literatures touch and names the hooks. It does not deliver a model, so its contribution is orientation. |
| Territorialization / coding as the two axes | **Mostly decorative — but see the one exception** | Territorialization ≈ cohesion/coupling. Coding ≈ schema-strictness or rule-governedness. Both are plainly nameable. The non-redundant part is that they are **independent**: a region can be tightly bound yet weakly coded (a dense cluster with no schema), or loosely bound yet strictly coded (a sparse set under a rigid rule). That 2×2 is not something "cohesion" alone gives you. |
| Baron 2026 | **Decorative** | Flocking was described adequately by Reynolds' boid rules in 1987. Relabelling separation/alignment/cohesion as machine/assemblage/flow adds vocabulary, not predictive or design content. The paper's own conclusion — that agents can "incorporate" the concepts — is a restatement of the reading, not a finding. |
| Robinson & Maguire 2010 | **Decorative by their own account** | They present it as metaphor and say practical value awaits research not yet done. Sixteen years later, this excursion found no follow-up that did it. |
| Tredinnick 2013 / 2023 | **Decorative, deliberately and usefully so** | These are explicitly analyses *of metaphors*. Treating "rhizome" as a metaphor whose costs can be examined is honest scholarship; it just is not a design input. |
| Cormier 2008 | **Decorative** | "The community is the curriculum" is a valuable pedagogical commitment, and it does not need Deleuze — connectivism, communities of practice, and constructivism reach it independently. The rhizome supplies the poster, not the argument. |
| Galloway, *Protocol* | **Load-bearing for critique, useless for construction** | The claim that decentralized architecture is compatible with intensified control is a genuine insight that the network vocabulary of its moment actively obscured. It tells you nothing about how to build a memory graph. |
| Berry & Pawlik 2005 | **Decorative** | "Code is production and as such is a machine" is a reading. No consequence follows for how code is written. |
| Guattari, "Machinic Heterogenesis" | **Load-bearing philosophically, not transferable** | The critique of autopoiesis for lacking evolutionary and cognitive openness is a real argument against a real position. It does not descend to mechanism. |
| ANT (Law, Latour) vs Deleuze | **ANT is doing most of the work Deleuze gets credited for** | On the shared claims — relationality, emergence, symmetric treatment of human and non-human components — ANT is the plainer and more empirically disciplined statement. Where they genuinely diverge (Harman: "irreconcilable projects"), the divergence is metaphysical, not methodological, so it does not reach a system design. |
| Simondon's concretization | **Load-bearing, and underused** | It names a directional quality criterion — convergence of separate functional units into multi-functional ones, plus an associated milieu — that neither modularity nor cohesion captures, because both of those push the *opposite* way (one function per part). That tension is real and interesting. Nobody found has operationalized it. |
| Souzis's Rhizome | **Not prior art at all** | Verified: no Deleuze content. |

**Aggregate verdict.** Deleuze's *machines* specifically — the *Anti-Oedipus* apparatus of desiring-machines and flow-interruption — produced **no** operational prior art in anything searched. What operational content exists comes from (a) the *rhizome* principles, once someone was willing to turn one of them into a threshold, and (b) DeLanda's post-Deleuzian assemblage parameters. If you are looking for the piece of this tradition most likely to pay off, it is DeLanda, exactly as the brief guessed — and Simondon is a live second.

---

## 3. Transferable ideas

Five, in plain operational terms, each with a mechanizability read and an honest note where it restates something the project already has.

### 3.1 Run a centralization guard against the graph's own shape

**Plain statement.** Continuously measure how concentrated edge mass is on a few nodes. When concentration crosses a bound, deliberately act against it — pull in or surface material from the sparsest regions.

**Source.** Serrano et al. 2026's Rupture Protocol, their operationalization of asignifying rupture.

**Mechanizability: high.** Degree distribution, a Gini coefficient over node degree, or share-of-edges-held-by-top-k are all cheap to compute over an existing graph and cheap to recompute incrementally.

**What it maps onto here.** The background crawler is the natural host — this is a periodic measurement, not a read-path cost. It is *not* a restatement of spreading activation; spreading activation follows the graph's existing shape, and this pushes back on it.

**The actual delta.** Nothing in the project currently exerts pressure *against* hub formation. A memory graph that gets used will concentrate: heavily-referenced nodes attract more edges, and preferential attachment is self-reinforcing. This is the one idea in the corpus that treats that as a defect to be counteracted rather than a signal to be exploited.

**Borrow the mechanism, not the number.** Their >40% is admitted by its own authors to be heuristic and uncalibrated, and it fires in 30–40% of their runs, which is a suspiciously high rate for something framed as an exceptional intervention. Whatever bound gets used here needs its own unit and its own justification.

### 3.2 Detect orthogonal isolation — same words, disconnected regions

**Plain statement.** Find clusters that share terminology but have no path between them. Distinguish that from a genuine semantic void (a region with nothing in it at all).

**Source.** Serrano et al.'s semantic topography phase: SciBERT → UMAP → HDBSCAN, yielding semantic clusters, semantic voids, orthogonal isolations, and a marginalization index (distance from corpus centroid).

**Mechanizability: high** if embeddings are already present; the clustering stack is off-the-shelf.

**What it maps onto here.** Partly a restatement — clustering and near-duplicate detection are standard, and "marginalization index" is distance-to-centroid with a costume on. **Orthogonal isolation is the part that is not a restatement**, and it is directly relevant to a *cross-project* memory: two projects independently coining the same term for different things, or the same concept under two names in unconnected subgraphs, is exactly the failure mode a shared graph invites. It is a link-suggestion signal and a collision detector at once.

### 3.3 Annotate regions with two independent dials: bindedness and coding

**Plain statement.** For a subgraph, record two separate scalars — how tightly its members are bound to each other, and how far its membership is governed by explicit rule versus emergent from use.

**Source.** DeLanda's territorialization/deterritorialization and coding/decoding axes; identified by Shults as the operational hooks for modelling.

**Mechanizability: medium.** Bindedness is computable (internal vs external edge ratio, clustering coefficient). Coding is not directly measurable — it is closer to a curatorial annotation: was this region defined by a schema, or did it accrete?

**What it maps onto here.** Largely a restatement. Bindedness ≈ cohesion; coding ≈ schema-strictness, which typed edges and facets already partly express.

**The delta, and it is narrow.** The two are *independent*, and the project's current vocabulary tends to conflate them. A dense uncoded cluster (much used, never schematized) and a sparse strictly-coded set (schematized, barely used) are different situations calling for different treatment, and "this region is well-structured" does not distinguish them. Worth knowing as a 2×2, not worth importing the words.

### 3.4 Make relations of exteriority a testable invariant on project-owned graphs

**Plain statement.** A memory node's meaning must not depend on the graph it currently sits in. Test it by export: take a node out of its project's graph, hand it to another project, and check whether it is still interpretable standalone.

**Source.** DeLanda's relations of exteriority — a component's identity is independent of the whole it belongs to, hence it can be detached and plugged elsewhere. Shults reads this as the precondition for micro-rules producing irreducible macro-wholes.

**Mechanizability: high, and unusually so** — this is the only place in the surveyed corpus where the philosophy states something a test can fail. It becomes a lint rule: a node whose content only resolves via context stored on its edges (unresolved pronouns, bare "this approach," project-local abbreviations, references to a container) violates the invariant.

**What it maps onto here.** Directly onto the cross-project sharing goal, which is the whole point of the design. If nodes are not exterior in this sense, cross-project reuse degrades to noise the moment a node leaves home.

**Note the tension worth surfacing.** This pulls against §3.2's orthogonal-isolation work and against context-rich nodes generally. Exteriority buys portability at the cost of self-containment overhead per node. That is a real trade, not a free win.

### 3.5 Give edges a type that means "this disagrees"

**Plain statement.** Alongside edges that mean *extends* or *derives from*, carry a type meaning *contradicts, breaks with, or does not fit*. Let traversal be told to prefer disagreement.

**Source.** Serrano et al.'s constructive / critical / rhizomatic typology, where the third type marks a break with the local paradigm rather than an extension of it.

**Mechanizability: high** — it is a type value, plus a traversal preference.

**What it maps onto here.** Typed edges already exist, so the schema cost is nil. **The delta is the traversal policy, not the type.** A retrieval that can be asked for the strongest available objection to what it just found behaves differently from one that always walks toward reinforcement — and the read-time dial is the obvious place to expose that. Note the honest caveat: nothing in the source validates that this improves anything; the three-way split is asserted, not measured.

**A sixth, flagged rather than numbered** — **Simondon's concretization as a maturity criterion**: a technical object matures when separate single-purpose parts converge into parts serving several functions at once. Applied to a memory graph, that would say maturity looks like *one* structure carrying several functions rather than a new mechanism per need. This is genuinely non-obvious and it cuts directly against the usual one-concern-per-component instinct — which is exactly why it should not be adopted without argument. No operational application of it was found in the literature; it is offered as a live question, not a transferable idea.

---

## 4. The two specific mappings the brief flagged

### 4.1 Smooth vs striated space → free traversal vs structured query

**Partially supported as framing. Null as mechanism.**

The literature does make this mapping, repeatedly, at metaphor level. Sian Bayne, "Smoothness and Striation in Digital Learning Spaces," *E-Learning* 1(2) (2004), applies it to digital learning environments. Web-design and hypertext writing distinguishes "surfing" (fluid, plan-oriented, unbounded) from "cruising the information superhighway" (linear, point-oriented, Cartesian), and reads the web's topography as closer to the sea than the highway. The standard gloss — striated space confines movement to preset paths between fixed points, smooth space lets you rise up at any point and move to any other — describes structured query versus free traversal almost too neatly.

**Why this excursion still calls it null as a mechanism:** no source found operationalizes it. Nobody ties it to a query language, an index structure, a retrieval mode, or a cost model. It renames a distinction the project already has and can already state precisely.

**The one thing in it worth keeping** is the part usually dropped. D&G's actual claim is that the two are *not* a binary — smooth space is continually striated and striation continually smoothed, and the interesting object is the conversion between them, not either pole. There is even a specific line: to navigate a smooth space *is to begin striating it*. Read against this project, that says the read-time dial is the D&G-faithful object and the two endpoints are not, and it warns that free traversal *generates* structure as a side effect of being used — which is the same phenomenon §3.1 wants to guard against, arriving from a different direction. That convergence is mildly reassuring. It is not evidence.

### 4.2 Machine-as-flow-interruption → the agent's read/write boundary

**Null. No prior art found.**

Searched specifically for the *Anti-Oedipus* definition — a machine as "a system of interruptions or breaks," every machine coupled to another whose flow it cuts, with the break itself productive because a disconnection simultaneously creates a new connection — applied to dataflow, stream processing, pipelines, or read/write boundaries. Nothing. The closest is Berry & Pawlik 2005 ("Code is production and as such is a machine. Every piece of code has components and is defined by them"), which stays entirely interpretive and draws no consequence for how anything is built.

**Scoped null, stated per the brief:** no operational prior art connecting flow-interruption to system read/write boundaries was found in web-accessible philosophy of technology, software studies, or the MAS literature reachable this pass. This does not kill the idea that the framing could be useful. It does mean there is nobody to cite, and it means anyone using it here would be doing original work, not applying prior art.

**One flag anyway.** Even granting the framing, "a component defined by what it cuts out of a stream, where the cut is itself productive" is close to what pipeline, filter, and backpressure vocabulary already say plainly and precisely. Judged against the brief's own test, it is likely decorative here too.

---

## 5. What was and was not searched

**Searched** (web + academic, this pass): assemblage theory × multi-agent systems; DeLanda × computational modelling; rhizome × knowledge organization and classification (LIS); rhizome × knowledge graphs and agent memory; desiring-machines / machinic × software studies; Deleuze × LLM agents and agentic AI (2025–2026); smooth/striated × interfaces, hypertext, information retrieval; rhizomatic learning; Simondon × software and AI; ANT versus assemblage; Deleuze × swarm robotics and self-organizing MAS; flow-interruption × dataflow; sociomateriality and operationalization critiques; Galloway and the internal critique of decorative Deleuzianism.

**Retrieved in full:** the Serrano et al. arXiv paper; the Baron *JCoDe* article page; the Souzis IEEE paper (checked directly for Deleuze content — negative); the Robinson & Maguire abstract; the Berry & Pawlik article; the Shults blog summary.

**Not retrieved — paywalled or blocked (HTTP 403/405) and read only via abstract or quoted snippet:** Shults 2022 in *Progress in Human Geography* (three separate routes blocked); Shults 2019 in *Open Philosophy*; "Simulating Machines: Modelling, Metaphysics and the Mechanosphere," *Deleuze and Guattari Studies* (2020); Müller & Schurr 2016; the *Futures* paper "The net effect: Design, the rhizome, and complex philosophy"; Tredinnick 2013 and 2023 full texts.

**Not searched at all:** ACM DL, IEEE Xplore, DBLP, and AAMAS proceedings queried directly rather than through general web search; Deleuze studies journals surveyed systematically; non-English literature (notably French — *agencement* scholarship is substantially French-language, and the English "assemblage" is a known bad translation, so the French-language search space is a real gap); patents; theses beyond the two surfaced incidentally; anything behind institutional access.

**Scoped nulls, explicitly:**
- No operational prior art found applying flow-interruption to read/write or dataflow boundaries, in the literature searched above.
- No Deleuze-derived system found in the semantic-web / RDF / knowledge-graph engineering lineage. The one candidate by name was checked and is negative.
- No Deleuze-citing work found in the swarm robotics or self-organizing MAS engineering literature.
- No quantitative evaluation found for *any* Deleuze-derived mechanism, anywhere in this pass. The single implemented system reports three preliminary observations and no baseline.

Each of these kills its specific search under these conditions. None kills the idea that the concepts could be useful here.

---

## Sources

- [Serrano, Kevari & Narayan (2026), A Multi-Agent Rhizomatic Pipeline for Non-Linear Literature Analysis, arXiv:2603.28336](https://arxiv.org/abs/2603.28336)
- [Shults (2022), Progress in simulating human geography, Progress in Human Geography](https://journals.sagepub.com/doi/full/10.1177/03091325211059567)
- [Shults, author summary of the above](https://leronshultsblog.com/2021/12/20/new-article-published-in-progress-in-human-geography-on-assemblage-theory-and-computer-modeling/)
- [Baron (2026), Representation and Interpretation of Multi-Agent Systems through Deleuzian Thought, Journal of Computational Design 7(1)](https://dergipark.org.tr/en/pub/jcode/article/1839208)
- [DeLanda, Assemblage Theory (2016), publisher's introduction PDF](https://edinburghuniversitypress.com/media/resources/9781474413640_Assemblage_Theory_-_Introduction.pdf)
- [Robinson & Maguire (2010), The rhizome and the tree, Journal of Documentation 66(4)](https://www.emerald.com/jd/article/66/4/604/205729)
- [Tredinnick (2013), Each One of us was Several: Networks, Rhizomes and Web Organisms, Knowledge Organization 40(6)](https://www.researchgate.net/publication/289742439_Each_One_of_us_was_Several_Networks_Rhizomes_and_Web_Organisms)
- [Tredinnick (2023), The intricate web, Journal of Documentation 79(6)](https://www.emerald.com/jd/article-abstract/79/6/1485/207206/The-intricate-web-network-and-rhizome-metaphors-in)
- [Müller & Schurr (2016), Assemblage thinking and actor-network theory, Transactions of the IBG](https://rgs-ibg.onlinelibrary.wiley.com/doi/full/10.1111/tran.12117)
- [Galloway (2004), Protocol: How Control Exists After Decentralization, MIT Press — full text PDF](http://www.asounder.org/resources/galloway_protocol.pdf)
- [Galloway on "Google Deleuzians" and reticular pessimism (b2o interview)](https://www.boundary2.org/2016/06/ending-the-world-as-we-know-it-an-interview-with-andrew-culp/)
- [Berry & Pawlik (2005), What is code? A conversation with Deleuze, Guattari and code](https://intertheory.org/berry.htm)
- [Cormier (2008), Rhizomatic Education: Community as Curriculum, Innovate 4(5)](https://nsuworks.nova.edu/innovate/vol4/iss5/2/)
- [Guattari, Chaosmosis, ch. 2 "Machinic Heterogenesis" (PDF)](https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/8/644/files/2017/08/felix-guattari-chaosmosis-Chapter-2-SF-copy-13yby1i.pdf)
- [Mills, Concrete Software: Simondon's mechanology and the techno-social](https://philpapers.org/rec/MILCSS-4)
- [On the individuation of complex computational models: Gilbert Simondon and the technicity of AI, AI & Society (2024)](https://link.springer.com/article/10.1007/s00146-024-02152-2)
- [Bayne (2004), Smoothness and Striation in Digital Learning Spaces, E-Learning 1(2)](https://journals.sagepub.com/doi/10.2304/elea.2004.1.2.6)
- [Pass, E-Pedagogy: Deleuze and Guattari in the Web-Design Class (Kairos 6.2) — smooth/striated cyberspace](https://kairos.technorhetoric.net/6.2/coverweb/de/pass/index2.htm)
- [Souzis, Building a Semantic Wiki, IEEE Intelligent Systems 20(5) — checked, no Deleuze content](https://www.onecommons.org/rhizome/IEEE_IS_Souzis_v20n5.pdf)
- [The Sociomateriality Debate Revisited: The Contribution of Assemblage Theory (2021)](https://www.researchgate.net/publication/354477991_The_Sociomateriality_Debate_Revisited_The_Contribution_of_Assemblage_Theory)
- [Simulating Machines: Modelling, Metaphysics and the Mechanosphere, Deleuze and Guattari Studies (2020)](https://www.euppublishing.com/doi/10.3366/dlgs.2020.0408)
