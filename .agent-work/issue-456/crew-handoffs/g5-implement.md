# Implementer Handoff — gate `g5`: unused and untested must stop looking identical

Issue #456. Invoke the `constellation-implementer` skill, drive it to a plan,
execute it, return an `IMPLEMENTER_RESULT`.

## THE ONE THING THIS GATE EXISTS FOR

Open any entity page today and you may read:

```
referenced by: none found
```

That single line is doing the work of **three completely different facts** and a
reader cannot tell which one they got:

1. **Nothing calls this.** Dead in production, dead in tests. The finding a map
   is *for*.
2. **Only tests call this.** Exercised, but nothing in the shipped system uses
   it. A different and often more interesting finding — and today it is not even
   distinguishable from (3), because a test caller is counted exactly like a
   production one and just named in the list.
3. **This IS a test.** Its caller is pytest. Zero inbound is the *normal,
   expected, uninteresting* state, and the line is pure noise on ~74% of this
   corpus's pages.

The gate: **split the caller list into production and test callers, and make a
test-defined entity's inbound line say something true instead of something
alarming.**

**Do NOT delete test pages.** Explicit ruling, critic IF7 over SY8. Deleting the
74% is not de-conflation, it is amputation, and it destroys the (2) signal —
you cannot say "only tests call this" if the tests are not in the graph.

## The hard question, and how to answer it honestly

**What makes a caller a test caller?** This is the gate's real design decision
and it is the same trap `g4` walked into: a predicate tuned to *this* repo's
shape looks perfect here and is worthless on the next corpus.

Do not invent a house convention. **Ground the predicate in the external
standard that already governs this** — pytest's own documented default discovery
rules (`test_*.py` / `*_test.py`, and the conventional `tests` package). A
predicate that cites a published tool default is *derived*; one that cites
"how this repo happens to be laid out" is *tuned*. Say in the code comment which
one you are and why.

Then answer the question a derived predicate forces you to answer:

> **What does the map do on a corpus whose tests do NOT follow that convention?**

It will classify every test caller as production. That is a real degradation and
it must **degrade honestly and visibly**, not silently — the way `g4`'s tier
reports "nothing to group" rather than fabricating structure. State on the page,
or in the run report, what the classification was based on. A reader who
disagrees with the split must be able to see the rule that produced it.

**Prove it on `f1Brainz`** (`C:/Programs/f1Brainz`, READ-ONLY, 1227 modules /
15037 entities, with BOTH a `tests` package of 548 modules AND a separate
`run_tests` module — a genuinely different shape from this repo). Report the
production/test split it produces there.

**Do NOT use `C:/Programs/superCoolSpaceSim` as a second corpus.** It is
C++/Obj-C with **zero tracked `.py` files**; it indexes to 0 modules / 0
entities. A previous handoff of mine named it as cross-corpus proof and that was
**wrong** — it is a null test, not a shape test. Run it if you want the null;
do not count it as evidence of anything.

## Also owned by this gate: `tc32`

> **A green determinism run is NOT evidence of stable caller ordering.**

The determinism check compares two builds of the same tree in the same order. It
would stay green even if the caller list were ordered by dict-insertion, because
both runs insert in the same order. `render.refs_line` currently does
`ext = sorted(...)`, so today it is stable — but **nothing proves it**, and this
gate is about to add a second list beside it.

Close `tc32` with a falsifier that actually distinguishes: build the same corpus
under a **permuted file-visit order** and assert the rendered caller lists are
byte-identical. Then prove the falsifier bites by deleting the `sorted(...)` and
showing it goes red. Both new lists must be covered, not just the old one.

## THE TRIPWIRE THIS GATE IS MOST LIKELY TO TRIP

`checks.py` declares `REFS_PREFIX`, `REFS_NONE`, `REFS_SELF_ONLY`,
`REFS_MODULES` and `REFS_LEGEND` **independently** of `render.py`'s copies. Read
`checks.py:286-292` — the comment says exactly why:

> *a check that reads its expected text out of the code under test can only ever
> agree with it.*

**You are changing that grammar, so you are the gate most likely to collapse
that independence into an `import`.** Do not. Update both declarations by hand
and let `RefsAccountingTests` prove they still match byte for byte. If you find
yourself typing `from .render import REFS_`, stop — that is the defect this whole
run exists to hunt (`tc29`/`tc38`: a check that cannot fail).

Everything downstream of that grammar must move with it:
`checks.parse_refs` / `Refs` (`checks.py:294-317`), `checks.refs_lines`,
`refs_line_self_consistent` (~`checks.py:408`), `inbound_attribution`
(~`checks.py:595`), and `render.refs_line` (`render.py:336-357`).
`parse_refs` returning `None` on your new form is a silent map-wide failure —
`refs_line_self_consistent` covers **every** page in the tree.

