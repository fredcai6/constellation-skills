# Rework handoff — C1: the lint refuses the very idiom the repo recommends

**Work id:** `epic-559/c1-spine-lint` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c1-spine-lint` (branch `epic-559/c1-spine-lint`)
**Your spine:** `.agent-work/epic-559/c1-spine-lint/REWORK_PLAN.json` — four gates. The Admiral ran every check before dispatching: all substantive ones **red**. Drive it gate by gate.

## Three of your four faults are clean, and that is a real result

A cold reviewer swept **539** gated-or-survey spines under `.agent-work/` plus the 12 shipped
templates and hand-inspected every distinct trigger. Faults 1, 3 and 4 produced **zero false
positives**. All three distinct fault-3 statement texts across 128 hits were hand-verified as genuine
#562-shaped defects. Every distinct fault-4 placeholder was confirmed genuinely unresolved. That is
the hard part of this job and you got it right.

Do not re-litigate those. Confirm they stay clean and spend everything on fault 2.

## Fault 2 refuses good spines, and it refuses the diligent ones specifically

**8 of the 9 zero-collect findings in the archive sweep are false positives**, all from one
mechanism.

`_pytest_segments` splits a command on bare `|`. In the corpus's own recommended idiom —

```
test $(pytest ... --collect-only 2>/dev/null | grep -c '::') -ge N && pytest ...
```

— the token `2>/dev/null` lands inside the first segment. `shlex` tokenizes it as one opaque
non-flag token, `_pytest_targets` folds it in as a positional pytest target (a path that does not
exist), `_collects_zero` runs pytest against that bogus path, gets nothing back, and reports
zero-collect. `_fault_zero_collect` dedupes by selector text in command order, so the corrupted
first-segment verdict wins before the real second segment is ever reached.

The Admiral reproduced it directly. A check that runs **32 passing tests** is flagged
`falsifiable-zero-collected` — the same severity as `check: null`.

That idiom is not an odd style. `docs/agents/CREW_CONTEXT.md`'s Verification Discipline asks authors
to write exactly it, so the lint **penalizes the author who follows the documented best practice and
rewards the naive one-liner that skips the self-check.** It fires on this epic's own spines, and on
your own `REWORK_PLAN.json` — gate `z3`'s check catches it there right now.

**Fix:** skip shell-redirect-shaped tokens when collecting pytest targets. Regression-test with the
idiom verbatim.

## Second mechanism, same gate

`_collects_zero` invokes pytest with `sys.executable`, discarding whatever interpreter the check's
own command text names, and never confirms pytest is importable there before treating an empty
result as zero-collect. On this host `python3` has no pytest, which
`docs/agents/CREW_CONTEXT.md` documents explicitly. Reproduced through the real CLI:

```
python3 -m scripts.validate_spine .agent-work/w5-gates/execute.json   -> 6 spurious faults
python  -m scripts.validate_spine .agent-work/w5-gates/execute.json   -> 0
```

Nothing distinguishes "pytest did not run" from "genuinely collected zero", so an operator typing
the more literal-looking `python3` gets false refusals on every pytest-based check in the file.

Confirm pytest is importable, or invoke the interpreter the command itself names. **When you cannot
tell, say you cannot tell rather than reporting a fault — an undecidable check is not a failing
check.** That distinction is the point of the gate.

## About your spine's own checks

`z1.c1` and `z3.c1` run two scripts the Admiral wrote, at
`.agent-work/epic-559/c1-spine-lint/check_idiom.py` and `check_corpus_fp.py`. **They are not yours
to edit.** They are the parent's independent statement of what "fixed" means: the canonical idiom
must not be flagged, and no spine this epic drove to a terminal state may be flagged zero-collect,
over an asserted count of what was examined. If you believe either script is wrong, block and say
so — do not change it.

## Scope

**In:** `scripts/validate_spine.py`, `tests/test_validate_spine.py`, fixtures, `map/INDEX.md`.
**Out:** `checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `settings.json`,
`docs/agents/*`, every spine template, and the two Admiral check scripts above. No merge or push to
`main`.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** the same reviewer standard applies again.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`. Commit before you finish —
  gate `z4.c2` refuses on a dirty tree.
- **Use the door.** `SPINE_FILE`/`SPINE_SESSION` are bound for you; `mcp__spine__*` via `ToolSearch`.
- **Do not dispatch anything and then end your turn to wait for it.** A crew died that way tonight.
  Nothing resumes a headless crew.

## Deliverable

`.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_RESULT.md` (pass 1 preserved as
`IMPLEMENTER_RESULT.pass1.md`), from the implementer skill's template, including **Workflow
Feedback**. State the false-positive rate before and after.
