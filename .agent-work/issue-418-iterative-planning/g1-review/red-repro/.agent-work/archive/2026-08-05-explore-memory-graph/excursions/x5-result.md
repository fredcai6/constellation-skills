# x5 result: Deriving the code map algorithmically

Excursion type: research. Cycle 3 (refine), `explore-memory-graph`. One focused pass, reading only — no tool was installed or run, per the brief.

**Headline.** The architectural layer is close to a solved extraction problem, and two shipping indexers (`scip-python`, `scip-clang`) already emit almost exactly the container↔transformer read/write edges the model wants. The concept layer is not a solved extraction problem, and the survey found no tool that derives it — the "flipping comments" hypothesis is mechanically true for the *attachment* step and empirically false for *coverage*: the comment-density literature says roughly 60–75% of public code entities carry no comment at all, so for most transformers there is nothing to flip. The granularity finding (§4) is the one most likely to move an open thread: the mature tools split cleanly at "does this name cross a file boundary," not at "is this a variable."

---

## 1. Survey of extraction approaches

### 1a. Architectural layer (containers, transformers, and the edges between them)

**Program dependence graphs / system dependence graphs (compiler lineage).** The classical foundation. A slice is taken with respect to a program point and a *variable*, and consists of the statements that might affect that variable's value at that point ([Horwitz, Reps & Binkley, TOPLAS 12(1), 1990](https://research.cs.wisc.edu/wpis/papers/toplas90.pdf)). The SDG extends the single-procedure PDG to collections of procedures, adding data-dependence edges that represent transitive dependencies due to the effects of procedure calls, built with an auxiliary structure representing calling and parameter-linkage relationships (ibid.). Relevance to our model: this lineage is the only one in the survey whose *primitive* is "a variable at a program point," and its central difficulty — correctly accounting for calling context — is precisely the difficulty of saying "this function writes that state" across a call boundary.

