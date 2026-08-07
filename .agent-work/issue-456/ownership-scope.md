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
   **CORRECTED. The "75 flat-name collisions, 1,848 nested defs" figure written
   here was WRONG and is withdrawn** — it modelled the symbol as `module.name`,
   which is not what `astx.py:_func` emits. Measured against the real rule:
   **exactly 4 collisions**, all closure-in-method, listed individually in
   `reference/d2_collisions.txt`. D2 has a **second arm** the panel found —
   `visit_ClassDef` has no enclosing-chain branch, so a class defined inside a
   function is named as if module-level; **0 occurrences here**, so it is
   fixture-only, same standing as BOM. → gate `g2`.
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

**This claim was FALSE as first written and is corrected here (critic F11).** An
earlier version asserted "thirteen decision-classes across ten gates, every
created/modified file assigned." Two rows had no owning gate:

- **Decision-class 10 (package layout)** — marked "already ruled by the human,
  carried to reconcile." A ruling is not a gate. Now attached to gate 0, which
  is where the package actually gets created.
- **The four `skills/` files** — assigned to "cherry-pick", which is not a gate
  either: no close criterion, no command, no evidence. Still **UNOWNED**,
  pending the human's call on adding an integration gate.

The sharp edge, and the reason this matters rather than being bookkeeping: the
commit being cherry-picked (`d102c05`) is the one that ADDS the rule to
`commander-core.md` requiring "one gate for every file and decision-class in the
issue's stated file-ownership scope... a gate imperative that merely
*references* a decision is not a substitute for that gate existing." The plan
would ship that rule while breaking it on that same commit's own files.

Second-order, also unowned: those skills instruct implementers to start from a
**map entry point**. Nothing in the plan generates a committed map for THIS
repo, so on merge every crew handoff here cites an entry point that does not
exist. That is a decision — generate the tree, or state the dangle knowingly —
not an oversight to leave implicit.

The check to run before freezing: no row above lacks an owning gate in the
authored `execute.json`. ~~It does not pass yet.~~

**It passes now.** Resolved at plan-freeze against the authored 11-gate
`execute.json` (gate ids are `g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs`, which are NOT
the issue's 0–9 numbering used in the rows above):

| Row | Owning gate |
|---|---|
| `scripts/code_map/` package, CLI, discovery, `.gitignore` | `g0` |
| checks module + decision-class 9 (committed thresholds) | `g1` authors the movable-invariant checks; **`gb`** commits every threshold |
| decision-class 3 (D2 symbol identity), 4 (referenced-by semantics) | `g2` |
| decision-class 1 (line base), 2 (statement schema) | `g3` |
| decision-class 6 (top-index routing tier) | `g4` |
| decision-class 5 (production vs test caller split) | `g5` |
| decision-class 8 (stale-tag anchor hashing) | `g6` |
| decision-class 7 (tag vocabulary + cull test) | `g7` |
| decision-class 11 (D3 wrapped docstring), 12 (BOM + fixture) | `g8` |
| the four `skills/` files, `map/` page tree, decision-class 13 (branch base) | **`gs`** |
| decision-class 10 (package layout) | `g0` creates it; carried to reconcile as a decision candidate |

Two gaps named above are now closed rather than left implicit:

- **The four `skills/` files have a real gate.** `gs` owns them, with a close
  criterion, a command, and evidence — not the non-gate "cherry-pick" label.
- **The map-entry-point dangle is decided, not left implicit.** `gs` is
  sequenced LAST precisely so the committed `map/` tree exists before the
  handoff templates that cite an entry point land, and its close criterion
  asserts a rebuild-and-diff against a fresh build.

**`gb` is a gate the original ownership list did not anticipate.** It exists
because a threshold committed before `g3`/`g4`/`g5` would be invalidated three
times, and the cheapest in-gate fix each time is to edit the baseline — which
turns the check back into the print-only diagnostic this issue exists to
replace.
