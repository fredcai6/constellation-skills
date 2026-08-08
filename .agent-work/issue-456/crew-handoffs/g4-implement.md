# Implementer Handoff — gate `g4`: the top index must ROUTE, not list

Issue #456. Invoke the `constellation-implementer` skill, drive it to a plan,
execute the plan, return an `IMPLEMENTER_RESULT`.

## Task

**A flat list of every module is not a routing surface.** The trial agent read 60
lines of today's `map/INDEX.md` and learned nothing — it could not tell where to
go next. Add a **second tier** so the top index *routes*: a reader arriving cold
should be able to pick a direction from the top page without opening 111 module
pages to find out which one matters.

The failure is not aesthetic. A list answers "what exists". A routing surface
answers "where do I go". Design for the second question.

## THE ONE THING MOST LIKELY TO GO WRONG — read this before you plan

**This repository's corpus shape will lie to you.** About **75% of this repo's
entities are test code**. A tier that keys off `src/` — or off any convention
this repo happens to follow — will look excellent here and fail on the next
corpus. Critic F9 named this before the gate opened.

So: **do not tune the tier to this repo.** Derive it from something the corpus
itself supplies. Then prove it on a corpus with a different shape.

Two read-only corpora are available for exactly this:
- `C:/Programs/f1Brainz`
- `C:/Programs/superCoolSpaceSim`

**READ-ONLY. Never write to either.** Use `build --artifacts/--out` pointed at a
scratch directory to index them without touching this repo's `map/` tree. If your
tier produces a useful routing surface here and a degenerate one there (one giant
bucket, or 111 buckets of one), you have tuned to this repo and the gate is not
met. **Report the tier's shape on all three corpora**, not just this one.

## Constraints that bind the design

- **No absolute-count thresholds.** This run changes the corpus it measures, so
  "more than 20 modules" or "at least 5 entities" bakes in today's numbers and
  rots by `gs`. Critic F4. Anything you need must be **relative or derived**.
- **Page register: agent-first, aggressively minimal, template text pure ASCII.**
  The reader is an agent with a context budget, not a human browsing. No
  decoration, no prose padding, no box-drawing characters.
- **Do not touch the page header format.** Headers carry path + `, N lines` and
  **no `:<line>` position**, by the human's own ruling.

## `tc31` — this gate owns it

**Nothing currently ties a page's location to its content.** A page could be
written into the wrong directory and every check would still pass. You are about
to add a second tier, which means you are about to add *more* location structure
— so this gate is where that gap either closes or gets twice as wide.

Either close it (a check that fails when a page's location disagrees with what
the page says it is) or state plainly why the new tier does not widen it.
**Silence on `tc31` is a `BLOCK`.**

## Test mode — red before green, reproducer committed failing

This run's constraint, and it has held for four gates: the reproducer is
**committed in its failing state** before the fix. Grade every falsifier **A**
(reproduces on real input today) or **B** (red by absence). Say which.

**A check that cannot fail and a check that can only ever fail are the same
defect** — both carry zero information. Before you finish, ask of every check you
add: *would this output differ in a defective world?* Two gates on this run
shipped a check that could not (`tc29`, `tc38`); both were caught late and both
cost a round trip.

## Name your tests so the gate's own check can select them

This gate's integrate check runs:

```
python -m pytest tests/test_code_map.py -k 'top_index' -q
```

`pytest -k` matches the full node id, so **your test class or method names must
contain `top_index`**. This is not cosmetic: at `g2` the equivalent selector
matched **zero** tests, pytest exited 5, and the gate refused to advance in a way
that looked like broken code rather than a broken check (`tc38`). **Before you
finish, run that exact selector by hand and confirm it selects a non-empty set
that covers your work.** At `g3` this instruction was followed and it worked
(21 tests).

## Close criteria — judged verbatim

- The top index has a **second tier** and a cold reader can pick a direction from
  it without opening module pages.
- The tier is **derived, not tuned** — demonstrated on `f1Brainz` and
  `superCoolSpaceSim` as well as this repo, with the shape reported for each.
- **No absolute-count threshold** anywhere in the tier logic.
- The page register stays agent-first, minimal, pure ASCII.
- `tc31` is either closed with a check or explicitly addressed.

## Allowed scope

`scripts/code_map/` render module (top `INDEX.md`) and `tests/test_code_map.py`.
Touch another `code_map` module only where the tier genuinely requires it, and
say so.

## Specific exclusions — the tripwires, and where they sit

- **Do not weaken or delete any check `g1`, `g2`, or `g3` shipped.** Where they sit:
  - `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
    falsifier for `page-accounting` and **must keep colliding** — an entity named
    `INDEX` must still land on its module's index page. **Your new tier will touch
    `INDEX.md` generation; this is the check most at risk from your work.**
  - `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py` and the input
    precondition of `test_refs_lines_are_self_consistent_on_an_intact_map`
    constrain anything touching the inbound line.
  - `entity_symbol_join` compares two genuinely independent derivations
    (`extract.child_sym` vs `checks.SourceScan`). Do not let the tier collapse
    them onto one code path.
- Do not rename symbols in non-map source files.
- No scope widening. Log anything else as an out-of-scope candidate.

## Required evidence

Per change: the reproducer, its RED output with exit code, the fix, its GREEN
output, and the falsifier grade. Plus: **the tier's shape on all three corpora**,
your `tc31` disposition, and proof that no absolute-count threshold survives in
the tier logic.

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'top_index' -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

Baseline entering this gate: **1767 passed, 2 skipped, 0 failed, 0 xfailed**, and
`check` **exit 0, 6/6**. `check` reads a **stale** tree at `<root>/map` — run
`build` first or the exit code means nothing. Use `python`, **never `py`** (`py -m
pytest` dies with "No module named pytest" and reads as a silently green run). The
`env -u ...` form is **refused** by the Bash tool in a worktree-isolated session —
`unset FORCE_COLOR PYTHONIOENCODING && python ...` is the working equivalent. Pipe
+ `PIPESTATUS` exit-code capture is also refused.

**Shell quoting:** this worktree's Bash refuses long quoted strings, so engine
verbs taking free text (`--why`, `--reason`, `--finding`) fail on any real
message. `g3`'s reviewer solved it with tiny wrapper scripts that read the text
from a file and pass a list argv via `subprocess`. **Adopt that pattern
immediately** rather than rediscovering it — it is filed as `tc43`.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,761-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` is clean of stray
  edits at the end, and report the sha256 of anything you mutated and restored.
- Never force-push; do not merge to `main`.

## You are expected to overrule this handoff if you can falsify it

Four times on this run a crew has proven a Commander instruction wrong, every time
by **running the thing rather than reading it** — including two errors in the `g2`
handoff, found by measurement, and an overclaimed docstring at `g3` the Commander
had missed. If something here is wrong, prove it and say so.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.render/`
- structural: `scripts/code_map/` render module — top `INDEX.md`
- capability: render an agent-lean page tree
- constraint: page register is agent-first and aggressively minimal

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g4-implement-RESULT.md`. Per change: the
reproducer, RED output + exit code, the fix, GREEN output, falsifier grade. Then
full suite numbers, the `check` exit code after a fresh `build`, the output of the
gate's own `-k top_index` selector, the tier's shape on all three corpora, your
`tc31` disposition, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through
— four crews have done exactly that and it cost the run almost nothing.

**Return thin, write fat.**
