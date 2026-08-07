# x12 result — prior art: giving coding agents maps

**Question:** what is the prior art on giving coding agents maps/navigation artifacts of a codebase, and which artifact shapes have *measured* evidence of making agents better?

**Status:** answered, with one strong contradiction to a premise near our design.

**Headline:** the evidence splits cleanly by *shape*. Machine-built, queryable, symbol-or-finer structure that the agent **pulls on demand** has repeatedly measured gains (RepoGraph +8.6% to +100% relative on SWE-bench-Lite; LocAgent ablation isolates the graph tool; ARISE +4.7pp; Codebase-Memory ~10x token reduction per query). Prose **repository overviews pushed into context** have measured *harm* or nothing — the ETH Zurich AGENTS.md study found LLM-generated context files reduced success by 0.5–2% while adding 20–23% cost, and stated flatly that "context files do not provide effective overviews." Our design sits on the good side of that line, but one of our assumptions is directly contradicted (see §6).

---

## 1. Artifact taxonomy

What exists, what it is on disk, granularity, and how it reaches context.

| Shape | On disk | Granularity | Reaches context by |
|---|---|---|---|
| Ranked symbol map (aider repo-map) | generated in-memory per request, rendered as an indented text listing | per-file, listing key symbols with signature lines | **push** — injected into every request |
| Hierarchical repo tree + skeletons (Agentless) | generated per task | file tree, then class/function names | **push**, staged over 3 localization phases |
| Code graph, DB-backed (CodexGraph) | graph database (nodes MODULE/CLASS/FUNCTION; edges CONTAINS/INHERITS/USES) | symbol-level | **pull** — agent writes NL queries translated to graph queries |
| Code graph, line-level (RepoGraph) | networkx graph, ~1,419 nodes / ~26,392 edges per repo | **line-level** def/ref nodes | both — a `search_repograph()` action (pull) and flattened ego-graph appended to prompt (push) for procedural frameworks |
| Heterogeneous index graph (LocAgent) | offline sparse index built "in seconds per repository" | directory / file / class / **function** as smallest node | **pull** — 3 tools: SearchEntity, TraverseGraph, RetrieveEntity |
| Multi-level program graph with dataflow (ARISE) | repo→file→class→function→**statement**, with intra-procedural def-use edges | down to statement | **pull** — three-tier tool API, framework-agnostic |
| Tree-sitter knowledge graph (Codebase-Memory) | **single SQLite file**, property graph, 66 languages | function/method/class/import nodes | **pull** — 14 typed MCP query tools |
| LSP-backed symbol tools (Serena) | no artifact; live language-server queries | symbol-level | **pull** — MCP tools |
| Auto-generated wiki (DeepWiki/Devin, CodeWiki) | hosted wiki pages, architecture diagrams, source links | module/subsystem prose | human-facing primarily; agent-facing via MCP/fetch |
| Instruction file as map (AGENTS.md, CLAUDE.md, .cursorrules) | markdown at repo root | whole-repo prose | **push** — prepended to system context |
| Memory bank (Cline) | several structured markdown files in-repo | project-level prose | **push**, re-read per session |
| Machine-facing index (`llms.txt` / `llms-full.txt`) | markdown at web root | document-level links | pull by fetch, in principle |

