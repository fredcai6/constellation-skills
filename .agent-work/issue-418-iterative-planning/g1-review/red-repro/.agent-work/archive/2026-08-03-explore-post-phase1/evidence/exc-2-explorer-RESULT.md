# exc-2-explorer — target architecture and longer-term vision from `explore-grander-scale`

**The one named question:** What target architecture and longer-term vision did the explore-grander-scale run (closed 2026-07-31) confirm or discuss-but-not-cut, and what does its own record imply the natural next step is?

**Verdict in one line:** The run confirmed a two-stratum design — a long-arc vision (Stratum A) that was deliberately *never cut*, and a near-term instruction-system slice (Stratum B) of which only B1+B3 were built; the record's own gating language now points at one unlocked next step (federation/idea-substrate, whose stated precondition "local map use is proven" was met by #307's PASS) and three explicitly-stalled ones (B2's kernel break, B4's context queries, and B1's never-run first consolidation).

---

## 0. Sources examined, and scoped nulls

**Examined (primary):**
- `C:/Programs/constellation-skills/.agent-work/archive/2026-07-31-explore-grander-scale/DESIGN_SPEC.md` — 226 lines, read in full (Confirmation, Intent, Exploration record, Chosen design incl. Stratum A and B0–B4, Load-bearing interfaces, Assumptions, Testing pathways, Out of scope, and the 65-row critic disposition table).
- `.../IDEAS_BOARD.md` — 556 lines; read the Point, Current candidates, Verdicts (46 rows), Open threads, the full "Excursion findings: recursive learning without instruction accretion" block (lines 348–545) incl. the Consolidated next-step roadmap, High-value tracer question, Open tensions, Durable reports, Rejected ideas, Cycle log. **Not read line-by-line:** the eight Excursion Brief blocks at lines 118–347 (each a question/type/budget scaffold for an excursion whose *findings* I did read).
- `.../filing-receipt.json` — the twelve issues (#299–#310) + epic #298 cut from the spec.

**Examined (secondary, read-only):**
- `gh issue view` on #298, #299–#310 (titles/states via `gh issue list --state all --limit 300`, bodies on #302, #307, #308, #309, #310), plus follow-ons #331, #392, #414, #415, and the context issues #297, #219.
- Comment threads on #302, #307, #308, #310 (verdicts live in comments, not bodies).
- `git show epic-298/310:.agent-work/archive/2026-08-02-issue-310/B2_GATE_EVIDENCE.md` — the B2 verdict packet, which is **not on `main`**.
- `.agent-work/epic-298/EPIC_SUMMARY.md` and `.agent-work/epic-298/BACKLOG_ROUTING.md` on `main`.

**Scoped nulls — examined and found absent, or deliberately not examined:**
- **`docs/ROADMAP.md` does not exist.** `ls docs/ROADMAP.md` → `No such file or directory`. Per issue #219 it "was retired 2026-07-24 (very out of date — most threads shipped)"; its surviving forward threads are in #219 itself, which I did read.
- The three durable excursion reports the ideas board links (`recursive-agent-learning.md`, `institutional-doctrine-learning.md`, `policy-architecture-accretion.md`) are cited at `.agent-work/explore-grander-scale/evidence/` — a **pre-archive path that no longer exists**. Their conclusions survive digested in the ideas board and the spec's Exploration record, which is what I used. I did not hunt for the moved files.
- `.agent-work/archive/2026-07-31-explore-grander-scale/{crew-runs.json, cycle-1.json, cycle-2.json, spine.json, issue-set.json, findings-comment.md, evidence/, triage-candidates/}` — not read. The design conclusions they support are all present in the spec and ideas board.
- Epic #298's *closeout* record (`ADMIRAL_LOG.md`, `LESSONS_AUDIT.md`, `ARCHITECTURE_RECONCILE.md`) — deliberately left to `exc-1-epic298`. I read `EPIC_SUMMARY.md` and `BACKLOG_ROUTING.md` only because the "implied next step" question cannot be answered without knowing what cut 1 actually delivered.
- I did **not** run `gh` writes of any kind, and made no edits outside this file.

---

## PART A — CONFIRMED SPEC CONTENT

Everything in Part A is from `DESIGN_SPEC.md`, whose header reads:

> **Status: CONFIRMED** · Confirmed by: Tommy · Date: 2026-07-31 · Critic findings dispositioned: YES — 65/65 (52 EDIT applied, 13 REJECT with reasons, 0 RE-EXPLORE)

Per-section approval is recorded individually (spec lines 107–119): Intent, Exploration record, Stratum A, B0, B1, B2 (incl. the kernel-plus-fragments delta), B3, B4, the load-bearing-interface deferral, Testing pathways (*"approved… noted lukewarm"*), and Out of scope — each "approved (Tommy, 2026-07-31)".

### A1. The spec is deliberately two strata, and only one of them is buildable

> *"The design is one spec in two strata. **Stratum A is direction: it constrains and orients but is not cut into issues.** **Stratum B is the actionable design: it is what gets cut.** Every Stratum B element must be buildable without committing to any Stratum A implementation, and must not foreclose it — and this is checked, not aspirational: the to-issues cut review includes an explicit per-element foreclosure check against Stratum A."* — spec line 43

This is the single most important structural fact for the excursion question: **the target architecture was confirmed, but confirmed as orienting direction that was explicitly forbidden from being cut into issues.** "Confirmed" and "cut" are different states here, and the spec keeps them apart on purpose.

### A2. Stratum A — the confirmed long-arc target architecture (CONFIRMED, explicitly NOT CUT)

Header: *"Stratum A — the long-arc vision (orienting context; DO NOT CUT into issues)"* (spec line 45). Seven elements, quoted in condensed form:

1. **A shared substrate, globally networked, locally structured.** *"The wider knowledge network has no mandatory spine; bounded subnetworks (project frames, a book, a philosophy region) may declare a local spine, schema, invariants, and completion rules when their purpose earns rigor. Frames are deliberately declared, with explicit overlapping membership — never exclusive containment."*
2. **One assertion truth model.** *"All truth claims — code structure, historical fact, personal belief, philosophical argument, cross-project analogy — use the same mechanics: an identified assertion with source, supporting and challenging evidence, and a qualitative weak/medium/strong assessment that allocates trust-but-verify attention and creates no inertia against decisive new evidence. Belief strength and lifecycle standing (disputed, superseded, rejected) remain separate dimensions. This paragraph is the model's one home in this spec; the deferred detailed mechanics live on the ideas board."*
3. **Maps are a frame-local construct, tuned to the present.** *"A map is how a frame keeps honest track of existing artifacts that change over time… the map holds strictly what currently is: navigating it never requires reconstructing history… How that non-map material is organized is deliberately unfixed — separate layers, a combined timeline view of an idea as it was and will be, or something finer-grained. The wider network is not map-shaped… A map may answer 'why must this exist?'; 'why is it this way?' is not map material."*
4. **Confederated agents with home frames.** *"A home frame is an explicit instantiation input supplying starting context, purpose, vocabulary, protocol, tools, and authority — an initialization and jurisdictional anchor, not a position."*
5. **Project truth federated into an idea commons.** *"Project frames own honest operational maps of what exists; a wider cross-project commons connects them with looser notes, concepts, questions, and proposed relationships — shared graph mechanics, distinct epistemic and mutation rules."*
6. **Git-native authored truth.** *"The human-reviewable, diffable representation stays canonical; derived indexes, visualizations, and database projections are reproducible accelerators, never a second truth."*
7. **Human-directed autonomy.** *"Human primacy is authority, not a universal approval gate: agents hold genuine delegated room to traverse, propose, verify, and act inside explicit envelopes; intent, values, contested interpretation, and consequential promotion remain deliberately human."*

The Intent frames Stratum A's role precisely:

> *"The long-arc stratum is not cut; it orients and constrains what is built now so the near-term work grows toward the substrate rather than away from it."* — spec line 22

### A3. The five anchoring purposes (CONFIRMED)

> *"Five purposes anchor it: personal experimentation; honest project maps that serve both agent action and human understanding; a cross-project network where accumulated material forms unexpected ideas; genuine agent autonomy under human primacy; and revision-controllable graph history."* — spec line 20

And the value framing that governs all of it:

> *"This is a personal experimentation project. Its value is enabling ideas, learning, and enjoyment; it has no utility-based kill condition and does not need to outperform ordinary notes. Tommy builds it himself as a learning playground."*

### A4. The confirmed cut scope — one sentence, unambiguous

> *"Scope of this cut, stated plainly: **B1 and B3 are the deliverables.** B2's kernel-plus-fragments break is **conditional** — it proceeds only if the evidence gates in B2 are met. B4 is **not in this cut**; its earning trigger is stated in B4."* — spec line 24

And the halving of the thesis, added by critic finding IF02:

> *"'Done' for this spec is narrower than the vision, and deliberately tests only half of it. This cut builds the **instruction-system half**… The **idea-substrate half** — where ideas themselves, not run defects or code facts, acquire structure — is an expected later problem: no near-term element builds it, and the near-term elements are required not to foreclose it."* — spec line 22

### A5. B0 — governing principles (CONFIRMED, normative on every B element)

1. **Sensors and actuators — the stochastic boundary.** *"LLMs are sensors: they notice, judge, propose, consolidate. Mechanisms are actuators: they assemble, route, enforce, repeat… stochastic work happens **upstream of canon**, where its output lands as reviewable, attributable change to canonical truth; between canonical truth and an agent's active surface, every transformation is deterministic and attributable."*
2. **Collate before reacting.** *"A single observation never triggers its own doctrine patch. Observations accumulate in a durable, queryable form; consolidation acts on clusters that rhyme."*
3. **The two-bin rule.** *"For any doctrine item, ask: can we afford to observe this failing once? If yes, it lives as prose and is always eligible for experimental pruning under a tripwire. If no, it is mechanized (validator, hook, gate) and its prose version is deleted because the mechanism owns it. A mechanization always carries a pointer to its motivating rationale and episodes."*
4. **Reviewed always; by human eyes when it counts.** *"independent agentic review is the standing floor, not a fallback, and its **depth scales with consequence class**."*

### A6. B1 / B2 / B3 / B4 as confirmed, and where each stands after cut 1

| Element | Confirmed status in spec | State as of 2026-08-03 | Evidence |
|---|---|---|---|
| **B1 — one observation framework** (lessons + Curator sweeps unified; durable queryable episodes; collate-before-react; pre-learning tripwires; Curator owns corpus coherence) | **Deliverable of this cut** | **Built, loop not closed.** 23 lessons migrated to episodes, store at 32 active, playbook retired, cap dropped, live agents cut off from lessons. **No consolidation ever landed.** | #301, #305, #308 closed; #308 close comment; #392 |
| **B2 — kernel + just-in-time fragments** | **Conditional** on two conjunctive evidence gates | **`not-yet-earned`.** Gate (b) n=0; conjunction cannot close; `break-proceeds` foreclosed by logic, not by numbers | `B2_GATE_EVIDENCE.md` §2, §7; #310 closed 2026-08-03 |
| **B3 — map-first tracer** | **Deliverable of this cut** | **PASS, adjudicated by Tommy 2026-08-02.** `map_before_src` 0/4 → 4/4 | #307 close comment: *"VERDICT: PASS — Tommy, 2026-08-02"* |
| **B4 — deterministic context queries** | **Explicitly NOT in this cut**, with a named earning trigger | **Untouched.** Trigger not met | spec line 101 |

**B2's gates, verbatim** (spec line 77) — the wording matters because the B2 verdict turns on the word *and*:

> *"The break proceeds only if (a) the corpus-size trend from git shows deletion alone is not getting the always-loaded role surface small enough, and (b) a role-competence test shows an agent operating from kernel-plus-fragments-plus-artifacts completes a representative mid-spine step as correctly as one holding the monolith. **If deletion alone suffices, the break is not taken — that outcome is success, not failure.** If the break proceeds, a generated **human-readable whole-role projection** is a required view."*

**B4's earning trigger, verbatim** (spec line 101):

> *"B4 is built only when B3's evidence shows both that map-first orientation works (the map finds seams) **and** that agents demonstrably need multi-hop context assembly beyond what the B2/B3 projections already deliver — i.e., manifests/transcripts show agents chaining map lookups by hand. Until then it is design direction, not work."*

The first conjunct is now satisfied (#307 PASS). **The second has no evidence either way** — nothing in the epic-298 record analyses transcripts for hand-chained map lookups. B4 is therefore *half-earned and unmeasured on the other half*, which is a cheap, well-specified next measurement rather than an open design question.

### A7. Confirmed out-of-scope, each with its own re-entry condition

Quoted from spec lines 148–156, because these are the confirmed *doors* to the longer-term vision:

- *"Graph database adoption (Neo4j or any backend) — deferred until the generated Markdown projection shows real query, maintenance, concurrency, or scale pressure."*
- *"Federation across project maps and the cross-project idea commons — Stratum A; **revisit after local map use is proven**."*
- *"A general query language (Cypher-like or otherwise) — one parameterized recipe with named presets only."*
- *"The idea-substrate half of the vision (ideas themselves acquiring structure) — expected later work."*
- *"Ontology expansion of the Cartographer map — the audit found the ontology is not the weakness."*
- *"ActiveGraph adoption in any form."*
- *"Assertion-strength mechanics, cross-frame mutation rules, and home-frame implementation — preserved on the ideas board for a future exploration."*
- *"Success/clean-use telemetry beyond mechanism byproducts — new watching infrastructure must earn its way in via a specific question."*
- *"Collation mechanization details ('things that rhyme') — explicitly deferred by Tommy as an implementation detail to iterate on."*

### A8. Confirmed assumptions and their current disposition

The spec enumerates six (lines 126–131). Current state:

| # | Assumption | Spec status | Now |
|---|---|---|---|
| 1 | Run artifacts carry sufficient state for a kernel+fragments agent | Untested; gated behind B2 role-competence test | **Still untested — n=0.** #414: relaunch runs "hold the always-loaded surface *constant*… the treatment was never varied" |
| 2 | The spine is the right selector for spine-driven work | Grounded in engine behavior | Unchanged; generalization to non-spine frames still deferred |
| 3 | An LLM can reliably find rhyming episode clusters | Untested; "the collation exercise required by 'done' is its first test" | **Partially exercised, positively.** #308: an independent cold sensor found 2 strong clusters over 7 episodes and *"independently rediscovered patterns `LESSONS.md` already holds, by a different route with no access to it"* |
| 4 | Manifests + transcripts suffice for map-use observability | Untested; B3's measurement is its first test | **Held.** #307 recovered ordering from transcripts; no access trace was needed |
| 5 | Deterministic recipes can express real working sets | Partially grounded | Exercised by B3's `map_orient.py` |
| 6 | Every catastrophic-class invariant is mechanizable | Untested; inventory pending, Tommy owner | **Adjudicated and closed.** #302: *"Ruled: no third bin. Assumption 6 stands, B0.3 unchanged."* Tommy verbatim: *"machinize the mechanizable. we don't need stochastic reasoning for predictable logic… these are aspirations."* Inventory: 16 invariants, 8 mechanism-owned, 8 prose-only |

---

## PART B — DISCUSSED BUT NOT CONFIRMED INTO THE CUT

Everything in Part B is from `IDEAS_BOARD.md`. It is the exploration's working record; material here was *not* elevated into the confirmed spec unless it also appears in Part A. Several items are considerably more specific than the spec's Stratum A paragraphs, which is exactly why they were left on the board.

### B1. The seven-step "Consolidated next-step roadmap" (ideas board lines 511–523)

This is the exploration's own most explicit statement of a target architecture and a build order. It was written *before* the spec was cut and only partially survives into it.

> *"The immediate objective is not a universal knowledge platform or graph database. It is one closed vertical slice proving that Constellation skills can natively enter, consume, and improve a shared graph."*

| # | Roadmap step (condensed quote) | Survived into the cut? |
|---|---|---|
| 1 | **"Name the minimum graph contract."** Stable IDs for architecture/skill/spine-node/policy/verification/evidence nodes; *"Compile and validate a generated adjacency projection rather than hand-maintaining a second truth"* | **No.** No node-ID scheme or adjacency projection was cut. B2's projection generator (#300) is doctrine-shaped, not graph-shaped |
| 2 | **"Make one skill path graph-native."** *"Use Commander `context -> plan` as the tracer"* | **Partly — as B3.** The tracer shipped, but as a prose contract + `map_orient.py`, not as typed graph links |
| 3 | **"Provide deterministic context queries."** *"orient to capability, recover prerequisites, find governing policy, and find verification surfaces"* | **No — this became B4**, explicitly out of the cut |
| 4 | **"Make graph use observable."** *"Every produced context packet gets an identity/manifest recording graph revision, seeds, recipes, nodes, edges, and source sections"* | **Yes, in reduced form.** Manifests exist (#300); the graph-revision/seed/edge fields do not |
| 5 | **"Capture structured feedback episodes."** | **Yes — this became B1** (#301, #305) |
| 6 | **"Turn Curator into the evolution boundary."** Propose `NO_CHANGE / INSERT / AMEND / MERGE / SPLIT / RELINK / RETUNE_RETRIEVAL / RETIRE` | **No.** The spec kept "Curator owns corpus coherence and the evolution boundary" as prose; the mutation vocabulary was never cut. #309 exercised the sweep only |
| 7 | **"Generalize only after the loop works."** *"Expand to other spine nodes and roles, then project/frame types such as the idea commons, journal, and philosophy. Revisit Neo4j/Cypher or another backend only when the generated Markdown projection exhibits real query, maintenance, concurrency, or scale pressure."* | **Not started** — and this is the record's own sequencing rule for everything in Part B |

The roadmap's closed-loop success criterion, quoted in full because it is the tightest statement of the target architecture anywhere in the record:

> *"`graph-authored current truth -> skill-native bounded traversal -> targeted work -> structured episode evidence -> Curator mutation proposal -> improved future traversal`, with every transition inspectable and revision-controlled."*

**Of that six-link chain, cut 1 delivered links 3 and 4** (targeted work, structured episode evidence) and a prose-shaped link 1. Links 2 (bounded traversal) and 5 (Curator mutation proposal) do not exist.

### B2. Skills and architecture as one operational graph (ideas board lines 445–467) — discussed, never cut

> *"The prior separation between 'how to work' skills and 'how the world works' architecture appears artificial. They are different modalities in one connected substrate."*
>
> *"A skill need not be a self-contained prose island. It can be an entry node plus a traversal contract."*
>
> Candidate relations: *"`ORIENTS_WITH`, `APPLIES_TO`, `GOVERNS`, `CONSUMES`, `PRODUCES`, `VERIFIES`, `MAINTAINS`, `IMPLEMENTS`, `DEPENDS_ON`, and `SUPERSEDES`. Their value is not ontology completeness but explicit multi-hop traversal such as: `plan node -> map-intake capability -> architecture index -> affected capability -> structural anchors -> governing constraints -> verification surfaces`."*

Nothing in Stratum A or B carries this. It is the most substantial piece of target architecture that exists only on the board.

### B3. Tool-mediated traversal, not document hopping (lines 469–485) — discussed, partially compressed into B4

> *"The graph should be **queried, not manually read**… A candidate Constellation query result should expose the route, not merely an answer or opaque bundle."*
>
> *"In a Markdown-first version, Markdown is the authored source of record; a generated node/edge index is the database-like projection; a deterministic traversal library is the query engine; and an optional small agent translates conversational intent into a strict query request. The agent may choose anchors and traversal recipes, but should not perform the hop-by-hop crawl itself."*

B4 preserved the *named-recipe* idea and the anchor-resolution rule; it dropped the adjacency index and traversal library entirely.

### B4. Concern ownership, module shapes, and the role/context/agent boundary split (lines 393–443) — discussed, never cut

Four module shapes named (knowledge / policy-aspect / capability-subskill / role-orchestrator), five boundary criteria from prior art (Parnas, DDD, RL options, AOP, evolutionary coupling), and:

> *"A candidate concern earns an independently loadable subskill only if its trigger, output/termination, failure behavior, canonical owner, and independent behavioral evaluation can be stated without replaying the parent role. Otherwise it likely belongs as a reference inside a skill, a shared policy/rail, or a knowledge interface. Extraction that creates only a pointer and still requires the caller's whole internal model is a shallow split."*

> *"Keep three boundaries independent: **Module boundary** … **Context boundary** … **Agent boundary**."*

This is the design content B2 would have needed and never got. It is directly relevant to the B2 gate stalemate (Part C).

### B5. SkillGraph's evolution loop (lines 487–509) — discussed, never cut

> *"Its maintenance vocabulary directly addresses instruction accretion: failure can insert a missing skill; overlapping neighborhoods can nominate a merge; high-use/low-success skills can be split… Total knowledge may continue growing while the active set and retrieved context remain bounded."*
>
> *"For Constellation, this suggests two distinct compilation concerns. An **evolution curator**… and a **context compiler**…"*
>
> Scoping caveat carried by the board itself: *"Transfer is suggestive, not demonstrated. SkillGraph is an arXiv v1 evaluated in simulated, single-environment settings."*

### B6. Density is three problems (lines 360–366) — discussed; the spec absorbed only part

> *"**Runtime density**… **Structural density**… **Evolutionary density**… Shorter prose or richer tags do not solve all three. Shared references can reduce literal duplication while worsening structural density; retrieval can reduce tokens while leaving conflicts and stale rules intact."*

B2 attacks runtime density; B3 attacks structural density for one contract. **Evolutionary density has no near-term element at all** — the roadmap's step 6 (evolution curator) was the answer and was not cut.

### B7. Open threads still standing (lines 95–116)

Current high-level orientation (five questions), of which cut 1 answered two:

- *"Which real project and task set should serve as the representative dogfood corpus?"* — **answered** by #299
- *"What is the lightest evidence that an agent used the map to choose a seam before opening source?"* — **answered** by #307 (transcript ordering)
- *"What is the smallest canonical map-input contract the orchestrator can consume directly?"* — **answered** by #304
- *"What map-health signal would reveal likely drift without pretending a changed file proves a claim false?"* — **partially**: #306 mechanized projection drift; the spec kept *stale/contradictory map* detection as an **open thread**, not a claimed guarantee (spec line 92)
- *"What is the smallest federation seam that connects project-owned maps without weakening their local structural spines?"* — **untouched**

Plus twelve deferred detail questions (assertion strength, verification order, cross-frame mutation, home-frame multiplicity), which the board explicitly ranks below the support-system work:

> *"The more detailed assertion-strength, verification-order, and cross-frame mutation questions below remain preserved, but should not drive the next pass until these support-system pressures are exercised."* — line 103

**Those support-system pressures have now been exercised.** That sentence is a dated release condition, and cut 1 satisfied its antecedent.

### B8. Resolved tensions with named residuals (lines 531–538)

All six open tensions were resolved on 2026-07-31. Three left explicit residuals that are still open:

- *"Residual: which adversarial viewpoints the coherence-hunting subagents should take, and on what cadence."*
- *"Residual: concrete recipe format and manifest shape."*
- *"Residual, explicitly deferred as an implementation detail to try something on: how to mechanize collation — ensuring observations that rhyme get grouped toward a single solution rather than each triggering its own patch."*

The third residual is the one that bit (Part C2).

### B9. Rejected, with reasons (lines 546–549)

> *"**Immediate Neo4j crawl experiment** - deferred, not permanently rejected… Revisit only after observed navigation, maintenance, or connection-building pressure."*
> *"**Adopting ActiveGraph** - rejected for this exploration… no implementation or future-runtime presumption should be carried forward."*

Also rejected in the spec's Exploration record: *"a universal knowledge platform as the first deliverable (the first deliverable is one closed vertical slice)"*; *"numeric instruction budgets"*; *"a general graph query language now"*.

---

## PART C — WHAT THE RECORD ITSELF SAYS THE NEXT STEP IS

Quoted, not inferred. Four independent statements point in four different directions; I state each and then give my read of how they compose.

### C1. Federation's stated precondition has been met — and nothing has acted on it

The spec defers federation with a condition attached:

> *"Federation across project maps and the cross-project idea commons — Stratum A; **revisit after local map use is proven**."* — spec line 149

The Scout audit ranked the same thing fourth of four pressures:

> *"Four support pressures outrank detailed truth behavior: establish a representative dogfood map; make map consumption observable and anchors resolvable; surface semantic drift/staleness; and **add federation above local project maps only after local use is proven**."* — ideas board line 82

**Local map use is now proven** — #307's close comment: *"VERDICT: PASS — Tommy, 2026-08-02… The B3 map-first pathway passes. #304's contract does what it was built to do."* with `map_before_src` 0/4 → 4/4 and attribution established (*"`scripts/map_orient.py` did not exist before `5d2585b` (#304)"*).

This is the only gating condition in the whole record that flipped from unmet to met. **It is also the door to the half of the vision the spec says it deliberately did not test** — the idea substrate, the cross-project commons, the journal/philosophy frames. The record contains no statement that anyone has noticed this.

Two bounds the record itself insists on carrying, both from #307's own verdict, and neither should be dropped when citing the PASS:
1. *"the corpus manipulation was `74953936` → `3595955` — **8 days and +31 files, not #304 alone.** `merge-base` proves containment, not exclusivity. The existence of the effect is attributable. The magnitude is not."*
2. *"'map-first' as delivered means **first-among-content, not first-among-actions**"* — `read_at_bootstrap` was 0/4 in **both** arms.

### C2. The B1 loop was built but has never closed — no consolidation has ever run

This is the sharpest unfinished thing in the cut, and it is a departure from the spec's own definition of done. The spec (as amended by critic finding IF01) requires:

> *"a reworked lessons framework (B1) in which observation is collated before reaction — **exercised by at least one consolidation acting on a collated cluster, not just a full store**"* — spec line 22

IF01's disposition made this binding: *"'Done' now requires at least one consolidation acting on a collated cluster; collation mechanics stay deferred but the behavior is exercised."*

**Collation was exercised and worked. Consolidation was cut.** #308's close comment lists under *"Superseded"*: *"**Half 1's consolidation** — no mechanization change, no instruction change, no bin ruling."* On Tommy's ruling, quoted in the issue: *"just go to episodes. no doctrine updates."* The stated reason:

> *"The store holds 7 episodes plus whatever migrates from 20 lessons — **not enough accumulated recurrence to judge from.** Landing a doctrine change on that basis would be a local call dressed as a global one."*

And the underlying reframing, Tommy verbatim in #308:

> *"there are no catastrophic failures, just workarounds and inefficiencies… fundamentally the thing that is finding the episodes cannot make a call on the importance, that requires a more global view. it is not smart to ask our lower level agents to diagnose. we just want observations of what happened and how they worked around it."*

What the collation half did produce, and it is positive evidence for assumption 3:

> *"An independent cold sensor — fresh context, given the 7 episodes, no hypothesis, explicitly authorised to return 'no cluster' — found **2 strong clusters**, and was run *before* the commander recorded its own read… Both clusters **independently rediscovered patterns `LESSONS.md` already holds**, by a different route with no access to it."* (#308)
>
> *"A solo read missed one of the two clusters."* — and #392 generalizes this: *"**one read is not enough to trust a null on any individual cluster.**"*

One strong cluster sits filed and deliberately unconsolidated as **#392** (*"a check that cannot register its own failure"*). The store is at **32 active episodes**, up from 7.

**The implied next step is stated by the reason for the deferral, not by a plan:** consolidation waits on accumulated recurrence. Nothing in the record names how much is enough, who checks, or on what trigger. That is an unowned gap, not a scheduled step.

### C3. B2 is blocked on one unrun arm, and two questions handed to Tommy

`B2_GATE_EVIDENCE.md` §7:

> *"**`SELECTED-OUTCOME: not-yet-earned`** — *keep deleting, re-evaluate in a follow-on.* **Selected by gate (b), and by nothing else.** Gate (b) was never run; the gates are conjunctive; a conjunction with an unrun conjunct cannot close. **`break-proceeds` is therefore not selectable, and the break is not earned.** *This argument uses no unit, no threshold and no number.*"*

§8, "What is actually being asked of you":

> *"1. **The unit** — bytes, lines, or words? … 2. **The threshold** — once a unit exists, what is 'small enough'…? 3. **Whether gate (b) is ever worth buying** — #414 says what it costs."*

And the open question the commander explicitly refused to rule:

> *"the corpus's existing three-bin shape — `SKILL.md` as trigger/pointer, `references/` as doctrine, `templates/` as interface — is **already kernel-shaped**, and #307 showed per-task delivery through the spine template moving behaviour that always-loaded delivery could not. It is possible B2's content axis is further along under a different name than 'unstarted' suggests, and that the remaining work is a **selector and a naming** question rather than a re-architecture. **I am not ruling on that. It is a durable-structure choice and it is yours.**"*

#414 carries the standing consequence:

> *"Until this arm (or an equivalent) runs, **gate (b) is unsatisfiable, the B2 conjunction cannot close, and `break-proceeds` is not selectable by any amount of trend evidence.**"*

…and the correction that makes it cheap: *"'You cannot test the break without building the break' is FALSE… **An ablation needs zero authoring of a decomposition.**"* Cost is specified: Commander, a mid-spine step, ≥4 runs per arm, reuse `discriminate.py` and the existing `RUBRIC.md`, no rebuilt scorer.

Tommy's scope ruling on that whole class, quoted in both #414 and #415:

> *"that seems like we're making our life hard to come up with metrics too early. right now we're just reworking the substrate, we're not aiming to idealize any particular metric."*

#414 accepts this may apply to itself: *"**Reason 2 may well apply to this arm too** — it is a measurement, and the substrate is in flux. This issue does not argue that the arm should be run now."*

### C4. A structural precondition on B2 that outlives the metrics question

`B2_GATE_EVIDENCE.md` §4 — and `EPIC_SUMMARY.md` promotes this to one of the epic's two findings that *"constrain what you build next"*:

> **The fact:** *"at `9a90298`, of **21** named reference tokens across the corpus, **10 do not resolve inside the citing role's own directory.**"*
>
> **The inference, labelled as one:** *"if that holds, a role's always-loaded surface cannot be computed from the role's local files, and **you cannot decompose a role into fragments if you cannot determine what the role loads.**"*
>
> *"**This is not a metrics finding and it does not die with the census.**… any kernel/fragment split has to answer *'what does this role actually load?'* first, and today that answer requires resolving through the installer's bundle table (`SKILL_REFERENCE_BUNDLES`), which only exists after a regime boundary partway through the corpus's life. **It bears directly on the substrate rework in flight.**"*

`EPIC_SUMMARY.md` adds a denominator disagreement that is itself a finding:

> *"**10 of 21 as the commander measured it; 29 of 46 when the auditor re-derived it independently.** Same finding, different denominator, because they tokenized differently. **That disagreement is the second finding in miniature.** Even the corpus's own count of its references is unit-dependent."*

### C5. The record's own routing advice for what comes after

`BACKLOG_ROUTING.md`, closing section:

> *"**Everything else is ordinary backlog and should be triaged against the Stratum A vision, not against its own severity.** Most of B, D, E, F, G are instrumentation for a measurement apparatus this epic built. **If the next arc is architectural, an instrument's defect is not worth fixing until the instrument is next used.**"*
>
> *"**The honest read:** this epic's real output is the doctrine in C and the two measured results (#307's 0/4→4/4, #308's 23 episodes with 11 unknowns preserved). The other ~65 issues are the *sediment* of producing those. Triaging them by asking 'is this worth fixing?' one at a time will keep all of them. **Ask instead: *which of these does the next arc actually walk through?***"*

Tommy's own words, quoted there: the issues *"seem navel gazy and not necessarily worth the fix while we're still doing big architectural overhauls."*

`EPIC_SUMMARY.md`'s explicit "Open for you" list: the kernel break (undecided, unit + threshold both handed up), the #414 ablation arm, `wip/clean-codebase` parked at `f704273`, and *"`settings.json` remains unwired (#180) — the Context Governor still never fires."*

### C6. The one finding that undercuts the whole delivery path — #331

> *"**All five measured runs invoked ZERO skills.** Not one `Skill` call across five Opus runs against a real 6,435-file repo, each given an ordinary planning brief with the full constellation corpus installed… This is not an instrument failure — **the treatment was offered and declined.**"*
>
> *"**Why this matters beyond #298:** the corpus only affects a run that invokes it… Any change we land in Commander doctrine — #304's map-input contract among them — reaches a subject only if something causes the skill to load."*
>
> *"Worth deciding: **is skill invocation supposed to be model-elected on an ordinary brief**, and if so, what evidence do we have that it happens at a useful rate in real use?"*

Still open. This is a question about whether the instruction-system half reaches anyone at all, and it sits underneath every element of Part A.

### C7. Tommy's own standing forward note — #297 "graph hardening" (open since 2026-07-30)

Filed during the exploration and never closed. His words:

> *"- markdown is kind of a shitty graph structure. Need something traceable, but allows propagation and coherence checks*
> *- agent on harness is clearly needed vice harness in agent*
> *- genericise constellation skills? This was focused on coding agent to start but we're driving towards generic conceptualizations with a coding basis. Maybe start working on the intersection of journal system and phylosophical system.*
> *- bias towards novel ideas means we need to keep a better idea on what's being discussed. May want a scheduled behavior that scans the ai news to see what's up"*

Three of those four are Stratum A and roadmap-step-7 material (traceable structure over Markdown; genericising beyond coding; the journal/philosophy frames). The fourth is the ideas board's *"Research radar"* candidate (line 29), which was never cut. **This is the human's own most recent statement of direction and it is not represented in any cut issue.**

---

## PART D — CONTRADICTIONS AND TENSIONS SURFACED

1. **The cut's own "done" definition was not met, and the closeout does not say so.** Spec line 22 requires *"at least one consolidation acting on a collated cluster"*; #308's re-scope superseded exactly that (*"Half 1's consolidation — no mechanization change, no instruction change, no bin ruling"*). `EPIC_SUMMARY.md` reports B1 as shipped without flagging the unmet clause. The deferral is well-reasoned and human-ruled; the gap is that nothing tracks it as outstanding.

2. **#392's body and #308's close comment disagree about what #308 did.** #392 (filed 2026-08-02 19:35) says #308 was *"bound by `decision:one-consolidation-not-many` to land exactly one consolidation. **Cluster A was selected**"*. #308's close comment (later) supersedes: no consolidation landed. #392's framing of itself as *"the cluster deliberately left unconsolidated"* now reads oddly — **both** clusters were left unconsolidated. Anyone reading #392 alone will conclude one consolidation exists.

3. **"The two-bin rule was withdrawn" is true only in a narrow scope.** `EPIC_SUMMARY.md` lists among Tommy's interventions *"withdrawing the two-bin rule"*; #308's body says *"The two-bin routing adjudication this issue originally carried has been withdrawn."* But #302 closed with *"Ruled: no third bin. **Assumption 6 stands, B0.3 unchanged.**"* The precise reading: **B0.3 remains a confirmed governing principle; what was withdrawn is bin-adjudication at episode-capture time**, because binning is an importance judgement requiring a global view. A reader taking the summary's phrasing at face value would wrongly conclude a confirmed B0 principle was repealed.

4. **B4's earning trigger is half-satisfied and nobody has measured the other half.** Conjunct one (map-first orientation works) is now evidenced. Conjunct two (*"manifests/transcripts show agents chaining map lookups by hand"*) has **no evidence in either direction** — the #307 transcripts exist and were analysed for map-vs-source ordering, not for hand-chained lookups. This is the cheapest unrun measurement in the entire record: same artifacts, different query.

5. **The confirmed spec forbids cutting Stratum A, and the record now contains an unlocked Stratum A door.** Federation/idea-commons is gated on a condition that has been met, but the spec's own rule is that Stratum A is *"DO NOT CUT into issues."* These are not formally in conflict — "revisit" is not "cut" — but the record provides no mechanism for a revisit, and no artifact schedules one. The natural resolution is a **new exploration**, not an issue; the spec says as much for the adjacent deferral (*"preserved on the ideas board for a future exploration"*, spec line 154).

6. **Stratum B was required not to foreclose Stratum A, and one near-term outcome pushes against it.** The episode record carries a non-foreclosure clause (IF05's edit: *"it must remain expressible as assertions under the Stratum A truth model"*). But #399 (open) reports the store *"STRUCTURALLY FORCES local diagnosis and FORBIDS honest gaps"*, and #342 (open) reports *"no 'confirmed' lifecycle-standing, so a held prediction is indistinguishable from an unchecked one"* — lifecycle standing being one of the two dimensions Stratum A's truth model requires be kept separate from strength. Tommy has ruled `strength` itself out of the episode schema (#399). Whether the store still satisfies its own non-foreclosure clause is untested.

7. **The exploration's roadmap ordering and the cut's actual ordering diverge on step 1.** The board says *"Name the minimum graph contract"* **first**, and treats the tracer as step 2 over that contract. The cut inverted this: the tracer shipped as prose plus a resolver script, with no node identity or adjacency projection underneath. That is a defensible simplification, but it means roadmap steps 2–4 were delivered in a form that does not compose into step 3 (deterministic queries need typed connections that were never created). Critic finding IF16 anticipated exactly this — *"B4 presumes 'the map's typed connections' exist without any element creating them"* — and was dispositioned **REJECT** with *"graph history proper is expected later work."*

---

## PART E — MY READ OF THE IMPLIED NEXT STEP

Stated as a read, separate from the quoted record above.

The record supports **one architectural next step and three cheap unblocking measurements**, and they are not the same kind of thing.

**The architectural step: a new exploration of the idea-substrate half, scoped by the roadmap's step 7 ordering.** This is what the record's gating language actually unlocks. The instruction-system half is built and one of its two headline claims is measured PASS. Federation's precondition ("local map use is proven") is met. The board's own release condition on the deferred assertion/frame questions ("should not drive the next pass until these support-system pressures are exercised") has fired. The spec routes this class of work to *"a future exploration"*, not to issues, and Stratum A remains explicitly uncuttable — so the correct vehicle is an explorer run, not a to-issues cut. Tommy's own #297 points the same way (genericise beyond coding; journal ∩ philosophy; something traceable that is not raw Markdown), and #297 is the only forward statement in the record authored by the human rather than by an agent.

**The three cheap measurements, in ascending cost:**
1. **B4's second conjunct** — re-query the #307 transcripts for hand-chained map lookups. Same artifacts, new question, no new runs. It either earns B4 or retires it as unneeded.
2. **The first real consolidation** — the store went 7 → 32 episodes, which was the stated blocker (*"not enough accumulated recurrence to judge from"*). #392 is a filed, cold-sensor-validated, deliberately-unconsolidated strong cluster sitting ready. This is the one outstanding clause of cut 1's own done definition.
3. **#414's ablation arm** — the only thing that can ever move B2. Explicitly costed, explicitly declined, explicitly *not* argued for by its own author under current conditions.

**What the record argues against doing next:** anything metric-shaped while the substrate is being reworked (Tommy, twice), and the ~65-issue sediment pile (`BACKLOG_ROUTING.md`: *"which of these does the next arc actually walk through?"*). The single exception the routing file pulls forward is **#395** — the corpus fingerprint being blind to `templates/` and `scripts/`, *"where the map-first contract actually lives"* — because it is what makes an entire defect class detectable rather than re-discoverable.

**The thing I would not let pass unexamined:** #331. If skill invocation is model-elected and five of five ordinary briefs declined it, then every element in Part A — the map contract that just passed, the episode store, any future projection — reaches a real run only when something causes the skill to load. That question is upstream of the architecture question, and it is open.
