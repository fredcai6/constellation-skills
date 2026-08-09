# g0 handoff — ADDENDUM 2 (final pass)

Pass 2 got the gate to **two items from done** and stopped cleanly at a context
trip. Read `g0-implement-ADDENDUM.md` (rulings) and `g0-implement.md` (original)
— both still govern. This adds one ruling and states exactly what is left.

## What is already done and verified — do not redo any of it

I verified all of this myself, not from the crew's word:

- `scripts/code_map/` — 8 modules. All four stage ports landed
  (`extract`, `supplement`, `render`, and the diagnostics wired behind `check`).
- `tests/test_code_map.py` — **14 tests green, 10 subtests**.
- **The end-to-end build runs.** It produced `.code-map/statements.jsonl`
  (24 MB), `supplement.json`, and a **3,635-page** tree under `map/`.
- The two `.gitignore` entries are in and correct — narrow by file, and
  `git status --ignored` confirms both stores are ignored.
- The bundling question is **resolved** as option (b): a
  `NON_INSTALLABLE_PACKAGES` declaration, with four guard tests holding every
  `scripts/` subdirectory to one declaration or the other — and the declaration
  is falsifiable (emptying it turns 3 of the 4 red).
- **No timings in any run report.** I checked all three; the constraint holds.

Sanity figures that reconcile: 112 files / 3,523 entities, against a 103-file
baseline. The +9 is exactly this gate's own new Python files. Nothing is
inflated.

## Ruling — ignore the three run reports too

`.code-map/extract_report.json`, `render_report.json`, and
`supplement_report.json` are currently **neither ignored nor committed**, so a
later `git add -A` would sweep them in by accident.

They are rebuilt on every run, exactly like the stores beside them. **Add the
three to `.gitignore` in the same narrow, one-file-per-line style** already used
for the stores — do not switch to a blanket `.code-map/` rule, and keep the
existing comment's reasoning intact.

The reports stay a build-time artifact that a reviewer reads after running the
build. That is what `g6`'s stale-tag flags will surface into later; nothing
needs them in git.

## What is left — two items, then the gate closes

Drive the same job file, `.agent-work/issue-456/g0-implementer-plan.json`.

1. **`m8-falsifiable`** — the load-bearing evidence. Delete the `.agent-work/`
   exclusion from the discovery layer, run the discovery tests, capture the RED,
   assert the mutation actually applied, restore it, capture the GREEN. Paste
   both runs.

   **Heads-up so you are not surprised, and so you assert the right number:** I
   ran this mutation myself and it turns **3 tests red**, not 2 — the CLI test
   catches it as well as the two discovery tests. An older note in the pass-1
   result says 2, from when fewer tests existed. Assert what you actually
   observe.

2. **`m9`** — closeout. The **full suite** green
   (`python -m pytest tests/ -q --color=no`), plus the **wiring grep** the
   original handoff requires: every symbol this gate added shown with a call
   site outside its own definition and outside any self-test. **State the
   count.** Zero external call sites for any new symbol is a stop condition.

   The full-suite baseline to beat, measured on this branch before the gate
   started: **1688 passed, 2 skipped, 0 failed**. It should now be higher by
   this gate's new tests and nothing should have gone red.

Then add the `.gitignore` ruling above, commit, and write your result.

## Do NOT commit the `map/` tree

It exists on disk and that is correct — building it proves the pipeline runs.
But it is staged at gate `gs`, deliberately last, so the intermediate gate diffs
stay reviewable. Leave it untracked. Same for `.code-map/`.

## Context

You are picking up a job file, not restarting work. Claim with the **same
session id `g0-impl-9febe0be`** — idempotent, not a takeover — then cold-start
from `current`.

If you trip, file the refresh-request and stop cleanly; say in your result how
much was left. The gauge is shared across the work area (`tc5`), so a reading
you see may be mine rather than yours — do not push through it, but do not read
it as proof you are nearly full either. **This is a short pass; you should have
ample room.**
