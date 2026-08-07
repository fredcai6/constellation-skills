# Excursion Brief: the articles trial — real rendered node articles from the statement store

## The one named question

Do articles generated from the statement store read as a usable alternative to reading the code — and what does the generator find missing or wrong in the statements when forced to render them?

## Type

prototype

**Why this type:** the skeleton-usefulness claim (x1's bucket b, ~50% of the map) has only ever been estimated from line counts; this generates the real thing and puts it in front of the human, whose read is the verdict.

## What "answered" looks like

1. **The articles**: one markdown page per module of `src/utils` (9 modules), each containing: a module rollup (purpose from the module docstring, dependency edges in/out at module level) and per-entity articles for every class/function — signature, purpose prose, param docs where present, reads/writes/calls (internal separated from stdlib/third-party), callers-in count, and file:line source link. Entities with NO docstring render with an explicit hole marker (this is the hole queue made visible in place). Saved under `evidence/x11/articles/` as `<module>.md`.
2. **A one-page index**: `evidence/x11/articles/INDEX.md` — the 9 modules with one-line purposes and counts.
3. **The result file** (`excursions/x11-result.md`): what the generator could and could not produce from the statements alone — every place it had to reach back into source or skip a section is a measured gap in the statement vocabulary; rendering cost; honest self-assessment of readability; scoped nulls.

## Inputs

- `evidence/x7b/statements.jsonl` and `statements_all.jsonl` (primary; own-resolution extractor — the ruled pipeline). `evidence/x7a/statements.jsonl` may fill gaps (its `documents` and param-prose coverage is richer); mark any statement sourced from x7a.
- If a needed fact is in neither artifact (e.g. module-level docstrings, callers-in counts beyond the slice), you may run a small supplementary extraction over `C:\Programs\f1Brainz\src\utils` with Python `ast` (READ-ONLY on f1Brainz; scripts under `evidence/x11/`) — but LOG each supplement as a statement-vocabulary gap: the store should have had it.
- x9-result §3 for how tag-minted content would render (none exists yet in real docstrings — render the section only if present; its absence is expected, not a gap).

## Budget / stop conditions

- ~45 minutes. Rendering is deterministic templating — no LLM prose generation; every sentence in an article must be traceable to a statement or the source docstring. (The judgment residue stays visibly empty; that emptiness is honest and is part of what the human evaluates.)
- READ-ONLY on f1Brainz. All outputs under the work area.
- **Scoped nulls:** one package, one repo; readability verdict belongs to the human, not the generator.

## Question
Do generated articles read as a usable alternative to reading the code, and what statement-vocabulary gaps does rendering expose?

## Branch
measurement

**Why this branch:** the deliverable is the artifact plus measured gaps; the human's read is the outcome.

## Location
worktree

**Driver:** agent-driven; outputs in the explorer work area only.

## Return format
`PROTOTYPE_RESULT` at `excursions/x11-result.md`; articles under `evidence/x11/articles/`.
