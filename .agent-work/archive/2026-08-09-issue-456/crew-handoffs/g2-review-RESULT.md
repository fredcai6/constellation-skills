VERDICT: APPROVE

# Review Result — gate `g2`: symbol identity and page identity

`constellation/issue-456/g2/reviewer/attempt-1`. Survey driven end to end through
the engine at `.agent-work/issue-456/g2-review/review.json`, lease
`g2-reviewer-attempt-1`, all seven checks recorded, consolidated to APPROVE.

**Every claimed number reproduced. Every named exclusion held. The
`entity_symbol_join` cannot-fail risk is real in principle and absent in fact — I
broke the other derivation and the check went red with 25 failures on the real
repository.**

My mutation harness is written independently of `tests/test_code_map.py`
(`.agent-work/issue-456/g2-review/attack.py`) so a defect in the implementer's
harness could not hide inside mine. Every mutation below is one neither
implementer chose.

---

## 1. The highest-risk item: is `entity_symbol_join` now a check that cannot fail?

**No. It can fail, and the strengthening is what makes it fail.** Three
independent results, all by running.

The premise of the risk is right: the fix makes the store symbol equal the
supplement key by construction, and the check was strengthened from `leaf ==
leaf` to `key == symbol`. If both sides came from one code path the check would
be a tautology. **They do not.** `key` is produced by `supplement.walk`'s own
`prefix` recursion; `symbol` is produced by `extract.Extractor.child_sym` walking
`self.encl`. Different modules, no shared helper, joined only on `(file, line)`.
Reading that is not proof, so I broke each side in turn.

### (i) Break the STORE side — the side the implementer's own mutants never touch

Every join mutant in the suite (`JOIN_SHIFT_MUTATION`,
`SUPPLEMENT_RENAME_MUTATION`) attacks `supplement.py`. I restored the exact D2
defect inside `extract.child_sym` and left `supplement.py` alone:

```python
# mutation applied to a throwaway copy of scripts/code_map
        base = self.here()
+       if self.clsstack:
+           return "%s:%s.%s" % (self.mod, self.clsstack[-1], name)
        return base + name if base.endswith(":") else base + "." + name
```

**On my synthetic nested fixture** — `python -m scripts.code_map check`, exit
**1**:

```
FAIL entity-symbol-join: 3
   pkg.nested/Holder.first.shared.md: page is titled pkg.nested:Holder.first.shared
     but the store symbol at that position is pkg.nested:Holder.shared
   pkg.nested/Holder.second.shared.md: ... but the store symbol ... is pkg.nested:Holder.shared
   pkg.nested/outer.Bundle.method.md: ... but the store symbol ... is pkg.nested:Bundle.method
FAILED 1 of 6 checks: entity-symbol-join
```

**On the REAL repository** — same mutation, built and checked against
`--root <worktree>` into a scratch `--artifacts`/`--out` so the worktree's own
`map/` was never touched. Build exit 0, check exit **1**:

```
FAIL entity-symbol-join: 25
   tests.test_agent_work_root/DurableRootFallbackTests.test_git_rev_parse_failure_falls_back.boom.md:
     page is titled ...test_git_rev_parse_failure_falls_back.boom but the store symbol
     at that position is tests.test_agent_work_root:DurableRootFallbackTests.boom
   ... 24 more, including all four of the named D2 collisions
FAILED 1 of 6 checks: entity-symbol-join
```

**25 is the number.** The design note measured 25 store/supplement mismatches
before the fix and 0 after. Restoring the defect produces exactly 25 again. The
check is a corpus-scale falsifier, not a tautology.

### (ii) Prove the STRENGTHENING is what caught it

Same mutation, plus `checks.py`'s old leaf comparison restored:

```python
-       if key != symbol:
+       if key.rsplit(".", 1)[-1] != symbol.rsplit(".", 1)[-1]:
```

Exit **0**, `passed 6 checks`. The old rule is blind to the regression the new
one kills. The strengthening bought a real falsifier; it did not launder one.

### (iii) Break the SUPPLEMENT side with a mutation nobody designed

Not the implementer's lowercase rename — a chain truncation
(`qual = child.name`, dropping the prefix). Exit **1**, `FAIL
entity-symbol-join: 5`.

