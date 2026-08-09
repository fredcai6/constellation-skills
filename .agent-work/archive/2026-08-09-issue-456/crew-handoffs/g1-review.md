# Review Handoff — gate `g1`: invariants that cannot move

Issue #456. Return a verdict — **APPROVE** or **BLOCK** — on gate `g1`. Invoke
the `constellation-reviewer` skill and drive it.

## What was implemented

`scripts/code_map/checks.py` was **rewritten, not ported**. It used to print and
assert nothing; `run()` ended in a literal `return 0` whose own docstring
admitted it gated nothing, so a completely broken map passed. Now: a `CHECKS`
registry over a `MapUnderCheck` that reads the stores and pages directly,
`run()` returns 1 on any failure, and a missing tree or store is a **failure**
rather than a skip. **Six checks ship.**

Read the implementer's own account in full first:
`.agent-work/issue-456/crew-handoffs/g1-implement-RESULT.md`.

## How to inspect the diff

```
git diff dbb8b6e3..HEAD -- scripts/code_map/checks.py tests/test_code_map.py
```
Two commits: `ba8e78aa` (predecessor crew, parked at a context seam) and
`44eeb740` (successor crew, finished on its plan). Review them as one change.

## Close criteria — the gate is judged against these, verbatim

> every check in this gate FAILS under a deliberate mutation of the property it
> guards, with a nonzero exit, demonstrated in the evidence; a double build is
> byte-identical; no check in this gate depends on a corpus count or a page's
> rendered shape

## Your primary job — attack, do not confirm

**This gate's entire subject is checks that can fail.** A check that cannot go
red is not a check, and this run has already shipped that defect twice at `g0`
and had to be blocked twice to catch it.

The lesson, and it is binding on you:

> Reproducing a falsifier its author designed proves only that *that probe*
> works. The shape that got past two reviewers was a test whose expected value
> was computed with the **same expression** as the code under test, so it could
> only ever agree with it.

So: for **each of the six checks**, devise and run a mutation **the implementer
did not design it for**, and report what you saw. The implementer says it
already did an undesigned-attack pass — **that does not discharge yours**, for
exactly the reason above. Look particularly for:

- a check whose expected value is derived from the same expression, structure, or
  code path as the thing it checks;
- a check that would pass on an **empty** or **absent** input (vacuity);
- a check that iterates a set built by the code under test rather than an
  independent enumeration (wrong iteration set);
- a check that asserts something true by construction rather than by measurement.

If a check survives an attack it should have caught, that is a **BLOCK**.

## Specific things to verify by running, not by reading

1. **Nonzero exit.** `check` must exit non-zero when an invariant fails. Confirm
   the exit code yourself.
2. **`check` currently exits 1 on this repository — and that is CORRECT**, until
   a later gate fixes the filename collision. Confirm it exits 1 for the *right*
   reason and not for an unrelated one.
3. **Determinism** is measured across two **separate processes** with
   `PYTHONHASHSEED` 0 vs 1. Verify that claim — a same-process comparison shares
   one seed and structurally cannot see this bug class. If it is actually
   same-process, that is a BLOCK.
4. **The RED-by-design invariant.** `pages - 1 - modules` = 3535 vs
   `entity_pages` = 3536 is asserted and marked xfail, gated on
   `CASE_INSENSITIVE_FS`. The implementer found — correctly, overruling the
   Commander's handoff — that a *bare* `strict=True` would XPASS on a
   case-sensitive filesystem and turn CI red on Linux. **Verify that reasoning
   and the guard.** The marker must still be `strict` where it applies, so the
   later gate cannot land the fix and leave the marker on.
5. **Suite numbers**, in a cleared environment: expected `1729 passed, 2 skipped,
   1 xfailed`. Baseline before this gate was `1709 / 2 / 0`. If your number
   differs, that is the headline of your report.

## Scope boundary you must police

`g1` carries only invariants that **survive a later render change**. Absolute
corpus-count thresholds and render-shape baselines belong to a later gate.

**But read the distinction carefully** — a *baseline* pins a number to a
remembered constant (out of scope); a *relational invariant* requires two
independently-derived numbers to agree and holds at any corpus size (in scope).
The implementer was asked to state its own rule for telling these apart. **Find
that rule, quote it, and judge it** — every later gate's thresholds will be
placed by it, so a vague rule here is a real finding.

## Explicitly NOT yours

- Do **not** rename anything to fix the collision — a later gate owns it.
- Do **not** "fix" `entity_pages` by counting the tree again. The root is the
  `sizes` structure, which feeds three fields; a second tree-count would just
  manufacture a second self-agreeing field.
- Do **not** touch the line base or the page header format — both settled
  elsewhere, the header format by the human's own ruling.
- No scope widening. Log anything else as an out-of-scope candidate.

## Constraints

- Stdlib only. No timings in any run report (it would break the determinism diff).
- **Do NOT `git add -A`** — the untracked ~3,635-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` is clean on
  `scripts/` and `tests/` at the end. Mutate a **copy** of the package where you
  can, as the implementer did.
- Never force-push; do not merge to `main`.

## Environment traps — all confirmed real on this run

`FORCE_COLOR=3` and possibly `PYTHONIOENCODING` are exported. Use
`env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest ...`. **Use `python`,
NEVER `py`** — `py` has no pytest, so `py -m pytest` dies with "No module named
pytest" and reads as a silently green run. That one already reached three
command postconditions in another crew's plan before it was caught.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.checks/`
- structural: `scripts/code_map/` checks module; `tests/test_code_map.py`
- constraint: checks must be able to fail; the run report carries no timings
- decision: what counts as a move-invariant check vs a baseline

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g1-review-RESULT.md`. **First line must be
the verdict alone:** `VERDICT: APPROVE` or `VERDICT: BLOCK`. Then, per check: the
undesigned mutation you ran, the command, the observed exit code and output. Then
the suite numbers, your judgement on the move-invariant-vs-baseline rule, your
judgement on the xfail guard, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through.

**Return thin, write fat.**
