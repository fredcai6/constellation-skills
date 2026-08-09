# Review Handoff — gate `g2`: symbol identity and page identity

Issue #456. Return a verdict — **APPROVE** or **BLOCK** — on gate `g2`. Invoke
the `constellation-reviewer` skill and drive it.

## What was implemented

Three defects, all three red-then-green, each reproducer **committed failing**
before its fix:

- **(a) D2** — `extract.py` named a nested definition from `clsstack[-1]`
  whenever any class was on the stack, so a closure inside `Class.test_x` was
  emitted as `mod:Class.<closure>` — the **method** name dropped, two same-named
  closures merged, their caller sets unioned. Fixed by collapsing both symbol
  expressions onto the enclosing scope's own symbol, plus a parallel
  enclosing-class-symbol stack so `self.x`, `cls.x` and the class-body rule spell
  the same string.
- **(b) referenced-by** — the count included the page's own module while the list
  omitted it, and nothing said what the count excluded, so the map said 3 where
  `grep` said 7 and the reader could not tell which was wrong.
- **(c) page-filename case collision** — `render.py` wrote each page as
  `key.split(":",1)[1] + ".md"`, so `Verdict` and `verdict` resolved to one file
  on a case-insensitive filesystem.

Read the implementer's account in full first:
`.agent-work/issue-456/crew-handoffs/g2-implement-RESULT-2.md`, and its
predecessor's park at `g2-implement-RESULT.md`. The fix design is at
`.agent-work/issue-456/g2-design-note.md`.

## How to inspect the diff

```
git diff dc1199b4..HEAD -- scripts/code_map/ tests/test_code_map.py
```
Six commits, three RED/GREEN pairs: `80702615`/`6d5b3131` (a),
`fd9170f5`/`103d03b5` (b), `4ea174b3`/`cdfd8213` (c). Review them as one change,
but **check each RED commit actually fails at that commit** — "committed failing"
is a claim you can verify directly, and it is the gate's own constraint.

## Close criteria — judged verbatim against these

- The 4 named D2 collisions resolve to 4 distinct symbols each carrying the
  enclosing **method** name, verified **by name** against the store.
- The class-in-function arm has a synthetic test, with its 0-occurrence status
  stated.
- Referenced-by count and list agree, and the page states what the count excludes.
- Case-only page collisions impossible **by construction**, proven with a
  synthetic pair unrelated to `Verdict`.
- The strict-xfail at `tests/test_code_map.py` is **deleted**.
- `python -m scripts.code_map check` exits **0**.
- **The FULL suite is green at this gate boundary.**

## Your primary job — attack, do not confirm

The standing lesson of this run, binding on you:

> Reproducing a falsifier its author designed proves only that *that probe*
> works. The shape that got past two reviewers at `g0` was a test whose expected
> value was computed with the **same expression** as the code under test.

The implementer says it ran its own undesigned-attack pass and added two mutants
chosen to attack its own strengthening. **That does not discharge yours.**

Specific things to attack here, because this gate's fixes are all "two things
must agree" shapes and that is exactly where same-expression agreement hides:

1. **(a)** The implementer claims the store symbol now **equals** the supplement
   key by construction. If both are now computed by the same code path, then
   `entity_symbol_join` — which it *strengthened* to a whole-symbol comparison —
   may now be a check that cannot fail. **This is the highest-risk item in the
   gate.** Attack it directly: break one derivation and confirm the join goes red.
2. **(b)** It strengthened `refs_line_self_consistent` to require a gap of
   exactly 1 or exactly 0. Confirm both arms can actually go red, and that the
   "exactly 0" arm is not vacuous on this corpus.
3. **(c)** The disambiguation must be **general**, not a special case for
   `Verdict`/`verdict`. Invent your own case-only pair with a different shape and
   confirm it survives. Also confirm the filename is derived with `hashlib`, not
   `hash()` — a hash-seed-dependent filename would break g1's determinism check,
   and if it does not break it, that check has a hole.

## Two things that must NOT have been "fixed"

- **`_make_collision_repo`'s `INDEX` collision must still collide.** It is g1's
  only cross-platform falsifier for `page-accounting`. If g2 reserved the `INDEX`
  stem, g1's check can no longer fail and that is a **BLOCK**, not a nicety.
- **No production symbol renamed.** `class Verdict` and `def verdict` in
  `scripts/run_skill_eval.py` must be untouched. The Commander ruled the fix
  belongs to the map's page naming; both implementers agreed and did not falsify
  it. Verify they actually complied.

## Scope to police

`checks.py` was touched beyond the handoff's named allowed scope. The implementer
justified it: (a) required strengthening `entity_symbol_join`, and (b) changed
what the rendered inbound line says while `checks.py` holds the one block
documenting how a page spells that line. **Judge that justification.** It claims
two g1 checks were *strengthened* and none weakened — verify that claim by
running g1's mutants, not by reading the diff.

Also verify: no `:<line>` position reintroduced into any page header (the human
ruled headers carry path + `, N lines` only), and `map/` still untracked.

## Verification commands

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

**`check` reads the tree at `<root>/map`, which goes stale** — run `build` first
or the exit code means nothing. Use `python`, **NEVER `py`** (`py` has no pytest;
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run). The `env -u ...` form is **refused** by the Bash tool in a worktree-isolated
session — `unset` is the working equivalent.

Claimed numbers: **1744 passed, 2 skipped, 0 xfailed, 0 failed** (baseline before
this gate was 1729/2/1xfail), `check` exit **0**, 6/6 checks, map tree 3761 pages
with 0 case-only folds. If your numbers differ, that is the headline of your
report.

## Explicitly NOT yours

- Do not fix the `INDEX` collision family (see above; filed as triage).
- Do not fix `supplement.walk`'s blindness to definitions inside `with`/`if`/
  `try`/`for` blocks — filed as triage, routed to a later gate.
- Do not touch the line base or page header format.
- No scope widening. Log anything else as an out-of-scope candidate.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`** — the untracked ~3,761-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate; prove `git status` is clean of stray
  edits at the end. Mutate a **copy** of the package where you can.
- Never force-push; do not merge to `main`.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.extract/` and
  `map/scripts.code_map.render/`
- structural: `scripts/code_map/` name-resolution and render modules
- capability: derive structure from source; answer cross-file questions cheaply
- constraint: checks must be able to fail
- decision: symbol identity for function-nested definitions — the enclosing
  METHOD must appear
- decision: referenced-by semantics — what the count includes vs what the list shows
- evidence: inbound-edge attribution — any page whose caller set differs from an
  independent full scan

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g2-review-RESULT.md`. **First line must be
the verdict alone:** `VERDICT: APPROVE` or `VERDICT: BLOCK`. Then, per defect:
the undesigned mutation you ran, the command, the observed exit code and output.
Then your verdict on the `entity_symbol_join` cannot-fail risk specifically, the
suite numbers, the `check` exit code, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through.

**Return thin, write fat.**
