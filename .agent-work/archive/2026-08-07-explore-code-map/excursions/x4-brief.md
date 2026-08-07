# Excursion Brief: hole-prioritization dry run on f1Brainz

## The one named question

Does graph centrality actually pick out the entities the human-curated map chose to document — i.e., does the planned hole-prioritization signal (centrality over the derived graph, holes from docstring coverage) reproduce f1Brainz's existing documentation choices when run on f1Brainz itself?

## Type

prototype

**Why this type:** it composes only existing tools (interrogate/docstr-coverage, networkx PageRank, pydeps or x1's SCIP index) into a measurement; the answer is a number, not a design.

## What "answered" looks like

`excursions/x4-result.md` containing: (1) f1Brainz's docstring-coverage numbers (overall + per-package) from an off-the-shelf coverage tool; (2) a centrality ranking of f1Brainz entities (PageRank or HITS over a dependency graph — module-level via imports at minimum; symbol-level from x1's SCIP index if available at `evidence/x1/`); (3) **the validation**: cross-check the top-K central entities against what f1Brainz's existing `docs/architecture/` map actually mentions (the Zaidman trick — the curated map is ground truth for "worth documenting"); report precision/overlap at K; (4) the deliverable artifact: a ranked "needs a description first" list — top central entities that currently have no docstring — as the first genuinely useful output of the whole exploration; (5) scoped nulls.

## Budget / stop conditions

- Budget: ~45 minutes. Report inconclusive with errors if tooling fights back after 3 distinct attempts.
- `C:\Programs\f1Brainz` is READ-ONLY. All outputs under `.agent-work/explore-code-map/evidence/x4/`.
- Do NOT write any docstrings/comments into f1Brainz; this produces a ranked hole list, not fills it.
- If x1's SCIP index is not yet present, fall back to a module-level import graph (pydeps or a small AST walker) — state which graph the centrality ran on.
- **Scoped nulls:** a null verdict states what was and what was NOT tested; module-level fallback does not kill symbol-level centrality.

## Question
Does centrality over the derived graph, intersected with docstring holes, reproduce the human-curated map's documentation choices on f1Brainz — and produce a credible "describe these first" list?

## Branch
measurement

**Why this branch:** the deliverable is measured overlap numbers and a ranked list.

## Host-project conventions
- **Runtime / language:** f1Brainz is Python (monorepo, `src/`); tools: `pip install interrogate docstr-coverage networkx pydeps` into a venv or `pipx`/`py -m pip --user`. Windows 11.
- **Task runner:** n/a — excursion runs its own commands.
- **Routing:** n/a
- **Other conventions:** none.

## Location
worktree

**Driver:** agent-driven; f1Brainz touched read-only, outputs land in the explorer work area only.

## Stop conditions
- Answered when coverage numbers, centrality ranking, map-overlap validation, and the ranked hole list exist (or honest inconclusive).
- Budget and exclusions as above.

## Return format
`PROTOTYPE_RESULT` at `excursions/x4-result.md` — the answer, what was tested / NOT tested, what it taught, the artifact (ranked list) location, disposition.
