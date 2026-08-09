# Reviewer Handoff — gate `g5`: unused vs untested must stop looking identical

Issue #456. Invoke the `constellation-reviewer` skill, drive it to a review plan,
execute it, return a `REVIEW_RESULT` with an explicit verdict.

## THE TWO THINGS THIS REVIEW EXISTS FOR — both already measured by the Commander

I did my own integration pass before dispatching you and found two problems. Your
first job is to **confirm or refute both by running them**, then rule on each.
Do not take my numbers on trust any more than I took the implementer's.

### FINDING A — the page tells the reader a rule the code does not apply

`render.SPLIT_LEGEND` is printed on **every one of the 3864 pages**. It says:

> `split: production vs test caller module, by pytest's default discovery
> convention -- test_*.py / *_test.py naming, or a **top-level** tests package.
> a module matching neither is counted production.`

The code (`render.is_test_module`, `render.py:387-391`) ends with:

```python
return "tests" in parts
```

That is a `tests` segment **ANYWHERE** on the dotted path, not top-level. I probed
it directly: `scripts.tests.helpers` → `True`, `pkg.sub.tests.foo` → `True`.
The function's own docstring says "anywhere on the module's own dotted path" and
the `IMPLEMENTER_RESULT`'s Assumptions section says the same — **only the legend,
the one surface the reader actually sees, says `top-level`.**

This lands squarely on the gate's own close criterion ("the page says what the
classification was based on") and on this run's central defect class: a stated
rule that does not match the applied rule. `checks.py` restates `is_test_module`
by hand for independence, which is right — but **nothing checks the legend
against the predicate**, so the two can drift silently.

Confirm it, decide whether the fix is the legend text or the predicate, and say
whether a check should pin them together the way `RefsAccountingTests` pins the
refs legend. **Rule it blocking or non-blocking and defend the ruling.**

### FINDING B — the headline split number conflates exactly what the gate de-conflated

The `IMPLEMENTER_RESULT` reports, as its top-line evidence:

> unused: **2428 (64.7%)**, test-only: 451 (12.0%), production: 873 (23.3%)

`measure_split.py` buckets purely on the two rendered caller lines. It never asks
whether the entity is **itself defined in a test module**. So every test function
with no callers lands in "unused" — the very entities whose own pages carry
`TEST_NOTE` saying *"zero callers here is the normal, expected state, not a
finding."*

I re-measured over the same built tree, adding that one dimension:

| bucket | prod-defined | test-defined |
|---|---|---|
| unused | **88** | **2340** |
| test-only | **2** | 449 |
| production | 873 | 0 |

**2340 of the 2428 "unused" entities (96.4%) are test-defined.** The number a
reader actually wants — genuinely unused production code — is **88**, not 2428.
A **27x** difference. And "production code exercised only by tests" is **2**.

Note the pages themselves are RIGHT: `TEST_NOTE` appears on 2789 test-defined
pages and on **zero** production-defined pages — I verified that count directly.
The defect is in the **measurement and the claim**, not obviously in the shipped
renderer. So the question I want you to answer is:

> **Does the gate actually deliver its stated capability, or only appear to?**
> A reader on a single page can tell the three states apart — that is real and it
> works. But the run's own summary number reproduces the conflation the gate
> exists to remove. Is that a reporting defect only, or does something a reader
> would reach for (the module index, the top index, any aggregate) carry the same
> conflated framing?

Check whether the conflation escapes `measure_split.py` into anything **shipped**.
If it does, that is materially more serious than a bad evidence number.

## Also verify

1. **`tc32` genuinely closed.** `CallerOrderStableUnderPermutedVisitTests`. The
   implementer honestly reported that its mutant initially SURVIVED against a
   1-external-caller fixture and only bites at 2 callers. Good disclosure —
   now **attack it with a mutation the implementer did not choose**. Its own
   probe (deleting `sorted(...)`) proves only that probe works. Try ordering by
   insertion, by reverse-sort, by call-count — and confirm the test still bites.
   Also confirm it covers **both** new bucket lines, not just one.

