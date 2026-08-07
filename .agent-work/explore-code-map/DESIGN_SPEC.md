# Design Spec — the code map: a derived, agent-facing map of a codebase

**UNCONFIRMED — DO NOT CUT**

_Draft state. This spec has not passed the confirm gate._

## Confirmation

- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**
- Confirmed by:
- Date:
- Critic findings dispositioned: NO
- Assumptions exercised:
- Assumptions accepted untested:

## Intent

A codebase should be traversable without reading it. Today a human-authored Cartographer map carries that job; it is expensive to build, expensive to keep true, and it drifts. This design replaces that *function* with a derived map: algorithms project the code — which is truth — into small, bite-sized pages an agent loads deliberately instead of spraying whole files into its context.

Done feels like this: a dev agent picking up an issue is handed the specific map pages for the work, learns the blast radius before its first edit, and the map rebuilds itself in under a minute at the end of the run. The human-facing docent site is a later, secondary projection of the same store.

**This is a standard, not an invention.** Everything here composes existing tooling (Python's `ast`, comment conventions, markdown, git) into a convention the constellation skills know how to use. The prototype already exists and works; this spec is the instruction to productionize it.

## The prototype is the reference implementation

Cut issues against these files. They are working code with measured behavior, not sketches. All paths relative to `.agent-work/explore-code-map/` on branch `worktree-explore-code-map`.

| Prototype file | What it is | Measured |
|---|---|---|
| `evidence/x13/astx.py` | the extractor: two-pass AST walk with own name resolution, emits statement lines | 1,224 files → 515,678 statements in 9.7s; 9.26% unresolved (95% of that one class: `dispatch-unknown-base`) |
| `evidence/x13/supplement.py` | AST supplement: kind, signature, span, docstring body, attrs/values, decorators, `__all__` | 1,224 files in 2.2s |
| `evidence/x13/render_map.py` | the renderer: agent-lean per-entity pages + module indexes + `ids.jsonl` | 16,222 pages in 23.6s, deterministic (double-build byte-identical) |
| `evidence/x11/render_fn.py` | the ruled page format at small scale (readable reference for the layout) | median entity page 16 lines |
| `evidence/x13/checks.py`, `checks2.py` | the self-checks: determinism, ASCII, entity reconciliation, spot check | all pass |
| `excursions/x13-result.md` | the dogfood use-trace — where the map paid and where it was blind | 5 pages loaded, honest verdict |
| `excursions/x10-candidate-3.md` | the storage design that won (minimal machinery) | full design doc |
| `excursions/x9-result.md` | the comment grammar with prior art and the survival law | — |

Full run: extract → supplement → render → checks is **~38 seconds cold** for a 1,224-file repo.

## Exploration record (digest)

- **Cycles:** 1 shotgun (measure the degree question) → 2 compare (extractor fork, grammar, comments-vs-graph) → 3 refine (storage design-it-twice, articles trial, prior art) → 4 trial (full map + real issue + regen).
- **Excursion answers (each scoped to its test):**
  - x1: SCIP reproduces the structural spine 100% and beat the curated map by 5 drift edges; the spine is 7% of the map's text. The degree question answers *mostly procedural*.
  - x2/x3: prior art draws the procedural/judgment line consistently; comment-as-typed-assertion prefixes are near-unprecedented as a *write-time* convention, which is what makes classification cheap.
  - x4: PageRank **refuted** as a hole-prioritization signal on this repo; raw call frequency validated. Free artifact: 692 ranked docstring holes.
  - x5: scip-clang is CI-only on Windows (C++ arm is proof-of-concept per human ruling). x6: no scip-matlab; `mtree` is the cheap MATLAB arm.
  - x7a/x7b: extractor fork settled by prototype — **AST-first wins, SCIP demoted to test oracle**. SCIP emits zero WriteAccess for Python.
  - x8: comments carry **89%** of the why; the one measured loss is deleted-anchor known-false records → the tombstone design.
  - x9: grammar v0 = `Assumption:` `Constraint:` `Rationale:` `Rejected:` + `See:`, `[stable-id]`, and the survival law (a tag survives when a tool visibly consumes it).
  - x10: storage design-it-twice, three candidates. Winner: minimal machinery — protect only authored identity.
  - x11: articles render from statements with no model prose; measured 8 vocabulary gaps and defect D1 (0- vs 1-based lines, schema silent).
  - x12: prior art on agent maps — per-entity pull-based structure has repeated measured gains; **pushed prose overviews measurably harm** (ETH: −0.5 to −2% success, +20–23% cost). The redundancy rule: generated context helps only when not cheaply recoverable from source.
  - Cycle 4 trial: the loop ran end to end. Map churn **98 lines vs 84 lines of source diff (~1.2×)**.
- **Scoped nulls carried:** Python only (x12 notes Python tooling may live in model parametric knowledge — niche languages untested); one repo; static reachability only; no staleness-harm measurement exists in the literature.
- **Rejected, with reasons:** PageRank prioritization (refuted by measurement); SCIP as the pipeline (heavier, worse write coverage); serial-number identity machinery (cost exceeds the benefit while regeneration is 2.3s — revive if external citation of structural ids becomes load-bearing); grouped plain-text store format (spends the JSON-lines substrate verdict); `llms.txt` as a model (no measured effect); pushed repo-overview prose (measured harmful).
- **Open threads carried:** MATLAB/C++ adapters behind the statement-line seam; docent website; dataflow (def-use) edges; runtime call edges.

## Chosen design

### 1. Pipeline (the Cartographer replacement)

Four stages, all deterministic, all rerunnable in under a minute:

1. **Extract** (`astx.py`) — two passes. Pass 1 indexes every module's top-level binding table across `src/`, `scripts/`, and `tests/`. Pass 2 walks each file tracking scopes and emits one **statement line** per fact:
   `{"s","p","o","q":{file,line,col},"ref","hash","res","why"}` with predicates `reads` `writes` `calls` `contains` `documents` `param-of` `imports` `inherits`. Unresolvable references are emitted explicitly with a failure class in `why` — never silently dropped.
2. **Supplement** (`supplement.py`) — a second AST pass for what the statement vocabulary does not yet carry: entity kind, full signature, span, docstring body, attribute values and annotations, decorators, `__all__`. *(These are the x11-measured gaps; folding them into the statement schema is a named build item, not a blocker.)*
3. **Render** (`render_map.py`) — one page per entity, module indexes, top index, `ids.jsonl`.
4. **Check** (`checks.py`) — determinism (rebuild twice, diff clean), ASCII-in-templates, entity reconciliation, and a named spot check.

**Ruling: the tool run is the predominant workflow step**, followed by hole adjudication and cleanup — not a background service. No live incrementality requirement.

### 2. Storage layout (minimal machinery)

- Source-mirrored `derived/` tree; two files per source file — `<name>.py.jsonl` (facts, with counts) and `<name>.py.md` (authored prose).
- **No positions in the committed store.** Line/column live in a gitignored cache that rebuilds in seconds. Positions are the churn that poisons every diff (measured: a 3-line edit rewrites ~450 position-bearing lines).
- **Facts, not occurrences** — each fact once, with a count `n` (preserves x4's validated call-frequency signal).
- Structural ids are **symbol paths**, disposable by design: regeneration is seconds and the interpreter already forced the developer to propagate any rename through the code.
- **Authored identity is what gets protected**, via the author-written `[stable-id]` — a free, author-supplied allocator.
- `rulings.jsonl` — the only hand-authored file; a flat redirect table for external references broken by renames. One line per rename PR, ruled at review.
- A committed **run report** per rebuild: name-resolved summary of what changed (minted/renamed/pending + fact deltas) — the reviewer's artifact.
- Build the named guards **first**: the empty-diff determinism assertion, the mis-pairing guard on auto-supersession, and the C++ colon collision fix in the relative-id rule.

### 3. Comment grammar (the why layer)

Bare `Word:` paragraph prefixes in ordinary comments — prior art shape is Go's `Deprecated:`:

- `Assumption:` `Constraint:` `Rationale:` `Rejected:` and the reference form `See: <target>`.
- `[kebab-slug]` for authored identity, minted **on demand only** — a comment line holding nothing but the bracket, directly above the `def`/`class`/assignment it names, same indent.
- **The code is truth.** When code changes because an assumption changed, the comment changes, and the comment updates the map. Constraints live *in* the function.
- **Survival law:** a tag survives when a tool visibly consumes it. Ship each tag with its consumer.
- **Doctrine rule:** no tag may assert the file's own history — that is git's job.
- First contact: six real tags authored in f1Brainz PR #733 (4 `Constraint:`, 1 `Rejected:`, 1 `Rationale:`), zero anchor ids. Open convention gap: where a tag goes when its rationale covers a whole function rather than a line.

### 4. Identity and the mind-map interface

The one external interface that must stay stable is the **mind map linking into the code map**.

- Mind map stores **repo + slug only** — never a path, never a line.
- `ids.jsonl` at the map root is the single lookup: one sorted line per id, `{"id","s","q":{file,line}}`. Sorted and derived, so its git diff *is* the id-motion report.
- Concept links ride the author-written slug (free, survives renames). Structural links use the symbol path and are caught by the run report when a rename breaks them; the fix is a one-line `rulings.jsonl` entry.
- Duplicate slug = build error in the run report. Deleted anchor = the orphan gate.

### 5. Tombstones

A dead limb on the concept tree, anchored to the concept that owns the problem (concepts outlive implementations), with `origin` pointing at the removal commit.

- **Creation gate, not a standing layer:** when re-derivation finds a `Rejected:`/`Rationale:` node's anchor deleted, the crawler flags an orphan — *promote to tombstone or let it die* — ruled at the deleting PR. Estimated volume ~6 per repo-lifetime.
- **Retrieval by location:** map-first plan queries surface tombstones because the plan touches their concept. History indexed by *where you'd stand when about to repeat it* — never a list anyone reads.

### 6. Rendering register (agent-first)

- **One page per entity.** Median 15–16 lines at both 9-file and 1,224-file scale.
- Aggressively minimal: entity id as title, plain lines, no tables, no footers, no provenance markers, no stats. Template text is pure ASCII; docstrings verbatim (their non-ASCII is source truth).
- **The redundancy rule governs content:** a page must lead with what a `grep` plus one file-read does *not* give — referenced-by, blast radius, cross-module structure, unresolved-edge honesty, tombstones. Never restate what reading the file shows. *(Prior art: pushed prose overviews measurably harm.)*
- The docent (human-facing site) is a **separate, richer projection** of the same store — secondary priority, cleanly separable.

### 7. Skills integration (how agents consume it)

Already live on this branch (`skills/commander/`, `skills/implementer/`, `skills/scout/`):

- **Two-tier handoff.** Top-level agents get the index pointer ("start your exploration here"); dispatched subagents get **named starting pages** ("start with this file") — the dispatcher did the map work at frame time and hands it down. The handoff template carries a **Map entry point** line.
- **Push-then-pull.** Push the entry point deterministically, let the agent pull neighbors. Ratified by both our own prior experiment (offered-and-declined got zero uptake; loading the skill flipped map-before-source 0/4 → 4/4) and the field (ToolFailBench names this failure "Tool-Skip").
- **Role-specific, light:** orchestrator uses blast radius for gate/wave fencing, surfaces recorded failures, treats in-scope holes as cheap adjacent work. Implementer starts at the entry point, reads referenced-by before editing, uses the map for cross-file questions and source for within-file ones, checks tombstones.
- **Writing tags is a skill function, not a culture hope** — the dev loop directs it.

### 8. Maintenance loop

Rebuild after change → read the run report → resolve orphan flags → check holes did not grow. Measured on a real change: **38 of 16,222 pages, 98 changed lines against 84 lines of source diff (~1.2×)**, bounded to the touched modules plus one importer index line.

### 9. Test-coverage projection (human-directed)

Extracting tests is what makes the inverse edge possible: a src entity's **`tested by:`** line is inbound `calls` filtered to `tests.*` — derivable from today's store with no new extraction (derived-views-never-stored).

- Split `referenced by` into **production callers** vs **test callers** — this fixes a currently-conflated signal (561 src entities with no inbound reference mix *unused* with *untested*).
- Emit a coverage report: src entities with zero inbound test edges, ranked by call frequency (x4's validated signal).
- **Stop rendering per-entity pages for test functions** (module indexes still list them) — 85% of them carry a true-but-useless "referenced by: none" because pytest discovers rather than calls. Halves the page count.
- **Named limit:** static direct-call reachability, not executed-line coverage. Fixture/helper indirection credits the helper; ~9% unresolved dispatch hides some edges. This complements `coverage.py`, it does not replace it.

## Testing pathways

| Pathway | Exercised by | Falsified by |
|---|---|---|
| Extraction correctness | SCIP as test oracle (x7a/x7b harness); entity reconciliation on source position | a symbol SCIP resolves that the AST pass misses, outside the named inference-rule gaps |
| Determinism | rebuild twice, `diff -r` exit 0 | any non-empty diff on unchanged source |
| Churn boundedness | map diff lines vs source diff lines per real change | a small source change producing large map churn |
| Page format | ASCII scan; template-sourced non-ASCII is a bug | template text carrying non-ASCII |
| Consumption value | use-trace per dispatch: page loaded, question answered, cheaper-than-grep? | a run where every page is parity-or-worse against grep |
| Tag extraction | the six real tags in f1Brainz PR #733 as the first corpus | tags that extract into wrong or missing statements |
| Coverage projection | `tested by:` counts against `coverage.py` on a known module | systematic disagreement beyond the named indirection limit |

**Deferred:** multi-issue consumption value across many dispatches (production answers this); staleness harm (no measurement exists in the field either).

## Build queue (ranked, from measured defects)

1. **Referenced-by trust fix** — the name list omits the defining module while the count includes it (nearly shipped a broken `main` in the trial); nothing says the count already excludes definition/import/docstring mentions (map 3 vs grep 7). Small diff, outsized trust impact.
2. **Top index needs a second tier** — 1,233 lines over 1,223 modules is not a routing surface. The trial agent read 60 lines of it and learned nothing.
3. **Test-coverage projection + test-page policy** (§9).
4. **Comment-extraction pass** — does not exist yet; six real tags wait in source. Needs **D2** first: nested definitions truncate their enclosing chain, colliding 87 definition sites (fatal once anchors rely on symbol identity).
5. **Statement-vocabulary extensions** — fold the supplement's facts (kind, signature, span, docstring body, values, decorators) into the line schema; declare the line base (**D1**); add an extraction-window statement.
6. Small: BOM-prefixed files rejected by `ast.parse`; wrapped-docstring render split (**D3**); handoff practice (name which caller holds the value being plumbed; absolute interpreter paths in verification commands).

## Out of scope

- **Dataflow (def-use) edges** — would catch the argument-flow blindness the trial found ("carried then dropped" is invisible to call edges). Genuinely expensive; parked as a named candidate with prior-art support.
- **Runtime/execution-context edges** — prior art rates them on par with edit location; our map is entirely static.
- **The docent site** — secondary goal, separate projection.
- **MATLAB and C++ adapters** — behind the statement-line seam; C++ is proof-of-concept only per human ruling.
- **Serial-number identity machinery** — named untaken road; revive only if function-level external links dominate.
- Two f1Brainz issues found adjacent to the trial, for their own tickets: test runs dirty the tracked `data/f1_data_2023.db`; `DEFAULT_STORE_PATH` hardcodes one machine's absolute path.

## Critic findings and dispositions

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
