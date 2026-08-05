# Excursion Brief: where the why lives — stress-testing "comments suffice" against the real map

## The one named question

Does any content in f1Brainz's curated map — `decisions/` (15 files), `overlays/` (18 purpose/capability/constraint nodes), and the packets' judgment prose (Responsibility, Known Limits, Decision anchors, Open Structural Questions) — actually resist living as in-code comments, and is the known-false record as small as the human suspects?

## Type

research

**Why this type:** the human's lean is that comments suffice for the why layer, including known-false records ("we tried X and it failed"), and asked for an excursion "to explore the graph and see if there's anything that proves me wrong." This is a falsification pass over repo content — reading and classifying, nothing built.

## What "answered" looks like

`excursions/x8-result.md` with: (1) a classification of EVERY why-bearing item in the map corpus into: **(a) single-anchor** — attaches to one function/class/module, lives as its comment/docstring; **(b) multi-anchor** — spans a small named set of declarations; lives as duplicated/grouped comments (Doxygen-`\defgroup`-style membership markers make this workable); **(c) genuinely unanchorable** — no code location is its natural home (cross-cutting rationale, retired-alternative records whose code no longer exists, workflow/process notes); with counts per bucket and the actual items listed for bucket (c); (2) the known-false census: every "we tried X / X doesn't work / rejected because" record found, counted, and classified by whether its anchor code still exists; (3) the decision-files question specifically: for each of the 15 `decisions/` files, could it be decomposed into anchored comments + git history, or does something irreducible remain?; (4) an honest verdict: does anything prove the human wrong, stated per scoped-nulls discipline; (5) scoped nulls (what was NOT examined — e.g. other repos' maps).

## Budget / stop conditions

- Budget: ~45 minutes of reading and classifying. The corpus is bounded: `C:\Programs\f1Brainz\docs\architecture\` (~7,800 lines).
- READ-ONLY on f1Brainz. Outputs under `evidence/x8/` (a classification table CSV/JSON welcome) and the result file.
- Classify by reading the actual items — no sampling; assert the count you covered (the map has 15 decision files, 18 overlay nodes; say how many items total you classified).
- Do NOT redesign the map or propose storage machinery; the deliverable is the classification and the counter-examples, if any.
- **Scoped nulls:** one repo's map; a verdict here does not generalize to every codebase's why-content.

## Research excursion

- **Sources:** the map corpus itself (`docs/architecture/index.md`, `packets/*.md`, `decisions/*.md`, `overlays/*.yml`, `reference/*.md`); the code under `src/` to check whether an item's anchor exists; x1's result §3 for the earlier bucket estimates.
- **Findings format:** counts per bucket with the full bucket-(c) list; every claim checkable against a named file/section.

## Return format

Result markdown at `excursions/x8-result.md`: verdict up top (does anything prove the human wrong), classification table, known-false census, decision-file decomposition assessment, scoped nulls.
