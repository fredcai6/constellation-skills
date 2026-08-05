# Excursion Brief: extractor fork, candidate B — AST-first single extractor

## The one named question

Can a pure-AST extractor (Python `ast` alone, no SCIP) emit the same statement lines for the same f1Brainz slice — and where exactly does its own cross-file name resolution break, measured against the SCIP index as ground truth?

## Type

prototype

**Why this type:** the human ruled the extractor fork is "decidedly determined by prototype." This is candidate B of a two-candidate design-it-twice; its twin (x7a, SCIP+sidecar) targets the same slice and output shape so the two are directly comparable.

## What "answered" looks like

`excursions/x7b-result.md` + `evidence/x7b/statements.jsonl` in the SAME line shape as x7a's brief (subject/predicate/object/qualifiers/ref/hash; deviate with stated reason). Result sections: (1) what was built — a single-pass `ast` walker with its own import/scope resolution (module-level: imports, attribute chains, self-methods; state your resolution rules explicitly); (2) statement counts by predicate; (3) **the resolution accuracy measurement — the load-bearing part**: for every call/read/write edge your resolver claims in the slice, check the subject/object symbol against what x1's SCIP index resolved (decode via `evidence/x1/decode_scip.py`); report resolved-correctly / resolved-wrongly / unresolved rates, and characterize the failure classes (dynamic dispatch, re-exports, star imports, method calls on inferred types — note x6 measured MATLAB's version of this hole at 56% of qualified calls); (4) cost accounting: lines of code, wall time, zero-external-dependency claim; (5) sample-verified correctness (hand-check ≥10 statements); (6) scoped nulls.

## Budget / stop conditions

- Budget: ~60 minutes. Slice = `src/utils` package plus its cross-package edges (both directions) — identical to x7a.
- `C:\Programs\f1Brainz` READ-ONLY. Outputs under `evidence/x7b/` only.
- Resolution: build the honest cheap version (per-module symbol tables + import following), not a type inferencer. Where you cannot resolve, emit the statement with an unresolved marker rather than dropping it — unresolved rate is a headline number.
- **Scoped nulls:** state what was and was NOT tested.

## Question
Can a pure-AST extractor emit the same statements, and what is its measured resolution accuracy vs SCIP ground truth?

## Branch
logic

**Why this branch:** working extraction slice proving an interface.

## Host-project conventions
- **Runtime / language:** Python stdlib only preferred (`ast`, `tokenize`); f1Brainz at `C:\Programs\f1Brainz`. SCIP ground truth: `evidence/x1/index.scip` + `decode_scip.py`. Windows 11, `py` = 3.12.
- **Task runner:** n/a.
- **Routing:** n/a
- **Other conventions:** none.

## Location
worktree

**Driver:** agent-driven; f1Brainz read-only; all writes in the explorer work area.

## Stop conditions
- Answered when statements.jsonl exists for the slice, the accuracy-vs-SCIP table is measured, and the result sections are filled.
- Budget as above; an honest "resolution accuracy is X% and here is where it dies" is the deliverable either way.

## Return format
`PROTOTYPE_RESULT` at `excursions/x7b-result.md`; statement artifact under `evidence/x7b/`.
