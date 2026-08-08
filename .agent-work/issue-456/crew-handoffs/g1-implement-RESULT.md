# IMPLEMENTER_RESULT — gate `g1`: invariants that cannot move

Issue #456. Written by the successor crew (`attempt-2`) on the predecessor's
plan; the predecessor's three checks are re-reported here and re-attacked, so
this file covers the whole gate and nothing needs to be read alongside it.

**Verdict: the gate's work is done.** `scripts/code_map/checks.py` is rewritten,
six checks ship, every one of them has been shown red under a mutation of the
property it guards, and every one has been attacked once more with a mutation
its author did not design for it. The full suite is green at the boundary.

---

## 1. The rule that outranks the rest

> A check that cannot go red is not a check.

Every check below is shown failing with a **nonzero exit**. Every mutation runs
against a **copy** of `scripts/code_map` (`tests/test_code_map.py:mutated_package`)
so the shipped tree is never edited in place, and every mutation has an
**unmutated positive control** run first — a red that is not attributable to the
mutation is not evidence.

The harness fails LOUDLY rather than silently: an anchor that does not occur
exactly once, a substitution that does not land, or a replacement whose count
does not go up by exactly one raises `HarnessError`, because a mutation that
quietly failed to apply produces a run indistinguishable from a passing one.

---

## 2. My move-invariant-vs-baseline rule

Stated explicitly because the handoff says later gates will be held to it.

> **A check is a move-invariant if its expected value is recomputed from the map
> on every run. It is a baseline if its expected value comes from a memory of
> this corpus.**

The distinction is *not* "does it mention a number". `pages == 1 + modules +
entities` mentions three numbers and is an invariant, because all three are read
off the map each time and the identity holds at any corpus size. `modules == 112`
mentions one number and is a baseline, because 112 is a remembered fact that a
legitimate change makes false.

Three corollaries I applied:

