Productionize the derived code map: the pipeline, the page format, and the skills that consume it. **One issue, one Commander** — this is a build, not an epic. The design is confirmed and the prototype works; the job is to turn measured prototype code into a shipped tool with checks that can fail.

Confirmed spec: `.agent-work/explore-code-map/DESIGN_SPEC.md` on branch `worktree-explore-code-map` (Status CONFIRMED, Tommy, 2026-08-07). Read it first — it carries the full design, the exploration digest, the 26 cold-critic findings with dispositions, and the testing pathways. This issue body is the operative summary, not a replacement.

## The point

Cross-file navigation should be cheap and trustworthy. A dev agent picking up an issue gets handed the specific map pages for its work, learns the blast radius before its first edit, and the map rebuilds in under a minute at the end of the run.

**Scoped honestly:** this does *not* replace reading code, and it does not replace the Cartographer wholesale (the derived spine is ~7% of that map's text). It owns the **structural layer and cross-file lookups**. Within-file questions stay with the source. The judgment layer stays with the Cartographer until a stated retirement gate.

## The prototype is the reference implementation

Working code with measured behavior, all under `.agent-work/explore-code-map/` on `worktree-explore-code-map`:

| File | What it is | Measured |
|---|---|---|
| `evidence/x13/astx.py` | extractor: two-pass AST walk, own name resolution, emits statement lines | 1,224 files → 515,678 statements in 9.7s; 9.26% unresolved |
| `evidence/x13/supplement.py` | AST supplement: kind, signature, span, docstring body, values, decorators | 1,224 files in 2.2s |
| `evidence/x13/render_map.py` | renderer: per-entity pages, module indexes, `ids.jsonl` | 16,222 pages in 23.6s, double-build byte-identical |
| `evidence/x13/checks.py`, `checks2.py` | **print-only diagnostics — no assertions, no exit code** | read as measurements, NOT a passing suite |
| `evidence/x11/render_fn.py` | the ruled page format at small scale | median entity page 16 lines |

Full run extract → supplement → render is **~38s cold** on a 1,224-file repo. A real dogfood ran end to end: f1Brainz #708 fixed map-first and merged (`e3d6b542`), then regen measured **98 lines of map churn against 84 lines of source diff (~1.2×)**.

## Gates (the ranked build queue — suggested gate plan)

Order matters: the first two are what the critic panel moved to the front.

1. **A check stage that can fail.** Rewrite, do not port. Assertions with nonzero exit and committed thresholds, covering: determinism (rebuild twice, `diff -r` clean — no implementation exists today); **referenced-by semantics** (count *and* module list against an independent source scan); edge recall per predicate with a floor, including `writes` (SCIP cannot see it, so the oracle is blind there); hole count against a committed baseline; template-ASCII by exact-line provenance. Nothing downstream is trustworthy until a regression can go red. *(label: theme:checks-that-cannot-fail)*
2. **D2 — nested-definition symbol collision, corrupting data today.** The renderer resolves callers through the store's flattened symbol, so a nested and a top-level definition that flatten together **merge their caller sets and both pages show the union**. 251 affected positions, 87 colliding definition sites. This is the same line that nearly shipped a broken `main` in the trial.
3. **Referenced-by trust fix.** The name list omits the defining module while the count includes it; nothing says the count already excludes definition/import/docstring mentions (map says 3, grep says 7). Ships with gate 2 — same line.
4. **Statement-schema merge, before productionizing the supplement.** Fold kind, signature, span, docstring body, values, decorators into the line schema; declare the line base (defect D1: store is 0-based, schema silent); add an extraction-window statement. Doing this first *removes* a pipeline stage rather than shipping one to deprecate later.
5. **Top index second tier.** 1,233 lines over 1,223 modules is not a routing surface — the trial agent read 60 lines of it and learned nothing.
6. **Split `referenced by` into production vs test callers.** De-conflates the 561 zero-inbound src entities (unused vs untested). Fix the useless "referenced by: none" line on test pages; do **not** delete test pages.
7. **Stale-tag detector.** Hash each tag's enclosing entity span at extraction; on rebuild flag any tag whose anchor body changed while its text did not, in the run report. Without this the design ships the predecessor's failure mode in a smaller box.
8. **Comment-extraction pass.** Six real tags already wait in f1Brainz `main` as its first corpus. Depends on gate 2. On first render apply the **cull test**: if the consumer treats `Assumption:`/`Constraint:`/`Rationale:` identically, collapse them.
9. **Small:** BOM-prefixed files rejected by `ast.parse`; wrapped-docstring render split (D3); handoff practice — name which caller holds the value being plumbed, absolute interpreter paths in verification commands, and **cut trial branches from `origin/<default>`, never the local default branch** (an unpushed commit underneath silently widened a PR from 3 files to 179 during the trial).

## Rulings that constrain the build

- **Committed artifact is the rendered page tree** — `map/<dotted.module>/<Entity>.md`, module `INDEX.md`, top `INDEX.md`, `ids.jsonl`. Statements, supplement, and the position cache are gitignored and rebuilt. The separate `derived/` tree from the storage design is dropped.
- **Nothing committed carries a position.** A page's `path:line, N lines` suffix and `ids.jsonl`'s location both move to the rebuildable cache. Positions are the churn that poisons every diff.
- **The run report carries no timings** (they go to an uncommitted report) so the determinism diff can cover it.
- **Page register: agent-first, aggressively minimal.** One page per entity, entity id as title, plain lines, no tables/footers/provenance markers, template text pure ASCII, docstrings verbatim. Redundancy rule as narrowed: *do not restate prose the file shows; DO carry the structural summary that saves opening the file at all* — signature and kind stay, they were the trial's measured wins.
- **Skills integration is already live** on `worktree-explore-code-map` (`skills/commander/`, `skills/implementer/`, `skills/scout/`): two-tier handoff (top-level agents get the index pointer; dispatched crews get named starting pages via the handoff's **Map entry point** line), push-then-pull, role-specific guidance. Keep it working; it ships with this branch.
- **Not built now, deliberately** (critic panel cut them as premature): `rulings.jsonl` redirect table, rename-motion machinery, tombstone machinery (one-line convention instead), and the ranked test-coverage report. All recorded as untaken roads in the spec with their revival conditions.

## Testing pathways (falsifiers, from the spec)

| Pathway | Falsified by |
|---|---|
| Extraction correctness | a symbol SCIP resolves that the AST pass misses, outside the named inference-rule gaps — plus a hand-labelled edge sample per predicate below its recall floor |
| Determinism | any non-empty diff on unchanged source |
| Churn boundedness | ratio above **3×** on either a local edit **or** a widely-referenced-symbol rename (the adversarial case, never yet measured) |
| Inbound-edge attribution | any page whose caller set differs from an independent full scan |
| Redundancy rule | a page whose non-recoverable lines are a minority |
| Consumption value | a named fraction of loaded pages failing to answer the question that motivated the load, per dispatch, **with a no-map control arm** |
| Authored-layer staleness | a tag whose anchor body changed while its text did not, going unflagged |

## Accepted untested (human-signed at confirm)

Consumption value across many dispatches (one 5-page use trace, no control arm); churn under a widely-referenced-symbol rename; staleness detection (designed, unbuilt); non-Python languages; the mind-map interface end to end (zero anchor ids exist anywhere yet).

## Provenance

Exploration `explore-code-map`: 4 cycles, 15 excursions, 3-lens cold critic panel (26 findings, all dispositioned, zero re-explores). Branch `worktree-explore-code-map` holds the spec, the ideas board with every verdict and rejected idea, the excursion results, and the prototype.

