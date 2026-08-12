# Reviewer Handoff — g1 RE-REVIEW (attempt 2)

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g1` · **Role:** `reviewer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-rereview-result.md`

## Why you are here

A first reviewer BLOCKed `g1` on one confirmed finding: `scripts/spine_lifecycle.py` wrote the compiled
spine without `newline="\n"`, which `docs/agents/CREW_CONTEXT.md:43` requires on **every** write and
which produces a CRLF spine on the `windows-latest` CI job (`.github/workflows/ci.yml:23`). No test
would have caught it. The Commander verified all three facts and returned the gate for rework.

You are reviewing **the rework**, and then the gate as a whole.

## The standard — this is why the first review was worth running

C2's branch was reviewed five times; the first four each ran real commands, each answered its own
questions correctly, and each missed something different — a field that was never quoted (invisible
because **absent**), a stale session id on nine of nine gates (invisible because **ubiquitous**), that
same id used as proof of completeness, and a divergence one reviewer described accurately then scoped
away. **A review establishes that a mechanism operates and does not ask whether the value it carries is
right.** For every check: ask both questions. Treat your own green results as questions.

## What changed in the rework

Read `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-rework-result.md` **after** forming your own
view. Inspect:

```
git diff -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && git status --short
```

Claimed: the write now passes `newline="\n"`; every other write in the module was audited for the same
omission; a byte-level CRLF assertion and a source-level pin over **all** `write_text` call sites were
added, the latter with a mutated positive control; `_rollback` was collapsed onto a helper while keeping
its never-raises contract.

## What to verify — the rework

1. **Is the fix complete, or only the instance someone looked at?** The rule is "every write". Enumerate
   every write site in `scripts/spine_lifecycle.py` **by command** and state the count. An
   under-inclusive enumeration presented as complete is the exact failure this gate just had.
2. **Can the new guard actually fail?** Mutate the fix out, run the guard, confirm red, restore. A guard
   you did not falsify is a guard you did not check. (The Commander did this and saw 2 failures — confirm
   independently rather than trusting that sentence.)
3. **Is the byte-level test byte-level?** A text-mode read translates on read and would pass on Windows
   regardless — a check that cannot fail.
4. **Does `_rollback` still never raise?** It is called from an exception handler; if it can raise, a
   failed open loses its rollback and leaves a half-created worktree — the exact state g1 exists to
   prevent.

## What to verify — the gate as a whole

The first reviewer approved everything else, but **it approved a version with a defect in it**, so do not
inherit its confidence wholesale. Re-check at least: rollback really removes worktree AND branch (assert
against real `git worktree list --porcelain` / `git branch --list`); `check_distinct_real` returning
not-ok forces a rollback despite `git worktree add` exiting 0; the `origin` round-trip drives the **real**
engine; and no test's "proof" of rollback is indistinguishable from "the worktree was never created".

## Constraints the change was held to — check them against the diff

`checklist_engine.py` and `validate_spine.py` unchanged · `settings.json`, `.mcp.json`, `docs/agents/*`
untouched · `skills/**` untouched · `scripts/generate_spine.py` untouched (its identical newline omission
at line 910 is **pre-existing and deliberately out of scope** — confirm it was left alone, and do not
treat it as a g1 defect) · no `git add -A` · no push to `main`.

## Evidence

Baseline before g1: 2824 passed, 3 skipped, 1121 subtests; sweep 23.
After g1 + rework, reproduced by the Commander: **2856 passed, 3 skipped, 1121 subtests**; sweep **23**.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`. Reproduce these cheaply; spend your budget on whether the tests test what
they claim.

## Stop conditions

- You cannot reproduce a claimed result → **BLOCK** with the output.
- A constraint above is violated → **BLOCK**.
- Leave the tree unmodified when you finish. Mutating, observing and reverting is sanctioned; leaving a
  mutation behind is not.
- **Never waive.** `spine_halt` with `action=block` and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Verdict`** field
whose value is exactly `APPROVE` or `BLOCK`. Number every finding with its evidence, consequence, and
whether it is confirmed or suspected. End with the single most likely way this gate produces a green run
that is wrong, and a short **Workflow Feedback** section.
