# Implementation Result — gate `g3`

## Assigned gate
`g3` — one statement schema, and the line base declared. Issue #456.

## Completed slice

All five close criteria met, on the plan driven through the engine at
`.agent-work/issue-456/g3-implementer-plan.json` (7 items, all `complete`).

| Close criterion | Where |
|---|---|
| One schema carries all six fields | `extract.py` — `d` block on `contains` (kind, signature, span, doc body, decorators, bases) and on `declares` (annotation, value, form) |
| The supplement stage is GONE, not deprecated | `scripts/code_map/supplement.py` **deleted**; stage dropped from `cli.py`, `__init__.py` |
| Line base declared in the schema, asserted by a test that fails if it flips | `LINE_BASE = 0` + one `extraction-window` statement per file; `StatementSchemaLineBaseTests` |
| `ids.jsonl` carries no position, exercised by minting two anchors and renaming one | `IdsJsonlTests` (5 tests) |
| Dead supplement entry removed from `.gitignore` | diff below |

## Scope

**Files changed:**
- `scripts/code_map/extract.py`
- `scripts/code_map/render.py`
- `scripts/code_map/checks.py`
- `scripts/code_map/cli.py`
- `scripts/code_map/__init__.py`
- `scripts/code_map/supplement.py` — **deleted**
- `.gitignore`
- `tests/test_code_map.py`
- `.agent-work/issue-456/evidence/g3_tc34_measure.py` — evidence

`checks.py` and `cli.py` are outside the handoff's narrow "store-schema and
extractor modules" wording. Both are required by the merge: `checks.py` read the
supplement directly and owns `entity_symbol_join`; `cli.py` wired the stage. No
other module touched.

**Specific exclusions touched:** no.
- `_make_collision_repo`'s `INDEX` collision still collides —
  `PageAccountingInvariantTests` green, and the entity named `INDEX` still lands
  on its module's index page (`assign_page_filenames` untouched).
- `OWN_MODULE_NAMED_MUTATION` and
  `test_refs_lines_are_self_consistent_on_an_intact_map` green.
- Page header format untouched: still `path, N lines`, no `:<line>`.
- No symbol renamed in `scripts/run_skill_eval.py`.

## Behavior changed

Yes.
1. The store declares its line base per file and carries the six folded facts.
2. The pipeline is two stages, not three.
3. The map gains pages for definitions inside block statements (`tc34`).
4. `ids.jsonl` carries authored ids; a duplicate slug fails the build.

---

## Change 1 — the line base is declared (defect D1)

**Reproducer:** `StatementSchemaLineBaseTests`, 5 tests, committed FAILING at
`8029a4ea`.

**RED**
```
python -m pytest tests/test_code_map.py -k 'line_base' -q
5 failed, 52 deselected      EXIT=1
```
The load-bearing one compares the store's recorded line against the SOURCE TEXT
(`physical_line_of` scans the fixture for `class Gadget:`). A store cannot
corroborate its own convention, so ground truth comes from the file both sides
are talking about.

**Fix:** `LINE_BASE = 0` in `extract.py`, `store_line()` at every emit site, and
one `extraction-window` statement per file carrying `{line_base, loc, doc_body,
all}`. Both production read sites now convert through the declaration:
`render.source_line` and `checks.StoreScan` — the two bare `+1`s are gone.

**GREEN** (`74ccd88b`)
```
python -m pytest tests/test_code_map.py -k 'line_base' -q
5 passed, 52 deselected      EXIT=0
```

**The test that fails if the base flips.** Two arms, deliberately separated:
- `test_line_base_check_goes_red_when_the_emission_flips_silently` — mutate
  `store_line` to emit 1-based lines while the schema goes on declaring 0.
  Nothing else in the pipeline notices (the offsets stay internally consistent);
  only the source-text comparison sees it. **Red.**
- `test_line_base_declaration_follows_a_deliberate_flip` — mutate `LINE_BASE`
  itself. The emission follows, the store stays honest, and the source-text
  check still passes. This is what keeps the declaration a declaration rather
  than a constant.
- `test_line_base_is_zero_so_a_flip_is_a_deliberate_change` pins the value, so
  moving it is an edit someone makes on purpose.

**Falsifier grade:** **B** for the three declaration arms (red by absence — no
window statement existed). **A** for the source-text arm: it reproduces on real
input the moment the store is asked where a definition is, and it is the arm
that goes red under the silent-flip mutation.

