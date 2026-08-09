# Re-review Handoff — gate `g5`, attempt 2 (remediation of a `BLOCK`)

Issue #456. Invoke the `constellation-reviewer` skill, drive it to a plan, execute
it, return a `REVIEW_RESULT` with a verdict of `APPROVE` or `BLOCK`.

**This is a RE-review after a BLOCK, not a fresh gate.** Attempt 1 shipped a
working production/test caller split and was blocked on ONE defect. Your job is
to decide whether that defect is genuinely closed and whether closing it broke
anything. Do not re-litigate attempt 1's capability — it was already reviewed and
confirmed. Do not widen scope.

## What was blocked, and what was ruled

`render.SPLIT_LEGEND` — printed on every entity page — said the test/production
split keys on a **top-level** `tests` package. `is_test_module` ends with
`return "tests" in parts`, matching a `tests` segment **anywhere** on the dotted
path. The page stated a rule the code does not apply, on the one sentence
explaining the gate's own mechanism.

**Commander's ruling:** fix the LEGEND, keep the PREDICATE, add a pinning check.
A nested `pkg/tests/` subpackage (Django-style app-local tests) is a real, common
layout, so "anywhere on the dotted path" is the more defensible reading of the
published convention. Smaller diff, reclassifies zero entities.

**You may overturn this ruling.** If the narrower predicate is actually the right
rule, say so and argue it — but then the remediation owes a re-measurement, and
that is a BLOCK.

## What the remediation did — commit `588d5419`

1. Reworded `SPLIT_LEGEND` in **both** hand-independent copies (`render.py` line
   361, `checks.py` line 301) to "a tests package anywhere on the module path".
2. Added `ProductionTestCallerSplitTests.
   test_the_legend_states_the_rule_the_predicate_actually_applies`, which pins
   both directions of drift: a behavioural half (nested `pkg.sub.tests.helper`
   must classify as a test module in **both** copies) and a wording half
   (neither legend may contain "top-level").
3. Fixed `.agent-work/issue-456/evidence/measure_split.py` to carry the definer
   dimension.

## What the Commander already verified — do NOT just reproduce these

I ran all of this myself. Reproducing it proves nothing new. It is here so you
can spend your budget on attack instead of repetition.

- Reword applied identically to both copies; **no import** introduced between
  them (`grep` for an import of `render` in `checks.py` → no match).
- Fresh `build` then `check` → **7/7, exit 0**. Modules 111, entities **3753**,
  pages **3865**.
- Full suite **1781 passed, 2 skipped, 672 subtests, 0 failed** (baseline+1).
- Commit contains explicit paths only; `git ls-tree -r HEAD -- map/` → **0**.
- Of 3865 pages, **3753** carry the new legend and exactly **1** contains the
  string "top-level tests package" — the new test's own page, whose docstring
  quotes the old legend to explain what the test guards against. That is correct
  behaviour, not a leftover. Do not "fix" it.
- The definer split now reads 88 / 2341 / 2 / 449 / 873 / 0. The single moved
  cell (`unused_test_defined` 2340 → 2341) is the new test itself — a brand-new
  test-defined entity with no callers — corroborated by entities 3752 → 3753 and
  pages 3864 → 3865. **A new entity, not a reclassified one.**

## Where to spend your budget — attack these

1. **The pinning check is the whole point of the remediation. Attack it.** The
   reword alone is cosmetic; the test is what stops the drift recurring. Mutate
   it with mutations its author did NOT choose. Reproducing the author's own
   red-before-green proves only that their probe works. Specifically worth
   trying: does the test still go red if someone rewords the legend to a
   *different* overclaim that avoids the literal string "top-level"? The wording
   half is an `assertNotIn("top-level", ...)` — a negative assertion against one
   literal. Decide whether that is a real pin or a pin against one exact past
   mistake. If it is the latter, say so and grade it.

2. **Independence must have survived.** `g2` established that `checks.py`
   re-declares the refs grammar **by hand** rather than importing it, because a
   check that reads its expected text out of the code under test can only ever
   agree with it. The remediation edited the legend in both copies. Verify the
   copies are still genuinely independent AND still load-bearing — the attempt-1
   reviewer proved load-bearingness by diverging only `checks.py`'s copy and
   watching **two** checks go red. Confirm that still holds after this edit.

3. **The +1 explanation.** I believe it, but I derived it partly by inference.
   Verify it directly: confirm the single new entity is the new test method and
   that no pre-existing entity changed bucket. If any existing entity moved, that
   is a BLOCK.

4. **Does the reworded legend actually describe the predicate?** Read
   `is_test_module` and the new legend side by side and decide whether the
   sentence is now TRUE — not merely different. Include the `test_*.py` /
   `*_test.py` half, not just the package half. If the legend is still wrong in
   some other respect, that is the same defect class and it blocks again.

## Your gate selector — run it by hand (`tc38`)

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'refs or caller or legend' -q --color=no
```

Collects **20** now (19 at baseline + the new test). Report its state with count
and exit code. A check that can only ever FAIL is as informationless as one that
cannot fail — run the selector yourself and confirm it discriminates.

## Do NOT touch

- `is_test_module`'s predicate body (unless you overturn the ruling and argue it).
- `_make_collision_repo`'s `INDEX` collision — `g1`'s only cross-platform
  falsifier for `page-accounting`.
- `OWN_MODULE_NAMED_MUTATION` / `LEGEND_DROPPED_MUTATION`.
- `entity_symbol_join`'s two independent derivations (`g3`'s whole gate).
- `g4`'s `page_location_matches_content`.
- Page headers: path + `, N lines`, **no `:<line>`**. This was a direct human
  ruling. 0 of 3865 headers carry a line position.
- The 386 non-ASCII pages — pre-existing docstring prose. Out of scope.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked map tree is staged at the final gate.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- `C:/Programs/f1Brainz` is READ-ONLY (1227 modules — the only real second Python
  corpus). `C:/Programs/superCoolSpaceSim` is C++/Obj-C with zero `.py` files — a
  **null test, never a shape test**.
- Use `python`, **never `py`** (`py -m pytest` dies "No module named pytest" and
  reads as a silently green run).
- The full suite takes ~6 minutes. Run it with `run_in_background` and let the
  completion notification wake you. Do **not** poll a buffered output file — both
  prior `g5` crews lost real wall-clock doing exactly that, and I had to nudge
  them twice each.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, loops,
  `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining. Use plain separate
  commands, script files, `git commit -F <file>`. Wrappers are in
  `.agent-work/issue-456/evidence/`.
- **Context governor (`tc39`):** the HARD band fires around 15% fill and refuses
  `advance` until you attach a refresh-request:
  `attach <item> --type refresh-request --field seam=<item> --field why_ref=<id>`
  where `<id>` is the **current latest** `why_trail[-1].id` read from the plan
  JSON. Every `advance` mints a new one, so a cited id goes stale instantly —
  read it and attach in the same breath. Both prior crews hit this.

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g5-rereview-RESULT.md`, with an explicit
verdict line of `APPROVE` or `BLOCK`.

**Do not end your turn with the RESULT file absent** — if blocked, write it
anyway with the blocker named. A partial result with an honest blocker beats
silence.

## You are expected to overrule this handoff if you can falsify it

Six times on this run a crew has proven a Commander instruction wrong, every time
by **running the thing rather than reading it**. The attempt-1 reviewer beat its
mandate and was right to. The ruling above is mine and is exactly the kind of
call that can be wrong.

**Return thin, write fat.**
