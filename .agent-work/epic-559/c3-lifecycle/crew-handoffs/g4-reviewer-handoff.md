# Reviewer Handoff — g4: the declared dispatch

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g4` · **Role:** `reviewer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-reviewer-result.md`

## The review standard this wave inherits — read it twice

C2's branch was reviewed **five** times. The first four each ran real commands, each answered its own
questions correctly, and each missed something different: a field that was never quoted (invisible because
**absent**); a stale session id on nine of nine gates (invisible because **ubiquitous**); that same id
written into a review's own evidence line **as proof of completeness**; and a divergence one reviewer saw,
described accurately, then **scoped away**.

**A review establishes that a mechanism operates and does not ask whether the value it carries is right.**
For every check, ask both questions. Treat your own green results as questions.

Demonstrated twice already on this run: `g1`'s first review found a write missing `newline="\n"` that
every test passed over; and the Commander's own AST purity check on `g3` returned a **false positive**
because it matched a docstring. Assume something equivalent is in this diff.

## What was implemented

`[[gate.dispatch]]` in the spec format, three new spec-shape faults, an injected `command`-kind
postcondition per declared dispatch, and `scripts/verify_declared_dispatch.py`. The crew committed its own
work; inspect the commits:

```
git diff 386d7635..HEAD --stat
git diff 386d7635..HEAD -- scripts/generate_spine.py
```

Its account is at `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-implementer-result.md`. Read it
**after** forming your own view. The spec is `LIFECYCLE_CONTRACT.md` §5 and the handoff
`g4-implementer-handoff.md`.

## What to verify — in this order

1. **Does the injected postcondition actually refuse a wrong parent?** This is the whole gate. Build a
   `crew-runs.json` yourself, run the emitted command, and confirm a non-zero exit naming the offending
   entry. (The Commander did this: declared `commander-session` against a recorded
   `admiral-epic-418-followon` exits 1; the matching case exits 0. **Confirm independently.**) Then ask
   the second question: is the message *correct* — does it name the right entry, the right fields?
2. **Is the injected check `command`-kind, not `artifact`?** `DESIGN_NOTE.md` §6's `### CORRECTION`
   records that `record()`/`consolidate()` never evaluate artifact-kind postconditions on a survey item,
   so an artifact check would be **silently inert** there. Assert the emitted shape, not the intent.
3. **`spec-dispatch-undeclared` is a TEXTUAL match on three markers.** Verify the code and the fault text
   say so honestly. The contract is explicit that this **narrows** the hole and does not close it — an
   imperative phrased without any marker is still invisible. **If the code, the fault message, or any doc
   line claims it is closed, that is a finding.** Overclaiming is the defect here, not the narrowness.
4. **Is `abandoned` respected?** The `ACCEPTED_FALSE_ALARM` fixture requires that a wrong-parent entry
   marked `abandoned: true` does **not** block. Does the code reuse `run_crew.is_abandoned` or re-implement
   it? A second implementation of that predicate can drift.
5. **Does the emitted command quote its tokens and anchor its `cd`?** Every other compiled check in this
   generator does. An unquoted token is defect 1 of the C2 design note, returning.
6. **Nothing shipped moved.** Neither shipped spec declares a dispatch, so the sweep must still be exactly
   **23**. If it moved, a shipped template moved, which is a no-go this wave.
7. **`not_yet_written` was left alone.** That is g5's, running next. Confirm `generate_spine.py:424`/`:673`
   still read it with bare truthiness and that g4 did not half-fix it.

## Constraints — check against the diff yourself

`checklist_engine.py` and `validate_spine.py` unchanged · `scripts/spine_lifecycle.py` and
`scripts/mcp_spine_server.py` untouched (g1–g3 own them, all reviewed) · `DESIGN_NOTE.md` untouched (g5
reconciles it) · `.mcp.json`, `settings.json`, `docs/agents/*` untouched · `skills/**` untouched ·
`encoding="utf-8", newline="\n"` on every write (`docs/agents/CREW_CONTEXT.md:43`; CI runs
`windows-latest`) · no push to `main`.

## Evidence

Before g4: 2884 passed, 3 skipped, 1121 subtests; sweep 23.
After, reproduced by the Commander: **2920 passed, 3 skipped, 1121 subtests**; sweep **23**.

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`. Reproduce these cheaply; spend your budget on questions 1–4.

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