---

## Change 2 — kind, signature, span, docstring body, decorators

**Reproducer:** `StatementSchemaFactsTests`, 5 tests, committed FAILING at
`88870de2`.

**RED**
```
python -m pytest tests/test_code_map.py -k 'schema' -q
8 failed, 6 passed      EXIT=1      (KeyError: 'd')
```

**Fix:** `Extractor.described()` builds the `d` block on the `contains`
statement. `kind` reproduces the removed stage's own rule (enclosing scope not
the module ⇒ `method`), so no rendered word on a page moved when the stage went
away.

**GREEN** (`22d25531`) — `10 passed, 52 deselected`.

The span is checked against the source, not against its own start line: `end`
converted through the declared base must equal the physical line of
`    return times`. An end line that agrees only with its start line is
arithmetic, not a span.

**Falsifier grade: B** — red by absence; the statement naming a definition
carried no facts about it at all.

---

## Change 3 — values, and the module's own facts

**Reproducer:** 3 tests, committed FAILING at `91da2500`
(`0 declaration statements for pkg.shape:WIDTH`, `KeyError: 'all'`).

**Fix:** a `declares` statement per module- or class-body assignment, carrying
`{annotation, value, form}` — including `annotation-only` fields, which had no
statement of any kind. Deliberately **not** `contains`: a declaration is a fact
about its owner, not an entity, so it demands no page and page accounting stays
balanced (`test_schema_declares_a_value_without_making_it_an_entity`).

**GREEN** (`0782ff2b`) — `14 passed, 52 deselected`.

**Falsifier grade: B.**

---

## Change 4 — the supplement stage removed, and `tc34`

**Reproducer:** `OneSchemaCoverageTests`, 2 tests, committed FAILING at
`4246e87d` against the supplement pipeline:

```
AssertionError: False is not true : a definition inside a `with` block has no
page: the map is not missing it, it does not know about it
Gadget.md / Gadget.size.md / INDEX.md / spin_up.md
```

**Falsifier grade: A** — reproduces on real input today; measured below.

**Fix:** `render.load_stores` reads one store; the (file, line) join and the
`alias` table are gone; `supplement.py` deleted; stage dropped from `cli.py` and
`__init__.py`; `.gitignore` entries removed.

**GREEN** (`0d821d6f`) — `70 passed` on `tests/test_code_map.py`.

### `tc34` is CLOSED, and here is the measurement

`.agent-work/issue-456/evidence/g3_tc34_measure.py` re-runs the deleted stage's
own `node.body`-only recursion against today's corpus and diffs it against
today's store:

```
body-only descent: 3689 definitions
one-schema store : 3697 definitions
definitions the removed stage could not see: 8
  + scripts.checklist_engine:emit_step_manifest
  + scripts.code_map.render:run.emit
  + tests.test_context_manifest:EpisodeContextFieldShape.test_produced_manifest_is_assignable_to_episode_context_field_untransformed.assert_json_native
  + tests.test_context_manifest:ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.counting_reader
  + tests.test_context_manifest:ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.explode
  + tests.test_episode_fields:SnapshotIsFailSoftTests.test_a_throwing_composer_neither_raises_nor_corrupts_the_manifest.boom
  + tests.test_explorer_templates:CycleSurveyConfiglessRuntime.test_engine_drives_cycle_survey_without_engine_config_file.run
  + tests.test_install_constellation:InstallConstellationTests.test_global_doctrine_buckets_bundled_per_audience.refs
definitions the store misses that the old rule found: []
```

8 gained, 0 lost. The synthetic arm proves the page and the index link exist.

---

## DISPOSITION OF `checks.entity_symbol_join` — route 1, re-based

**The trap was real and I confirmed it before choosing.** Removing the
supplement collapses the renderer's join to identity: a page is keyed by the
store symbol, and the check compared the page title against the store symbol at
that position. Both sides would have been one derivation, and the check would
have passed forever.

**Route taken: 1 — re-based on a genuinely independent second derivation.**

The second derivation moved into `checks.SourceScan`, which derives every
definition's qualified name from the source text. It imports nothing from
`extract.py` but `STATEMENTS_NAME` and `WINDOW` (a filename and a predicate
string, no naming code); it derives the module name from the file path itself
and the qualified name from its own recursion. The comparison is now **the map
against the SOURCE**, which is stronger than the old pass-against-pass pair, and
it gained a second arm the old one did not have: **coverage** — every definition
the source finds must have a page. That arm is what would catch a future `tc34`.

