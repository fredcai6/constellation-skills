# Reviewer Handoff — gate `g3`: one statement schema, and the line base declared

Issue #456. Invoke the `constellation-reviewer` skill, drive it to a review plan,
execute it, return a `REVIEW_RESULT` with an explicit verdict.

## THE ONE THING THIS REVIEW EXISTS FOR — read before you plan

The gate's whole named risk was this: `g2` shipped `checks.entity_symbol_join`,
the map's strongest check, and it was strong *because* it compared two genuinely
independent derivations of a qualified name — `extract.Extractor.child_sym`
(walking `self.encl`) against `supplement.walk`'s own `prefix` recursion.
Different modules, no shared helper, joined only on `(file, line)`.

**`g3` deleted one of those two derivations.**

The implementer says it confirmed the trap was real before choosing: with the
supplement gone, the check collapses to identity — a page is keyed by the store
symbol and the check compared the page title against the store symbol at that
position, so both sides become one derivation and the check **passes forever**.
It says it then took route 1: introduced `checks.SourceScan`, which derives
qualified names **from the source text itself**, and re-based the naming arm of
`entity_symbol_join` onto it. It claims that is a real second derivation, not a
second pass over the same machinery, and it added a test asserting `checks.py`
borrows no naming code from `extract.py`.

**The Commander has NOT independently attacked that claim.** I verified the
numbers (suite, build, `check`, tree cleanliness) by running them. I did not
verify independence. That is your first and most important job:

> **Break each side in turn and show the check goes RED for each.** Mutate the
> extractor's naming so it flattens an enclosing chain — the check must fail.
> Then, separately, mutate `SourceScan`'s derivation — the check must fail again.
> If breaking either side leaves the check green, the independence claim is false
> and this gate does not close.

The standing lesson from this run applies with full force: **reproducing a
falsifier its author designed proves only that that probe works.** The
implementer's own independence tests are its chosen probes. Attack the check with
mutations **it did not choose**. `g2`'s reviewer did exactly this and it is why
`g2` closed honestly.

Note the shape of what you are hunting. A check that **cannot fail** and a check
that **can only ever fail** are the same defect — both carry zero information
(`tc29`, `tc38`). Whichever side you are on, ask: *would this output differ in a
defective world?*

## Three more things to verify, in order

2. **Did `tc34` actually close?** `supplement.walk` descended `node.body` only, so
   definitions inside `with` / `if` / `try` / `for` blocks got **no page at all**.
   The reproducer was committed RED at `4246e87d`. The implementer claims removing
   the stage closed it by construction and that 8 definitions the old recursion
   could never see now have pages. **Verify it directly**: a definition inside a
   `with` block must now get a page. Confirm the count independently rather than
   taking 8 on trust.

3. **Does `ids.jsonl` carry no position under a code move?** The gate's constraint
   is that nothing committed carries a position. Mint two anchors, move the code
   so line numbers shift, and confirm the ids are unchanged. The implementer's own
   exercise renames one; **you should move one**, which is the mutation it did not
   choose.

4. **Judge the "extraction-window statement" against intent.** The phrase is named
   in this gate's spec and defined **nowhere** in the run. The implementer invented
   a definition and flagged that it had done so — which is the honest move, and it
   means the design is unratified. Say whether what it built is what the constraint
   *wanted*: does the extraction-window statement let a reader know what the
   extractor could and could not see for that file? If it is decorative, say so.
   This is `tc40`; your judgement is what settles it.

## What was implemented

Five commits, red before green throughout:

- `91da2500` RED / `0782ff2b` GREEN — the schema can say what a value is
- `4246e87d` RED — the `tc34` reproducer (definition inside a `with` block)
- `0d821d6f` GREEN — supplement removed, `entity_symbol_join` re-based
- `70b60555` RED / `68f4a2eb` GREEN — `ids.jsonl`

Inspect with `git log --oneline` and `git diff 91da2500~1..HEAD -- scripts/ tests/ .gitignore`.

## Close criteria — judged verbatim

- One schema carries **all six** fields (kind, signature, span, doc body,
  decorators, bases on contains; annotation, value, form on declares).
- The supplement stage is **GONE**, not deprecated — dropped from `cli.py` and
  `__init__.py`, file deleted.
- The line base is **declared in the schema** and asserted by a test that **fails
  if the base flips**. Flip it yourself and confirm the test goes red.
- `ids.jsonl` carries **no position**.
- The dead supplement entry is **removed from `.gitignore`**.

## Specific exclusions — the tripwires, and where they sit

- `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and **must keep colliding**. An entity named
  `INDEX` must still land on its module's index page.
- `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py` and the input
  precondition of `test_refs_lines_are_self_consistent_on_an_intact_map` both
  constrain anything touching the inbound line.
- Page headers carry path + `, N lines` and **no `:<line>`**, by the human's own
  ruling. Do not propose reinstating a position.
- No check `g1` or `g2` shipped may be weakened or deleted, except by the stated
  re-basing route for `entity_symbol_join`.

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'schema or line_base or ids_jsonl' -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

Entering this review: **1767 passed, 2 skipped, 0 failed, 0 xfailed**, `check`
**exit 0, 6/6**, gate selector selects **21 tests**. `check` reads a **stale**
tree at `<root>/map` — run `build` first or the exit code means nothing. Use
`python`, **never `py`** (`py -m pytest` dies with "No module named pytest" and
reads as a silently green run). The `env -u ...` form is **refused** by the Bash
tool in a worktree-isolated session — `unset FORCE_COLOR PYTHONIOENCODING &&
python ...` is the working equivalent. Pipe + `PIPESTATUS` capture is also refused.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,761-page `map/` tree is staged at the
  final gate. Stage explicit paths only. Use `build --artifacts/--out` for a
  real-corpus experiment without clobbering that tree.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` is clean of stray
  edits at the end. Report the sha256 of any file you mutated and restored.
- Never force-push; do not merge to `main`.

## You are expected to overrule this handoff if you can falsify it

Three times on this run a crew has proven a Commander instruction wrong, every
time by **running the thing rather than reading it** — including two errors in the
`g2` handoff, found by measurement. If something here is wrong, prove it and say so.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.extract/`
- structural: `scripts/code_map/` store schema and extractor; `.gitignore`
- capability: derive structure from source
- constraint: nothing committed carries a position
- decision: line base — 0-based vs 1-based, **declared not implied**
- decision: statement-line schema shape
- evidence: extraction correctness

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g3-review-RESULT.md` with an explicit
verdict (APPROVE / APPROVE-WITH-FINDINGS / BLOCK). Lead with your **independence
finding** — the exact mutation you applied to each side and the exact red output
it produced, or the fact that it stayed green. Then `tc34`, then `ids.jsonl` under
a move, then your judgement on the extraction-window statement. Then full suite
numbers, `check` exit code after a fresh `build`, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through
— three crews have done exactly that and it cost the run almost nothing.

**Return thin, write fat.**
