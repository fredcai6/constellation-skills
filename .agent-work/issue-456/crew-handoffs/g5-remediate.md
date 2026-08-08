# Remediation Handoff — gate `g5`: the legend lies about the predicate

Issue #456. Invoke the `constellation-implementer` skill, drive it to a plan,
execute it, return an `IMPLEMENTER_RESULT`. **This is a rework after a `BLOCK`,
not a new gate.** The scope is deliberately narrow — do not widen it.

## The block, in one paragraph

`g5` shipped a production/test caller split that works. Its one defect:
`render.SPLIT_LEGEND` — printed on **every one of the 3864 pages** — tells the
reader the rule is *"a **top-level** tests package"*, while `is_test_module` ends
with `return "tests" in parts`, matching a `tests` segment **anywhere** on the
dotted path. Both the reviewer and the Commander reproduced it directly:
`is_test_module("scripts.tests.helpers")` → `True`,
`is_test_module("pkg.sub.tests.foo")` → `True`, in **both** hand-independent
copies (`render.py` and `checks.py`). The one sentence explaining the gate's
mechanism, on every page, states a rule the code does not apply.

## The Commander's ruling — do exactly this

**Fix the LEGEND. Keep the PREDICATE. Add a pinning check.**

Reasoning, so you can challenge it if it is wrong: a nested `pkg/tests/`
subpackage is a real and common layout (Django-style app-local tests), so
*"a `tests` segment anywhere on the dotted path"* is the more defensible reading
of pytest's published convention — `top-level` is simply the less accurate
description of what the code correctly does. It is also the smaller diff and it
**reclassifies zero entities**, so every measured number in this gate's evidence
stands unchanged. If you can show the narrower predicate is actually the right
rule, say so and argue it — but then you owe a re-measurement.

Three pieces of work, all small:

1. **Reword `SPLIT_LEGEND`** so it states the rule the code applies. Keep it one
   sentence, pure ASCII, agent-lean. Remember `checks.py` declares its own copy
   of the legend **by hand** for independence — update **both**, and do **not**
   collapse them into an import. That independence is load-bearing: the reviewer
   proved it by diverging only `checks.py`'s `is_test_module` and watching **two**
   checks go red.

2. **Add the pinning check that was missing** (this is the real fix — the reword
   alone leaves the same drift possible tomorrow). The precedent is one function
   away and you should follow its shape:
   `RefsAccountingTests.test_the_legend_names_the_predicates_the_count_actually_counts`
   pins `REFS_LEGEND` to `load_stores`'s real predicate set. Do the same for
   `SPLIT_LEGEND` against `is_test_module`'s real behaviour — the test must go
   **red** if the legend's stated rule and the predicate drift again. Prove it:
   show it red against the current (wrong) legend **before** you reword, then
   green after. That is your red-before-green, and it is a grade **A** falsifier
   — it reproduces on real input today.

3. **Fix `measure_split.py`** to carry the definer dimension. Its headline
   "unused: 2428 (64.7%)" reproduces the exact conflation this gate exists to
   remove: 2340 of those 2428 (**96.4%**) are test-defined entities whose own
   pages say zero callers is the normal expected state. The number a reader wants
   — genuinely unused **production** code — is **88**. A ready template is at
   `.agent-work/issue-456/evidence/g5_reviewer_split_by_definer.py`. The correct
   figures, already measured twice independently and agreeing exactly:

   | bucket | prod-defined | test-defined |
   |---|---|---|
   | unused | **88** | **2340** |
   | test-only | **2** | 449 |
   | production | 873 | 0 |

   Report the corrected headline in your `IMPLEMENTER_RESULT`.

## Close criteria

- The legend states the rule the code applies, in both hand-independent copies.
- A check goes **red** when the legend and the predicate disagree, shown red
  before green.
- `measure_split.py` reports the definer dimension; the corrected split is stated.
- No entity is reclassified — the split counts above must be unchanged.
- The two `is_test_module` copies stay independent; **no import** between them.
- FULL suite green; fresh `build` then `check` → 7/7, exit 0.

## Your gate selector — run it by hand (`tc38`)

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'refs or caller or legend' -q --color=no
```

Report its RED and GREEN states with counts and exit codes. `-k 'refs or caller'`
collects **19** today; adding `legend` should collect your new test too.

## Do NOT touch

- `is_test_module`'s predicate body (per the ruling above, unless you overturn it).
- `_make_collision_repo`'s `INDEX` collision (`g1`'s only cross-platform falsifier).
- `OWN_MODULE_NAMED_MUTATION` / `LEGEND_DROPPED_MUTATION` — already retargeted by
  `g5` and re-verified by the reviewer as still killing their mutants.
- `entity_symbol_join`'s two independent derivations (`g3`'s whole gate).
- `g4`'s `page_location_matches_content`.
- Page headers: path + `, N lines`, **no `:<line>`**. Verified 0 of 3864 headers.
- The 386 non-ASCII pages — all traced to **pre-existing** docstring prose (an
  em-dash in `scripts/agent_work_root.py`). **Out of scope. Leave them.**

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,864-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- `C:/Programs/f1Brainz` is READ-ONLY. `C:/Programs/superCoolSpaceSim` is
  C++/Obj-C with zero `.py` files — a **null test, never a shape test**.
- Never force-push; do not merge to `main`.
- Use `python`, **never `py`**.
- The full suite takes ~5 minutes. Run it with `run_in_background` and let the
  completion notification wake you — do **not** poll an empty output file. The
  `g5` implementer lost real wall-clock doing exactly that.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, loops,
  `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining. Wrapper scripts are
  in `.agent-work/issue-456/evidence/` — `run_record.py`, `run_waive.py`,
  `run_consolidate.py`, `run_flag_candidate.py`. **Reuse them.**

## Baseline entering this remediation

Commit `1f5c8a6e`. Suite **1780 passed, 2 skipped, 672 subtests, 0 failed**;
fresh `build` then `check` → **7/7 exit 0**; modules 111, entities 3752, pages
3864; selector `-k 'refs or caller'` → 19.

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g5-remediate-RESULT.md`.

**Do not end your turn with the RESULT file absent** — if blocked, write it anyway
with the blocker named. A partial result with an honest blocker beats silence.

## You are expected to overrule this handoff if you can falsify it

Six times on this run a crew has proven a Commander instruction wrong, every time
by **running the thing rather than reading it**. The ruling above is mine and it
is exactly the kind of call that can be wrong.

**Return thin, write fat.**
