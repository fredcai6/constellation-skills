# Design Spec — the code map: a derived, agent-facing map of a codebase


_Draft state. This spec has not passed the confirm gate._

## Confirmation

- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**
- Confirmed by:
- Date:
- Critic findings dispositioned: NO
- Assumptions exercised:
- Assumptions accepted untested:

## Intent

**Cross-file navigation should be cheap and trustworthy.** Today a human-authored Cartographer map carries that job; it is expensive to build, expensive to keep true, and it drifts. This design derives the structural layer from the code — which is truth — into small, bite-sized pages an agent loads deliberately.

Done feels like this: a dev agent picking up an issue is handed the specific map pages for the work, learns the blast radius before its first edit, and the map rebuilds itself in under a minute at the end of the run. The human-facing docent site is a later, secondary projection of the same store.

**Scoped honestly (critic IF1/IF2).** The map does *not* replace reading code, and it does not yet replace the Cartographer wholesale. It replaces the **structural layer and cross-file lookups**: who calls this, what breaks downstream, what does this function accept. Within-file questions stay with the source. The judgment layer (x1: the derived spine is ~7% of the curated map's text) stays with the Cartographer until a stated **retirement gate**: the comment-extraction pass shipped *and* a named tag-coverage threshold met on a real repo. Until then both exist, and the spec claims only what the evidence carries.

**Success measure:** cross-file lookups avoided per dispatch — not files unread.

**Intent risk, stated rather than buried in the queue.** The trial that motivates this also produced counter-evidence: the top index taught the consuming agent nothing, and a wrong `referenced by` line nearly shipped a broken `main`. Prior art (x12/ETH) records that pushed generated context can measurably harm. Consumption value rests on one use trace of five pages; it is the least-evidenced claim here and is gated accordingly in Testing pathways.

**This is a standard, not an invention.** Everything here composes existing tooling (Python's `ast`, comment conventions, markdown, git) into a convention the constellation skills know how to use. The prototype already exists and works; this spec is the instruction to productionize it.

## The prototype is the reference implementation

Cut issues against these files. They are working code with measured behavior, not sketches. All paths relative to `.agent-work/explore-code-map/` on branch `worktree-explore-code-map`.

| Prototype file | What it is | Measured |
|---|---|---|
| `evidence/x13/astx.py` | the extractor: two-pass AST walk with own name resolution, emits statement lines | 1,224 files → 515,678 statements in 9.7s; 9.26% unresolved (95% of that one class: `dispatch-unknown-base`) |
| `evidence/x13/supplement.py` | AST supplement: kind, signature, span, docstring body, attrs/values, decorators, `__all__` | 1,224 files in 2.2s |
| `evidence/x13/render_map.py` | the renderer: agent-lean per-entity pages + module indexes + `ids.jsonl` | 16,222 pages in 23.6s, deterministic (double-build byte-identical) |
| `evidence/x11/render_fn.py` | the ruled page format at small scale (readable reference for the layout) | median entity page 16 lines |
| `evidence/x13/checks.py`, `checks2.py` | diagnostic scripts — ASCII scan, entity reconciliation, one spot check, D2/D4 measurement | **print-only: no assertions, no exit code.** Read as measurements, not as a passing suite (critics IF3/TS1). Stage 4 is a rewrite, not a port |
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
4. **Check** — **must be rewritten, not ported (critics IF3/TS1/TS2, the panel's strongest convergence).** The prototype's `checks.py`/`checks2.py` are print-only diagnostics: zero assertions, no exit code, hardcoded repo root and spot-check target, no stored baselines. "All pass" in the table above means a human read output once — that is not a check. Production stage 4 asserts with a nonzero exit and committed thresholds, and must cover at minimum:
   - **determinism** — rebuild twice, `diff -r` clean (no implementation exists today; the cited byte-identical result was a manual observation);
   - **referenced-by semantics** — every page's caller count *and* module list checked against an independent source scan. A deterministically wrong blast radius rebuilds byte-identically forever, so determinism alone protects nothing;
   - **edge recall** — a hand-labelled sample per predicate with a floor, including `writes`, which SCIP cannot see at all (critic TS7);
   - **hole count** against a committed baseline (§8's "holes did not grow" currently has no line to grow against);
   - **template ASCII** — by exact-line provenance, not the current substring match against thousands of docstring fragments (critic TS5).

**Ruling: the tool run is the predominant workflow step**, followed by hole adjudication and cleanup — not a background service. No live incrementality requirement.

### 2. Storage layout (minimal machinery)

**Ruling after the critic panel (SY1/SY3): the committed artifact is the rendered page tree — the thing agents read and the only representation that was actually measured.** The separate source-mirrored `derived/` tree from x10-candidate-3 is dropped; keeping both bought the churn argument in one layer and paid it back in the next.

- **Committed:** `map/<dotted.module>/<Entity>.md`, module `INDEX.md`, top `INDEX.md`, `ids.jsonl`.
- **Not committed** (gitignored, rebuilt in seconds): `statements.jsonl`, the supplement, and the position cache.
- **No positions in the committed artifacts.** A page's `path:line, N lines` suffix moves to the position cache and is resolved at read time; `ids.jsonl` lines are `{"id","s"}` with no `q` (critic TS3). Positions are the churn that poisons every diff (measured: a 3-line edit rewrites ~450 position-bearing lines) — the rule now actually holds, because nothing committed carries one.
- **Facts, not occurrences** — each fact once, with a count `n` (preserves x4's validated call-frequency signal).
- Structural ids are **symbol paths**, disposable by design: regeneration is seconds and the interpreter already forced the developer to propagate any rename through the code.
- **Authored identity is what gets protected**, via the author-written `[stable-id]` — a free, author-supplied allocator.
- A committed **run report** per rebuild: name-resolved summary of what changed (minted/renamed + fact deltas) — the reviewer's artifact. **It carries no timings** (they go to an uncommitted report), so the determinism diff can cover it rather than being defeated by it (critic TS2).
- `rulings.jsonl` is **not built now** (critic SY2): it would redirect external references that have never been made. Named untaken road — add it the first time a real external link breaks.
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
- `ids.jsonl` at the map root is the single lookup: one sorted line per id, `{"id","s"}` (no position — critic TS3). Sorted and derived, so its git diff *is* the id-motion report.
- **Scope, honestly (critic SY2/IF6):** define the syntax, emit the file, stop. Concept links ride the author-written slug and are the durable path. **Structural links are best-effort — the mind map must tolerate dangling links.** No redirect table, no rename-motion machinery, until a real break happens.
- Duplicate slug = build error in the run report.

### 5. Tombstones

**Reduced to a convention after the critic panel (SY6): four mechanisms for ~6 lifetime events did not earn their build cost, and the ruled design anchors tombstones to the concept tree — which is the mind map, an unbuilt separate system. That dependency is now flagged rather than assumed.**

- **Ships now, as convention:** when you delete a `Rejected:` comment, paste its text where it still applies. No code.
- **Revives as machinery if** orphan volume ever exceeds what a reviewer notices — and only once the mind map exists to anchor to.
- The ruled design is preserved for that revival: dead limb on the concept tree, `origin` pointing at the removal commit, orphan flagged at re-derivation and ruled at the deleting PR, retrieval by location (surfaced because a plan touches the concept, never a list anyone reads).

### 6. Rendering register (agent-first)

- **One page per entity.** Median 15–16 lines at both 9-file and 1,224-file scale.
- Aggressively minimal: entity id as title, plain lines, no tables, no footers, no provenance markers, no stats. Template text is pure ASCII; docstrings verbatim (their non-ASCII is source truth).
- **The redundancy rule, narrowed after the critic panel (SY4):** *do not restate prose the file shows; DO carry the structural summary that saves opening the file at all.* Signature, kind, and the docstring summary stay — the trial's two clear wins were exactly cross-module signature lookups, and the literal reading of the old rule would have deleted them. What the rule forbids is re-narrating the body. What the page must lead with is still what `grep` cannot give: referenced-by, blast radius, cross-module structure, unresolved-edge honesty. *(Prior art: pushed prose overviews measurably harm; structural facts do not.)*
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

- **Ships now:** split `referenced by` into **production callers** vs **test callers**. This alone fixes the conflated signal (561 src entities with no inbound reference mix *unused* with *untested*).
- **Fix, do not delete (critic IF7):** test-entity pages carry a true-but-useless "referenced by: none" because pytest discovers rather than calls. Fix that line to say so. Deleting the pages would remove traversability into tests in the very section arguing test links are first-class, and page count costs nothing under pull-based loading.
- **Deferred to its own ticket (critics IF7/SY8):** the ranked coverage report. It is a different product with a different consumer, and `coverage.py` already answers the executed-line question. Build it when someone names a question `coverage.py` cannot answer — and ship it with a per-entity confusion count and a false-negative ceiling, not a module-level agreement check (critic TS9).
- **Named limit:** static direct-call reachability, not executed-line coverage. Fixture/helper indirection credits the helper; ~9% unresolved dispatch hides some edges. This complements `coverage.py`, it does not replace it.

## Per-section approval and design-it-twice disposition

The human directed a low-ceremony spec: *"this is an easy one — implement the thing we've made. you can make references to the prototype directly... lets not over think this, just do enough to keep our thoughts organized."* Approval is therefore section-level against the exploration's own rulings, each already made by him in-run and recorded in `IDEAS_BOARD.md` and the cycle files.

| Section | Approved by | Where ruled |
|---|---|---|
| 1 Pipeline | human | cycle-3 D1 ("agree with your method + scip as test oracle... definitely like your lighter footprint") |
| 2 Storage layout | human | cycle-3 x10 pick (minimal machinery), after design-it-twice |
| 3 Comment grammar | human | cycle-3 D2 ("good starting vocabulary"); `map-model.md` amendment signed off 2026-08-07 |
| 4 Identity / mind-map interface | human | 2026-08-07 ("ids as needed when the mindmap wants to hook into a function... establish the syntax now") |
| 5 Tombstones | human | cycle-2 ("functionally a dead limb on the concept tree we shouldn't forget about") |
| 6 Rendering register | human | 2026-08-07 (function-by-function; "aggressively minimize every excess character") |
| 7 Skills integration | human | 2026-08-07 (three directed work items; push-then-pull; two-tier handoff) — already implemented on this branch |
| 8 Maintenance loop | human | cycle-3 T2 (rebuild-and-diff per run, no live incrementality) |
| 9 Test-coverage projection | human | 2026-08-07 ("id actually like us to explicitly create links between functions and test files") |

**Design-it-twice disposition.** Run on the one interface where the shape was genuinely open — **the storage layout and node identity** (x10: three parallel candidates under distinct constraints, synthesis at `excursions/x10-result.md`, human picked). Also effectively run on **the extractor** (x7a/x7b: two full competing implementations, settled by measurement).

**Skipped, with reason, on the remainder:** the other interfaces are not open designs — they exist as working, measured prototype code (§"The prototype is the reference implementation"), and their shapes were each ruled by the human in-run. Re-designing a built-and-measured interface in parallel would produce candidates competing against evidence rather than against each other. The build queue's items are diffs against that code, not new interfaces.

## Testing pathways

| Pathway | Exercised by | Falsified by |
|---|---|---|
| Extraction correctness | SCIP as test oracle (x7a/x7b harness); entity reconciliation on source position | a symbol SCIP resolves that the AST pass misses, outside the named inference-rule gaps |
| Determinism | rebuild twice, `diff -r` exit 0 | any non-empty diff on unchanged source |
| Churn boundedness | map diff lines vs source diff lines, on **both** a local edit and a widely-referenced-symbol rename (the adversarial case, never measured) | **ratio above 3× on either case.** Threshold and unit stated because "small change, large churn" cannot be judged (critic TS6). Re-measure after build items 2–6, which move the number in both directions |
| Page format | ASCII scan; template-sourced non-ASCII is a bug | template text carrying non-ASCII |
| Consumption value | use-trace per dispatch **plus a no-map control arm** on the next trial | **a named fraction of loaded pages fails to answer the question that motivated the load** (per-dispatch, can actually fire) — replaces the old universal-quantifier bar, which one useful page in a hundred would pass (critics TS5/IF8) |
| Redundancy rule | per-page audit: which lines are recoverable from the file at that position | a page whose non-recoverable lines are a minority (currently untested — critic SY4) |
| Inbound-edge attribution | independent source scan of caller sets, all entities, not one hand-picked function | any page whose caller set differs from the scan (this is D2's falsifier — critic TS4) |
| Authored-layer staleness | anchor-span hash compared across rebuilds | a tag whose anchor body changed while its text did not, going unflagged (critics IF4/TS8) |
| Tag extraction | the six real tags in f1Brainz PR #733 as the first corpus | tags that extract into wrong or missing statements |
| Coverage projection | `tested by:` counts against `coverage.py` on a known module | systematic disagreement beyond the named indirection limit |

**Deferred:** multi-issue consumption value across many dispatches (production answers this); staleness harm (no measurement exists in the field either).

## Build queue (ranked, from measured defects)

**Reordered by the critic panel.** Two items moved to the front: the check stage (three critics converged on it) and D2 (the testability critic proved it corrupts data *today*, not later).

1. **A check stage that can fail** — rewrite per §1 stage 4: assertions, nonzero exit, committed thresholds, referenced-by semantics, edge-recall floors, hole baseline. Nothing else in this queue is trustworthy until a regression can go red.
2. **D2 — nested-definition symbol collision.** The renderer resolves callers through the store's flattened symbol, so a nested and a top-level definition that flatten together **merge their caller sets and both pages show the union**. 251 affected positions, 87 colliding definition sites. This corrupts `referenced by` now; it is not only a future anchor problem.
3. **Referenced-by trust fix** — the name list omits the defining module while the count includes it (nearly shipped a broken `main` in the trial); nothing says the count already excludes definition/import/docstring mentions (map 3 vs grep 7). Ships with #2 — same line.
4. **Statement-vocabulary merge, before productionizing the supplement (critic SY7)** — fold kind, signature, span, docstring body, values, decorators into the line schema; declare the line base (**D1**); add an extraction-window statement. Doing this first *removes* a pipeline stage instead of shipping one to deprecate it later.
5. **Top index second tier** — 1,233 lines over 1,223 modules is not a routing surface. The trial agent read 60 lines of it and learned nothing.
6. **`referenced by` split into production vs test callers** (§9) — de-conflates the 561 zero-inbound entities, and fixes the useless test-page line rather than deleting the pages (critic IF7).
7. **Stale-tag detector (critics IF4/TS8)** — hash each tag's enclosing entity span at extraction; on rebuild, flag any tag whose anchor body changed while the tag text did not, in the run report the reviewer already reads. Without it the design ships the predecessor's failure mode in a smaller box.
8. **Comment-extraction pass** — six real tags wait in f1Brainz main as its first corpus. Depends on #2. On first render, apply the **cull test** (critic SY5): if the consumer treats `Assumption:`/`Constraint:`/`Rationale:` identically, collapse them.
9. Small: BOM-prefixed files rejected by `ast.parse`; wrapped-docstring render split (**D3**); handoff practice (name which caller holds the value being plumbed; absolute interpreter paths; **cut trial branches from `origin/<default>`, never the local default branch** — an unpushed commit underneath silently widens the PR, as it did in the trial's merge).

**Deferred out of the queue by the panel:** the ranked test-coverage report (critics IF7/SY8 — build it when someone names a question `coverage.py` cannot answer, and ship it with a per-entity false-negative ceiling per TS9); `rulings.jsonl` and rename-motion machinery (SY2); tombstone machinery (SY6).

## Out of scope

- **Dataflow (def-use) edges** — would catch the argument-flow blindness the trial found ("carried then dropped" is invisible to call edges). Genuinely expensive; parked as a named candidate with prior-art support.
- **Runtime/execution-context edges** — prior art rates them on par with edit location; our map is entirely static.
- **The docent site** — secondary goal, separate projection.
- **MATLAB and C++ adapters** — behind the statement-line seam; C++ is proof-of-concept only per human ruling.
- **Serial-number identity machinery** — named untaken road; revive only if function-level external links dominate.
- Two f1Brainz issues found adjacent to the trial, for their own tickets: test runs dirty the tracked `data/f1_data_2023.db`; `DEFAULT_STORE_PATH` hardcodes one machine's absolute path.

## Critic findings and dispositions

Three cold critics (intent-fit / testability / simplicity), each reading the spec with no exploration record. 26 findings; full text at `excursions/critic-intent-fit.md`, `critic-testability.md`, `critic-simplicity.md`.

**Dispositions below are the agent's RECOMMENDATION, pending the human's one-pass triage at the confirm gate.** No finding was dispositioned RE-EXPLORE: the panel found spec overclaim, unspecified choices, and premature machinery — not a broken design. Three findings converge on one real defect (the check stage asserts nothing) and one converges on a live data bug (D2 corrupts `referenced by` today, not later).

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| IF3 | intent-fit | BLOCKING | Stage 4 "Check" checks nothing: `checks.py`/`checks2.py` have zero assertions and no exit code, so "all pass" means a human read printed output once; nothing checks `referenced by`, the most intent-critical line. A deterministically wrong blast radius rebuilds byte-identically forever. | EDIT | Correct and verified in source. The check stage becomes assertions with nonzero exit plus committed thresholds, and gains a semantic check on referenced-by against an independent scan. Promotes to build-queue #1. |
| TS1 | testability | BLOCKING | Same defect from the testability side: no assertion, no baseline, no threshold; `holes: 8583` has no recorded line to grow against; `ROOT` and the spot-check target are hardcoded so the suite cannot run on the repo it guards. | EDIT | Merged with IF3 as one build item. Hardcoded ROOT/spot-check target is a productionization requirement, stated. |
| TS2 | testability | BLOCKING | Determinism has no implementation (`checks.py` contains no rebuild-and-diff) and the committed run report carries wall-clock fields, making a byte-diff of two builds non-empty by construction. | EDIT | Real contradiction. Ruling: the run report is excluded from the determinism diff and carries no timing fields in its committed form; timings go to an uncommitted report. Determinism check gets written, not assumed. |
| SY1 | simplicity | BLOCKING | The spec never says which representation is committed. Pages carry positions (`method, path:414, 11 lines`), so committing them defeats §2's no-positions rule; not committing them means agents cannot read the map without building it. | EDIT | The genuine unspecified choice. Ruling to write into §2: the **page tree is the committed artifact** (it is what agents read and what was measured); positions inside pages are accepted churn on a gitignored-cache basis only if pages are rebuilt — so pages are committed WITHOUT the line-number suffix, which moves to the cache. Statements stay uncommitted. This deletes the separate `derived/` tree. |
| SY3 | simplicity | MAJOR | §2's source-mirrored `derived/` tree is not what the prototype builds, so the design-it-twice skip ("built and measured code") is false for §2, and every measurement cited belongs to the page tree. | EDIT | Correct; resolved by the SY1 ruling — §2 collapses onto the measured page tree, and the skip claim becomes true rather than being defended. |
| TS3 | testability | MAJOR | §4 is "the interface that must stay stable" yet has zero instances, no pathway row, and `ids.jsonl` is specified with positions — the churn §2 exists to prevent. | EDIT | `ids.jsonl` drops `q` to `{"id","s"}`; position resolution goes through the same cache as everything else. Add a pathway row exercised by minting two anchors and renaming one. |
| TS4 | testability | MAJOR | D2 is corrupting `referenced by` TODAY: the renderer resolves callers through the store's flattened symbol, so nested and top-level definitions that flatten together merge their caller sets. Not a future anchor problem. | EDIT | Materially correct and the single most valuable finding. D2 moves from build-queue #4 to #1, ahead of the referenced-by naming fix, since it corrupts the same line. |
| SY4 | simplicity | MAJOR | The redundancy rule, applied literally, deletes ~half of every page (title, position, signature, hole marker, and same-body call lines are all recoverable by opening the file); the 15-line median exists only because the rule is not enforced. | EDIT | Rule is overstated. Narrowed in §6 to: *do not restate prose the file shows; DO carry the structural summary that saves opening the file at all.* Signature and kind stay — the trial's two clear wins were exactly signature lookups. |
| IF1 | intent-fit | BLOCKING | The spec claims to replace the Cartographer function but the derived spine is 7% of the curated map's text; the other 93% rests on a comment grammar whose extractor does not exist and whose corpus is six tags. No interim ownership, no retirement criterion. | EDIT | Correct overclaim. Intent narrowed to what is evidenced: the derived map owns the structural layer and cross-file navigation now; Cartographer keeps judgment content until a stated retirement gate (extractor shipped + a named tag-coverage threshold on a real repo). |
| IF2 | intent-fit | MAJOR | "Traversable without reading it" contradicts §6's own rule and §7's "map for cross-file, source for within-file". The design actually serves cheaper cross-file navigation and blast radius. | EDIT | Correct. Intent restated to the goal the design serves; the success measure becomes cross-file lookups avoided, not files unread. |
| IF4 | intent-fit | MAJOR | Drift is relocated, not removed: derived facts get machinery, authored tags get one doctrine sentence. A stale `Constraint:` faithfully rendered is worse than no map. | EDIT | Accepted with the cheap detector TS8 names: hash the tag's enclosing entity span at extraction; flag on rebuild any tag whose anchor body changed while the tag text did not. New build-queue item. |
| TS8 | testability | MAJOR | Same finding from testability, plus: the "no staleness measurement exists in the field" excuse is about the literature, not about whether this build can detect its own rot. | EDIT | Merged with IF4 into one build item. The literature excuse is struck from the spec. |
| IF5 | intent-fit | MAJOR | The spec asserts the incumbent's expense as motivation, then never prices its own per-PR human cost (hole adjudication, rulings lines, orphan gates, hole-growth checks). | EDIT | Fair. Spec gains a stated expected per-PR human cost and the evidence that would show it exceeds the incumbent's. |
| IF6 | intent-fit | MAJOR | The must-not-break interface rests on an unadopted mechanism (zero anchor ids authored) backed by a deliberately disposable one, repaired by manual review. | EDIT | Accepted in the honest direction: spec states structural links are best-effort and the mind map must tolerate dangling links; concept links via `[stable-id]` are the durable path. No new machinery. |
| IF7 | intent-fit | MAJOR | §9 imports a second product (a test-gap tool) into a traversability spec, then proposes deleting test pages in the section whose premise is that test links are first-class. | EDIT | Split accepted: keep the prod/test `referenced by` split (serves the intent), defer the ranked coverage report to its own ticket, and fix the useless line rather than deleting test pages wholesale. |
| SY8 | simplicity | MINOR | Same bundling objection: ship the deletion and the split, defer the report until someone names a question `coverage.py` does not answer. | EDIT | Merged with IF7. Note the disagreement between them on deleting test pages — resolved in IF7's favour (fix the line, keep the pages). |
| SY2 | simplicity | MAJOR | §4's machinery has zero instances and no live consumer: `rulings.jsonl` redirects links that have never been made; duplicate-slug guards an empty namespace. | EDIT | Accepted. §4 reduces to: define the syntax, emit `ids.jsonl`, stop. `rulings.jsonl` and rename-motion reporting move to "add on first real break" — recorded as an untaken road, not built. |
| SY6 | simplicity | MAJOR | §5 specifies four mechanisms for ~6 lifetime events, and anchors them to the mind map — an unbuilt separate system, a dependency the spec never flags. | EDIT | Accepted. §5 becomes a one-line convention now (when you delete a `Rejected:`, paste it where it still applies); machinery revives if orphan volume exceeds what review notices. The mind-map dependency is flagged explicitly. |
| SY5 | simplicity | MAJOR | Four tags exceed what the evidence or the survival law supports; no consumer distinguishes `Assumption:`/`Constraint:`/`Rationale:`. Corpus is six tags, four of one kind. | EDIT | Partially accepted. The human ruled the four-plus-one as *trial* vocabulary with an explicit right to cull after contact; the spec now states the cull test — if the extractor's consumer treats them identically at first render, collapse to `Rationale:`/`Rejected:`/`See:`. Not culled preemptively. |
| SY7 | simplicity | MINOR | The supplement is a whole stage that build-queue #5 exists to delete; productionizing it first pays for it twice. | EDIT | Accepted as sequencing: the statement-schema merge moves ahead of productionizing the supplement, removing a stage rather than deprecating one. |
| TS5 | testability | MAJOR | The consumption-value falsifier is a universal quantifier ("every page parity-or-worse"), judged by the agent under test, with no control arm; meanwhile every other metric rewards emptier pages and the ASCII check is near-vacuous. | EDIT | Correct and important. Replaced with a per-dispatch criterion that can fail (a named fraction of loaded pages must answer the question that motivated the load) plus a no-map control arm on the next trial. ASCII check tightened to exact-line provenance. |
| IF8 | intent-fit | MAJOR | Same vacuous bar, plus: the trial's own counter-evidence (index taught nothing; referenced-by nearly shipped a broken `main`) is filed as build items rather than as intent risk. | EDIT | Merged with TS5. The counter-evidence is restated in the intent-risk section rather than only in the queue. |
| TS6 | testability | MAJOR | Churn boundedness has no threshold, no unit, one data point, on the flattering change type; the adversarial case (rename a widely-referenced symbol) was never measured, and two queued items move the number in opposite directions with no re-measurement gate. | EDIT | Accepted. Threshold stated as a ratio ceiling, the rename case added as a required measurement, and a re-measurement gate attached to the build queue. |
| TS7 | testability | MAJOR | The SCIP oracle is blind to `writes` (the reason it was demoted), and the falsifier's "outside the named gaps" clause lets any miss be reclassified; reconciliation compares definitions, not edges. | EDIT | Accepted. Adds a hand-labelled edge sample with a per-predicate recall floor, including predicates SCIP cannot see. This is the honest fix for a self-exempting falsifier. |
| TS9 | testability | MAJOR | The coverage falsifier is aggregate where the harm is per-entity; a false `tested by: none` drives both "write a test" and "delete this" wrongly. | EDIT | Accepted, and it rides with the IF7 deferral — when the report is built, it ships with a per-entity confusion count and a false-negative ceiling. |
| TS10 | testability | MINOR | §7 is already shipped, has no pathway row, and its evidence measures compliance, not benefit; the design could regress silently. | EDIT | Accepted. Pathway row added; the compliance-vs-benefit distinction is stated in the spec rather than left implicit. |
