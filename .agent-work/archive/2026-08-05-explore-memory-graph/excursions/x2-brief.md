# Excursion Brief: Two-speed memory — working vs long-term architectures

Cycle 2 (shotgun), `explore-memory-graph`. Human-initiated.

## The one named question

How do systems that split memory into a fast/sloppy working store and a maintained long-term store — in cognitive science AND in software/AI systems — handle capture, consolidation/promotion, and forgetting, and what should a "two-speed knowledge graph" steal from them?

Context for the searcher: the project is designing an agent memory graph with a proposed two-speed shape — a cheap-write working graph during a task, then an end-of-task "merge-up" that promotes proven conceptual changes into a maintained long-term graph, filtering sloppiness at promotion time. This is explicitly analogized to working memory vs long-term memory. We want to know what the real versions of that split actually do.

## Type

research

**Why this type:** prior art question spanning cognitive science and systems literature; answerable from published work.

## What "answered" looks like

A cited comparison covering both worlds: (1) cognitive science — e.g. working-memory models (Baddeley et al.), hippocampal→neocortical consolidation, complementary learning systems, sleep replay, forgetting curves; (2) systems/AI — e.g. write-ahead logs and LSM-tree compaction as the systems analog, ACT-R/Soar chunking, agent-memory designs (MemGPT/Letta, generative-agents memory streams with recency/importance/relevance scoring, reflection steps), caching hierarchies. For each: what triggers promotion, what the promotion unit is, what gets filtered/forgotten, and who has authority. End with: the 3–5 mechanisms most worth stealing for the merge-up design, and any evidence that the two-speed split is the WRONG shape (alternatives like single-store-with-decay).

## Budget / stop conditions

- Budget: one focused research pass; report even if partial. Depth on promotion/consolidation mechanics specifically; breadth elsewhere.
- Do NOT design the merge-up; do NOT touch this repo's code. Survey and comparison only.
- **Scoped nulls:** a finding that some mechanism doesn't transfer kills that mechanism under these conditions, never the two-speed concept.

## Research excursion

- **Sources:** web + academic literature (cognitive psychology, neuroscience of consolidation, databases/storage engines, LLM-agent memory papers). Prefer primary sources; name the paper/system.
- **Findings format:** each claim carries its source. Where cognitive science and systems disagree, surface the tension.

## Result artifact (required)

Write the full findings to `.agent-work/explore-memory-graph/excursions/x2-result.md` in the repo at C:\Programs\constellation-skills. The run is complete only when that file exists.