2. **The two `is_test_module` copies really are independent.** `checks.py` has no
   `import` from `render.py` — I grepped and confirmed. But independence is only
   worth something if a **divergence is catchable**. Diverge them deliberately
   (change one copy's rule) and prove a check goes red. If nothing catches it,
   the second copy is decoration and that is a `tc29`/`tc38` finding.

3. **The retargeted mutation anchors.** The implementer moved
   `OWN_MODULE_NAMED_MUTATION` to a new anchor and changed `LEGEND_DROPPED_MUTATION`.
   Retargeting a mutation anchor is the single easiest way to quietly defang a
   guard. Verify each still **kills its mutant**, and that the new anchor is
   load-bearing rather than incidental.

4. **`tc32`'s sibling risk:** the gate added a second caller list. Confirm both
   lists are ordered deterministically, not just the production one.

## Close criteria — judged verbatim

- A reader can tell **unused** from **only-tests-use-it** from **is-a-test**
  without opening another page.
- The predicate is **derived from a published convention**, not tuned to this
  corpus, and the page says what it was based on.
- `referenced by: none found` no longer appears bare on test-defined entities.
- Test pages are **NOT** deleted (critic IF7 over SY8).
- `tc32` closed, proven red before green.
- **No absolute-count threshold** in the classification (critic F4).
- Page register agent-first, minimal, **pure ASCII**.
- FULL suite green (critic F6).

## Specific exclusions — the tripwires, and where they sit

- `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and **must keep colliding**.
- `OWN_MODULE_NAMED_MUTATION`'s anchor in `render.py` — **retargeted by this
  gate**, so check it directly (see item 3).
- `test_refs_lines_are_self_consistent_on_an_intact_map`'s input precondition.
- `entity_symbol_join`'s two independent derivations (`extract.child_sym` vs
  `checks.SourceScan`) — `g3`'s whole gate proved that independence.
- `g4`'s `page_location_matches_content` (7th check) must stay green.
- Page headers carry path + `, N lines` and **no `:<line>`**, by the human's
  ruling. Re-verify at the full 3864-page scale.

## What was implemented

`render.py` (`is_test_module`, `_bucket_line`, rewritten `refs_line`, new
`REFS_PROD_PREFIX` / `REFS_TEST_PREFIX` / `TEST_NOTE` / `SPLIT_LEGEND` /
`REFS_NONE`), `checks.py` (independent second copies, rewritten
`refs_line_self_consistent` and `inbound_attribution`, new `refs_prefix_of`),
`tests/test_code_map.py` (`ProductionTestCallerSplitTests` ×6,
`CallerOrderStableUnderPermutedVisitTests` ×2, two new fixtures, three retargeted
anchors), and `.agent-work/issue-456/evidence/measure_split.py`.

The crew committed its own work at **`1f5c8a6e`** ("g5: split caller lists into
production vs test, close tc32"). Inspect with
`git show 1f5c8a6e -- scripts/ tests/` or `git diff 5e5e2794..1f5c8a6e`.
Verified: the commit does **not** contain the untracked `map/` tree, and
`git ls-tree -r HEAD --name-only -- map/` still returns **0** files.

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'refs or caller' -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

Commander's own integration numbers, independently run: fresh `build` then `check`
→ **7/7, exit 0**; report modules 111, entities 3752, pages 3864. Selector
`-k 'refs or caller'` collected 11 entering the gate, **19** now. `check` reads a
**stale** tree at `<root>/map` — run `build` first or the exit code means nothing.
Use `python`, **never `py`**.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,864-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- `C:/Programs/f1Brainz` is **READ-ONLY** and is the only real second Python
  corpus. `C:/Programs/superCoolSpaceSim` is C++/Obj-C with **zero `.py` files** —
  it indexes to 0 modules. It is a **null test, never a shape test**. A previous
  handoff of mine named it as cross-corpus proof and that was **wrong**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` shows the same
  modified set at the end, and report the sha256 of anything mutated and restored.
- Never force-push; do not merge to `main`.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, loops,
  `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining. Wrapper scripts that
  read text from a file and pass list argv via `subprocess` are in
  `.agent-work/issue-456/evidence/` — `run_record.py`, `run_waive.py`,
  `run_consolidate.py`, `run_flag_candidate.py`. **Reuse them; do not rediscover
  them.**

## A note on this crew's predecessor

The implementer stalled twice and needed two nudges, but its `IMPLEMENTER_RESULT`
is unusually honest — it volunteered that its own `tc32` mutant initially
survived, and it disclosed the nested-vs-top-level `tests` assumption in its
Assumptions section even though the legend contradicts it. **Read that Assumptions
section; it is where Finding A is admitted.** Honest disclosure is not the same as
a correct implementation — grade the code, credit the disclosure.

## You are expected to overrule this handoff if you can falsify it

**Six times** on this run a crew has proven a Commander instruction wrong, every
time by **running the thing rather than reading it**. Findings A and B above are
mine and they are exactly the kind of thing that can be wrong. If my measurement
is off, prove it and say so.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.render/`
- structural: `scripts/code_map/` render module
- capability: answer cross-file questions cheaply
- constraint: page register is agent-first and aggressively minimal
- decision: production vs test caller split
- evidence: inbound-edge attribution

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g5-review-RESULT.md` with an explicit verdict
(APPROVE / APPROVE-WITH-FINDINGS / BLOCK). **Lead with your ruling on Findings A
and B** — confirmed or refuted, blocking or not, and why. Then `tc32`'s attack,
the independence-divergence test, the retargeted anchors, full suite numbers,
`check` exit code after a fresh `build`, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through.
**Do not end your turn with the RESULT file absent** — a partial result naming an
explicit blocker is worth far more to me than silence.

**Return thin, write fat.**
