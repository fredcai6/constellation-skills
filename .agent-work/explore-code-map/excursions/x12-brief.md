# Excursion Brief: prior art — giving coding agents maps

## The one named question

We are not the only ones building dev tools for agents: what is the prior art on giving coding agents **maps / navigation artifacts** of a codebase, and which artifact shapes have **measured evidence** of making agents better?

## Type

research

**Why this type:** the human asked directly for prior art before we design our consumption skills; facts-and-citations, not a build question.

## Context (read first, do not re-derive)

- This exploration has ruled: statement store (JSON-lines facts per source file) + rendered **per-entity markdown pages** (one page per function/class/method, agent-lean, ~16 lines median, entity id as title, mirrored `derived/` tree, `ids.jsonl` lookup). The skills that TEACH agents to use these artifacts are the next design item; this excursion informs that design.
- Internal prior evidence (context, not your subject): in this project's epic #298 experiments, a map corpus *offered* to agents got **zero skill invocations** (offered-and-declined), while loading the skill outright flipped map-before-source reading 0/4 → 4/4 without changing orientation behavior. External prior art on push-vs-pull uptake is directly relevant.

## What "answered" looks like

`excursions/x12-result.md` with cited findings on:

1. **Artifact taxonomy** — what shapes exist for agent-facing codebase maps: ranked symbol maps (aider's repo-map: tree-sitter + graph ranking), skeleton/outline views, auto-generated wikis (DeepWiki/Devin), instruction files as maps (CLAUDE.md / AGENTS.md / .cursorrules conventions), `llms.txt`-style machine-facing indexes, graph-DB + query interfaces (CodexGraph, RepoGraph, GraphRAG-on-code), LSP/ctags-backed navigation tools, retrieval indexes (Sourcegraph Cody context, embeddings), agent memory banks (Cline and kin). For each: what the artifact IS on disk, granularity, how it reaches the agent's context.
2. **Evidence of usefulness** — ablations and benchmark deltas that isolate the artifact's contribution, not vibes: aider's repo-map ablations if published; SWE-agent's agent-computer-interface paper (what interface design measurably changed success); Agentless and OpenHands localization studies (what repo representation improved fault localization); CodePlan / RepoUnderstander / CodexGraph reported gains; anything measuring auto-wiki usefulness. Note effect sizes and what benchmark.
3. **Granularity and token-budget findings** — per-symbol vs per-file vs whole-repo views; how the field sizes map artifacts against context budgets; any evidence on bite-sized-nodes vs monolithic context dumps.
4. **Push vs pull** — is the map injected into context (push) or fetched by the agent via tools (pull)? Any published findings on agents *declining to use* offered tools/artifacts, and what made usage stick.
5. **Freshness** — how these systems keep the map current against code churn (regen cadence, incremental, on-demand), and whether staleness measurably hurt.
6. **Delta to our design** — which of our choices prior art confirms, which it contradicts, and what useful artifact shapes exist that we have NOT considered. Contradictions surfaced, not smoothed.

## Budget / stop conditions

- One focused research pass (~60 min of searching/reading); report even if inconclusive.
- No code, no installs — reading and citing only. Primary sources (papers, project docs, changelogs) over blog summaries; note publication dates — this field moves fast, prefer 2024–2026.
- READ-ONLY everywhere except `.agent-work/explore-code-map/excursions/x12-result.md`.
- **Scoped nulls:** a null states what was and was NOT searched — it kills *this search under these conditions*, never the idea class.

## Return format

Result markdown at `excursions/x12-result.md`: findings per the six-point spec above, each claim cited; then scoped nulls and the unsearched space. Your final text is a data payload for the orchestrator, not a human-facing message.
