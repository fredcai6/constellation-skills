# Implementation Result — gate `g2`, attempt 2

`constellation/issue-456/g2/implementer/attempt-2`, successor to attempt-1.
Resumed the same engine plan and the same lease (`g2-implementer-attempt-1`,
re-claimed idempotently, no takeover). All five plan items driven to `complete`.

**Status: `complete`.** All three defects fixed. Full suite green at the gate
boundary. `python -m scripts.code_map check` exits **0** after a fresh `build`.

## Headline numbers

| | before g2 | after g2 |
|---|---|---|
| full suite | 1729 passed, 2 skipped, **1 xfailed**, 0 failed | **1744 passed, 2 skipped, 0 xfailed, 0 failed** |
| `scripts.code_map check` | exit 1 | **exit 0**, 6/6 checks ok |
| map tree | 3760 pages, 1 lost to a case collision | 3761 pages, **0 case-only folds** |

+15 over baseline: 14 new tests (5 for (a) from attempt-1, 5 for (b), 4 for (c))
plus the strict-xfail becoming a pass. This is the shape the handoff predicted.

## Commits

| commit | what |
|---|---|
| `80702615` | (a) RED — attempt-1, not rewritten |
| `6d5b3131` | (a) GREEN |
| `fd9170f5` | (b) RED |
| `103d03b5` | (b) GREEN |
| `4ea174b3` | (c) RED |
| `cdfd8213` | (c) GREEN + strict-xfail marker deleted |

## Scope

**Files changed:** `scripts/code_map/extract.py`, `scripts/code_map/render.py`,
`scripts/code_map/checks.py`, `tests/test_code_map.py`, the engine plan, and
five evidence files under `.agent-work/issue-456/evidence/`.

`checks.py` is outside the handoff's named allowed scope
(`extract.py`, `render.py`, `tests/test_code_map.py`) and the handoff permits
touching another `code_map` module "only where one of the three fixes genuinely
requires it, and say so." Two fixes required it, both by the design note's
route: (a) strengthens `entity_symbol_join` from a leaf comparison to a
whole-symbol one, which only becomes safe once the store symbol equals the
supplement key; (b) changes what the rendered inbound line SAYS, and `checks.py`
holds the one block that documents itself as the sole place that knows how a
page spells that line.

**Specific exclusions touched:** none. No symbol renamed in
`scripts/run_skill_eval.py` or any non-map source. No g1 check weakened or
deleted — two were strengthened. No line-base or page-header change; no `:<line>`
position reintroduced. `git add -A` never used; every stage was an explicit path
list. `map/` left untracked for the final gate.

**Test mode:** `test-first`. Satisfied for all three — each reproducer was
observed failing and **committed in that state** before its fix.

---

## Defect (a) — D2, the enclosing METHOD is dropped

### Reproducer
Attempt-1's, unchanged, committed failing at `80702615`:
`RealCorpusNestedSymbolIdentityTests` (four collisions pinned **by string**,
asserted against the store, plus the corpus-wide invariant) and
`FunctionNestedSymbolIdentityTests` (synthetic: two closures named `shared` in
two methods of one class, a class `Bundle` defined inside a function, and a
page-content arm).

### RED — exit 1
`python -m pytest tests/test_code_map.py -q --color=no -k NestedSymbolIdentity`

```
9 failed, 2 passed, 38 deselected
SUBFAILED(merged='tests.test_context_determinism:RealCheckoutSkew.project')
SUBFAILED(merged='tests.test_context_manifest:ProducerGuards.explode')
SUBFAILED(merged='tests.test_feedback_tooling:InboxLifecycleTests.f')
SUBFAILED(merged='tests.test_install_constellation:InterpreterProbeTests.fake_run')
```

The sharpest line: the page titled `Holder.first.shared` printed the **second**
closure's docstring. Full text: `.agent-work/issue-456/evidence/g2-red-d2.txt`.

### The fix
`scripts/code_map/extract.py`. Both symbol expressions collapse onto one rule:

```python
def child_sym(self, name):
    base = self.here()
    return base + name if base.endswith(":") else base + "." + name
```

