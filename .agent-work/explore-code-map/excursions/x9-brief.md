# Excursion Brief: the prefix grammar — prior art, mapped onto the existing graph

## The one named question

What minimal comment-tag grammar does prior art support for our assertion classes — and how does that vocabulary map onto the existing Cartographer map-model's statement/edge types, so a classified comment becomes a graph statement mechanically?

## Type

research

**Why this type:** the human is "open for suggestions — what does prior art show, then how does that map to the existing graph." Reading and proposing; nothing built.

## What "answered" looks like

`excursions/x9-result.md` with: (1) a survey of shipped tag grammars — Javadoc/JSDoc/Doxygen tag sets, Python docstring styles (Google/NumPy/reST field lists), contract conventions (JML, Eiffel DbC, .NET code contracts), annotation/attribute systems (`@Deprecated`, Rust `#[deprecated]`, `#[must_use]`), and lightweight conventions (TODO/FIXME/HACK/XXX lineage, `# docstr-coverage:excused`) — for each: what assertion classes it covers, adoption friction, and what made it stick or die; (2) **a proposed minimal grammar (2–3 options, recommendation-led, not a menu)** covering the content classes x8 measured on the real map: assumption / requirement-constraint / explanation-why / known-false ("tried X, doesn't work") / grouping-membership (concept spanning, decision-id) — honoring IBIS discipline (tiny vocabulary; every tag must earn its place against the 454-item classification); (3) **the mapping table**: proposed tag → map-model statement/edge type (read `C:\Programs\constellation-skills\skills\cartographer\references\map-model.md` if present, else the map-model vocabulary visible in `C:\Programs\f1Brainz\docs\architecture\index.md` — nodes, `depends-on`/`supports`/`constrained-by`/`explained-by` edges, provenance/confidence fields) — showing for each tag what statement the crawler emits; (4) the residue: which of x8's resisting classes (deleted-anchor known-false, artifact-staleness, freeze-provenance) the grammar deliberately does NOT try to carry, stated as untaken roads; (5) scoped nulls.

## Budget / stop conditions

- Budget: ~45 minutes. Prior-art half is a focused pass; the mapping half is analysis over documents already in reach.
- Read first: `excursions/x8-result.md` (the content classes and their counts — the grammar's requirements), `excursions/x3-result.md` (why markers are what make classification easy; the composite-taxonomy finding), `excursions/x2-result.md` §1.2 (Doxygen grouping). Everything read-only.
- Do NOT invent project dialect: prefer existing, widely-known tag names wherever one fits (the human is expert; precise established jargon welcome, coined terms are not).
- Recommendation-led: converge to one recommended grammar with alternatives as named untaken roads.
- **Scoped nulls:** state what was NOT surveyed.

## Research excursion

- **Sources:** primary tool/language docs for the tag systems; x2/x3/x8 results for the measured constraints; the f1Brainz map for the statement vocabulary.
- **Findings format:** cited; contradictions surfaced; the proposal clearly separated from the survey.

## Return format

Result markdown at `excursions/x9-result.md`: survey → proposal (recommendation-led) → mapping table → untaken roads → scoped nulls.
