# Excursion Brief: Deriving the code map algorithmically

Cycle 3 (refine), `explore-memory-graph`. Human-initiated.

## The one named question

How can the three-node-type code map be **derived algorithmically from a codebase** — what tooling and prior art exists for extracting each layer, at what granularity, with what support for incremental re-derivation?

Context for the searcher — the model being derived (settled this cycle, do not redesign it):

- The graph is specifically a **map for code**: a navigation surface that is an alternative to reading the code itself.
- Three node types: **information containers** (variables/state), **information transformers** (functions), **concepts** (the idea behind these things).
- Containers + transformers form the **architectural layer**. Edges run container↔transformer (a function reads and writes state), so the layer is bipartite in spirit; collapsed views (function-to-function map, directional variable map) are projections computed on demand, never stored.
- **Concepts** form a second layer over it — a mind map of the code. The human's working hypothesis: this layer is largely derivable too, "the concept side is just flipping comments" — i.e., comments/docstrings/docs are the raw material for concept nodes.
- Storage is atomic statements in git-covered files; a disposable index is derived from them. A code change **forces supersession**: re-derive, diff, update. So incrementality matters.

## Type

research

**Why this type:** a tooling/prior-art question about existing static-analysis and code-intelligence ecosystems; answerable from published work and tool documentation.

## What "answered" looks like

A cited assessment with four parts:

1. **A survey of extraction approaches mapped to our three node types.** For the architectural layer: compiler-lineage static analysis (def-use chains, reaching definitions, program dependence graphs), code property graphs (Joern/CPG), Google Kythe, SCIP/LSIF indexers, GitHub stack graphs, tree-sitter, LSP-based extraction, CodeQL, Meta's Glean — what each actually extracts, and which of its outputs map onto containers, transformers, and the edges between them. For the concept layer: comment/docstring extraction, documentation-generator lineage (Javadoc/Doxygen/Sphinx autodoc), feature-location and concern-mining literature, identifier/comment topic mining, and recent LLM-based repo summarization (repo maps, auto-generated codebase wikis). Do not assume all are relevant.
2. **A per-approach verdict**: granularity it settles on (does anything track *variables*, or does everything stop at symbol/function level?), how it models calls (data-mediated vs direct call edges), language coverage (Python and C++ both matter here), incremental re-derivation support, and realistic adoption cost for a small project.
3. **A derivation-pipeline sketch**: given the survey, what a parse → emit-statements → diff pipeline would plausibly look like, with an explicit line between what is **deterministic** (no model call) and what needs judgment (is comments→concepts pure extraction, or does it need a model to name/merge concepts?). Test the "flipping comments" hypothesis honestly: report where comments are known to be absent, stale, or wrong as a data source, with evidence from the comment-quality literature if it exists.
4. **The granularity finding, called out separately** — what node granularity the mature tools converged on and why. This directly feeds an open thread (containers-as-every-variable vs durable-state-at-boundaries).

## Budget / stop conditions

- Budget: one focused research pass; report even if partial. Prefer a short honest answer over a long speculative one.
- Do NOT design our schema or write our pipeline; survey, verdicts, and a plausibility sketch only.
- Do NOT install or run tools; this is a reading pass.
- **Scoped nulls:** "no tool extracts at variable granularity" (if true) kills that expectation for surveyed tools under these conditions, never the model itself. State what was and was NOT surveyed.

## Research excursion

- **Sources:** tool documentation and papers (Joern/CPG paper, Kythe docs, SCIP spec, stack graphs posts, CodeQL docs, Glean docs), program-analysis literature, feature-location/concern-mining literature, comment-quality studies, recent LLM repo-mapping writeups. Prefer primary docs and peer-reviewed work over blog commentary.
- **Findings format:** each claim carries its source. Keep the sourced description of what a tool does clearly separate from this excursion's own verdict about fit.

## Result artifact (required)

Write the full findings to `.agent-work/explore-memory-graph/excursions/x5-result.md` in the repo at C:\Programs\constellation-skills. The run is complete only when that file exists.