`self.encl` already carries the enclosing scope's own symbol (`"mod:"` at module
level), so module level → `mod:name`, class → `mod:Class.name`, function →
`mod:f.g`, **method → `mod:Class.m.name`**, class-in-function → `mod:f.Name`.

A parallel `self.clsyms` stack is pushed beside `self.clsstack`, so the three
resolvers that spell a class-qualified symbol (`self.x`, `cls.x`, the class-body
name rule) spell the same string a nested class was emitted under. The R2a
member-set lookup is gated on `len(self.clsstack) == 1`, because `build_table`
records module-level classes only and would otherwise read a same-named
module-level class's members for a nested one.

`checks.entity_symbol_join` was then **strengthened** from `leaf == leaf` to
`key == symbol`, and the D2 paragraphs in `render.py`'s module docstring and in
that check's own docstring — both of which asserted in their own words that D2
was unfixed — were rewritten.

### GREEN — exit 0
`5 passed, 38 deselected, 8 subtests passed`.

### Before → after, all four named collisions

| merged symbol emitted before | the two symbols now emitted |
|---|---|
| `tests.test_context_determinism:RealCheckoutSkew.project` | `…RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.project` and `…RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.project` |
| `tests.test_context_manifest:ProducerGuards.explode` | `…ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.explode` and `…ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.explode` |
| `tests.test_feedback_tooling:InboxLifecycleTests.f` | `…InboxLifecycleTests._filer.f` and `…InboxLifecycleTests._recorder.f` |
| `tests.test_install_constellation:InterpreterProbeTests.fake_run` | `…InterpreterProbeTests.test_probe_prefers_py_over_python3_when_both_succeed.fake_run` and `…InterpreterProbeTests.test_probe_timeout_candidate_falls_through_without_hanging.fake_run` |

### The class-in-function arm — 0 occurrences here, stated plainly
Attempt-1 measured this repository by an independent AST walk: **0 nested
classes, 0 classes defined inside a function, 31 closures defined inside a
method.** The class-in-function arm has no real-corpus instance here, so the
synthetic `pkg.nested:outer.Bundle` fixture is the only place it runs anywhere.

### Falsifier grade
**A** — red on this repository's real input, on four named entities.

---

## Defect (b) — the referenced-by count and its list

### Reproducer — `RefsAccountingTests`, committed failing at `fd9170f5`
Fixture: `_make_cross_module_repo`, where `pkg.callee:target` is referenced
twice from its own module and three times from `pkg.far`. Three arms, each with
its input precondition asserted rather than assumed:

1. **reconciliation** — the line must let a reader account for all 5 sites.
2. **the legend** — every inbound line on every page in the tree must be followed
   by a statement of what the count counted.
3. **the contract** — `checks.py` declares that legend independently, and it is
   pinned to `load_stores`' actual predicate test, so widening one without the
   other goes red.

### RED — exit 1
`python -m pytest tests/test_code_map.py -q --color=no -k RefsAccounting`
→ `3 failed, 43 deselected`. Text: `.agent-work/issue-456/evidence/g2-red-refs.txt`.

```
AssertionError: '2 in this module' not found in
'referenced by: 5 sites in 2 modules (pkg.far)' : ... a reader cannot tell how
many of those sites the unnamed module holds

AssertionError: pkg.callee/near.md: the inbound line 'referenced by: none found'
is not followed by a statement of what the count counted ...; got ''
```