**Code property graphs / Joern.** The CPG merges AST, CFG and PDG into one property multigraph; all nodes originate from AST nodes, control-flow and control-dependence edges are established on statement and predicate nodes, and **data dependence edges are established on the variable level** ([Yamaguchi et al., IEEE S&P 2014](https://www.researchgate.net/publication/263658395_Modeling_and_Discovering_Vulnerabilities_with_Code_Property_Graphs)). The [CPG specification](https://cpg.joern.io/) defines node types that map directly onto our two architectural types:

- `LOCAL` — "represents a local variable"; `MEMBER` — a type member (field); `IDENTIFIER` — "an identifier as used when referring to a variable by name"; `FIELD_IDENTIFIER` — the `b` in `a.b`. These are containers.
- `METHOD` / call sites. These are transformers.
- `REF` — "the source node is an identifier that denotes access to the destination node," i.e. use→declaration.
- `REACHING_DEF` — "a variable produced at the source node reaches the destination node without being reassigned," carrying a `VARIABLE` property naming which variable propagates.
- `CALL` — "connects call sites to the method node that represents the method they invoke"; plus `ARGUMENT`, `RECEIVER`, `EVAL_TYPE`.

Joern ships frontends for C/C++ (`c2cpg`) and Python (`pysrc2cpg`) among others ([Joern frontends docs](https://docs.joern.io/frontends/), [repo](https://github.com/joernio/joern)). The Python frontend has documented rough edges: type-declaration inheritance is recorded in two fields that "sometimes disagree," and the docs advise querying both ([Joern Python frontend](https://docs.joern.io/frontends/python/)); a reported `StringIndexOutOfBoundsException` on importing a large Python project ([joern#2269](https://github.com/joernio/joern/issues/2269)) is one data point on robustness at scale.

**Google Kythe.** A language-agnostic graph schema of nodes (with facts) and edges. The [schema reference](https://kythe.io/docs/schema/) defines a `variable` node kind with subkinds `local`, `local/parameter`, `field`, and edges including `defines/binding` (definition site anchor → semantic node), `ref` (use site), `ref/writes` ("references in expressions likely updating values"), `ref/call`, `property/reads`, `property/writes`, and `param.N` ("A param.N B if B is the Nth parameter of A"). It also carries an `influences` edge — "A directly affects B during program evaluation" — marked experimental. Callgraph construction is a documented use ([Kythe callgraphs](https://kythe.io/docs/schema/callgraph.html)). Cost: indexing requires knowing every dependency and compiler setting for a file, delivered via a compilation database ([KCD spec](https://kythe.io/docs/kythe-compilation-database.html)); the repo README lists indexer implementations for **C++, Go, and Java** ([kythe/kythe](https://github.com/kythe/kythe)). The docs are explicit that purely dynamic languages like Python and JavaScript that lack type annotations produce an AST without enough information to do more than rudimentary scoped name lookup ([writing an indexer](https://kythe.io/docs/schema/writing-an-indexer.html)).

**SCIP (and its predecessor LSIF).** SCIP is Sourcegraph's replacement for LSIF, a Protobuf schema centred on human-readable string symbol IDs rather than LSIF's monikers and result sets ([announcing SCIP](https://sourcegraph.com/blog/announcing-scip)). From [scip.proto](https://github.com/sourcegraph/scip/blob/main/scip.proto), the parts that matter here:

- Symbols follow `<scheme> ' ' <package> ' ' (<descriptor>)+`, with descriptor suffixes including `Type`, `Term`, `Method`, `TypeParameter`, `Parameter`, `Meta`, `Local`, `Macro`.
- **Local variables are representable**: the `local <local-id>` symbol form exists, restricted to entities local to a Document and not accessible from outside it.
- `SymbolRole` is a bitset: `Definition` 0x1, `Import` 0x2, **`WriteAccess` 0x4, `ReadAccess` 0x8**, `Generated` 0x10, `Test` 0x20, `ForwardDefinition` 0x40.
- There are **no call edges and no data-flow representation**. `Relationship` carries `is_reference` / `is_implementation` / `is_type_definition` / `is_definition` only.

Indexers exist for Python ([scip-python](https://github.com/sourcegraph/scip-python)) and for C/C++/CUDA ([scip-clang](https://sourcegraph.com/blog/announcing-scip-clang), beta, built on Clang 16, driven by `compile_commands.json`, designed to handle Chromium/LLVM/Linux-kernel scale). Incrementality is the weak point: SCIP generation is always full-project, there is no per-file generation, and incremental indexing is on the roadmap rather than shipped ([Sourcegraph docs / scip-clang announcement](https://sourcegraph.com/blog/announcing-scip-clang)).

**GitHub stack graphs.** An extension of Visser et al.'s scope graphs; name binding information is encoded as a graph in which paths represent valid bindings, and resolving a reference to its definition is a path-finding search ([Creager & Hendrickson, *Stack graphs: Name resolution at scale*, EVCS 2023 / arXiv:2211.01224](https://arxiv.org/abs/2211.01224)). The headline property is that **graph construction and path-finding are file-incremental**: an isolated subgraph is built per source file with no visibility into any other file, and data can be generated without configuration from the repository owner and without tapping the build process ([Introducing stack graphs, GitHub Blog](https://github.blog/open-source/introducing-stack-graphs/); [github/stack-graphs](https://github.com/github/stack-graphs)). Scope: name binding only — no calls, no dataflow, no state.

**tree-sitter.** Incremental GLR parsing with error recovery: only the affected parts of the syntax tree are rebuilt on edit, and invalid or mid-edit code yields a working tree with error nodes ([tree-sitter docs](https://tree-sitter.github.io/tree-sitter/)). It is a parser, not a resolver — GitHub uses it for *partial* symbol resolution in the online code viewer, with stack graphs layered on for precise navigation. A critique worth knowing before building on it: mainstream tree-sitter bindings traverse only named nodes and discard anonymous tokens, so operators vanish and `x + y` / `x * y` produce the same tree ([Cubix, *Why Tree-Sitter is inadequate for program analysis*](https://www.cubix-framework.com/tree-sitter-limitations.html) — vendor-authored, treat as a pointer to check rather than settled fact).

**LSP.** `textDocument/documentSymbol` gives a declaration outline; call hierarchy (`textDocument/prepareCallHierarchy`, `callHierarchyItem/incomingCalls`, `callHierarchy/outgoingCalls`, since spec 3.16) gives a portion of the static call graph ([gopls navigation docs](https://go.dev/gopls/features/navigation)). Two limits are documented rather than incidental: dynamic calls are excluded because detecting them is not analytically practical (ibid.), and support is per-server — some servers do not implement `prepareCallHierarchy` at all ([claude-code#38683](https://github.com/anthropics/claude-code/issues/38683)). No variable read/write graph, no dataflow.

**CodeQL.** The program is a relational database queried in QL. It carries SSA form as a first-class dataflow concept: `DataFlow::SsaDefinitionNode` is "a data flow node that corresponds to an SSA variable, which is a local variable with additional information to reason more precisely about different assignments to the same variable" ([CodeQL dataflow docs](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/)). In Python a dataflow `Node` is either an SSA variable (`EssaNode`) or a control-flow node ([Python DataFlowPublic](https://codeql.github.com/codeql-standard-libraries/python/semmle/python/dataflow/new/internal/DataFlowPublic.qll/type.DataFlowPublic$Node.html)); in C/C++ the local flow step relation follows def-to-first-use and use-to-next-use on SSA variables ([C/C++ dataflow guide](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-cpp/)). Local dataflow is within one callable and is "easier, faster, and more precise"; global dataflow is more powerful and more expensive (ibid.). C++ database creation runs the build under compiler tracing ([database create](https://docs.github.com/en/code-security/codeql-cli/codeql-cli-manual/database-create)). Incremental analysis for C/C++ and Go landed in 2026 and is available in the CLI from 2.25.5 ([GitHub Changelog, 2026-06-10](https://github.blog/changelog/2026-06-10-incremental-analysis-for-go-c-c-and-codeql-cli/)).

**Meta Glean.** Indexes C++, Python, PHP, JavaScript, Rust, Erlang, Thrift and Haskell, storing facts about declarations, classes, methods, type signatures, inheritance and docstrings ([Indexing code at scale with Glean, Meta Engineering, 2024-12-19](https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/)). Two mechanisms are directly relevant to our storage/index split:

- **Derived predicates**: facts generated by a query rather than an indexer, either `stored` (computed once and persisted — "rather like a materialized view in SQL") or computed on the fly at query time ([Glean derived predicates](https://glean.software/docs/derived/)). This is a working precedent for "collapsed views are projections computed on demand, never stored" — with the option to materialise when it pays.
- **Incrementality by stacking**: immutable database layers, each of which can non-destructively add to or hide information from the layers below, avoiding a full reindex. The stated practical limitation is **fanout** — when a file changes, all dependent files must be reprocessed, and Glean computes the fanout set using its own queries, e.g. finding every file that includes a modified C++ header (Meta Engineering, ibid.; [Incremental indexing with Glean](https://glean.software/blog/incremental/)).

The article does not state whether local variables are indexed; on the evidence available Glean's facts are declaration-level.

**Doxygen (as a structure extractor, not just a doc tool).** With `CALL_GRAPH`/`CALLER_GRAPH` it draws per-function call and caller graphs, and it renders class usage relations through member variables — if class A has a member `m_a` of type B, A gets an arrow to B labelled `m_a` ([Doxygen: Graphs and diagrams](https://www.doxygen.nl/manual/diagrams.html), [Configuration](https://www.doxygen.nl/manual/config.html)). Known gaps: library function calls are not shown in call graphs, and static functions are not linked without `EXTRACT_STATIC` ([doxygen#2071](https://github.com/doxygen/doxygen/issues/2071)).

**Python-specific call graph reality check.** PyCG computes assignment relations between identifiers of functions, variables, classes and modules via interprocedural analysis, reporting **~99.2% precision and ~69.9% recall** at ~0.38s per 1k LoC ([Salis et al., *PyCG: Practical Call Graph Generation in Python*, ICSE 2021, arXiv:2103.00587](https://arxiv.org/abs/2103.00587)). Read the recall figure as the ceiling on "how complete can a static Python call/assignment graph be" — roughly 30% of real call edges are missed by a state-of-the-art static analyser.

### 1b. Concept layer (the idea behind the code)

**Documentation-generator lineage (Javadoc / Doxygen / Sphinx autodoc).** Forty years of tooling establishes that *attaching* a comment or docstring to the declaration it documents is a fully mechanical, deterministic operation. Doxygen's `EXTRACT_ALL`, `HIDE_UNDOC_MEMBERS` and `WARN_IF_UNDOCUMENTED` switches exist precisely because the interesting variable is not whether extraction works but whether the human wrote anything ([Doxygen configuration](https://www.doxygen.nl/manual/config.html)). Glean likewise stores docstrings as facts and Meta's code browser generates documentation on the fly from them (Meta Engineering, ibid.).

**Feature location.** The systematic survey covers 89 articles across 25 venues and taxonomises techniques as dynamic (execution traces), static (structure), textual/IR (vocabulary), and hybrid ([Dit, Revelle, Gethers & Poshyvanyk, *Feature location in source code: a taxonomy and survey*, JSEP 2013](https://www.cs.wm.edu/~denys/pubs/JSME-FL-SurveyCRCV1.pdf)). Textual approaches rest on the premise that **identifiers and comments encode domain knowledge**, using pattern matching, IR and NLP (ibid.) — this is the academic form of the "flipping comments" hypothesis, and the survey names its two standing failure modes: **vocabulary mismatch** (the feature description uses terms absent from the code) and **poor identifier quality** (abbreviated or cryptic names), with sparse comments degrading performance substantially. Output granularity varies by technique from statement to method to class; no universally superior technique emerged, and hybrids generally beat single-strategy methods (ibid.).

**Concern graphs.** The classic representation of "concepts over code": a concern is anything a stakeholder may want to consider as a conceptual unit — features, non-functional requirements, design idioms — and a concern graph abstracts the implementation detail while making the relationships between the concern's parts explicit, with a cheap mapping back to source ([Robillard & Murphy, *Concern Graphs*, ICSE 2002](https://dl.acm.org/doi/abs/10.1145/581339.581390); [*Representing concerns in source code*, TOSEM 2007](https://dl.acm.org/doi/10.1145/1189748.1189751)). The decisive detail for us: the FEAT tool lets **developers iteratively build** concern graphs while investigating source, and the evaluated claim is that they are *inexpensive to create during program investigation* and robust across versions — not that they are derived. The most-cited academic realisation of a concept layer is human-curated with structural-dependency assistance.

**LLM repo mapping.** Aider parses with tree-sitter to find where "functions, classes, variables, types and other definitions occur" plus their references, using per-language `*-tags.scm` queries emitting `def`/`ref` tags, then ranks with a graph algorithm over a file-level dependency graph and fills a token budget in rank order ([Building a better repository map with tree sitter](https://aider.chat/2023/10/22/repomap.html)). Note what it actually ships: it "only includes the most important identifiers" and focuses on top-level definitions rather than all variables (ibid.). This is a *relevance* map, not a semantic one.

**LLM codebase wikis.** DeepWiki (Cognition) clones a repository, analyses structure, and generates wiki documentation with Mermaid architecture diagrams and source links ([Devin docs](https://docs.devin.ai/work-with-devin/deepwiki)). CodeWiki is the academic counterpart: hierarchical decomposition with specialised agents that map the repository, document modules and synthesise system-wide docs across seven languages, evaluated by CodeWikiBench with rubrics derived from human-written docs. Its two reported findings matter here: traditional NLP metrics (BLEU/ROUGE) are inadequate for documentation quality, and grounding generation in a structural code graph is what reduces hallucination. Scores: 68.79% quality with proprietary models vs 64.06% for DeepWiki ([*CodeWiki*, arXiv:2510.24428](https://arxiv.org/abs/2510.24428)).

**How reliable is model-generated concept text?** In a human-subject study, humans judged LLM-generated code summaries worse than developer-written ones at explaining a method's role **46.3% of the time**, and in a follow-up 70–80% of the time LLMs produced summaries humans did not find acceptably similar to human summaries ([*Calibration of Large Language Models on Code Summarization*, PACMSE 2025 / arXiv:2404.19318](https://arxiv.org/html/2404.19318)).

---

## 2. Per-approach verdicts

Sourced facts are in §1; this section is *this excursion's judgement* about fit, and should be read as opinion resting on those facts.

| Approach | Node granularity | Call modelling | Python | C++ | Incremental | Adoption cost |
|---|---|---|---|---|---|---|
| PDG/SDG (classical) | statement + variable-at-point | context-sensitive via linkage structure | via implementations | via implementations | no | high (theory to implement) |
| Joern / CPG | `LOCAL`, `MEMBER`, `IDENTIFIER` + `METHOD` | direct `CALL` edges **and** `REACHING_DEF` data mediation | `pysrc2cpg`, rough edges | `c2cpg` | no (rebuild CPG) | medium (JVM, own query language) |
| Kythe | `variable` (local / parameter / field) + functions | `ref/call`; `influences` experimental | weak by design | yes | not documented | high (needs compilation DB) |
| SCIP | symbols incl. `local <id>`; `ReadAccess`/`WriteAccess` roles | **none** | `scip-python` | `scip-clang` (beta) | **no** — full-project only | **low** (two CLIs + protobuf) |
| Stack graphs | name bindings | none | grammar-dependent | grammar-dependent | **yes, file-level** | medium (Rust lib, per-language rules) |
| tree-sitter | syntax nodes | none | yes | yes | **yes, edit-level** | **very low** |
| LSP | declarations | call hierarchy, no dynamic calls | pyright/jedi | clangd | server-managed | low, but server-dependent |
| CodeQL | full AST + **SSA variables** + dataflow nodes | local + global dataflow | yes | yes (build tracing) | recent (2026, C/C++ & Go) | medium-high (build integration, QL) |
| Glean | declaration-level facts | via language schemas | yes | yes | **yes, stacked DBs + fanout** | high (server, schemas, indexers) |
| Doxygen | declarations + member-variable usage arrows | call/caller graphs, no library calls | limited | native | no | very low |

Reading of the table:

- **The cheapest thing that actually produces our edge type is SCIP.** `ReadAccess`/`WriteAccess` occurrence roles against a resolved symbol, restricted to a source range, *is* a container↔transformer read/write edge — and both languages we care about have an indexer. It is the only low-adoption-cost option in the survey that emits read/write directionality rather than undifferentiated references. Its two costs are real: no call edges (recover those from LSP call hierarchy or from occurrence-in-range), and no incrementality (full-project reindex per derivation).
- **Joern/CPG is the only one that gives the whole model in one artifact** — containers, transformers, direct calls, and variable-level data dependence with the variable named on the edge. It is also the heaviest, has no incrementality story, and its Python frontend is the weakest link.
- **CodeQL is the strongest *analysis*, the worst *map*.** SSA-variable dataflow with both languages covered and newly-shipped incrementality; but the derivation would run through a build and a query language, and the natural output is answers to questions rather than a stable set of nodes with identity.
- **Stack graphs are the only file-incremental semantic option**, and they resolve names only. If incrementality dominates and the container/transformer edges can be recovered from occurrences, stack graphs plus tree-sitter is the architecturally-honest cheap stack — at the cost of implementing per-language rules.
- **Glean's design is the closest match to the storage model in the brief**, independent of whether it is adopted: derived predicates that are either materialised or computed on the fly is exactly "collapsed views are projections computed on demand," and stacked immutable layers with query-computed fanout is exactly "a code change forces supersession: re-derive, diff, update." Worth reading as a design precedent even if the operational cost rules it out for a small project.
- **Doxygen and LSP are not derivation substrates**, but both are useful cross-checks — Doxygen's member-variable usage arrows and LSP's call hierarchy are cheap second opinions on edges derived elsewhere.
- **The LLM repo-map lineage does not compete on the architectural layer.** Aider's map is a token-budgeted relevance ranking of top-level definitions; it deliberately drops variables. Nothing about it produces stable node identity.

---

## 3. Derivation pipeline sketch, with the deterministic line drawn

Plausibility sketch only, as instructed — not a design.

```
                    ┌──────────────── DETERMINISTIC (no model call) ────────────────┐
source tree ──▶ parse (tree-sitter)           ── syntax, ranges, incremental on edit
            ──▶ resolve (scip-python / scip-clang)
                     ├─ symbols with stable string IDs      ──▶ TRANSFORMER nodes (Method/Term at callable scope)
                     ├─ symbols at module/class/field scope ──▶ CONTAINER nodes
                     └─ occurrences × SymbolRole            ──▶ CONTAINER↔TRANSFORMER edges
                                                                 (WriteAccess ⇒ transformer writes container,
                                                                  ReadAccess  ⇒ transformer reads container,
                                                                  attributed by enclosing transformer range)
            ──▶ calls (LSP call hierarchy, or occurrence-of-a-Method-symbol-in-range)
                                                             ──▶ derived, not stored (projection)
            ──▶ attach doc (the comment/docstring lexically attached to a declaration)
                                                             ──▶ CONCEPT CANDIDATE, verbatim, with provenance
                    └────────────────────────────────────────────────────────────────┘
                    ┌──────────────── NEEDS JUDGEMENT (model or human) ─────────────┐
                    │  name a concept that has no comment                           │
                    │  merge two candidates into one concept                        │
                    │  attach one concept to N transformers/containers (scattering)  │
                    │  decide a surviving comment still describes changed code       │
                    └────────────────────────────────────────────────────────────────┘

diff loop: per-node content hash (symbol ID + defining range text + attached doc text).
           changed range ⇒ node superseded ⇒ re-derive that node,
           plus fanout (Glean's lesson: dependents of a changed C++ header must be reprocessed).
```

The line is sharp and it falls in an unintuitive place. Everything on the architectural layer is deterministic. Everything about *concept identity* is not. The comment text itself crosses cleanly — extracting it is deterministic — but the moment you ask "what concept is this," you are on the other side.

### Testing "the concept side is just flipping comments"

Verdict: **partly true, load-bearing where true, and insufficient as the whole layer.** Three separate objections, each with evidence.

**(a) The mechanical part genuinely is free.** Attaching a comment to the declaration it documents is deterministic and has forty years of tooling behind it (Javadoc/Doxygen/Sphinx; Glean stores docstrings as facts). Where a docstring exists, a concept candidate costs zero model calls. Keep this — it is the strongest part of the hypothesis and it should not be given up because of the objections below.

**(b) Coverage kills it as a complete source — this is the strongest counter-evidence.** Across 5,229 open-source projects, average comment density is **18.67%**, stable regardless of team or project size ([Arafat & Riehle, *The comment density of open source software code*, ICSE NIER 2009](https://dirkriehle.com/wp-content/uploads/2009/02/icse-2009-nier-for-web.pdf)). The comment-quality literature reports comment **incompleteness between 60% and 75%** — on average nearly three quarters of public code entities carry no comment — and one Java study found **77% of 33k+ methods have no header comment** (both figures reached here through secondary summaries in the search results rather than the primary PDFs; treat the exact numbers as approximate, the order of magnitude as solid). Whatever the precise figure, the majority of transformers in a typical codebase have no comment to flip. A comments-only concept layer is a concept layer with holes over most of the code.

**(c) Staleness is real but weaker than folklore suggests.** Fluri et al. found that 23%, 52% and 43% of comment changes in ArgoUML, Azureus and JDT Core respectively were driven by source changes, and that in **97%** of those cases the comment change landed in the *same revision* as the code change; a follow-up across eight systems found code and comments co-evolved in **90%** of cases in six of the eight ([Fluri et al., *Do code and comments co-evolve?* / analysing co-evolution, WCRE 2007 and follow-up, as reported in Wen et al. 2019](https://www.inf.usi.ch/lanza/Downloads/Wen2019a.pdf)). So when a comment is touched, it is usually touched with the code. The consistent negative finding across both studies is different and more damaging: **newly added code is scarcely commented**. That reinforces (b) rather than (c) — the failure mode is absence, not rot. The largest study to date mined 1.3 billion AST-level changes across 1,500 systems and manually analysed 500 commits to build a taxonomy of code-comment inconsistencies developers fix ([Wen, Nagy, Bavota & Lanza, ICPC 2019](https://dl.acm.org/doi/abs/10.1109/ICPC.2019.00019)); its specific percentages could not be retrieved in this pass (see nulls).

**(d) Level mismatch — the objection the hypothesis has no answer to.** A comment attaches to *one* declaration. A concept in the model being built spans several. Getting from per-declaration comments to a concept node covering N transformers is exactly the concern-location / feature-location problem, and the survey literature says textual approaches to it fail on vocabulary mismatch and poor identifier quality, with no universally superior technique ([Dit et al. 2013](https://www.cs.wm.edu/~denys/pubs/JSME-FL-SurveyCRCV1.pdf)) — while the canonical concept-over-code representation, concern graphs, was built *by developers* with tool support, not derived ([Robillard & Murphy](https://dl.acm.org/doi/10.1145/1189748.1189751)).

**(e) Filling the gaps with a model is possible but not free.** The gap is exactly what LLM wiki generators target, and grounding generation in a structural code graph measurably reduces hallucination ([CodeWiki, arXiv:2510.24428](https://arxiv.org/abs/2510.24428)) — a direct argument for deriving the architectural layer *first* and conditioning concept generation on it. But the quality ceiling is visible: humans judged LLM summaries worse than developer-written ones 46.3% of the time ([arXiv:2404.19318](https://arxiv.org/html/2404.19318)). Model-named concepts should be stored as human-confirmable statements with provenance, not silently re-derived — which is what the atomic-statements-in-git storage model already affords.

Net: comments → concept *candidates*, deterministically and for free, covering perhaps a quarter to a third of declarations. Concept *identity* — naming, merging, spanning — needs judgement, and needs to survive re-derivation rather than being recomputed each time.

---

## 4. The granularity finding (called out separately)

**The mature tools did not converge on a single granularity. They split, and the split is not where you would expect.**

The dividing line is not "variables vs functions." It is **whether a name has to survive crossing a file boundary**:

- Tools built for **navigation at scale** — Kythe, SCIP, stack graphs, LSP, Glean — settle on the **named, resolvable declaration**. Kythe has a `variable` node kind, but a *semantic* one reached through name resolution. SCIP represents locals only as `local <id>` symbols that MUST NOT be referenced outside their Document. Stack graphs resolve names and stop. Glean's facts are declaration-level. These tools are cross-file, cross-repo, and cheap to keep current.
- Tools built for **reasoning about execution** — PDG/SDG, Joern's CPG, CodeQL — go all the way down to the **variable at a program point** (`REACHING_DEF` carrying a `VARIABLE` property; `SsaDefinitionNode` as an SSA variable). They pay for it with build integration and, mostly, no incrementality.

The reason for the split is legible in the artifacts. Cross-file variable-level tracking requires interprocedural dataflow, which requires calling-context precision — the exact problem the SDG was invented to solve ([Horwitz et al. 1990](https://research.cs.wisc.edu/wpis/papers/toplas90.pdf)) — and that is what makes incrementality hard, because a local edit's effects propagate. CodeQL draws the same line internally and states the tradeoff plainly: local dataflow (within one callable) is "easier, faster, and more precise"; global dataflow is more powerful and costlier ([CodeQL docs](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/)). SCIP encodes the same boundary in its data model: a symbol either has a package-qualified global identity or it is `local <id>` and confined to its Document.

**What this feeds into the containers-as-every-variable vs durable-state-at-boundaries thread** (this excursion's reading, not a finding):

The ecosystem has independently discovered, several times, that *named state crossing a file boundary* and *every variable* are two different objects with two different cost structures. Every scalable tool treats the first as a durable node with stable identity, and the second as something derived within a procedure when someone asks. That is an argument for durable state at boundaries as the stored container, with per-function locals available on demand from a local-dataflow pass — and it comes with a bonus: SCIP's `local <id>` form and CodeQL's local-vs-global split both give a ready-made, tool-supported way to *express* the distinction rather than having to invent one. The counter-consideration is that the split was driven by cross-repo scale, which a small project does not have; the cost argument is weaker here than it was for Google, GitHub and Meta, and adopting the boundary should rest on whether every-variable nodes are *useful* in a navigation map, not on whether they are affordable.

---

## Scoped nulls — what was searched and what was not

Negative findings from this pass, each scoped to what was actually looked at:

- **No surveyed tool derives the concept layer.** Searched: doc-generator lineage, feature-location and concern-mining literature, LLM repo maps and wiki generators. Every artifact found either extracts author-written text mechanically (doc generators, Glean docstring facts), or requires a human to build the concern representation (FEAT/concern graphs), or generates prose with a model at measurable error rates (DeepWiki, CodeWiki). This kills "an off-the-shelf tool will hand us concept nodes" for the tools surveyed; it says nothing about whether a project-specific derivation can work.
- **No surveyed tool combines variable-level containers, incrementality, and low adoption cost.** The three exist pairwise, never all three. Not a claim that the combination is impossible — SCIP + stack graphs is an untested pairing that plausibly gets close, and SCIP incrementality is on Sourcegraph's roadmap.
- **Could not retrieve** the specific percentages from Wen et al. ICPC 2019 (the USI PDF returned 404, the ACM DL page returned 403) or the full text of Rani et al.'s *A Decade of Code Comment Quality Assessment* (PDF fetched as binary, unreadable). The Fluri co-evolution numbers and the 60–75% incompleteness figure reached this report through secondary summaries in search results, not the primary papers. The comment-density figure (18.67%, 5,229 projects) is from the primary ICSE NIER 2009 PDF.
- **Not surveyed at all** (out of budget, not judged irrelevant): SciTools Understand, Sourcetrail, Lattix, Structure101 and other commercial architecture tools; srcML; LLVM/Clang IR-level frameworks (SVF, PhASAR, the Clang Static Analyzer); Soot/WALA; Infer; Semgrep; ctags/GNU Global; Eclipse JDT/CDT indexes; LSIF in its own right beyond its supersession by SCIP; the primary LDA/LSI topic-mining-on-identifiers papers (reached only through the Dit et al. survey); GraphRAG-style code knowledge-graph systems beyond DeepWiki and CodeWiki; and any hands-on evaluation whatsoever — per the brief, nothing was installed or run, so every claim about robustness, output shape or cost is documentary.

---

## Sources

- [Yamaguchi et al., *Modeling and Discovering Vulnerabilities with Code Property Graphs*, IEEE S&P 2014](https://www.researchgate.net/publication/263658395_Modeling_and_Discovering_Vulnerabilities_with_Code_Property_Graphs)
- [Code Property Graph specification](https://cpg.joern.io/) · [Joern](https://github.com/joernio/joern) · [Joern frontends](https://docs.joern.io/frontends/) · [Joern Python frontend](https://docs.joern.io/frontends/python/) · [joern#2269](https://github.com/joernio/joern/issues/2269)
- [Kythe schema reference](https://kythe.io/docs/schema/) · [Kythe schema overview](https://kythe.io/docs/schema-overview.html) · [Kythe callgraphs](https://kythe.io/docs/schema/callgraph.html) · [Writing a new indexer](https://kythe.io/docs/schema/writing-an-indexer.html) · [Kythe compilation database spec](https://kythe.io/docs/kythe-compilation-database.html) · [kythe/kythe](https://github.com/kythe/kythe)
- [scip.proto](https://github.com/sourcegraph/scip/blob/main/scip.proto) · [SCIP announcement](https://sourcegraph.com/blog/announcing-scip) · [scip-clang announcement](https://sourcegraph.com/blog/announcing-scip-clang) · [scip-python](https://github.com/sourcegraph/scip-python) · [SCIP indexers](https://scip-code.org/)
- [Creager & Hendrickson, *Stack graphs: Name resolution at scale*, arXiv:2211.01224 / EVCS 2023](https://arxiv.org/abs/2211.01224) · [Introducing stack graphs (GitHub Blog)](https://github.blog/open-source/introducing-stack-graphs/) · [github/stack-graphs](https://github.com/github/stack-graphs)
- [tree-sitter documentation](https://tree-sitter.github.io/tree-sitter/) · [Why tree-sitter (github/semantic)](https://github.com/github/semantic/blob/main/docs/why-tree-sitter.md) · [Cubix: tree-sitter limitations](https://www.cubix-framework.com/tree-sitter-limitations.html)
- [gopls navigation features (LSP call hierarchy)](https://go.dev/gopls/features/navigation) · [claude-code#38683 (server-side prepareCallHierarchy gaps)](https://github.com/anthropics/claude-code/issues/38683)
- [CodeQL: about data flow analysis](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/) · [C/C++ data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-cpp/) · [Python DataFlowPublic Node](https://codeql.github.com/codeql-standard-libraries/python/semmle/python/dataflow/new/internal/DataFlowPublic.qll/type.DataFlowPublic$Node.html) · [codeql database create](https://docs.github.com/en/code-security/codeql-cli/codeql-cli-manual/database-create) · [Incremental analysis changelog, 2026-06-10](https://github.blog/changelog/2026-06-10-incremental-analysis-for-go-c-c-and-codeql-cli/)
- [Indexing code at scale with Glean (Meta Engineering)](https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/) · [Glean derived predicates](https://glean.software/docs/derived/) · [Incremental indexing with Glean](https://glean.software/blog/incremental/)
- [Horwitz, Reps & Binkley, *Interprocedural Slicing Using Dependence Graphs*, TOPLAS 1990](https://research.cs.wisc.edu/wpis/papers/toplas90.pdf)
- [Salis et al., *PyCG: Practical Call Graph Generation in Python*, ICSE 2021](https://arxiv.org/abs/2103.00587)
- [Doxygen: Graphs and diagrams](https://www.doxygen.nl/manual/diagrams.html) · [Doxygen configuration](https://www.doxygen.nl/manual/config.html) · [doxygen#2071](https://github.com/doxygen/doxygen/issues/2071)
- [Dit, Revelle, Gethers & Poshyvanyk, *Feature location in source code: a taxonomy and survey*, JSEP 2013](https://www.cs.wm.edu/~denys/pubs/JSME-FL-SurveyCRCV1.pdf)
- [Robillard & Murphy, *Concern Graphs*, ICSE 2002](https://dl.acm.org/doi/abs/10.1145/581339.581390) · [*Representing concerns in source code*, TOSEM 2007](https://dl.acm.org/doi/10.1145/1189748.1189751)
- [Arafat & Riehle, *The comment density of open source software code*, ICSE NIER 2009](https://dirkriehle.com/wp-content/uploads/2009/02/icse-2009-nier-for-web.pdf)
- [Wen, Nagy, Bavota & Lanza, *A Large-Scale Empirical Study on Code-Comment Inconsistencies*, ICPC 2019](https://dl.acm.org/doi/abs/10.1109/ICPC.2019.00019)
- [*CodeWiki: Evaluating AI's Ability to Generate Holistic Documentation for Large-Scale Codebases*, arXiv:2510.24428](https://arxiv.org/abs/2510.24428) · [DeepWiki (Devin docs)](https://docs.devin.ai/work-with-devin/deepwiki)
- [*Calibration of Large Language Models on Code Summarization*, arXiv:2404.19318 / PACMSE 2025](https://arxiv.org/html/2404.19318)
- [Building a better repository map with tree sitter (aider)](https://aider.chat/2023/10/22/repomap.html)
