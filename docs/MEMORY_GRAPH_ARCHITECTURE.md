# Memory Graph — idea dump

Status of this document: **raw idea capture, not a design.** These are unrefined notes
dumped to be preserved and argued with later. Nothing here is decided, specced, or
scheduled. It has not been reconciled against the existing episode store, lessons loop, or
rhyme sensor beyond the "how this touches what exists" notes below. Treat every claim as a
hypothesis. If this graduates, it becomes a design-it-twice brief, not an implementation.

Source: a five-point brain dump. Each idea is captured in the dumper's own framing first,
then annotated. Annotations are the note-taker's, and are the softest part of the document.

---

## The five ideas

### 1. Memory as a graph, entered through MCP

Model memory as a graph — nodes and edges, not a flat log or a folder of files. Put an MCP
server in front of it as the entry point so **agents don't have to think about thinking**:
an agent asks for what it needs and writes what it learned, and the graph mechanics
(traversal, linking, retrieval) live behind the tool boundary rather than in the agent's
head or its prompt.

*Why this matters:* the cost we keep paying is agents spending reasoning on *how to
remember* instead of on the task. MCP-as-entry pushes the bookkeeping below the waterline.
The agent's contract shrinks to "query / assert," and the graph decides shape.

*Touches what exists:* the episode store (`docs/EPISODE_STORE.md`) already draws the line
this idea depends on — it is the *mechanical* half of memory (capture, partition, find) and
"never judges, ranks, or decides that two episodes rhyme." An MCP memory-graph front is the
same split at a different layer: mechanics behind the tool, judgment left to the caller (or
to the downstream rhyme sensor, issue #308). Open: does the graph *replace* the episode
store's storage, or sit above it as an index?

### 2. Graphs can be coupled — project-local, keyed to checkout

Memory graphs are not one global blob. They **couple**: a local directory keeps graphs
connected based on **what project is currently checked out**. Switch project / checkout, and
the relevant memory couples in; the graph you operate against is a composition of the pieces
relevant to where you are.

*Why this matters:* this is the missing scoping story. A global memory is noise; a
purely-per-repo memory can't share what's genuinely cross-project. Coupling by checkout lets
the same substrate serve both — you assemble the working graph from whichever coupled graphs
the current context pulls in.

*Touches what exists:* Constellation already distinguishes *project truth* (`docs/agents/…`,
tracked per repo) from *cross-project workflow signal* (the `constellation` lessons in
`_shared`, bundled at install). Idea 2 is a mechanism for that distinction rather than a new
axis: coupling = the wiring that decides which graphs are in scope for this checkout. Open:
where does the "local directory" live so it survives worktree teardown and fresh clone — the
same durability question `episodes/` answered by being git-tracked at repo root?

### 3. Two speeds — a fast, sloppy short-term graph; a maintained long-term one

Two classes of graph:

- **Short-term / working:** a much **faster, sloppier** graph built for the *current
  problem*, with hooks into the maintained memories. Cheap to write, tolerant of mess,
  disposable.
- **Long-term / maintained:** the curated graph that persists.

The working graph runs hot during the task. At the **end**, **merge up** the conceptual
changes — promote what proved out of the sloppy graph into the maintained one; drop the rest.

*Why this matters:* this is the whole trick. It separates *write-cheap, read-fast during
work* from *write-careful, keep-forever*. You never pay curation cost mid-task, and you never
let mid-task mess pollute long-term memory. The merge-up step is where sloppiness gets
filtered.

*Touches what exists:* this is close to a graph-shaped restatement of the pattern
Constellation already runs in prose — the transitory lessons inbox (`.agent-work/LESSONS.md`,
"where lessons pass through, not where they live") feeding a graduation step that applies and
deletes, and the ACE Generator→Reflector→Curator loop cited in
`docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (explicitly warning against "context collapse" from
wholesale rewrites). **Import the warning:** merge-up must be an *itemized delta*, not a
regenerate-the-long-term-graph. Open: what's the merge-up unit — a node? a subgraph? a
claim with provenance? — and who/what runs it (the agent, a curator pass, a human gate)?

### 4. Federate with external graphs — same structure, so crawl anything graph-shaped

Our memory graph is **functionally the same structure** as public knowledge graphs, so hook
into external ones. No reason we couldn't **crawl Wikipedia** and treat it as memory — same
nodes-and-edges shape means external sources plug in with little translation, *especially*
public Wikipedia-style graphs.

*Why this matters:* if internal and external memory share one structure, "look it up
externally" and "recall internally" stop being two systems. The graph becomes the universal
adapter — federate a public source in by pointing coupling (idea 2) at it.

*Touches what exists:* Constellation already installs and tracks external corpora
(`docs/installed_externals_manifest.json`). This is the same instinct — external knowledge as
a first-class input — pushed down to the graph layer. Open, and load-bearing: **trust and
provenance.** Internal memory is execution-validated (cf. Voyager in
`RECURSIVE_IMPROVEMENT_DESIGN.md` — "lessons need provenance and validation before they
become doctrine"). Crawled Wikipedia is not. A federated node must carry its source and
never silently graduate into maintained memory as if it were earned. Freshness and crawl
staleness are the other open edge.

---

## Cross-cutting open questions (unresolved on purpose)

1. **Node/edge grammar.** What is a node — an episode? a claim? an entity? a skill? Edges
   are the harder half: typed how, directed or not, weighted by what? Idea 4's "same
   structure" claim only holds once this is pinned, and it's the thing most likely to be
   wrong on first cut.
2. **Storage vs. index.** Is the graph the store, or a layer over `episodes/`? Idea 1 works
   either way; the rest of the system doesn't.
3. **Judgment boundary.** Episode-store doctrine keeps mechanics and judgment strictly apart.
   The MCP front (idea 1) must hold that line — no ranking/rhyming behind the tool boundary,
   or it swallows the sensor's job.
4. **Merge-up mechanics (idea 3).** Delta unit, trigger, and authority. The "sloppy → clean"
   promotion is where this design lives or dies.
5. **Coupling resolution (idea 2).** How the current checkout resolves to a set of coupled
   graphs, and where that wiring is durably stored.
6. **Provenance & trust (idea 4).** One trust model spanning execution-validated internal
   memory and unvalidated crawled external nodes, so federation can't launder unverified
   claims into doctrine.

---

## Not yet touched

Retrieval ranking, eviction/forgetting, conflicting-edge resolution, concurrency (two agents
writing one working graph), and how any of this reaches the checklist engine. Out of scope
for an idea dump; listed so the gaps are visible.