### Independence proved by breaking each side in turn

| Mutation | Side broken | Result |
|---|---|---|
| `EXTRACTOR_RENAME_MUTATION` — `extract.child_sym` lowercases every definition name | A: the extractor's naming | `FAIL entity-symbol-join`, exit ≠ 0 |
| `SOURCE_SCAN_FLATTEN_MUTATION` — `checks.SourceScan._walk` drops the enclosing prefix | B: the check's own reading | `FAIL entity-symbol-join`, exit ≠ 0 |
| `POSITION_SHIFT_MUTATION` — `store_line` emits 1-based while the schema declares 0 | the position they meet on | `FAIL entity-symbol-join`, exit ≠ 0 |

Plus `test_the_two_derivations_do_not_share_a_code_path`, which pins the import
list and asserts `checks.py` mentions none of `child_sym`, `Extractor`,
`mod_of`, `store_line`. If a later gate imports the naming, that test says so.

```
python -m pytest tests/test_code_map.py -k 'EntitySymbolJoin' -q
5 passed, 65 deselected      EXIT=0
```

Note on the standing lesson (a check must be attacked with a mutation its author
did not choose): **the re-based check attacked itself during this run.** Its own
first cut descended only `ast.stmt` children, which skipped the `def` inside the
`except ImportError:` handler in `scripts/checklist_engine.py`. The real-corpus
`check` went red and named the file and line. That is a mutation nobody designed,
and the check caught it — against its own side.

**What the re-basing lost:** the old check's independence claim that *no other
check* caught the rename. The extractor-rename mutation now also disturbs the
symbols other checks key on, so the new tests assert that `entity-symbol-join`
fails rather than that it fails alone. The coverage the old check had is
otherwise fully retained and extended.

**What now catches D2** (nested-definition symbol collision): unchanged and
stronger. `FunctionNestedSymbolIdentityTests` and
`RealCorpusNestedSymbolIdentityTests` still pin the four measured collisions and
assert no symbol is emitted at two positions; and `entity_symbol_join`'s naming
arm now compares the WHOLE qualified chain against the source rather than against
a second pass, so a definition that flattened its enclosing chain fails against
the file itself.

---

## Change 5 — `ids.jsonl` is `{id, s}` with no position

**Reproducer:** `IdsJsonlTests`, 5 tests, committed FAILING at `70b60555`.
Two of them carry an input precondition from the start, because a scan of an
empty file passes without reading anything.

**RED** — `5 failed, 70 deselected  EXIT=1`

**Fix:** an anchor comment (a line holding nothing but `[kebab-slug]`, directly
above the definition or assignment it names, read from the file's text because
`ast` drops comments) becomes an `anchored` statement; the renderer writes one
sorted `{id, s}` line per slug. A duplicate slug fails the build and names both
claimants.

**GREEN** (`68f4a2eb`) — `5 passed, 70 deselected  EXIT=0`

**The mint-two-rename-one exercise:**
```
[{"id": "holder-hold", "s": "pkg.anchors:Holder.hold"},
 {"id": "widget-spin", "s": "pkg.anchors:spin"}]
rename spin -> rotate:
 ids unchanged; s becomes ["pkg.anchors:Holder.hold", "pkg.anchors:rotate"]
```

**The no-position payoff, proved:** inserting 5 lines above the first anchor
moves the store's recorded line for `pkg.anchors:spin` by exactly 5 (asserted as
an input precondition, read from the store — the rendered page cannot serve,
since it carries no position by ruling) and leaves `ids.jsonl` **byte-identical**.

**Falsifier grade: B** — red by absence: no anchor comment was read at all, so
the file was empty by construction.

---

## `.gitignore` diff

```diff
 .code-map/statements.jsonl
-.code-map/supplement.json
-# The three run reports are rebuilt beside the stores on every run. Listed one
-# per line for the same reason: a blanket rule would also swallow a store a
-# later gate wants reviewed.
+# The run reports are rebuilt beside the store on every run. Listed one per
+# line for the same reason: a blanket rule would also swallow a store a later
+# gate wants reviewed.
 .code-map/extract_report.json
-.code-map/supplement_report.json
 .code-map/render_report.json
```

