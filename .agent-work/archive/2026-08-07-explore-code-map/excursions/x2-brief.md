# Excursion Brief: prior art — comment/concept layer derived alongside the structural layer

## The one named question

Has anyone built a system that derives a concept/comment layer **together with** the variable/function structural layer of a codebase — and what did they learn about how much of that job is procedural vs judgment?

## Type

research

**Why this type:** the human asked directly for prior art; this is a facts-and-citations question, not a build question.

## What "answered" looks like

`excursions/x2-result.md` with cited findings on: (1) systems that combine structural extraction (symbols, call/data edges) with a derived documentation/concept layer — doc generators that ingest structure (Doxygen graphs + docs), literate programming lineage, CodeWiki-style LLM wiki generators, concern graphs / feature-location tooling, architecture-recovery research (e.g. reflexion models, Moose/FAMIX), commercial tools (Understand, Sourcetrail, CodeSee, Glean-backed docs) — each with what is procedural, what needs judgment, and any measured quality/coverage numbers; (2) specifically: prior art on *hole-driven prioritization* (choosing which undocumented entities need descriptions first — centrality-based or otherwise); (3) specifically: prior art on *write-back* — documentation systems where generated/edited prose is stored back in the code rather than beside it; (4) contradictions between sources surfaced, not smoothed; (5) scoped nulls — what was NOT searched.

## Budget / stop conditions

- Budget: one focused research pass (~45 min of searching/reading); report even if inconclusive.
- Do NOT re-tread the parent's x5 survey (`.agent-work/archive/2026-08-05-explore-memory-graph/excursions/x5-result.md` — read it first; it covers SCIP/Kythe/Glean/Joern/CodeQL extraction, comment-density stats, feature-location's no-superior-technique result, CodeWiki's grounding finding). x2 goes specifically after *combined structural+concept systems*, hole prioritization, and write-back — the three things x5 did not chase.
- No code, no installs — reading and citing only.
- **Scoped nulls:** a null verdict states what was and what was **NOT tested/searched** — it kills *this search under these conditions*, never the idea class.

## Research excursion

- **Sources:** primary sources first — project docs/papers over blog summaries. Start: literate programming (Knuth's WEB, org-babel lineage) for write-back; Doxygen/Sphinx/Javadoc ecosystems for structure+prose coupling; academic: software architecture recovery surveys, concern graphs (Robillard), feature location surveys, code summarization eval literature (incl. LLM-era, 2023–2026); industrial: CodeWiki, Sourcegraph docs efforts, Glean at Meta, Understand/Sourcetrail; hole-prioritization: documentation-debt / doc-coverage tooling, PageRank-on-call-graph literature.
- **Findings format:** cited findings; each claim carries its source; contradictions surfaced, not smoothed.

## Return format

Result markdown at `excursions/x2-result.md`: findings per the "answered" spec, then scoped nulls and the unsearched space.
