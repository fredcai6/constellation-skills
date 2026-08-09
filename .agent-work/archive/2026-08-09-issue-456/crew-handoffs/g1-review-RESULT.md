VERDICT: APPROVE

# REVIEW_RESULT — gate `g1`: invariants that cannot move

Issue #456. Registry slot `constellation/issue-456/g1/reviewer/attempt-1`.
Survey driven end to end at `.agent-work/issue-456/g1-review/review.json`
(7 items, all visited, consolidated `APPROVE`, 0 open findings).

Evidence written this run:

| path | what |
|---|---|
| `.agent-work/issue-456/evidence/g1-reviewer-attacks.py` | my attack harness, independent of the implementer's |
| `.agent-work/issue-456/evidence/g1-reviewer-attacks.txt` | its transcript |
| `.agent-work/issue-456/evidence/g1-reviewer-realcorpus.py` / `.txt` | scratch build + `check` against this repository |
| `.agent-work/issue-456/evidence/g1-reviewer-fullsuite.txt` | the full suite |
| `.agent-work/issue-456/g1-review/fowler-pass.json` | the required refactoring pass |

---

## 1. The headline: the suite number is exactly what was expected

```
unset FORCE_COLOR PYTHONIOENCODING; python -m pytest tests/ -q --color=no
->  1729 passed, 2 skipped, 1 xfailed, 651 subtests passed in 464.12s
EXIT=0
```

Baseline `1709 / 2 / 0`. **+20 passed, 0 failed, `xfail` is not red.** No
deviation to report.

---

## 2. The attacks — eleven mutations the implementer did not design for

Harness: `.agent-work/issue-456/evidence/g1-reviewer-attacks.py`. Every mutation
runs against a **copy** of `scripts/code_map`; the shipped tree was never edited.
I reused `tests.test_code_map.mutated_package` only for its loud-failure
property — it raises unless the anchor occurs exactly once and the replacement
count rises by exactly one. **It fired twice on my own malformed mutations**, so
a silently-unapplied mutation could not read as a surviving check.

Green control first:

```
CONTROL unmutated package, undamaged map           exit=0 SURVIVED by=['NOTHING']
```

```
A1  no-empty: whitespace-only page                 exit=1 CAUGHT  by=['no-empty-pages','page-accounting']
A2  no-empty: BOM-only page                        exit=1 CAUGHT  by=['page-accounting']
A3  no-empty: header-only stub page                exit=1 CAUGHT  by=['inbound-attribution']
A4  accounting: duplicate page, same title         exit=1 CAUGHT  by=['page-accounting']
A5  refs-line: renderer respells the inbound line  exit=1 CAUGHT  by=['inbound-attribution']
A6  refs-line: counts 3 modules, names 1           exit=1 CAUGHT  by=['refs-line-self-consistent','inbound-attribution']
A7  refs-line: names 2 modules, counts 0           exit=1 CAUGHT  by=['refs-line-self-consistent','inbound-attribution']
A8  join: EXTRACT pass mangles the leaf name       exit=1 CAUGHT  by=['entity-symbol-join']
A9  inbound: every edge counted twice              exit=1 CAUGHT  by=['inbound-attribution']
A10 inbound: one caller name dropped, count kept   exit=1 CAUGHT  by=['inbound-attribution']
A11 determinism: artifact stamped with hash('x')   exit=1 CAUGHT  by=['deterministic-rebuild']
```

### Per check — the undesigned mutation, the command, what I saw

**`no-empty-pages`.** Designed for a page truncated to zero bytes. I attacked
with three shapes it was not designed for. **A1** whitespace-only
(`"   \n\t\n  \n"`) — caught, `no-empty-pages` fires. **A2** a page whose only
content is a BOM — `no-empty-pages` **misses it**; `U+FEFF` is not `str.strip`
whitespace. `page-accounting` catches it (the page has no title), so the gate
still exits 1. **A3** a header-only stub page — not empty by this check's
definition; `inbound-attribution` catches it. Narrowing, not a hole. Observation
(§5b).

