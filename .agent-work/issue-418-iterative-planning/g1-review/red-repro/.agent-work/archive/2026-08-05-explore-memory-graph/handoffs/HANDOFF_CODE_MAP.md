# Handoff: the code map

Seed for a new exploration (suggested work id: `explore-code-map`). Descendant of `explore-memory-graph`, closed by split on 2026-08-05. The full record is `IDEAS_BOARD.md` beside this file's parent directory; excursion x5 (`excursions/x5-result.md`) is this handoff's main evidence base. Nothing here is a confirmed spec — verdicts below were settled by the human during the parent exploration; open threads are genuinely open.

## The point

A map for code: make a codebase easier to traverse **as an alternative to reading the code itself**. The graph is the navigation surface; the code stays the truth. This replaces the hand-maintained architecture map with a derived one. The long goal: a clear procedural description of what is going on inside the code and **why**. But first: build the graph.

## The model (settled)

- **Three node types.** Information **containers** (variables/state), information **transformers** (functions), **concepts** (the idea behind these things).
- **Two layers.** Containers + transformers form the architectural map; concepts form a conceptual map over it — a mind map of the code.
- **Derived views, never stored.** Collapse relationships through variables → a functional map; collapse through functions → a directional variable map. All collapsed views are projections computed on demand (Glean's derived predicates are the working precedent).
- **Derivation is algorithmic.** The architectural layer is close to a solved extraction problem (x5): SCIP indexers (`scip-python`, `scip-clang`) emit resolved-symbol occurrences with ReadAccess/WriteAccess roles — nearly our exact container↔transformer edge — at low adoption cost. Joern's code property graph holds the entire model in one artifact (down to variable-level data dependence) but is heavy, with a weak Python frontend. Calls are recoverable from LSP call hierarchy and belong in a projection.
- **Concept layer starts procedural, with holes as the signal.** A variable is representative of a concept — usually captured in its name, sometimes needing a comment. Comment/docstring attachment is deterministic and free, but coverage is the limit (~19% average comment density; 60–75% of entities uncommented; the failure mode is absence, not rot). Expect massive holes and unclear connections at first; **the holes are the prioritization signal** — high-level, many-connection functions and variables need descriptions first. Agents and humans detangle over time.
- **Two-way flow is required.** Comments must make their way from the graph back **into the code**, so re-deriving the graph preserves concept text. The code is the durable store for concept prose.
- **Re-derivation on change.** A code change forces supersession: re-derive, diff, update (per-node content hash; fanout of dependents is the named cost — Glean's lesson).

## Shared substrate (inherited by all three descendants)

Markdown/text files in git are the truth; any database is a disposable derived index — files win every disagreement. Statement layers are JSON-lines (one statement per line, diff-reviewable); prose layers are markdown; RDF/JSON-LD is an export format only. A node's address is an opaque serial identity, never a classification — selection happens on properties. Statements follow the Wikidata shape: qualifiers (when/where it holds) and references (where it came from), with a small, owned edge vocabulary. Storage is atomic; article-shaped views are rendered on demand. The graph holds the **current view** (true, known-false, suspected, and typed unknowns are all valid content); git holds history; retained history is rationale only. Each project owns its own graph; cross-project reach is by declared location. Evidence classes on statements set durability and supersession; the class of the source artifact sets the strength of the update — a code change means the old statement IS wrong (forced supersession).

## Open threads this exploration takes

1. **Container granularity.** x5's finding: the ecosystem splits at "does this name cross a file boundary," not at variables-vs-functions. Navigation tools store named declarations and derive locals on demand. Strong default: durable state at boundaries as stored containers, per-function locals on demand — but adopt on usefulness, not affordability (the scale pressure that forced the split elsewhere doesn't exist here).
2. **Call modeling.** Store pure container↔transformer edges and project the call graph, or store direct call edges too? x5 default: calls as projection (from LSP call hierarchy or occurrence-in-range). Side effects and closures are the test cases.
3. **Comment write-back mechanism.** How a graph-side concept edit becomes a code comment (format, placement, review path) so the round trip closes.
4. **Hole-driven prioritization.** The concrete metric for "needs a description first" — presumably connectivity/centrality in the derived graph.
5. **Pipeline concretely.** tree-sitter parse → SCIP resolve → emit statements → diff. What runs where, incrementality (SCIP is full-project today), node identity across renames, file granularity of the stored statements (directory-per-subject / file-per-layer came from the parent).
6. **Concept candidates vs concept identity.** Extraction of comment-attached candidates is deterministic; naming, merging, and spanning concepts across N declarations needs judgment (unsolved feature-location territory). Where the deterministic pipeline hands off to the judgment step, and how model-named concepts are stored as confirmable statements with provenance.

## Inputs and maintainer

Input: the code itself, via parse/resolve. Maintainer: a deterministic crawler; agents/humans assist only on the concept layer. No postmortem input — this map is algorithmically derived.

## Interlinks (expected to grow)

- **Mind map:** owns librarian/traversal/dial design; the code map's near-term retrieval is projections and queries, not walks — efficient exploration arrives later from there. Concept identity judgment is the seam where the two will eventually intertwine; not designed now.
- **Self-improvement:** none near-term. Later, traces of how the map gets used may feed traversal weights.

## Build order (human-set)

The code mapper is built **first**, before the mind map's traversal machinery. It is the most algorithmic, least blocked piece.