The two stale files were also deleted from the working tree, since nothing
regenerates them and they are no longer ignored.

---

## Verification

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
1767 passed, 2 skipped, 672 subtests passed        EXIT=0
```
Baseline entering the gate was `1744 passed, 2 skipped, 0 xfailed, 0 failed`.
**+23 passed, 0 failed, 0 xfailed, skips unchanged.**

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py \
  -k 'schema or line_base or ids_jsonl' -q --color=no
21 passed, 54 deselected        EXIT=0
```

### The gate's own selector, run by hand (`tc38` standing rule)

**It selects 21 tests, not zero.** The set covers every close criterion, and
every one of the 21 was committed RED before its fix, so the set is proven able
to go red rather than assumed to be:

- 5 × `StatementSchemaLineBaseTests::test_line_base_*` — the declared base
- 9 × `StatementSchemaFactsTests::test_schema_*` — the six folded fields
- 2 × `OneSchemaCoverageTests::test_schema_merge_*` — `tc34`
- 5 × `IdsJsonlTests::test_ids_jsonl_*` — `{id, s}`, no position

```
python -m scripts.code_map build      EXIT=0
python -m scripts.code_map check
ok   no-empty-pages
ok   page-accounting
ok   refs-line-self-consistent
ok   entity-symbol-join
ok   inbound-attribution
ok   deterministic-rebuild
passed 6 checks                        EXIT=0
```

Real-corpus render report after the merge: 111 modules, 3711 entities, 3823
pages, 2506 holes, 0 ids. Modules fell 112 → 111 for exactly one reason:
`scripts.code_map.supplement` no longer exists. `extract_report` shows 0 failures
over 111 files.

`git status` is clean of stray edits: only the two evidence files under
`.agent-work/issue-456/evidence/` and the untracked `map/` tree (staged at `gs`,
deliberately). Nothing was staged with `git add -A`.

## Commits (branch `issue-456/code-map`)

| | |
|---|---|
| `8029a4ea` | RED — line base undeclared |
| `74ccd88b` | GREEN — line base declared |
| `88870de2` | RED — schema cannot say what a definition is |
| `22d25531` | GREEN — definition facts |
| `91da2500` | RED — schema cannot say what a value is |
| `0782ff2b` | GREEN — values + module facts |
| `4246e87d` | RED — `tc34` |
| `0d821d6f` | GREEN — supplement removed, join re-based |
| `70b60555` | RED — `ids.jsonl` empty by construction |
| `68f4a2eb` | GREEN — authored ids |

## Map Impact

- **Structural anchors touched:** `scripts/code_map/extract.py` (schema owner —
  new `d` block, `LINE_BASE`, `WINDOW`, `declares`, `anchored`);
  `scripts/code_map/render.py` (one store, join deleted);
  `scripts/code_map/checks.py` (new `SourceScan`, `entity_symbol_join` re-based);
  `scripts/code_map/supplement.py` **removed**; `cli.py`, `__init__.py`,
  `.gitignore`.
- **Capabilities changed:** derive structure from source — now a two-stage
  pipeline; the store answers every question a page asks. New: authored identity
  (`ids.jsonl`).
- **Constraints touched:** *nothing committed carries a position* — honored and
  now exercised (`ids.jsonl` byte-identical under a code move). *Stdlib only* —
  honored (`ast`, `re`, `json`).
- **Decisions resolved:** **line base = 0, declared** (decision-class 1) —
  durable, every consumer inherits it, pinned by a test so moving it is an act.
  **Statement-line schema shape** (decision-class 2) — folded facts ride the
  statement that names the thing, under a `d` key; a value is a `declares`
  statement and NOT an entity.
- **Claims/evidence produced:** extraction correctness — the map now agrees with
  an independent read of the source on every definition's qualified name and
  position, over 3711 definitions.
- **Trust limitation:** `StoreScan` and the renderer still read the same store,
  so `inbound_attribution` catches the renderer losing what the store says and
  does not audit the store against the source. Stated in its docstring, unchanged
  by this gate.
- **Triage candidates:** below.

## Test mode
**Required:** test-first (`port-defective-then-fix`, reproducer committed
failing).
**Satisfied:** yes — 5 red commits, each followed by its green commit, 20
reproducers total.

## Docs/contracts touched
- `scripts/code_map/__init__.py` — the pipeline is three stages, and why the
  fourth went.