### The trap, and the route taken instead
The obvious fix — naming the page's own module in the caller list — destroys two
g1 artifacts: `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor
`    ext = sorted(m for m in callers if m != mod)\n` (which must occur exactly
once in `render.py` or the harness raises), and the input precondition of
`test_refs_lines_are_self_consistent_on_an_intact_map`, which requires *some*
page to count a module it does not name. **Neither was touched.** The list still
holds the other modules only.

### The fix
`render.refs_line` appends `+ N in this module` when the page's own module holds
counted sites, and every inbound line — `none found` included — is followed by
`REFS_LEGEND`:

```
referenced by: 5 sites in 2 modules (pkg.far) + 2 in this module
counted: calls and reads that resolved to this symbol. not counted: its own
definition, imports, inheritance, attribute writes, docstring mentions,
unresolved references.
```

`checks.py`: `REFS_MODULES` gains an optional trailing group; `Refs` gains
`own`; `refs_line_self_consistent` **replaces** "at most one counted module may
go unnamed" with the exact rule in both directions — exactly one unnamed when the
line accounts for own-module sites, exactly none when it does not — plus
`own <= sites`, `sites - own >= len(named)`, and "an inbound line must be
followed by the legend". Every failure mode the check had is still reachable.
`inbound_attribution` now also holds the own-module clause to the store, so it
is not a number nobody checks.

### The g1 tripwires, re-run and still red
`test_self_consistent_line_goes_red_when_a_page_names_its_own_module`,
`test_inbound_goes_red_when_the_renderer_drops_a_predicate` (`DROP_READS_MUTATION`)
and `test_caller_modules_go_red_when_the_renderer_misattributes_the_caller` all
still pass, i.e. all three mutants still die.

### Two NEW mutants, chosen to attack the strengthening itself
Per the run's standing lesson, the strengthened rule was attacked with mutations
its own author did not inherit:

- `OWN_SITES_UNACCOUNTED_MUTATION` — keep counting the own module's sites, stop
  saying so. This is defect (b) exactly, and the **old** rule passed it. The new
  one kills it: `FAIL refs-line-self-consistent … must name every module it counts`.
- `LEGEND_DROPPED_MUTATION` — publish the number, drop the sentence.
  `FAIL refs-line-self-consistent … legend`.

### GREEN — exit 0
`5 passed, 43 deselected`. Text: `.agent-work/issue-456/evidence/g2-green-refs.txt`.

### Falsifier grade
**A** for arms 1 and 2 (red on the real rendered tree). **B** for arm 3, the
legend contract — red by absence, and said so in the test's own docstring.

---

## Defect (c) — the page-filename case collision

### Reproducer — `CaseOnlyPageIdentityTests`, committed failing at `4ea174b3`
A **fresh** case-only pair with nothing to do with `Verdict`: a module declaring
`class Ledger` and `def ledger`. Four arms:

1. input precondition — the fixture really declares two keys that fold to one name;
2. **loss** — `page_accounting` is empty (red on a case-insensitive filesystem);
3. **folding** — no two page filenames in one directory fold to one lowercase
   name (red on a case-**sensitive** filesystem, where nothing is lost and the
   collision is only latent);
4. **links** — every `](…)` the map writes resolves to a file that exists.

Arms 2 and 3 are each red on only ONE kind of filesystem. Together they are red
on every platform, which is the same reasoning that made g1's `xfail` conditional.

### RED — exit 1
`python -m pytest tests/test_code_map.py -q --color=no -k CaseOnlyPageIdentity`
→ `1 failed, 3 passed, 48 deselected`. Text:
`.agent-work/issue-456/evidence/g2-red-case.txt`.

```
AssertionError: ['pkg.book:Ledger: an entity the map claims and does not have',
 'the tree holds 5 pages; the store accounts for 6 (1 top index + 2 module
  indexes + 3 entities)'] != []