**Verdict on the cannot-fail risk: cleared, with evidence on the real corpus.**

---

## 2. Defect (b) — both arms of the strengthened rule, and neither is vacuous

The rule is now "the counted modules you do not name must be exactly one when the
line accounts for own-module sites, exactly none when it does not."

| mutation (mine) | arm hit | result |
|---|---|---|
| `{len(callers)}` → `{len(callers) + 1}` on a page with own-module sites | exactly-one, high side | exit 1 — `attributes 2 sites to its own module, so exactly one counted module -- its own -- must go unnamed, but 2 of 3 are` |
| `{len(callers)}` → `{len(callers) - 1}`, same page | exactly-one, low side | exit 1 — `... but 0 of 1 are` |
| `", ".join(ext)` → `", ".join(ext[1:])` on pages with no own-module sites | exactly-zero | exit 1 — `a line that attributes no sites to its own module must name every module it counts` |

`inbound_attribution` caught all three as well, from the store side.

**Non-vacuity, measured on the real 3761-page tree:** 12 pages carry the
`... modules (...) + N in this module` form (the exactly-one arm) and 7 carry the
modules form with no own clause (the exactly-zero arm). Plus 1271 self-only and
2358 `none found`. Neither arm is empty on this corpus.

**Strengthened, not weakened — proven by running, not reading.** My
drop-a-named-module mutant is **GREEN** on `refs-line-self-consistent` under g1's
old "at most one unnamed" rule (I restored it verbatim in a copy) and **RED**
under g2's. In the other direction, g1's own failure mode `gap > 1` is still
caught by both rules. Nothing the old rule caught is now uncaught: zero
`failures.append` lines were deleted from `checks.py`, all six checks are still in
the `CHECKS` registry, and all 12 g1 mutant tests pass.

A real line and its legend, from the built map:

```
referenced by: 2 sites in 2 modules (tests.test_code_map) + 1 in this module
counted: calls and reads that resolved to this symbol. not counted: its own
definition, imports, inheritance, attribute writes, docstring mentions,
unresolved references.
```

---

## 3. Defect (c) — general, not a special case for `Verdict`

I built my **own** case-only family in a shape the implementer never used: a pair
nested inside a class, so the qualified names are dotted (`Box.Item` /
`Box.item`), plus a **three-way** module-level fold group (`Thing` / `thing` /
`THING`). Nothing named Verdict anywhere.

```
pkg.casey/Box.Item.use.md        # pkg.casey:Box.Item.use     <- NOT disambiguated: its fold is unique
pkg.casey/Box.item~31748ca0.md   # pkg.casey:Box.item
pkg.casey/Box.Item~c462fac2.md   # pkg.casey:Box.Item
pkg.casey/Box.md                 # pkg.casey:Box
pkg.casey/THING~472f09c6.md      # pkg.casey:THING
pkg.casey/thing~863cc374.md      # pkg.casey:thing
pkg.casey/Thing~e0681542.md      # pkg.casey:Thing
broken links: []
check: exit 0, passed 6 checks
```

Dotted names, three-way groups, and minimality (only the colliding group moves)
all hold. The fix is general.

**`hashlib`, not `hash()` — and the guard has no hole.** `render._case_tag` is
`hashlib.sha1(...)[:8]`; the builtin `hash()` appears nowhere in `render.py`. I
swapped it for `"%08x" % (hash(name) & 0xFFFFFFFF)` and
`deterministic-rebuild` caught it immediately: exit 1, 12 failures, five
filenames "in the first build only" and five different ones "in the second build
only". A seed-dependent filename is detected.

---

## 4. The two things that must NOT have been fixed

