# Excursion Brief: scip-python on f1Brainz — degree-of-coverage measurement

## The one named question

How much of f1Brainz's existing Cartographer map (`C:\Programs\f1Brainz\docs\architecture\`) can scip-python's output procedurally reproduce, and what does it structurally miss?

## Type

prototype

**Why this type:** the parent's x5 was one reading pass — nothing installed or run. This tests the load-bearing "extraction is nearly solved" assumption with running code, and produces the first degree measurement for "how much of the mapping job goes procedural."

## What "answered" looks like

`excursions/x1-result.md` containing: (1) whether scip-python actually runs against f1Brainz on this machine, and what it cost to get there; (2) what the emitted index contains in our vocabulary — counts and samples of containers (named variables/fields/params), transformers (functions/methods), and read/write edges between them; (3) a side-by-side against the existing map: which map content (index.md, packets, overlays, decisions) the SCIP output could procedurally reproduce, which it could partially support, and which it cannot touch (higher-level abstractions, capabilities, decisions, the "why"); (4) comment/docstring coverage measured on f1Brainz itself (what fraction of emitted entities have an attachable docstring/comment — the concept-layer seed density); (5) scoped nulls — what was NOT tested.

## Budget / stop conditions

- Budget: ~60 minutes of work; if scip-python cannot be made to run after 3 genuinely different attempts (e.g. npx, global npm install, different node version), report inconclusive with the exact errors — that is itself a finding about adoption cost.
- Do NOT modify anything in `C:\Programs\f1Brainz` — read-only. All outputs (index files, decoded dumps, scripts) live under the explorer work area `evidence/` dir or a temp dir.
- Do NOT build any storage/statement layer — this measures extraction only.
- **Scoped nulls:** a null verdict states what was and what was **NOT tested** — it kills *this test under these conditions*, never the idea class. Default next move after a null is another variant.

## Question
How much of f1Brainz's existing Cartographer map can scip-python's output procedurally reproduce, and what does it structurally miss?

## Branch
measurement

**Why this branch:** the deliverable is a measured comparison (coverage counts, gap lists), not a UI or a logic module.

## Host-project conventions
- **Runtime / language:** f1Brainz is Python (monorepo: `src/data/`, plus model/analysis packages; see pyproject.toml). scip-python is a Node/npm tool (`@sourcegraph/scip-python`); the SCIP index is protobuf — decode with the `scip` CLI (`scip print --json` or snapshot) or the protobuf schema.
- **Task runner:** n/a — this excursion runs its own commands.
- **Routing:** n/a
- **Other conventions the prototype must match:** Windows 11 host; prefer `npx`; Python 3.12+ available as `py`/`python`.

## Location
worktree

**Driver:** agent-driven; but f1Brainz itself is touched read-only, so no worktree of f1Brainz is needed — outputs land in the explorer work area only.

## Stop conditions
- Answered when the four deliverable sections above are filled with measured numbers (or an honest inconclusive with errors).
- Budget as above.
- Exclusions as above.

## Return format
`PROTOTYPE_RESULT` — the answer, what was tested and what was NOT tested, what it taught, any surviving module, and the disposition. The result lands at `excursions/x1-result.md` in the cycle record and on the ideas board before consolidation.
