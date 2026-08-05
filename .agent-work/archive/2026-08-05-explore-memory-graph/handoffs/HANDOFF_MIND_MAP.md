# Handoff: the mind map

Seed for a new exploration (suggested work id: `explore-mind-map`). Descendant of `explore-memory-graph`, closed by split on 2026-08-05. The full record is `IDEAS_BOARD.md` beside this file's parent directory; excursions x1 (organizing forms), x2 (two-speed memory), x3 (linking rules), and x4 (Deleuze) are its main evidence base. Nothing here is a confirmed spec — verdicts below were settled by the human during the parent exploration; open threads are genuinely open.

## The point

Shared, cross-project, agent-based memory: concept-anchored knowledge that would blow out a context window, managed so an agent can pull the facts relevant to consider. This side is **LLM-heavy** — judgment lives here. The founding itch: agents step on themselves pulling in excess/adjacent detail; good thinking is directed — intentional focus and intentional expansion over a network connected enough to inspire without forcing you to chase every vector. Three wins in order: focused retrieval, deliberate cross-domain inspiration, compounding memory as a byproduct of the first two.

## What this exploration owns (settled in the parent)

- **The librarian and the one dial.** Interface is `question + context`; mode selection is system-owned. Dial rule: direct trace → silent core; unclear or strong pull → surface associated info. Default silence, expansion triggered.
- **The traversal mechanism (the near-term build).** Enter → step (follow pull, track budget) → stop (dial-bounded, always halts). Phasing stands: reliable traversal with **static/simple pull first**; learned pull deferred. Entry is the crux: two access paths — a property/address lookup returns node handles, the graph reaches from them; a pure filter question never needs a walk or a model call.
- **Memory is the union derivable from artifacts, never the artifacts themselves.** The journal is an artifact with hooks in and out, like code. "What did you learn" intake is journal-focused for now: distill insights out of entries, attach ideas to ideas hierarchically.
- **Forgetting is de-weighting; eviction is separate and narrow.** Relevance decays (per-project, by time and use); a decayed topic gets harder to reach, never gone. Eviction only for false/antagonistic content, curator-gated: librarians propose, a curator disposes.
- **Typed nulls from day one** ("mu instead of false"); the argument/decision layer (IBIS-style) is first-class content — "we tried X and it failed because Y" is the highest-value thing this memory holds.
- **Deferred but shaped: usage and success as two traversal-derived weights** (the librarian's explored subgraph vs the path it settled on), kept separate, never pre-combined; trace reason fields are mechanism identifiers, not prose. Explicitly not the first version.
- **Candidates held, not adopted** (from the multi-geometric roll-up, status: idea material): named geometric spaces over properties, suppression-as-masks vs spreading activation, rule-driven edge growth (x3's five mechanizable rules), retrieval-outcome-driven weights, x4's centralization guard / orthogonal-isolation detection / exteriority lint rule / disagreement edge type.

## Shared substrate (inherited by all three descendants)

Markdown/text files in git are the truth; any database is a disposable derived index — files win every disagreement. Statement layers are JSON-lines (one statement per line, diff-reviewable); prose layers are markdown; RDF/JSON-LD is an export format only. A node's address is an opaque serial identity, never a classification — selection happens on properties. Statements follow the Wikidata shape: qualifiers (when/where it holds) and references (where it came from), with a small, owned edge vocabulary. Storage is atomic; article-shaped views are rendered on demand. The graph holds the **current view** (true, known-false, suspected, and typed unknowns are all valid content); git holds history; retained history is rationale only. Each project owns its own graph; cross-project reach is by declared location. Evidence classes on statements set durability and supersession; the class of the source artifact sets the strength of the update — a code change forces supersession, a recorded opinion adds a contextual note.

## Open threads this exploration takes

1. **Entry design** — question+context → start nodes: the property schema, the store technology, the similarity/filter mix, and whether an embedding layer earns its cost over properties+queries (residue: graded similarity along undeclared axes, exactly the cross-project case).
2. **Dial mechanics** — how the system reads context to place the dial; suppression masks (by edge type / provenance / layer) vs spreading activation, or both.
3. **Curator process** — the evidentiary bar for "misleading," the propose/dispose loop, who re-judges reliability over time.
4. **Decay concretely** — rates, thresholds, grace period for new material.
5. **Learn-channel prompt** — "process this journal entry": contextualizing an observation into an evidence class; the full class list; how purely-inferred statements (derived from statements, no artifact) are classed.
6. **Cross-project federation** — jump economics (lazy mount vs registry), same-subject convergence under opaque ids.
7. **Null flavor list** per node kind; the agent-side observation-ledger format (short-term memory shell is parked with self-improvement for now).

## Inputs and maintainer

Inputs: journals, distilled insights, human/agent judgment, postmortem "what did you learn" observations (journal-focused for now). Maintainers: the librarian (read side), a curator (write gate), a background crawler (link building) — all with a model in the loop where judgment is needed.

## Interlinks (expected to grow)

- **Code map:** built first; consumes this exploration's traversal/librarian work later. Concept identity (naming/merging/spanning concepts over code) is the seam where the two eventually intertwine.
- **Self-improvement:** owns postmortem intake; feedback = procedural memory (skills), this graph = declarative memory, artifacts/journal/traces = episodic. Observations route by the three questions; only "what did you learn" lands here, and only via the journal for now.
