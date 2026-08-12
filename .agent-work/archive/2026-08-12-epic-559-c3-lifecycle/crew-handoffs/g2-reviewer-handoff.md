# Reviewer Handoff — g2: close

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g2` · **Role:** `reviewer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g2-reviewer-result.md`

## The review standard this wave inherits — read it twice

C2's branch was reviewed **five** times. The first four each ran real commands, each answered its own
questions correctly, and each missed something different:

- a field that was never quoted — invisible because it was **absent**;
- a stale session id present on nine of nine gates — invisible because it was **ubiquitous**;
- that same stale id written into a review's own evidence line **as proof of completeness**;
- a divergence one reviewer saw, described accurately, and then **scoped away**.

One sentence: **a review establishes that a mechanism operates and does not ask whether the value it
carries is right.** Absence and ubiquity both read as correct. The fifth review broke the pattern by
treating its own green results as questions.

So for every check: **does this mechanism work, and is the value it carries correct?** Re-run every
command the implementer pasted. **A claim you cannot reproduce is a defect, not an accepted fact.**

This is not hypothetical here. `g1` of this same run shipped, was reviewed, and the first reviewer found
a write missing `newline="\n"` that every test passed over. Assume something equivalent is in this diff.

## What was implemented

`closeout_refusal` (pure) and `close_work` (impure) added to `scripts/spine_lifecycle.py`, with tests in
`tests/test_spine_lifecycle.py`. Both files are tracked, so:

```
git diff -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py
```

The implementer's account is at `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g2-implementer-result.md`.
Read it **after** you have formed your own view.

## The specification it was held to

`LIFECYCLE_CONTRACT.md` §4 and §2's `closeout_refusal` entry. The handoff is `g2-implementer-handoff.md`.

**The close ordering is fixed and is not anyone's latitude:** satisfy postconditions → final `advance` →
`release` → **then** move the work area, spine **last** → commit → report. Steps 1–3 are the caller's;
`close_work` starts at step 4.

`close_work` must refuse **doing nothing at all** unless: the lease is `"released"`, every item is
terminal (naming the offending gate), and the archive directory does not already exist. It must
**never** open a PR, **never** remove a worktree, and **never** `git add -A` or stage a bare `.`.

## What to verify — in this order

1. **The excluded names are DERIVED, not literal.** `close_work` must exclude `Path(spine_path).name` and
   that name plus `.journal`, not the strings `"spine.json"`/`"spine.json.journal"`. This is the finding a
   cold critic raised as the single most likely way this gate ships green and wrong: both filenames are in
   heavy use here (measured: `spine.json` 48 vs `execute.json` 40 at depth 3 under `.agent-work/`), and
   **this Commander's own driving spine is `execute.json`**. A literal hardcode sweeps a live driving
   checklist into the early batch, before the spine-last step.
   **Falsify it yourself:** mutate the derivation to the literal string, run the test, confirm red,
   restore. (The Commander did this and saw
   `TestCloseWorkDifferingBasenameMandatory::test_execute_json_spine_moves_last_not_swept_into_the_early_batch`
   fail — confirm independently rather than trusting that sentence.)
2. **Does a refusal really do nothing?** "Refuses, doing nothing at all" is the property. Does any test
   distinguish "it refused and moved nothing" from "it refused after moving something and the test only
   checked the return value"? Check the work area's full file set, not just the archive's absence.
3. **Is the spine genuinely last?** The interruption fixture is *simulated* (a monkeypatched raise). Does
   it prove ordering, or only that a mock raised? And could the test pass if the spine were moved *first*?
4. **Does the end-to-end test drive the real engine**, or simulate a drive? If simulated, it proves
   nothing about a real close.
5. **Does `closeout_refusal` agree with `run_crew.spine_terminal`?** The contract deliberately forbids
   calling it (it takes a path and does I/O; the predicate is pure) and requires a **differential test**
   instead. Verify that test exists and actually exercises both a terminal and a non-terminal case.
6. **The stage-by-name guard** must have a mutated positive control proving it can fail. A guard you did
   not falsify is a guard you did not check.
7. **`newline="\n"` on every write.** `docs/agents/CREW_CONTEXT.md:43`; CI runs `windows-latest`
   (`.github/workflows/ci.yml:23`). g1 was BLOCKed for exactly this and the module now carries a
   source-level pin — confirm g2 did not weaken, exempt, or route around it.

## Constraints — check them against the diff yourself

`checklist_engine.py` and `validate_spine.py` unchanged · `scripts/mcp_spine_server.py` untouched (that
is g3's) · `scripts/generate_spine.py` untouched (g4/g5; its own missing `newline` at line 910 is
pre-existing and **out of scope** — do not treat it as a g2 defect) · `settings.json`, `.mcp.json`,
`docs/agents/*` untouched · `skills/**` untouched · no push to `main`.

## Evidence

Before g2: 2856 passed, 3 skipped, 1121 subtests; sweep 23.
After, reproduced by the Commander: **2875 passed, 3 skipped, 1121 subtests**; sweep **23**; 51 tests in
`tests/test_spine_lifecycle.py`.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`. Reproduce these cheaply; spend your budget on whether the tests test what
they claim.

## Stop conditions

- Cannot reproduce a claimed result → **BLOCK** with the output.
- A constraint above is violated → **BLOCK**.
- Leave the tree unmodified. Mutating, observing and reverting is sanctioned; leaving a mutation behind
  is not — check `git status` before you finish.
- **Never waive.** `spine_halt` with `action=block` and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Verdict`** field
whose value is exactly `APPROVE` or `BLOCK`. Number every finding with evidence, consequence, and
confirmed-vs-suspected. End with the single most likely way this gate produces a green run that is wrong,
and a short **Workflow Feedback** section.