- **`_make_collision_repo`'s `INDEX` collision STILL collides.** My own `class
  INDEX` fixture, unmutated shipped package: exit **1**, `FAIL page-accounting:
  2` — `pkg.thing: a module index the map claims and does not have` / `the tree
  holds 5 pages; the store accounts for 6`. `assign_page_filenames` does not
  reserve the `INDEX` stem. g1's only cross-platform falsifier for
  `page-accounting` retains its ability to fail. **Not a BLOCK.**
- **No production symbol renamed.** `git diff dc1199b4..HEAD --
  scripts/run_skill_eval.py` is empty. `class Verdict` (line 178) and `def
  verdict` (line 407) are both present and untouched. The Commander ruling was
  complied with. **Not a BLOCK.**

---

## 5. RED commits — each one re-run at its own commit

Each commit was exported with `git archive` into a throwaway directory and
re-inited as its own git repo, so `git ls-files` sees exactly that commit's
tracked set. The worktree was never checked out, stashed or otherwise disturbed.

| commit | selector | exit | observed |
|---|---|---|---|
| `80702615` (a) | `-k NestedSymbolIdentity` | **1** | `9 failed, 2 passed, 38 deselected`; all four D2 collisions `SUBFAILED` **by name** |
| `fd9170f5` (b) | `-k RefsAccounting` | **1** | `3 failed, 43 deselected` |
| `4ea174b3` (c) | `-k CaseOnlyPageIdentity` | **1** | `1 failed, 3 passed, 48 deselected`; `pkg.book:Ledger: an entity the map claims and does not have` |

All three reproducers were genuinely committed failing. One arm of (b) fails with
`AttributeError: module 'scripts.code_map.checks' has no attribute
'REFS_LEGEND'` — red by absence, which the implementer graded **B** and said so
in the test's own docstring. Honest.

---

## 6. Numbers

| claim | mine | agree |
|---|---|---|
| full suite | `1744 passed, 2 skipped, 659 subtests passed`, exit 0, **0 failed, 0 xfailed** | ✅ |
| `check` after fresh `build` | exit **0**, `passed 6 checks` (all six `ok`) | ✅ |
| map tree | **3761** pages | ✅ |
| case-only folds | **0** in any directory | ✅ |
| disambiguated filenames | exactly two: `Verdict~7f6e5a6e.md`, `verdict~860360ac.md` | ✅ |

Test accounting reconciles: 10 new tests inside `dc1199b4..HEAD`, plus the 5 for
(a) that landed at `80702615` (which is **before** the review diff base), plus
the strict-xfail becoming a pass = **+15**, i.e. 1729 → 1744.

The strict-xfail marker is gone, along with `COLLISION_XFAIL_REASON`,
`CASE_INSENSITIVE_FS`, `_filesystem_is_case_insensitive()` and `import pytest`.
The assertion survives, unconditional. One test *appears* deleted by name; it is a
rename with the body intact
(`..._whose_pages_share_one_filename` → `..._whose_names_differ_only_by_case`).
No g1 test was deleted.

Page headers carry `<kind>, <path>, N lines` — **no `:<line>` position**
anywhere. The single `map/*.md` hit for `.py:NNN` is inside a rendered source
docstring, not a header field. `map/` is still untracked.

---

## 7. Scope

`checks.py` was touched beyond the named allowed scope. **The justification
holds.** For (b) it is strictly required: adding `+ N in this module` to the
rendered line makes `checks.REFS_MODULES` fail to parse, and the check would go
red for the wrong reason. For (a) it is required in the weaker but real sense
that the old check's docstring asserted D2 was unfixed and its leaf comparison
was blind to a D2 regression — which I proved by running it (§1.ii). The extra
`inbound_attribution` own-module clause is a strengthening the exclusions allow.

No other production file touched. `supplement.walk`'s compound-statement
blindness untouched. No line-base or page-header change. `git status` shows zero
modified tracked files; the only untracked paths are `map/`, the two pre-existing
`.agent-work/g*-implement/` dirs, and this review's own workbench.

---

## 8. Refactoring pass (Fowler)

Record: `.agent-work/issue-456/g2-review/fowler-pass.json`, rail exit 0. 12/12
smells judged — 1 flagged, 4 overridden with logged standards, 7 absent.

**Flagged (observation, not a blocker):** in `refs_line_self_consistent` the
local `own` means *the page's own module name* while `stated.own` three lines
later means *the count of sites attributed to that module*. One word, two
meanings, one function. Rename the local to `own_module`. Filed as `tc1`.

**Overridden, each with the standard that wins:** long-method on
`refs_line_self_consistent` (its eight branches must stay individually reachable
and individually named in `check` output — that is what the gate's mutants select
on); duplicated-code on the byte-identical `REFS_LEGEND` in `render.py` and
`checks.py` (importing it would make the legend assertion compare the renderer's
string to itself and never fail); primitive-obsession on stringly-typed symbols
(a shared `Symbol` type would have to live in a module both AST passes import,
and that shared path is exactly what would make `entity_symbol_join` unable to
fail); speculative-generality on `clsyms` and N-way fold groups (a corpus-shaped
fix is the hand-maintained list CREW_CONTEXT forbids, and I demonstrated the
generality with my own fixture rather than taking it on faith).

**Two smells the diff removes:** shotgun-surgery — three sites that each spelled
a page filename now read one `page_file` index; and message-chains — the join's
double `split`/`rsplit` is gone.

---

## 9. Out-of-scope candidates

Mine:

- **tc1** — rename `own` → `own_module` in `checks.refs_line_self_consistent`.
  Cosmetic, no behaviour change.
- **tc2** — `refs_lines` and `refs_line_self_consistent` identify a page's inbound
  line by the literal prefix `referenced by: `, so a rendered source docstring
  beginning with that exact string would be parsed as an inbound line and fail
  the new legend rule. Pre-existing shape, not introduced by g2, no such
  docstring in the corpus today. Worth a fixture at a later gate.

The implementer's three (tc1–tc3 on its own plan) are correctly routed and none
is mine to fix. I confirmed the mechanism of the first by reading
`supplement.walk`: it descends `node.body` only, so a definition inside
`with`/`if`/`try`/`for` gets no page, and any check iterating supplement keys is
blind to it. That is the one stated trust limitation of this gate and it is
recorded honestly in the implementer's Map Impact.

---

## 10. Blockers

**None.**

---

## Workflow Feedback

- **The handoff's "attack it first and directly" instruction is the reason this
  review has evidence rather than an opinion.** Naming the specific hypothesis —
  *both sides may now be one code path* — converted an open-ended audit into one
  falsifiable experiment. That framing should be a standing field in any review
  handoff for a "two things must agree" fix. The generalization worth keeping:
  **when a check compares two derivations, the reviewer must break the derivation
  the implementer's own mutants do not touch.** Every join mutant in this suite
  attacks `supplement.py`; the whole risk lived on the `extract.py` side, and
  nothing in the shipped test suite attacks it.
- **`--artifacts` / `--out` make the real-corpus attack safe, and no handoff
  mentions them.** The handoff's warning is only that `check` reads a stale
  `<root>/map`. But mutating the package and building against the real repo would
  have overwritten the untracked 3761-page `map/` tree that `gs` stages, with a
  *mutated* map. `build --root <repo> --artifacts <tmp>/a --out <tmp>/m` keeps the
  worktree pristine. Worth naming in every later gate's handoff.
- **`git archive` is the clean way to verify a RED commit.** Exporting the commit
  into a temp dir and `git init`-ing it lets `discover_corpus` (which shells out
  to `git ls-files`) see exactly that commit's tracked set, with no checkout, no
  stash, and no second worktree. Recommend it as the standing recipe for
  "check each RED commit actually fails at that commit".
- **The Fowler rail's postcondition placeholder is still broken, third reviewer
  in a row.** `REVIEW_SURVEY.template.json` ships `r6-fowler.c1` with a literal
  `<fowler-pass-record-path>`, and no engine verb can replace it on a **survey**
  controller: `amend` is refused (`amend applies to gated checklists`) and
  `attest` is refused for an engine-checked condition. The only route is a
  `waive --force` that is not a risk acceptance at all — the rail was run and
  passed. Same forced waiver appears at `.agent-work/issue-456/g0-review/` and
  `g1-review/`. Fix: let `record` substitute a `--fowler-record` argument into
  the command, or allow `amend` on surveys.
- **The Bash tool eats backticks inside `--finding` strings.** Three words were
  silently dropped from the `r6-fowler` finding the engine journaled (the full
  text is intact in `fowler-pass.json` and above). Findings with inline code
  should be passed via a file, not an argument.
