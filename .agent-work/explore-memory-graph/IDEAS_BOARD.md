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

## Open threads

- **THE tricky bit — multiple traversal modes.** Focus (narrow, deep, alignment-gated) and inspiration (wide, weak-tie, cross-cluster) pull in opposite directions. How do both live in one graph without inspiration collapsing into "chase every vector"? What *governs mode selection* — agent intent, query type, an explicit budget? *(Central thread for the next cycle.)*
- **What is "excess detail," concretely?** A real transcript of agents stepping on themselves — context-window bloat vs. wrong-thread pursuit vs. retrieval noise. Different failure → different mode design. (Excursion candidate: research.)
- **The graph ↔ `episodes/` interface** — additive, but *how*? Does the graph index episodes, cite them, or hold its own nodes that point at them? (Not "replace" — that's retired.)
- **Node/edge grammar** — load-bearing for federation *and* for what "pull"/alignment weights attach to. Deferred until the mode design is clearer.
- The raw-dump open-questions set lives in draft `docs/MEMORY_GRAPH_ARCHITECTURE.md` (PR #417) — *input*, not conclusion.

## Rejected ideas (with reasons)

*Culled and rejected ideas stay here WITH their reason — a cull is a scoped verdict and can come back.*

- **#25 "no persistent graph at all — rebuild per-task from episodes + ranker"** — retired: the human confirms the graph is a *given*, not a hypothesis, so this tests a fork that isn't live. *Revives only* if graph upkeep proves untenable at implementation — a feature-level cost question, never a concept fork.
- **The "does a ranker beat a graph?" kill-condition framing** (agent-introduced) — retired: mis-set. There is no concept-level kill condition; pruning is per-pathway.

## Cycle log

*One row per cycle. None run yet — cycle 1 pending flavor choice.*

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| — | — | — | — |

---

### Provenance of this seed
Two idea dumps from the human (this session) + the draft capture in `docs/MEMORY_GRAPH_ARCHITECTURE.md` (PR #417). Grounded against existing repo memory doctrine: `docs/EPISODE_STORE.md` (mechanics vs. judgment), `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (ACE context-collapse warning; Voyager provenance), `docs/installed_externals_manifest.json` (external corpora already tracked). Deep-module vocabulary loaded from `skills/_shared/global-everyone.md` §"Deep-module vocabulary" for the spec phase.