**`page-accounting`.** Designed for a collision, a deletion, and a
deletion-plus-stray. I attacked with a **duplicate page carrying the same title**
(A4) — coverage is silent, the count arm fires, exit 1. The check is not
self-agreeing: both arms read page **titles** off disk against the supplement
store, never the renderer's filename expression. The strongest proof is §3 — it
is red on the real corpus right now.

**`refs-line-self-consistent`.** Designed for a page naming its own module. I
attacked its **parser** (A5): the renderer respells `referenced by:` as `refs:`,
so the check's prefix no longer matches. Isolated in-process:

```
refs lines in the whole tree: 0
refs_line_self_consistent(m) -> []
inbound_attribution(m)       -> 3 failures
```

The check goes **vacuous**, not red. It is not a blocker — the property it
guards still fails loudly under attack (A6 counts 3 modules and names 1; A7
names 2 and counts 0; both caught, exit 1) and the render change that silences
it makes `inbound-attribution` red in the same run. But it iterates a set it
never asserts is non-empty, which is exactly what CREW_CONTEXT's *"any guard
that loops must assert what it looped over"* forbids. The implementer put that
assertion in the positive-control **test** and not in the **check**. Filed as
`tc1`.

**`entity-symbol-join`.** Both designed mutations were in `supplement.py`. I
attacked the **other** AST pass (A8): `extract.py` emits `contains` with a
mangled leaf name, every position intact.

```
A8 join: EXTRACT pass mangles the leaf name   exit=1 CAUGHT by=['entity-symbol-join']
```

**Only** `entity-symbol-join` fires. Its independence is now measured from both
sides, not asserted from one.

**`inbound-attribution`.** Designed for a dropped `reads` predicate and a
misattributed caller. I attacked with **inflation** (A9, every edge counted
twice) and with a **caller name dropped while the count is kept** (A10). Both
caught by `inbound-attribution` alone; A10 is the one `refs-line-self-consistent`
is blind to, exactly as its docstring says.

**`deterministic-rebuild` — the decisive attack.** Designed for a dropped
`sorted()` around a set. I attacked the *claim itself*: the renderer stamps
`str(hash("x"))` into a built artifact. A string's `hash` is fixed for a
process's life, so that byte differs between the two builds **only if they
really are separate processes under different `PYTHONHASHSEED` values**.

```
A11 determinism: artifact stamped with hash('x')   exit=1 CAUGHT by=['deterministic-rebuild']
```

A same-process comparison, or two processes sharing a seed, would have
**SURVIVED**. The separate-process claim is proven by running, not read out of
`_build_into`. **Not a BLOCK.**

---

## 3. `check` exits 1 on this repository, for the right reason

Built into scratch (the committed `map/` tree and `.code-map/` untouched) and
ran `check`:

```
CHECK exit=1
ok   no-empty-pages
FAIL page-accounting: 2
      scripts.run_skill_eval:Verdict: an entity the map claims and does not have
      the tree holds 3726 pages; the store accounts for 3727 (1 top index + 112 module indexes + 3614 entities)
ok   refs-line-self-consistent
ok   entity-symbol-join
ok   inbound-attribution
ok   deterministic-rebuild
FAILED 1 of 6 checks: page-accounting
```

**One check, off by exactly one page, naming the collision `g2` owns.** The other
five are green — including `deterministic-rebuild`, which is the close criterion's
*"a double build is byte-identical"*, satisfied on the real corpus.

A missing tree or store is a failure, not a skip:

```
python -m scripts.code_map check --root . --artifacts <nonexistent> --out <nonexistent>
->  FAIL cannot check: nothing built at ... -- run `build` first
EXIT=1
```

**A note on the numbers, not a finding.** Mine are `112 / 3614 / 3726`; the
implementer's were `112 / 3581 / 3693`; the handoff's were different again. The
corpus grows while the run works on it. The **invariant is identical in all
three** — off by exactly one — which corroborates the implementer's own §8.1
finding that no absolute number from a run report should be quoted across
sessions.

