# Rework handoff — B: the #562 fix blocked on cold review, and the reviewer was right

**Work id:** `epic-559/b-instructions-to-checks` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks` (branch `epic-559/b-instructions-to-checks`, one local commit `0ee69c94`)
**Your spine:** `.agent-work/epic-559/b-instructions-to-checks/REWORK_PLAN.json` — four gates, every postcondition a real command. Drive it gate by gate.

## What happened

Your first pass was good work and most of it stands. The census, the Admiral `init` conversion, and
the Explorer statement fix all survived review. One thing did not.

The #562 fix constrained `EXECUTE_PLAN.g1-implement.c1` to `match: {"status": "complete"}`. You
flagged, honestly and in your own Assumptions section, that no document tells a Commander to attach
a `status` field, and that a Commander which does not reinvent the convention "will find
`g1-implement.c1` permanently unsatisfiable." That flag was the most valuable thing in your result,
and it turned out to understate the problem.

The cold reviewer counted every `implementer-result` evidence record in this repo's history. The
Admiral re-ran the count independently and it holds:

```
total implementer-result records: 122
    28  status=complete      <- the only shape your check accepts
    17  verdict=COMPLETE
    16  verdict=complete
     3  status=COMPLETE
     2  status=COMPLETED
    10  keys: path,summary
     8  keys: diff_digest,gate_id,green_command,green_exit
     5  keys: blockers,path,verified
   ...
```

23% of real records match. `verdict` is more common than `status`. Case varies. Several runs use a
bespoke schema. **There is no convention** — that is the actual finding, and it is bigger than a
missing doc.

The engine's artifact match is exact dict equality (`checklist_engine.py:846-860`), so every shape
above except the first fails. A gate that refuses legitimate completed work is the same defect as
one that cannot fail, with the sign flipped, and this one ships in the template every Commander
instantiates. Hence `BLOCK`.

## What you are NOT being asked to do

Do not revert to a presence-only check. Weakening the statement back to "IMPLEMENTER_RESULT
returned" would be honest, and it would leave the gate unable to notice a blocked implementer — the
original complaint in #562. Blocking is the safe direction here: a Commander stuck at a gate can ask
up, and by ruling a Commander may waive a crew's check. A gate that silently accepts failure cannot
be recovered from at all.

## What you ARE being asked to do

**Close the loop instead of guessing at it.** The template that carries the check must carry the
instruction that satisfies it. Right now `g1-implement`'s imperative says only "integrate the
returned IMPLEMENTER_RESULT as evidence" — it never says as what. Say it: the field name, that the
value is the IMPLEMENTER_RESULT's own Return status, and that it is lowercase. Then repeat it where
a Commander would look — `commander-core.md` and `IMPLEMENTER_HANDOFF.template.md`.

Then prove it, which is gate `r2`: **no test in this repo has ever asked whether a shipped
template's gates are satisfiable by a real run.** That absence is why this shipped. Instantiate the
real template, drive the real gate through the real engine with evidence attached exactly as your
new imperative instructs, and assert it advances — plus the negative, that a blocked result refuses.

**The historical records are not your problem.** Old spines are not re-run. New runs instantiate
from the template you are fixing, so template and instruction agree from here forward.

## The second defect the reviewer found, which is yours

`REVIEW_SURVEY.template.json`'s `r6-fowler.c1` ships a check command containing
`<fowler-pass-record-path>` — a token `init_work_area.resolve_spine` cannot resolve. That check is
non-functional out of the box. The reviewer hit it live and had to repair its own survey mid-review
to proceed.

Your census called that row "already converted, no action." That is the census miscounting in
exactly the way the task existed to catch: it verified a check was *present*, never that it *runs*.
Gate `r3` fixes that placeholder and sweeps all six templates for the same shape, with a test so the
next author cannot ship another.

## Scope

**In:** `skills/commander/templates/EXECUTE_PLAN.template.json`,
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
`skills/commander/references/commander-core.md`,
`skills/reviewer/templates/REVIEW_SURVEY.template.json`, the other shipped role templates as `r3`
requires, and the three new test files your gates name.

**Out — hard no-gos:** `scripts/checklist_engine.py`, `scripts/run_crew.py`,
`skills/implementer/*` and `skills/reviewer/SKILL.md` (**another crew owns those this wave — do not
touch them**), `settings.json`, `docs/agents/*`. No merge or push to `main`. Local commits only.

## Notes on your own spine

Every postcondition on `REWORK_PLAN.json` is a real command, and each test gate requires a minimum
collected-test count before running the suite — a test file that collects nothing will refuse the
gate. That is deliberate, and it is the same falsifiability rule your own task is about: a check
that cannot fail is indistinguishable from one that passed.

Two door tools you may want, `spine_capture` and `spine_amend`, are denied on this branch — the
crew tool grant froze at seven names while the door grew to nine. Another crew is fixing that right
now. If you hit the denial, use the engine CLI for those two verbs only and say so in your result;
the reviewer hit the same wall and that is how we know it is real.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **The goal is a weaker agent than you.** Prose instruction is a liability; anything that can sit
  behind a check should.
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** the same reviewer standard applies again.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.

## Deliverable

`.agent-work/epic-559/b-instructions-to-checks/IMPLEMENTER_RESULT.md` (overwrite the existing one),
from the implementer skill's template, including its **Workflow Feedback** section. Say explicitly
what your first census missed and whether your new tests would have caught it.
