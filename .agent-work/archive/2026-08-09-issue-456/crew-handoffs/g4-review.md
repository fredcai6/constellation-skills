# Reviewer Handoff — gate `g4`: the top index must ROUTE, not list

Issue #456. Invoke the `constellation-reviewer` skill, drive it to a review plan,
execute it, return a `REVIEW_RESULT` with an explicit verdict.

## THE ONE THING THIS REVIEW EXISTS FOR — a Commander error, already admitted

Critic F9 named the gate's trap before it opened: **~75% of this repo's entities
are test code**, so a routing tier tuned to this repo's shape will look excellent
here and fail on the next corpus. The handoff demanded proof on **two** other
corpora.

**My handoff was wrong.** I named `C:/Programs/superCoolSpaceSim` as one of the
two. It is a **C++/Obj-C repository with zero tracked `.py` files** — it indexes
to `no mappable modules found`, 0 modules, 0 entities. That is a **null test, not
a counter-shape test**. The implementer ran it rather than reading it, and
reported the null honestly instead of dressing it up as a pass. Credit to it.

**The consequence: only ONE corpus (`f1Brainz`) actually exercised the trap.**
That is the residual risk and it is your first job.

> **Find a genuinely different corpus shape and run the tier against it.**
> `f1Brainz` (1227 modules / 15037 entities, a conventional `src/` layout) is one
> shape. This repo is another. Both are multi-package Python trees. Go find a
> third that stresses the tier differently — a flat single-package tree, a tree
> with one dominant package, a deeply-nested one, a tree of loose top-level
> modules with no packages at all. Synthesize it if no real one is at hand; a
> constructed corpus with a stated shape is honest evidence, an untested claim is
> not.
>
> The tier logic is **one predicate**: `len(m.split(".")) >= 3`. Ask directly:
> **what corpus shape makes that predicate produce a useless index?** Then build
> that shape and run it. If you find one, say whether it is a real-world shape or
> a pathological one — that distinction is the finding, not a technicality.

Judge the **routing** claim too, not just the shape. A cold reader must be able to
pick a direction from the top page **without opening module pages**. Read the
generated `map/INDEX.md` as that reader and say whether it actually routes, or
whether it is a prettier list. That is the gate's stated purpose and no test
asserts it.

## Also verify

2. **`tc31` genuinely closed.** `checks.page_location_matches_content` is new and
   registered (7 checks now, 7/7). Its RED commit claims a page relocated into
   another module's directory previously passed `check`. **Attack it with a
   relocation the implementer did not choose** — its own probe proves only its own
   probe works. Confirm the check goes red, and that it is not vacuous.

3. **No absolute-count threshold survived.** The crew claims exactly one
   predicate, grepped and confirmed. Re-grep the tier path yourself. A threshold
   hidden in a sort, a slice, or a truncation counts.

4. **The one non-falsifier.** `test_top_index_lists_a_loose_module_directly_with_no_subheading`
   passed unchanged before and after; the crew named it a regression guard rather
   than a falsifier. Confirm that label is right and it is not a check that cannot
   fail (`tc29`/`tc38` — and remember a check that can *only* ever fail is the
   same defect from the other side).

## Close criteria — judged verbatim

- The top index has a **second tier** and a cold reader can pick a direction from
  it without opening module pages.
- The tier is **derived, not tuned**, with its shape reported per corpus.
- **No absolute-count threshold** anywhere in the tier logic.
- Page register stays agent-first, minimal, **pure ASCII**.
- `tc31` closed with a check.

## Specific exclusions — the tripwires, and where they sit

- `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and **must keep colliding**. The tier work
  touches `INDEX.md` generation, so **this is the check most at risk** — verify it
  directly, and check the test body is not vacuous.
- `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py` and the input
  precondition of `test_refs_lines_are_self_consistent_on_an_intact_map`.
- `entity_symbol_join`'s two independent derivations (`extract.child_sym` vs
  `checks.SourceScan`) must stay independent — `g3`'s whole gate was proving that.
- Page headers carry path + `, N lines` and **no `:<line>`**, by the human's ruling.

## What was implemented

`render.py` (`top_index`, new `module_group_key`, `_module_line`), `checks.py`
(new `page_location_matches_content`, registered in `CHECKS`),
`tests/test_code_map.py` (`TopIndexSecondTierTests`, `TopIndexPageLocationTests`),
plus evidence scripts. Inspect with `git log --oneline` and
`git diff 0e63f208..HEAD -- scripts/ tests/`.

`checks.py` sits outside the handoff's literal "render module" wording; the
handoff itself assigned `tc31` here and predicted it. Judge whether the exception
is as narrow as claimed.

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'top_index' -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

Entering this review: **1772 passed, 2 skipped, 0 failed, 0 xfailed**; `check`
**exit 0, 7/7**; selector selects **5**. `check` reads a **stale** tree at
`<root>/map` — run `build` first or the exit code means nothing. Use `python`,
**never `py`**. The `env -u ...` form is **refused** here; use `unset FORCE_COLOR
PYTHONIOENCODING && python ...`. Pipe + `PIPESTATUS` capture is also refused.

**Shell quoting:** this worktree's Bash refuses long quoted strings, so engine
verbs taking free text fail on any real message. `g3`'s reviewer solved it with
tiny wrapper scripts that read text from a file and pass a list argv via
`subprocess` — they are in `.agent-work/issue-456/evidence/` (`run_record.py`,
`run_waive.py`, `run_consolidate.py`). **Reuse them; do not rediscover them.**

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,761-page `map/` tree is staged at the
  final gate. Stage explicit paths only. Use `build --artifacts/--out` into scratch.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` clean at the end and
  report the sha256 of anything mutated and restored.
- Never force-push; do not merge to `main`.

## You are expected to overrule this handoff if you can falsify it

**Five times** on this run a crew has proven a Commander instruction wrong, every
time by **running the thing rather than reading it** — including the
`superCoolSpaceSim` error above, found by this gate's own implementer. If
something here is wrong, prove it and say so.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.render/`
- structural: `scripts/code_map/` render module — top `INDEX.md`
- capability: render an agent-lean page tree
- constraint: page register is agent-first and aggressively minimal

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g4-review-RESULT.md` with an explicit verdict
(APPROVE / APPROVE-WITH-FINDINGS / BLOCK). **Lead with the corpus-shape finding**:
the third shape you tested, how you obtained it, and whether the tier routed or
degenerated. Then your judgement on whether the index actually routes, the `tc31`
attack, the threshold re-grep, the non-falsifier label, full suite numbers,
`check` exit code after a fresh `build`, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through.

**Return thin, write fat.**
