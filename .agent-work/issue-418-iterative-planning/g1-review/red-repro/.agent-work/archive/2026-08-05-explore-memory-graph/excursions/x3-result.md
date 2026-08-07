# Excursion Result: Cognitive rules for building conceptual links

Cycle 2 (shotgun), `explore-memory-graph`. Research excursion. Run 2026-08-04.

**Question asked:** what deliberate cognitive techniques in the family of "ask why 5 times" exist for building conceptual links between ideas — and which could an agent run mechanically as a repeatable rule to grow edges in a knowledge graph?

**What this is:** a catalog of 20 techniques from six published traditions, each with its origin, the kind of link it produces, and a verdict on whether an agent could run it as a rule. Descriptions are sourced. **Verdicts are this excursion's own judgment and are labelled as such in every entry.** Ends with a shortlist of five rules worth building first, and the techniques that failed under this framing.

---

## How to read the verdicts

Two distinctions turned out to matter more than anything else, and they are not in the source literature — they come from asking what an agent would actually have to do.

**Edge-only versus node-minting.** Some rituals only propose links between things that already exist in the graph ("does this contradict anything I already hold?"). Others invent new content as they run — 5 Whys manufactures a cause at every step, and that cause is usually not yet a node. Edge-only rules are cheap, bounded, and safe to run on a schedule. Node-minting rules grow the graph and can bloat it without limit, so each one needs a stop rule and a binding step that checks whether the newly-named thing is already a node under a different name.

**Checkable versus unfalsifiable output.** A proposed "contradicts" edge can be checked by a second pass that tries to state the contradiction as a sentence; if it can't, the edge is dropped. A proposed "this reminds me of that" edge has no truth condition, so a bad one is indistinguishable from a good one until a human looks. Rules in the first group can run unattended. Rules in the second group need a human or a downstream usefulness signal.

**Cost** below is stated in a common unit: how many existing nodes must be retrieved, how many model calls one application takes, and roughly how many edges come out.

**Edge vocabulary used in the verdicts** (a working set, not a proposal): `caused-by`, `explained-by`, `supports`, `contradicts`, `refines`, `depends-on`, `constrained-by`, `trades-off-against`, `generalizes` / `specializes`, `part-of`, `analogous-to`, `contrasts-with`, `supersedes`, `threatened-by`, `responds-to`.

---

# Part 1 — The catalog

## Family A: causal and root-cause rituals

### T1. The 5 Whys

