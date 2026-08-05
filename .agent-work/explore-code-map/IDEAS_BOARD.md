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
| **Replace the FUNCTION, not the artifact format — with a loss accounting.** The derived map replaces what the Cartographer map does, not its index/packets/overlays format; part of the work is understanding what we're losing. Human suspects most of what the old graph captured should be procedural and kept close to truth | Settles the replacement target and x1's comparison criteria (content coverage, not format reproduction); does NOT settle the loss accounting itself — x1 measures it | cycle-1, human |
| **Old-overlay dispositions: comments in code become the carrier.** Capabilities = really a "why" (concept-layer material). Decisions = arguably history that drives the design — candidate for retiring entirely to git history (tentative: "maybe"). Constraints (what information is available, what compute is limited to the function) = listed **in** the function as a comment; when code changes because an assumption changed, the comment changes, and the comment updates the graph. **The code IS truth; algorithms merely project that truth into an interpretable graph** | Settles the direction of travel for each overlay class and strengthens the two-way-flow verdict (comments are the durable store for constraints, not just concept prose); does NOT settle the comment grammar (see q3), nor finally whether decisions retire — flagged tentative | cycle-1, human |
| **FRAMING: this is developer ergonomics for agents — a STANDARD, not an invention.** "All I'm really doing here is making life easy on agents the same way we should make life easy on developers generally." Lean into it: invent nothing new; compose existing tools and conventions into a standard for the constellation-skills project, and make sure local constellation development agents know how to use the artifacts provided. Deliverable shape: adopted extraction tooling + comment/grouping conventions + produced artifacts + agent education | Settles the exploration's register (adopt-and-standardize over invent) and the deliverable shape; does NOT settle which tools/conventions the standard adopts — x1/x3 inform that | cycle-1, human |
| **Comment layer gets prefix conventions; every comment is an ASSERTION.** A comment states an assumption, a requirement, or an explanation; categorize it by kind and put it into the graph as a typed statement. Human expects this to be straightforward ("will take a little work") and assumes prior art exists for the categorization | Settles that a light convention is the mechanism (not free-prose-plus-judgment); does NOT settle the taxonomy or the claimed ease — x3 tests the prior-art assumption with measured accuracy numbers | cycle-1, human |
| **C++ arm is proof-of-concept, not a requirement.** superCoolSpaceSim is "a bit of a dead project"; the scip-clang run stands as the one PoC datum on C++ adoption cost and is not chased further (no Linux/CI variant, no Joern-for-C++). The standard's near-term target language is Python (f1Brainz is the primary dev area) | Settles the C++ arm's weight for this exploration; does NOT settle whether a future live C++ project re-raises it | cycle-1, human |
| **Kill condition named, and reframed as a DEGREE question.** The existing map's usefulness is already proven; the exploration's live question is whether the LLM-heavy Cartographer can be replaced by something algorithmic. If not at all, this is "more or less dead" — but the human suspects degree, not true/false. The measures: how much of the mapping job goes procedural; what higher-level-abstraction ability the procedure lacks; how much agent is needed for the "why" layer; what prior art exists for deriving the comment layer alongside the variable/function layer | Settles the kill condition's shape and cycle-1's agenda; does NOT settle the degree itself — that is what cycle 1 measures | cycle-1, human |

## Open threads

*Inherited from the handoff — these seed cycle 1.*