1. **A relational identity between two independently-derived numbers is an
   invariant.** Both sides must come from different derivations; a number
   compared against itself is a tautology, not a check (that is `tc18`, and the
   render report's `pages` field is the standing example).
2. **A page's rendered text, header format, section order and link spelling are
   shape.** Shape belongs to `gB`. This is why the two survivors in §5 were
   routed to `g4` instead of being fixed here.
3. **A structural constant that is fixed by the layout rather than by the
   corpus is allowed, and must be named.** There is exactly one top index at any
   corpus size; it lives in `checks.TOP_INDEX_PAGES`, in one place, so that the
   gate which adds an index tier has to change it deliberately.

---

## 3. Every check, its mutation, its command, its exit code

Common commands:

```
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/test_code_map.py -q --color=no
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/ -q --color=no
```

`python`, never `py` — `py` has no pytest and its failure reads as a clean run.

### 3.1 `no-empty-pages` (predecessor; `tc26`)

A page that exists and holds nothing is a page the map counts and a reader
cannot use. The render report's `pages` is `rglob("*.md")`, which counts a file
created and never written.

| | |
|---|---|
| mutation | truncate `map/pkg.thing/Widget.md` to zero bytes |
| test | `CheckExitCodeTests::test_check_exits_non_zero_when_a_page_is_empty` |
| observed | `cli.main(["check"])` returns **1**, output names `Widget.md` |
| positive control | `test_check_exits_zero_on_an_intact_map` → **0** |

TDD red was observed against the print-only module before the rewrite: `1 failed,
2 passed`, the assertion message being the whole print-only diagnostic dump over
a map with a zero-byte page — `run()` printed four sections and returned a
literal `0`.

### 3.2 `page-accounting` (new — **the RED invariant**, §4)

Two arms:

- **coverage** (shape-free): every module and every entity the store declares
  must be the **title** of some page. It never says where a page lives or what
  it is called, so no later gate moves it.
- **count**: `pages == 1 + modules + entities`. This is the identity the render
  report contradicts.

| mutation | test | observed |
|---|---|---|
| `class INDEX` collides with its own module's `INDEX.md` (`_make_collision_repo`) | `test_the_invariant_goes_red_when_two_pages_resolve_to_one_file` | exit **1**, `FAIL page-accounting`, names `pkg.thing` as a module index the map claims and does not have |
| delete `map/pkg.thing/helper.md` | `test_the_invariant_goes_red_when_a_page_is_simply_deleted` | exit **1**, names `pkg.thing:helper` |
| delete one page **and** add one stray page | `test_the_invariant_goes_red_when_the_books_balance_but_a_page_is_gone` | coverage arm fires with the count arm silent |
| — | `test_the_page_accounting_invariant_holds_on_an_intact_map` | positive control, `[]` |

The fixture collides `INDEX` rather than `Verdict`/`verdict` on purpose: the real
collision needs a case-insensitive filesystem, so a fixture built on it would
prove nothing on Linux. The `INDEX` collision collides on every platform.

**The third row is a hole I found by attacking my own check.** The count arm
alone calls a map healthy when one page is lost and one stray page is added,
because the arithmetic balances. Coverage is therefore asserted on its own,
not merely reported as a diagnostic when the count is off.

### 3.3 `refs-line-self-consistent` (new)

Page-local — reads the page and nothing else. The rules are the arithmetic the
line must satisfy whatever the numbers are: no module named twice; never more
named than counted; at most **one** counted module unnamed (the page's own, which
the renderer omits because the count already implies it); `sites >= modules`;
zero sites and zero modules arrive together.

| | |
|---|---|
| mutation | `render.py`: `ext = sorted(m for m in callers if m != mod)` → `sorted(m for m in callers)` — the page names its own module in a list whose count already accounts for it |
| test | `test_self_consistent_line_goes_red_when_a_page_names_its_own_module` |
| observed | `check` exits **1**, `FAIL refs-line-self-consistent`, output contains `its own module` |
| positive control | `test_refs_lines_are_self_consistent_on_an_intact_map` → `[]`, with an input precondition asserting some page actually exercises the at-most-one-unnamed rule |

**Its independent scope is measured, not argued.**
`test_self_consistent_check_sees_pages_the_store_check_cannot` writes
`referenced by: 1 sites in 3 modules (a, b, c)` onto `map/INDEX.md`, then asserts
`inbound_attribution(m) == []` and that `refs_line_self_consistent` names
`INDEX.md`. `inbound-attribution` only walks pages whose title names a known
entity; the top index is not one. If that ever stops holding, the test says so
and this check should be declared redundant rather than kept out of politeness.

**What it does NOT prove:** that the numbers are *right*. A line can be perfectly
self-consistent and completely wrong — that is `inbound-attribution`'s job, and
`inbound-attribution` is strictly stronger wherever the store is readable.

### 3.4 `entity-symbol-join` (new)

`extract.py` and `supplement.py` are two **independent AST passes** over the same
source, welded by a `(file, line)` join that decides whose docstring and whose
callers a page shows. This check compares the join's output against a third fact
neither pass shares with the other: the entity's own **leaf name**. Leaf only,
because the store truncates the enclosing chain for entities nested inside a
function (D2, owned by `g2`) — so the chains legitimately differ today and the
leaf does not, and this check will not go red at `g2` for the wrong reason.

| mutation | test | observed |
|---|---|---|
| `supplement.py`: `"line": child.lineno` → `child.lineno + 1`, desynchronising the two passes | `test_join_goes_red_when_the_two_ast_passes_disagree_about_a_position` | exit **1**, `FAIL entity-symbol-join` |
| `supplement.py`: lowercase every entity name, leaving every position intact | `test_join_catches_a_rename_that_every_other_check_agrees_with` | exit **1**, and **`entity-symbol-join` is the only failing check** |
| — | `test_every_page_title_agrees_with_the_store_symbol_it_is_joined_to` | positive control, `[]` |

The second row is this check's **independence proof**. Every position is still
right, so the join resolves, the caller sets are still correct, no page is empty,
no page is lost and the build is still deterministic — five checks pass. The map
is nonetheless titling pages after entities that do not exist under that name.
The test asserts the failing-check list is *exactly* `["FAIL entity-symbol-join"]`,
so the independence claim cannot quietly rot if a later gate makes another check
catch it too.

The fixture (`_make_mixed_repo`) deliberately carries **both** an entity whose
name is not already lowercase (or the rename mutation is silently a no-op) **and**
real cross-module inbound edges (or `inbound-attribution` passes vacuously by
comparing empty caller sets).

An entity that joins to **no** symbol is a failure too: the renderer falls back
to the key, and the page then shows no docstring and no callers from the store
while still looking finished.

### 3.5 `inbound-attribution` (predecessor)

A page's caller set against `checks.StoreScan`, a second reading of the statement
store written from the schema rather than borrowed from `render.load_stores`.
Three facts per page — sites, distinct caller modules, and which modules — all
compared against the **rendered page**, not the renderer's in-memory dict.

| mutation | observed |
|---|---|
| `render.py`: `if p in ("calls", "reads")` → `("calls",)` | exit **1**, `FAIL inbound-attribution`, `inbound sites` |
| `render.py`: `inbound[o][intern(modof(s))]` → `modof(o)` — every caller credited to the callee's own module | exit **1**, `FAIL inbound-attribution`, `as callers` |
| unmutated copy | exit **0** (positive control) |

Both mutations are silent by design: the map still builds, every page still
renders, and the number on the page is still plausible.

### 3.6 `deterministic-rebuild` (predecessor)

Two builds from unchanged source must produce **byte-identical** page trees, in
**separate processes** with `PYTHONHASHSEED` pinned to `0` and `1`.

| | |
|---|---|
| mutation | `render.py`: `ext = sorted({...})` → `list({...})` over the module's import set |
| test | `test_determinism_goes_red_when_the_renderer_orders_pages_by_hash` |
| observed | exit **1**, `FAIL deterministic-rebuild`, diff names `INDEX.md` |
| positive control | `test_determinism_baseline_an_unmutated_package_copy_passes` → **0** |

---

## 4. The determinism-diff evidence

`checks.deterministic_rebuild` is not a boolean. `tree_diff` returns **every path
on which the two trees disagree**, classified three ways — in the first build
only, in the second build only, or same path with differing bytes (reporting
byte lengths when they differ, and `same length, different bytes` when they do
not). `test_determinism_reports_every_differing_path_not_a_boolean` builds two
scratch trees with one file missing on each side and one file differing, and
asserts exactly three diff entries naming `gone.md`, `extra.md` and `moved.md`,
with the identical `same.md` absent.

Two properties carry the weight:

- **Separate processes.** A string hash seed is fixed for a process's life, so
  two builds inside one process share it and a hash-ordered listing looks
  perfectly stable. The seeds are pinned to different values rather than left to
  per-process randomization, so the check exercises the difference on every run
  instead of once in a while.
- **No timings anywhere.** Nothing in any run report carries a timestamp or a
  duration, precisely so this diff can cover the whole tree. Confirmed by the
  `timestamp-on-a-page` attack in §5: adding one makes the check red immediately.

On the real corpus a double build is byte-identical (`deterministic-rebuild`
green among the six on this repo).

---

## 5. The undesigned-attack pass — including four survivors

Eleven attacks, one harness, one green positive control. Harness:
`.agent-work/issue-456/evidence/g1_attack_harness.py`. Full transcript:
`.agent-work/issue-456/evidence/g1-undesigned-attacks.txt`.

```
CONTROL  unmutated copy, undamaged map -> exit 0, failed=none
```

| attack | exit | caught by |
|---|---|---|
| delete a page | 1 | `page-accounting` |
| stray extra page | 1 | `page-accounting` |
| empty a page | 1 | `no-empty-pages`, `page-accounting` |
| drop every module `INDEX.md` | 1 | `page-accounting` |
| flat page tree (entity pages written into `map/`) | 1 | `page-accounting` |
| timestamp on a page | 1 | `deterministic-rebuild` |
| **swap two pages' contents** | **0** | **NOTHING** |
| **rename `helper.md` → `Helper.md`** | **0** | **NOTHING** |
| **reversed caller list** | **0** | **NOTHING** |
| **extractor never records `reads`** | **0** | **NOTHING** |

Three of these are attacks on the predecessor's checks that its author did not
choose: `timestamp-on-a-page` attacks `deterministic-rebuild`, which was designed
against hash order and not against a clock (it caught it); and
`extractor-never-records-reads` and `reversed-caller-list` attack
`inbound-attribution` (it survived both).

### Survivor 1 + 2 — nothing in `g1` ties a page's location to its content

Swapping the **contents** of two entity pages, and renaming a page file while
leaving its title alone, each pass **all six checks with exit 0**. Both produce a
map whose module-index links send a reader to the wrong page or to a 404.

This is structural, not an oversight in one check: every content check in the
gate classifies a page by its **title**, deliberately, so that a page which
landed on another page's path is still read as the entity it describes. That
choice is what makes the checks survive a rename gate — and it is exactly what
makes them blind here.

**Not fixed here, and stated rather than narrowed away.** The assertion that
would catch it — a link resolves, and the target page's title matches the link
text — is a **render-shape** assertion, and `g1` carries none. The natural owner
already exists: `g4`'s close criteria require "a GRAPH WALK that follows links
rather than trusting layout". Filed as **`tc1`** on the plan and routed there.

### Survivor 3 — reversed caller list

`inbound-attribution` compares **sets** of caller modules (`tuple(sorted(...))` on
both sides), so presentation order is not asserted. Deliberate: ordering of
presentation is a render shape and belongs to `gB`.

### Survivor 4 — an extractor that never records an edge

Mutating `extract.py` so `_ref` drops every `reads` statement leaves
`inbound-attribution` **green**. This is the limit `StoreScan`'s docstring
already declares, now **measured** instead of asserted: the second derivation
reads the same store, so it catches the renderer losing, miscounting or
misattributing what the store says, and it does **not** audit the store against
the source. An extractor that never recorded a call agrees with itself and both
derivations are wrong together.

Filed as **`tc3`** (superseding a garbled `tc2` — one word was lost to shell
backtick expansion when it was filed; read `tc3`): **dropping a `sorted()` is not
uniformly a determinism defect.** The designed determinism mutation drops
`sorted()` around a *set* comprehension, which is hash-ordered and correctly
caught. Dropping the `sorted()` around the *caller* list is correctly **not**
caught: the caller map is a `collections.Counter`, so iterating it yields
insertion order, fixed by the statement order in the store and identical under
every hash seed. Consequence for `g5`: a green determinism run is **not** evidence
that the caller split's ordering is stable or sensible.

---

## 6. The RED invariant, and the finding that changed how it ships

### It is red, and it is red for the reason the handoff said

Fresh build of this repository:

```
modules 112   entities 3581   pages 3693   entity_pages 3581
pages - 1 - modules = 3580     entity_pages = 3581
```

`checks.page_accounting` names the loss without recomputing the renderer's
filename expression — it reads the **title** of every page that exists:

```
scripts.run_skill_eval:Verdict: an entity the map claims and does not have
the tree holds 3693 pages; the store accounts for 3694
```

`scripts/run_skill_eval.py:178` declares `class Verdict` and `:407` declares
`def verdict`; their pages resolve to one filename on a case-insensitive
filesystem and the second write destroys the first.

**`g1` does not fix it.** Nothing was renamed. `entity_pages` was not "fixed" by
counting the tree a second time (`tc24`).

### THE FINDING THE PLAN DID NOT ANTICIPATE — a bare `xfail(strict=True)` would have turned the suite RED on Linux

Measured over the whole corpus (every module + entity page path, grouped
case-sensitively and case-insensitively):

```
case-SENSITIVE collisions:   0
case-INSENSITIVE collisions: 1   scripts.run_skill_eval/{Verdict,verdict}.md
```

**The only page collision on this corpus is a case collision.** On a
case-sensitive filesystem the two are separate files, nothing is lost, and the
invariant is **green today**. A bare `xfail(strict=True)` would therefore XPASS on
Linux CI and turn the run red — the exact failure mode the marker exists to
prevent, fired at the wrong gate on the wrong machine.

The marker is therefore **conditional on the property that causes the defect**:

```python
@pytest.mark.xfail(CASE_INSENSITIVE_FS, strict=True, reason=COLLISION_XFAIL_REASON)
def test_every_page_this_repo_claims_is_a_page_this_repo_has(self):
    self.assertEqual(checks.page_accounting(self.m), [])
```

`CASE_INSENSITIVE_FS` is **measured** by writing `CaseProbe.tmp` into a temp
directory and asking whether `caseprobe.tmp` exists — never inferred from
`sys.platform`, because case sensitivity is a property of the filesystem and both
a case-sensitive Windows volume and a case-insensitive Linux one exist.

Strictness is preserved exactly where the defect exists. Where it does not exist,
the assertion simply passes.

### The strict mechanism is verified end to end, not read out of the docs

**Today:**

```
XFAIL tests/test_code_map.py::RealCorpusPageAccountingInvariantTests::
      test_every_page_this_repo_claims_is_a_page_this_repo_has
```

run exits **0**.

**Simulating `g2`'s fix:** renamed `def verdict(` → `def verdict_of(` in
`scripts/run_skill_eval.py`, reran the single test:

```
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/test_code_map.py \
    -k every_page_this_repo_claims -q --color=no -rxX
->  [XPASS(strict)] RED BY DESIGN, owned by gate g2. ...
->  1 failed
EXIT=1
```

Restored with `git checkout -- scripts/run_skill_eval.py`; `git status --porcelain`
then showed only the two files this gate changes.

**A second forcing function fires at the same moment.**
`test_this_repo_declares_two_entities_whose_pages_share_one_filename` asserts the
collision set is *exactly* `{scripts.run_skill_eval:Verdict, :verdict}`, grouping
per **module** (two names collide only if they are in the same module —
`tests.test_map_orient:verdict` is another `verdict` in this repo and collides
with nothing). Under the simulated rename that test also went red. So `g2` cannot
remove the marker without also updating the recorded collision, and cannot update
the collision without confronting the marker.

### Note for `g2`

The handoff calls the fix "the rename". Worth knowing before you pick it up:
the underlying defect is that the renderer derives a filename from an entity
name with no collision handling at all — the synthetic `class INDEX` fixture
collides on **every** platform without any case involved. Renaming `verdict`
closes today's instance; it does not close the class. `page-accounting` will keep
catching the next one either way.

---

## 7. Full suite at the boundary

```
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/ -q --color=no
->  1729 passed, 2 skipped, 1 xfailed, 651 subtests passed in 405.14s
EXIT=0
```

Baseline was `1709 passed, 2 skipped, 0 failed`. **+20 passed, 0 failed.** `xfail`
is not red. The gate commands:

```
... -m pytest tests/test_code_map.py -k 'determinism or invariant' -q --color=no
->  8 passed, 28 deselected, 1 xfailed
... -m pytest tests/test_code_map.py -k 'consistent or join' -q --color=no
->  6 passed, 31 deselected
```

Test names were chosen so those two selectors actually select the new work —
`-k invariant` reaches the accounting tests through
`PageAccountingInvariantTests` / `RealCorpusPageAccountingInvariantTests`.

**Cost added to the suite:** `RealCorpusPageAccountingInvariantTests` builds the
real map once in `setUpClass` (~10s) into a scratch directory, so it needs
nothing to be built beforehand and never touches the committed `map/` tree. This
is the only test in the file that runs against the real corpus.

---

## 8. Things I found that were not asked about

1. **`.code-map/render_report.json` in the worktree was stale on arrival** —
   `pages 3636 / entity_pages 3523` against a `map/` tree of 3635 files, from an
   older build. The handoff's `3648 / 3536` and my `3693 / 3581` are different
   builds again. The invariant is the same in all three (off by exactly one) but
   **no absolute number from a run report should be quoted across sessions** —
   this corpus grows while the run is working on it. That is `gB`'s whole reason
   for existing, confirmed empirically.
2. **`no-empty-pages` and the `page-accounting` coverage arm overlap** on a
   zero-byte page: an empty page has no title, so coverage names the entity too.
   Not a problem, but a reviewer seeing two reds for one defect should know why.
3. **`inbound-attribution` and `entity-symbol-join` are blind to a page's
   absence.** Both iterate `m.entity_pages`, which is pages that exist. Only
   `page-accounting` sees a page that is gone. Measured in §5 row 1.
4. **`checks.py` now makes `check` exit 1 on this repository**, correctly, until
   `g2` lands. It is stated at the top of the module docstring so nobody
   "fixes" it by disabling the check. Any later gate whose command runs
   `python -m scripts.code_map check` on this repo must expect exit 1.
5. The one thing that would most improve this gate's checks is the `tc1` link
   walk. Two of the four survivors collapse the moment a page's location is tied
   to its content.

---

## 9. Files

| path | what |
|---|---|
| `scripts/code_map/checks.py` | rewritten; six checks in a `CHECKS` registry over `MapUnderCheck`; `run()` returns 1 on any failure; a missing tree or store is a failure, not a skip |
| `tests/test_code_map.py` | +20 tests across `RefsLineSelfConsistencyTests`, `EntitySymbolJoinTests`, `PageAccountingInvariantTests`, `RealCorpusPageAccountingInvariantTests`, plus the `_make_mixed_repo` fixture |
| `.agent-work/issue-456/evidence/g1_attack_harness.py` | the undesigned-attack harness (evidence, not part of the suite) |
| `.agent-work/issue-456/evidence/g1-undesigned-attacks.txt` | its transcript |

`git status --porcelain scripts/ tests/` shows exactly `M scripts/code_map/checks.py`
and `M tests/test_code_map.py`. Nothing under `scripts/code_map/` was edited in
place; every mutation ran against a copy. `git add -A` was never used — the
untracked `map/` tree is staged at the final gate.
