# Implementation Result — gate `g2`, attempt 1

**PARKED AT A CONTEXT SEAM.** The engine's HARD context trip fired at the
`advance m0-context` boundary — gauge 17.9% of a 1M window (178K tokens) against
a 150K hard cap. Per doctrine I attached a `refresh-request` and stopped rather
than pushing through. `current` now reads
`REFRESH REQUESTED: m0-context` / `hand off now; do not keep working`.

Relaunch a fresh implementer against the SAME plan file
(`.agent-work/issue-456/g2-implementer-plan.json`). It resumes at
`m1-d2-symbol-identity` and should need nothing but that file, this result, and
`.agent-work/issue-456/g2-design-note.md`.

## Assigned gate
`g2` — symbol identity and page identity. Three defects: (a) D2 nested-symbol
naming, (b) referenced-by count/list disagreement, (c) page-filename case
collision.

## Completed slice
Defect (a)'s reproducer, **committed FAILING** as the gate requires — commit
`80702615`. Nothing under `scripts/` has been touched; no fix has landed.

## Scope
**Files changed:**
- `tests/test_code_map.py` (reproducer for defect (a) only)
- `.agent-work/issue-456/g2-implementer-plan.json` (+ journal) — the engine plan
- `.agent-work/issue-456/g2-design-note.md` — the design and the measurements
- `.agent-work/issue-456/evidence/g2-baseline-suite.txt`,
  `.agent-work/issue-456/evidence/g2-red-d2.txt`

**Specific exclusions touched:** no. No symbol in `scripts/run_skill_eval.py` or
any non-map source file was renamed. No g1 check was weakened or deleted. No
line-base or page-header change. `git add -A` was never used; every stage was an
explicit path list.

## Behavior changed
No. Test-only, and the tests are red by design.

## Test mode
**Required:** `test-first` — reproducer committed failing before any fix.
**Satisfied:** yes for defect (a); (b) and (c) not started.

---

## Defect (a) — D2, the enclosing METHOD is dropped

### Reproducer
`tests/test_code_map.py`:

- `RealCorpusNestedSymbolIdentityTests` — runs `extract` over THIS repository
  into a scratch directory and reads `contains` statements straight from the
  store (never through `render.load_stores`, which would ask the code under test
  what it thinks it emitted).
  - `test_the_four_measured_collisions_are_four_pairs_of_distinct_symbols` —
    the four collisions from `reference/d2_collisions.txt` are pinned as
    `D2_MEASURED_COLLISIONS`, **by string**, one subtest each: both true
    qualified names must be in the store exactly once, and the merged symbol
    must not be there at all.
  - `test_no_definition_symbol_is_emitted_at_two_positions` — the corpus-wide
    invariant behind them.
- `FunctionNestedSymbolIdentityTests` — synthetic, hermetic:
  two closures named `shared` in two methods of one class; a class `Bundle`
  defined inside a function; and a page-content test showing the reader-visible
  consequence.

### Why the criterion is named and not counted
"All four resolve" passes on an empty set, and it passes on an extractor that
quietly stopped emitting nested definitions. The four are pinned as strings, and
the corpus-wide arm is kept honest by the named arm sitting in the same class.

### RED output — exit code 1
`python -m pytest tests/test_code_map.py -q --color=no -k NestedSymbolIdentity`,
`FORCE_COLOR` and `PYTHONIOENCODING` unset. Full text:
`.agent-work/issue-456/evidence/g2-red-d2.txt`.

```
9 failed, 2 passed, 38 deselected

SUBFAILED(merged='tests.test_context_determinism:RealCheckoutSkew.project')
SUBFAILED(merged='tests.test_context_manifest:ProducerGuards.explode')
SUBFAILED(merged='tests.test_feedback_tooling:InboxLifecycleTests.f')
SUBFAILED(merged='tests.test_install_constellation:InterpreterProbeTests.fake_run')
FAILED RealCorpusNestedSymbolIdentityTests::test_no_definition_symbol_is_emitted_at_two_positions
FAILED FunctionNestedSymbolIdentityTests::test_two_closures_in_two_methods_are_two_symbols
FAILED FunctionNestedSymbolIdentityTests::test_each_closure_page_carries_its_own_docstring_and_not_its_sibling_s
SUBFAILED(symbol='pkg.nested:outer.Bundle')
SUBFAILED(symbol='pkg.nested:outer.Bundle.method')
```

All four named collisions fail individually. The sharpest line in the output is
the page-content one:

```
AssertionError: "The first method's closure" not found in
"# pkg.nested:Holder.first.shared\nmethod, pkg/nested.py, 3 lines\n\n
```python\ndef shared()\n```\n\nThe second method's closure.\n\n
referenced by: none found\n"
```

