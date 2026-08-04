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
- **Coupled, project-local graphs** — a local directory couples graphs by current checkout, so what's in scope tracks where you are (project truth vs. cross-project signal).
- **Two speeds — fast sloppy working graph + maintained long-term graph** — cheap-write during the task, then an end-of-task *merge-up* of proven conceptual changes; sloppiness filtered at promotion, not carried into long-term memory.
- **Federation with external graphs** — same node/edge shape means public Wikipedia-style graphs plug in as memory, subject to provenance/trust.

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
- The raw-dump material (the original five ideas, the cross-cutting open questions, the not-yet-touched list) is folded into the **Raw-dump appendix** at the foot of this board — *input*, not conclusion.

## Rejected ideas (with reasons)

*Culled and rejected ideas stay here WITH their reason — a cull is a scoped verdict and can come back.*

- **#25 "no persistent graph at all — rebuild per-task from episodes + ranker"** — retired: the human confirms the graph is a *given*, not a hypothesis, so this tests a fork that isn't live. *Revives only* if graph upkeep proves untenable at implementation — a feature-level cost question, never a concept fork.
- **The "does a ranker beat a graph?" kill-condition framing** (agent-introduced) — retired: mis-set. There is no concept-level kill condition; pruning is per-pathway.
- **"`episodes/` is the front door / entry index"** (agent-introduced) — retired: the human says episodes are *unrelated* — a holding tank for runtime issues encountered while running code, maybe a graph someday but separate for now. The closer kin is the architecture map. *Revives* only if episodes are later graph-ified and deliberately linked in.

## Cycle log

*One row per cycle. None run yet — cycle 1 pending flavor choice.*

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun → (converged toward refine) | The point (directed relevance over a given graph); the librarian model + the one dial; substrate = existing architecture map (north star: general KG); pull as spreading activation | **Cracked the traversal question.** The near-term build is crisp (see below). Left open: **entry** (question+context → start nodes), **dial-setting** (how the system reads context to place the dial), the **two-speed** working/long-term graph (barely touched), and the **generalization** mechanism. Not converged — human's call. |

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