```

### The fix
`render.assign_page_filenames(keys)` assigns page filenames per module
directory: keys grouped by their **folded** spelling, and only a group with more
than one member disambiguated, as `<name>~<sha1(name)[:8]>.md`.

- `hashlib`, **never** the builtin `hash()` — `PYTHONHASHSEED` varies per process
  and `deterministic-rebuild` would correctly go red on a seed-dependent filename.
- `~` cannot occur in a Python qualified name, so a disambiguated filename can
  never collide with an undisambiguated one.
- All three places that spell a page filename read the same assignment: `run()`'s
  `emit`, `entity_page`'s child list, and `module_index`'s `walk`. The links move
  with the files, which is what arm 4 exists to hold.

Deliberately **not** fixed: an entity named `INDEX` still lands on its module's
own index page. `_make_collision_repo` is `page_accounting`'s only
cross-platform falsifier, and reserving the stem would make that g1 test unable
to fail — the exact defect this run exists to stamp out. Filed as triage, not
silently swallowed.

### GREEN — exit 0
`4 passed, 48 deselected`, and on the real corpus after a fresh build:

```
pages: 3761
case-only folds: 0
disambiguated: ['Verdict~7f6e5a6e.md', 'verdict~860360ac.md']
```

Exactly two filenames in 3761 changed shape. The fix is general; its footprint is
not.

### The strict-xfail marker is DELETED
It XPASSed the moment the fix landed and turned the run red, exactly as designed:

```
[XPASS(strict)] RED BY DESIGN, owned by gate g2 …
1 failed, 51 passed
```

Deleted with it: `COLLISION_XFAIL_REASON`, `CASE_INSENSITIVE_FS`,
`_filesystem_is_case_insensitive()` and the now-unused `import pytest` — all four
existed only to gate that marker. The assertion itself survives, unconditional,
and the precondition test that pins this repository's case-only pair survives
with a docstring that no longer describes a marker that is gone.

### Falsifier grade
**A** for the loss arm (red on a synthetic pair on this filesystem today).
**B** for the links arm, stated in place.

### Commander ruling on (c) — NOT falsified
The ruling is to fix the map's page naming, not to rename `class Verdict` /
`def verdict` in `scripts/run_skill_eval.py`. The general fix resolves any
case-only pair without touching a production symbol, so nothing measured gives a
reason to overrule. **No overrule.**

---

## Evidence

Cleared environment throughout (`unset FORCE_COLOR PYTHONIOENCODING`), `python`
never `py`.

```bash
python -m pytest tests/ -q --color=no
```
**exit 0 — `1744 passed, 2 skipped, 659 subtests passed`.** No xfail, no failure.
Text: `.agent-work/issue-456/evidence/g2-final-suite.txt`.

```bash
python -m scripts.code_map build   # FIRST -- check reads a stale <root>/map
python -m scripts.code_map check
```
**exit 0** — `ok no-empty-pages · ok page-accounting · ok
refs-line-self-consistent · ok entity-symbol-join · ok inbound-attribution · ok
deterministic-rebuild · passed 6 checks`. Text:
`.agent-work/issue-456/evidence/g2-check-after.txt`.

`git status`: no stray edit. `git diff HEAD -- scripts/ tests/` is empty. The
only untracked paths are `map/` (staged at `gs` by design),
`.agent-work/g1-implement/` and `.agent-work/g2-implement/` (both untracked
before this attempt started), and this attempt's final suite log.

### TDD evidence
- Failing test observed and **committed failing**: (a) `80702615`, (b) `fd9170f5`,
  (c) `4ea174b3`.
- Passing test observed: (a) `6d5b3131`, (b) `103d03b5`, (c) `cdfd8213`.
- Refactor while green: none needed.

## Docs/contracts touched
Three docstrings that asserted a defect which is now fixed were rewritten:
`render.py`'s module-level `D2` paragraph, `checks.entity_symbol_join`'s "Leaf
name, not the whole symbol" paragraph, and `checks.refs_line_self_consistent`'s
"at most ONE counted module may go unnamed" rule statement. A docstring that
describes a defect you just fixed is a lie in the codebase.

## Assumptions
- The four collisions live in the STORE's symbol space, and only three are
  two-page merges. Asserted against the store, per the successor handoff's first
  correction. Confirmed: the store arm passes and the page arm was never claimed.

## Stop conditions hit
None. No blocker, no waiver, no context seam.

## Out-of-scope observations (triage candidates, filed on the plan as tc1–tc3)
1. **`supplement.walk` descends `node.body` only**, so any definition inside a
   compound statement (`with`, `if`, `try`, `for`) gets no page at all. Measured:
   one of the four D2 collision members, at `tests/test_context_manifest.py:771`,
   sits inside a `with` block and is invisible to the supplement while
   `extract.py` (which uses `generic_visit`) sees it. The two AST passes disagree
   about what the corpus contains, and `entity_symbol_join` cannot see it because
   it iterates supplement keys.
2. **The `INDEX` page-filename family** — an entity named `INDEX` still overwrites
   its module index. Fixing it requires g1's `page-accounting` falsifier to be
   rebuilt on a different collision first.
3. **`class_member` still keys on the bare class name.** `resolve_attr`'s
   `self.x` / `cls.x` branches call `class_member(self.clsstack[-1], attr)`, which
   walks `build_table`'s module-level class records, so for a nested class that
   lookup can read a same-named module-level class's member set. Zero occurrences
   in this corpus and the fallback beneath it is now correct via `clsyms`, so this
   is latent, not live. The same `len(clsstack) == 1` gate that R2a now carries
   would close it.

## Map Impact
- **Structural anchors touched:** `scripts/code_map/extract.py` name resolution
  (`child_sym`, `clsyms`), `scripts/code_map/render.py` page naming
  (`assign_page_filenames`, `page_file`) and inbound-line rendering
  (`refs_line`, `REFS_LEGEND`), `scripts/code_map/checks.py` rendered-line
  grammar and two check bodies.
- **Capabilities affected:** derive structure from source; answer cross-file
  questions cheaply. All three are the same capability getting *trustworthy*
  rather than merely present.
- **Decisions settled (were candidates, now measured):**
  - *Symbol identity for function-nested definitions* — the enclosing METHOD
    appears, and a definition's store symbol EQUALS `supplement.py`'s qualified
    key by construction. The (file, line) join is now a redundancy check between
    two agreeing passes rather than a translation between two spellings. Durable;
    every consumer inherits it. `@grade: measured — supplement-key/store-symbol
    mismatches were 25, are now 0, which is what makes the whole-symbol
    comparison in entity_symbol_join safe.`
  - *Referenced-by semantics* — the count includes the page's own module and the
    line now says how many; the list stays the OTHER modules; the page states in
    its own words what was counted (`calls`, `reads` that resolved to this
    symbol) and what was not. `@grade: measured`
  - *Page identity* — a page's filename is assigned per module directory, not
    derived from the entity name alone. `@grade: measured`
- **Constraint reinforced:** checks must be able to fail. Two g1 checks were
  strengthened and both were re-attacked with mutations chosen for the new rule,
  not inherited from their authors. The `INDEX` collision was left in place
  precisely so a falsifier keeps its ability to fail.
- **Claims/evidence produced:** 3619 distinct definition symbols, 4 emitted at two
  sites before / 0 after. Real map: 3761 pages, 0 case-only folds, 2
  disambiguated filenames. `check` 6/6 ok.
- **Trust limitations:** the supplement still does not see definitions inside
  compound statements, so any check iterating supplement keys is blind to them
  (tc1).

## Workflow Feedback
- **The successor handoff's tripwire section paid for itself immediately.** The
  three named traps — (b)'s two g1 artifacts, (c)'s `INDEX` falsifier, and the
  stale `<root>/map` — were the three places this attempt would otherwise have
  spent its time. Nothing was rediscovered. That section should be a standing
  field in any handoff that hands a defect to a crew that must not break the
  checks guarding it.
- **`env -u` vs `unset` confirmed again.** The Bash tool refuses
  `env -u FORCE_COLOR -u PYTHONIOENCODING python …` in a worktree-isolated
  session. `unset FORCE_COLOR PYTHONIOENCODING && python …` works. The engine's
  own POSIX-shell command checks still use the `env -u` form and ran fine — this
  bites only an agent running the command by hand. **Note the plan's `m3` and
  `m4` command checks are joined with ` && ` and the engine executed them
  without complaint**, so the `tc29` repair holds.
- **A second Bash-tool refusal, not previously recorded:** any command combining a
  pipe with a `PIPESTATUS`/`$?` echo, or several `python` invocations joined with
  `;`, is refused as "too complex to verify". Exit codes had to be captured by
  redirecting to a file and echoing `$?` on the next line. Worth naming in the
  next handoff — it changes how you capture an exit code, which is the one thing
  every evidence line needs.
- **Plan drift, harmless but worth flagging:** `m4-close`'s imperative names
  `g2-implement-RESULT.md` as the output path, but the dispatch specifies
  `g2-implement-RESULT-2.md`. Wrote to the latter; attempt-1's result is left
  intact at the former, which is what a successor run wants.
- **What would have made this easier:** nothing beyond what the successor handoff
  already carried. The design note was executable as written; the only judgement
  calls left were how to grade each arm and whether to add the two mutation tests
  and the `own`-vs-store check in `inbound_attribution`, all of which are
  strengthenings the exclusions explicitly allow.

## Return status
`complete`.