Sources: [aider repo-map post, 2023-10-22](https://aider.chat/2023/10/22/repomap.html); [Agentless (arXiv 2407.01489)](https://huggingface.co/papers/2407.01489); [CodexGraph, NAACL 2025 (arXiv 2408.03910)](https://aclanthology.org/2025.naacl-long.7/); [RepoGraph, ICLR 2025 (arXiv 2410.14684)](https://arxiv.org/html/2410.14684v1); [LocAgent (arXiv 2503.09089, 2025-03-12)](https://arxiv.org/html/2503.09089v1); [ARISE (arXiv 2605.03117, subm. 2026-05-04, rev. 2026-07-03)](https://arxiv.org/abs/2605.03117); [Codebase-Memory (arXiv 2603.27277v1, 2026-03-28)](https://arxiv.org/html/2603.27277v1); [Serena](https://github.com/oraios/serena); [DeepWiki docs](https://docs.devin.ai/work-with-devin/deepwiki); [CodeWiki (arXiv 2510.24428)](https://arxiv.org/pdf/2510.24428); [Cline Memory Bank](https://docs.cline.bot/best-practices/memory-bank).

**Where our design lands:** rendered per-entity markdown pages in a mirrored `derived/` tree with an `ids.jsonl` lookup is closest to **Codebase-Memory** (a built, on-disk, per-symbol store queried on demand) and to **Corpus2Skill** (§4), but rendered as files rather than a DB. No prior-art system in this sweep renders one markdown page per entity as the primary artifact — the closest analogues store nodes in a graph DB or SQLite and render only on query. That is a genuine gap, not obviously a mistake (see §6).

---

## 2. Evidence of usefulness — ablations and deltas

**SWE-agent / ACI (NeurIPS 2024, arXiv 2405.15793).** The foundational result that *interface design* — not just model or context — moves the number: the same GPT-4 with the same problem statement "scores roughly 2× on SWE-Bench when given Agent-Computer Interface tools versus raw bash." Main results 12.5% pass@1 on full SWE-bench; ablations run on SWE-bench Lite with GPT-4 Turbo and Claude 3 Opus. ([OpenReview](https://openreview.net/forum?id=mXpq6ut8J3), [arXiv](https://arxiv.org/abs/2405.15793))

**RepoGraph (ICLR 2025).** The cleanest plug-in ablation in the field — same framework, with and without the graph, four frameworks:

| Framework | Baseline | +RepoGraph | Relative |
|---|---|---|---|
| RAG | 2.67% | 5.33% | +99.6% |
| Agentless | 27.33% | 29.67% | +8.6% |
| AutoCodeRover | 19.00% | 21.33% | +12.3% |
| SWE-agent | 18.33% | 20.33% | +10.9% |

Average relative improvement 32.8%. Localization gains: file-level +4.4–5.6pp, function-level +2.0–3.4pp, line-level +1.6–2.7pp. Cross-task transfer on CrossCodeEval: GPT-4o exact match 10.8% → 28.5% (2.6×). ([arXiv 2410.14684](https://arxiv.org/html/2410.14684v1))

**LocAgent (2025-03).** File-level Acc@5 94.16% vs 90.15% OpenHands baseline on SWE-Bench-Lite (274 examples). The load-bearing ablation: **removing the `TraverseGraph` tool drops module-level accuracy 82.85% → 78.47%**, with the authors' stated reason — "the agent cannot obtain any structure information." A fine-tuned Qwen-2.5-32B reached 92.70% file-level Acc@5 at **86% lower cost** ($0.09 vs $0.66/example). ([arXiv 2503.09089](https://arxiv.org/html/2503.09089v1))

**ARISE (2026-05).** SWE-bench Lite, 300 issues: 22.0% resolve (66/300), **+4.7pp over unmodified SWE-agent**. Retrieval deltas are the striking part: Function Recall@1 0.43 → 0.60 (+40% rel.), Line Recall@1 0.26 → 0.41 (+58% rel.). ([arXiv 2605.03117](https://arxiv.org/abs/2605.03117))

**Codebase-Memory (2026-03).** 31 repos / 31 languages. Graph queries used **~1,000 tokens/query vs ~10,000 for file exploration (10×)** and **2.3 vs 4.8 tool calls per question (2.1×)**. But note the honest negative: **answer quality 83% vs 92% for the file-exploration baseline** — the graph was cheaper and faster, not more accurate, and matched-or-beat the explorer on only 19 of 31 languages. ([arXiv 2603.27277v1](https://arxiv.org/html/2603.27277v1))

**ORACLE-SWE (arXiv 2604.07789v2, 2026-05-29).** Quantifies what navigational information is *worth* by handing agents oracle signals. On SWE-bench-Verified with GPT-5-Thinking-Medium, baseline 35%:

| Oracle signal | Resolve rate |
|---|---|
| Reproduction test | 71% |
| **Edit location** (file, class/function, line range) | **74%** |
| API usage | 72% |
| Execution context (stack traces, call relations) | 71% |
| Regression test | 58% |

Authors' ordering: "Reproduction Test ≫ Execution Context ∼ Edit Location ≫ API Usage ≫ Regression Test." **The ceiling for perfect localization is roughly +39pp** — that is the size of the prize a map is competing for, and it is very large. ([arXiv 2604.07789](https://arxiv.org/html/2604.07789v2))

**Auto-wikis.** Weakest evidence tier. The only evaluation found is CodeWiki's pilot **human** study: CodeWiki preferred over DeepWiki in 7/9 assessments across OpenHands, svelte, puppeteer. That is documentation-quality preference by humans, **not** agent task success. No study found measuring whether an auto-wiki improves an agent's downstream coding performance. ([arXiv 2510.24428](https://arxiv.org/pdf/2510.24428))

**aider's repo-map — a null worth naming.** Despite being the most-cited map artifact in practice, aider's own writeup contains **no benchmark numbers isolating the repo map's contribution**. The available comparisons come from aider's own test harness, not a neutral benchmark. The most influential artifact shape in this space is, as far as this search found, the least independently measured. ([aider repomap post](https://aider.chat/2023/10/22/repomap.html), [aider repomap docs](https://aider.chat/docs/repomap.html))

---

## 3. Granularity and token budget

This is where prior art speaks most directly to our per-entity page decision, and it broadly supports us.

**Bite-sized beats monolithic — measured.** RepoGraph's variant ablation is the single best evidence:

| Variant | Resolve rate |
|---|---|
| 1-hop flattened | **29.67%** |
| 1-hop summarized | 28.33% |
| 2-hop summarized | 28.67% |
| 2-hop flattened | 26.00% |

A 1-hop neighbourhood is ~11.6 nodes / ~2,310 tokens; 2-hop is ~54.5 nodes / ~10,505 tokens. **The bigger dump scored worst** — the authors attribute it to context explosion. And the full graph (1,419 nodes / 26,392 edges) is never injected at all. The paper explicitly notes gains required "modest token increases proportional to accuracy gains, contradicting simple 'more tokens = better performance' assumptions." ([arXiv 2410.14684](https://arxiv.org/html/2410.14684v1))

**Two other independent confirmations of the same shape:**
- Progressive-disclosure study (§4): "One flat routing level suffices; deeper hierarchies harm performance through context saturation." Hierarchical disclosure collapsed En.MC accuracy 0.91 → 0.64 on one agent. ([arXiv 2607.17598v1, 2026-07-20](https://arxiv.org/html/2607.17598))
- Exploration-structure study: naive full-filesystem access **underperformed a plain LLM with no codebase access at all** (0.151 vs 0.199 micro-F1 for a Haiku-class agent), because "unconstrained directory traversal can lead agents into large, irrelevant test hierarchies." More access is not more signal. ([arXiv 2606.11976v1, 2026-06-10](https://arxiv.org/html/2606.11976v1))

**Finer granularity wins where measured.** ORACLE-SWE puts edit location (file + function + line range) at the top of the useful-signal list. ARISE goes to statement level and gets its biggest wins on *line* recall (+58% rel.). RepoGraph is line-level and explicitly frames this as its distinction from "prior work that operated at file or function levels." LocAgent's smallest node is the function. The trend across 2024→2026 is **downward in granularity**, toward per-entity and finer. Our per-function/class/method page granularity is squarely on this trend line; aider's per-file granularity is the older shape.

**Token budgets in practice.** aider defaults to `--map-tokens 1000` for the whole-repo push map — a hard ceiling that forces ranking. Pull systems have no equivalent ceiling because they never present the whole thing; Codebase-Memory's ~1,000 tokens is *per query*, not per repo. Our ~16-line median page is roughly 150–250 tokens, so a working set of 5–10 pages lands near the 1–2.5k range that both aider's budget and RepoGraph's optimal 1-hop retrieval converge on. That convergence from three directions is the most reassuring number in this report.

---

## 4. Push vs pull

**The field has moved to pull, and our internal offered-and-declined result is a known failure mode with a name.**

Every 2025–2026 system with measured gains is pull-based: LocAgent (3 tools), CodexGraph (query interface), ARISE (three-tier tool API), Codebase-Memory (14 MCP tools), Serena (MCP). The push-based artifacts are the older (aider, 2023) or the weakly-evidenced (AGENTS.md) ones. RepoGraph is the interesting hybrid — it offers `search_repograph()` as an agent-invoked action for agentic frameworks *and* appends flattened subgraphs directly to prompts for procedural ones, and the **procedural (pushed) variants scored higher** (Agentless+RepoGraph 29.67% vs SWE-agent+RepoGraph 20.33%), which the authors attribute to "deterministic workflows mitigating error accumulation seen in agent-based trial-and-error approaches." That is a real point against pure pull for weaker agents.

**Agents declining offered tools is measured.** ToolFailBench diagnoses exactly this, labelling traces with **Tool-Skip** (never calls a needed tool), Result-Ignore, Output-Fabrication, and Unnecessary-Tool-Use across 1,000 tasks. Across 19 headline models, the best Clean Tool-Use Rate is **86.33%** — "faithful tool use is not saturated," and models with similar aggregate scores fail in *different* ways. Our epic #298 zero-invocation result is a Tool-Skip observation, and it is the field's normal case, not an anomaly of our corpus. ([arXiv 2607.04686](https://arxiv.org/html/2607.04686v1))

**What makes usage stick — three mechanisms found:**
1. **Fewer, higher-level tools.** LocAgent deliberately collapses navigation into 3 tools. Reported tool-count degradation is steep: reliability "falls off a cliff" past ~20 tools, with ≤10 per context the common recommendation, and RAG-MCP reports a plain LLM picking correctly from a large MCP pool at 13.62%. Note: the ≤10 figure and the "cliff" come from vendor/practitioner telemetry and blog analysis, **not** peer-reviewed work — treat as directional. ([RAG-MCP arXiv 2505.03275 via](https://pub.towardsai.net/adding-more-mcp-tools-made-my-ai-agent-dumber-accuracy-collapses-past-20-8e754d09bee4), [MCP-Manager checklist](https://github.com/MCP-Manager/MCP-Checklists/blob/main/infrastructure/docs/improving-tool-selection.md))
2. **Loading the instruction outright.** This is precisely our #298 finding (map-before-source 0/4 → 4/4 when the skill was loaded rather than offered), and it matches the Agent Skills progressive-disclosure model: names and one-line descriptions are preloaded, bodies fetched on demand. ([Agent Skills open standard, 2025-12-18](https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure))
3. **Navigation over retrieval.** "Don't Retrieve, Navigate" (Corpus2Skill, arXiv 2604.14572) distils a corpus into hierarchical **navigable agent skills** with explicit links, and argues navigation needs fewer model calls and tokens than embedding retrieval, letting agent reasoning pick the path. This is the closest published analogue to our rendered-pages-plus-teaching-skill plan. Caveat: exact quantitative results were not extractable from the PDF in this pass — treat the direction as supported, the effect size as unverified.

**Sharpest caveat on pull.** The progressive-disclosure study found disclosure "buys context, not intelligence" — it was **redundant for strong native navigators** (Codex, which "already grepped passages natively") and only became decisive at library scale (En.QA at K=20 books: 0.46 flat vs 0.26 raw). Read against a codebase: a strong agent with good grep on a small repo may get nothing from our pages. The value should appear at scale and for weaker agents. That is a testable prediction and a good place to aim a measurement.

---

## 5. Freshness

Thin evidence, but what exists is pointed.

- **Incremental re-index is the working answer.** Codebase-Memory uses XXH3 content hashes to re-index only changed files. LocAgent builds indexes offline "in seconds per repository" and describes **no continuous updating mechanism** — cheap-enough full rebuild is the implicit strategy. Neither paper measures staleness harm.
- **No study found that measures staleness degradation directly.** This is the clearest gap in the literature this pass turned up.
- **The strongest available claim is indirect and it is an argument, not a measurement:** on stale context files, "the cost of a stale cache entry is not zero — it is negative, because the agent will follow the outdated instruction with the same diligence it applies to current ones." ([Codex KB, 2026-03-27](https://codex.danielvaughan.com/2026/03/27/agents-md-bloat-problem/)) Practitioner reasoning, not data — but consistent with the ETH finding that bad context actively costs steps.
- Corroborating field observation: "silent rule dropout" in long sessions, with documented Claude Code issues of agents ignoring CLAUDE.md due to lost-in-the-middle. Push does not guarantee attention. ([InfoQ, 2026-03-06](https://www.infoq.com/news/2026/03/agents-context-file-value-review/))
- Generated-from-code artifacts sidestep most of this by construction, which is the design argument for our statement store over hand-written wikis.

---

## 6. Delta to our design

### Confirmed

1. **Per-entity granularity.** RepoGraph (line), ARISE (statement), LocAgent (function), ORACLE-SWE (edit location tops the signal ranking) all point below file level. Our per-function/class/method page is on trend; aider's per-file map is the legacy shape.
2. **Small units, retrieved in ones and twos.** RepoGraph's 1-hop-flattened (29.67%) beating 2-hop-flattened (26.00%) is direct measured support for bite-sized nodes over monolithic dumps. Our ~16-line pages are well inside the winning regime.
3. **Generate from code, don't hand-write.** Every measured winner is machine-derived from AST/LSP. The only artifacts with measured *harm* are prose files.
4. **A lookup index alongside the artifacts.** `ids.jsonl` matches LocAgent's "global name-to-nodes mapping" and entity-ID indexing.
5. **Pull, taught by a loaded skill.** Convergent: ToolFailBench names Tool-Skip as a first-class failure; our #298 zero-invocation is that failure; Agent Skills' preload-the-description/fetch-the-body model and Corpus2Skill's navigate-don't-retrieve are the field's answer, and it is the same answer #298 found empirically.

### Contradicted — surfaced, not smoothed

6. **"An architectural overview helps the agent orient."** This is the one that takes a real hit. The ETH Zurich study (138 AGENTbench instances / 12 repos, plus SWE-bench Lite 300 tasks / 11 repos; Claude Code on Sonnet-4.5, Codex on GPT-5.2 and GPT-5.1-mini, Qwen Code on Qwen3-30b-coder) states: **"Context files do not provide effective overviews"** — measured by step counts before the agent reaches the modified file — and **"repository overviews, although popular and recommended by model providers, are not helpful."** LLM-generated files *reduced* success by 0.5% (SWE-bench Lite) and 2% (AGENTbench) while adding 20% and 23% cost and 2.45/3.92 steps. Developer-written files gained 4% on average but still cost up to 19% more. ([arXiv 2602.11988, subm. 2026-02-12, rev. 2026-06-23](https://arxiv.org/abs/2602.11988))

    This maps onto our #298 result unnervingly well: *orientation behaviour was unmoved in both arms* (0/4 both) even when map-before-source flipped 0/4 → 4/4. **Two independent lines of evidence now say the same thing — a map changes what an agent reads, and does not change how it orients.** If any part of our design is justified by "the agent will orient better," that claim is currently unsupported by external evidence *and* by our own.

7. **The redundancy mechanism — and the escape hatch.** The ETH authors isolate *why*: the context was redundant, not wrong; the agent could read the same thing from the repo. The decisive sub-finding: **when existing documentation was removed, "LLM-generated context files not only consistently improve performance by 2.7%, but also outperform developer-written documentation."** So generated context helps exactly when it is *not* recoverable from what the agent can already see. This is the sharpest single design constraint in this report: **our pages must carry something reading the source does not cheaply give** — cross-file reference structure, call/def relations, the tombstone/dead-limb information — and must not restate what a `grep` and one file read would surface.

8. **Pure pull is not strictly better.** RepoGraph's pushed-into-procedural-workflow variants outscored its agent-invoked-tool variants. A skill that *teaches* pull is our plan; the evidence says a deterministic step that *inserts* the relevant pages at a fixed point in a workflow may beat leaving it to the agent's judgement. Worth considering as an alternative arm, not a settled loss.

9. **Cheaper is not the same as better.** Codebase-Memory, the closest structural analogue to our store, came in at **83% quality vs 92% for plain file exploration** while being 10× cheaper per query. If our pages are evaluated only on token cost we may declare a win while quality slips. Whatever measurement we design should hold answer quality as a first-class outcome, not an assumed constant.

### Shapes we have not considered

10. **Dataflow / def-use edges (ARISE).** Nothing in our design carries "which statements define or consume this variable." ARISE's largest measured gains were on *line* recall (+58% rel.), and this is the machinery behind it. A statement-level slice is far below our current entity granularity — a real extension, not a tweak.
11. **Execution context as a map layer (ORACLE-SWE).** Stack traces and runtime call relations scored 71% — on par with edit location. Our map is entirely static. A runtime-observed call edge is a different and apparently comparably-valuable kind of navigational fact.
12. **Reproduction tests outrank everything.** The single most valuable oracle signal was the reproduction test (71%, and top of the authors' ordering). This is not a map at all, which is a useful check on ambition: the best map in the world competes in the same band as "here is a test that fails."
13. **Bounded-I/O and repository-scoped dispatch.** The exploration-structure paper's conclusion — effective exploration needs "bounded I/O mechanisms" and "repository-aware context management using programmatic environments rather than raw file exposure" — frames our `derived/` tree as a *bounded* substitute for raw file access, which is a stronger framing of our own design than "it's a map." Their parallel subsystem dispatch beat sequential exploration significantly (p=0.015).
14. **`llms.txt` — actively discouraged as a model.** Do not borrow this pattern. SE Ranking's 300,000-domain analysis found **no measurable effect on AI citation**, and removing the `llms.txt` variable from their XGBoost model *improved* prediction accuracy — it was noise. Google's John Mueller (June 2025) said no AI system uses it and bots are not fetching it. The one narrow place it works is developer docs with programmatic consumers pointing a context window at one clean markdown file — which is closer to our case, but the general pattern has no evidence. ([OrganiKPI adoption data](https://organikpi.com/blog/distribution/llms-txt-adoption-impact/), [aiseousa](https://aiseousa.com/blog/what-is-llms-txt-does-it-work)) Caveat: these are SEO-industry analyses, not peer-reviewed.

---

## Scoped nulls — what was NOT searched

This kills these searches under these conditions, not the idea classes.

- **No search of closed-source vendor internals.** Cursor's codebase index, GitHub Copilot Workspace, Sourcegraph Cody's context selection, Windsurf, and Augment were not searched for published ablations. Cody in particular was named in the brief and I did not reach it. Vendor engineering blogs may carry numbers this pass missed.
- **No search for negative/null results on graph maps.** I searched for evidence *of* usefulness and found the AGENTS.md contradiction incidentally. A deliberate "code graph did not help" / failed-replication search was not run. Publication bias is therefore unmitigated in §2.
- **aider repo-map ablation: searched, not found.** I searched specifically for aider repo-map benchmark evidence and found none isolating its contribution. This is a null on *finding published numbers*, not evidence the repo map does not work.
- **`Corpus2Skill` effect sizes not extracted.** The PDF resisted extraction; direction supported, magnitude unverified. Re-fetch the HTML version to close this.
- **ORACLE-SWE cross-model detail not fully extracted.** I have the GPT-5-Thinking-Medium column on SWE-bench-Verified; the Claude-4.5-Sonnet and SWE-bench-Live/Pro columns were summarized as "similar patterns" rather than read.
- **Freshness/staleness: searched, essentially empty.** I found no study measuring degradation from a stale map. Either it does not exist, or it is indexed under vocabulary I did not try (documentation drift, index invalidation, code-comment inconsistency detection). The one comment-internalization paper found ([arXiv 2512.16790](https://arxiv.org/html/2512.16790v1)) was not read; it may bear on how misleading text steers a model.
- **No non-English sources, no venue-proceedings sweep** (ICSE/FSE/ASE 2025–2026 were not searched systematically; hits arrived via general web search).
- **Effect sizes are reported as published.** No independent replication was checked, and SWE-bench-Lite numbers across papers use different harnesses and model versions — the tables in §2 are **not** safely comparable across rows from different papers.
- **Practitioner-tier claims flagged inline** (the ≤10 tools guidance, the "cliff past 20," the staleness-is-negative argument, the `llms.txt` SEO analyses). These are directional, not peer-reviewed, and are marked as such where used.
