# x3 result: prior art — classifying code comments as typed assertions

Excursion type: research. `explore-code-map`. One focused pass, reading and citing only — nothing installed or run.

Companion to `x2-result.md` and the parent exploration's `x5-result.md`. Where those settled a point (comment density and coverage, combined structural+concept systems, write-back, hole prioritization), this report cites rather than re-derives. x3 is only about **classifying comment content**.

**Provenance convention:** *(primary)* = the paper, repo or tool doc was fetched and the numbers read out of it. *(secondary)* = the claim reached this report through a search summary only. Treat secondary claims as leads with a citation, not settled numbers.

---

## Direct answer

**The premise splits in two, and the two halves have opposite verdicts.**

**Half one — "every comment is an assertion of some sort." No one in this literature has framed it that way, and that is a genuine gap rather than a settled question.** Every published comment taxonomy classifies comments by *what the comment is about* (topic / information type: summary, usage, ownership, license, TODO) — not by *what kind of speech act it performs* (asserting, directing, promising, warning). Searle's five-way illocutionary taxonomy (assertive, directive, commissive, expressive, declaration) has been applied to developer Q&A conversations ([Detecting Speech Act Types in Developer Question/Answer Conversations, arXiv:1806.05130](https://arxiv.org/pdf/1806.05130)) and to tweets and political text, but a targeted search found **no study applying speech-act or assertion theory to source code comments**. *(scoped null — see nulls; searched three query formulations across arXiv, ACL Anthology and open web.)* So the assertion framing is not contradicted by prior art; it is simply absent from it. The nearest thing to an assertion-typed corpus is the contract-conventions line (Javadoc `@param`/`@return`/`@throws`, JML, Design-by-Contract), which *is* an assertion taxonomy — precondition, postcondition, exceptional condition — but one authors write explicitly rather than one derived from prose.

**Half two — "we should be able to easily categorize them." This is measurably false for the exact three categories the framing cares about, and measurably true for the ones it does not.** The decisive numbers come from the NLBSE tool competition, the only standardized, shared-task benchmark for this problem. On the NLBSE'25 baseline (SetFit, multi-label, sentence-level), per-category F1: *(primary)*

| Category | Baseline F1 | What it is |
|---|---|---|
| Java `Ownership` | **1.000** | author tags — literally `@author` |
| Pharo `Example` | 0.888 | code examples |
| Java `usage` | 0.862 | how to call it |
| Java `summary` | 0.851 | what it does |
| Python `DevelopmentNotes` | 0.325 | notes to future maintainers |
| Pharo `Classreferences` | 0.286 | references to other classes |
| **Java `rational`** | **0.209** | **why it is done this way** |

The ordering is not noise, and it is not fixed by better models. The best NLBSE'25 entrant lifted the average from 63.7 to 72.6 F1c and beat the baseline in 17 of 19 categories — but Java-Rationale only reached **31.1** and Java-Expand **50.2** ([Optimizing Deep Learning Models to Address Class Imbalance in Code Comment Classification, arXiv:2501.15854](https://arxiv.org/html/2501.15854)). *(primary)* **The categories that are easy to classify are the ones that carry an explicit syntactic marker (a tag, a keyword, a code block). The categories that require reading the prose and judging its illocutionary force — rationale, expansion, developer notes — are the hard ones, and they are the ones the assertion framing is about.**