## Close criteria — judged verbatim

- A reader can tell **unused** from **only-tests-use-it** from **is-a-test**
  without opening another page.
- The test/production predicate is **derived from a published convention**, not
  tuned to this corpus, and the page or report says what it was based on.
- `referenced by: none found` no longer appears bare on test-defined entities.
- Test pages are **NOT** deleted.
- `tc32` closed: caller ordering proven stable under a permuted visit order, by a
  test shown red before green.
- **No absolute-count threshold** anywhere in the classification (critic F4).
- Page register stays agent-first, minimal, **pure ASCII**.
- The FULL suite green at the gate boundary (critic F6).

## Your gate selector — run it by hand (`tc38`)

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'refs or caller' -q --color=no
```

Collects **11** today. Report its RED state (before your fix) and its GREEN state
(after), with counts and exit codes for both. A selector that collects zero, or
one that can never go red, fails this gate on its own.

## Specific exclusions — the tripwires, and where they sit

- `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and **must keep colliding**.
- `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py` — the refs line
  is exactly what it anchors on, so **check this one directly**.
- `test_refs_lines_are_self_consistent_on_an_intact_map`'s input precondition.
- `entity_symbol_join`'s two independent derivations (`extract.child_sym` vs
  `checks.SourceScan`) must stay independent — `g3`'s whole gate proved that.
- Page headers carry path + `, N lines` and **no `:<line>`**, by the human's
  ruling. Re-verify at the full 3840-page scale.
- `g4`'s `page_location_matches_content` (7th check) must stay green.

## Test mode

**port-defective-then-fix / red-before-green.** Every reproducer committed in its
FAILING state before the fix. Grade each falsifier **A** (reproduces on real
input today) or **B** (red by absence / negative control). If something is a
regression guard rather than a falsifier, **say so** rather than silently
counting it as one — `g4`'s implementer did exactly that and got credit for it.

## Allowed scope

`scripts/code_map/render.py`, `scripts/code_map/checks.py`,
`tests/test_code_map.py`, plus evidence scripts under
`.agent-work/issue-456/evidence/`. `checks.py` is in scope here by necessity, not
exception — the grammar lives in both files by design.

## Constraints

- Stdlib only. **No timings in any run report** — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,840-page `map/` tree is staged at the
  final gate. Stage explicit paths only. Use `build --artifacts/--out` into scratch.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` clean at the end and
  report the sha256 of anything mutated and restored.
- Never force-push; do not merge to `main`.
- Use `python`, **never `py`**.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, compound
  commands with loops, `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining.
  Engine verbs taking free text fail on any real message. Wrapper scripts that
  read text from a file and pass list argv via `subprocess` are already in
  `.agent-work/issue-456/evidence/` — `run_record.py`, `run_waive.py`,
  `run_consolidate.py`, `run_flag_candidate.py`. **Reuse them; do not rediscover
  them.**

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'refs or caller' -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

Entering this gate: **1772 passed, 2 skipped, 672 subtests, 0 failed, 0 xfailed**;
fresh `build` then `check` → **7/7, exit 0**; render report modules **111**,
entities **3728**, pages **3840**. `check` reads a **stale** tree at `<root>/map`
— run `build` first or the exit code means nothing.

## Authority

Push and a full non-draft PR are pre-approved at the Commander level; **merge to
`main` is NOT**. You commit within the worktree; the Commander pushes.

## Required evidence

- Both selector states (RED then GREEN) with counts and exit codes.
- Full suite numbers before and after.
- Fresh `build` then `check` exit code and check count.
- The three-way split measured on **this repo**: how many entities land in each
  of unused / test-only / production, as counts and as a share of 3728.
- The same split measured on **`f1Brainz`**, with its shape stated.
- The `tc32` permuted-order falsifier, shown red before green.
- A named statement of what the classification predicate is derived from, and
  what corpus shape defeats it.

## You are expected to overrule this handoff if you can falsify it

**Six times** on this run a crew has proven a Commander instruction wrong, every
single time by **running the thing rather than reading it** — including the
`superCoolSpaceSim` error I admitted above, found by `g4`'s own implementer. If
something here is wrong, prove it and say so. That is a success, not a conflict.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.render/`
- structural: `scripts/code_map/` render module
- capability: answer cross-file questions cheaply
- constraint: page register is agent-first and aggressively minimal
- decision: production vs test caller split
- evidence: inbound-edge attribution

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g5-implement-RESULT.md`.

If you hit a context seam, park cleanly and hand off rather than pushing through.

**Return thin, write fat.**