---

## 4. The xfail guard — verified, and the reasoning is stronger than claimed

**Today.** `pytest tests/test_code_map.py -k RealCorpus -q -rxX` →
`1 passed, 1 xfailed`, exit 0.

**Simulated `g2`.** `def verdict(` → `def verdict_of(` in
`scripts/run_skill_eval.py`:

```
[XPASS(strict)] RED BY DESIGN, owned by gate g2. ...
->  1 failed   EXIT=1
```

and the collision-set test went red in the same run (`2 failed` over the class).
**Both forcing functions fire together**, so `g2` cannot drop the marker without
updating the recorded collision, and cannot update the collision without
confronting the marker.

Restored byte-exact: SHA256 `ECFBC02C5C9B3AF2D62E39478E2FF31C988DC685AB5422BFC161C0E7A5726048`
before and after; `git status --porcelain scripts/ tests/` empty.

**The conditional is correct.** I measured the corpus myself rather than taking
the implementer's word:

```
case-INSENSITIVE collisions: 1  [('scripts.run_skill_eval:Verdict', 'scripts.run_skill_eval:verdict')]
case-SENSITIVE   collisions: 0  []
```

So on a case-sensitive filesystem the accounting is genuinely green today and a
bare `strict=True` **would** have XPASSed and turned CI red. The implementer was
right to overrule the handoff.

I then probed pytest's own semantics instead of trusting the docs:

```
@pytest.mark.xfail(False, strict=True, reason=...)  passing body -> passed
@pytest.mark.xfail(False, strict=True, reason=...)  failing body -> failed
```

A false condition makes the marker a **complete no-op**. That is better than the
implementer argued: on a case-sensitive filesystem the assertion stays **live**,
so a new *non-case* collision appearing on Linux would go red rather than be
silently swallowed. Strictness is preserved exactly where the defect exists, and
the check is not disabled where it does not.

---

## 5. Move-invariant vs baseline — the rule, quoted and judged

The implementer's rule, verbatim (`g1-implement-RESULT.md` §2):

> **A check is a move-invariant if its expected value is recomputed from the map
> on every run. It is a baseline if its expected value comes from a memory of
> this corpus.**

