# Implementer Handoff — gate `g3`: one statement schema, and the line base declared

Issue #456. Invoke the `constellation-implementer` skill, drive it to a plan,
execute the plan, return an `IMPLEMENTER_RESULT`.

## Task

Fold **kind, signature, span, docstring body, values and decorators** into the
statement-line schema and add an **extraction-window** statement. Then **declare
the line base**.

**D1 — the line base is undeclared.** The store is 0-based today and the schema
is silent about it. The renderer compensates with a `+1` at the read site, and
**that compensation is the proof of the silence**: a reader who trusted the
schema would be off by one and never know. Declare the base in the schema and
assert it with a test that **fails if the base flips**.

Doing the schema merge now **removes the supplement stage** rather than
productionizing one a later gate would deprecate. `ids.jsonl` lines become
`{id, s}` with **no `q`**. And the now-dead supplement entry must be **removed
from `.gitignore`**.

## THE ONE THING MOST LIKELY TO GO WRONG — read this before you plan

`g2` shipped `checks.entity_symbol_join`, and it is currently the map's strongest
check *because* it compares two genuinely independent derivations: the store
symbol from `extract.Extractor.child_sym` (walking `self.encl`) against the
supplement key from `supplement.walk`'s own `prefix` recursion — different
modules, no shared helper, joined only on `(file, line)`.

**You are deleting one of those two derivations.**

If you remove the supplement stage and leave that check standing on a single
source, it becomes a check that **cannot fail** — a tautology dressed as a
guard. That is the exact defect this entire run exists to stamp out, and it
would arrive here through a legitimate refactor rather than an oversight. It has
already happened twice on this run in other forms (`tc29`, `tc38`).

You have exactly two honest routes. Pick one, say which, and prove it:

1. **Re-base the join on a genuinely independent second derivation** — something
   that does not share a code path with the store symbol. Prove independence the
   way `g2`'s reviewer did: break each side in turn and show the check goes red
   for each.
2. **Remove the check, and say plainly in your result what coverage was lost and
   what now catches D2 instead.** A deleted check with a stated replacement is
   honest. A retained check that cannot fail is not.

What you may **not** do is keep it, have it pass, and not mention it.

Related: `tc34` records that `supplement.walk` descends `node.body` only, so
definitions inside `with`/`if`/`try`/`for` blocks get **no page at all** — one of
`g2`'s four D2 collision members is exactly such a case. Removing the supplement
stage may close `tc34` by construction. **If it does, say so and prove it** (a
definition inside a `with` block now gets a page); that is a real win and it
should be claimed with evidence, not assumed.

## Test mode — red before green, reproducer committed failing

This run's constraint, and it has held for three gates: the reproducer is
**committed in its failing state** before the fix. Follow the
`port-defective-then-fix` idiom used in `tests/test_mutation_floor.py`. Grade
every falsifier **A** (reproduces on real input today) or **B** (red by absence —
the negative control *is* the falsifier), and say which.

## Close criteria — judged verbatim

- One schema carries **all six** fields.
- The supplement stage is **GONE**, not deprecated.
- The line base is **declared in the schema** and asserted by a test that
  **fails if the base flips**.
- `ids.jsonl` carries **no position**, exercised by **minting two anchors and
  renaming one**.
- The dead supplement entry is **removed from `.gitignore`**.

## Name your tests so the gate's own check can select them

This gate's integrate check runs:

```
python -m pytest tests/test_code_map.py -k 'schema or line_base or ids_jsonl' -q
```

`pytest -k` matches against the full node id, so **your test class or method
names must contain `schema`, `line_base`, or `ids_jsonl`**. This is not
cosmetic: at `g2` the equivalent selector matched **zero** tests, pytest exited 5,
and the gate refused to advance in a way that looked like broken code rather than
a broken check (`tc38`). **Before you finish, run that exact selector and confirm
it selects a non-empty set that covers your work.**

## Allowed scope

`scripts/code_map/` store-schema and extractor modules, `.gitignore`, and
`tests/test_code_map.py`. Touch another `code_map` module only where the schema
merge genuinely requires it, and say so.

## Specific exclusions

- **Do not weaken or delete any check `g1` or `g2` shipped** *except* by the
  explicit, stated route above for `entity_symbol_join`. Where the tripwires sit:
  `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and **must keep colliding**;
  `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py` and the input
  precondition of `test_refs_lines_are_self_consistent_on_an_intact_map` both
  constrain anything that touches the inbound line.
- **Do not touch the page header format.** Headers carry path + `, N lines` and
  **no `:<line>` position**, by the human's own ruling. The gate's own constraint
  says *nothing committed carries a position* — that includes `ids.jsonl`.
- Do not rename symbols in non-map source files.
- No scope widening. Log anything else as an out-of-scope candidate.

## Required evidence

Per change: the reproducer, its RED output with exit code, the fix, its GREEN
output, and the falsifier grade. Plus: the line-base assertion demonstrated
failing when the base is flipped; the two-anchor mint-and-rename exercise; the
`.gitignore` diff; and **your explicit disposition of `entity_symbol_join`** with
proof.

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'schema or line_base or ids_jsonl' -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

Baseline entering this gate: **1744 passed, 2 skipped, 0 xfailed, 0 failed**, and
`check` **exit 0, 6/6**. `check` reads a **stale** tree at `<root>/map` — run
`build` first or the exit code means nothing. Use `python`, **never `py`** (`py`
has no pytest; `py -m pytest` dies with "No module named pytest" and reads as a
silently green run). The `env -u ...` form is **refused** by the Bash tool in a
worktree-isolated session — `unset FORCE_COLOR PYTHONIOENCODING && python ...` is
the working equivalent. Pipe + `PIPESTATUS` exit-code capture is also refused.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,761-page `map/` tree is staged at the
  final gate. Stage explicit paths only. Use `build --artifacts/--out` to run a
  real-corpus experiment without clobbering that tree.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` is clean of stray
  edits at the end.
- Never force-push; do not merge to `main`.

## You are expected to overrule this handoff if you can falsify it

Three times on this run a crew has proven a Commander instruction wrong, every
time by **running the thing rather than reading it** — including two errors in
the `g2` handoff, found by measurement. If something here is wrong, prove it and
say so.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.extract/`
- structural: `scripts/code_map/` store schema and extractor; `.gitignore`
- capability: derive structure from source
- constraint: nothing committed carries a position
- decision: line base — 0-based vs 1-based, **declared not implied**; durable,
  every consumer inherits it
- decision: statement-line schema shape
- evidence: extraction correctness

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g3-implement-RESULT.md`. Per change: the
reproducer, RED output + exit code, the fix, GREEN output, falsifier grade. Then
full suite numbers, the `check` exit code after a fresh `build`, the output of
the gate's own `-k` selector, your disposition of `entity_symbol_join` with
proof, whether `tc34` closed, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through
— two crews have done exactly that and it cost the run almost nothing.

**Return thin, write fat.**
