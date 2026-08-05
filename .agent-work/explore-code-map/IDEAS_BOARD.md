# Ideas Board — `explore-code-map`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed. Keep it current — it is what survives a reopen cascade.

Descendant of `explore-memory-graph` (closed by split 2026-08-05). Seed: `.agent-work/archive/2026-08-05-explore-memory-graph/handoffs/HANDOFF_CODE_MAP.md`. Main evidence base: parent excursion x5 (`.agent-work/archive/2026-08-05-explore-memory-graph/excursions/x5-result.md`).

## The point

A map for code: make a codebase easier to traverse **as an alternative to reading the code itself**. The graph is the navigation surface; the code stays the truth. Replaces the hand-maintained architecture map with a derived one. Long goal: a clear procedural description of what is going on inside the code and **why** — but first, build the graph. Build order (human-set): the code mapper is built **first**, before the mind map's traversal machinery — it is the most algorithmic, least blocked piece.

## Current candidates

*None yet beyond the inherited model — cycle 1 populates this from the open threads.*

## Verdicts

*Inherited verdicts were settled by the human during the parent exploration (`explore-memory-graph`); they arrive as inheritance, not as re-litigable candidates. New verdicts appear below them as cycles run.*

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Three node types: information **containers** (variables/state), information **transformers** (functions), **concepts** (the idea behind them) | Settles the node vocabulary; does NOT settle container granularity or call modeling | inherited (parent cycle-3, human) |
| Two layers: containers + transformers = architectural map; concepts = conceptual map over it | Settles the layer shape; does NOT settle the concept↔architecture edge vocabulary | inherited (parent cycle-3, human) |
| Derived views, never stored: collapse through variables → functional map; collapse through functions → directional variable map; all projections computed on demand (Glean's derived predicates = precedent) | Settles views-as-projections; does NOT settle which projections ship first | inherited (parent cycle-3, human) |
| Derivation is algorithmic; the architectural layer is close to a solved extraction problem (SCIP indexers emit resolved-symbol occurrences with ReadAccess/WriteAccess roles ≈ our container↔transformer edge) | Settles feasibility of the architectural layer per x5's survey; does NOT settle the pipeline concretely — x5 was one reading pass, nothing installed or run | inherited (parent x5) |
| Concept layer starts procedural; holes are the prioritization signal (high-connection uncommented entities need descriptions first); agents/humans detangle over time | Settles where the concept layer starts; does NOT settle the hole metric or the detangling process | inherited (parent cycle-3, human) |
| Two-way flow required: concept prose written graph-side must land back **in the code** as comments, so re-derivation preserves it — the code is the durable store for concept prose | Settles the requirement; does NOT settle the write-back mechanism | inherited (parent cycle-3, human) |
| Re-derivation on change: a code change forces supersession — re-derive, diff, update (per-node content hash; dependent fanout is the named cost, Glean's lesson) | Settles the update posture; does NOT settle incrementality mechanics | inherited (parent cycle-3, human) |
| Shared substrate (all three descendants): markdown/text in git is the truth, any DB a disposable derived index; statement layers JSON-lines, prose markdown, RDF/JSON-LD export-only; opaque serial identity, selection on properties; Wikidata statement shape (qualifiers + references), small owned edge vocabulary; atomic storage, article-shaped rendered views; current view only, git holds history; per-project graphs, cross-project reach by declared location; evidence classes set durability — code change = forced supersession | Settles the substrate for this descendant; does NOT settle file granularity or the exact line schema | inherited (parent, human) |
| Librarian/traversal/dial are mind-map-first; this map's near-term retrieval is projections and queries, not walks | Settles ownership and build order; does NOT settle the eventual traversal design | inherited (parent cycle-3, human) |
| Input is the code itself via parse/resolve; maintainer is a deterministic crawler; agents/humans assist only on the concept layer; no postmortem input | Settles inputs and maintainer; does NOT settle where the deterministic pipeline hands off to judgment | inherited (parent cycle-3, human) |
| **Kill condition named, and reframed as a DEGREE question.** The existing map's usefulness is already proven; the exploration's live question is whether the LLM-heavy Cartographer can be replaced by something algorithmic. If not at all, this is "more or less dead" — but the human suspects degree, not true/false. The measures: how much of the mapping job goes procedural; what higher-level-abstraction ability the procedure lacks; how much agent is needed for the "why" layer; what prior art exists for deriving the comment layer alongside the variable/function layer | Settles the kill condition's shape and cycle-1's agenda; does NOT settle the degree itself — that is what cycle 1 measures | cycle-1, human |

## Open threads

*Inherited from the handoff — these seed cycle 1.*

1. **Container granularity.** x5: the ecosystem splits at "does this name cross a file boundary," not variables-vs-functions. Strong default: durable state at boundaries stored, per-function locals derived on demand — but adopt on usefulness, not affordability (the scale pressure that forced the split elsewhere doesn't exist here).
2. **Call modeling.** Pure container↔transformer edges with the call graph as projection (x5 default, from LSP call hierarchy or occurrence-in-range), or direct call edges stored too? Side effects and closures are the test cases.
3. **Comment write-back mechanism.** How a graph-side concept edit becomes a code comment (format, placement, review path) so the round trip closes.
4. **Hole-driven prioritization.** The concrete metric for "needs a description first" — presumably connectivity/centrality in the derived graph.
5. **Pipeline concretely.** tree-sitter parse → SCIP resolve → emit statements → diff. What runs where; incrementality (SCIP is full-project today); node identity across renames; file granularity of stored statements (directory-per-subject / file-per-layer came from the parent).
6. **Concept candidates vs concept identity.** Comment-attached candidate extraction is deterministic; naming/merging/spanning concepts across N declarations needs judgment (unsolved feature-location territory). Where the deterministic pipeline hands off to the judgment step, and how model-named concepts are stored as confirmable statements with provenance.

## Excursions

| Id | Question (short) | Type | Status | Brief / result |
|---|---|---|---|---|
| x1 | How much of f1Brainz's Cartographer map can scip-python procedurally reproduce, and what does it miss? | prototype (measurement) | dispatched (cycle 1) | `excursions/x1-brief.md` → `excursions/x1-result.md` |
| x2 | Prior art: concept/comment layer derived together with the structural layer? Plus hole-prioritization and write-back precedents | research | dispatched (cycle 1) | `excursions/x2-brief.md` → `excursions/x2-result.md` |

## Interlinks (expected to grow)

- **Mind map:** owns librarian/traversal/dial; concept-identity judgment is the eventual seam. Not designed now.
- **Self-improvement:** none near-term; later, usage traces may feed traversal weights.

## Rejected ideas (with reasons)

*None yet.*

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