**And there is barely anything there to classify.** Two independent corpora agree that "why" comments are 2–4% of comments:
- Pascarella & Bacchelli hand-classified >15,000 comment blocks from six large Java projects; `RATIONALE` accounts for **256 blocks / 563 lines** — roughly **1.7% of blocks** — against `SUMMARY` at 5,346 blocks. *(primary, with a caveat on table extraction — see §1.1.)*
- The NLBSE Java dataset has **379 positive `Rational` instances out of 9,339 comments (4.1%)**, and positive-instance rates across all 19 categories run **1.4% to 30.6%** ([arXiv:2501.15854](https://arxiv.org/html/2501.15854)). *(primary)*

Read with x5's finding that 60–75% of entities carry no comment at all, the funnel is severe: most entities have no comment; of the comments that exist, ~2–4% state a rationale; and the classifier that would find them scores 0.21–0.31 F1.

**Where "easily" *does* hold: one concept at a time, as a binary decision.** Every strong number in this literature comes from a binary "is this comment an X?" task, not from multi-class typing:
- **Assumptions:** ALBERT fine-tuned on the AssuEval dataset (TensorFlow + Keras comments, issues, PRs) reaches **F1 0.9584**; the best general LLM, Claude 3.5 Sonnet, reaches 0.8858, and the authors explicitly recommend against using ChatGPT/Claude/Gemini as-is for this task ([arXiv:2401.03653](https://arxiv.org/abs/2401.03653)). *(primary)*
- **Trigger-action comments** (conditional directives — "when X holds, do Y"): classifier **81.1% accuracy, F1 0.790** ([Executable Trigger-Action Comments, arXiv:1808.01729](https://arxiv.org/pdf/1808.01729)). *(primary)*
- **Rule-bearing comments** (iComment): **90.8–100% accuracy within a project**, dropping to **78.6–89.3% cross-project** ([iComment, SOSP 2007](https://pdfs.semanticscholar.org/d813/8bcf285547b1b0939c9ad86ecd97a1b82621.pdf)). *(primary)*
- **Javadoc → executable specification** (Jdoctor): **92% precision, 83% recall** ([Blasi et al., ISSTA 2018](https://software.imdea.org/~alessandra.gorla/papers/Blasi-JDoctor-ISSTA18.pdf)). *(secondary)*

The pattern across all four: **narrow the target to one assertion kind and give it a template, and accuracy jumps into the 80s–90s. Ask for a general typing of arbitrary prose and it collapses to the 20s–50s on the interesting classes.** iComment states the cost of that narrowing outright — "checking can only be done topic by topic," and each new topic needs new templates and new training data. *(primary)*

**Best-fit taxonomy for the assumption / requirement / explanation framing:** no single one covers it. The honest answer is a composite of three, detailed in §4 — Pascarella's `PURPOSE`/`NOTICE` branches for explanation and directive, the Javadoc/JML tag conventions for requirement/constraint, and the self-claimed-assumption line for assumption. Nothing published unifies them.

**Comment → knowledge graph:** partially precedented, never with *typed* comments. GraphGen4Code puts docstrings into a 2-billion-triple RDF graph as untyped documentation nodes; SEON provides the RDF/SPARQL substrate for software facts; RepoDoc (covered in x2) builds concept entities with an LLM rather than from classified comments. **The specific thing the premise proposes — classify each comment by assertion type, then store the typed statement as a graph node — was not found anywhere.** §5.

---

## 1. Taxonomies found

### 1.1 Pascarella & Bacchelli (MSR 2017) — the reference taxonomy for Java

Six top-level and 16 inner categories, derived by hand-classifying **more than 15,000 comment blocks / over 28,000 lines** from 2,000 sampled source files across six Java projects (Apache Spark, Eclipse CDT, Google Guava, Apache Hadoop, Google Guice, Vaadin) ([Pascarella & Bacchelli, MSR 2017](https://sback.it/publications/msr2017a.pdf)). *(primary)*

| Top | Inner | Definition |
|---|---|---|
| **PURPOSE** | Summary | brief description of what the code does |
| | Expand | detailed explanation |
| | **Rationale** | **explanation of design choices — the "why"** |
| **NOTICE** | Deprecation | warning about a deprecated interface |
| | Usage | how to use the functionality |
| | Exception | why an exception is raised |
| **UNDER DEVELOPMENT** | TODO | action to be completed |
| | Incomplete | partial / pending comment body |
| | Commented code | source code inside a comment |
| **STYLE & IDE** | Directive | text addressed to the IDE/compiler |
| | Formatter | logical separation only |
| **METADATA** | License | EULA text |
| | Ownership | author / ownership |
| | Pointer | reference to a linked resource |
| **DISCARDED** | Auto-generated | IDE stub |
| | Noise | meaningless or unclear |

Corpus proportions (comment blocks / lines): Summary 5,346 / 7,344; Usage 2,904 / 3,332; Directive 1,023 / 1,241; License 564 / 11,369; Commented code 329 / 684; **Rationale 256 / 563**; Exception 244 / 336; Ownership 205 / 205; Expand 199 / 1,995; TODO 190 / 248; Incomplete 87 / 111; Formatter 57 / 73; Deprecation 54 / 63; Pointer 20 / 22. *(primary, but flagged: the extracted top-level subtotals are internally inconsistent — PURPOSE's total equals Summary's, and METADATA's total equals STYLE & IDE's — so the extraction of that table is unreliable. The per-inner-category rows are consistent with the paper's narrative and with the independent NLBSE counts, and the relative ordering is safe; treat the exact figures as approximate.)*

The paper's own headline conclusion is the one that matters for a code map: **"59% of lines of comments should not be considered"** when computing comment-based readability metrics, because they are license text, commented-out code, formatter noise and IDE directives rather than content about the code. *(primary)*

Classification: **Naive Bayes Multinomial**, 10-fold cross-validation plus cross-project validation. Weighted-average TP rate **0.85** at both the top level and the inner level under 10-fold — but **0.74 under cross-project validation** (per-system range 0.74–0.83). Summary, the largest class: P=0.88 / R=0.82 under 10-fold, but cross-project precision ranged **0.61–0.99** and recall **0.56–0.99**. *(primary)* **The 10-fold-to-cross-project drop is the single most important methodological fact in this report: it is the difference between "works on the projects it was tuned on" and "works on your repository."**

Agreement: three professional Java developers independently classified the same three files, with **agreement above 92%**, and all found the categories clear and the task feasible. One author classified 100% of the 2,000 files, a second re-did a random 10% with "only negligible differences." *(primary)* So the taxonomy is *humanly* reliable even where it is machine-hard — worth keeping separate from the accuracy story.

An extended journal version exists — [Pascarella, Bruntink & Bacchelli, *Classifying code comments in Java software systems*, EMSE 2019](https://link.springer.com/article/10.1007/s10664-019-09694-w) — which adds industrial code. Springer gated it and the TU Delft mirror failed to extract. *(null — its generalization claims are unread.)*

### 1.2 Rani et al. (JSS 2021) — CCTM, the multi-language taxonomy

The Class Comment Type Model, built from **1,066 manually classified class comments** out of 37,446 extracted, across Java (6 projects, 378 classified), Python (7 projects, 349) and Smalltalk (7 projects, 341) ([Rani et al., JSS 2021](https://scg.unibe.ch/archive/papers/Rani21d.pdf)). *(primary)*

Categories, by language:
- **Java:** Summary, Expand, Ownership, Pointer, Usage, Deprecation, Rationale, Exception, Version, Commented Code, Todo, Warning, Recommendation, Observation, Precondition, Extension, Subclass Explanation
- **Python:** Summary, Usage, Expand, Development Notes, Parameters, Warning, Links, Recommendation, Observation, Precondition, Extension, Subclass Explanation, Todo, Version, Deprecated, Exception
- **Smalltalk:** Responsibility, Intent, Collaborator, Examples, Class Reference, Key Message, Key Implementation Point, Warning, Observation, Precondition, Extension, Subclass Explanation, Todo

Note that CCTM contains **Precondition**, **Warning**, **Recommendation** and **Observation** as first-class categories — the closest any published taxonomy comes to typing by assertion force rather than topic. They are also, tellingly, among the rarest.

Proportions (share of manually classified class comments): Java — Summary 89%, Expand 29%, Ownership 26%, Pointer 23%, Usage 23%, Deprecation 22%, **Rationale 13%**. Python — Summary 91%, Usage 26%, Expand 25%, Development Notes 19%, Parameters 16%. Smalltalk — Responsibility 70%, Intent 56%, Collaborator 27%, Examples 24%, Class Reference 17%. *(primary)* These are much higher than Pascarella's because CCTM is multi-label and scoped to *class* comments only — the richest comments in a codebase, not a random sample.

Best classification result: Random Forest on NLP+TEXT features, 10-fold — **Java P/R/F 92/92/92; Python 85/86/84; Smalltalk 78/90/77**, with Java Rationale at **95% F-measure** and Ownership at 99%. Worst: Smalltalk Class References **29% F-measure** with Random Forest (though Naive Bayes reached 93% on the same class). *(primary)*

The authors name why the hard categories are hard, and the reasons are structural rather than fixable by more data: *(primary)*
- categories without explicit markers (tags, headers) have no distinctive features;
- NLP heuristic patterns that appear in `Expand` also appear in `Pointer` and `Usage`, so the classes bleed;
- comments mixing prose with code snippets degrade the features (Python `Usage` had 17% incorrectly classified, the worst rate);
- CamelCase class names get split into words in prose, so class references stop looking like class references.

### 1.3 Steidl, Hummel & Juergens (ICPC 2013) — the quality-model taxonomy

Seven categories by *position and role* rather than content — copyright, header, member, inline, section, code (commented-out), task — assessed against four quality attributes: consistency, coherence, completeness, usefulness; applied to Java and C/C++ ([Steidl et al., ICPC 2013](https://teamscale.com/hubfs/26978363/Publications/2013-quality-analysis-of-source-code-comments.pdf)). *(secondary — the PDF was fetched but arrived as unparseable binary; the category list and quality attributes come from search summaries and from citations in other fetched papers.)* This is the taxonomy that shipped commercially (Teamscale) and it is deliberately *not* about assertion type — it types comments by where they sit, because that is machine-decidable.

### 1.4 Self-Admitted Technical Debt — the one category with a decade of tooling

Maldonado & Shihab's five types: **design debt, requirement debt, defect debt, documentation debt, test debt**, from manually reviewing 33,093 heuristically filtered comments in five Java projects and identifying 2,457 SATD comments. Design debt is 42–84% of SATD and requirement debt 5–45%. *(secondary)* The relevant point for the premise is not the taxonomy but the pipeline shape: SATD detection is a **binary filter first** (keyword heuristics: TODO/FIXME/HACK/XXX) and a **five-way classification second**, on a corpus already reduced by two orders of magnitude. That is the same "narrow first, then type" shape as iComment and Jdoctor.

### 1.5 The tag conventions — an assertion taxonomy that already ships

Not a research taxonomy, but the only one deployed at scale, and the one that actually types by assertion kind rather than topic:

| Tag | Assertion kind |
|---|---|
| `@param` (with a constraint clause) | precondition on an input |
| `@return` | postcondition |
| `@throws` / `@exception` | guarded/conditional assertion |
| `@deprecated` | directive to the caller |
| `@see` / `@link` | pointer |
| `@since`, `@author` | metadata |

Jdoctor exploits exactly this: it takes the `@param`, `@return` and `@throws` tags at method level and translates them into executable Java expressions, at **92% precision / 83% recall** ([Blasi et al., ISSTA 2018](https://software.imdea.org/~alessandra.gorla/papers/Blasi-JDoctor-ISSTA18.pdf); [toradocu](https://github.com/albertogoffi/toradocu)). *(secondary)* **This is the strongest evidence in the report for the assertion framing — but note what carries it: the assertion kind is given by the tag, not inferred from the prose. The hard NLP problem is reduced to translating a short clause whose type is already known.**

---

## 2. Classification accuracy — the consolidated numbers

Ordered by how close the task is to "generally type arbitrary comment prose."

| Task | Method | Result | Source |
|---|---|---|---|
| Binary: is this an assumption? | ALBERT fine-tuned | **F1 0.9584** | [arXiv:2401.03653](https://arxiv.org/abs/2401.03653) *(primary)* |
| same | Claude 3.5 Sonnet (best LLM) | F1 0.8858 | ibid. *(primary)* |
| Javadoc tag → executable spec | Jdoctor, pattern+lexical+semantic matching | P 92% / R 83% | [ISSTA 2018](https://software.imdea.org/~alessandra.gorla/papers/Blasi-JDoctor-ISSTA18.pdf) *(secondary)* |
| Rule extraction, one topic, same project | iComment | 90.8–100% accuracy | [SOSP 2007](https://pdfs.semanticscholar.org/d813/8bcf285547b1b0939c9ad86ecd97a1b82621.pdf) *(primary)* |
| Rule extraction, one topic, cross-project | iComment | **78.6–89.3%** | ibid. *(primary)* |
| Multi-class class-comment typing, 10-fold | Random Forest + NLP&TEXT | Java F 92%, Python 84%, Smalltalk 77% | [Rani JSS 2021](https://scg.unibe.ch/archive/papers/Rani21d.pdf) *(primary)* |
| Binary: is this a trigger-action comment? | ML classifier | 81.1% acc, F1 0.790 | [arXiv:1808.01729](https://arxiv.org/pdf/1808.01729) *(primary)* |
| Line-level typing, 10-fold | Naive Bayes Multinomial | weighted TP 0.85 | [MSR 2017](https://sback.it/publications/msr2017a.pdf) *(primary)* |
| Line-level typing, **cross-project** | same | **weighted TP 0.74** | ibid. *(primary)* |
| Multi-label sentence typing, 19 classes | NLBSE'25 SetFit baseline | **avg F1c 63.7** | [nlbse2025](https://github.com/nlbse2025/code-comment-classification) *(primary)* |
| same | best 2025 entrant (CodeBERT + reweighting) | **avg F1c 72.6** | [arXiv:2501.15854](https://arxiv.org/html/2501.15854) *(primary)* |
| same, rationale class only | best 2025 entrant | **F1c 31.1** | ibid. *(primary)* |

**Contradiction, surfaced not smoothed.** Rani et al. report **95% F-measure for Java Rationale**; the NLBSE'25 baseline reports **20.9** and the best 2025 entrant **31.1** for the same-named class. That is a factor of three on the single most important category. Three differences plausibly explain it, and this pass could not determine which dominates: (i) Rani classifies whole *class comments*, NLBSE classifies individual *sentences*, and a rationale sentence stripped of its surrounding comment loses most of its context; (ii) Rani's Java corpus is 378 hand-classified class comments evaluated by 10-fold cross-validation on the same corpus, while NLBSE is a held-out 20% test split on a 9,339-comment dataset; (iii) the two "Rationale" labels may not denote the same thing. **The reconciliation matters for any design decision: if (i) is the cause, classify whole comment blocks, never sentences.** Offered as a hypothesis, not a finding.

A second, milder contradiction: [CodeComClassify](https://www.researchgate.net/publication/392679821) reports **81% average F1** with distilbert on the same 19 categories. *(secondary)* That is a *weighted* average, which the huge Java-Summary class dominates; the NLBSE competition reports macro-style per-category F1c. Both can be true and they answer different questions. Weighted averages on a dataset with 1.4%-positive classes are close to meaningless for the rare categories — and the assertion-bearing categories are the rare ones.

**On LLMs specifically:** the only head-to-head found on a comment-classification task has fine-tuned ALBERT (F1 0.9584) beating Claude 3.5 Sonnet (0.8858), GPT and Gemini, with the authors recommending against the LLMs as-is *(primary)*. Pointing the other way, an adjacent literature on *code review* comments finds LLMs outperforming the trained deep-learning state of the art across 17 categories, with more balanced performance on low-frequency categories ([arXiv:2508.09832](https://arxiv.org/abs/2508.09832)) *(secondary)*. The second result is on a different artifact (review comments, which are conversational and long) and does not transfer without testing. No NLBSE entrant found in this pass used an LLM — the 2025 field was RoBERTa/CodeBERT/UniXcoder/DistilRoBERTa *(primary)*. **This is the most likely place where the literature is out of date relative to what is now cheaply possible, and the most defensible thing to actually measure rather than cite.**

---

## 3. What the "assumption" category looks like when someone mines it

The only category in the assumption/requirement/explanation triple with a dedicated empirical corpus.

Yang, Liang, Fu & Li mined nine deep-learning framework repositories and found **3,084 self-claimed assumptions across 1,775 files**, ranging from 1,460 in TensorFlow to 8 in Keras ([arXiv:2104.14208](https://arxiv.org/abs/2104.14208)). *(primary)* Two orthogonal taxonomies: by **validity** (valid / invalid / conditional / unknown) and by **content** (configuration-and-context / design / tensor-and-variable / miscellaneous). Assumptions were found to relate to technical debt, design decisions and implementation choices. The follow-up built **AssuEval** and got to F1 0.9584 with ALBERT ([arXiv:2401.03653](https://arxiv.org/abs/2401.03653)). *(primary)*

Two cautions. The 3,084 count is *self-claimed* — assumptions a developer explicitly flagged, typically with a keyword like "assume"; it is a lower bound on assumptions actually present, and the high F1 is partly a consequence of that lexical marking. And the variance across projects (1,460 vs 8) says the density of assumption comments is a property of a project's culture, not of code in general.

**The conditional-directive number is the sharpest one in the report.** Of **3,542 TODO comments** across eight open-source projects, keyword filtering on discourse cues ("if", "when", "once", "as", "then") surfaced 572 candidates, of which manual inspection confirmed **256 as genuine trigger-action comments** — a 45% confirmation rate on the filtered set, and **7.2% of all TODOs**. Of those 256, only the **20** highest-specificity ones were judged concrete enough to convert into executable checks ([arXiv:1808.01729](https://arxiv.org/pdf/1808.01729)). *(primary)* **20 out of 3,542 — 0.6% — is what "comments that are precise enough to act on mechanically" costs, inside the comment category that is supposed to be the most actionable of all.**

---

## 4. Best-fit taxonomy for the assumption / requirement / explanation framing

No published taxonomy covers all three. The honest composite:

| Framing category | Best-fit prior art | Fit quality |
|---|---|---|
| **Explanation / why** | Pascarella `PURPOSE::RATIONALE`; Rani CCTM `Rationale` | Exact name match, well-defined, hand-agreement good. **But ~2–4% of comments and F1 0.21–0.31 on the standard benchmark.** |
| **Explanation / what** | Pascarella `PURPOSE::SUMMARY`, `EXPAND` | Easy to classify (0.85 F1), abundant (89–91% of class comments), and the least informative — it restates the code. |
| **Requirement / constraint** | Javadoc `@param`/`@return`/`@throws` → Jdoctor/JML/DbC | Best mechanical fit of anything found (92%/83%), because the tag *declares* the assertion type. Only covers what authors chose to tag. |
| **Assumption** | Self-Claimed Assumptions (Yang et al.), content taxonomy | Real corpus, F1 0.9584 binary. Lexically marked ("assume") — an unmarked assumption is invisible to it. |
| **Directive** | Pascarella `NOTICE::DEPRECATION`/`USAGE`; `STYLE&IDE::DIRECTIVE`; trigger-action comments | Split across three taxonomies; the compiler-directive sense and the human-directive sense are different things that Pascarella keeps apart and the assertion framing would merge. |
| **TODO / debt** | Pascarella `UNDER DEVELOPMENT::TODO`; Maldonado & Shihab five-way SATD | Most mature tooling of any category. Keyword-filterable, so nearly free. |
| **Warning / precondition / observation** | Rani CCTM (`Warning`, `Precondition`, `Recommendation`, `Observation`) | The only categories in the literature typed by *force* rather than topic. Rare, and Rani does not report their individual F-measures. |

**Recommendation, stated as this excursion's judgement rather than a finding:** if a taxonomy has to be chosen, take **Pascarella's six-top/16-inner as the spine** — it is the most-cited, it was validated for human agreement above 92%, it is line-level (so it composes with a structural map), and its `DISCARDED` + `METADATA` + `STYLE&IDE` branches give you a principled way to throw away the 59% of comment lines that carry no information about the code. Then **overlay CCTM's `Precondition`/`Warning`/`Recommendation`** where assertion force matters, and treat **Javadoc tags as pre-classified ground truth** rather than as text to classify. Do not expect a general classifier to find rationale; expect to detect it where a marker exists and to accept a hole where it does not.

---

## 5. Comment → graph or queryable store

**Nothing found stores *classified* comments as typed nodes.** Three partial precedents, in descending order of relevance:

**GraphGen4Code** (IBM/WALA) is the largest. It builds RDF code knowledge graphs from **1.3M Python files and 47M forum posts** into **over 2 billion triples**, with **257K classes, 5.8M methods and 278K functions linked to documentation**. Three graph layers: dataflow from WALA static analysis, StackOverflow posts matched by IR, and **docstrings extracted from source**. Output is RDF N-Quads (so SPARQL-queryable) and JSON ([GraphGen4Code](https://wala.github.io/graph4code/); [wala/graph4code](https://github.com/wala/graph4code)). *(primary)* **The docstrings are nodes, but untyped** — the graph records *that* a function has documentation and links it, not what kind of statement the documentation makes. No accuracy or evaluation numbers are given on the project page. *(primary null.)*

**SEON** (Würsch, Ghezzi, Hert, Reif, Gall, *Computing* 94(11), 2012) is a pyramid of ontologies for software evolution: stakeholders, activities, artifacts and their relations, expressed in RDF and queried with **SPARQL**, linking code structures, issues, bugs and changes over time ([se-on.org](http://se-on.org/); [Springer](https://link.springer.com/article/10.1007/s00607-012-0204-1)). *(secondary)* This is the substrate precedent — "software facts in RDF, asked questions in SPARQL, including a natural-language query interface for developers" — but no evidence was found that SEON types comments by assertion kind.

**Contemporary code-KG tooling** puts comments in the graph as attached text. FalkorDB's CodeGraph and similar local-first tools parse "all docstrings and comments into the graph along with the raw source code," typed as documentation attached to a node rather than as statements with a kind. *(secondary, vendor sources.)* RepoDoc's RepoKG (covered in x2) creates **Concept Entities via LLM enrichment** rather than by classifying existing comments — which is a different design: it generates the concept layer instead of typing the harvested one.

Two adjacent items worth flagging without endorsement: US patent 10,656,938, *External comment storage and organization*, describes generating a comment database for a codebase with a navigation UI, motivated by comments being "unorganized and lack[ing] standardization" *(secondary — patent text not read in full)*; and iComment is arguably the closest functional precedent in the whole survey, since it converts comments into **rules** (`Lock L must be held before entering Function F`) which are structured, queryable assertions with subject/predicate/object shape — it just checks them against code rather than storing them in a graph. *(primary)*

**The gap is real and it is specific:** the classification literature classifies and stops; the graph literature ingests comments as opaque text. The join — classify, then store the typed statement with provenance and query it — was not found. Whether that is because it is a bad idea or because no one has done it, this pass cannot say.

---

## 6. Contradictions carried forward, not resolved

1. **Rationale F-measure: 95% (Rani, class-comment level, 10-fold) vs 20.9–31.1 (NLBSE, sentence level, held-out).** Factor of three on the category the premise cares about most. Hypothesized causes in §2; unresolved.
2. **10-fold vs cross-project.** Pascarella drops 0.85 → 0.74; iComment drops 90.8–100% → 78.6–89.3%. Every headline accuracy number in this literature is the optimistic one. No comment-classification paper found reports performance on a repository outside the research corpus entirely.
3. **LLMs worse (assumption detection, F1 0.886 vs 0.958) vs LLMs better (review-comment classification, beating trained DL across 17 categories).** Different artifacts, different tasks; not reconcilable from what was read.
4. **Weighted vs macro averaging.** 81% (weighted, CodeComClassify) and 63.7–72.6 (per-category F1c, NLBSE) describe the same 19-category task. With positive-instance rates from 1.4% to 30.6%, the weighted figure says almost nothing about the rare categories.
5. **Human agreement is high (>92%) where machine accuracy is low.** Pascarella's developers agreed on categories the classifiers get 0.21 F1 on. So the taxonomy is not incoherent — the automation is the weak link, which is a different problem with different fixes.

---

## Scoped nulls — what was and was not searched

Each null kills *this search under these conditions*, not the idea.

**Searched and genuinely absent:**
- **Speech-act / illocutionary-force classification of source code comments.** Three query formulations ("speech act applied to source code comments", "assertion theory taxonomy pragmatics software", "speech act code comments classification") returned Searle applied to tweets, political text, German offensive language, and developer Q&A conversations — never to code comments. Searched: open web + arXiv + ACL Anthology surfaced results. **Not searched:** ACM DL, IEEE Xplore or Springer full-text, where a workshop paper could hide.
- **A system that classifies comments by type and stores the typed statements in a graph.** Searched five query formulations across comment-classification and code-knowledge-graph vocabularies. Found the two halves separately, never joined.

**Sources attempted and not retrieved:**
- [Pascarella, Bruntink & Bacchelli, EMSE 2019](https://link.springer.com/article/10.1007/s10664-019-09694-w) — Springer redirected to an auth gate; the TU Delft mirror returned HTTP 422 through the text extractor. **This is the most valuable unread source**: it is the version that adds industrial code and would say whether the taxonomy generalizes beyond six OSS Java projects.
- [Steidl, Hummel & Juergens, ICPC 2013](https://teamscale.com/hubfs/26978363/Publications/2013-quality-analysis-of-source-code-comments.pdf) — PDF arrived as unparseable binary; the category list and quality model here are secondary. Their measured classification accuracy is unread.
- [C2S, FSE 2020](https://www.cs.purdue.edu/homes/lintan/publications/c2s-fse20.pdf) — the comments→JML line. Two fetch attempts failed (raw PDF, and the text extractor returned no content). Confirmed only that C2S is the sole technique generating non-return-related normal postconditions and that Jdoctor cannot. **Its precision/recall numbers are unread**, which leaves the comments→formal-specification accuracy story resting on Jdoctor alone.
- [Maldonado & Shihab SATD primaries](https://posl.ait.kyushu-u.ac.jp/~kamei/publications/Sierra_JSS2019.pdf) — the five-type taxonomy and the 42–84%/5–45% proportions are secondary. Their detection F1 numbers were not retrieved.
- [Jdoctor ISSTA 2018 primary](https://software.imdea.org/~alessandra.gorla/papers/Blasi-JDoctor-ISSTA18.pdf) — not fetched; 92%/83% is from a search summary. The corpus it was measured on is unknown to this report.
- Pascarella's per-category count table extracted with internal inconsistencies (§1.1) — the top-level subtotals should not be quoted.

**Named but not read:** STACC (arXiv:2302.13149, the NLBSE baseline's own paper — PDF unparseable); the NLBSE'23 and '24 competition reports and their full leaderboards; CodeComClassify primary; *Taxonomy of inline code comment smells* (EMSE 2023) and *Towards Automated Detection of Inline Code Comment Smells* (arXiv:2504.18956); aComment (ICSE 2011) and @tComment (ICST 2012) primaries; *A Survey on Research of Code Comment*; DocTer (documentation-guided fuzzing — extracts input constraints from docs, likely relevant to the requirement/constraint category); *Beyond Postconditions: Can LLMs infer Formal Contracts* (arXiv:2510.12702); *Automated Classification of Human Code Review Comments with LLMs* (arXiv:2604.23667); *Code Comments for Quantum SDKs* (arXiv:2512.00766).

**Not searched at all:**
- **Databases:** no ACM DL, IEEE Xplore, Springer, ScienceDirect or Scopus full-text search. ICPC, ICSME, MSR, EMSE and TSE are represented only by what leaked into open web search and author-hosted PDFs.
- **Formal-annotation conventions were surveyed only through the comment-translation papers.** JML, Microsoft SAL, Eiffel Design-by-Contract, ACSL, Ada/SPARK contracts, Rust doc attributes and `#[must_use]`, Python `typing`/`@deprecated`/doctest, and Go's `// Deprecated:` convention were **not** researched in their own right. If the design wants a ready-made assertion vocabulary, that body — decades of standardized precondition/postcondition/invariant syntax — is the most likely place to find one and it is unexamined here.
- **Languages beyond Java, Python, Smalltalk/Pharo and (via iComment) C.** No C++-specific comment-classification work was searched, which matters given `superCoolSpaceSim_cpp`.
- **Requirements-engineering NLP** (requirement classification, FR/NFR taxonomies, PROMISE datasets) — a large adjacent literature on classifying natural-language statements by assertion type, deliberately skipped for budget. It is the most likely source of a ready-made assertion taxonomy that this pass did not open.
- **Commit messages, issue text and code review comments** as assertion sources — touched only where they appeared incidentally (AssuEval, review-comment LLM papers).
- **Nothing was installed, run, evaluated or measured.** Every accuracy number here is as reported by its authors on their own corpus. No claim has been checked against this repository or any other.

---

## Sources

Taxonomies:
- [Pascarella & Bacchelli, *Classifying Code Comments in Java Open-Source Software Systems*, MSR 2017](https://sback.it/publications/msr2017a.pdf) · [EMSE 2019 extension](https://link.springer.com/article/10.1007/s10664-019-09694-w) *(gated)*
- [Rani et al., *How to identify class comment types? A multi-language approach*, JSS 2021](https://scg.unibe.ch/archive/papers/Rani21d.pdf) · [arXiv:2107.04521](https://arxiv.org/abs/2107.04521)
- [Rani et al., *A Decade of Code Comment Quality Assessment: A Systematic Literature Review*, arXiv:2209.08165 / JSS 2023](https://arxiv.org/abs/2209.08165) — 2,353 papers screened, 47 reviewed, 21 quality attributes; finds researchers rely on manual assessment and heuristics rather than automation
- [Steidl, Hummel & Juergens, *Quality Analysis of Source Code Comments*, ICPC 2013](https://teamscale.com/hubfs/26978363/Publications/2013-quality-analysis-of-source-code-comments.pdf)
- [Sierra, Shihab & Kamei, *A Survey of Self-Admitted Technical Debt*, JSS 2019](https://posl.ait.kyushu-u.ac.jp/~kamei/publications/Sierra_JSS2019.pdf)

Accuracy / benchmarks:
- [NLBSE'25 code comment classification](https://github.com/nlbse2025/code-comment-classification) · [NLBSE'24](https://github.com/nlbse2024/code-comment-classification) · [NLBSE'23](https://github.com/nlbse2023/code-comment-classification)
- [*Optimizing Deep Learning Models to Address Class Imbalance in Code Comment Classification*, arXiv:2501.15854](https://arxiv.org/html/2501.15854)
- [*STACC: Code Comment Classification using SentenceTransformers*, arXiv:2302.13149](https://arxiv.org/pdf/2302.13149)
- [*Exploring the Potential of LLMs in Fine-Grained Review Comment Classification*, arXiv:2508.09832](https://arxiv.org/abs/2508.09832)

Assertion-typed comments:
- [Tan et al., */\*iComment: Bugs or Bad Comments?\*/*, SOSP 2007](https://pdfs.semanticscholar.org/d813/8bcf285547b1b0939c9ad86ecd97a1b82621.pdf)
- [Blasi et al., *Translating code comments to procedure specifications* (Jdoctor), ISSTA 2018](https://software.imdea.org/~alessandra.gorla/papers/Blasi-JDoctor-ISSTA18.pdf) · [toradocu](https://github.com/albertogoffi/toradocu)
- [Zhai et al., *C2S: Translating Natural Language Comments to Formal Program Specifications*, FSE 2020](https://www.cs.purdue.edu/homes/lintan/publications/c2s-fse20.pdf) *(unread)*
- [*Executable Trigger-Action Comments*, arXiv:1808.01729](https://arxiv.org/pdf/1808.01729)
- [Yang, Liang, Fu & Li, *Self-Claimed Assumptions in Deep Learning Frameworks*, EASE 2021 / arXiv:2104.14208](https://arxiv.org/abs/2104.14208)
- [*An Exploratory Study on Automatic Identification of Assumptions in the Development of Deep Learning Frameworks*, arXiv:2401.03653](https://arxiv.org/abs/2401.03653)

Comments in graphs / stores:
- [GraphGen4Code](https://wala.github.io/graph4code/) · [wala/graph4code](https://github.com/wala/graph4code)
- [SEON — Software Evolution Ontologies](http://se-on.org/) · [Würsch et al., *SEON: a pyramid of ontologies for software evolution*, Computing 2012](https://link.springer.com/article/10.1007/s00607-012-0204-1)
- [US 10,656,938 — External comment storage and organization](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10656938)

Speech acts (adjacent, not applied to code comments):
- [*Detecting Speech Act Types in Developer Question/Answer Conversations During Bug Repair*, arXiv:1806.05130](https://arxiv.org/pdf/1806.05130)
