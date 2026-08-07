# x2 result: prior art — a concept layer derived alongside the structural layer

Excursion type: research. `explore-code-map`. One focused pass, reading and citing only — nothing installed or run.

Companion to the parent exploration's `x5-result.md` (SCIP/Kythe/Glean/Joern/CodeQL extraction, comment-density statistics, feature-location's no-superior-technique result, CodeWiki's structural-grounding finding, concern graphs being developer-built). Where x5 already settled a point, this report cites it rather than re-deriving it.

**Provenance convention used below:** claims marked *(primary)* came from fetching the paper, project doc or repo directly; claims marked *(secondary)* reached this report through a search-result summary and the primary source was not retrieved. Treat secondary claims as leads with a citation, not as settled numbers.

---

## Direct answer to the one question

**Yes — one system does almost exactly this, and it is nine months old.** [RepoDoc (arXiv:2604.26523)](https://arxiv.org/html/2604.26523v1) builds a single graph, RepoKG, whose node types are **Code Entity** (functions, classes, interfaces, modules), **Concept Entity** (business concepts, identified by an LLM) and **Doc Entity** (markdown documentation), joined by seven relation types: the structural ones (`calls`, `implements`, `extends`, `imports`, `contains`) plus two semantic ones — `semantic-impact`, linking code to concepts, and `describes`, linking documentation to code. Construction is three sequential steps in one pipeline: AST extraction of code entities, then structural relation extraction, then LLM semantic enrichment. The paper's own framing is that this is "an integrated semantic backbone rather than separate layers." *(primary)*

**What it teaches about the procedural/judgment split** — and this is the load-bearing part, because RepoDoc's split is drawn in exactly the same place as every other system in this survey:

| Procedural (no model call) | Judgment (model or human) |
|---|---|
| AST parsing, structural relation extraction | Concept entity creation |
| Git diff → which entities changed | Module clustering decisions |
| Bidirectional graph traversal to find affected entities | Documentation prose generation |
| Topological sort for update ordering | Validation of the result |

*(primary)*

Two of its measured numbers bound the judgment side usefully. RepoDoc's incremental update path — the procedural part, driven by graph traversal from a git diff — reports **97% update recall vs RepoAgent's 80%**, with 73% less time and 77% fewer tokens. But its **API coverage is 53.13%** (against CodeWiki's 40.09%): even the system that wins this benchmark leaves roughly half the API surface undocumented. *(primary)* That is the same shape as x5's coverage finding, arrived at from the opposite direction — x5 found ~60–75% of entities have no comment to harvest; RepoDoc finds that the best generator covers ~53% of the API. **Knowing which node changed is close to solved. Saying what a node means is not, and the gap is roughly half the codebase in both directions.**

The pre-LLM answer to the same question is worth more than RepoDoc for design purposes, because it is thirty years old and has held up: **software reflexion models** ([Murphy, Notkin & Sullivan, FSE 1995](https://dl.acm.org/doi/10.1145/222132.222136); ACM SIGSOFT Retrospective Impact Paper Award 2011). The engineer supplies two things — a high-level model and a *mapping* from it to the source — and the tool computes, procedurally, where the source agrees with the model (convergence), contradicts it (divergence), and where the model claims something the source does not have (absence). An engineer produced several reflexion models of the NetBSD virtual-memory subsystem (250 KLOC of C) "in only a few hours." *(primary — but note the gap: the paper reports time to compute models once the mapping exists, not time to build the mapping.)*

The reflexion lineage is the cleanest statement of the split anywhere in this survey: **the concept layer is an input, not an output; what is derived is the relation between the concept layer and the structure.** RepoDoc, thirty years later, moves concept-naming from the human to a model but leaves the architecture identical — concepts attach to structure, and the traversal between them is procedural.

---

## Target 1 — combined structural + concept systems

### 1.1 RepoDoc and the LLM knowledge-graph documentation line (2024–2026)

RepoDoc's numbers, all self-reported in a single unreplicated paper and partly LLM-judged, against [CodeWiki](https://arxiv.org/abs/2510.24428) and [RepoAgent](https://arxiv.org/abs/2402.16667): *(primary)*

- Completeness: API coverage 53.13% vs CodeWiki 40.09%; Completeness@K 74.12% vs 67.16%; 5.3× more words, 4.2× more cross-references.
- Quality (rubric scores, 10-point): clarity 8.25 vs 7.00, conciseness 7.40 vs 6.10, structure 8.05 vs 7.20.
- Efficiency: 1,242s vs CodeWiki's 3,673s; 780K vs 5,311K tokens; 73× faster than RepoAgent.
- Incremental update vs RepoAgent: 73% less time, 77% fewer tokens, update recall 97% vs 80%.

Caveats worth carrying: the quality deltas are ~1 point on a 10-point rubric between two LLM pipelines, and x5 already recorded CodeWiki's own finding that BLEU/ROUGE-style metrics are inadequate for documentation quality — so these rubric scores are the field's least-bad instrument, not a trustworthy one. The paper does not say where documentation is written to disk (see §3.4).

The surrounding 2025–2026 cluster is large and converging on the same idea — a structural graph as the retrieval substrate for LLM reasoning about code. Named in search but not read in this pass: CodexGraph (NAACL 2025), RepoGraph (ICLR 2025, reported +32.8% relative on SWE-bench), LocAgent (ACL 2025), Code Graph Model, [Codebase-Memory (arXiv:2603.27277)](https://arxiv.org/pdf/2603.27277), [LARGER (arXiv:2605.16352)](https://arxiv.org/pdf/2605.16352). *(secondary)* One that was fetched: [Citation-Grounded Code Comprehension (arXiv:2512.12117)](https://arxiv.org/pdf/2512.12117) explicitly separates a **structural layer** (dependency graph) from a **conceptual layer** (documentation and citations) and requires explanations to cite actual code elements rather than rely on model inference — the citation-provenance discipline, applied to code explanation. Quantitative results were not extractable from the fetched PDF. *(primary for architecture, null for numbers.)*

### 1.2 The oldest working answer: Doxygen's grouping commands

This is the finding most likely to be underrated, because Doxygen is filed mentally as "a doc generator." x5's objection **(d)** was *level mismatch* — a comment attaches to one declaration, a concept spans several — and noted the hypothesis has no answer to it. Doxygen has shipped an answer for twenty years.

`\defgroup` defines a named group with a title; `\ingroup` assigns an entity to it; `\addtogroup` and `\weakgroup` extend one without redefining it; and the markers `@{` / `@}` let one group annotation **"span multiple declarations"** in a single block. Doxygen resolves conflicting membership by a fixed priority (`\ingroup` > `\defgroup` > `\addtogroup` > `\weakgroup`) and generates a separate documentation page per group automatically; `\subpage` builds page hierarchy without the author constructing it. ([Doxygen: Grouping](https://www.doxygen.nl/manual/grouping.html)) *(primary)*

The split, again in the same place: **the author writes group membership and the group's prose; Doxygen procedurally resolves the hierarchy, collects members, and renders.** And note where the concept layer lives — inside source comments, spanning N declarations, versioned with the code. That makes Doxygen groups simultaneously a precedent for §1 (concept layer beside structure) and for §3 (write-back into source).

x5 already covered Doxygen's *structural* half — `CALL_GRAPH`/`CALLER_GRAPH` and member-variable usage arrows. Read together, Doxygen is the earliest system in this survey that emits both a structural index and a concept layer from one pass. Its concept layer just isn't *derived* — it's harvested from author annotations.

### 1.3 Architecture recovery: reflexion models and the clustering line

**Reflexion models** are covered in the direct answer. The design principle to extract: the human's model is allowed to be *wrong*, and the tool's output is the disagreement. Nothing else in this survey treats the concept layer as falsifiable against the structure.

**Clustering-based recovery** attacks the same target — a module-level concept structure — without a human model. The recurring five are ACDC (pattern-based), ARC (Architecture Recovery using Concerns), Bunch (search-based, optimizing TurboMQ), LIMBO (hierarchical, information-bottleneck) and WCA. *(secondary)* ARC is the one that matters here: it is the concern-bearing member of the family, i.e. clustering driven by semantic/topic information rather than dependency structure alone.

The state of the art is candid about accuracy. [SARIF (arXiv:2311.04643)](https://arxiv.org/abs/2311.04643) reports being **"36.1% more accurate than the best of the previous techniques on average"** across nine state-of-the-art techniques, and frames the motivating problem as architects having to "track the implementation-level changes and update the architectural documentation accordingly, which is time-consuming and error-prone." *(primary)* A 36% relative improvement over the prior best, published in 2023 on a problem worked since the 1990s, is a reasonable proxy for "this is not solved." The exact MoJoFM figures and the remaining gap to ground truth were not retrievable in this pass (see nulls).

**Moose / FAMIX** is the platform lineage. FAMIX is a language-independent metamodel of source entities — `Method`, `Attribute`, `Access` and so on — with Moose as the reengineering environment on top, now [Modular Moose (arXiv:2011.10975)](https://arxiv.org/pdf/2011.10975) with a modular, extensible metamodel. Directly relevant: **Hapax**, a Moose tool that uses "the comments and names of the identifiers from the code to recover the domain information" — the concept layer derived from the same artifact the structural layer comes from. *(secondary)* This is the academic realisation of x5's "flipping comments" hypothesis, in a platform that already holds the structural model — and it lands in the family x5's feature-location survey judged to have no universally superior technique, with vocabulary mismatch and poor identifier quality as standing failure modes.

### 1.4 Commercial tools: mostly a graveyard, and none derived concepts

- **Sourcetrail** — interactive source explorer, indexes C/C++/Java/Python, graph focused on the selected symbol showing incoming and outgoing dependencies. **No longer maintained.** ([Sourcetrail docs](https://github.com/CoatiSoftware/Sourcetrail/blob/master/DOCUMENTATION.md)) *(secondary)* Its indexer survives as the substrate for Quarkslab's Numbat/Pyrrha.
- **SciTools Understand** — actively maintained, commercial, 70+ languages; ships Call/Called-by, Butterfly, Object References, Control Flow, UML class and sequence, Data Flow, Dependency and Declaration graphs. ([SciTools: Graphs](https://scitools.com/graphs)) *(secondary)*
- **CodeSee** — automated codebase maps and review maps; **acquired by GitKraken and sunset as a standalone product in 2024**, no longer available to new users. *(secondary)*

**The finding here is the mortality rate, not the feature lists.** Two of the three most-cited commercial "map your codebase" products are dead, and the survivor sells static analysis and metrics rather than a concept layer. Every one of them visualises structure that a tool can extract; none derives what the code *means*. A design that assumes the concept layer is the hard, valuable part is consistent with which products survived.

---

## Target 2 — hole-driven prioritization

This target has a real, named literature: **prioritizing documentation effort**. It is small, it is contradictory, and it directly answers "which undocumented entities need descriptions first."

### 2.1 Hole *detection* is fully procedural and shipping

`interrogate` reports which methods, functions, classes and modules have docstrings and which do not, and is designed to run as a CI/CD gate on newly-added code ([interrogate docs](https://interrogate.readthedocs.io/)). `docstr-coverage` reports per-file and whole-project coverage and lists the missing ones ([docstr_coverage](https://github.com/HunterMcGushion/docstr_coverage)). `sphinx.ext.coverage` does the same inside Sphinx. *(secondary, but these are tool docs and the behaviour is uncontroversial.)*

One detail is worth stealing outright: `docstr-coverage` supports `# docstr-coverage:excused` and `# docstr-coverage:inherited` comments placed above a definition to exclude it from coverage. *(secondary)* That is a **human judgment about a hole, stored in the source next to the hole, versioned with it** — the cheapest possible write-back, and it exists because "this entity does not need documenting" is a judgment no coverage tool can make.

### 2.2 The prioritization literature, and its central disagreement

Four positions, and they do not agree:

**(a) Structural attributes are poor predictors; text is good.** [McBurney, Jiang et al., *Towards Prioritizing Documentation Effort*](https://repository.rit.edu/article/1887/) ran two user studies — open-source API libraries and closed-source industrial software at ABB — and concluded that **"static source code attributes are poor predictors of documentation effort priority, whereas textual analysis of source code consistently performed well as a predictor of documentation effort priority."** *(primary, abstract)*

**(b) A dependency-graph PageRank beats the supervised model.** [*Prioritizing documentation effort: Can we do better?* (arXiv:2006.10892)](https://arxiv.org/abs/2006.10892) proposes an unsupervised PageRank over module dependency relations as an alternative to the prior supervised artificial-neural-network approach, evaluated on the earlier small datasets plus six larger open-source ones, and concludes **"the PageRank approach is superior to the state-of-the-art ANN approach in prioritizing important modules for documentation effort,"** recommending it as the baseline future work should beat. *(primary, abstract)*

**(c) Refined centrality plus a complexity filter beats plain PageRank.** [Pride (IEEE TSE, 2022)](https://ieeexplore.ieee.org/document/9765699/) builds a weighted directed class coupling network, runs a PageRank-like algorithm over it, then applies complexity-metric filtering rules to drop unimportant classes and takes the top-k%. Nine systems; superior on average ranking by Friedman test. *(secondary)*

**(d) The empirical link between centrality and "worth documenting" exists, and it is by construction.** Zaidman & Demeyer's key-class work applies **HITS** — a webmining graph-ranking algorithm — to models built by static *and* dynamic analysis to find the classes with the most control in a system ([*Automatic identification of key classes in a software system using webmining techniques*, JSME 2008](https://onlinelibrary.wiley.com/doi/abs/10.1002/smr.370)). The decisive methodological detail: **Zaidman et al. defined "key classes" as the classes mentioned in the system's high-level documentation.** *(secondary)* So the entire key-class line is validated against *what humans actually chose to document* — which is precisely the empirical link this target asked for. Graph centrality predicts human documentation choices well enough that the field has used the latter as ground truth for the former for eighteen years.

**The contradiction, stated rather than smoothed.** (a) says structural metrics fail and text wins; (b), (c) and (d) say a purely structural graph ranking is the best-performing prioritizer known. These cannot both be read at face value. The most likely reconciliation — offered as a hypothesis, not a resolution, because the primary McBurney text beyond the abstract was not retrieved — is that **"static source code attributes" means per-entity attributional metrics (size, complexity, fan-out counts), whereas PageRank/HITS centrality is a relational property of the whole graph.** Those are different objects that both get called "static metrics." If that reconciliation holds, the design reading is: *rank holes by graph centrality, not by entity complexity, and use identifier/comment text as an independent second signal.* If it does not hold, one of these literatures is wrong and this survey cannot say which.

A fifth position exists and was not reachable: [EASE (TOSEM 2024)](https://dl.acm.org/doi/10.1145/3635714), an "effort-aware extension of unsupervised key class identification," whose title implies prior evaluations ignored the cost of documenting each candidate. ACM returned 403. *(null — see nulls.)*

---

## Target 3 — write-back

### 3.1 Literate programming does not write back; it inverts ownership

Knuth's WEB and its language-agnostic successor noweb are **one-way from a single source of truth**. The `.nw` file contains prose and code; `notangle` emits compilable source, `noweave` emits the document; both are generated artifacts ([noweb](https://github.com/nrnrnr/noweb); [Ramsey, *Literate Programming Using Noweb*](https://dl.acm.org/doi/fullHtml/10.5555/326984.326985)). *(secondary)* This is not a round trip — it is the opposite arrangement to the one in question. The prose file is primary and the code is derived, so the question "where do we store prose about code" never arises. The practical cost is well known and is why the model never became mainstream: debuggers, linters, IDEs and reviewers all see the generated file, not the source of truth.

### 3.2 org-babel is the genuine round trip, and its mechanism is the transferable lesson

Org-mode tangles code blocks out of an `.org` file, and **`M-x org-babel-detangle` propagates edits made in the tangled source file back into the original org document.** The enabling condition is explicit and is the whole trick: you must set `:comments link` (with `:padline` true), which makes Org **insert link comments into the generated code file pointing back at the org source**. ([Org manual: Extracting Source Code](https://orgmode.org/manual/Extracting-Source-Code.html); [ob-tangle detangle commit](https://code.orgmode.org/bzg/org-mode/commit/2152f1ec28dab77a3b8ee86ca012d19b1351882e)) *(secondary)*

**Lesson: write-back is possible exactly when the generated artifact carries provenance markers back to its source.** Detangle is not clever diffing — it is a pointer lookup made possible because tangling deliberately polluted the output with links. Any design that wants edited prose to flow back to a store needs the same thing: an identity marker on the emitted text, not a similarity match after the fact.

### 3.3 Anchoring research argues *against* writing into the file — with reasons

[Codetations (arXiv:2504.18702)](https://arxiv.org/html/2504.18702v1) is a VSCode annotation system that deliberately does **not** modify file content, and lists its reasons: embedded annotations clutter code and force teams to agree on acceptable clutter; they cannot work in formats without comment syntax (their example: JSON); they require write access to the annotated document; and edits can accidentally damage the annotation markers. Instead it uses a two-tier anchoring strategy — **cheap positional updates for online edits made through the editor, and LLM-based semantic re-anchoring for offline edits**, gated behind a user permission prompt because it is "slow, semantically correct, and potentially surprising." *(primary)*

On prior work, Codetations reports that Horvath et al.'s **Catseye** anchors by text comparison and "occasionally requires users to manually reattach annotations," because text comparison "lacks understanding of what text actually means." *(primary)* **No anchoring accuracy numbers are reported in either direction** — this literature argues from failure modes, not measurements.

This is a head-on contradiction with §3.2 and with Doxygen groups (§1.2), and it should not be smoothed. Org-babel's answer to anchoring is *put a marker in the file*; Codetations' answer is *never touch the file, and pay an LLM call when the anchor breaks*. The disagreement is about who owns the file: Codetations is designed for annotating code you may not have write access to and may not share conventions about. Where you *do* own the source and already have comment syntax — the case for a code map of your own repository — Doxygen groups and org-babel link comments are the precedents that work, and Codetations' objections mostly do not bind.

### 3.4 Systems that actually write prose into source

**Comment updating (the strongest write-back line).** CUP automates just-in-time comment updating: when a developer changes code, it suggests an updated comment, applied with one click ([Liu et al., *Automating Just-In-Time Comment Updating*, ASE 2020](https://yanmeng.github.io/papers/ASE20.pdf)). HebCUP does the same heuristically via token-level replacements on the old comment; HatCUP reports **+53.8% accuracy, +31.3% recall, +14.3% METEOR over CUP**; LLMCup reports **+49.0–116.9% accuracy over CUP and HebCUP**. The documented limit is sharp: **CUP and HebCUP handle simple code changes (modifying a single token) well and complex ones poorly.** *(secondary — the ASE 2020 primary PDF was located but its numbers here come from search summaries.)*

Read against x5's finding (c): x5 established that comments and code co-evolve in ~90% of cases and that the real failure mode is *absence*, not rot. This line confirms it from the tooling side — the automatable part of comment maintenance is the mechanical token-level rewrite, and everything past that degrades.

**Docstring insertion.** `pyment`, `PyMend` and `doc-writer` parse Python with the AST, generate docstring skeletons with parameters, returns and raises filled in, and either emit a patch or overwrite the source in place ([pyment](https://github.com/dadadel/pyment); [PyMend](https://github.com/JanEricNitschke/pymend)). *(secondary)* Visual Studio ships automatic doc-comment generation, now Copilot-backed, writing into the source at the cursor. *(secondary)* The split is the familiar one: **the skeleton is procedural and free; the sentence describing what the function is for is not.**

**And the leading LLM doc framework chose *not* to write back.** RepoAgent creates a `Markdown_Docs` folder at the repository root and stores documents there — **not** as docstrings in source. It integrates via a **git pre-commit hook** so each commit triggers detection of changes and regeneration of the affected documents, and exposes `repoagent diff` to preview what would be updated. ([OpenBMB/RepoAgent](https://github.com/OpenBMB/RepoAgent)) *(primary)* RepoDoc's paper does not state where its documentation lands on disk at all *(primary null)*.

So on write-back the field is genuinely split three ways: **into the source** (Doxygen groups, docstring inserters, CUP-family comment updaters, `docstr-coverage:excused`), **beside the source with a git hook** (RepoAgent), and **deliberately outside the source with semantic re-anchoring** (Codetations). No source found compares them empirically.

---

## Contradictions carried forward, not resolved

1. **Structural vs textual prioritization** (§2.2): McBurney says static source-code attributes are poor predictors and text wins; the PageRank/Pride/HITS line says structural centrality is the best-known prioritizer. Proposed reconciliation — attributional metrics ≠ relational centrality — is a hypothesis this pass could not verify.
2. **Markers in the file vs never touch the file** (§3.3): org-babel's detangle works *because* it writes provenance links into the generated code; Codetations refuses to write anything into the file and pays an LLM re-anchoring call instead. Both are reasoned positions; neither reports anchoring accuracy numbers.
3. **Coverage direction** (direct answer): x5 measured the hole from the harvest side (~60–75% of entities have no comment); RepoDoc measures it from the generation side (best system covers 53.13% of the API). Nothing found reconciles these into a single "how much of a codebase can carry a concept layer" figure.
4. **Whether an LLM concept layer is good enough** — RepoDoc's rubric scores are ~1 point better than CodeWiki's on 10-point scales judged partly by models, while x5's calibration study found humans judged LLM summaries worse than developer-written ones 46.3% of the time. The benchmarks say "improving"; the human study says "not acceptable yet." Both can be true and the survey cannot rank them.

---

## Scoped nulls — what was and was not searched

Each null kills *this search under these conditions*, not the idea.

**Sources attempted and failed to retrieve:**
- [EASE, TOSEM 2024](https://dl.acm.org/doi/10.1145/3635714) — ACM DL returned 403. The title implies a critique of prior key-class/documentation-prioritization evaluations for ignoring effort; that critique is unread and could weaken §2.2 (b) and (c).
- [Reengineering with Reflexion Models: A Case Study](https://www.cs.ubc.ca/~murphy/papers/rm/rm-case-study.pdf) — PDF fetched as unparseable binary. The Microsoft Excel case study's concrete numbers (mapping-entry counts, iteration counts, convergent/divergent/absent proportions, engineer time on the *mapping* rather than the computation) are therefore missing. This is the single most valuable unretrieved number set in the report, because it would quantify the human half of the reflexion split.
- [Zaidman & Demeyer JSME 2008 PDF](https://azaidman.github.io/publications/azaidmanJSME2008b.pdf) — unparseable binary. The precision/recall of HITS key-class identification is unretrieved; only the ground-truth definition (classes mentioned in high-level documentation) is carried, and that via a secondary summary.
- [SARIF (arXiv:2311.04643)](https://arxiv.org/abs/2311.04643) full text and [arXiv:2006.10892](https://arxiv.org/pdf/2006.10892) full text — abstracts only; MoJoFM figures and the ANN-vs-PageRank effect sizes are unretrieved.
- [Citation-Grounded Code Comprehension (arXiv:2512.12117)](https://arxiv.org/pdf/2512.12117) — architecture extracted, results tables not.
- ScienceDirect (403 twice) blocked the static-analysis key-class comparison and the *Prioritizing code documentation effort: can we do it simpler but better?* journal version.

**Named but not read** (surfaced in search, judged lower priority for the three targets): CodexGraph, RepoGraph, LocAgent, Code Graph Model, GraphCodeAgent, Codebase-Memory, LARGER, CodeCompass, ReCUBE; the ACDC/Bunch/LIMBO/ARC/WCA primaries and Garcia et al.'s comparative analysis; Hapax's own paper; Modular Moose beyond its abstract; the CUP/HatCUP/LLMCup primaries; Verifiable Literate Programming (arXiv:2607.02333, fetched but extraction was thin and unreliable — treat everything about it as unverified and it is therefore not cited in the body).

**Not searched at all:**
- **Databases**: no IEEE Xplore, ACM DL, Springer, ScienceDirect or Scopus full-text search — everything came through public web search plus arXiv/author-hosted PDFs. Paywalled venues where documentation and program-comprehension research primarily publishes (TSE, TOSEM, EMSE, ICSE/ICPC proceedings) are represented only by whatever leaked into open search results.
- **Languages/communities**: nothing in Japanese, Chinese or German-language SE literature; nothing from the Smalltalk/Pharo community's own forums where Moose actually lives; no Emacs/org-mode mailing-list archives beyond one commit page; no Rust (`missing_docs`, rustdoc's coverage output), Go (`go doc`, `revive` doc rules), Java (Javadoc doclint) or .NET doc-coverage tooling — target 2 was surveyed almost entirely through Python tooling.
- **Adjacent fields deliberately skipped**: ontology learning from text, knowledge-graph construction outside software, requirements traceability (which is arguably the same problem as concept-to-code mapping and was not touched), and the entire aspect-oriented / concern-separation literature past x5's concern-graph coverage.
- **Nothing was installed, run, or evaluated hands-on.** Every claim about behaviour, output shape, coverage or cost is documentary. In particular, no claim here about RepoDoc, RepoAgent, Codetations, interrogate or pyment has been checked against the running software.

---

## Sources

Combined structural + concept:
- [RepoDoc: A Knowledge Graph-Based Framework to Automatic Documentation Generation and Incremental Updates, arXiv:2604.26523](https://arxiv.org/html/2604.26523v1)
- [Murphy, Notkin & Sullivan, *Software Reflexion Models*, FSE 1995](https://dl.acm.org/doi/10.1145/222132.222136) · [author page](https://www.cs.ubc.ca/~murphy/papers/rm/fse95.html) · [SIGSOFT Impact Award 2011](https://news.cs.washington.edu/2011/09/10/gail-murphy-david-notkin-and-kevin-sullivan-win-acm-sigsoft-2011-retrospective-impact-paper-award/)
- [Doxygen: Grouping](https://www.doxygen.nl/manual/grouping.html)
- [SARIF: Software Architecture Recovery with Information Fusion, arXiv:2311.04643](https://arxiv.org/abs/2311.04643)
- [Modular Moose, arXiv:2011.10975](https://arxiv.org/pdf/2011.10975) · [The Moose Book](http://themoosebook.org/book/index.html)
- [Citation-Grounded Code Comprehension, arXiv:2512.12117](https://arxiv.org/pdf/2512.12117)
- [Sourcetrail documentation](https://github.com/CoatiSoftware/Sourcetrail/blob/master/DOCUMENTATION.md) · [SciTools Understand: Graphs](https://scitools.com/graphs) · [CodeSee codebase maps](https://www.codesee.io/codebase-maps)

Hole-driven prioritization:
- [McBurney, Jiang et al., *Towards Prioritizing Documentation Effort*](https://repository.rit.edu/article/1887/)
- [*Prioritizing documentation effort: Can we do better?*, arXiv:2006.10892](https://arxiv.org/abs/2006.10892)
- [Pride: Prioritizing Documentation Effort Based on a PageRank-Like Algorithm and Simple Filtering Rules, IEEE 2022](https://ieeexplore.ieee.org/document/9765699/)
- [Zaidman & Demeyer, *Automatic identification of key classes using webmining techniques*, JSME 2008](https://onlinelibrary.wiley.com/doi/abs/10.1002/smr.370)
- [EASE, TOSEM 2024](https://dl.acm.org/doi/10.1145/3635714) *(unread — 403)*
- [interrogate](https://interrogate.readthedocs.io/) · [docstr_coverage](https://github.com/HunterMcGushion/docstr_coverage) · [sphinx.ext.coverage](https://www.sphinx-doc.org/en/master/usage/extensions/coverage.html)

Write-back:
- [Org manual: Extracting Source Code](https://orgmode.org/manual/Extracting-Source-Code.html) · [ob-tangle detangle commit](https://code.orgmode.org/bzg/org-mode/commit/2152f1ec28dab77a3b8ee86ca012d19b1351882e) · [Introducing Babel](https://orgmode.org/worg/org-contrib/babel/intro.html)
- [noweb](https://github.com/nrnrnr/noweb) · [Ramsey, *Literate Programming Using Noweb*](https://dl.acm.org/doi/fullHtml/10.5555/326984.326985)
- [Codetations: Intelligent, Persistent Notes and UIs for Programs, arXiv:2504.18702](https://arxiv.org/html/2504.18702v1)
- [Liu et al., *Automating Just-In-Time Comment Updating*, ASE 2020](https://yanmeng.github.io/papers/ASE20.pdf) · [Just-In-Time Obsolete Comment Detection and Update, TSE](https://xin-xia.github.io/publication/tse221.pdf)
- [pyment](https://github.com/dadadel/pyment) · [PyMend](https://github.com/JanEricNitschke/pymend)
- [RepoAgent, arXiv:2402.16667](https://arxiv.org/abs/2402.16667) · [OpenBMB/RepoAgent](https://github.com/OpenBMB/RepoAgent)
- [CodeWiki, arXiv:2510.24428](https://arxiv.org/abs/2510.24428) *(cited via x5)*
