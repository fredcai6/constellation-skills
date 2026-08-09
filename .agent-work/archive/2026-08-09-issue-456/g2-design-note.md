# g2 implementer — design note, written at the context seam

Attempt 1 (`constellation/issue-456/g2/implementer/attempt-1`) hit the engine's
HARD context trip at the `advance m0-context` boundary (gauge 17.9% of a 1M
window = 178K tokens, hard cap 150K). It parked here rather than pushing
through. **Everything below is measured, not proposed.** A fresh implementer
should be able to execute from this note plus the handoff without re-deriving
anything.

Plan file: `.agent-work/issue-456/g2-implementer-plan.json`
(items `m0-context`, `m1-d2-symbol-identity`, `m2-refs-accounting`,
`m3-page-identity`, `m4-close`). `m0-context` is `in-progress` with `c1`
attested; the refresh-request is attached to it.

## State at the seam

- **Baseline, measured before any edit** (`python -m pytest tests/ -q --color=no`,
  `FORCE_COLOR`/`PYTHONIOENCODING` unset): exit 0,
  `1729 passed, 2 skipped, 1 xfailed, 651 subtests passed`. Matches the handoff.
  Saved at `.agent-work/issue-456/evidence/g2-baseline-suite.txt`.
- **Committed RED for defect (a)**: `tests/test_code_map.py` carries the
  reproducer and it fails. Output at
  `.agent-work/issue-456/evidence/g2-red-d2.txt`, exit 1, `9 failed, 2 passed`.
  Falsifier grade **A** — it reproduces on this repository's real input today.
- Nothing in `scripts/` has been touched. `git status` is otherwise as it was.

## Measurements (this repository, at the g2 revision)

Corpus shape, by an independent AST walk:

| shape | count |
|---|---|
| nested classes (class inside a class) | 0 |
| classes defined inside a function | 0 |
| closures defined inside a method | 31 |

Statement store, `contains` statements only: **3619 distinct symbols, exactly 4
emitted at more than one definition site** — the same four named in
`reference/d2_collisions.txt`, and no others. So "no definition symbol is
emitted at two positions" is a clean corpus-wide invariant: 4 today, 0 after the
fix, with no redefinition noise to explain away.

Supplement keys vs store symbols: 3614 entities, **0 join misses, 25
mismatches** — the 31 closures-in-methods minus those whose enclosing method the
supplement never recorded. After the fix this should be **0 mismatches**, which
is what makes the `entity_symbol_join` strengthening below safe.

**One nuance the reference file does not state.** The four collisions live in
the STORE's symbol space. Only three of them are two-page merges, because
`supplement.walk` descends `node.body` only: the second
`ProducerGuards...explode` (tests/test_context_manifest.py:771) sits inside a
`with` block, so the supplement never records it and it has no page. That is a
separate, pre-existing gap — logged as a triage candidate below, NOT fixed here.

## Defect (a) — the fix

