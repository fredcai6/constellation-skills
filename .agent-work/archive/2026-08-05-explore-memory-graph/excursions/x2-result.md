# x2 Result: Two-speed memory — working vs long-term architectures

Excursion x2, cycle 2 (shotgun), `explore-memory-graph`. Research type. One focused pass, 2026-08-04.

**Question:** How do systems that split memory into a fast/sloppy working store and a maintained long-term store — in cognitive science AND in software/AI — handle capture, consolidation/promotion, and forgetting, and what should a two-speed knowledge graph steal from them?

---

## Headline

The two-speed split is real, well-supported, and independently reinvented in three separate fields. But the specific move this project proposed — **"end-of-task merge-up that promotes proven conceptual changes into a maintained long-term graph"** — is the exact mechanism that the strongest recent empirical test says degrades over time. Zhang (2026) ran that paradigm across five agent benchmarks and found accumulated consolidation reliably makes memory *worse* than keeping raw episodes, with one benchmark collapsing from 100% to 54% accuracy after consolidating from ground-truth solutions ([Zhang 2026](https://dylanzsz.github.io/faulty-memory/), arXiv:2605.12978).

The scoped null is narrow and worth stating precisely: **unconditional, every-task, rewrite-in-place promotion fails. The two-speed shape survives** — Zhang's own recommended fix is a fast episodic buffer plus a *slow, gated* abstract store, explicitly citing complementary learning systems theory. What dies is the "merge-up runs every task and rewrites the long-term store" default. What lives is "merge-up is gated, additive, and keeps the episodes."

Everything below is organized so the promotion mechanics are the depth and the rest is breadth, per the brief.

---

## Part 1 — Cognitive science

### 1.1 The canonical split: complementary learning systems

McClelland, McNaughton & O'Reilly (1995) is the foundational statement. The hippocampus learns fast, one-shot, and sparsely; the neocortex learns slowly and extracts structure across many overlapping experiences. The reason for the split is not convenience — it is that a single system cannot do both. Fast learning into a densely-overlapping representation causes catastrophic interference: new learning overwrites old. The two-speed architecture exists *specifically to make fast writes safe* ([McClelland et al. 1995](https://www.researchgate.net/publication/15575602_Why_There_are_Complementary_Learning_Systems_in_the_Hippocampus_and_Neocortex_Insights_from_the_Successes_and_Failures_of_Connectionist_Models_of_Learning_and_Memory); updated in [Kumaran, Hassabis & McClelland 2016](https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(16)30043-2)).

This is the single most load-bearing point for the design. The brain does not have a fast store because writing is cheap there. It has a fast store because **the slow store cannot tolerate fast writes without corruption.** If the long-term graph in this project can absorb a write without damaging its neighbours, the two-speed split is solving a problem you may not have.

| Axis | What CLS does |
|---|---|
| Promotion trigger | Offline replay, predominantly during sleep and quiet rest |
| Promotion unit | Reactivated activity patterns (whole episodes), replayed *interleaved with existing memories* |
| Filtered / forgotten | Contextual and idiosyncratic detail; the gist survives, the episode's specifics thin out |
| Authority | No central authority — neuromodulatory tagging decides, distributed and local |

The interleaving is not incidental. Replay presents new patterns *mixed with* old ones so the slow store adjusts to both at once. A merge-up that considers only the new material, in isolation, is not doing what replay does.

### 1.2 What actually gets promoted — the tagging mechanism

Consolidation is selective, and the selection happens *at capture time, during the task*, not at consolidation time. Sharp-wave ripples — ~100 ms bursts of synchronised firing — occur during waking behaviour, concentrated at moments of reward and novelty. The sequences replayed during subsequent sleep are mainly the ones that were tagged by those *waking* ripples ([Science 2023, "Selection of experience for memory by hippocampal sharp wave ripples"](https://www.science.org/doi/10.1126/science.adk8261); [PMC10659301](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10659301/)). Ripple rate is highest under novelty and reward; dopamine release gates which assemblies become replay-eligible ([Atherton et al. 2015, "Memory trace replay: the shaping of memory consolidation by neuromodulation"](https://pubmed.ncbi.nlm.nih.gov/26275935/); [dopamine and replay, PMC11185723](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11932692/)).

**The mechanism worth naming: the eligibility decision is made online and cheaply, and the expensive consolidation pass only considers already-tagged material.** Nothing surveys the whole day's experience at bedtime and decides what mattered.

### 1.3 Schema-consistency accelerates promotion enormously

Tse et al. (2007) trained rats on flavour-place associations. Once a stable schema existed in cortex, *new* associations consistent with it consolidated after a **single trial** and became hippocampus-independent within about 48 hours instead of weeks ([Tse et al., Science 2007](https://www.science.org/doi/abs/10.1126/science.1135935); [PubMed 17412951](https://pubmed.ncbi.nlm.nih.gov/17412951/)).

Promotion speed is not a property of the item. It is a property of **the fit between the item and the existing long-term structure.** Schema-congruent material goes almost straight through; schema-violating material needs the slow path. A promotion gate with one uniform cost is leaving this on the table.

The complication: novelty and prior-knowledge fit pull in opposite directions on whether to *update an existing trace or create a new one* ([Phil. Trans. R. Soc. B 2024, "To update or to create?"](https://royalsocietypublishing.org/rstb/article/379/1906/20230238/42861/To-update-or-to-create-The-influence-of-novelty)). That is precisely the ADD-vs-UPDATE decision an agent memory graph has to make on every promoted fact, and the biology says it is genuinely two-sided, not a default.

### 1.4 Forgetting is a feature with its own machinery

Richards & Frankland (2017) argue transience is not decay-as-failure but an adaptive process serving decision quality: forgetting reduces the pull of outdated information and prevents overfitting to specific past episodes, promoting generalisation. Their framing — "the goal of memory is not the transmission of information through time, per se, but rather to optimize decision-making" — reframes the whole forgetting question ([Richards & Frankland, *Neuron* 2017](https://www.cell.com/fulltext/S0896-6273(17)30365-3)).

Complication for the "keep the raw episodes" instinct: awake hippocampal-cortical co-reactivation has been associated with *forgetting*, not only strengthening ([bioRxiv 2022](https://www.biorxiv.org/content/10.1101/2022.12.10.519896.full.pdf)). Replay is not purely additive.

### 1.5 Repetition and spacing as the promotion signal

Spaced review consolidates more durably than massed review, and retrieval itself (the testing effect) strengthens the trace rather than merely reading it out ([Frontiers in Psychology 2017, spacing over long timescales](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.00962/full); [Memory & Cognition, retrieval practice and desirable difficulty](https://link.springer.com/article/10.3758/s13421-014-0499-6)). Also: retrieval destabilises a consolidated memory and requires reconsolidation — the act of reading makes it briefly writable again.

**Recurrence across separated occasions, not strength on one occasion, is the biological promotion signal.** This maps cleanly onto cache admission (§2.5) and is the single most transferable idea in this document.

### 1.6 The tension: is the split even architectural?

Two live disagreements, both relevant.

**Standard consolidation vs. multiple trace theory.** The standard model says memories migrate to cortex and become hippocampus-independent. Multiple trace theory says every retrieval lays down another hippocampal trace, and that episodic, context-rich memories *always* need the hippocampus — only context-free semantic material ever becomes independent. Neuroimaging evidence favours multiple trace theory; neuropsychological evidence favours it but not conclusively ([Springer, "Systems consolidation and hippocampus: two views"](https://link.springer.com/article/10.1007/s11559-007-9003-9); [Sciencedirect overview](https://www.sciencedirect.com/topics/psychology/systems-consolidation)).

If multiple trace theory is right, **the fast store is never drained.** Promotion is not a move; it is a copy that abstracts, and the specific episode stays in the fast store permanently. That is a different design from "merge up and clear."

**Working memory may not be a separate store at all.** Cowan's embedded-processes model treats working memory as the currently-activated subset of long-term memory, with a focus of attention holding roughly four chunks — not a distinct system with its own representations. Jonides et al. (2008) survey the unitary-store position: the two differ in activation and in the processes acting on them, not in underlying representation ([Jonides et al., *Annu. Rev. Psychol.* 2008](https://sites.lsa.umich.edu/jonides-lab/wp-content/uploads/sites/439/2016/10/2008_8.pdf); [Cowan 2001 via Scholarpedia](http://www.scholarpedia.org/article/Working_memory)). Baddeley's own model needed a fourth component in 2000 — the episodic buffer — precisely to explain binding between the subsystems and long-term memory, an admission that the boundary leaks ([Baddeley 2000](https://pubmed.ncbi.nlm.nih.gov/11058819/)).

**This is the strongest cognitive-science argument against a hard two-graph split.** A defensible alternative reading: one graph, with an activation/recency marking that distinguishes "hot, provisional" nodes from "settled" ones, and promotion as a *state change on a node* rather than a *move between stores*.

---

## Part 2 — Systems and AI

### 2.1 LSM-trees: the closest engineering analog

Log-structured merge trees are the two-speed shape built for durability. Writes append to a write-ahead log, then land in an in-memory memtable. When the memtable fills it is frozen (becomes immutable) and flushed to disk as an SSTable; background compaction merges SSTables into progressively larger levels, typically with a fan-out around 10 ([LSM overview](https://www.emergentmind.com/topics/log-structured-merge-tree-lsm-tree); [CockroachDB storage layer](https://www.cockroachlabs.com/docs/stable/architecture/storage-layer)).

| Axis | LSM-tree |
|---|---|
| Promotion trigger | Size threshold (memtable full), then background compaction on level-size ratios — **not** task boundaries |
| Promotion unit | The whole immutable sorted run, merged wholesale |
| Filtered | Overwritten keys and tombstoned deletes are dropped *at merge time* |
| Authority | Deterministic system policy; no judgement call anywhere |

Three things transfer.

**Freeze before promote.** The memtable becomes immutable the moment it is a promotion candidate. Nothing writes to a run that is being merged. A merge-up that reads a working graph still being mutated is racing itself.

**Deletes are records, not absences.** A tombstone is a written entry that means "this is gone," and it only actually removes anything when it meets the old value during compaction. For a knowledge graph, "the working graph learned that a long-term fact is wrong" has to be a *writable retraction in the fast store*, not an in-place edit of the slow store.

**Write amplification is the cost, and it is brutal.** A record may be rewritten 3–10 times in size-tiered compaction; documented worst cases reach 42× in RocksDB and 27× in LevelDB. Repeated rewriting of the same content has a real price. In an LLM-mediated graph that price is paid in tokens *and* in fidelity (see §2.7) — the database only loses I/O, you lose accuracy.

### 2.2 W-TinyLFU: an admission filter, and the best-transferring mechanism here

Caffeine's W-TinyLFU is the most directly stealable design in this survey. New items enter a small window LRU (~1% of capacity) that acts as a "doorman." When an item is evicted from the window, it is not promoted automatically — it is compared against the main cache's eviction candidate using an approximate frequency estimate. **The window victim is admitted to the main cache only if its estimated frequency exceeds that of the item it would displace**; otherwise it is discarded ([TinyLFU paper, arXiv:1512.00727](https://www.arxiv.org/pdf/1512.00727); [Caffeine discussion #790](https://github.com/ben-manes/caffeine/discussions/790); [moka wiki](https://github.com/moka-rs/moka/wiki)).

The purpose is named explicitly in the literature: keep **"one-hit wonders"** from polluting the main cache.

Three properties matter for merge-up design.

1. **Promotion is competitive, not absolute.** The question is never "is this good enough to promote?" It is "is this better than what it would displace?" That makes the gate self-calibrating as the long-term store fills.
2. **The gate runs on eviction from the fast store, not on a schedule.** Something is evaluated for promotion exactly when it is about to be lost.
3. **The frequency estimate is approximate and cheap** (a count-min sketch with periodic aging), so gating costs far less than promoting.

A task that touched a fact once is a one-hit wonder. That is the default case for an agent working graph, and this is the field's answer to it.

### 2.3 Generative agents: scored retrieval, and reflection as promotion

Park et al. (2023) keep an append-only memory stream of natural-language observations, each with a creation timestamp and a last-access timestamp. Retrieval scores candidates on three factors: **recency** (exponential decay since last retrieval), **importance** (an LLM-assigned score at write time), and **relevance** (embedding similarity to the query). Reflection is the promotion step: periodically, the agent takes the 100 most recent records, asks the LLM to generate high-level questions about them, answers those, and writes the answers back into the same stream as higher-level memories that can themselves be reflected on ([Park et al., arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)).

| Axis | Generative agents |
|---|---|
| Trigger | Cumulative importance of recent observations crossing a threshold |
| Unit | A synthesised statement with pointers to the observations that produced it |
| Filtered | Nothing is deleted; low scores just stop surfacing |
| Authority | The LLM, at both scoring and reflection time |

Two things to note. **Importance is scored at capture, not at promotion** — the same online-tagging discipline the hippocampus uses (§1.2). And **reflections cite their evidence**: the higher-level memory keeps pointers to the observations it came from. Provenance survives promotion. That is the property whose absence causes drift in §2.7.

Also worth stealing: **there is one store, with tiers emerging from scores.** Reflections live in the same stream as observations. This is the single-store-with-decay alternative running in production, and it works.

### 2.4 MemGPT / Letta: OS-style paging with the agent as authority

MemGPT frames the context window as a memory-management problem and builds three tiers: **core memory** (small, in-context, pinned, directly editable — RAM), **recall memory** (searchable conversation history outside context — disk cache), and **archival memory** (large external store queried by tool call — cold storage). The agent moves data between tiers by calling functions (`core_memory_append`, `archival_memory_search`) during its reasoning loop ([Letta, "Agent Memory"](https://www.letta.com/blog/agent-memory/)).

Letta's sleep-time compute variant is the direct precedent for an end-of-task merge-up, and it makes an interesting authority choice. A second "sleep" agent shares the primary agent's memory blocks and rewrites them while the primary is idle. **The primary agent is not given tools to edit its own core memory at all — the sleep agent holds exclusive write authority.** It runs on a configurable frequency rather than an event trigger. Reported as a Pareto improvement on math benchmarks; the recommended configuration uses a *smaller* model for live interaction and a *larger* one for the sleep pass ([Letta, "Sleep-time Compute"](https://www.letta.com/blog/sleep-time-compute/); [Lin et al., arXiv:2504.13171](https://arxiv.org/html/2504.13171v1)).

**Separating write authority from the agent doing the work is a real design option, and Letta went all the way to exclusive.** It buys consistency and lets you spend more model on the promotion decision than on the task.

### 2.5 Mem0: an explicit promotion policy with four verbs

Mem0's pipeline is the most concretely specified promotion gate in production. An extraction LLM turns each conversation window into compact atomic factual assertions. Each candidate is compared by cosine similarity against the top-k existing memories, and an LLM policy routes it to one of four operations: **ADD** (genuinely new), **UPDATE/MERGE** (augment an existing memory with newer or more detailed information), **DELETE** (the new fact contradicts a stored one), or **NOOP** (already known or irrelevant) ([Mem0 overview](https://www.emergentmind.com/topics/mem0); [Mem0 breakdown](https://memo.d.foundation/breakdown/mem0)).

The NOOP verb is the important one and the one most likely to be dropped by accident. **A promotion pass needs an explicit, first-class "this changes nothing" outcome**, or an LLM asked to merge will always find something to merge.

The unit choice also matters: Mem0 promotes **atomic facts**, not episodes or summaries. Small units make the four-way routing decidable. A large unit forces UPDATE because it always partially overlaps something.

A-MEM takes the adjacent approach, structuring each memory as a Zettelkasten-style atomic note with contextual description, keywords, tags, and explicit links to related notes — the graph structure is built at capture, not derived later.

### 2.6 Zep / Graphiti: three subgraph tiers and non-destructive invalidation

Zep is the closest existing system to what this project is designing: agent memory as a temporal knowledge graph with three tiers — **episode** (raw ingested data), **semantic entity** (extracted entities and facts), and **community** (Leiden-algorithm clusters of related entities, summarised) ([Rasmussen et al., arXiv:2501.13956](https://arxiv.org/pdf/2501.13956); [Graphiti overview](https://help.getzep.com/graphiti/getting-started/overview)).

The mechanism to steal is **bi-temporal edge invalidation.** Every edge carries four timestamps: `t_valid`/`t_invalid` for when the fact held true in the world, and `t_created`/`t_expired` for when the system learned and un-learned it. When a new fact temporally contradicts an existing edge, the system **sets the old edge's `t_invalid` to the new edge's `t_valid` — it does not delete the old edge** ([Zep, temporal knowledge graph](https://www.getzep.com/ai-agents/temporal-knowledge-graph/); [Neo4j on Graphiti](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)).

Two timelines, kept apart, and superseded facts invalidated rather than discarded. This gives you the one thing every other system in this survey lacks: **an audit trail through the promotion step.** You can ask "what did the graph believe on day 12, and what changed it?" and get an answer. Given the drift findings in §2.7, that is not a nice-to-have.

The raw episodes are retained as their own tier. Zep does not drain the fast store either.

### 2.7 The counter-evidence: consolidation degrades

This is the most decision-relevant finding in the excursion, and it is a direct test of the proposed design.

Zhang (2026), *Useful Memories Become Faulty When Continuously Updated by LLMs* (arXiv:2605.12978), tests "distil experiences into textual lessons, store them, rewrite them repeatedly" across ALFWorld, ScienceWorld, WebShop, AppWorld, Mind2Web, and a custom ARC-AGI stream, comparing one-shot abstraction against incremental streaming consolidation ([project page](https://dylanzsz.github.io/faulty-memory/)).

Findings, with numbers:

- **ARC-AGI: 100% → 54%.** GPT-5.4 solved 19 problems perfectly, then consolidated memory *from the ground-truth solutions to those same problems*, and dropped to 54%. Consolidating from correct answers made it worse.
- **ScienceWorld:** performance peaked around consolidation step 20, then fell **below the no-memory baseline** by step 100.
- **WebShop:** memory utility fell from 0.64 at 8 examples to 0.20 at 128 — the benefit was fully erased by scale.
- **ALFWorld:** a 50-item structured memory was collapsed to a **single entry** in one consolidation step, costing 6–13 wins.
- **Over-generalised entries accumulated at ~5× the rate of fresh consolidation; garbage entries at ~20×.**
- Exact task repetitions stayed stable; **small variants of the same family collapsed after 50 passes.**

Three named failure modes: **misgrouping** (forced consolidation merges episodes from genuinely distinct problem classes), **interference** (abstraction strips the applicability conditions, so lessons overgeneralise onto related-but-different cases), and **overfitting** (memory memorises surface regularities instead of strategy).

The mechanism behind the drift, described independently in practitioner writing: at each compression pass, specific facts are the most surprising tokens conditional on the running summary, so they are the first to drop. **Memory drifts toward the model's prior about what a good lesson looks like, rather than toward the truth of the trajectories.** Errors also self-reinforce, because a stored mistake biases the retrieval that feeds the next summary ([Hindsight, "The Consolidation Problem in Agent Memory"](https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation); [Zylos Research](https://zylos.ai/research/2026-04-20-memory-consolidation-ai-agents/)). One reported 28-day autonomous agent run degraded around day 20 — not through index failure, but because curated summaries had drifted from source, returning "confident, plausible answers that were subtly wrong."

Zhang's recommended architecture is worth quoting in shape, because it is *not* a rejection of two-speed:

1. Raw episodes are **first-class evidence**, not material to be compressed away.
2. Abstraction is **gated and opt-in**, not applied to every trajectory.
3. **Episodic-only retrieval matched or beat every tested consolidation method** (ACE, AWM, Dynamic Cheatsheet) on WebShop, ALFWorld and AppWorld — "the useful information was sitting in the curated raw episodes the whole time."
4. Target architecture: a fast episodic buffer plus a **slow, gated abstract store**, explicitly mirroring complementary learning systems.

A corroborating data point from the other direction: RecMem's ablation found the largest performance drop came from removing the **raw-interaction** layer, "the only faithful carrier of raw interaction units" ([arXiv:2605.16045](https://arxiv.org/pdf/2605.16045)).

Counterweight, so this is not one-sided: Auto-Dreamer (Ye et al., arXiv:2605.20616) reports offline consolidation *helping* across ALFWorld, ScienceWorld and WebArena versus Reflexion, ExpeL and several memory-augmented baselines. The difference from Zhang's failing configurations appears to be that Auto-Dreamer **learns which memories improve task performance and filters on that**, rather than consolidating unconditionally. Where the two disagree, the discriminating variable looks like the gate, not the two-speed shape.

### 2.8 Who holds authority — the axis nobody agrees on

Yang (2026), *Control-Plane Placement Shapes Forgetting* (arXiv:2606.15903), studies exactly this across thirteen configurations, comparing agent-controlled, background-process, deterministic-rule, and human-directed memory authority. The core claim: **systems do not forget uniformly; retention patterns depend on where consolidation authority sits.** (Numerical tables were not extractable from the PDF in this pass — flagged as a gap.)

The field's positions are genuinely split:

| System | Who decides what gets promoted |
|---|---|
| Brain | Nobody — distributed neuromodulatory tagging at capture |
| LSM-tree / W-TinyLFU | Deterministic policy, zero judgement |
| Generative agents | LLM, at both scoring and reflection |
| Mem0 | LLM policy, constrained to four verbs |
| Letta sleep-time | A **separate** agent, with exclusive write authority |
| Zep | Hybrid — LLM extraction, deterministic temporal invalidation |

Note the pattern in the last two rows: the systems that handle contradiction best do **not** let a single LLM call both decide and execute. Zep splits extraction (LLM) from invalidation (deterministic rule on timestamps). Letta splits the agent that does the work from the agent that writes memory.

---

## Part 3 — The mechanisms most worth stealing

Five, ranked by how much they change the merge-up design.

**1. Gate promotion competitively at eviction time, not unconditionally at task end (W-TinyLFU).** Ask "does this beat what it would displace?" rather than "is this good?", and ask it when working-graph content is about to be discarded rather than on a fixed schedule. This is the field's specific answer to one-hit wonders, and a single task's working graph is mostly one-hit wonders. It is also the mechanism that most directly defuses Zhang's §2.7 failures, because it makes most tasks promote nothing at all.

**2. Tag eligibility online, during the task; let the merge-up only consider tagged material (sharp-wave ripples, generative-agents importance-at-write).** Both biology and the best-performing agent systems score importance at capture. A merge-up that surveys the entire working graph at the end and decides what mattered is doing something neither does — and it is the expensive, error-prone framing.

**3. Never destroy on promotion: supersede with two timelines (Zep bi-temporal invalidation, LSM tombstones).** Set `t_invalid` on the superseded edge; keep it. Given documented drift, the ability to reconstruct what the graph believed and what changed it is the primary defence. It also makes a bad merge-up reversible instead of terminal.

**4. Keep raw episodes as first-class, permanently — do not drain the fast store (Zhang's fix, RecMem's ablation, multiple trace theory, Zep's episode tier).** Three independent lines converge here. Episodic-only retrieval matched every consolidation method Zhang tested. If the merge-up's abstractions drift, the episodes are what you recover from; if they never drift, you have lost only storage.

**5. Promote atomic units through an explicit verb set that includes NOOP (Mem0).** Small units make ADD/UPDATE/DELETE/NOOP decidable; large units force UPDATE because they always partially overlap. And the "nothing changed" outcome must be first-class and cheap, or an LLM asked to merge will always merge something. This is the mechanical form of failure mode "misgrouping."

**Runners-up, worth knowing but weaker evidence:** interleave old material into the promotion decision rather than judging new material alone (CLS replay); tier promotion cost by schema fit, so structure-congruent facts pass cheaply and structure-violating ones take the slow path (Tse et al.); split the deciding authority from the executing agent (Letta, Zep); require recurrence across *separated* tasks rather than strength within one (spacing effect, TinyLFU frequency).

---

## Part 4 — Evidence the two-speed split is the wrong shape

Stated as scoped nulls, per the brief. None of these kill the two-speed concept; each kills a specific version of it.

**The strongest challenge is not to two-speed but to unconditional merge-up.** Zhang's numbers (§2.7) kill "every task, rewrite in place, compress away the episodes." They explicitly endorse "fast episodic buffer plus slow gated abstract store."

**Single-store-with-decay is a real, working alternative, not a strawman.** Generative agents run one append-only stream where reflections live alongside observations and tiering emerges from recency/importance/relevance scores. Cowan's embedded-processes model and the unitary-store position in Jonides et al. (2008) say the same about the brain: not two stores, one store with an activation gradient and a ~4-chunk focus of attention. Baddeley needing to add the episodic buffer in 2000 to explain binding is evidence the boundary leaks even in the canonical model. **If the long-term graph can tolerate a cheap write without corrupting neighbours, the entire justification for the fast store (§1.1) does not apply, and one graph with a provisional/settled marking on nodes is simpler and loses nothing.** This is the design's most serious unexamined assumption.

**"Merge up and clear" is contradicted from three directions.** Multiple trace theory says the fast store is never drained and episodic material stays hippocampus-dependent permanently; Zep keeps its episode tier; Zhang's fix requires keeping episodes. Promotion should be understood as a *copy that abstracts*, never a move.

**The end-of-task boundary is an assumption, not a finding.** LSM-trees promote on size thresholds, W-TinyLFU on eviction events, generative agents on cumulative importance crossing a threshold, Letta on a configurable frequency, the brain on sleep and quiet rest. **Not one system in this survey uses "the unit of work finished" as its promotion trigger.** Task boundaries are convenient for an agent framework, but nothing here suggests they are the right moment — and a task boundary guarantees promotion happens exactly once per task regardless of whether anything worth promoting occurred, which is the shape Zhang found fails.

**Repeated LLM rewriting has a cost with no counterpart in the database analogy.** LSM write amplification of 42× costs I/O and nothing else. Every rewrite pass through an LLM is lossy in a directed way — toward the model's prior about what a lesson looks like. The rate-distortion framing of memory compaction ([arXiv:2607.08032](https://arxiv.org/pdf/2607.08032)) makes this explicit. **Borrow LSM's structure; do not borrow its comfort with rewriting the same content many times.**

---

## Gaps in this pass

- Yang (2026) *Control-Plane Placement Shapes Forgetting* is the most on-point paper for the authority question, but its result tables did not extract from the PDF. Worth a targeted re-fetch if authority placement becomes a live decision.
- Zep's DMR and LongMemEval numbers were not extractable from the arXiv PDF in this pass; the architecture description is solid, the quantitative claims are not verified here.
- Auto-Dreamer's specific numbers were likewise not extractable. It is cited as a directional counterweight to Zhang, not as a verified result. The disagreement between them (gated vs. unconditional consolidation) is the highest-value follow-up in this area.
- Soar and ACT-R were surveyed only at breadth. The relevant transfer is that both promote on *impasse* — Soar chunks when problem-solving gets stuck and compiles the resolution into a rule — and both use base-level activation computed from access timestamps, meaning **forgetting is driven by access patterns, not by outcomes** ([ACT-R/Soar comparison](https://advancesincognitivesystems.github.io/acs2021/data/ACS-21_paper_6.pdf)). Impasse-triggered promotion — promote when the agent got stuck and then unstuck — is an unexplored trigger option that no LLM-agent system in this survey uses, and it is a better fit for "proven conceptual change" than a task boundary is.
