# Reviewer Handoff — g1: open

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g1` · **Role:** `reviewer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-reviewer-result.md`

## The review standard this wave inherits — read it twice, it is why you are here

C2's branch was reviewed **five** times. The first four each ran real commands, each answered its own
questions correctly, and each missed something different:

- a field that was never quoted — invisible because it was **absent**;
- a stale session id present on nine of nine gates — invisible because it was **ubiquitous**;
- that same stale id written into a review's own evidence line **as proof of completeness**;
- a divergence one reviewer saw, described accurately, and then **scoped away**.

One sentence: **a review establishes that a mechanism operates and does not ask whether the value it
carries is right.** Absence and ubiquity both read as correct.

The fifth review broke the pattern by treating its own green results as questions. So, **for every check
you run, ask two questions: does this mechanism work, and is the value it carries correct?** A green
result is the beginning of a question, not the end of one.

Re-run every command the implementer pasted. **A claim you cannot reproduce is a defect, not an accepted
fact.** Your judgment rests on what you observed, never on what the report asserted.

## What was implemented

`scripts/spine_lifecycle.py` (270 lines, new) and `tests/test_spine_lifecycle.py` (460 lines, new) —
the lifecycle module's pure helpers and `open_work`. Both files are **staged but not committed**, so they
appear in `git diff --cached` and in `git status`, not in a bare `git diff`.

Inspect with:

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && git diff --cached -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py
```

The implementer's own account is at
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-implementer-result.md`. Read it **after** you have
formed your own view of the diff, not before.

## Task statement it was held to

`LIFECYCLE_CONTRACT.md` §2 and §3 are the specification — read them, and §1b for why four decisions are
shaped the way they are. The handoff it worked from is `g1-implementer-handoff.md`.

`open_work` must, in order: validate the work id (reusing `run_crew`'s validator, never a second one);
refuse an occupied worktree path; refuse a work id whose spine carries an `engine_session` with
`status == "active"`; `git worktree add`; scaffold via `init_work_area`; compile via `generate_spine`
**imported, never re-implemented**; inject a top-level `origin` block and **re-validate**; self-verify
with `verify_worktree_isolation.check_distinct_real` **in-process**; return the crew-binding values.

**Any failure at or after the worktree add removes the worktree AND deletes the branch this call
created**, scoped to what this call created, then refuses legibly.

## Close criteria — verify each, do not take them on trust

1. Occupied-path refusal, by name, with a VIOLATING fixture.
2. Active-`engine_session` refusal, by name, with a VIOLATING fixture and a `"released"` INNOCENT case.
3. A late failure after `git worktree add` leaves **no worktree and no branch** — asserted against real
   `git worktree list --porcelain` and `git branch --list` output, not against a string the code under
   test produced.
4. `check_distinct_real` returning not-ok forces a rollback **even though `git worktree add` exited 0**.
5. Rollback is **scoped**: a pre-existing unrelated worktree survives a failed open of a different id.
6. The `origin` block survives a real `claim → start → attest → advance` drive byte-identical.
7. The pure helpers take `today`/`wt_root` as parameters and read no clock or host path inside.
8. `worktree_path_for("epic-559/c3-lifecycle", wt_root=<default>)` reproduces this run's **real** worktree.
9. Suite green; sweep exactly 23.

## Specific things worth your scepticism

Offered so you do not spend your budget rediscovering the obvious. **Not** a list to work through, and
**not** a hint that these are the real problems — the real problem is probably somewhere else.

- **Every fixture that "proves" rollback is a fixture that also wrote the rollback's inputs.** Does any
  test distinguish "the worktree was removed" from "the worktree was never created"? Those look
  identical in a final-state assertion, and only one of them is the property.
- Point 6 is the load-bearing plan measurement. Does that test drive the **real engine**, or does it
  simulate a drive? If the latter, it proves nothing about the engine.
- Point 8 passes today on this host. Would it pass on a host whose checkout is named differently — and
  if it derives the expected value from the same function it is testing, does it assert anything at all?
- `_compile_spine` claims to reuse `generate_spine` rather than re-implement it. Is that true of every
  layer `generate_spine.main()` runs, or only some of them? A layer quietly skipped is a check that
  stopped existing.
- The refusal messages: do they name the offending thing, or do they merely refuse? "Refuse with a
  legible reason" is a close criterion, not a nicety.
- Does anything in the module read a clock, a host path, or the real repo outside the one test that is
  explicitly allowed to?

## Allowed scope for your review

`scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py`, `map/INDEX.md` (regenerated). Everything
else in the tree is **out of scope for this gate** — if you find something wrong there, record it as an
out-of-scope finding rather than blocking g1 on it.

## Constraints the change was held to

`checklist_engine.py`'s on-disk format unchanged · `validate_spine.py` unchanged · `settings.json`,
`.mcp.json`, `docs/agents/*` untouched · `skills/**` untouched · no `git add -A` · no push to `main`.
**Check these against the diff yourself** — a constraint nobody verified is a constraint that was not
enforced.

## Evidence the implementer produced

Baseline before the change: **2824 passed, 3 skipped, 1121 subtests**; sweep **23**.
Claimed after: 28 new tests; suite **2852 passed, 3 skipped, 1121 subtests**; sweep **23**.

The Commander independently reproduced all three of those numbers. **They are not the interesting
question** — reproduce them cheaply and spend your budget on whether the tests test what they claim.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`.

**A guard needs a violating case.** Where a test only exercises the happy path, say so by name — that is
a finding, not a style note. Where you doubt a guard can fail, **mutate the code and prove it**: break
the guard, run the test, confirm it goes red, and put it back. A guard you did not falsify is a guard you
did not check.

## Stop conditions

- You cannot reproduce a claimed result → that is a **BLOCK**, with the output.
- A constraint above is violated → **BLOCK**.
- You would need to change source to review it → do not; describe the experiment instead. (Mutating,
  observing and reverting a guard is sanctioned; leaving the tree modified is not.)
- **Never waive.** A crew cannot waive its own bound spine check.

## Return format

Write the result artifact at the path above **before ending your turn** — that write is the delivery. It
must carry a **`Verdict`** field whose value is exactly `APPROVE` or `BLOCK`.

Number every finding: what is wrong, the **evidence** (a command and its output, or a file and line),
the consequence if it ships, and whether it is confirmed or a suspicion. Separate confirmed from
suspected — a suspicion labelled as one is useful; a suspicion dressed as a finding costs a round.

End with **the single most likely way this gate produces a green run that is wrong**, and a short
**Workflow Feedback** section.
