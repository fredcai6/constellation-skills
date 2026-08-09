# Implementer Handoff — gate `g1`: invariants that cannot move

Issue #456. `g0` is closed: the code map runs behind a real entrypoint
(`scripts/code_map/`, CLI `extract` → `render` → `check`). `g1` is the gate that
makes the map *checkable*.

Invoke the `constellation-implementer` skill and drive it.

## Task

**REWRITE `scripts/code_map/checks.py`. Do not port it.**

Read it first — all 211 lines. Every function in it `print()`s and asserts
nothing, and `run()` ends with a literal `return 0` whose own docstring admits
"Always returns 0 -- these do not gate anything until g1 rewrites them." So a
completely broken map passes `check` today. They are measurements wearing a
suite's clothes. That is what you are here to end.

## Protected intent

The map exists so an agent can orient in this repo without reading it. A check
here is worth having only if it would **catch a map that lies**. The gate's
subject is checks that **can fail** — so every check you write must be
demonstrated failing.

## What belongs in this gate — and what does not

`g1` carries ONLY invariants that **survive a later render change**. Gates `g2`
(symbol collisions), `g3` (line base), `g4` (schema/top index), `g5`
(determinism of caller split), `g6`–`g8` all still move the map's *shape*. A
check pinned to today's shape would go red for the wrong reason at every one of
them, and would be deleted rather than believed.

**IN scope — three families:**

1. **Nonzero exit on failure.** `check` must exit non-zero when any invariant
   fails. Prove it: run `check` against a deliberately broken map and show the
   exit code.
2. **Determinism.** Build twice from unchanged source; the two page trees must be
   **byte-identical**, and any non-empty diff is the failure. Note the run report
   carries **no timings** precisely so this diff can cover it — do not add any.
3. **Structural assertions provable by deliberate mutation.** Specifically:
   - a page's **caller set matches an independent full scan** — compute the
     inbound edges a second way and require agreement;
   - a page's **referenced-by count agrees with its own list**.

