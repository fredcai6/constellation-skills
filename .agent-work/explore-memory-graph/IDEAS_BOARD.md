# Ideas Board — `explore-memory-graph`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed. Keep it current — it is what survives a reopen cascade.

## The point

*Sharpened in cycle 1 against the starting questions; human-corrected (this session). The corrections below are settled, not provisional.*

**The graph is a given, not a hypothesis.** It stays. This exploration is about the *future
pathways/features the graph enables*, not about whether to build it. There is **no
concept-level kill condition** — pruning happens per-pathway, not at the concept. (Human,
verbatim: "no kill condition for the concept of a graph. we're just talking about future
pathways so some of those might be pruned.")

**The itch:** agents keep **stepping on themselves pulling in excess/adjacent detail.**
Good thinking is **directed** — intentional *focus* (deepen the thread that matters) and
intentional *expansion* (widen only when chosen) — over a network **connected enough to
inspire without forcing you to chase every vector.** Directed traversal is one **feature the
graph enables**, not a rival to it.

**Not replacing `episodes/`.** Red herring (human). The graph is **additive** — it coexists
with the episode store; "replace vs. index over episodes" is not a live question here.

**What "done" feels like — all three wins are the point, in this order:**
1. **Focused retrieval** — noticed *first*; the near-term win. Query returns a tight core + a
   few labeled doors, not a pile.
2. **Multi-mode traversal for cross-domain inspiration** — the **tricky bit**. Requires
   *multiple traversal modes* so an agent can deliberately reach across domains without
   collapsing back into "chase every vector."
3. **Compounding memory** — a **glorious byproduct** *if the first two are done right*, not a
   thing built directly.

## Current candidates

*Live directions still in play — not decisions. Carried in from the two idea dumps; each will be tested, sharpened, or culled in the cycles.*

- **Directed traversal as the core primitive** — the graph exists so an agent can *focus* (deepen one thread) and *expand* (widen deliberately) without walking the whole neighborhood. This is the load-bearing idea the second dump surfaced; the other four are in service of it.
- **MCP as the entry boundary** — memory mechanics live behind a tool so agents "don't think about thinking." Query/assert contract; traversal and linking below the waterline.
- **Coupled, project-local graphs** — a local directory couples graphs by current checkout, so what's in scope tracks where you are (project truth vs. cross-project signal). **Sharpened cycle 2 (human):** each project owns its graph outright; other projects are reached by *declared location* ("f1brainz is over here"), never by a global index. Federation is deliberate reach, not ambient availability.
- **Two-layer backend: address book + graph** *(new, cycle-2 discussion, human)* — a property/address store (relational-shaped) answers "which handful of topics" by content; the graph answers "what reaches from here." Addresses are cheap index numbers serving as identity only; properties carry the facets that selection runs on. Resolves the entry crux without a model call on the common path.
- **Two speeds — fast sloppy working graph + maintained long-term graph** — cheap-write during the task, then a *merge-up* of proven conceptual changes. **Revised by cycle 2 (x2):** merge-up must be *gated, additive, and episode-preserving* — competitive gating (promote only what beats what it displaces), eligibility tagged online during the task, supersede-don't-delete, raw material kept permanently. The end-of-task trigger and even the hard two-store split are now open questions (impasse-triggered promotion and one-store-with-provisional/settled-marking are live rivals).
- **Federation with external graphs** — same node/edge shape means public Wikipedia-style graphs plug in as memory, subject to provenance/trust.
- **Rule-driven edge growth** *(new, cycle 2, from x3)* — a small set of mechanized linking rituals (relate-check, compass, bounded causal descent, trade-off detection, scored analogy) that grow typed edges deliberately; edge-only rules run unattended, node-minting rules run capped, unfalsifiable rules run human-gated.
- **Suppression as the dial's mechanization** *(new, cycle 2, from x1)* — guard-field framing: default-connected, with constraints that *remove* by task state; retrieval = "what is not excluded now." Rival or complement to spreading activation.
- **Retrieval-outcome-driven weights** *(new, cycle 2, from x1+x3)* — spaced-repetition insight: weights/pull come from whether retrieved material got used, not from authoring intent. The concrete candidate mechanism for the deferred learned-pull pathway.

## Key finding — the closest kin already exists: the Cartographer map (cycle 1)

*Human pointer: "the closer equivalent is the docs/architecture area." `episodes/` is unrelated (a holding tank for runtime issues — maybe a graph someday, separate for now).*

The Cartographer map (`skills/cartographer/references/map-model.md`, artifacts under
`docs/architecture/`) is **the same species as the memory graph, already built**:
- **Explicitly a sparse graph** — struct hierarchy + capability/event/constraint/assumption/decision/claim overlays.
- **Typed, directed edges with semantics** — `supports`, `depends-on`, `emits`, `constrained-by`,
  `explained-by`, `verified-by`; each carries `provenance` (curated/generated), `evidence`,
  `confidence`. → the federation trust/provenance problem is **already solved on this substrate**.
- **An Inclusion Rule** — a node/edge earns its place only if it helps planning / boundary
  correctness / rule preservation / trust; when in doubt leave it out; speculative → Triage.

**The reframe this forces — two relevance filters, not one:**
- **Write-time sparsity** = the map's Inclusion Rule. "Don't chase every vector" applied to
  *what gets in*. **Already exists.**
- **Read-time dial** = the librarian. Even over a clean graph, one question wants a slice; the
  dial sets how wide. **This is the half we're designing** — the map has *no* traversal/librarian
  layer (read today via index + packets, not question+context → core+doors).

So the memory-graph work ≈ **a map-model-shaped graph + the librarian/traversal layer it lacks**,
plus the two things the map deliberately omits (two-speed working/long-term; learned pull —
the map is current-only, single-speed by doctrine).

**Correction to the earlier strawman:** edge-typing is **not** "optional for now" on this
substrate — the six edge types are load-bearing and a *gift to the dial*: a direct trace follows
structural edges (`depends-on`/`supports`); inspiration follows a *different* edge kind, a
lower-confidence edge, or crosses overlays. **Edge type may be a primary input to pull.**

## Working model: the librarian (cycle 1)

*The organizing metaphor, human-chosen. Not yet a spec — the frame the rest hangs on.*

**Interface = `question + context`.** The agent submits what it wants to know and its
situation; nothing else. No node ids, no mode names, no traversal knobs. The *intent* is
carried by how the question is framed; the system translates it.

**Two layers, matching the repo's own mechanics/judgment split (`docs/EPISODE_STORE.md`):**
- **The stacks = the graph.** Mechanical: stores, links, traverses. Never judges what you
  "really" need.
- **The librarian = a judgment layer on top.** Reads question+context, **dials the
  exploration level**, decides what to hand back. Inference, not lookup — plausibly the same
  *stochastic-sensor* class the repo already uses for episode "rhyme" (#308), aimed at a new
  job. **System owns mode selection** (human-settled), so agents never think about thinking.

**Candidate synthesis — the tension may dissolve.** Instead of *modes you switch between*, one
response with **two layers**: a focused **core** (exactly what was asked) + a few labeled
**doors** (nearby shelves you might not know about). Focus lives in the core; inspiration lives
in the optional doors you can ignore. The "dial" is then not a mode selector but **how many
doors and how far afield** — set by the librarian from your question/context. Cross-domain
inspiration becomes *how wide the doors open*, never a vector you're forced to chase. If this
holds, "multiple traversal modes" collapses to one traversal + a librarian-set dial (much
smaller to build). **Status: CONFIRMED by human — the dial rule below.**

**The dial rule (human, cycle 1).** One axis, default silence, expansion *triggered* not chosen:
- **Direct trace** (clear, specific) → silent core, no doors, cheap. The common path.
- **Unclear query OR strong associative pull in the graph** → open the doors, surface
  associated information.

"Interpret vs. answer" and "focus vs. inspiration" are the **same question** (human) — this one
dial answers both. Cost consequence: heavy librarian judgment fires only on ambiguity/pull,
never on a direct trace, so win #1 (focused retrieval) is the cheap common case.

## Shotgun divergence (cycle 1, un-culled)

*Cheap, wide, wild-sanctioned. Nothing here is a decision or even a candidate yet — culls and clustering happen at consolidation, with reasons. Loosely grouped for reading only.*

**Reframes — what "relevance" even is**
1. Relevance isn't a property of a memory, it's a property of the *path* you took to reach it.
2. The unit isn't "a memory," it's a **traversal budget** — you get N steps, spend them well.
3. A query carries an *intent vector*; an edge is followed only if it aligns. Directed = alignment-gated.
4. "Excess detail" is a **retrieval/traversal** concern, not a storage one — the fix lives in how you *walk* the graph, not whether it exists. *(anti-graph tail retired per human; the graph is a given.)*
5. The graph's job is to make **forgetting safe**, not to make remembering complete.
6. `focus` and `expand` are the only two verbs; everything else is implementation.
7. Inspiration = deliberately following exactly **one** low-alignment edge per query (a weak-tie budget).
8. A thought is a subgraph you assemble then throw away; memory is *which assemblies recur*.

**Traversal mechanics**
9. Two MCP verbs: `focus(node)` deepens, `expand(node, budget)` widens — budget caps the chase.
10. Every edge has a "pull" weight; expansion stops when cumulative pull drops below a threshold.
11. Traversal is **lazy**: fetch a node's neighbors only when focus lands there — no eager pull-in.
12. The agent never sees the graph — it sees a ranked **frontier** of "next places worth going."
13. Relevance decays with hop distance: 2 hops is inspiration, 4 hops is noise.
14. A query returns a **horizon**, not a set: focused core + a few *labeled expansion doors*.

**Two-speed / working graph**
15. The working graph is a scratch overlay; its nodes are "candidate edges" until merge-up validates them.
16. Merge-up promotes **edges that got traversed and paid off**, not nodes — usage is the validator.
17. Sloppy graph = write-ahead log; long-term = compacted store; merge-up = compaction.
18. Working graph forgets on task-end **by default**; you opt *in* to promote, never opt out.

**MCP boundary — no thinking-about-thinking**
19. The agent asks "what's relevant to X?" and asserts "Y mattered" — it never names a node id.
20. Assertions are **edges-in-waiting**; the graph decides if/where they attach. The agent stays dumb.
21. The MCP tool *is* the whole interface — swap graph for vectors for SQL and no caller changes.

**Federation / external**
22. External graphs mount **read-only, decay-pinned**: traverse in, never merge-up out.
23. Wikipedia is a graph with a different *provenance stamp*; federation = trust-tagging edges.
24. A federated node can *inspire* but can't be *cited as earned memory* until an episode validates it.

**Wild / kill-the-graph**
25. **No persistent graph at all** — rebuild the relevant subgraph per-task from `episodes/` + a ranker. (Direct test of Q5.)
26. Relevance is *learned*: log which expansions the agent actually used; retrain edge weights. The graph tunes itself.
27. Two agents = two working graphs; merge-up is a 3-way merge that **surfaces** conflict edges, doesn't resolve them.

## Key findings — cycle 2: the graph survives contact, but on conditions (excursion results)

*From the three cycle-2 research excursions (full cited results: `excursions/x1-result.md`, `x2-result.md`, `x3-result.md`). These are excursion findings, agent-consolidated — NOT human verdicts yet; the human elevates or culls.*

**x1 — the form question.** Almost every organizing form ever built *encodes* as a graph; almost none are *well served* by the encoding. The informative question is what the encoding makes expensive and which invariant it stops enforcing. Three losses recur: (1) **enforced independence** (facets/dimensions promise orthogonal, freely-combinable axes; edge types can't enforce that); (2) **the un-named relation** (spatial hypertext's founding evidence — Aquanet gave authors typed links and *they stopped linking*; VIKI was built for the unnamed proximity relations they used instead); (3) **the computed relation** (Storyspace guard fields: connection is a predicate over current reader/task state, evaluated at read time, not a stored edge). Top challengers to node-and-edge: conceptual spaces / embedding geometry (similarity as an always-available relation needing no authoring — and VSA/HDC shows graph-vs-vector is a false binary); guard-field suppression (default-connected; authored constraints *remove* — reframes retrieval as "what is not excluded now", which rhymes hard with our dial); faceted/OLAP roll-up (summarization as movement along a dimension); **retrieval-outcome-driven scheduling** (spaced repetition: weights come from retrieval outcomes, not authoring intent — a concrete answer to "where does pull come from"); scope + reified relations (Topic Maps' "true in context C"; trails as first-class nameable paths — "how I reasoned to this, saved"). Standing warnings: Woods 1975 (typed edges need stated semantics or the store becomes un-reasonable-over); Codd (a typed weighted graph IS a navigational model, and navigational lost to relational on ease-of-use — content-addressed query must be co-equal with traversal, which lands squarely on our **entry** crux). Cheap steals: the red link / empty slot (named-but-absent nodes = curiosity backlog), Novak's proposition test (an edge label must make the triple read as a true sentence), migration-as-forgetting (survival by effortful re-derivation, decay by default), IBIS's restraint (3 node types + 2 edge types structured wicked problems for 30 years — resist edge-vocabulary growth).

**x2 — the two-speed question.** The two-speed shape is real — independently reinvented by brains (complementary learning systems), storage engines (LSM-trees), and agent frameworks — but **our proposed version of merge-up is the exact configuration the strongest recent evidence kills**: Zhang 2026 tested "consolidate every task, rewrite the long-term store, compress the episodes away" across five benchmarks and it reliably degrades (one benchmark 100%→54% *after consolidating from ground-truth solutions*; memory drifts toward the model's prior about what a good lesson looks like). What survives: fast episodic buffer + **slow, GATED, additive** abstract store. The five mechanisms worth stealing: (1) **competitive gating at eviction** (W-TinyLFU: "does this beat what it would displace?", asked when working content is about to be lost — most tasks promote nothing); (2) **tag eligibility online during the task** (hippocampal ripples and generative-agents importance both score at capture; nothing surveys the whole day at bedtime); (3) **never destroy — supersede bi-temporally** (Zep: set `t_invalid`, keep the edge; audit trail through promotion); (4) **keep raw episodes permanently** — promotion is a *copy that abstracts*, never a move (three independent lines converge: Zhang's fix, multiple-trace theory, Zep's episode tier); (5) **atomic units through an explicit verb set with first-class NOOP** (Mem0's ADD/UPDATE/DELETE/NOOP — without NOOP an LLM asked to merge always merges something). Two structural challenges: the **end-of-task trigger is pure assumption** — no surveyed system promotes on task boundaries (size thresholds, eviction, cumulative importance, sleep; Soar promotes on *impasse-resolved*, arguably the best fit for "proven conceptual change"); and the **hard two-store split itself is contestable** — Cowan's embedded-processes model and generative-agents-in-production both suggest ONE store with an activation/provisional-vs-settled marking, with promotion as a state change on a node, not a move between stores. The split is only justified if the slow store can't tolerate fast writes without corruption. Also: the systems that handle contradiction best split *deciding* from *executing* (Letta's sleep agent holds exclusive write authority; Zep pairs LLM extraction with deterministic invalidation).

**x3 — the linking-rules question.** "5 Whys" has a large, mostly-mechanizable family. Two distinctions the source literature doesn't make but the design needs: **edge-only vs node-minting** rules (edge-only = cheap, bounded, safe unattended; node-minting needs caps + a bind-to-existing-node step or it's a bloat engine), and **checkable vs unfalsifiable** output (a `contradicts` edge can be tested — "state the contradiction in one sentence, or drop the edge"; a "reminds me of" edge cannot). Build-first shortlist: (1) **Ahrens four-way relate check** at node creation — contradict/correct/support/extend against k nearest existing nodes, justification required per edge, mints nothing, falsifiable; (2) **Idea Compass** — four fixed questions yielding `part-of`/`composed-of`/`analogous-to`/`contrasts-with`, best edges-per-call, only cheap source of contrast edges; (3) **bounded causal descent** (5 Whys capped at depth 3 + Ishikawa category fan, bind-or-mint per step) on problem/failure nodes; (4) **TRIZ trade-off detection** (detection half only) on decision nodes — sole source of `trades-off-against`; (5) **structure-mapped analogy with systematicity scoring** (Gentner) as a periodic batch — the only analogy rule that ships its own ranking criterion, and its high-scoring pairs feed schema-minting (analogical encoding). Free win: **Novak's cross-link ranker** — prefer proposed edges whose endpoints are currently far apart; a path-length query, no model call. Scoped nulls: random pairing (de Bono PO, Oblique Strategies) and SCAMPER fail *as autonomous rules* — an LLM will relate any two nodes on request, 100% output rate, unknown error rate; they revive with a human in the loop or a downstream usefulness signal (which is exactly the deferred **learned pull**). Caveat carried: human generation-effects don't transfer to agents — judge every rule on edge yield and correctness, never on its psychology-literature effect size.

**Cross-connections the consolidation surfaced (agent synthesis, for the human to test):**
- Guard fields and the dial may be the same shape: "direct trace → silent core" ≈ heavy suppression; "open the doors" ≈ relax the constraints. Suppression-over-default-connected is a *rival mechanization* of the dial to spreading activation — or its complement (activation proposes, guards veto by task-state).
- The Aquanet failure + the two-speed graph may solve each other: the working graph can be the home of *unnamed, provisional* association (cheap to record, no type demanded), and merge-up = the naming/typing step. Sloppiness isn't just tolerated in the fast tier — it's the feature that keeps agents recording relations at all.
- Retrieval-outcome weighting (spaced repetition) + x3's "usefulness signal" gate + deferred learned pull are one thread: the missing signal that would make culled techniques (random pairing) and learned pull both viable is *the same signal* — did a surfaced edge/door get used?
- Codd's warning lands on the entry crux: traversal must not be the only access path, so entry (question+context → start nodes) is content-addressed query, co-equal by design, not a bolt-on.

## Verdicts

*What has been decided, each with the SCOPE of what was tested. None yet — exploration has not run a cycle.*

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| The graph is a given (foundation, staying); exploration maps the pathways it enables | Settles the concept; does NOT settle which pathways survive | cycle-1, human |
| Directed traversal is a *feature enabled by* the graph, not a rival to it | Settles the framing; does NOT settle the traversal design | cycle-1, human |
| The graph is additive to `episodes/`, not a replacement | Settles coexistence; does NOT settle the graph↔episode interface | cycle-1, human |
| All three wins (focused retrieval → cross-domain inspiration → compounding) in scope, ordered | Settles scope + order; does NOT settle how modes coexist | cycle-1, human |
| Mode selection is **system-owned**; interface is `question + context`; system dials exploration level | Settles who chooses (the "librarian") | cycle-1, human |
| **The dial rule**: direct trace → silent core; unclear OR strong pull → surface associated info. Default silence, expansion triggered. Interpret-vs-answer = focus-vs-inspiration = one dial | Settles librarian behavior; does NOT settle what "pull" *is* mechanically, or static-vs-learned | cycle-1, human |
| **Phasing**: learned pull is the long-run destination (agreed) but DEFERRED — "learning" is hard to define now. Near-term = a **reliable traversal mechanism** with static/simple pull. Steps 2–3 of the walk keep the same shape static-or-learned, so nothing built now is thrown away | Settles sequencing; does NOT settle grammar, entry, or the eventual learning rule | cycle-1, human |
| **Two access paths, not one.** Entry is a **content-addressed lookup over an address-book/property store** (relational-shaped) returning a handful of node handles; the graph does reach *from* those handles. Traversal is never the only way in — a pure filter question is answered without a walk, with no model call on the common path | Settles the entry crux's shape and kills traversal-only access; does NOT settle the property schema, the store technology, or the similarity/filter mix | cycle-2 discussion, human |
| **The address is IDENTITY, not classification.** A topic gets a cheap index number within an area; stable, never reused, assigned without thought at write time. **Selection happens on properties**, not on the address path, so reclassifying never re-addresses and never breaks a citation. Relationships are allowed to emerge rather than being declared by filing | Settles address semantics; does NOT settle the property vocabulary or how areas are delimited | cycle-2 discussion, human |
| **Each project owns its own graph** (the architecture-map replacement), and the `project` qualifier is a **physical storage fact, not a taxonomy segment** — a pointer saying "f1brainz lives over here, go look that way." No store ever knows about everything; cross-project reach is by declared location | Settles graph ownership + what `project` means; does NOT settle the federation mechanism (lazy load? shared registry? read-only mount?) | cycle-2 discussion, human |
| **Substrate + north star**: librarian starts on the **existing architecture map**; long-term goal is generalizing the map from a *view of the code* → a **general knowledge graph**. Design constraint: the traversal layer must NOT bake in architecture-only assumptions (treat node kinds/edge types generically) | Settles what to build on and the direction; does NOT settle the generalization mechanism (relaxing current-only/architecture-anchored) | cycle-1, human |

## Open threads

- **THE live thread — the reliable traversal mechanism (near-term focus).** Minimum grammar
  strawman: *weighted edges over standable nodes* (node = a place with neighbors; edge = a
  weight = pull; edge-typing optional-for-now, the federation hook). The walk: **enter → step
  (follow highest pull, track budget) → stop (the dial; bounded by budget + visited-set,
  always halts)**. Steps/stop shaped by the dial already; grammar starts minimal.
- **The crux — step 1, "enter."** question+context → start node(s) is its own retrieval
  problem, *before* the graph can help. Entry is into a **map-shaped graph** (see finding
  below), via its struct/capability nodes — not via episodes.
- **THE live thread — pull as spreading activation (refined).** *Distance-decay retired as a
  raw-hop term* (human: hop count ≠ conceptual reach — topic separation varies; more hops only
  *mildly* more likely uncertain). Replaced by **path-accumulated pull**:
  `pull(node) = ∏ (edge-type-prior × confidence)` along the path, node `status` as a penalty.
  Hop count gets **no term of its own** — a long path of strong/confident edges stays strong;
  the "more reach → mild uncertainty" effect falls out of confidence compounding (each hop
  multiplies in a confidence < 1). This is **spreading activation**: activation flows from the
  entry frontier along type/confidence-weighted edges, fades over weak/uncertain edges, pools
  at nodes; the **dial = the activation threshold** (high → strongly-activated core only; lower
  → moderately-activated doors). Topology-aware, deterministic, uses only what the map stores;
  learning later only replaces the static priors, walk unchanged. Grounds in the cognitive model
  of associative recall — matches "how good thinking occurs."
  - **Sub-fork RESOLVED — it's the dial again.** accumulate-across-paths vs. single-best-path is
    *another dial setting*, not a global choice (human): direct hops = single best path (tight);
    open the dial = accumulate across converging paths (inspiration). **Phasing: start with the
    direct version** (single best path); accumulation is a later, wider dial setting.
- **RESOLVED — substrate fork.** Build over the existing architecture map; generalize to a
  knowledge graph long-term (see Verdicts). No longer open.
- **What sets the dial (query side)?** Signals of "direct trace" vs. "unclear": question
  specificity, agent state (stuck/looping → widen; mid-execution → tighten). Query-side
  input; "pull" is the graph-side input. Both feed the one dial.
- **FUTURE PATHWAY (deferred, not rejected) — learned pull → compounding memory.** When
  "learning" is definable: pull shaped by which opened doors got *used*. If built, win #3
  (compounding) falls out of the win-#2 machinery for free. Revisit after the traversal
  mechanism is reliable.
- **Is the librarian a model?** "Determine what you really need" is judgment — likely
  stochastic/LLM, not deterministic code — but the dial rule means it only runs heavy on
  ambiguity/pull, not on direct traces. Cost/latency/placement open. Grounds vs. #308 rhyme sensor.
- **RESOLVED — interpret-vs-answer & multiple-modes-as-a-switch.** Collapsed into the one dial
  (see Working model / Verdicts). No longer open.
- **What is "excess detail," concretely?** A real transcript of agents stepping on themselves — context-window bloat vs. wrong-thread pursuit vs. retrieval noise. Different failure → different mode design. (Excursion candidate: research.)
- **The graph ↔ `episodes/` interface** — additive, but *how*? Does the graph index episodes, cite them, or hold its own nodes that point at them? (Not "replace" — that's retired.)
- **Node/edge grammar** — load-bearing for federation *and* for what "pull"/alignment weights attach to. Deferred until the mode design is clearer.
- **NEW (cycle-2 discussion) — layers/frames: separate nodes, or facets on one node?** The human's maps already split **purpose / code description / testing** as explicit dimensions with *looser ties between them*. That is faceting, and the current map arguably already implements the separate-nodes answer (capability vs struct vs verification nodes, joined by `explained-by`/`verified-by`). Fork: does a subject get one node carrying a layer facet, or one node per layer sharing a subject identity? Bears on duplication, on differing change-rates/confidence per layer, and on whether you can traverse within a layer without dragging the others.
- **NEW (cycle-2 discussion) — layer as the primary suppression axis.** If layers are explicit, the cheapest guard is a *layer mask*: a direct implementation trace stays in the code layer; widening admits purpose and test layers. Possibly more natural and more legible than suppressing by edge type. Test against the edge-type/provenance masks.
- **NEW (cycle-2 discussion) — cross-project reach is a JUMP, not a walk.** Activation cannot be computed over a store that has not been loaded, so following a cross-project pointer is a deliberate, more expensive act than stepping an edge. Consequence: the boundary node must carry enough summary to decide whether to jump *without* loading the far store — which makes the cross-project pointer and cycle 1's **labeled door** the same object. Open: lazy read-only mount vs a thin shared registry of other projects' top-level topics; and whether cross-project doors are simply the widest dial setting.
- **NEW (cycle-2 discussion) — property store shape.** Many-valued facets (a node has several topics/layers/scopes) mean a join table, not wide columns. Scope ("true in context C") lands naturally here as a property. Cheap to decide now, annoying to retrofit.
- **CORRECTION pending (cycle-2 discussion) — multi-source entry vs single-best-path phasing.** Cycle 1 pinned phase 1 to single-best-path, but "select a handful of topics and fan out" seeds activation from several nodes at once, and converging paths from different seeds is the deferred accumulation behavior. Multi-source *entry* with single-best-path *traversal* is coherent — but the phasing note must say so explicitly rather than drift.
- **NEW (cycle 2) — is the two-store split real, or one graph with hot/settled node states?** The strongest x2 challenge: promotion as a state change on a node vs a move between stores. Decides much of the merge-up design.
- **NEW (cycle 2) — what triggers promotion?** End-of-task is an assumption no surveyed system shares. Candidates: eviction-time competitive gating, cumulative-importance threshold, impasse-resolved (Soar), scheduled sleep pass. Related: who holds write authority (the working agent vs a separate consolidator).
- **NEW (cycle 2) — spreading activation vs guard-field suppression** as the dial's mechanization — rivals, or activation-proposes/guards-veto?
- **NEW (cycle 2) — a provisional, unnamed-association tier.** The Aquanet lesson: demand a type for every relation and agents will stop recording relations. Does the working graph hold untyped proximity/association, with typing happening at merge-up?
- **NEW (cycle 2) — the usefulness signal.** One signal (did a surfaced door/edge get used?) unlocks three deferred things at once: learned pull, autonomous wild-linking rules, and promotion gating. What's the cheapest honest version of it?
- The raw-dump material (the original five ideas, the cross-cutting open questions, the not-yet-touched list) is folded into the **Raw-dump appendix** at the foot of this board — *input*, not conclusion.

## Rejected ideas (with reasons)

*Culled and rejected ideas stay here WITH their reason — a cull is a scoped verdict and can come back.*

- **#25 "no persistent graph at all — rebuild per-task from episodes + ranker"** — retired: the human confirms the graph is a *given*, not a hypothesis, so this tests a fork that isn't live. *Revives only* if graph upkeep proves untenable at implementation — a feature-level cost question, never a concept fork.
- **The "does a ranker beat a graph?" kill-condition framing** (agent-introduced) — retired: mis-set. There is no concept-level kill condition; pruning is per-pathway.
- **"`episodes/` is the front door / entry index"** (agent-introduced) — retired: the human says episodes are *unrelated* — a holding tank for runtime issues encountered while running code, maybe a graph someday but separate for now. The closer kin is the architecture map. *Revives* only if episodes are later graph-ified and deliberately linked in.

## Excursion briefs (cycle 2 — shotgun on the graph's nature)

*Recorded before dispatch, per doctrine. Full briefs live at `excursions/x[1-3]-brief.md`; results land at `excursions/x[1-3]-result.md` and fold back here at consolidation. All three human-initiated this session. The cycle's framing: the inspiration sits between a mind map and Wikipedia — poke at whether that spectrum is the whole space.*

- **x1 — Organizing forms beyond the graph** (research). *Question:* what ways/tools have people used to organize diverse interconnected thoughts, and is any of them genuinely NOT a graph (or lossy to reduce to one)? Answered = cited survey of 10–20 forms with steal/decline verdicts + a 3–5 form shortlist that most challenges node-and-edge.
- **x2 — Two-speed memory prior art** (research). *Question:* how do working-vs-long-term memory architectures (cognitive science AND software/AI systems) handle capture, consolidation/promotion, forgetting — what should the two-speed graph steal? Answered = cited comparison of promotion triggers/units/filters/authority + 3–5 mechanisms worth stealing + any evidence the two-speed split is the wrong shape.
- **x3 — Link-building cognition rules** (research). *Question:* what deliberate techniques in the "ask why 5 times" family build conceptual links, and which could an agent run mechanically as edge-generation rules? Answered = cited catalog of 8–15 techniques with link-kind + mechanizability verdicts + top 3–5 mapped to the map's typed edges.

## Cycle log

*One row per cycle. None run yet — cycle 1 pending flavor choice.*

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun → (converged toward refine) | The point (directed relevance over a given graph); the librarian model + the one dial; substrate = existing architecture map (north star: general KG); pull as spreading activation | **Cracked the traversal question.** The near-term build is crisp (see below). Left open: **entry** (question+context → start nodes), **dial-setting** (how the system reads context to place the dial), the **two-speed** working/long-term graph (barely touched), and the **generalization** mechanism. Not converged — human's call. |
| 2 | shotgun (graph nature) | Three research excursions: x1 organizing forms beyond graphs; x2 two-speed vs working/long-term memory prior art; x3 mechanizable linking rituals | **The graph survives, conditionally.** No mature non-graph form found (scoped: conceptual spaces and guard fields resist reduction on principle); the real finding is which invariants need homes (unnamed relations, scope, roll-up, content-addressed entry). Two-speed shape confirmed but OUR merge-up variant (unconditional, rewriting, episode-draining) is empirically killed — gated/additive/episode-keeping survives. Linking rituals yield a build-first shortlist of 5 edge rules + 2 hard nulls (autonomous random pairing, SCAMPER). Five new open threads (store split, promotion trigger, activation-vs-suppression, unnamed tier, usefulness signal). Not converged — human's call. |

---

## Raw-dump appendix (folded from the retired `docs/MEMORY_GRAPH_ARCHITECTURE.md`)

*The original idea-dump doc was folded into this board and deleted from `docs/` — the board is the single source of truth. Preserved here verbatim-in-substance so nothing is lost; the five ideas themselves live on above under **Current candidates** (developed) and were dumped in the human's own words this session.*

**The original five ideas (raw framing):**
1. **Memory as a graph, entered through MCP** — mechanics behind a tool so agents don't think about thinking.
2. **Coupled, project-local graphs** — a local directory couples graphs by current checkout.
3. **Two speeds** — a fast sloppy short-term working graph with hooks into maintained memory; end-of-task *merge-up* of proven conceptual changes.
4. **Federate external graphs** — same node/edge shape means public Wikipedia-style graphs plug in with little translation, subject to provenance/trust.
5. *(the sharpening second dump)* **directed relevance** — kill excess-detail overhead; intentional focus + intentional expansion; connected enough to inspire without chasing every vector. *(This became the point — see top of board.)*

**Cross-cutting open questions from the dump, with current exploration status:**
1. **Node/edge grammar** — what a node/edge is; typed/directed/weighted how. → *Partly answered:* on the map substrate, edges are typed+directed+confidence-weighted; still open for the generalized graph. (Also live under Open threads.)
2. **Storage vs. index** — is the graph the store or a layer over `episodes/`? → **Resolved/retired:** episodes are unrelated; the graph is additive and the closer kin is the architecture map, not the episode store.
3. **Judgment boundary** — keep mechanics and judgment apart (no ranking behind the tool). → **Confirmed:** the librarian is the judgment layer *on top of* the mechanical graph; matches `docs/EPISODE_STORE.md` doctrine.
4. **Merge-up mechanics** — delta unit, trigger, authority for sloppy→clean promotion. → **Still open, deferred:** tied to the two-speed graph (barely touched in cycle 1) and to learned pull.
5. **Coupling resolution** — how a checkout resolves to a set of coupled graphs, durably stored. → **Still open, untouched** in cycle 1.
6. **Provenance & trust** — one trust model spanning validated internal memory and unvalidated external nodes. → *Partly answered:* the map already carries `provenance`/`confidence` per node/edge; the federation trust model still needs its own pass.

**Not yet touched (named so the gaps stay visible):** retrieval ranking *(now shaped as spreading activation)*, eviction/forgetting, conflicting-edge resolution, concurrency (two agents writing one working graph), and how any of this reaches the checklist engine.

---

### Provenance of this seed
Two idea dumps from the human (this session), with the original dump doc now folded into the **Raw-dump appendix** above (doc deleted; board is the source of truth). Grounded against existing repo memory doctrine: `docs/EPISODE_STORE.md` (mechanics vs. judgment), `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (ACE context-collapse warning; Voyager provenance), `docs/installed_externals_manifest.json` (external corpora already tracked). Deep-module vocabulary loaded from `skills/_shared/global-everyone.md` §"Deep-module vocabulary" for the spec phase.