The page titled `Holder.first.shared` prints the **second** closure's docstring.
That is the protected intent failing in one line: the map states something
specific, confident and untrue.

### Falsifier grade
**A** — reproduces on this repository's real input today, on four named
entities, with no fixture required for the primary arm.

### Before / after symbol strings for the four named collisions
Before (measured, in the store now) → after (what the fix must produce):

| merged symbol emitted today | the two entities it merges |
|---|---|
| `tests.test_context_determinism:RealCheckoutSkew.project` | `…RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.project` and `…RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.project` |
| `tests.test_context_manifest:ProducerGuards.explode` | `…ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.explode` and `…ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.explode` |
| `tests.test_feedback_tooling:InboxLifecycleTests.f` | `…InboxLifecycleTests._filer.f` and `…InboxLifecycleTests._recorder.f` |
| `tests.test_install_constellation:InterpreterProbeTests.fake_run` | `…InterpreterProbeTests.test_probe_prefers_py_over_python3_when_both_succeed.fake_run` and `…InterpreterProbeTests.test_probe_timeout_candidate_falls_through_without_hanging.fake_run` |

### The class-in-function arm — 0 occurrences here, stated plainly
Measured by an independent AST walk over the tracked corpus: **0 nested classes,
0 classes defined inside a function, 31 closures defined inside a method.** The
class-in-function arm has **no real-corpus instance in this repository**, so the
synthetic `pkg.nested:outer.Bundle` fixture is the only place it runs anywhere.

### The fix
Not landed. Designed and written down in full at
`.agent-work/issue-456/g2-design-note.md` §"Defect (a) — the fix": collapse both
symbol expressions in `extract.py` onto `self.encl` (the enclosing scope's own
symbol + this name), add a parallel enclosing-class-symbol stack so `self.x`,
`cls.x` and the class-body name rule spell the same string, and strengthen
`checks.entity_symbol_join` from a leaf comparison to a whole-symbol one.

### GREEN output
Not reached.

---

## Defect (b) — referenced-by count and list

Not started. Designed in the note, including **the trap**: naming the page's own
module in the list destroys two g1 artifacts — `OWN_MODULE_NAMED_MUTATION`'s
byte-exact anchor in `render.py` and the input precondition of
`test_refs_lines_are_self_consistent_on_an_intact_map`. The design instead
accounts for the own module's sites explicitly (`+ N in this module`) and adds a
legend line stating what the count counted, then strengthens
`refs_line_self_consistent` (gap exactly 1 when the line accounts for own-module
sites, exactly 0 otherwise) without removing any failure mode it has today.

## Defect (c) — page-filename case collision

Not started. Designed in the note: deterministic per-name disambiguation of page
filenames inside each module directory, `hashlib` never `hash()`. The `INDEX`
collision family is deliberately left alone, because `_make_collision_repo` is
g1's cross-platform falsifier for `page-accounting` — logged as triage, not
silently fixed.

## Commander ruling on (c) — NOT falsified
Nothing measured contradicts it. The designed fix resolves any case-only pair
generally, without touching a production symbol, so there is no reason to rename
`class Verdict` or `def verdict`. No overrule.

---

## Evidence

Baseline, before any edit, cleared environment:

```bash
python -m pytest tests/ -q --color=no      # FORCE_COLOR, PYTHONIOENCODING unset
```
**Result:** exit 0 — `1729 passed, 2 skipped, 1 xfailed, 651 subtests passed`.
Exactly the shape the handoff states. Text:
`.agent-work/issue-456/evidence/g2-baseline-suite.txt`.

Reproducer, red:

```bash
python -m pytest tests/test_code_map.py -q --color=no -k NestedSymbolIdentity --tb=line
```
**Result:** exit 1 — `9 failed, 2 passed, 38 deselected`.

Full suite after the red commit: **not re-run** — the only change is a
deliberately failing test, so the suite is red by design at this seam and the
number would be misread as a regression. The next implementer takes it green.

`python -m scripts.code_map check`: **not run at this seam.** It exits 1 today
and correctly stays 1 until (c) lands. Note for the next implementer: `check`
reads the tree at `<root>/map`, which is stale — run `build` first or the exit
code means nothing.

## TDD evidence
- Failing test observed: yes, exit 1, output above, **committed in that state**
  at `80702615`.
- Passing test observed: not reached.
- Refactor while green: n/a.