`scripts/code_map/extract.py`. Both symbol expressions (`visit_ClassDef` ~500,
`_func` ~524) collapse to one rule: **the enclosing scope's symbol plus this
name**. `self.encl` already carries exactly that stack (`["mod:"]` at module
level, the enclosing definition's own symbol otherwise), so:

```python
def child_sym(self, name):
    base = self.here()
    return base + name if base.endswith(":") else base + "." + name
```

- module level -> `mod:name`
- in a class -> `mod:Class.name`
- in a function -> `mod:f.g`
- **in a method -> `mod:Class.m.name`  <- the fix**
- class in a function -> `mod:f.Name`  <- the second arm

The result equals `supplement.py`'s qualified key by construction.

Then add a parallel stack of enclosing CLASS SYMBOLS so the resolvers spell the
same string (0 instances in this repo, but the fix must be general, not
corpus-shaped):

- `self.clsyms` pushed/popped beside `self.clsstack` in `visit_ClassDef`.
- `resolve_attr`, the `self.x` and `cls.x` branches: the fallback
  `"%s:%s.%s" % (self.mod, self.clsstack[-1], attr)` becomes
  `"%s.%s" % (self.clsyms[-1], attr)`.
- `resolve_name` R2a: same substitution, and gate the
  `self.table.classes.get(self.clsstack[-1], ())` lookup on
  `len(self.clsstack) == 1` — `build_table` only records MODULE-LEVEL classes,
  so for a nested class that lookup silently reads a same-named module-level
  class's member set.

Also update the `D2` paragraph in `render.py`'s module docstring and the
`Leaf name, not the whole symbol` paragraph in `checks.entity_symbol_join` —
both assert in their own words that D2 is unfixed.

**Then strengthen `entity_symbol_join` to compare the WHOLE symbol, not the
leaf.** That is the shipped check that would catch a D2 regression on this
repository, and the 0-mismatch measurement above says it is safe. Verified
against the two mutations that guard it: `SUPPLEMENT_RENAME_MUTATION`
(lowercases every qual) and `JOIN_SHIFT_MUTATION` (line+1) both still go red.

## Defect (b) — the fix, and the trap in it

`render.refs_line`. Today: both totals count the page's own module, the
parenthesized list names the other modules only, and nothing says what the count
counted.

**THE TRAP — do not "fix" this by naming the own module in the list.** Two g1
artifacts forbid it, and both are load-bearing:

- `OWN_MODULE_NAMED_MUTATION` (tests/test_code_map.py) anchors the literal line
  `    ext = sorted(m for m in callers if m != mod)\n` and requires it to occur
  **exactly once** in `render.py`. Changing that line raises `HarnessError` and
  destroys g1's falsifier.
- `test_refs_lines_are_self_consistent_on_an_intact_map` asserts as an input
  precondition that some rendered page **counts a module it does not name**.
  Naming every module makes that precondition false.

So: keep the list as the other modules, and **account for the own module's
sites explicitly** so nothing is silently omitted:

```
referenced by: 5 sites in 2 modules (pkg.far) + 2 in this module
counted: calls and reads that resolved to this symbol. not counted: its own
definition, imports, inheritance, attribute writes, docstring mentions,
unresolved references.
```

- the `+ N in this module` clause is emitted only when `callers[mod]` is
  non-zero; the existing `N sites, this module only` form already accounts for
  itself and stays.
- the legend is a `REFS_LEGEND` constant in `render.py`, appended after every
  inbound line including `none found`.
- **the legend's wording is coupled to `if p in ("calls", "reads"):` in
  `load_stores`** — which is `DROP_READS_MUTATION`'s anchor and must ALSO survive
  byte-exact. Do not refactor that predicate test into a named tuple.

Then `checks.py`, in the block that documents itself as the one place that knows
how a page spells its inbound references:

- `REFS_MODULES` gains an optional trailing group:
  `r"^(\d+) sites in (\d+) modules \(([^)]*)\)(?: \+ (\d+) in this module)?$"`.
- `Refs` gains a field (`own`); `parse_refs` fills it — `N` for the self-only
  form, the captured group for the modules form, 0 otherwise.
- `refs_line_self_consistent` REPLACES "at most one counted module may go
  unnamed" with the strictly stronger pair: the gap must be **exactly 1 when the
  line accounts for own-module sites and exactly 0 otherwise**; plus
  `own <= sites` and `sites - own >= len(named)`. Every failure mode it has today
  is still reachable (gap < 0 and gap > 1 both still fail), and the
  "names its own module" rule stays untouched.
- add one failure mode: an inbound line must be immediately followed by the
  legend. Declare the legend text independently in `checks.py`, the same
  contract `REFS_PREFIX` already has.
- `inbound_attribution` needs no change — it already subtracts the own module
  from `expected_named`.

Check `OWN_MODULE_NAMED_MUTATION` still goes red afterwards: the mutant names
its own module, so `gap` becomes 0 while `own` is 2 — red on the new rule AND on
the untouched own-module rule, and the string `its own module` still appears.

## Defect (c) — the fix

`render.py:414`. Assign page filenames per module directory, deterministically:

```python
def assign_page_filenames(keys):
    groups = collections.defaultdict(list)
    for key in keys:
        groups[key.split(":", 1)[1].lower()].append(key)
    out = {}
    for group in groups.values():
        for key in group:
            name = key.split(":", 1)[1]
            out[key] = (f"{name}~{_case_tag(name)}.md" if len(group) > 1
                        else f"{name}.md")
    return out
```

with `_case_tag(name) = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]`.
**`hashlib`, never the builtin `hash()`** — `PYTHONHASHSEED` varies per process
and `deterministic-rebuild` would catch it. `~` is safe: it cannot occur in a
Python qualified name, so a disambiguated filename can never collide with an
undisambiguated one.

Fill a module-level `page_file` dict in `load_stores` (per module, from
`members_of`), and read it in all three places that spell a page filename:
`run()`'s `emit`, the children list in `entity_page`, and `walk` in
`module_index`.

**Deliberately NOT fixed: the `INDEX` family.** An entity named `INDEX` still
lands on its module's own index page. That collision is `_make_collision_repo`,
which is g1's falsifier for `page-accounting` on every platform — reserving the
stem would make that g1 test unable to fail. This repository declares no such
entity, so `check` still reaches 0. Logged as a triage candidate.

Synthetic proof of generality: a module declaring `class Ledger` and
`def ledger` — a fresh case-only pair unrelated to `Verdict`. Assert BOTH arms,
because each is red on only one kind of filesystem:

- every entity key is the title of some page (red on a case-insensitive FS
  before the fix — one page is destroyed);
- no two page filenames in the module directory fold to one lowercase name (red
  on a case-sensitive FS before the fix — two files, one folded name).

Together they are red on every platform. Add an input precondition asserting the
fixture really declares two keys that fold to one name.

Then **delete** the `@pytest.mark.xfail(CASE_INSENSITIVE_FS, strict=True, ...)`
marker and the `COLLISION_XFAIL_REASON` text it cites. `strict` forces this: the
test XPASSes the moment the fix lands and the run goes red until the marker is
gone.

`check` reads the tree at `<root>/map`, which is stale — **run `build` before
`check`** or the exit code means nothing.

## Commander ruling: not falsified

The ruling is to fix the map's page naming, not to rename `class Verdict` /
`def verdict` in `scripts/run_skill_eval.py`. Nothing measured here contradicts
it, and the general fix above resolves any case-only pair without touching a
production symbol. No overrule.

## Triage candidates found (out of scope, do not fix here)

1. **`supplement.walk` descends `node.body` only**, so any definition inside a
   compound statement (`with`, `if`, `try`, `for`) gets no page — measured: one
   of the four D2 collision members, at tests/test_context_manifest.py:771.
   `extract.py` sees them (it uses `generic_visit`), so the two passes disagree
   about what the corpus contains.
2. **The `INDEX` filename family** (above) — an entity named `INDEX` still
   overwrites its module index. Fixing it requires g1's `page-accounting`
   falsifier to be rebuilt on a different collision first.
