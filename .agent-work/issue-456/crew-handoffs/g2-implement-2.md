# Implementer Handoff — gate `g2`, attempt 2 (successor)

Issue #456. You are the **successor** to `g2/implementer/attempt-1`, which parked
cleanly at a context seam with defect (a) red-committed and all three fixes
designed. **You are not starting over.**

## Read these three, in this order, before anything else

1. `.agent-work/issue-456/crew-handoffs/g2-implement-RESULT.md` — what your
   predecessor landed, measured, and designed. Status `partial`.
2. `.agent-work/issue-456/g2-design-note.md` — the full fix design for all
   three defects, including two traps that are not obvious from the code.
3. `.agent-work/issue-456/crew-handoffs/g2-implement.md` — the original handoff.
   Still authoritative for scope, exclusions, and close criteria, **with the two
   corrections below**.

Then resume the engine plan at `.agent-work/issue-456/g2-implementer-plan.json`.
Re-claim the lease `g2-implementer-attempt-1` **idempotently** — same id, NOT a
takeover, no `--force`. It was deliberately left active for you. You resume at
`m1-d2-symbol-identity`.

## Two corrections to the original handoff — my errors, found by measurement

1. **The four D2 collisions are STORE-SYMBOL merges, not four page merges.**
   My handoff called them "same-depth siblings" and implied four page-level
   merges. Only **three** are two-page merges: `supplement.walk` descends
   `node.body` only, so it never records the fourth's sibling (a `with`-nested
   def at `tests/test_context_manifest.py:771`). A crew that went hunting for
   four pairs of *pages* would find three and wrongly conclude its own
   measurement was broken. Assert against the **store**, as your predecessor did.
2. **The `env -u FORCE_COLOR -u PYTHONIOENCODING python …` command form in my
   handoff is REFUSED by the Bash tool** in a worktree-isolated session. Use
   `unset FORCE_COLOR PYTHONIOENCODING && python …` — it clears the same two
   variables. The engine's own POSIX-shell command checks still use the `env -u`
   form and are unaffected; this bites only an agent running the command by hand.

## The section my first handoff should have had: where g1's tripwires are

The exclusion "do not weaken or delete any of the six checks g1 shipped" is the
right rule, but it does not tell you **where** the tripwires sit — and two of the
three defects have one directly in the path of the obvious fix. Your predecessor
paid a full read of the g1 test file to find these. You do not have to.

**Defect (b) — two tripwires.** The obvious fix (name the page's own module in
the caller list) destroys BOTH:
- `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py`
- the input precondition of `test_refs_lines_are_self_consistent_on_an_intact_map`,
  which requires *some* page to count a module it does not name

The design note's alternative accounts for the own module's sites explicitly
(`+ N in this module`) plus a legend line stating what the count counted, and
**strengthens** `refs_line_self_consistent` (gap exactly 1 when the line accounts
for own-module sites, exactly 0 otherwise) without removing any failure mode it
has today. Take that route, or beat it and say why.

**Defect (c) — one tripwire.** `_make_collision_repo`'s `INDEX` collision is
g1's **only cross-platform falsifier** for `page-accounting`. An entity named
`INDEX` still overwrites its own module's index page — and it must **keep**
doing so. Reserving the stem would make that g1 test unable to fail, which is
the exact defect this whole run exists to stamp out. Fix the **case-only**
collision; leave the `INDEX` family alone. It is already filed as a triage
candidate, not silently swallowed.

**Defect (a) — no g1 tripwire**, but the fix must move two docstrings that
currently assert D2 is unfixed: `render.py`'s D2 docstring, and
`checks.entity_symbol_join`'s "leaf name, not the whole symbol" paragraph. A
docstring that describes a defect you just fixed is a lie in the codebase.

## What is left to do

- **(a)** The reproducer is committed FAILING at `80702615` — do not rewrite it.
  Land the fix from the design note (collapse both symbol expressions in
  `extract.py` onto `self.encl`; add a parallel enclosing-class-symbol stack so
  `self.x`, `cls.x` and the class-body name rule spell the same string;
  strengthen `checks.entity_symbol_join` from a leaf comparison to a whole-symbol
  one). Take it GREEN.
- **(b)** Not started. Reproducer first, red, committed. Then fix.
- **(c)** Not started. Reproducer first, red, committed. Then fix — deterministic
  per-name disambiguation of page filenames inside each module directory,
  `hashlib` **never** `hash()` (a hash-seed-dependent filename would fail g1's
  determinism check, correctly). Then **delete** the strict-xfail marker at
  `tests/test_code_map.py:982`; `strict` will force this — when the fix lands the
  test XPASSes and the run goes red until the marker is gone. That is by design.

The Commander ruling on (c) stands and was **not** falsified by your
predecessor: fix the map's page naming, do **not** rename `class Verdict` or
`def verdict` in `scripts/run_skill_eval.py`. If you can falsify it, say so with
evidence.

## Close criteria — unchanged

- The 4 named D2 collisions resolve to 4 distinct symbols each carrying the
  enclosing **method** name, verified by name against the store.
- The class-in-function arm has a synthetic test, with its 0-occurrence status
  stated (predecessor measured: 0 nested classes, 0 classes-in-functions,
  31 closures-in-methods).
- Referenced-by count and list agree, and the page states what the count excludes.
- Case-only page collisions impossible by construction, proven with a synthetic
  pair unrelated to `Verdict`.
- The strict-xfail at `tests/test_code_map.py:982` is **deleted** and
  `python -m scripts.code_map check` **exits 0**.
- **The FULL suite is green at this gate boundary.** It is red right now by
  design — (a)'s reproducer is committed failing. Taking it green is your job.

## Verification commands — corrected form

```
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -q --color=no
python -m scripts.code_map build && python -m scripts.code_map check
```

**`check` reads the tree at `<root>/map`, which is STALE** — your predecessor
flagged this. Run `build` first or the exit code means nothing. That is a real
trap: a stale-tree `check` can report a state that no longer exists.

Baseline before this gate was `1729 passed, 2 skipped, 1 xfailed, 0 failed`.
When you are done the xfail should be **gone**: expect `1730+ passed, 2 skipped,
0 xfailed, 0 failed`, and `check` exit **0**. If your numbers differ from that
shape, that is the headline of your report, not a footnote.

## Constraints — unchanged, and they held through attempt 1

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,635-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- Do not touch the line base or the page header format. Headers carry path +
  `, N lines` and **no** `:<line>` position, by the human's own ruling. Do not
  reintroduce positions.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Never force-push; do not merge to `main`.
- Use `python`, **NEVER `py`** — `py` has no pytest, so `py -m pytest` dies with
  "No module named pytest" and reads as a silently green run. That one already
  reached three command postconditions in another crew's plan before it was caught.

## You are expected to overrule this handoff if you can falsify it

Twice on this run a crew has proven a Commander instruction wrong, both times by
**running the thing rather than reading it**. Your predecessor found two errors
in this very handoff. If something here is wrong, prove it and say so.

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g2-implement-RESULT-2.md`. Per defect: the
reproducer, RED output + exit code, the fix, GREEN output, and the falsifier
grade (A or B). Then full suite numbers, the `check` exit code after a fresh
`build`, confirmation the xfail marker is deleted, and any out-of-scope
candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through
— your predecessor did exactly that and it cost the run almost nothing.

**Return thin, write fat.**