**Origin (sourced).** Developed by Sakichi Toyoda in the 1930s as part of what became the Toyota Production System; his son Kiichiro and engineer Taiichi Ohno refined it after the war. Ohno: "The basis of Toyota's scientific approach is to ask why five times whenever we find a problem … By repeating why five times, the nature of the problem as well as its solution becomes clear." Ohno was demanding about depth and rejected answers that stopped at symptoms. The method is now embedded in Six Sigma, ISO 45001, and OSHA investigation guidance. ([Wikipedia](https://en.wikipedia.org/wiki/Five_whys), [5xwhys.com history](https://5xwhys.com/articles/5-whys/history-toyota/), [Sloww](https://www.sloww.co/5-whys/))

**Link kind.** A single causal chain: symptom → proximate cause → … → systemic cause. Strictly linear, one parent per step.

**Verdict (excursion judgment).** Mechanizable, and the closest thing in the catalog to a ready-made edge rule — but node-minting, which is its whole risk. Each "why" names a cause that probably isn't a node yet. Without a binding step the rule generates a private chain of five orphans hanging off one node, which is graph bloat wearing a lean-manufacturing hat. Make it usable with three constraints: cap depth at 3 rather than 5 (the fourth and fifth steps in practice drift into organizational platitude — "insufficient training"); after each generated cause, run a similarity search and bind to an existing node if one matches, minting only on a miss; and stop early when a step produces a cause already in the graph, since arriving at an existing node is the success case, not the boring case. Known limitation worth carrying: the ritual assumes a single cause per level, so it will systematically miss the multi-cause case — that is what T2 is for.
**Cost:** retrieval of ~10 nodes per step for binding; 3 model calls; yields 1–3 `caused-by` edges plus 0–3 new nodes.

### T2. Ishikawa fishbone with the 6M categories

**Origin (sourced).** Invented by Kaoru Ishikawa at the University of Tokyo (1943, popularised through Toyota quality circles in the 1960s); one of the seven basic quality tools. The classic categories are Manpower, Method, Machine, Material, Measurement, and Mother Nature — though Ishikawa encouraged renaming the categories to suit the domain. ([ASQ](https://asq.org/quality-resources/fishbone), [Wikipedia](https://en.wikipedia.org/wiki/Ishikawa_diagram))

**Link kind.** A fan of candidate causes, bucketed by category — many-to-one causal, in contrast to 5 Whys' one-to-one chain.

**Verdict (excursion judgment).** Mechanizable and better suited to an agent than 5 Whys in one specific respect: the category list is the prompt. Iterating a fixed six-item checklist is exactly the sort of thing that runs identically every time, whereas free-form "why?" wanders. The 6M labels are manufacturing-specific, so a software-memory graph would need its own six — Ishikawa's own advice licenses that substitution. The catch is precision: a fan rule proposes six candidate causes where the chain rule proposes one, and most of the six will be empty. Require the rule to return "no cause in this category" as a first-class answer, or it will confabulate one per bucket.
**Cost:** 1 model call with the category list inlined; retrieval of the node plus neighbours; yields 0–6 `caused-by` candidates, expect high reject rate.

### T3. Abduction (inference to the best explanation)

**Origin (sourced).** C. S. Peirce's third form of inference alongside deduction and induction. His schema: a surprising fact C is observed; if hypothesis A were true, C would follow as a matter of course; so there is reason to suspect A is true. Peirce held abduction is the only logical operation that introduces a new idea, since it generates the hypotheses the other modes then test; the conclusion is a plausible conjecture, not a proof. ([Psillos on Peirce, PDF](http://users.uoa.gr/~psillos/PapersI/11-Peirce-Abduction.pdf), [De Gruyter](https://www.degruyterbrill.com/document/doi/10.1515/css-2024-2022/html))

**Link kind.** `explained-by`, from an observation node to a hypothesis node.

**Verdict (excursion judgment).** Mechanizable only if the graph can supply the trigger, and that trigger is the interesting part. Abduction needs a *surprising* fact, and surprise is a graph-computable property: a node that contradicts an existing node, or that has no incoming explanatory edge after N days, is the mechanical stand-in for surprise. That makes this less a linking rule than a *scheduler* for the other rules — it says which node to point them at. Peirce's own caveat, that many hypotheses explain any C, means output must be marked as conjecture and never as settled.
**Cost:** graph query for unexplained or conflicting nodes (cheap, no model call); then 1 call per selected node; yields 1 `explained-by` edge, low confidence by construction.

### T4. Pre-mortem / prospective hindsight

**Origin (sourced).** Gary Klein introduced the project pre-mortem in *Harvard Business Review* (2007): imagine the project has already failed, then work backwards to what caused it. The underlying effect is older — Mitchell, Russo and Pennington (1989, *Journal of Behavioral Decision Making*) found that framing an event as already having occurred increases the ability to correctly identify reasons for outcomes by about 30%. ([Ness Labs](https://nesslabs.com/pre-mortem-anticipate-failure-with-prospective-hindsight), [Klein, "Performing a Project Premortem"](https://www.researchgate.net/publication/3229642_Performing_a_Project_Premortem), [ScienceBlog on the 1989 finding](https://scienceblog.com/g-stay-a-step-ahead-premortem-technique-prospective-hindsight-research/))

**Link kind.** `threatened-by` — from a plan or decision node to failure-mode nodes.

**Verdict (excursion judgment).** Mechanizable and unusually well-suited to an agent, because the entire technique is a prompt reframe with a measured effect size behind it. Applies only to a specific node type (plans, decisions, designs), which is a feature: it gives a clean trigger condition. The edges it produces are the ones a memory graph is otherwise worst at holding, since risks get recorded in prose and lost. Node-minting, but bounded — failure modes are a closed-ish set per plan and the rule can be capped at three.
**Cost:** 1 call on plan-type nodes; yields 2–3 `threatened-by` edges plus new failure-mode nodes.

## Family B: explanation and self-testing rituals

### T5. Elaborative interrogation

**Origin (sourced).** A learning-science strategy in which the learner generates an explanation for why a stated fact is true, integrating it with prior knowledge. Meta-analytic evidence spans over 250 effect sizes; learners prompted to explain why facts were true recalled significantly more than those who reread the same material, and generating the explanation yourself matters more than reading one. Documented limits: it works for learners with adequate prior knowledge, on relational and causal material, and shows up more on cued recall than on transfer. ([Wikipedia](https://en.wikipedia.org/wiki/Elaborative_interrogation), [Learning Scientists](https://www.learningscientists.org/blog/2017/7/11-1))

**Link kind.** `explained-by` and `supports` edges reaching from a new node back into prior knowledge.

**Verdict (excursion judgment).** Mechanizable and cheap, and its documented limits map onto graph conditions almost perfectly. "Requires adequate prior knowledge" becomes "only run on nodes with at least k existing neighbours" — a query, not a judgment call. "Works on relational and causal material" becomes a node-type filter. That is a rare case of a psychological boundary condition translating directly into a gating predicate, which is what makes this a good first rule rather than a good idea. Edge-only if the prompt is constrained to explain using retrieved existing nodes.
**Cost:** retrieve k neighbours; 1 call; yields 1–2 `explained-by` edges to existing nodes.

### T6. Self-explanation prompting

**Origin (sourced).** Identified by Chi, Bassok, Lewis, Reimann and Glaser (1989) and Chi, De Leeuw, Chiu and Lavancher (1994, *Cognitive Science*): learners who articulate their reasoning while studying worked examples infer missing knowledge, notice inconsistencies, and repair their conceptual frameworks. A meta-analysis reports a mean effect of g = 0.66 across 69 effect sizes. Students typically need prompting to do it. ([Chi et al. 1994, Wiley](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1803_3), [Chi et al. 1989](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1302_1))

**Link kind.** Gap-filling: `depends-on` edges to unstated prerequisites, and `contradicts` edges to inconsistencies surfaced along the way.

**Verdict (excursion judgment).** Mechanizable, and the "notice inconsistencies" half is the valuable half. Self-explanation as an agent rule means walking a node's stated reasoning step by step and flagging each step that doesn't follow from a linked node — every flag is a missing `depends-on` edge, and every conflict is a `contradicts` candidate. Note the honest asymmetry: the effect in humans comes from the *generation* doing something to the learner's memory, which does not transfer to an agent. What transfers is only the output — the gaps found. Judge the rule on edge yield, not on any claimed benefit to the model.
**Cost:** 1 call per node, longer context than most; yields 1–3 `depends-on` plus occasional `contradicts`.

### T7. The Feynman technique

**Origin (sourced).** Named for Richard Feynman and his reputation for explaining complex ideas plainly. The loop: try to teach the concept at a sixth-grade level, find the points where you cannot, return to the source, then simplify and organise. Gap identification is the operative step — the places you cannot retrieve or cannot say simply. ([Farnam Street](https://fs.blog/feynman-learning-technique/), [E-Student](https://e-student.org/feynman-technique/))

**Link kind.** `depends-on` — every term you cannot avoid using is a prerequisite concept.

**Verdict (excursion judgment).** Mechanizable in a reframed form, and the reframe is where it gets good. The technique as written depends on an audience and on feeling stuck, neither of which an agent has. But there is a mechanical equivalent with a hard test: *restate this node using only vocabulary defined by its currently linked neighbours; every term you had to import from outside that set is a missing `depends-on` edge.* That version has a real pass/fail condition instead of a vibe, and it produces edges pointing at genuine prerequisite gaps. Recommended as a rule in this form only; the "explain it simply" framing alone produces no edges at all.
**Cost:** retrieve the node's current neighbourhood; 1 call; yields 0–4 `depends-on` edges, mostly to existing nodes.

## Family C: argument-structure rituals

### T8. Socratic questioning taxonomy

**Origin (sourced).** Richard Paul and Linda Elder's six categories: questions of clarification; questions probing assumptions; questions probing reasons and evidence; questions about viewpoints and perspectives; questions probing implications and consequences; and questions about the question. Paul and Elder distinguish spontaneous, exploratory, and focused Socratic questioning; the taxonomy has been extended to nine types in later adaptations. ([Paul & Elder, *The Thinker's Guide to Socratic Questioning*, PDF](https://www.criticalthinking.org/files/SocraticQuestioning2006.pdf), [U. Michigan summary](https://websites.umich.edu/~elements/probsolv/strategy/cthinking.htm))

**Link kind.** Two of the six categories yield edges directly: assumptions give `depends-on` links to unstated premises, implications give forward `entails` or `supports` links. The rest largely produce clarification, which improves a node rather than linking it.

**Verdict (excursion judgment).** Partly mechanizable — take the two categories that produce edges and discard the other four for this purpose. The assumption probe is the strongest single question in the whole catalog for a memory graph, because unstated premises are exactly what an agent's notes omit and exactly what breaks when the premise later changes. Running all six categories as a rule wastes four calls out of six on prose polish. Treat the taxonomy as a menu to raid, not a ritual to run whole.
**Cost:** 1 call for the assumption probe, 1 for implications; yields 1–3 `depends-on` and 1–2 forward edges.

### T9. The Toulmin model

**Origin (sourced).** Stephen Toulmin's six-part structure: claim, grounds, warrant, backing, qualifier, rebuttal. Claim, grounds and warrant are the essential parts; the warrant is the reasoning that licenses the leap from grounds to claim, and warrants are often left implicit and unstated. Backing supports the warrant; rebuttal states exceptions and is itself a full argument. ([Write What Matters](https://idaho.pressbooks.pub/write/chapter/toulmin-argument-model/), [UMW Speaking Center](https://academics.umw.edu/speaking/resources/handouts/toulmin-argument-model/))

**Link kind.** A typed skeleton: `supports` (grounds → claim), `licensed-by` (claim → warrant), `contradicts` or `undercuts` (rebuttal → claim), plus a confidence qualifier on the claim itself.

**Verdict (excursion judgment).** Mechanizable, and the most useful thing here is a slot the graph would otherwise never fill: the warrant. Toulmin's own observation that warrants usually go unstated is the whole opportunity — "name the unstated warrant connecting these two linked nodes" turns an existing untyped edge into a typed one with an explicit reason attached. That makes this an *edge-refinement* rule rather than an edge-discovery rule, which is a distinct and probably under-valued category: it improves edges the graph already has instead of adding more. The qualifier slot also gives a natural home for edge confidence.
**Cost:** 1 call per existing claim-support edge; yields 0 new edges but types and annotates 1 existing edge.

### T10. IBIS (issue-based information system)

**Origin (sourced).** Proposed by Werner Kunz and Horst Rittel in the late 1960s and 70s as an argumentative model for decision-making on wicked problems with many stakeholders. Three node types: issue (a question), position (an answer or alternative), argument (an opinion that supports or objects to a position). It underpins dialogue mapping and systems including Zeno, HERMES, QuestMap and Compendium. ([Kunz & Rittel 1970, PDF](http://magrawal.myweb.usf.edu/phd/articles/ibis_wp_70.pdf), [Conklin, "IBIS: A Tool for All Reasons"](https://www.cognexus.org/IBIS-A_Tool_for_All_Reasons.pdf))

**Link kind.** `responds-to` (position → issue), `supports` and `objects-to` (argument → position).

**Verdict (excursion judgment).** Mechanizable, and worth noting that IBIS is not really a linking *ritual* — it is a schema, and a battle-tested one. Its value to this project is as a target vocabulary rather than a generation rule: it is a small typed edge set that survived thirty years of tool-building, which is evidence that three or four edge types is enough to be useful. The one generative rule it suggests is decomposition: given a decision node, split it into the issue it answers and the positions it rejected, which recovers the road-not-taken that memory notes almost always drop.
**Cost:** 1 call per decision node; yields 1 issue node, 1–3 position nodes, `responds-to` edges.

### T11. The Zettelkasten relate-check (Ahrens)

**Origin (sourced).** Sönke Ahrens, *How to Take Smart Notes*: when turning a fleeting note into a permanent one, ask how the new information "contradicts, corrects, supports, or adds to what I already know." Practitioners in the Zettelkasten community formalise similar categories — similarity between different ideas, difference between similar ideas, supporting evidence, contradicting evidence — and stress writing down *why* two notes are connected, not just that they are. Where the reason is long, it goes in a bridge note. ([Ahrens summary, Reading Graphics](https://readingraphics.com/book-summary-how-to-take-smart-notes/), [zettelkasten.de, "Different Kinds of Ties Between Notes"](https://zettelkasten.de/posts/kinds-of-ties/), [Zettelkasten Forum on link types](https://forum.zettelkasten.de/discussion/2023/link-types))

**Link kind.** Four typed edges in one question: `contradicts`, `refines`, `supports`, `extends`.

**Verdict (excursion judgment).** Mechanizable, cheapest in the catalog, and the single best candidate to build first. It is strictly edge-only — it links a new node to existing ones and mints nothing. It is checkable, because each of the four types has a testable restatement ("state the contradiction in one sentence"; if the model can't, drop the edge). It runs on a natural trigger, node creation, so it needs no scheduler. And the community's insistence on recording *why* maps to putting the justification on the edge, which is what makes an edge auditable later. Bounded by k, the number of neighbours retrieved.
**Cost:** 1 vector query for k≈10 candidates; 1 call; yields 0–4 typed edges to existing nodes. No new nodes.

## Family D: analogy rituals

### T12. Structure-mapping

**Origin (sourced).** Dedre Gentner's structure-mapping theory (1983, *Cognitive Science*): an analogy maps knowledge from a base domain to a target, conveying that a system of relations holding among base objects also holds among target objects. Two principles govern it — relations are mapped rather than object attributes, and *systematicity*: a set of matching relations interconnected by higher-order relations is a better analogical match than the same number of unconnected matching relations. ([Gentner 1983, Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0702_3), [Gentner & Markman, PDF](https://home.csulb.edu/~cwallis/382/readings/482/GenterMarkman.pdf))

**Link kind.** `analogous-to`, between structurally aligned subgraphs rather than between single nodes.

**Verdict (excursion judgment).** Mechanizable, and uniquely among the analogy techniques it ships with its own scoring function. Systematicity is the thing this catalog otherwise lacks: a stated, countable criterion for whether a proposed link is good, namely the number of higher-order relations that survive the alignment. Every other "what does this remind me of" method proposes edges no one can rank. The cost is real — analogy retrieval is over the whole graph, not a neighbourhood, and surface similarity actively misleads here since the theory's whole point is that relational match beats attribute match, while embedding search returns attribute match. The practical implication: don't use plain vector similarity to find analogy candidates, or the rule reduces to "these two nodes use similar words."
**Cost:** graph-wide candidate retrieval (the expensive part); 1 call per candidate pair to align and count shared relations; yields 0–1 high-value `analogous-to` edges with a numeric confidence.

### T13. Analogical encoding (comparing two cases)

**Origin (sourced).** Gentner, Loewenstein and Thompson (2003, *Journal of Educational Psychology*): comparing two analogous examples makes their common relational structure salient, letting learners derive a schema that transfers to structurally similar problems. In their negotiation study, management students who drew an analogy across two cases were nearly three times more likely to use the strategy later than students given the same two cases separately. People who study cases one at a time encode them concretely, and later remindings then run on surface similarity. ([Gentner, Loewenstein & Thompson 2003, PDF](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf), [Loewenstein, Thompson & Gentner 1999, PDF](https://groups.psych.northwestern.edu/gentner/papers/LoewensteinThompsonGentner99.pdf))

**Link kind.** `generalizes` — two sibling nodes both pointing up at a newly minted schema node.

**Verdict (excursion judgment).** Mechanizable and this is the catalog's clearest argument for a *consolidation* rule rather than a linking rule. It says something a memory graph should care about: cases stored singly get retrieved by surface features, and the fix is to compare pairs and store the abstraction. Mechanically this is "find two nodes that are already `analogous-to` each other, mint the schema node above them, and link both to it." Node-minting, but it mints the one kind of node worth minting, since the schema node becomes a retrieval target that generalises across future cases. Best run as a periodic batch over existing analogy edges rather than at write time.
**Cost:** operates on pairs already linked by T12; 1 call per pair; yields 1 new schema node plus 2 `generalizes` edges.

### T14. Pólya's related-problem heuristic

**Origin (sourced).** George Pólya, *How to Solve It* (1945), in the devising-a-plan stage: "Have you seen it before? Or have you seen the same problem in a slightly different form? Do you know a related problem?" — and, specifically, "try to think of a familiar problem having the same or a similar unknown." The analogy principle directs the solver to a resembling problem with a known solution method and to study the similarities and differences between the two. ([Pólya, *How to Solve It*, full text PDF](https://www.hlevkin.com/hlevkin/90MathPhysBioBooks/Math/Polya/George_Polya_How%20to%20Solve%20It.pdf), [Northeastern summary](http://www.ccs.neu.edu/home/lieber/courses/csu670/f04/materials/problem-solving/G_%20Polya,%20How%20to%20Solve%20It.htm))

**Link kind.** `analogous-to` with a precedent flavour — problem-to-problem, carrying a method across.

**Verdict (excursion judgment).** Mechanizable and narrower than T12, which is why it may be more useful. "Same or similar unknown" is a far tighter retrieval key than general similarity: index problem-type nodes by what was unknown or what was being sought, and the query becomes a filter rather than a fuzzy search. For an agent memory graph the payload is the method, so the edge should carry it — `solved-by-same-method-as` rather than a bare `analogous-to`. Pólya's "study the similarities *and differences*" is worth keeping in the prompt, since the difference is what tells a future reader when the precedent stops applying.
**Cost:** filtered retrieval on unknown-type; 1 call; yields 0–2 precedent edges.

## Family E: structural and hierarchical rituals

### T15. The Idea Compass

**Origin (sourced).** Created by Vicky Zhao and Fei-Ling Tseng, presented at the Linking Your Thinking conference in May 2022, building on Luhmann's Zettelkasten. Four directional questions: North, "what larger pattern does this concept belong to?"; South, "what more basic components is this concept made of?"; East, "what is this concept similar to?"; West, "what is this concept different from?" The framework distinguishes hierarchical links (N/S, tree-like) from rhizomatic links (E/W, networked). ([Writing Slowly, "How to connect your notes"](https://writingslowly.com/2023/08/27/how-to-connect.html), [Zahler Design](https://www.zahlerdesign.com/blog/enter-the-idea-compass))

**Link kind.** Four at once: `part-of` or `instance-of` (N), `composed-of` (S), `analogous-to` (E), `contrasts-with` (W).

**Verdict (excursion judgment).** Mechanizable and the best value-per-call in the catalog: four differently-typed edges from one fixed prompt with no free parameters. The West question is the sleeper — "what is this different from?" produces contrast edges, and contrast is both rare in auto-built graphs and disproportionately useful, since knowing what a thing is *not* is how you avoid retrieving the wrong neighbour. The rule needs one guard: constrain all four answers to existing nodes, or North and South will mint abstraction ladders forever. Its own authors' hierarchical/rhizomatic split is a useful hint that these two pairs might warrant separate storage or separate traversal costs.
**Cost:** 1 call, 1 retrieval of candidates; yields 0–4 typed edges, all to existing nodes if constrained.

### T16. Laddering (up and down)

**Origin (sourced).** Grounded in George Kelly's personal construct theory (1955), which holds that construct systems are hierarchically organised. Hinkle (1965), Kelly's student, developed laddering to elicit constructs at higher levels of abstraction by analysing the implications of change in one construct; Landfield's pyramid technique (1971) moves downward. From a seed item, probing questions guide the participant up, down and across the hierarchy. The standard probes: "why is that important to you?" to move up, "how is it different?" to move down. ([Emerald, "Use a repertory grid"](https://www.emeraldgrouppublishing.com/how-to/observation/use-a-repertory-grid), [EduTech Wiki](https://edutechwiki.unige.ch/en/Repertory_grid_technique))

**Link kind.** Upward `serves` or `generalizes` toward goals and values; downward `specializes` toward concrete instances.

**Verdict (excursion judgment).** Mechanizable and it is the right tool where 5 Whys is the wrong one. 5 Whys asks why something *happened* and needs a causal domain; laddering asks why something *matters* and works on preferences, goals and design decisions — which is a large share of what an agent memory actually holds. Same recursive shape, same stopping problem, same fix (cap the depth, bind each rung to an existing node). Hinkle's stop condition, the point where the person can generate no new construct, has a mechanical analogue: stop when a rung paraphrases the rung below it.
**Cost:** 2–3 calls for a bounded ladder; yields 2–3 hierarchy edges, some node-minting.

### T17. Concept mapping: focus questions and cross-links

**Origin (sourced).** Joseph Novak began this work in the 1960s from Ausubel's theory of meaningful learning, on which new concepts are assimilated into existing cognitive structure rather than memorised in isolation. A proper concept map has a focus question it answers, a rough hierarchy with general concepts above specific ones, and *cross-links* joining separate branches. Labelled links form propositions — statements defining how two ideas connect. ([Novak & Cañas, "The Theory Underlying Concept Maps", PDF](https://cmap.ihmc.us/publications/researchpapers/theoryunderlyingconceptmaps.pdf))

**Link kind.** Cross-links specifically: edges between distant branches, as opposed to parent-child edges within a branch.

**Verdict (excursion judgment).** Two mechanizable pieces, and the cross-link one is a genuine structural insight. Novak singles out cross-branch links as the characteristic feature of a good map, which translates into a graph-computable target: prefer proposed edges whose endpoints are currently far apart in the graph over ones connecting already-adjacent nodes. That gives an edge-proposal *ranker* usable across every other rule in this catalog, and it costs a path-length query rather than a model call. Second piece: Novak's insistence that every link is labelled and forms a proposition argues against untyped edges anywhere in the design — an unlabelled edge is not a claim and cannot be checked or refuted later.
**Cost:** the ranker is a graph query, no model call. Labelling an unlabelled edge is 1 cheap call.

## Family F: transformation and contradiction rituals

### T18. TRIZ contradiction analysis

**Origin (sourced).** Genrich Altshuller began TRIZ in 1946; he and his team analysed over 400,000 patents through 1985, deriving 40 inventive principles and a contradiction matrix. A *technical contradiction* is when improving one parameter degrades another; the matrix is a 39 × 39 cross-reference of improving against worsening parameters, each cell naming up to four principles. *Physical contradictions*, where one parameter must hold opposite values, are handled by separation principles instead. ([Wikipedia, 40 principles](https://en.wikipedia.org/wiki/40_principles_of_invention), [TRIZ Consulting Group](https://www.triz-consulting.de/about-triz/triz-matrix/?lang=en))

**Link kind.** `trades-off-against` and `constrained-by` — symmetric tension edges rather than directional support.

**Verdict (excursion judgment).** Partly mechanizable, and worth separating the two halves. The *detection* half — "does this node improve something at the cost of something else, and is the something-else already a node?" — is a straightforward rule and produces an edge type nothing else in the catalog produces. Trade-off edges are what make a memory useful at decision time, because they explain why the obvious improvement wasn't taken. The *resolution* half, the 39 × 39 matrix and 40 principles, is engineering-domain-specific and does not transfer to a software memory graph; treat it as out of scope rather than as a source of edges. Verdict is a partial: detection yes, matrix no.
**Cost:** 1 call per design or decision node; yields 0–2 `trades-off-against` edges, usually to existing nodes.

### T19. Morphological analysis with cross-consistency assessment

**Origin (sourced).** Developed in the 1940s by Fritz Zwicky at Caltech to investigate the totality of relationships in multi-dimensional, non-quantified problems. Parameters are set against each other in an n-dimensional "Zwicky box"; each cell is one configuration. Cross-consistency assessment then eliminates internally inconsistent configurations, and Zwicky's stricture is that only logical and empirical judgments should enter the assessment, not normative ones. ([Ritchey, "Fritz Zwicky, Morphological Analysis and Futures Studies", PDF](https://www.swemorph.com/pdf/gma.pdf), [Wikipedia](https://en.wikipedia.org/wiki/Morphological_box))

**Link kind.** `incompatible-with` and `compatible-with`, over pairs of option or configuration nodes.

**Verdict (excursion judgment).** Mechanizable in a restricted setting, and interesting because it is the only technique here whose output is *pairwise and exhaustive* rather than generative. Given a set of sibling options under a decision, every pair gets one binary question, which is deterministic in a way none of the "what does this remind you of" rules are. That makes it the easiest rule to evaluate: a wrong incompatibility claim is straightforwardly wrong. It only applies where the graph already holds several parallel options, so it is a narrow rule, and it is quadratic in the option count — cap it at small sets. Zwicky's "logical and empirical only, not normative" is a good prompt constraint verbatim.
**Cost:** n(n−1)/2 cheap calls for n options, or one batched call; yields compatibility edges across the option set.

### T20. McLuhan's tetrad

**Origin (sourced).** Marshall and Eric McLuhan, *Laws of Media: The New Science* (1988). Four simultaneous questions applicable to any technology or medium: what does it enhance, what does it obsolesce, what does it retrieve that was earlier obsolesced, and what does it reverse into when pushed to its limits? Their worked example for Xerox: enhances the speed of the printing press, obsolesces the assembly-line book, retrieves the oral tradition, reverses into everybody-becomes-a-publisher. ([McLuhan.org](https://mcluhan.org/the-tetrad/), [McLuhan Galaxy](https://mcluhangalaxy.wordpress.com/2014/10/10/the-laws-of-media-a-conceptual-tool-for-understanding-media/))

**Link kind.** `enhances`, `supersedes`, `revives`, `inverts-into`.

**Verdict (excursion judgment).** Mechanizable as a fixed four-question prompt on technology, tool and approach nodes, and it earns its place for one edge type the rest of the catalog misses entirely: `supersedes`. A memory graph that never records what a new approach obsoleted keeps recommending the old one. The retrieval question is the second-most-valuable and the least obvious — "what does this bring back that we'd abandoned" catches the cyclic return of old designs, which is exactly the pattern a long-lived memory should be able to see and a human usually can't. The reversal question is the most speculative and should be marked low-confidence.
**Cost:** 1 call with four sub-questions; yields 1–4 edges; `supersedes` usually binds to an existing node, the others may mint.

### T21. SCAMPER

**Origin (sourced).** Bob Eberle, *SCAMPER: Games for Imagination Development* (1971), built on Alex Osborn's idea-spurring checklist in *Applied Imagination* (1953). The acronym: Substitute, Combine, Adapt, Modify/Magnify/Minify, Put to other uses, Eliminate, Reverse/Rearrange. Originally for fostering imagination in children, later adopted in design and business. ([Wikipedia](https://en.wikipedia.org/wiki/SCAMPER), [Toolshero](https://www.toolshero.com/creativity/scamper-technique-bob-eberle/), [IfM on Osborn's checklist](https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/osborns-checklist/))

**Link kind.** `variant-of` and `derived-from`, linking a hypothetical alternative back to the original.

**Verdict (excursion judgment).** Mechanizable but not recommended for an autonomous edge-builder. Every one of the seven prompts mints a node describing a thing that does not exist and was never considered, so a single application can add seven speculative nodes to the graph. The purpose it was built for — generating options for a human to sift — is real, and it survives as an interactive ideation tool. As an unattended graph-growth rule it is a bloat engine: high volume, no truth condition, no natural stop. Scoped null for autonomous use; keep it as a human-invoked mode.
**Cost:** 1 call, 7 candidate nodes, nearly all speculative.

### T22. Assumption reversal and reverse brainstorming

**Origin (sourced).** Reverse brainstorming is attributed to Alex Osborn: identify ways to cause or worsen the problem, then flip the anti-solutions into fixes. The assumption reversal variant is credited to Stephen R. Grossman, former head of new product research at Scott Paper: list six to ten assumptions about the idea, state the reverse of each, and use the resulting insights as a springboard. ([Think Jar Collective](https://thinkjarcollective.com/tools/reversing-assumptions-technique), [Toolshero](https://www.toolshero.com/creativity/reverse-brainstorming/))

**Link kind.** `contradicts` against the node's own premises; `inverts` toward a mirrored alternative.

**Verdict (excursion judgment).** Partly mechanizable, and the useful half is the assumption-listing step, not the reversal. Enumerating a node's six to ten assumptions is the same operation as the Socratic assumption probe (T8) and produces the same `depends-on` edges to unstated premises — the difference is that Grossman's version demands a fixed count, which is a better prompt because it prevents the model from stopping at one. The reversal step then mints speculative nodes with the same bloat problem as SCAMPER. Take the enumeration, leave the reversal.
**Cost:** 1 call; yields 6–10 assumption candidates, of which the ones matching existing nodes become `depends-on` edges.

## Family G: random-stimulus rituals

### T23. Random entry and provocation (PO)

**Origin (sourced).** Edward de Bono coined "lateral thinking" in *The Use of Lateral Thinking* (1967). Random stimulation, set out in *Lateral Thinking: Creativity Step by Step* (1970), breaks established patterns by forcing cross-domain connections. PO — from hypothesis, suppose, possible, poetry — was introduced in *PO: Beyond Yes and No* (1972) as a marker signalling that a provocation is not a proposal to be judged but a stimulus for new perception. ([Wikipedia on Po](https://en.wikipedia.org/wiki/Po_(lateral_thinking)), [Peak Performance Center](https://thepeakperformancecenter.com/educational-learning/thinking/types-of-thinking-2/lateral-thinking/lateral-thinking-techniques/))

**Link kind.** Unconstrained: any edge type, between a node and a randomly drawn other node.

**Verdict (excursion judgment).** Trivially mechanizable to *run* and not mechanizable to *evaluate* — which makes it a scoped null as an autonomous rule. Drawing a random node pair and asking for a connection costs one call and always returns something, because a language model will always find a way to relate any two things. That is precisely the failure: there is no signal distinguishing a real cross-domain insight from a fluent confabulation, and de Bono's own PO marker exists to tell humans not to judge the provocation on its merits. Running it unattended fills the graph with plausible false edges, which is worse than no edges. It survives with a human in the loop, or gated behind a downstream usefulness signal (did anyone traverse this edge?) that the current design does not have. **This null kills random pairing under autonomous operation; it does not touch the rule-driven linking idea generally.**
**Cost:** 1 call, unbounded false-positive rate.

### T24. Oblique Strategies

**Origin (sourced).** A deck of cards by Brian Eno and Peter Schmidt, first published 1975, subtitled *Over One Hundred Worthwhile Dilemmas*. Each card offers a constraint intended to break creative block through lateral thinking. It grew from parallel projects — Schmidt's 1970 box of 55 letterpressed sentences, Eno's 1974 handwritten bamboo cards — merged in late 1974; the concept drew on the I Ching and on synchronicity. ([Wikipedia](https://en.wikipedia.org/wiki/Oblique_Strategies), [history at hyperreal.org](http://music.hyperreal.org/artists/brian_eno/osfaq2.html))

**Link kind.** None reliably.

**Verdict (excursion judgment).** Same scoped null as T23, and for the same reason. The deck's constraints are addressed to a person stuck in a studio and depend on a human's felt sense of what to do with an oblique instruction. There is no output type and no way to tell a good application from a bad one. Included in the catalog because the brief named it and because ruling it out sharpens the boundary: a linking rule needs a *stated output type*, and this is the clearest example of a celebrated technique that has none.

## Considered and set aside

**Kipling's 5W1H** — from the 1902 verse in *The Elephant's Child*: "I keep six honest serving-men … Their names are What and Why and When And How and Where and Who." Now standard in journalism, investigation and lean practice. ([t2informatik](https://t2informatik.de/en/smartpedia/5w1h-method/), [Velaction](https://www.velaction.com/5w1h/)) *Verdict: mechanizable but fills node attributes rather than making edges — a completeness checklist for a node's fields, not a linking rule.* Its Why branch is just T1.

**Six Thinking Hats** — de Bono, 1985; six perspectives (white facts, red feelings, black risks, yellow benefits, green creativity, blue process) worn by everyone at once, which he called parallel thinking. ([Wikipedia](https://en.wikipedia.org/wiki/Six_Thinking_Hats)) *Verdict: produces perspectives on one node, not relations between two. Black hat overlaps the pre-mortem (T4), which is the better-specified version of the same move.*

---

# Part 2 — The five to build first

Ranked by expected typed edges per unit of cost, weighted by whether the output can be checked without a human.

**1. The four-way relate check (T11, Ahrens/Zettelkasten).** Trigger: node creation. Retrieve the k nearest existing nodes, ask the single question "does this contradict, correct, support, or extend each of these," require a one-sentence justification per edge, and drop any edge whose justification the model cannot state. Maps to `contradicts` / `refines` / `supports` / `extends`. Build this first because it mints no nodes, needs no scheduler, and every edge it proposes is falsifiable.

**2. The four-direction compass (T15, Idea Compass).** Trigger: node creation or periodic sweep. One call, four fixed questions, answers constrained to existing nodes. Maps to `part-of` / `composed-of` / `analogous-to` / `contrasts-with`. Best edges-per-call in the catalog, and the only cheap source of contrast edges.

**3. Bounded causal descent (T1 + T2, 5 Whys with Ishikawa categories).** Trigger: nodes typed as problem, failure or incident. Depth capped at 3, each generated cause bound to an existing node when one matches, category list used to catch the multi-cause case that the linear chain misses. Maps to `caused-by`. The most valuable edges here and also the most dangerous rule, because it is the one that mints nodes at every step.

**4. Trade-off detection (T18, TRIZ detection half only).** Trigger: nodes typed as design, decision or change. One question: what does this improve, what does it cost, and is the cost already a node? Maps to `trades-off-against` / `constrained-by`. Low volume, high value, and no other rule produces this edge type.

**5. Structure-mapped analogy with systematicity scoring (T12, feeding T13).** Trigger: periodic batch, not write time. Retrieve candidates by shared *relational* pattern rather than by embedding similarity, align, and score by the count of higher-order relations preserved. Maps to `analogous-to` with a real numeric confidence; pairs that score high feed the consolidation rule (T13) that mints a schema node above them. Most expensive rule on the list and the only one with a principled ranking criterion.

**Honourable mention — the warrant-naming pass (T9, Toulmin).** Not an edge-discovery rule but an edge-*refinement* one: walk existing untyped edges and name the unstated warrant that licenses each. Cheap, and it upgrades the graph you already have instead of enlarging it. Worth a slot if edge quality turns out to matter more than edge count.

**Free with any of the above — the cross-link ranker (T17, Novak).** Prefer proposed edges whose endpoints are currently distant in the graph. It is a path-length query, costs no model call, and applies to the output of every rule above.

## Where the shortlist points on a typed graph

| Rule | Edge types produced | Mints nodes? | Checkable? |
|---|---|---|---|
| Four-way relate check | `contradicts`, `refines`, `supports`, `extends` | no | yes |
| Four-direction compass | `part-of`, `composed-of`, `analogous-to`, `contrasts-with` | no, if constrained | partly |
| Bounded causal descent | `caused-by` | yes, capped | partly |
| Trade-off detection | `trades-off-against`, `constrained-by` | rarely | yes |
| Structure-mapped analogy | `analogous-to` (scored), then `generalizes` | only the schema node | yes, via systematicity count |

Two edge types that nothing on the shortlist covers, in case they matter to the design: `depends-on` (T5, T6, T7 and T8 all produce it — the Feynman restatement test in T7 is the sharpest version), and `supersedes` (only T20, the McLuhan tetrad, produces it, and a long-lived memory that never records what replaced what will keep recommending superseded approaches).

---

# Part 3 — Scoped nulls

Recorded per the brief: each of these kills a *technique under this framing*, not the rule-driven linking idea.

- **Random pairing as an autonomous rule (T23, T24) fails.** Both are trivial to run and impossible to evaluate. A language model will relate any two nodes on request, so the rule has a 100% output rate and an unknown error rate. Both survive as human-invoked modes, and would become viable if the system ever gains a downstream usefulness signal — for instance, whether anyone later traversed the edge.
- **SCAMPER as an autonomous rule (T21) fails.** Seven speculative nodes per application, no stop condition, no truth condition. Survives as interactive ideation.
- **TRIZ's resolution half (T18) fails.** The 39 × 39 matrix and 40 principles are tied to physical engineering parameters and do not transfer to a software memory graph. The detection half survives and is on the shortlist.
- **The Feynman technique as written (T7) fails**, because it needs an audience and a felt sense of being stuck. The restatement variant — restate the node using only its linked neighbours' vocabulary, and treat every imported term as a missing edge — passes, and is the form recommended.
- **Four of the six Socratic categories (T8) fail** to produce edges; they improve a node's prose instead. The assumption and implication probes pass.
- **5W1H (Kipling) and Six Thinking Hats fail** as linking rules: the first fills a node's attributes, the second produces perspectives on a single node. Neither is relational.

## One caveat on the whole catalog

Every technique here was designed for a human mind with a limited working memory, and several of them work in humans *because* the effort of generation changes the person doing it — that is explicitly the finding in elaborative interrogation and self-explanation, where generating the explanation beats reading one. None of that transfers to an agent. What transfers is only the output: the edges the ritual names. So judge each rule on edge yield and edge correctness, never on the psychological effect its literature reports. The published effect sizes justify the *shape* of the question, not the benefit of running it.

---

## Sources

- [Five whys — Wikipedia](https://en.wikipedia.org/wiki/Five_whys)
- [The Origin of 5 Whys: How Toyota Revolutionized Problem-Solving](https://5xwhys.com/articles/5-whys/history-toyota/)
- [Five Whys: Root Cause Analysis for Problem Solving — Sloww](https://www.sloww.co/5-whys/)
- [What is a Fishbone Diagram? Ishikawa Cause & Effect Diagram — ASQ](https://asq.org/quality-resources/fishbone)
- [Ishikawa diagram — Wikipedia](https://en.wikipedia.org/wiki/Ishikawa_diagram)
- [Psillos, "An Explorer Upon Untrodden Ground: Peirce on Abduction" (PDF)](http://users.uoa.gr/~psillos/PapersI/11-Peirce-Abduction.pdf)
- [The relation of Peirce's abduction to inference to the best explanation — De Gruyter](https://www.degruyterbrill.com/document/doi/10.1515/css-2024-2022/html)
- [Klein, "Performing a Project Premortem"](https://www.researchgate.net/publication/3229642_Performing_a_Project_Premortem)
- [Pre-mortem: how to anticipate failure with prospective hindsight — Ness Labs](https://nesslabs.com/pre-mortem-anticipate-failure-with-prospective-hindsight)
- [Prospective hindsight research (Mitchell, Russo & Pennington 1989) — ScienceBlog](https://scienceblog.com/g-stay-a-step-ahead-premortem-technique-prospective-hindsight-research/)
- [Elaborative interrogation — Wikipedia](https://en.wikipedia.org/wiki/Elaborative_interrogation)
- [Elaborative Interrogation: What if Students Can't Produce Useful Elaborations? — The Learning Scientists](https://www.learningscientists.org/blog/2017/7/11-1)
- [Chi, De Leeuw, Chiu & Lavancher (1994), "Eliciting Self-Explanations Improves Understanding" — Cognitive Science](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1803_3)
- [Chi et al. (1989), "Self-Explanations: How Students Study and Use Examples" — Cognitive Science](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1302_1)
- [The Feynman Learning Technique — Farnam Street](https://fs.blog/feynman-learning-technique/)
- [Feynman Technique: A Complete Beginner's Guide — E-Student](https://e-student.org/feynman-technique/)
- [Paul & Elder, *The Thinker's Guide to the Art of Socratic Questioning* (PDF)](https://www.criticalthinking.org/files/SocraticQuestioning2006.pdf)
- [Six types of Socratic questions — University of Michigan](https://websites.umich.edu/~elements/probsolv/strategy/cthinking.htm)
- [Toulmin Argument Model — Write What Matters](https://idaho.pressbooks.pub/write/chapter/toulmin-argument-model/)
- [Toulmin Argument Model — UMW Speaking Intensive Program](https://academics.umw.edu/speaking/resources/handouts/toulmin-argument-model/)
- [Kunz & Rittel, "Issues as Elements of Information Systems" (1970, PDF)](http://magrawal.myweb.usf.edu/phd/articles/ibis_wp_70.pdf)
- [Conklin, "IBIS: A Tool for All Reasons" (PDF)](https://www.cognexus.org/IBIS-A_Tool_for_All_Reasons.pdf)
- [Different Kinds of Ties Between Notes — Zettelkasten Method](https://zettelkasten.de/posts/kinds-of-ties/)
- [Link types — Zettelkasten Forum](https://forum.zettelkasten.de/discussion/2023/link-types)
- [How to Take Smart Notes (Ahrens) — summary, Reading Graphics](https://readingraphics.com/book-summary-how-to-take-smart-notes/)
- [Gentner (1983), "Structure-Mapping: A Theoretical Framework for Analogy" — Cognitive Science](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0702_3)
- [Gentner & Markman, "Structure Mapping in Analogy and Similarity" (PDF)](https://home.csulb.edu/~cwallis/382/readings/482/GenterMarkman.pdf)
- [Gentner, Loewenstein & Thompson (2003), "Learning and Transfer: A General Role for Analogical Encoding" (PDF)](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf)
- [Loewenstein, Thompson & Gentner (1999), "Analogical encoding facilitates knowledge transfer in negotiation" (PDF)](https://groups.psych.northwestern.edu/gentner/papers/LoewensteinThompsonGentner99.pdf)
- [Pólya, *How to Solve It* (full text PDF)](https://www.hlevkin.com/hlevkin/90MathPhysBioBooks/Math/Polya/George_Polya_How%20to%20Solve%20It.pdf)
- [Pólya, *How to Solve It* — Northeastern summary](http://www.ccs.neu.edu/home/lieber/courses/csu670/f04/materials/problem-solving/G_%20Polya,%20How%20to%20Solve%20It.htm)
- [How to connect your notes (Idea Compass, McLuhan tetrad) — Writing Slowly](https://writingslowly.com/2023/08/27/how-to-connect.html)
- [Enter the Idea Compass — Zahler Design](https://www.zahlerdesign.com/blog/enter-the-idea-compass)
- [Zhao & Tseng, "The Compass of Zettelkasten Thinking" — Linking Your Thinking Conference](https://www.linkingyourthinking.com/lytcon/vicky-and-fei-compass-of-zettelkasten-thinking)
- [Use a repertory grid — Emerald Publishing](https://www.emeraldgrouppublishing.com/how-to/observation/use-a-repertory-grid)
- [Repertory grid technique — EduTech Wiki](https://edutechwiki.unige.ch/en/Repertory_grid_technique)
- [Novak & Cañas, "The Theory Underlying Concept Maps and How to Construct and Use Them" (PDF)](https://cmap.ihmc.us/publications/researchpapers/theoryunderlyingconceptmaps.pdf)
- [40 principles of invention — Wikipedia](https://en.wikipedia.org/wiki/40_principles_of_invention)
- [TRIZ Matrix — TRIZ Consulting Group](https://www.triz-consulting.de/about-triz/triz-matrix/?lang=en)
- [Ritchey, "Fritz Zwicky, Morphological Analysis and Futures Studies" (PDF)](https://www.swemorph.com/pdf/gma.pdf)
- [Morphological analysis (problem-solving) — Wikipedia](https://en.wikipedia.org/wiki/Morphological_box)
- [McLuhan's Tetrad unveiled — McLuhan.org](https://mcluhan.org/the-tetrad/)
- [SCAMPER — Wikipedia](https://en.wikipedia.org/wiki/SCAMPER)
- [SCAMPER Technique (Bob Eberle) — Toolshero](https://www.toolshero.com/creativity/scamper-technique-bob-eberle/)
- [Osborn's checklist — Institute for Manufacturing, Cambridge](https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/osborns-checklist/)
- [Reversing Assumptions Technique — Think Jar Collective](https://thinkjarcollective.com/tools/reversing-assumptions-technique)
- [Reverse Brainstorming explained — Toolshero](https://www.toolshero.com/creativity/reverse-brainstorming/)
- [Po (lateral thinking) — Wikipedia](https://en.wikipedia.org/wiki/Po_(lateral_thinking))
- [Lateral Thinking Techniques — Peak Performance Center](https://thepeakperformancecenter.com/educational-learning/thinking/types-of-thinking-2/lateral-thinking/lateral-thinking-techniques/)
- [Oblique Strategies — Wikipedia](https://en.wikipedia.org/wiki/Oblique_Strategies)
- [History of the Oblique Strategies — hyperreal.org](http://music.hyperreal.org/artists/brian_eno/osfaq2.html)
- [The 5W1H Method — t2informatik](https://t2informatik.de/en/smartpedia/5w1h-method/)
- [5W1H, the Kipling Method — Velaction](https://www.velaction.com/5w1h/)
- [Six Thinking Hats — Wikipedia](https://en.wikipedia.org/wiki/Six_Thinking_Hats)
- [Evergreen notes should be densely linked — Andy Matuschak](https://notes.andymatuschak.org/Evergreen_notes_should_be_densely_linked)
- [LLM-empowered knowledge graph construction: a survey (2025)](https://arxiv.org/html/2510.20345v1)