**OUT of scope — belongs to `gB`, after the last gate that moves the numbers:**
- absolute-count thresholds ("103 modules", "3411 entities")
- render-shape baselines (a page's rendered text, header format, section order)

**Read that boundary carefully — it is a distinction between two things that
both mention counts.** A *baseline* pins a count to a remembered constant and
belongs to `gB`. A *relational invariant* asserts two independently-derived
numbers must agree with each other, holds at any corpus size, and belongs
**here**. The next section is exactly such an invariant, and it is in scope.

## The invariant that is RED today — read this in full

The run report already contains a self-contradiction and **nothing asserts it**:

```
pages - 1 - modules   =  3648 - 1 - 112  =  3535
entity_pages          =  3536
```

They differ by exactly **one** page: `map/scripts.run_skill_eval/Verdict.md` and
`verdict.md` are two distinct entity keys that derive the same filename on a
case-insensitive filesystem, so one silently overwrites the other. The map
claims 3536 entity pages and has 3535.

**Assert it.** This is the single best check in the gate: it is relational (no
constant), it is derived two independent ways, and it catches a **real defect
that exists right now** — which is far stronger evidence that a check can fail
than any synthetic mutation.

**But `g1` does NOT fix it.** The rename that resolves the collision is `g2`'s,
by ruling. So the assertion arrives RED, and the full suite must still be green
at this gate's boundary. Resolve that with the **port-defective-then-fix**
mechanism this plan already adopted (see `tests/test_mutation_floor.py` for the
house idiom):

- assert the invariant;
- mark it **`xfail(strict=True)`** with a reason naming the `Verdict`/`verdict`
  collision and `g2` as its owner;
- **strict** matters: when `g2` lands the rename the test XPASSes, `strict` turns
  that into a failure, and `g2` is forced to remove the marker. The defect cannot
  be silently left behind, and the check cannot be silently left disabled.

If you see a better mechanism with those two properties, use it and say why.

Also fold in **`tc26`**: the page count is `rglob("*.md")`, which counts a file
that was created and never written, so a zero-byte page is invisible. Your
structural checks should notice an empty page.

## Explicitly NOT yours

- **Do NOT rename anything to fix the collision** — that is `g2`.
- **Do NOT "fix" `entity_pages` by counting the tree again.** `tc24` corrects
  `tc18`: the root is the `sizes` structure, which feeds **three** fields, and a
  second tree-count would just manufacture a second tautological field. `g1`
  *asserts* the disagreement; it does not paper over it.
- **Do NOT touch the line base** (`g3`) or the header format (`g0`, settled: path
  + `, N lines`, no line number — the human ruled it).
- No corpus-count thresholds, no render-shape baselines (`gB`).

## The one rule that outranks the rest

**A check that cannot go red is not a check.** For **every** check you write,
mutate the property it guards and show it failing with a nonzero exit. Put the
mutation, the command, and the observed output in your result.

And the lesson this run has already paid for twice, at `g0`:

> Reproducing a falsifier *you* designed proves only that your own probe works.
> After you have shown each check goes red under your chosen mutation, **attack
> it once more with a mutation you did not design for it** — the shape that
> caught us was a check whose expected value was computed with the *same
> expression* as the code under test, so it could only ever agree with it.

If any check of yours survives an attack it should have caught, say so plainly
rather than quietly narrowing what it claims.

## Constraints

- **Stdlib only.** No new dependencies.
- **No timings in any run report** (it would break the determinism diff).
- **Full suite green at the boundary. Current baseline: `1709 passed, 2 skipped,
  0 failed`.** Any red below that line is yours. `xfail` is not red.
- **Do NOT `git add -A`.** The untracked ~3,635-page `map/` tree is staged at the
  final gate, deliberately. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**
  corpora. Do not write to them.
- Work only in the worktree
  `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; `git status` clean on `scripts/` and
  `tests/` except your intended changes.

## Environment traps — all three confirmed real on this run

- `FORCE_COLOR=3` is exported and defeats a FAILED-line regex in
  `tests/test_mutation_floor.py:255`. Pass `--color=no`, or clear the variable.
- `PYTHONIOENCODING` may be exported; clear it for an honest suite number.
- **Use `python`, NEVER `py`.** `py` has no pytest, so `py -m pytest` dies with
  "No module named pytest" and reads as a silently green run. That one already
  reached three command postconditions in another crew's plan before it was caught.

Belt and braces: `env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest ...`

## Verification commands (this gate's close criteria)

```
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/ -q
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/test_code_map.py -k 'determinism or invariant' -q
```

Close criteria, verbatim: *every check in this gate FAILS under a deliberate
mutation of the property it guards, with a nonzero exit, demonstrated in the
evidence; a double build is byte-identical; no check in this gate depends on a
corpus count or a page's rendered shape.*

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.checks/` and
  `map/scripts.code_map.render/`.
- structural: `scripts/code_map/` checks module; `tests/test_code_map.py`
- capability: derive structure from source
- constraint: checks must be able to fail; the run report carries no timings, so
  the determinism diff can cover it
- decision: **what counts as a move-invariant check vs a baseline** — this
  governs where every later threshold lands, so state your rule explicitly in the
  result; later gates will be held to it.
- evidence: determinism — any non-empty diff on unchanged source;
  inbound-edge attribution — any page whose caller set differs from an
  independent full scan

## Authority

Commit with **explicit paths**. Push is pre-approved for this branch
(`issue-456/code-map`). **Do not merge to `main`. Never force-push.**

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g1-implement-RESULT.md`: each check, the
mutation that makes it red, the command and observed exit code, the
determinism-diff evidence, your move-invariant-vs-baseline rule, the full-suite
number, the treatment of the RED invariant, and anything you found that I did
not ask about.

**Return thin, write fat.**