1. **Container granularity.** x5: the ecosystem splits at "does this name cross a file boundary," not variables-vs-functions. Strong default: durable state at boundaries stored, per-function locals derived on demand — but adopt on usefulness, not affordability (the scale pressure that forced the split elsewhere doesn't exist here).
2. **Call modeling.** Pure container↔transformer edges with the call graph as projection (x5 default, from LSP call hierarchy or occurrence-in-range), or direct call edges stored too? Side effects and closures are the test cases.
3. **Comment write-back mechanism.** How a graph-side concept edit becomes a code comment (format, placement, review path) so the round trip closes.
4. **Hole-driven prioritization.** The concrete metric for "needs a description first" — presumably connectivity/centrality in the derived graph.
5. **Pipeline concretely.** tree-sitter parse → SCIP resolve → emit statements → diff. What runs where; incrementality (SCIP is full-project today); node identity across renames; file granularity of stored statements (directory-per-subject / file-per-layer came from the parent).
6. **MATLAB arm (new, cycle 1 — human point of interest, not chased yet).** Tommy works in MATLAB a lot; the standard working similarly there would be good; the original superCoolSpaceSim is the MATLAB case (verified: `matlab_src/`, `.m` drivers). No SCIP indexer exists for MATLAB — candidate extraction routes: MathWorks' own dependency tooling (`requiredFilesAndProducts`, Code Analyzer) or tree-sitter-matlab plus our own resolution. If the pipeline seam is "any resolver that emits our statement lines," MATLAB is an adapter question, not a redesign.
7. **Concept candidates vs concept identity.** Comment-attached candidate extraction is deterministic; naming/merging/spanning concepts across N declarations needs judgment (unsolved feature-location territory). Where the deterministic pipeline hands off to the judgment step, and how model-named concepts are stored as confirmable statements with provenance.

## Excursions

| Id | Question (short) | Type | Status | Brief / result |
|---|---|---|---|---|
| x1 | How much of f1Brainz's Cartographer map can scip-python procedurally reproduce, and what does it miss? | prototype (measurement) | **complete** (cycle 1) | `excursions/x1-brief.md` → `excursions/x1-result.md` |
| x2 | Prior art: concept/comment layer derived together with the structural layer? Plus hole-prioritization and write-back precedents | research | **complete** (cycle 1) | `excursions/x2-brief.md` → `excursions/x2-result.md` |
| x3 | Prior art: classifying code comments as typed assertions; accuracy numbers; comment→graph pipelines | research | **complete** (cycle 1) | `excursions/x3-brief.md` → `excursions/x3-result.md` |
| x4 | Does centrality × docstring-holes reproduce the curated map's documentation choices on f1Brainz? (+ first "describe these first" artifact) | prototype (measurement) | **complete** (cycle 1) | `excursions/x4-brief.md` → `excursions/x4-result.md` |
| x5 | scip-clang on superCoolSpaceSim_cpp: the C++ adoption cost; same completeness and role gaps as Python? | prototype (measurement) | dispatched (cycle 1) | `excursions/x5-brief.md` → `excursions/x5-result.md` |

## Key findings — cycle 1, x1: extraction is solved for the spine; the spine is 7% of the map's text

*Excursion finding (measured, registry-verified) — NOT human verdicts yet. Full result: `excursions/x1-result.md`; all measurements under `evidence/x1/`.*

- **It runs: ~15 minutes to a working 22 MB index** (443 files, 3,686 functions, 600 classes, 16,767 named containers, 220,915 occurrences) — after a one-line patch: scip-python 0.6.6 is broken on Windows out of the box (`new RegExp(path.sep)`), and a forward-slash `--cwd` yields a **silently empty index with exit 0** — any pipeline needs a non-empty assertion on the output.
- **The degree answer, measured on f1Brainz's 7,793-line map: ~7% procedurally reproducible / ~50% skeleton-derivable with prose left to judgment / ~43% untouchable** (decisions/ 100%, overlays ~90%, purpose/confidence fields, Known Limits, Responsibility). The 50% middle bucket is the interesting one: SCIP generates every heading, name, signature, and dependency list of a packet — the sentence hung on each is the judgment residue.
- **On the structural spine, extraction beat the human map**: 34/34 curated container dependency edges confirmed, zero missed, **plus 5 real edges the map omits** — map-drift findings produced for free. The 5 remaining curated edges touch external nodes (fastf1, sqlite) whose *promotion to named architectural node* is human judgment, not an extraction gap.
- **CRITICAL for our model: scip-python emits ZERO WriteAccess and ZERO Import roles.** Every non-definition occurrence is ReadAccess — mutations indistinguishable from reads. The read/write directionality our container↔transformer edge assumes is **not available from this indexer**; it is recoverable from a plain Python AST pass (`Store`/`Load` contexts). Consequence: SCIP owns resolution/identity; a cheap AST pass owns the read/write layer. Also: `kind` never set (parse the symbol grammar), locals anonymous (`local 42` — names recovered only by reading source at the occurrence range), inheritance edges effectively absent (105 Relationship records for 600 classes).
- **Concept-layer seed density is two-tier**: ~72% of classes and public functions carry docstrings (good harvest for the transformer surface); containers are nearly bare (4.1% of class fields, 23.7% of module state). A concept layer over containers will be *inferring*, not harvesting. Docstrings are the channel — leading comments add +1.7pp, not worth scraping. Free bonus: Google-style `Args:` blocks give 646 parameters their own prose.
- **Load-bearing nulls**: incrementality untested (6-minute full rebuild per index as-is — gates a live map), rename/move identity untested, C++ untested (→ x5), single codebase (f1Brainz's map is unusually decision-heavy; proportions will move elsewhere), and no generated skeleton was put in front of a reader (the obvious next excursion).

**Tool-run queue and skips (cycle 1):** queued — `scip-clang` on superCoolSpaceSim_cpp once x1's verdict lands (measures the C++ adoption cost: compile_commands.json etc., the other half of the language story). Skipped with reasons, revivable: **Doxygen** (needs comment rewrites we haven't earned yet — human); **Joern** (heavy, weak Python frontend per x5 — revisit for C++ if scip-clang disappoints); **RepoAgent/RepoDoc-style LLM doc generation** (token cost; papers already bound the result; revisit when testing the judgment residue); **Sourcetrail** (unmaintained), **Understand** (commercial license), **CodeSee** (sunset).

## Key findings — cycle 1, x2: the prior art exists, and it draws the procedural/judgment line in one consistent place

*Excursion finding, agent-consolidated — NOT human verdicts yet. Full cited result: `excursions/x2-result.md`.*

- **The closest existing thing is RepoDoc (arXiv 2026)**: one graph holding code entities + concept entities + doc entities, structural relations extracted procedurally by AST, concepts named by an LLM. Its procedural/judgment split matches every other system surveyed: parsing, git-diff→affected-entities, traversal, and update ordering are procedural; concept naming, clustering decisions, and prose are judgment. Its incremental-update recall is 97% (procedural half works); its API coverage is 53% (judgment half doesn't scale) — the same "roughly half the codebase" hole x5 measured from the harvest side (60–75% of entities uncommented).
- **Reflexion models (Murphy/Notkin 1995, 30 years of standing)** are the cleanest statement of the split: the concept layer is an *input* (human-supplied model + mapping), and what's *derived* is the agreement/disagreement between concept layer and structure (convergence/divergence/absence). The concept layer is falsifiable against the code — a shape that fits "code is truth" exactly.
- **Doxygen grouping commands are a 20-year-old shipped answer to x5's level-mismatch objection**: `\defgroup`/`\ingroup`/`@{ @}` let one concept span N declarations, stored *in source comments*, with procedural resolution of hierarchy and membership. Precedent for both concept-spanning and comments-as-the-carrier.
- **Write-back: the field splits three ways** — into the source (Doxygen groups, docstring inserters, the CUP comment-updater line), beside the source with a git pre-commit hook (RepoAgent), or never touch the file and pay LLM re-anchoring (Codetations). The transferable law from org-babel's detangle: **write-back works exactly when the emitted text carries provenance markers back to its source** — pointer lookup, not similarity matching. Where you own the repo and have comment syntax, the into-source precedents work; Codetations' objections mostly don't bind.
- **Hole prioritization has a real literature with a live contradiction**: PageRank/HITS-style graph centrality over dependency edges is the best-performing prioritizer in several studies (and the key-class line literally uses "what humans chose to document" as ground truth for centrality), but McBurney reports static source attributes are poor predictors and *text* wins. Proposed reconciliation (unverified): per-entity attributional metrics ≠ whole-graph relational centrality. Design lean: rank holes by centrality, use text as an independent second signal.
- **Commercial "map your codebase" products are mostly dead** (Sourcetrail unmaintained, CodeSee sunset; Understand survives selling analysis/metrics). None derived a concept layer. Consistent with the concept layer being the hard, valuable part.

## Key findings — cycle 1, x3: the assertion framing is unprecedented (a gap, not a refutation); markers are what make classification easy

*Excursion finding, agent-consolidated — NOT human verdicts yet. Full cited result: `excursions/x3-result.md`.*

- **"Every comment is an assertion" has no prior art either way** — published comment taxonomies classify by *topic* (summary, usage, TODO, license), never by *what kind of assertion the comment performs*. Speech-act theory has been applied to developer Q&A but never to source comments. The framing is novel, not contradicted.
- **"Easily categorize" is false for free prose on exactly the classes we care about, true one-kind-at-a-time with templates.** Shared-task benchmark (NLBSE): rationale/why classification scores F1 0.21–0.31 even for the best entrant; the classes that score 0.85–1.0 are the ones carrying an explicit syntactic marker (`@author`, code blocks, tags). Binary per-kind extractors with templates hit the 80s–90s (assumptions F1 0.96 fine-tuned; Javadoc→spec 92% precision; in-project rule comments 90%+).
- **The design lean this hands us**: the reason easy classes are easy IS the marker — so the human's prefix-convention instinct is exactly what the literature rewards. **Write-time prefixes make comments self-classifying and delete the classification problem for new code**; the hard free-prose numbers then apply only to legacy backfill, where one-kind-at-a-time binary extraction is the working recipe. This is the Javadoc/JML tag pattern generalized to assumption/requirement/explanation.
- **Rationale comments are 2–4% of comments** in two independent corpora (and 60–75% of entities have no comment at all, per x5) — the "why" layer barely exists in the wild; it will be *authored under the standard*, not harvested.
- **Comment → typed statement → graph was found nowhere** — GraphGen4Code stores docstrings as untyped nodes in a 2B-triple graph; nothing types them. Another confirmation that the standard is composition, not invention — but the composed thing itself is new.

## Key findings — cycle 1, x4: PageRank refuted on this test; raw call frequency validated; 130 pre-certified holes for free

*Excursion finding (measured, registry-verified) — NOT human verdicts yet. Full result: `excursions/x4-result.md`; artifact: `evidence/x4/hole_priority_list.md`.*

- **PageRank over the symbol-level call graph failed to beat a random draw at every K** (lift 0.87–1.73x, p≥0.17); half its top 30 are private helpers (`_json_ready`, `_error`, `_ensure_matplotlib`). The mechanism of the failure is instructive: propagation *manufactures* importance for utilities that are called everywhere precisely because they are beneath notice. HITS was degenerate (sparse, near-acyclic graph). Scoped: one repo, one alpha, call-graph edges only — betweenness, boundary-crossing, churn, and text signals untested.
- **What validated: the dumbest signals.** Distinct-caller count and total call count into *public* entities both clear significance at every K≥20 (top-10 in-weight: 60% map-named vs 19.4% base rate, p=0.005; top-30: 47%, p=0.0005). "The entities called most often are ~2.4x more likely to be map-named" — weaker than the centrality hypothesis, but real.
- **The free target beats any ranking: 130 of the 487 entities the curated map names (27%) have no docstring.** The map already certified them worth explaining — no signal needs to be trusted. Top of that set: `PhysicsSimulator.simulate_lap`, `load_latent_power_module_bundle`, `EstimateStore.load`. This is the natural first work-queue for the concept layer.
- **Module-level validation is impossible on this repo by construction** — the map names 95.2% of modules, so the test is at ceiling. A stricter ground truth (dedicated section, not mere mention) would be needed.
- **The artifact shipped**: a ranked describe-these-first list (692 public docstring holes, ordered by the validated signal, with file:line). f1Brainz overall docstring coverage: 62.3% (interrogate), holes concentrated in `fantasy_scoring` (26%), `compound_prior` (30%), `latent_power` (35%).

## Interlinks (expected to grow)

- **Mind map:** owns librarian/traversal/dial; concept-identity judgment is the eventual seam. Not designed now.
- **Self-improvement:** none near-term; later, usage traces may feed traversal weights.

## Rejected ideas (with reasons)

*None yet.*

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