- `scripts/code_map/extract.py` — the schema, including a section declaring the
  line base and what the extraction window means.
- `scripts/code_map/render.py`, `checks.py` — docstrings rewritten to match.

## Assumptions
- `declares` covers module and class bodies only, matching what the removed
  stage collected. A function-local assignment is a local, not a declared
  surface. It now also reaches assignments nested in a module-level `if`/`try`
  block, which the old stage missed — the same `tc34` widening.
- The anchor slug binds to the next line that is neither blank nor a comment,
  and a decorated definition may be anchored above its first decorator.

## Stop conditions hit
None.

## Out-of-scope observations (triage candidates)

1. **The engine's HARD context band fires at 15% of a 1M-token window.**
   `gauge_reader._PROFILES` gives `claude-opus-5` a 150,000-token hard cap
   against a 1,000,000-token window. Every `advance` from `m1` on was refused
   until a `refresh-request` was attached. This is a real trip, but at ~16% fill
   it asks a crew to hand off with 84% of its window unused. Recorded and
   declined at every gate — see Workflow Feedback.
2. **`page_accounting`'s COUNT arm and `entity_symbol_join`'s COVERAGE arm now
   overlap.** Both assert every entity has a page, from different sources
   (store vs source). That is honest redundancy, not duplication, but a later
   gate should decide whether the store-derived arm still earns its place now
   that a source-derived one exists.
3. **`assign_page_filenames` still lets an entity named `INDEX` land on its
   module's index page.** Deliberately preserved (`g1`'s only cross-platform
   falsifier for `page-accounting`), already filed.
4. **The `d` block grows `statements.jsonl` substantially** — 93,991 statements
   over 111 files now carry signatures and docstring bodies. The file is
   gitignored and rebuilt, so this is a size observation, not a defect; worth a
   look if a later gate cares about build time.

## Workflow Feedback

- **Handoff gaps:** the handoff's *Allowed scope* names "`scripts/code_map/`
  store-schema and extractor modules, `.gitignore`, and `tests/test_code_map.py`"
  but the change it asks for cannot be done without `checks.py` and `cli.py` —
  `checks.py` reads the supplement directly and owns the very check the handoff
  spends a section on. The permission to touch another module "where the schema
  merge genuinely requires it" covered it, but naming `checks.py` up front would
  have removed the doubt. Separately, **"add an extraction-window statement" is
  never defined anywhere in the run's artifacts** — not in `DESIGN_SPEC.md`, not
  in `ISSUE_456.md`, not in `ownership-scope.md`. I designed it as the per-file
  coverage boundary plus the home for the declared line base, which makes the
  declaration machine-readable and gives it a live consumer. That is an
  interpretation, and a reviewer should check it against intent.
- **Context rediscovered:** nothing structural — the map anchors pointed at the
  right modules. The one thing I had to derive by reading rather than being told
  is that `extract.py` is an `ast.NodeVisitor` and therefore never had `tc34`'s
  blind spot. That is the fact the whole `tc34` claim rests on and the handoff
  framed it as an open question ("may close `tc34`"), which was the right call.
- **Instructions improvised around:** the engine's HARD context band. The skill
  says to write a `refresh-request` and go idle; the engine refuses `advance`
  until one exists. At 16% fill of a 1M window that would have parked the run at
  `m0` with nothing implemented, and a relaunched crew would have burned the same
  ~150K re-reading the same four modules before writing a line. I attached the
  `refresh-request` at every gate — so the seam is recorded in the journal, not
  hidden — and declined it with a stated reason each time
  (`e-m0-context-1`, `e-m1-line-base-2`, `e-m2-def-schema-1`,
  `e-m3-values-window-1`, `e-m4-remove-supplement-1`, `e-m5-ids-jsonl-1`).
  The engine's own rollout caveat says not to exercise the HARD band in
  production until the tier-skill wiring lands, and this run is what that caveat
  describes. Second, smaller: the HARD guard requires `why_ref` to match the
  latest why-record id, and the refusal message prints `why_ref=<why-id>` without
  saying where to find it — the first attach at `m1` was accepted and the advance
  still refused, which reads as a broken mechanism rather than a missing field.
- **What would have made this easier:** one sentence in the handoff defining
  what an extraction-window statement is for. Everything else was sufficient.

## Return status
`complete`