## Docs/contracts touched
None. `render.py`'s D2 docstring and `checks.entity_symbol_join`'s "leaf name,
not the whole symbol" paragraph both assert D2 is unfixed and must move with the
fix — flagged in the design note, not yet edited.

## Assumptions
- The four collisions live in the STORE's symbol space, which is what
  `reference/d2_collisions.txt` measured. Only three of them are two-page
  merges; see the first triage candidate.

## Stop conditions hit
Engine HARD context trip at the `advance m0-context` boundary. `refresh-request`
`e-m0-context-1` attached to `m0-context`; the lease
`g2-implementer-attempt-1` is left ACTIVE so the relaunched implementer re-claims
the same id idempotently rather than taking it over.

## Out-of-scope observations (triage candidates)
1. **`supplement.walk` descends `node.body` only**, so any definition inside a
   compound statement (`with`, `if`, `try`, `for`) gets no page at all.
   Measured: one of the four D2 collision members, at
   `tests/test_context_manifest.py:771`, sits inside a `with` block and is
   invisible to the supplement while `extract.py` (which uses `generic_visit`)
   sees it. The two AST passes disagree about what the corpus contains, and
   `entity_symbol_join` cannot see it because it iterates supplement keys.
2. **The `INDEX` page-filename family.** An entity named `INDEX` still
   overwrites its own module's index page. It is left unfixed on purpose:
   `_make_collision_repo` is g1's only cross-platform falsifier for
   `page-accounting`, and reserving the stem would make that g1 test unable to
   fail. Fixing this needs the falsifier rebuilt on a different collision first.

## Map Impact
- **Structural anchors touched:** `scripts/code_map/extract.py` name resolution
  and `scripts/code_map/render.py` page naming — designed, not yet changed.
  `tests/test_code_map.py` gained the D2 reproducer.
- **Capabilities affected:** none yet; no behavior changed.
- **Decision candidates:** symbol identity for function-nested definitions —
  the enclosing METHOD must appear, and the definition symbol should equal
  `supplement.py`'s qualified key by construction, so the (file, line) join
  becomes a redundancy check rather than a translation.
  `@grade: guess · leans m1-d2-symbol-identity · settle: land the fix and read
  the supplement-key/store-symbol mismatch count, which is 25 today and must be 0`
- **Claims/evidence produced:** this repository emits 3619 distinct definition
  symbols, of which exactly 4 are emitted at two definition sites — the four in
  `reference/d2_collisions.txt` and no others, with no redefinition noise.
  Measured at commit `80702615`'s parent tree.
- **Trust limitations:** the supplement does not see definitions inside
  compound statements, so any check that iterates supplement keys is blind to
  them. Triage candidate 1.

## Workflow Feedback
- **Handoff gaps:** the handoff says the four D2 collisions are "all same-depth
  siblings" and treats them as four page-level merges. They are four **store
  symbol** merges; only three are two-page merges, because the supplement never
  records the fourth's sibling. The close criterion is still satisfiable as
  written — I asserted against the store — but a crew that went looking for four
  pairs of PAGES would have found three and concluded its measurement was wrong.
- **Context rediscovered:** the handoff names defect (b) but not the two g1
  artifacts that constrain its fix — `OWN_MODULE_NAMED_MUTATION`'s byte-exact
  anchor in `render.py`, and the input precondition in
  `test_refs_lines_are_self_consistent_on_an_intact_map` requiring some page to
  count a module it does not name. The obvious fix (name every module) breaks
  both. That took a full read of the g1 test file to find, and it is the single
  most expensive thing I rediscovered.
  Same shape for (c): `_make_collision_repo` is g1's `page-accounting`
  falsifier, so the `INDEX` collision must NOT be fixed while fixing the
  case-only one. Neither is in the handoff.
- **Instructions improvised around:** the handoff's verification commands all
  begin `env -u FORCE_COLOR -u PYTHONIOENCODING python …`. The Bash tool in a
  worktree-isolated session **refuses** that form — "this command runs `env` with
  `-m`, whose effect on the command it wraps can't be verified". I used
  `unset FORCE_COLOR PYTHONIOENCODING && python …`, which clears the same two
  variables. The engine's own POSIX-shell command checks still take the `env -u`
  form and are unaffected; this bites only an agent running the command by hand.
- **What would have made this easier:** a fourth section in the handoff listing,
  per defect, the g1 tests and mutation anchors that constrain its fix. The
  exclusion "do not weaken or delete any of the six checks g1 shipped" is the
  right rule but it does not tell you WHERE the tripwires are, and two of the
  three defects have one.

## Return status
`partial` — parked at a context seam, cleanly, with defect (a) red-committed and
the remaining work designed and measured. Not blocked on anything external.