**Judgement: sound, and keep it.** It is operational rather than a matter of
taste, it is testable against any candidate check, and it classifies all six
correctly. It also correctly rejects the trap the handoff warns about — a
relational identity between two *independently derived* numbers is in scope, a
number compared against itself is not (the implementer's own corollary 1, which
is why the render report's `pages` field is excluded).

**One real weakness, for the gate that places the next threshold.** Corollary 3 —
*"a structural constant fixed by the layout rather than by the corpus is allowed,
and must be named"* — is an exception **carved out of** the rule rather than
derived from it, and "fixed by the layout" is nowhere defined. `TOP_INDEX_PAGES = 1`
is a legitimate instance. But a later gate could smuggle a remembered number in
under the same heading, and the containment (it must live in one named constant
a gate has to change deliberately) is process, not mechanism. Observation for
`gB`, not a blocker.

**Scope held.** The diff is exactly two files. Nothing renamed. `entity_pages`
was not "fixed" by counting the tree a second time. The line base and the page
header format are untouched. The only numeric constants in `checks.py` are
`MAX_REPORTED = 10` (a reporting cap, not an assertion) and `TOP_INDEX_PAGES = 1`.

---

## 6. Observations — four, none blocking

Each is a place a check degrades **quietly** rather than loudly. None breaks the
close criteria, because in every case another check in the same gate goes red and
`check` still exits non-zero.

**(a)** `refs_line_self_consistent` returns `[]` when no page carries a
recognisable inbound line (A5). One assertion — the tree must carry at least one
parsed line — makes the degradation loud. → `tc1`.

**(b)** `no_empty_pages` misses a BOM-only page (A2). `page_accounting` catches
it. → `tc2`.

**(c)** `tree_diff(empty, empty) -> []` with no assertion that either build
produced a page. Unreachable through `run()` — `page_accounting` reads the same
tree — but the same standard applies. → folded into `tc1`.

**(d)** The `module:name` supplement key has no type: `checks.py` splits it six
times and twice chains a further `rsplit` to reach the leaf. Deliberately NOT
fixed here — the store schema is strings and `g3` owns it. → `tc3`.

### Fowler pass

`.agent-work/issue-456/g1-review/fowler-pass.json`; `verify_fowler_pass.py`
exits 0, 12 smells, none skipped.

- **flagged**: `duplicated-code`, `data-clumps`, `primitive-obsession`,
  `message-chains` — all observations above.
- **overridden**: `comments-as-deodorant`. `checks.py` is about half docstring;
  `page_accounting` carries 42 documentation lines over 13 code lines. Standard
  that wins: CREW_CONTEXT *"Verification Discipline"* + *"Evidence You Owe Back"*,
  plus the handoff's own requirement that what a check does **not** prove is
  recorded beside it. The prose records **measured limits and their owners** —
  `StoreScan`'s blindness to the extractor, `entity_symbol_join`'s leaf-only
  comparison and D2, `page_accounting`'s `tc24` ruling — not restatements of
  short plain code. I confirmed two of those limits by attack. Deleting the prose
  would delete the gate's findings.
- **absent**: `long-method` (longest body 31 code lines, AST-measured),
  `large-class`, `feature-envy`, `long-parameter-list`, `shotgun-surgery`
  (tested by attack: A5's blast radius was exactly the `REFS_*` block, as
  designed), `divergent-change`, `speculative-generality`.

---

## 7. Constraints honoured

- `git status --porcelain scripts/ tests/` is **empty**. The only file I mutated
  outside a copy was `scripts/run_skill_eval.py`, restored byte-exact and
  SHA256-verified.
- `git add -A` never used; nothing staged. The untracked `map/` tree is untouched.
- Stdlib only. No timings introduced. `python`, never `py`.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` never touched.
- All work inside `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
  No force-push, no merge to `main`.

---

## Workflow Feedback

1. **The `r6-fowler` rail is still broken for a survey, and this is the second
   crew to hit it.** `REVIEW_SURVEY.template.json` ships postcondition `c1` with
   a literal `<fowler-pass-record-path>` placeholder, and SKILL.md instructs the
   reviewer to "fill this item's postcondition command with the real record
   path". No engine verb can do that on a **survey** controller: `amend` refuses
   with *"amend applies to gated checklists"*, and `attest` refuses an
   engine-checked condition. The only route left is a **forced waive**, which
   journals as a risk acceptance when in fact the rail was run and passed. The
   `g0` reviewer left exactly this note at
   `.agent-work/issue-456/g0-review/review.json`. Fix: ship `c1` with no command
   and let `record` accept an attached command evidence item, or make
   `retext-check` legal on a survey.
2. **`bash -c` with `env -u ...` is refused in a worktree-isolated session.** The
   handoff mandates `env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest`, but
   the Bash tool rejects it ("runs `env` with `-m`, whose effect on the command it
   wraps can't be verified"). `unset FORCE_COLOR PYTHONIOENCODING; python -m pytest`
   is equivalent and accepted; PowerShell's `$env:FORCE_COLOR=$null` also works.
   Worth putting in the handoff's environment-traps section, because the mandated
   incantation does not run.
3. **The handoff's `entity_pages = 3536` needs a unit.** It refers to the *render
   report's* field, but `checks.MapUnderCheck.entity_pages` is a different
   quantity (pages whose title names an entity) and the two agree even when the
   invariant is red — I measured `pages - 1 - modules = 3613` and
   `entity_pages = 3613` while `page_accounting` was correctly failing. A reviewer
   chasing the handoff's number could conclude the check was broken. Name the
   field's source next time.
4. The handoff was otherwise unusually good to work from: naming the exact defect
   shape to hunt (expected value from the same expression) and the exact claims to
   reproduce by running turned an open-ended attack into a bounded one.
