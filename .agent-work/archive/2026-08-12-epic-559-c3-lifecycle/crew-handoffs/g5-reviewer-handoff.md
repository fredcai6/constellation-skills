# Reviewer Handoff — g5: the two carried findings

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g5` · **Role:** `reviewer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g5-reviewer-result.md`

## The review standard this wave inherits

C2's branch was reviewed **five** times; the first four each ran real commands, each answered its own
questions correctly, and each missed something different — a field that was never quoted (invisible
because **absent**), a stale session id on nine of nine gates (invisible because **ubiquitous**), that
same id used as proof of completeness, and a divergence one reviewer described accurately then scoped
away.

**A review establishes that a mechanism operates and does not ask whether the value it carries is right.**
Ask both questions. Treat your own green results as questions.

**This gate is the one where that matters most**, because half of it is a *document*. §7 of
`DESIGN_NOTE.md` is a list, and a list is exactly the artifact where absence is invisible.

## What was implemented

1. A new spec-shape fault `spec-not-yet-written-not-bool` refusing a non-`bool` `not_yet_written`.
2. A reconciliation of `DESIGN_NOTE.md` §4, §7 and §10 against shipped behaviour.

```
git diff b88f13a4..HEAD --stat
git diff b88f13a4..HEAD
```

The crew's account is `g5-implementer-result.md`; the spec is `LIFECYCLE_CONTRACT.md` §7 and the handoff
`g5-implementer-handoff.md`. Read the result **after** forming your own view.

## What to verify

1. **The guard is about TYPE, not value.** Six cases, all of which the Commander ran:
   `"false"`, `"true"`, `1` must each be **refused** by fault name; `true`, `false`, and the field
   **omitted entirely** must behave exactly as before (`true` still yields the non-blocking
   `undecidable-pytest-not-yet-written` note and compiles to `check: null`). Re-run all six.
2. **Does the fault message tell the truth?** It claims a string would compile the check to `None` and
   lose it entirely. Verify that claim against `compile_condition` — a message that misdescribes the
   defect is worse than a terse one.
3. **§7's fault vocabulary — this is the load-bearing one.** It must list **every** fault code the
   generator can raise. **Enumerate the codes mechanically from the source, count them, and compare with
   the note's list, item by item.** A missing code is invisible unless you diff the two sets. State both
   counts. (For calibration: the Commander's rough grep found 17 `spec-*` literals in
   `scripts/generate_spine.py` and 18 `spec-*` strings in the note — those two numbers are **not**
   directly comparable, because the note legitimately names things the source spells differently and the
   grep may catch prose. **Do the comparison properly rather than trusting either number.** If they
   genuinely disagree, that is a finding.)
4. **§4 and §10.** Does §4 now account for what `not_yet_written` does (it compiles to `check: null`)?
   Does §10's four-defect table still hold after g4 added dispatch faults? Where a claim was deleted, was
   deletion right — or was a true claim removed to make the section easier?
5. **Was a correct paragraph rewritten for no reason?** Churn in a frozen contract costs every future
   reader a re-verification. Flag needless edits.
6. **`generate_spine.py:910`'s missing `newline="\n"`** was in scope for this gate. Was it fixed?
   (`docs/agents/CREW_CONTEXT.md:43`; CI runs `windows-latest`.)
7. **Nothing shipped moved.** Neither shipped spec uses `not_yet_written`, so the sweep must still be
   exactly **23**.

## Constraints — check against the diff

`checklist_engine.py` and `validate_spine.py` unchanged · `scripts/spine_lifecycle.py`,
`scripts/mcp_spine_server.py` and g4's dispatch code untouched · `.mcp.json`, `settings.json`,
`docs/agents/*` untouched · `skills/**` untouched · no push to `main`.

Note `validate_spine.py` has **no `not_yet_written` concept**, so a legitimately-TDD-red check and a
permanently-vacuous one are indistinguishable to the oracle. That is a **recorded finding**
(`LIFECYCLE_CONTRACT.md` §7b), deliberately **not** fixed this wave. Do not treat it as a g5 defect.

## Evidence

Before g5: 2920 passed, 3 skipped, 1121 subtests; sweep 23.
After, reproduced by the Commander: **2932 passed, 3 skipped, 1121 subtests**; sweep **23**.

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`. Spend your budget on question 3.

## Stop conditions

- Cannot reproduce a claimed result → **BLOCK** with the output.
- A constraint above is violated → **BLOCK**.
- Leave the tree unmodified — check `git status` before finishing.
- **Never waive.** `spine_halt` with `action=block` and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Verdict`** field whose
value is exactly `APPROVE` or `BLOCK`. Number every finding with evidence, consequence, and
confirmed-vs-suspected. End with the single most likely way this gate produces a green run that is wrong,
and a short **Workflow Feedback** section.
