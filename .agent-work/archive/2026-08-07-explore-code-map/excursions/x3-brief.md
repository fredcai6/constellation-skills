# Excursion Brief: prior art — classifying code comments as typed assertions

## The one named question

What taxonomies and tools exist for classifying code comments by the *kind of assertion they make* (assumption, requirement/constraint, explanation/why, directive, TODO, ...), and has anyone mapped classified comments into a knowledge graph or queryable store?

## Type

research

**Why this type:** the human's working premise is "every comment is an assertion of some sort; we should be able to easily categorize them" and he assumes prior art exists. Confirming or scoping that premise is a facts-and-citations question.

## What "answered" looks like

`excursions/x3-result.md` with cited findings on: (1) published comment-classification taxonomies (academic and tooling — e.g. the comment-classification literature in empirical SE; language-specific conventions like Javadoc/doc-comment tags, Rust doc attributes, Python typing/deprecation markers; annotation conventions like SAL/JML/Design-by-Contract as formalized "assertion comments"); (2) measured classification accuracy where reported — is categorization actually "easy" (automatable with what precision, by rules vs ML vs LLM)?; (3) any system that stores classified comments in a graph/database for querying (comment → typed statement pipelines); (4) which taxonomy best matches the assertion framing (assumption / requirement / explanation) and what categories real corpora actually contain in what proportions; (5) scoped nulls — what was NOT searched.

## Budget / stop conditions

- Budget: one focused pass (~30–40 min); report even if inconclusive.
- Read `excursions/x2-result.md` and the parent's x5 result first (paths below) — do not re-tread combined structural+concept systems, hole prioritization, write-back, or comment-density statistics; x3 is only about *classifying comment content*.
- No code, no installs — reading and citing only.
- **Scoped nulls:** a null verdict states what was and what was NOT searched — it kills *this search under these conditions*, never the idea class.

## Research excursion

- **Sources:** primary sources first. Start: Pascarella & Bacchelli-style comment-classification studies (Java/Python/C++), Steidl/Hummel/Juergens comment quality work, "self-admitted technical debt" detection literature (TODO/FIXME mining), directive/contract conventions (JML, SAL annotations, Eiffel DbC, doctest), LLM-era comment-intent classification papers (2023–2026), and any comment→knowledge-graph pipeline.
- **Findings format:** cited findings; each claim carries its source; contradictions surfaced, not smoothed.

## Return format

Result markdown at `excursions/x3-result.md`: direct answer up top (does the human's "easily categorize" premise hold, with numbers), then findings per the "answered" spec, then scoped nulls.

Context paths (read-only):
- x2 result: `C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\excursions\x2-result.md`
- parent x5: `C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\archive\2026-08-05-explore-memory-graph\excursions\x5-result.md`
