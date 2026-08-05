# Excursion Brief: extractor fork, candidate A — SCIP + AST sidecar

## The one named question

Can a SCIP index plus a small AST sidecar emit our statement lines for one bounded slice of f1Brainz — containers, transformers, read AND write edges, calls, docstring attachments — and what does the glue actually cost?

## Type

prototype

**Why this type:** the human ruled the extractor fork is "decidedly determined by prototype." This is candidate A of a two-candidate design-it-twice; its twin (x7b, AST-first) targets the same slice and the same output shape so the two are directly comparable.

## What "answered" looks like

`excursions/x7a-result.md` + a statement-line artifact: JSON-lines at `evidence/x7a/statements.jsonl`, one statement per line, shape (deviate with a stated reason if reality demands):
`{"s": "<subject symbol>", "p": "reads|writes|calls|contains|documents|param-of", "o": "<object symbol or text>", "q": {"file": "...", "line": N}, "ref": "scip|ast", "hash": "<content hash>"}`

Result sections: (1) what was built and reused (x1's index + decoder at `evidence/x1/` are the starting point — do NOT re-index unless forced; state if you do); (2) statement counts by predicate for the slice; (3) the WriteAccess gap in practice — how the AST sidecar recovers writes (`ast.Store` contexts) and joins them to SCIP symbol identities: how hard was the join, where does it misalign; (4) cost accounting: lines of glue code, wall time, and the two-tool coupling risks; (5) sample-verified correctness (hand-check ≥10 statements against source); (6) scoped nulls.

## Budget / stop conditions

- Budget: ~60 minutes. Slice = `src/utils` package plus its cross-package edges (both directions). Do not extract the whole repo.
- `C:\Programs\f1Brainz` READ-ONLY. Outputs under `evidence/x7a/` only.
- Do not design storage beyond the line schema; no DB, no views.
- **Scoped nulls:** state what was and was NOT tested.

## Question
Can SCIP + an AST sidecar emit the statement lines for one slice, and what does the glue cost?

## Branch
logic

**Why this branch:** the deliverable is a working extraction slice proving an interface, not a measurement of an existing tool.

## Host-project conventions
- **Runtime / language:** Python; f1Brainz at `C:\Programs\f1Brainz` (src/). x1 artifacts: `evidence/x1/index.scip` (22MB), `decode_scip.py` (pure-Python decoder), `defs.jsonl`, `edges.jsonl` (regenerate from index.scip via decode_scip.py if the jsonl files are absent — they are gitignored). Windows 11, `py` = 3.12.
- **Task runner:** n/a.
- **Routing:** n/a
- **Other conventions:** none.

## Location
worktree

**Driver:** agent-driven; f1Brainz read-only; all writes in the explorer work area.

## Stop conditions
- Answered when statements.jsonl exists for the slice with all six predicates attempted and the result sections are filled.
- Budget as above; report honestly if the join proves harder than the budget allows — that IS the finding.

## Return format
`PROTOTYPE_RESULT` at `excursions/x7a-result.md`; statement artifact under `evidence/x7a/`.
