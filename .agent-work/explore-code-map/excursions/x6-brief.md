# Excursion Brief: MATLAB structural extraction — is there a scip-matlab or quick equivalent?

## The one named question

Is there a SCIP indexer (or quick equivalent structural extractor) for MATLAB, and what container/transformer structure can the best locally-available route emit from superCoolSpaceSim's `matlab_src` (539 `.m` files) today?

## Type

prototype

**Why this type:** the human asked "can we test quickly" — the answer is a measured run, not a citation. A short verification search (does scip-matlab exist?) precedes the hands-on part.

## What "answered" looks like

`excursions/x6-result.md` containing: (1) verification: does any SCIP emitter for MATLAB exist (Sourcegraph org, community, sourcegraph.com docs) — cite what was checked; (2) which local routes were tried and what each cost: **MATLAB R2025b's own tooling headless** (`matlab -batch`; `mtree` parse tree, `matlab.codetools.requiredFilesAndProducts` file-level deps, `checkcode`), and if time allows tree-sitter-matlab as the no-MATLAB fallback; (3) what the best route emits in our vocabulary — counts of containers (variables/properties/persistent/global), transformers (functions/methods/scripts), and recoverable edges (calls, file-level deps), sampled for correctness; (4) MATLAB-specific hazards for a mapper (dynamic dispatch, `eval`, path-dependent resolution, scripts-vs-functions, classdef vs function files); (5) an adoption-cost verdict next to x1 (Python: 15 min) and x5 (C++: blocked); (6) scoped nulls.

## Budget / stop conditions

- Budget: ~60 minutes. MATLAB license checkout may fail or `-batch` may hang — timeout every MATLAB invocation (e.g. 300s) and fall back to tree-sitter-matlab if MATLAB is unusable after 2 attempts.
- `C:\Programs\superCoolSpaceSim` is READ-ONLY. All outputs under `.agent-work/explore-code-map/evidence/x6/`. Do not add its paths to any persistent MATLAB path/settings; use `-batch` with explicit addpath in-session only.
- Do NOT run the simulation itself — parse/analyze only.
- **Scoped nulls:** a null verdict states what was and was NOT tested; a failed route does not kill the others.

## Question
Is there a scip-matlab or quick equivalent, and what structure does the best local route emit from matlab_src today?

## Branch
measurement

**Why this branch:** the deliverable is a verified existence answer plus measured extraction counts.

## Host-project conventions
- **Runtime / language:** MATLAB R2025b at `C:\Program Files\MATLAB\R2025b\bin\matlab` (headless: `matlab -batch "cmd"` — no GUI, exits when done). Target: `C:\Programs\superCoolSpaceSim\matlab_src` (539 .m; subdirs actors/commands/core/examples/io/math/models/sensors). Windows 11; node/npm and Python available for tree-sitter fallback.
- **Task runner:** n/a.
- **Routing:** n/a
- **Other conventions:** none.

## Location
worktree

**Driver:** agent-driven; target repo read-only; outputs in explorer work area only.

## Stop conditions
- Answered when the six deliverable sections are filled (measured or crisply blocked).
- Budget and exclusions as above.

## Return format
`PROTOTYPE_RESULT` at `excursions/x6-result.md` — the answer, what was tested / NOT tested, what it taught, disposition.
