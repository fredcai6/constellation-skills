# File-ownership scope — issue-456

Enumerated BEFORE the plan freezes, per `commander-core.md`: every file and
decision-class the issue puts in scope, so `execute.json` can be checked to
carry a gate for each one. A gate imperative that merely *references* a
decision as "handled elsewhere" is not a substitute for that gate existing —
the missing gate surfaces only at review and forces a reopen.

Panel-independent: this list is what the plan must cover whichever candidate
wins.

## Files this run creates

| Path | Owning gate (to be assigned) | Note |
|---|---|---|
| `scripts/code_map/__init__.py` | gate 0 | package marker; the departure from 42 flat scripts |
| `scripts/code_map/` extractor module(s) | gate 0 + gate 4 | from prototype `astx.py`; two-pass AST walk, own name resolution |
| `scripts/code_map/` render module(s) | gate 0 + gates 5/6 | from prototype `render_map.py` |
| `scripts/code_map/` checks module | gate 1 | REWRITE, not port — prototype checks are print-only |
| `scripts/code_map/` CLI entrypoint | gate 0 | the prototype has NO argparse; hardcodes an external ROOT |
| `tests/test_code_map.py` | every gate | the suite CI runs |
| `tests/fixtures/` code-map corpus | gate 1, gate 9 | BOM fixture MUST live here — zero BOM files exist in this repo |
| `map/` page tree | gate 5, gate 6 | the committed artifact: `map/<dotted.module>/<Entity>.md`, module `INDEX.md`, top `INDEX.md`, `ids.jsonl` |

## Files this run modifies

| Path | Owning gate | Note |
|---|---|---|
| `.gitignore` | gate 0 | **newly identified.** Statement store, supplement, and position cache are rebuilt-not-committed and need entries. `.agent-work/` is deliberately TRACKED here, so the ignore rules must be narrow and explicit rather than a blanket scratch rule. |
| `skills/commander/references/commander-core.md` | cherry-pick | from `d102c05` |
| `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md` | cherry-pick | from `d102c05` |
| `skills/implementer/SKILL.md` | cherry-pick | from `d102c05` |
| `skills/scout/SKILL.md` | cherry-pick | from `d102c05` |

The cherry-pick is 4 skills files / 9 changed lines out of `d102c05`. That
commit also touches `.agent-work/explore-code-map/cycle-3.json`, which is
exploration scratch and must NOT ride this branch — so it is a scoped
cherry-pick of the `skills/` paths only, not `git cherry-pick d102c05`.

`52376d9` (cartographer `map-model.md`) is a SEPARATE change and is deliberately
NOT part of this integration.

## Files explicitly NOT touched

- `scripts/build_architecture_map.py` — the incumbent packet compiler. No
  functional overlap, no integration required.
- `skills/cartographer/**` — the judgment layer stays until a stated retirement
  gate that this run does not build.

## Decision-classes needing a gate

Each must be *owned* by a gate, not merely mentioned:

1. **Line base** (defect D1) — the store is 0-based and the schema is silent.
   Must be *declared*. Durable: every consumer inherits it. → gate 4.
2. **Statement-line schema** — folding kind, signature, span, docstring body,
   values, decorators into one schema, plus an extraction-window statement.
   Removes a pipeline stage rather than shipping one to deprecate. → gate 4.
3. **Nested-definition symbol identity** (defect D2) — how a nested def is
   distinguished from a top-level one that flattens to the same symbol.
   **Measured on this repo: 75 flat-name collisions, 1,848 nested defs.** → gate 2.
4. **Referenced-by semantics** — what the count includes versus what the name
   list shows; the defining module is in one and not the other. → gate 3.
5. **Production vs test caller split** — de-conflates unused from untested.
   Test pages are NOT deleted. → gate 6.
6. **Top-index routing tier** — 1,233 lines over 1,223 modules is not a routing
   surface. → gate 5.
7. **Tag vocabulary + the cull test** — collapse `Assumption:`/`Constraint:`/
   `Rationale:` if the consumer treats them identically. Vocabulary reach beyond
   this run. → gate 8.
8. **Stale-tag anchor hashing** — what constitutes a tag's anchor body, and what
   the run report says when it changed. → gate 7.
9. **Committed thresholds** — every threshold must be measured against THIS
   corpus (103 files / 3,411 entities / 52,292 lines), not inherited from the
   prototype's 1,224-file repo. → gate 1.
10. **Package layout** — `scripts/code_map/` as a package vs the 42 flat
    scripts. Already ruled by the human; carried to reconcile as a decision
    candidate because it governs future structure.
11. **Wrapped-docstring render split** (defect D3) → gate 9.
12. **BOM-prefixed files rejected by `ast.parse`** → gate 9, with a fixture.
13. **Branch-base practice** — cut trial branches from `origin/<default>`, never
    the local default. Already applied to this run's own branch. → gate 9.

## Coverage check

Thirteen decision-classes across ten gates, every created/modified file
assigned. The check to run before freezing: no row above lacks an owning gate in
the authored `execute.json`.
