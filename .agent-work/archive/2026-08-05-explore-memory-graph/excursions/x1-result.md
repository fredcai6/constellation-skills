# Excursion Result x1: Organizing forms beyond the graph

**Session:** `explore-memory-graph`, cycle 2 (shotgun), excursion x1 — research
**Question:** What ways and tools have people used to organize large bodies of diverse, interconnected thoughts, and do any of them rest on a form that is genuinely NOT a graph (or that a plain node-and-edge graph fails to capture)?
**Budget:** one focused research pass (seven search batches, web + prior knowledge). Breadth over depth, as briefed.

---

## Headline verdict

**Almost every form below can be *encoded* as a graph. Almost none of them are *well served* by one.** That distinction is the whole finding, so state it precisely before the survey:

A graph is expressively universal in the same uninteresting way a Turing machine is. Any of these structures can be flattened into nodes and edges, usually by reifying whatever the graph lacks (turn a facet into an edge type, a position into a coordinate property, an n-ary fact into a blank node). The question that matters for a memory design is not *"can it be encoded?"* but **"what does the encoding make expensive, and what invariant does it stop enforcing?"** Every entry below therefore answers three things: what the form is, what the graph reduction *loses* (not whether it's possible), and the one idea worth stealing or explicitly declining.

Three losses recur across the whole survey and are worth naming up front, because they are the real content of "not a graph":

1. **Loss of enforced independence.** Facets, dimensions, and lattice axes come with a guarantee that axes are orthogonal and freely combinable. Encoded as edge types, that guarantee evaporates — nothing stops edge type A from implying edge type B, and nothing tells you which combinations are legal.
2. **Loss of the un-named relation.** Spatial layouts, similarity distance, and adjacency carry relational information *without* committing to what the relation means. A graph demands you name an edge to have one at all, which forces premature commitment and silently discards everything the author wasn't ready to name.
3. **Loss of the computed relation.** In several forms the connection does not exist in storage; it is evaluated at read time against the reader's state, the query, or the clock. A stored edge is a different object from a predicate over a context.

---

## The survey

### 1. Hierarchy / outline
*Canonical: Engelbart's NLS/Augment; Dewey Decimal; filesystems; Workflowy, org-mode.*

Documents in NLS were always structured as a tree, with every statement given a positional identifier (`1`, `1a`, `1a2b`) and a rich set of **view-control** commands to display the outline to a chosen depth ([mprove, Vision and Reality of Hypertext](https://mprove.de/visionreality/text/3.1.3_nlsaugment.html)). The tree is not the interesting part; the *view control* is — the same structure rendered at many depths on demand.

- **Graph verdict:** Reduces (a tree is a graph). Lost: the **single-parent discipline** and the resulting guarantee that "collapse this subtree" is well defined. In a general graph there is no such thing as "the outline of this region to depth 2," because there's no canonical parent and no total order among siblings. Sibling *order* is the quietest casualty — trees carry it for free, graphs need an explicit index property.
- **Steal:** view control — one structure, many depths, summarization as a *view* rather than a stored artifact.
- **Decline:** single-parent-ness as a global constraint.

### 2. Faceted classification
*Canonical: S. R. Ranganathan's Colon Classification (1933), PMEST — Personality, Matter, Energy, Space, Time.*

Ranganathan's system is **analytico-synthetic**: rather than assigning each document one fixed slot in a large hierarchy (as Dewey and LCC do), it analyses a subject into independent facets and *synthesizes* a class number by combining them ([Wikipedia, Faceted classification](https://en.wikipedia.org/wiki/Faceted_classification); [Broughton, "Faceted classification as the basis of all information retrieval"](https://discovery.ucl.ac.uk/10038742/3/Broughton_final_Faceted%20classification.pdf)). Facets may each be internally hierarchical; the point is that the *combination* is not pre-enumerated ([Hedden Information Management](https://www.hedden-information.com/faceted-classification-and-faceted-taxonomies/)).

- **Graph verdict:** Reduces, badly. Lost: **orthogonality as an enforced invariant.** Facets promise that any legal combination of values across axes names a real, findable class — this is what makes faceted search's "narrow by any dimension in any order" work. Model facets as edge types and the promise is gone: you can no longer tell which edges are axes and which are just relations, nor which combinations are meaningful.
- **Steal:** the distinction between *analysis* (decompose into independent axes) and *synthesis* (recombine on demand). This is the single strongest challenger to "everything is an edge."

### 3. Spatial hypertext
*Canonical: Marshall & Shipman's VIKI (1994) and VKB; descendants include Muse, Kinopio, tldraw, Miro, Obsidian Canvas.*

The founding observation is a failure report: given Aquanet, a system for explicit typed links, authors **stopped making links** and instead arranged material in space so that proximity, alignment, and colour implied the relationships. VIKI was built to support that implicit structure directly, with a "spatial parser" that recognizes emergent visual groupings ([Shipman & Marshall, VIKI abstract](https://people.engr.tamu.edu/shipman/abstracts/echt94-abstract.html); [Shipman, "Seven Directions for Spatial Hypertext Research"](https://people.engr.tamu.edu/shipman/SpatialHypertext/SH1/shipman.pdf)). Spatial hypertext's claimed advantage is that it "allows more ambiguous, implicit, and non-verbal expression than other hypermedia."

- **Graph verdict:** **Does not reduce cleanly.** You can store `(x, y)` as node properties, but then the *structure lives outside the graph* — it is in the geometry, and the graph engine can't traverse it. Lost: (a) the ability to express a relation you have not named, (b) *degree* of relatedness as continuous rather than present/absent, (c) the fact that moving one item re-relates it to everything nearby at once, without editing N edges.
- **Steal:** a tier of **provisional, unnamed association** below the typed-edge tier — a place to put "these belong together, I don't know why yet." The VIKI history is direct evidence that forcing authors to name relations up front makes them stop recording relations at all. That is the sharpest risk to a typed-weighted-graph memory design.

### 4. Method of loci / memory palace
*Canonical: classical rhetoric (Ad Herennium); Renaissance ars memoriae.*

Items are placed at ordered locations along a familiar route and recalled by mentally walking it. The organizing substrate is **a body's path through space**, not a topical structure. Note the etymological link to the next entry: *loci communes*, "commonplaces," is the same word ([Fabric, commonplace book guide](https://fabric.so/learn/commonplace-book)).

- **Graph verdict:** Reduces to a path graph, and that reduction is almost total — but it discards the thing that makes it work. Lost: the **exogenous scaffold.** Recall is powered by a structure the rememberer already knows (their house) which has *nothing to do with the content*. A graph derives structure from the content; the palace imports it.
- **Steal (speculative, cheap to test):** a stable, content-independent addressing scaffold that the agent knows cold, so that retrieval has a fixed frame even when content is unfamiliar. Compare Zettelkasten addresses (#6).

### 5. Commonplace book with Locke's index
*Canonical: Renaissance commonplacing; John Locke, "Méthode nouvelle de dresser des recueils" (1685).*

Readers excerpted passages into a notebook under thematic heads. Locke's contribution was purely an **addressing/indexing** innovation: a two-page expandable index keyed by first letter plus first vowel of the head-word, allowing entries to be written wherever there is space and still be found ([Public Domain Review](https://publicdomainreview.org/collection/john-lockes-method-for-common-place-books-1685/); [Walker, "Indexing commonplace books: John Locke's method," *The Indexer*](https://www.liverpooluniversitypress.co.uk/doi/pdf/10.3828/indexer.2001.22.3.2)). Darnton's reading is that commonplacers "broke texts into fragments and assembled them into new patterns" — the fragment, not the source document, is the unit.

- **Graph verdict:** Mostly reduces (heads are nodes, excerpts are leaves). Lost: **append-only physical economics.** Locke's index exists because pages are consumed in write order and cannot be reordered — a constraint that produced a decoupling of *write position* from *retrieval path* that is genuinely useful and that a graph, being freely reorganizable, never forces you to invent.
- **Steal:** atomicity of the excerpt, and the separation of where-it-was-written from how-it's-found.

### 6. Zettelkasten branching address
*Canonical: Niklas Luhmann's slip-box; the Folgezettel numbering `1`, `1a`, `1a1`, `21/3d2`.*

New notes are placed *behind* the note they continue, receiving a branching alphanumeric address. **Sources contradict each other on what the numbering is**, and the contradiction is instructive rather than resolvable:

- One reading: it is not a hierarchy at all but a pure coordinate — "merely the location of where the leaf lives on a branch… think of it more like a geographic coordinate system, like latitude and longitude" ([zettelkasten.de, Antinet introduction](https://zettelkasten.de/posts/introduction-antinet-zettelkasten/)), giving O(1) direct addressing like a hash table, so the address's job is lookup, not structure.
- The other reading: it plainly *is* a branching hierarchy of continuation, and it encodes "this note grew out of that one" — a claim about intellectual descent that the links alone don't carry.

Both readings agree there is "no privileged place" and the box grows without a preconceived scheme.

- **Graph verdict:** Reduces to a tree plus a link overlay. Lost: **immutable identity.** A Luhmann address, once assigned, never changes and never gets reused, so a citation from anywhere stays valid forever, and the address itself is a compressed statement of provenance. Graph node IDs are usually opaque and carry neither guarantee nor meaning.
- **Steal:** stable, human-legible, provenance-bearing identifiers assigned at write time and never mutated.

### 7. Wiki
*Canonical: Ward Cunningham's WikiWikiWeb (1995); Wikipedia.*

Links are made by *naming* — CamelCase words in the prose become links, so writing a name creates the connection and, if the page doesn't exist, an invitation to write it ([Wikipedia, WikiWikiWeb](https://en.wikipedia.org/wiki/WikiWikiWeb)). Structure is maintained by continuous **refactoring**: deleting, merging, splitting pages. Cunningham's own summary of the economics: "A wiki is always in the process of being organized, but for every hour spent organizing, two more hours are spent adding new material" ([Cunningham, "Exploring with Wiki," Artima](https://www.artima.com/articles/exploring-with-wiki)).

- **Graph verdict:** Reduces well — it genuinely is a graph — but the reduction loses the two things that make wikis work. Lost: (a) **prose is the edge.** The connective tissue is a sentence that says *how* things relate, in full natural language; a typed edge is a lossy compression of that sentence. (b) **The unresolved link as a work queue** — a red link is a first-class object meaning "this concept is needed and absent," which a graph of existing nodes has no natural slot for.
- **Steal:** the red link. A memory that can hold *named-but-absent* nodes has a built-in curiosity backlog.
- **Also steal:** the 1:2 maintenance-to-growth ratio as a sanity check. Organizing is not free and never finishes.

### 8. Trails
*Canonical: Vannevar Bush's Memex, "As We May Think" (1945); guided tours in 1990s hypertext.*

A trail is a **new linear sequence** built across an arbitrary set of documents, with the trail itself named, stored, recalled, and *given to another researcher* ([Wikipedia, Memex](https://en.wikipedia.org/wiki/Memex)). Multiple sources make the point that the Memex "is not considered to be hypertext" — Bush's unit is a persistent ordered path, not a point-to-point link between a phrase and a destination.

- **Graph verdict:** Reduces only if you reify. A trail is a *path made into an object*: it has a name, an author, an order, and it is the thing shared. Lost: **paths as first-class citizens.** In a plain graph, a path is something a query computes and throws away; nobody can annotate it, version it, or hand it to a colleague.
- **Steal:** trails as durable, nameable, shareable objects. For an agent memory, this is close to "how I reasoned to this conclusion, saved" — the reified reasoning path is exactly the artifact that a node-and-edge store keeps losing.

### 9. Sculptural hypertext / guard fields
*Canonical: Mark Bernstein, Eastgate's Storyspace; quality-based narrative (StoryNexus, Fallen London).*

Inverts the usual construction: "sculptural hypertext assumes that everything might be linked together; the writer adds constraints to **remove** connections" ([Emily Short, "Mark Bernstein on Hypertext Narrative"](https://emshort.blog/2016/04/28/mark-bernstein-on-hypertext-narrative/)). **Guard fields** are tests evaluated at read time that decide whether a given link is available *on this reading* — Storyspace has had them since the 1990s, and they are expressive enough to model finite state machines.

- **Graph verdict:** **Does not reduce.** The connection is not stored; it is a predicate evaluated against reader state. You could materialize the graph, but only per-state, and the state space is combinatorial.
- **Steal (strongest single idea in the survey for a retrieval system):** the default is *connected*, and authored knowledge is expressed as **constraints that suppress** rather than links that permit. For an agent memory this reframes the whole retrieval question: relevance is not "which edges exist from here" but "what is *not* excluded given the current task state." Guard fields are also the natural home for context-sensitivity — "recall this only when the agent is doing X" — which a static weighted edge cannot express.

### 10. ZigZag / zzstructure
*Canonical: Ted Nelson, "A Cosmology for a Different Computer Universe" (JoDI, 2004).*

Cells are connected along named **dimensions**; each cell has at most one neighbour in each direction along each dimension. Nelson describes it as "a multidimensional, non-hierarchical spreadsheet," built from cells and untyped connections grouped into dimensions ([Nelson, JoDI](https://journals.tdl.org/jodi/index.php/jodi/article/view/131/129)). Formalized set-theoretically, a zzstructure is a family of **disjoint sets of partial functions** — a dimension is a partial permutation of cells, not an arbitrary relation. Nelson's polemic against everything else is "intertwingularity": knowledge is not decomposable into hierarchies ([Wikipedia, Intertwingularity](https://en.wikipedia.org/wiki/Intertwingularity)).

- **Graph verdict:** It is a graph with a hard structural constraint (edge-coloured, degree ≤ 1 per colour per direction). Lost: **the constraint itself**, which is the whole design. Because each dimension is a partial function, "move rightward along dimension `d`" is always unambiguous — you can *navigate deterministically*. Drop the constraint and every step becomes a choice among N, which is why general graph browsing feels like drowning.
- **Steal:** navigability as a design constraint. Some subset of edges should form deterministic axes you can traverse without deciding.
- **Related:** Nelson's **transclusion** — content included by reference with identity preserved, so a quote remains the original rather than a copy ([Xanalogical Structure](https://xanadu.com.au/ted/XUsurvey/xuDation.html)). A graph edge to a source is not transclusion; transclusion means there is only one instance, appearing in many contexts.

### 11. Relational model
*Canonical: E. F. Codd (1970).*

Codd's objection to the CODASYL network model was precisely an objection to graphs: the navigational model required programs to chase pointers, and Codd insisted applications should **search by content, not by following links.** He argued the relational model "appears to be superior in several respects to the graph or network model presently in vogue," because it describes data "with its natural structure only," free of access paths imposed for retrieval convenience ([Two-Bit History, "Codd and the Relational Model"](https://twobithistory.org/2017/12/29/codd-relational-model.html)).

- **Graph verdict:** Inter-reducible, and the industry has now gone around this loop twice. Lost: **set-at-a-time, declarative, content-based access**, and the physical/logical independence that comes with it. In a graph, "what do I know about X" is a traversal from a starting node — you must already have a handle on X. In a relation it is a predicate over everything, no entry point required.
- **Steal:** never let traversal be the only access path. Content-addressed query must be co-equal, or the memory becomes unreachable from a cold start.
- **Historical caution worth carrying:** the navigational model lost to relational largely on ease-of-use grounds, not expressiveness. A typed weighted graph is a navigational model.

### 12. Multidimensional / OLAP cube
*Canonical: data cubes, star schemas, pivot tables.*

Facts are measures indexed by a tuple of dimension values, where each dimension carries its own hierarchy of aggregation levels (day → month → year), and the operations are roll-up, drill-down, slice, dice, and pivot ([AWS, "What is OLAP?"](https://aws.amazon.com/what-is/olap/); [Knowage, Multidimensional Analysis](https://knowage-suite.readthedocs.io/en/master/functionalities-guide/multidimensional-analysis/index.html)).

- **Graph verdict:** Reduces (a fact is a node with edges to dimension members) — this is exactly the star schema, and it is why the reduction is unpopular in practice. Lost: **aggregation as a native operation.** Roll-up requires that a dimension be a well-founded hierarchy with a summable measure; graphs have no such notion, so "summarize everything I know about deployments in Q2" becomes an ad-hoc traversal instead of a drill-up.
- **Steal:** the idea that *summarization is a movement along a dimension*, not a separate derived artifact. Closely related to NLS view control (#1).

### 13. Formal Concept Analysis / concept lattice
*Canonical: Rudolf Wille; Galois lattices.*

From a binary object-attribute incidence table, FCA derives the complete lattice of all *formal concepts* — maximal (object-set, attribute-set) pairs closed under a Galois connection ([Springer, "Formal Concept Analysis as Applied Lattice Theory"](https://link.springer.com/chapter/10.1007/978-3-540-78921-5_3)). Critically, the hierarchy is **derived, not authored**: you supply flat facts, and the concept hierarchy — including concepts nobody named — falls out mathematically, always as a complete lattice.

- **Graph verdict:** The lattice is drawable as a graph (it is literally called the Galois graph), but that's the *output*. Lost: the **generative guarantee.** The lattice is not a set of curated links; it is every concept implied by the data, with a proof that it is complete. Store the drawing as a graph and you have thrown away the derivation, so it no longer updates when a fact arrives.
- **Steal:** derive hierarchy from attributes instead of authoring it. If a memory system stores atomic (item, attribute) facts, groupings can be *computed*, and "which items share exactly these properties" is answered without anyone having pre-declared that category. Strong candidate for cheap emergent structure.
- **Cost to note honestly:** lattices blow up combinatorially, which is why FCA stayed academic.

### 14. Hypergraph / n-ary relations
*Canonical: hypergraph knowledge representation; the n-ary problem in RDF.*

A hyperedge connects any number of nodes at once. "Graphs can accurately capture binary relations… but they are not a natural representation of n-ary relations"; forcing multi-party events into pairwise edges "destroys their overall semantics," and the standard example is a protein complex that only exists in the presence of three or more proteins ([Survey: Representing Higher-Order Networks](https://arxiv.org/pdf/2605.12509); [Hypergraph-Based Knowledge Representations](https://www.emergentmind.com/topics/hypergraph-based-knowledge-representations)).

- **Graph verdict:** Reduces via reification — invent a node for the event and hang N edges off it. Lost: **arity as a checkable thing**, and atomicity. The reified event node is indistinguishable from a real entity, so nothing prevents a partially-built 4-ary fact from existing with only two arms attached. Every provenance question ("who said this, when, with what confidence") is an n-ary problem in disguise, so this bites any memory system that wants weighted, sourced beliefs.
- **Steal or decline explicitly:** decide whether facts are binary-with-reification or n-ary natively, and *write the decision down*, because the cost surfaces later as unenforceable invariants.

### 15. Frames, slots, schemas, scripts
*Canonical: Minsky, "A Framework for Representing Knowledge" (1974); Schank & Abelson's scripts.*

A frame is a stereotyped situation with named **slots** and **default values** filled by expectation until contradicted ([Minsky 1974, MIT course PDF](https://courses.media.mit.edu/2004spring/mas966/Minsky%201974%20Framework%20for%20knowledge.pdf)). A script is a frame for a typical *sequence* of events.

The essential companion citation is W. A. Woods, **"What's in a Link: Foundations for Semantic Networks" (1975)** — the canonical demolition of naive node-and-edge knowledge representation. Woods showed that link notations of the day had no agreed semantics: an arc might assert a fact, define a term, express a default, or state a structural relation, with nothing in the notation to distinguish them, and that essentially all of them were "logically inadequate for representing quantified information" ([Woods 1975, DTIC full text](https://apps.dtic.mil/sti/tr/pdf/ADA022584.pdf); [summary](http://www.jimdavies.org/summaries/woods1975-a.html)).

- **Graph verdict:** Frames reduce to nodes-with-typed-edges, and that reduction is exactly what Woods warned about. Lost: **slots with defaults and expectations.** A frame says "a meeting has an agenda; if you don't know it, assume none" — a graph edge cannot express a *missing but expected* value, so absence is indistinguishable from unknown-ness.
- **Steal:** typed slots with defaults, and the ability to represent "this should have a value and doesn't" (which is the same shape as the wiki red link, #7).
- **Decline at your peril:** Woods's warning. If a memory design has typed edges, the type system needs stated semantics — is `relates_to` an assertion, a definition, or a hint? — or the graph accretes into something no consumer can reason over.

### 16. Topic Maps
*Canonical: ISO/IEC 13250; the TAO model — Topics, Associations, Occurrences.*

Subject-centric by design: every subject has exactly **one** topic that gathers everything known about it. Associations relate subjects; occurrences link subjects to information resources ([W3C, RDF/Topic Maps interoperability guidelines](https://www.w3.org/2001/sw/BestPractices/RDFTM/guidelines-20060630.html)). Two features have no clean RDF equivalent: **scope** (an assertion is valid only within a stated context) and **multiple subject identifiers** enabling merge. The W3C survey is explicit that these are where interoperability breaks — identity mismatch causes incomplete merging, and "Topic Maps' contextual scoping lacks direct RDF equivalents." The community split is philosophical: RDF favoured automated machine inference, Topic Maps favoured "empowering subject matter experts" ([xml.com, "Topic Maps Now"](https://www.xml.com/articles/2017/06/23/topic-maps-now/)).

- **Graph verdict:** Serializes into RDF *lossily*, by the standards bodies' own admission. Lost: **scope** and **merge-by-identity**.
- **Steal:** scope. "This is true in context C" is exactly what an agent memory needs and what a global weighted edge cannot say — a belief learned on project A shouldn't fire on project B, and lowering the weight is the wrong instrument. Related to guard fields (#9).
- **Steal:** the one-topic-per-subject rule plus explicit merge on shared identifiers. This is the deduplication story most memory graphs don't have.

### 17. Folksonomy / tagging
*Canonical: del.icio.us, Flickr; Clay Shirky, "Ontology is Overrated" (2005).*

Shirky's argument: tags are "a radical break with previous categorization strategies," and "if you've got a large, ill-defined corpus, if you've got naive users, if your cataloguers aren't expert, if there's no one to say authoritatively what's going on, then ontology is going to be a bad strategy." Formally, a folksonomy is a **tripartite** structure of (user, tag, resource) — not bipartite, and not a plain graph.

**Contradictions, surfaced not smoothed:** critics argue Shirky "confuses ontology-as-specified-conceptualization with a very narrow form of specification" and that empirical tagging data shows users *do* converge on shared tags, contra his premise ([Halpin, "Evolving Ontologies from Folksonomies"](http://www.ibiblio.org/hhalpin/homepage/notes/taggingcss.html); [Trant, "Studying Social Tagging and Folksonomy"](https://repository.arizona.edu/bitstream/handle/10150/105375/trant-studyingFolksonomy.pdf)). The documented costs are real too: lack of precision, no hierarchy, low findability, poor scaling.

- **Graph verdict:** The tripartite structure reduces only by reifying the tagging *act*. Lost: **who tagged it.** Strip the user dimension and you lose the ability to say "this categorization is one perspective," which is the only thing that makes disagreement representable.
- **Steal:** the tagging *event* as the unit, carrying an agent and a timestamp — so a memory can hold competing categorizations rather than being forced to reconcile them at write time.

### 18. Conceptual spaces
*Canonical: Peter Gärdenfors, "Conceptual Spaces: The Geometry of Thought" (2000).*

Concepts are **regions in a geometric space** whose axes are quality dimensions (hue, weight, pitch), with similarity as distance and natural categories as convex regions. Gärdenfors positions this explicitly as a third option between symbolic and connectionist representation, motivated by a failure of the symbolic approach: it is "particularly weak at modeling concept learning, and concept learning is closely tied to the notion of similarity, which is also poorly served by the symbolic approach" ([MIT Press book preview](https://direct.mit.edu/books/monograph/2532/bookpreview-pdf/2444788); [excerpt/summary, IIT Kanpur](https://cse.iitk.ac.in/users/amit/books/gardenfors-2000-conceptual-spaces-geometry.html)).

- **Graph verdict:** **Genuinely does not reduce**, and it is the cleanest non-graph form in the survey. In a space, *every pair of items has a relation* (their distance) without any edge existing, and relations that were never authored — betweenness, "the thing halfway between A and B," "the nearest unlike neighbour" — are computable. Discretize into k-nearest-neighbour edges and you lose: continuity, betweenness, the ability to name a region that contains no stored item, and prototype structure (a category having a *centre*, with graded membership).
- **Steal:** similarity as an intrinsic, always-available relation requiring no authoring. A memory that only knows what it was told relates loses every connection nobody thought to write down — which was the original Aquanet failure (#3) in a different costume.

### 19. Embedding / latent space, and structure inside vectors
*Canonical: vector stores and RAG; Kanerva's Sparse Distributed Memory (1988); Plate's Holographic Reduced Representations and the VSA/HDC family.*

The engineering version of #18. **SDM** stores patterns in a high-dimensional binary space across randomly-distributed hard locations; retrieval is **content-addressable** by Hamming distance, and it "exhibits behaviors reminiscent of human memory, such as rapid recognition and the discovery of novel connections between seemingly unrelated ideas" ([Wikipedia, Sparse distributed memory](https://en.wikipedia.org/wiki/Sparse_distributed_memory)). **VSA/HDC** goes further, showing that compositional structure — binding variables to values, representing whole relational tuples — can live *inside a single fixed-width vector* via algebraic operations, "computing in superposition" ([Kleyko et al., Survey Part I](https://arxiv.org/abs/2111.06077); [Part II](https://dl.acm.org/doi/10.1145/3558000)). This is the strongest formal evidence that graph structure and vector geometry are not opposed.

- **Graph verdict:** Does not reduce. Lost from a graph framing: **graceful degradation and approximate recall.** SDM recall "may not be perfect, with accuracy depending on saturation" — a *feature*, since it means partial and noisy cues still retrieve. Graph traversal from a wrong node returns nothing.
- **Current-practice check, with a contradiction surfaced.** The 2026 agent-memory literature has converged on episodic/semantic/procedural tiers, and reports that "vector memory retrieves semantically similar facts, graph-style memory retrieves facts through entities and relationships, and both are useful; **neither is sufficient alone**" ([The Nuanced Perspective, "Designing Agentic Memory in 2026"](https://thenuancedperspective.substack.com/p/designing-agentic-memory-in-2026)). Other 2026 surveys make a stronger pro-graph claim, that graphs "model relational dependencies, hierarchy, and efficient retrieval better than flat stores" ([Rethinking Memory Mechanisms of Foundation Agents, arXiv 2602.06052](https://arxiv.org/pdf/2602.06052)). These are not the same claim and should not be averaged. The one operational warning both agree on: **do not mix episodic logs into a semantic index — it degrades retrieval for both.**

### 20. Chronological log / journal
*Canonical: Ryder Carroll's Bullet Journal; daily notes in Roam/Obsidian/Logseq; event sourcing in software.*

Entries are appended in time order and never reordered. The Bullet Journal's four components are rapid logging, an index, collections, and **migration** — a periodic review where surviving items are *rewritten* forward and the rest are allowed to die, which is framed explicitly as "more than just rewriting your to-dos, it's about taking time to ask what is important to keep" ([bulletjournal.com](https://bulletjournal.com/pages/how-to-bullet-journal); [BuJoing on migration](https://bujoing.com/bujo-rapid-log-migration/)).

- **Graph verdict:** Reduces to a path, trivially and pointlessly. Lost: **append-only as an invariant**, and with it the audit trail — a graph's current state usually cannot tell you what it believed last month. Also lost: time as a *free* organizing axis requiring zero authoring effort, which matters enormously because it is the one structure you get even when the capture is lazy.
- **Steal (arguably the most practically important item here):** **migration as the forgetting mechanism.** Effortful manual re-write is the filter — what isn't worth copying forward is gone, and decay is the default rather than an action. A weighted graph typically decays weights, which is a much weaker signal than "a re-derivation of this note was worth someone's attention."

### 21. Scheduling as organization
*Canonical: SuperMemo (SM-2), Anki, FSRS; Ebbinghaus's forgetting curve.*

The structure is neither topical nor relational — it is **temporal**. The system predicts a forgetting curve per item per learner and surfaces the item when recall probability falls to a threshold, typically 90% ([SuperMemo method](https://www.supermemo.com/en/supermemo-method); [Anki manual, Background](https://docs.ankiweb.net/background.html)). Items are scheduled *independently*; the feedback signal is the grade on each review.

- **Graph verdict:** **Orthogonal to graphs entirely** — it is not a competing topology, it's a competing answer to "what should be in front of me now." Lost when you think in graphs: the idea that **retrievability changes without the structure changing at all.** A graph is static until edited; a scheduled store re-prioritizes itself hourly with no writes.
- **Steal:** review-driven weight update. The weight on a memory should be a function of *retrieval outcomes* — was it recalled, was it useful — not of authoring intent at write time. This is the single most concrete, implementable idea in the survey for a *weighted* memory graph, because it answers "where do the weights come from" with something other than a guess.

### 22. Actionability-based organization
*Canonical: Tiago Forte's PARA (Projects, Areas, Resources, Archives); Johnny Decimal.*

PARA's whole move is to sort by **actionability rather than topic**, explicitly pushing against subject-based classification of the Dewey kind: "topic-based organization creates reference libraries; action-based organization creates systems that drive output" ([Forte, PARA summary](https://thomasjfrank.com/productivity/books/the-para-method-by-tiago-forte-summary-and-book-notes/)). Johnny Decimal is the opposite pole — a strict, deliberately shallow numeric taxonomy (`10-19`, `11.01`) that buys **memorable, stable addresses** by capping breadth and depth ([lucaf.eu on combining them](https://lucaf.eu/2023/02/23/luca-decimal.html)).

- **Graph verdict:** Reduces (properties on nodes). Lost: **the primacy of the axis.** These systems work because *one* dimension is the top-level cut and everything else is subordinate — that's what makes retrieval a two-step decision instead of a search. A graph flattens all dimensions to equal status, which is exactly the "no privileged entry point" problem.
- **Steal:** ask what the memory is *for* before asking what it's *about*. A memory sorted by "what would make an agent act differently" is a different object from one sorted by topic, and the survey suggests the former is more useful and less popular.
- **Also steal from Johnny Decimal:** constrain breadth deliberately so addresses stay memorable. Related to #6.

### 23. Mind map (radial) vs concept map (propositional)
*Canonical: Tony Buzan (1970s) vs Joseph Novak (Cornell, 1972).*

Two forms usually conflated. A **mind map** is a strict radial hierarchy: one central image, curved branches, single keywords, aimed at memorization and visualization. A **concept map** is a network where **every link is labelled with a relationship, so each connection reads as a proposition** — "plants require sunlight" — aimed at meaningful learning ([Mindomo comparison](https://www.mindomo.com/blog/concept-map-vs-mind-map/); [Storyflow guide](https://storyflow.so/blog/mind-map-vs-concept-map-complete-guide)). The brief names "somewhere between a mind map and Wikipedia" as this project's inspiration, so the distinction is load-bearing: a typed knowledge graph is a **concept map**, not a mind map.

- **Graph verdict:** Concept maps *are* labelled directed graphs — the closest match to this project's stated design in the entire survey. Mind maps reduce to trees and lose the single-centre discipline and the visual-mnemonic encoding (colour, curvature, image), which is the entire mechanism Buzan cared about.
- **Steal:** Novak's proposition discipline — an edge label must make the triple read as a true sentence. It is a cheap, checkable quality bar on typed edges, and it directly addresses Woods's complaint (#15).
- **Note honestly:** the searches surfaced no substantive scholarly criticism of Buzan's radial form; treat any claim of mind-map superiority as unevidenced in this pass.

### 24. IBIS / argument mapping
*Canonical: Kunz & Rittel (1970); Conklin's gIBIS (1988); Compendium.*

A deliberately tiny type system — **Issues** (questions), **Positions** (candidate answers), **Arguments** (pro/con) — for structuring argumentative discourse on wicked problems ([Wikipedia, Compendium](https://en.wikipedia.org/wiki/Compendium_(software)); [Eight to Late, "The what and whence of IBIS"](https://eight2late.com/2009/07/08/the-what-and-whence-of-issue-based-information-systems/)). Dialogue mapping builds the map live during conversation, so competing options sit side by side.

- **Graph verdict:** Reduces cleanly — it is a typed graph with about six node/edge types. Lost: essentially nothing structural, which makes it the useful counter-example in this survey. **What's lost is not in the data model but in the practice** — IBIS works because the map is built *live, by a facilitator, during the disagreement*, and because the type vocabulary is small enough to apply in real time without deliberation.
- **Steal:** severe restraint in the type vocabulary. IBIS is ~30 years of evidence that 3 node types and 2 edge types are enough to structure genuinely hard, contested reasoning. Any memory design proposing 20 edge types should have to explain why it needs more than Rittel did.
- **Steal:** first-class representation of *open questions* and *disagreement*. Most memory graphs store settled facts, so the state "we considered X and rejected it, here's why" — the highest-value thing an agent memory could hold — has nowhere to live.

---

## Shortlist: the five forms that most challenge node-and-edge

Ranked by how much they'd change the design, not by novelty.

**1. Conceptual spaces / embedding geometry (#18, #19).** The only form in the survey that is *provably* not a graph. Every pair of items relates by distance with no edge authored, so relations nobody thought to write down remain available; and betweenness, prototype centres, and regions containing no stored item have no graph analogue at all. It also directly answers the historical failure mode from spatial hypertext — authors stop authoring links, and a similarity space keeps working when they do. Take seriously that VSA/HDC shows compositional relational structure can live *inside* vectors, so "graph vs. vector" is a false binary.

**2. Sculptural hypertext / guard fields (#9).** Inverts the primitive: default-connected, with authored constraints that *suppress*. The relation is a predicate evaluated against current state, not a stored edge, which makes context-sensitivity ("recall this only while doing X") expressible in a way a static weight can never be. Reframes retrieval from "traverse from here" to "what is not excluded now." Cheapest big idea to prototype.

**3. Faceted / multidimensional classification (#2, #12, #10).** The core challenge is *enforced orthogonality*: independent axes freely combinable, with the promise that any legal combination names a findable class. Encoded as edge types this guarantee vanishes silently. Bring in OLAP's roll-up (summarization as movement along a dimension) and ZigZag's determinism (each dimension a partial function, so navigation needs no choice) and this is the strongest structural alternative on offer.

**4. Scheduling and decay as the organizing axis (#21, #20).** Orthogonal to topology, and it answers the question a *weighted* graph must answer and usually fudges: where do weights come from? Spaced repetition says they come from retrieval outcomes, updated automatically, with retrievability changing continuously while the structure stays still. Bullet-journal migration supplies the matching forgetting mechanism — effortful re-derivation as the filter, decay as default.

**5. Scope and reified relations (#16, #14, #8).** Three complaints with one shape: a relation needs to be a thing you can talk about. Topic Maps' scope ("true in context C"), hypergraph arity ("this fact has four participants, all required"), and Memex trails ("this path has a name, an author, and can be handed to someone") all require relations to carry structure. Provenance, confidence, and context are all n-ary and all get mangled by binary edges. Whatever this project decides here, decide it explicitly — the cost surfaces later as invariants nothing can enforce.

**Runner-up worth one line:** Formal Concept Analysis (#13), because it *derives* hierarchy from flat attribute facts with a completeness guarantee rather than asking anyone to author it — the cheapest available source of emergent structure, at the cost of combinatorial blowup.

---

## Cross-cutting recommendations

**Steal:**
- Trails as first-class named objects (#8) — for an agent, "how I reasoned to this" is the artifact node-and-edge stores keep losing.
- The red link (#7) and the empty slot (#15) — named-but-absent nodes give the memory a curiosity backlog.
- Novak's proposition test (#23) — an edge label must make the triple read as a true sentence.
- Migration (#20) — decay by default, survival by effortful re-derivation.
- Scope (#16) — beliefs true in a context, not globally weighted down.
- View control (#1) and roll-up (#12) — summarization as a view, not a stored artifact.
- Stable human-legible immutable IDs (#6, #22).

**Explicitly decline (with reasons, so the decline is auditable):**
- Single-parent hierarchy as a global constraint (#1).
- A large edge-type vocabulary (#24 — IBIS needed five types for wicked problems).
- Traversal as the only access path (#11 — Codd's objection to navigational models was ease of use, and a typed weighted graph *is* a navigational model).
- Mixing episodic logs into the semantic index (#19 — the one point all 2026 agent-memory sources agree on).

**Heed:** Woods (1975) is the standing warning (#15). Typed edges without stated semantics — is `relates_to` an assertion, a definition, a default, or a hint? — accrete into a store no consumer can reason over. And the Aquanet-to-VIKI history (#3) is the empirical warning: given only explicit typed links, real authors stopped linking. If typed edges are the only way to record a relation, expect relations to go unrecorded.

---

## Scoped null

**No form was found that is both non-graph-encodable and mature as a tool.** That verdict is narrow and does not close the question of graph-sufficiency. Two forms — conceptual spaces (#18) and sculptural/guard-field hypertext (#9) — resist graph encoding on principle rather than on convenience, and several others (faceted classification, Topic Maps scope, hypergraph arity) encode only by discarding an invariant they exist to enforce. "It reduces to a graph" was true for most entries and *informative* for almost none.

**Traditions searched:** tools-for-thought / PKM literature; HCI and hypertext research (ACM Hypertext lineage: Memex, NLS, Aquanet/VIKI/VKB, Storyspace, gIBIS, Xanadu/ZigZag); library and information science (faceted classification, folksonomy, Topic Maps); AI knowledge representation (frames, semantic networks, description-logic-adjacent, hypergraphs, FCA); cognitive science (conceptual spaces, schemas/scripts, forgetting curve); data modelling (relational, CODASYL, OLAP); connectionist and distributed memory (SDM, VSA/HDC, embeddings); contemporary LLM-agent memory (2026 surveys); and popular practice (Zettelkasten, commonplace books, PARA, Johnny Decimal, Bullet Journal, mind/concept maps).

**Traditions NOT searched — the honest gaps, roughly in order of how likely they are to contain a genuine non-graph form:**
- **Category theory / sheaf-theoretic knowledge representation.** Sheaves formalize "locally consistent data glued over a space with obstructions to global consistency," which is a plausible model for a memory holding locally-true-but-globally-contradictory beliefs. Not searched; would be the first follow-up.
- **Topological data analysis / simplicial complexes.** Related to hypergraphs but with genuine topological structure (holes, connectivity at multiple scales) that graphs lack.
- **Non-Western knowledge-organization traditions.** Chinese *leishu* encyclopaedias, Islamic *isnad* transmission chains (provenance-as-structure — likely relevant), Aboriginal songlines (route-as-memory, cf. #4), oral-formulaic composition. Ranganathan was reached via LIS, not via this route.
- **Archival and museum description.** ISAD(G), *respect des fonds* / original order, CIDOC CRM's event-centric model — provenance-first organizing, directly relevant to a memory system, and not covered.
- **Legal citation and precedent networks.** Shepardizing, distinguishing, overruling — a graph whose edges *change the truth value* of what they point at.
- **Process and workflow notations.** BPMN, Petri nets, statecharts — organizing by *process* rather than by topic. Statecharts' hierarchical-and-orthogonal state decomposition is a near-relative of faceting and was not examined.
- **Music notation, dance notation (Labanotation), knitting charts.** Domain notations that organize dense structured information with no graph framing at all.
- **Enterprise/library practice at scale.** SKOS, thesauri, MARC, controlled vocabularies in production — the survey covered theory more than operational practice.

**Method limits.** Findings are one search pass; several entries rest on secondary sources (blog summaries, encyclopaedia entries) rather than the primary papers, which are cited by name where the secondary source was what was actually read. No claim here has been checked against this repo's code, and no design work was done, per the brief.
