# Implementer handoff — w3a-465 / g1-implement

## Task

Three coupled changes in worktree `C:/Programs/wt-w3a-465`, branch `epic-418/w3a-465`. Issue #465.

**1. `scripts/checklist_engine.py` — let `amend`'s `retext-check` op run on a SURVEY checklist.**

`amend()` opens with a blanket `if cl.get("type") != GATED: raise EngineError("amend applies to gated
checklists")`. Relax it so a delta whose ops are **all** `retext-check` is accepted on a survey.
`add`/`drop`/`rescope` stay gated-only, and the refusal message for those on a survey must say this
is a **conservative choice, not a type-level impossibility** — `drop` on a survey item is a coherent
thing to want; it is refused because nothing needs it yet. The `retext-check` op body needs no
change: its status guard (`pending` or `in-progress`) is already satisfiable on a survey item.

**2. `scripts/checklist_engine.py` `save()` — preserve the file's existing line ending, write bytes.**

Currently `Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")` — text mode,
`newline=None`, so on Windows every `\n` becomes `\r\n` and on POSIX every existing `\r\n` becomes
`\n`. One engine call rewrites a whole file's endings and destroys blame. Detect the target file's
dominant existing line ending and write bytes with it. **A file that does not exist yet, or one with
mixed endings, gets LF** — state that in the docstring. Scope is `save()` only.

**3. `skills/reviewer/` — the two prose corrections.**

- `templates/REVIEW_SURVEY.template.json`, `r6-fowler`'s imperative currently says *"Before recording
  pass, fill this item's postcondition command with the real record path you wrote it to."* Rewrite
  it to name **both** paths, in this order of prominence:
  - **normal path:** resolve the real record path when you **instantiate** the survey from this
    template, before you `claim` — the same instantiation-time substitution `<work-id>` on line 2
    gets. This is the documented route.
  - **repair path:** if the record moves or the path was wrong, correct it with
    `amend --delta <file> --op retext-check` through the engine — never by hand.
  Do not let the repair path read as the documented route.
  Say what `--authority` and `--reason` mean here: **the authority is the dispatching Commander,
  named in the reviewer handoff — never a string the reviewer invents.** Keep the placeholder token
  in the shipped template (it marks an instantiation-time substitution, like `<work-id>`); what
  changes is the instruction about when and how it is resolved.
- `SKILL.md` line 28 says *"an open fail cannot consolidate to APPROVE."* `consolidate()` refuses
  that **unless `--override-reason` is supplied** (`docs/CHECKLIST_SCHEMA.md:276` documents the guard
  as intentional shape-checking that kills the weak-reviewer failure mode). Correct the sentence so a
  reviewer with a real out-of-scope finding is pushed toward neither a wrong BLOCK nor a silently
  downgraded finding. **The prose moves; `consolidate()` is unchanged.**

## Protected intent

An instruction an agent cannot follow through the engine is an invitation to hand-edit engine state,
which the engine exists to prevent. After this change, every instruction in the reviewer skill names
an action the engine can actually perform.

## The red you must observe FIRST

Two reds are already captured at `.agent-work/w3a-465/red/amend-refusal.txt` — read them, do not
redo them. You owe the **third**: the line-ending red.

Build the defective world and watch the current code get it wrong before you fix anything.

`tests/test_engine_survey_retext_and_newlines.py`, with exactly these four node ids (they are named
in the gate's check command, so a renamed or missing test is a red gate):

- `test_retext_check_works_on_a_survey`
- `test_add_drop_rescope_still_refuse_a_survey`
- `test_save_preserves_lf_line_endings`
- `test_save_preserves_crlf_line_endings`

**Both line-ending fixtures ship and each has a different job.** On Windows the **LF** fixture is the
discriminating one for this bug — `write_text` already emits CRLF here, so a CRLF-only test passes in
the healthy world and the broken one alike and proves nothing. The **CRLF** fixture is the guard
against the obvious over-correction of "always write LF". On POSIX the roles swap. Name in your
result **which fixture went red on which platform**, and paste the failure output.

**Three test shapes that cannot fail. All forbidden:**

1. Building the LF fixture with `write_text("...\n")` — on Windows that fixture is **born CRLF**, so
   the discriminating test silently degenerates into the vacuous one. Use `write_bytes`.
2. Asserting on `read_text()` — universal-newline translation makes `b"\r\n" not in p.read_text()`
   vacuously true forever. Assert on `read_bytes()`.
3. Asserting the saved bytes equal the fixture's bytes — `save()` re-serialises with `indent=2`, so
   content legitimately differs; the assertion fails for the wrong reason and gets loosened. Scope
   the assertion to line-ending bytes.

## Allowed scope

`scripts/checklist_engine.py`, `skills/reviewer/**`, and the one new test file under `tests/`.

## Specific exclusions

- **Do not touch** `tests/test_episode_negative_control.py`, `scripts/hooks/gauge_writer_hook.py`,
  `tests/test_verify_spec_confirmed.py` — concurrent sibling dispatches own them.
- **Do not touch** `skills/interrogator/**`. Its `zc-consolidate` carries the identical defect
  word-for-word; it is outside this fence and already raised as a triage candidate.
- Do not change `consolidate()`.
- Do not touch the journal append near line 2762 (also text-mode; raised as a triage candidate).
- Do not refactor the engine beyond these two edits.

## Constraints

- The `r6-fowler` command postcondition is an enforced invariant (two-bin rule) and **stays a command
  check**. Do not delete it.
- Never hand-edit a checklist JSON file; drive the engine.
- Do not use `py` for pytest (#454). `FORCE_COLOR=3` gives false reds for `python` too.

## Required evidence

1. The line-ending test observed **failing** against the unmodified `save()`, pasted, with the
   platform and the fixture named.
2. The same test passing after the fix.
3. `amend --op retext-check` observed **working** on a real survey after the change, and
   `add`/`drop`/`rescope` observed still refusing one.
4. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` with its **real exit code**. If you pipe it,
   `$?` is the pipe's exit code — use `${PIPESTATUS[0]}`.

## Verification commands

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_engine_survey_retext_and_newlines.py
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

## Authority

Commander `w3a-465`, under Admiral launch order LO-465 (epic #418, wave 3). No reachable human.
Float anything outside this handoff back to the Commander rather than deciding it.

## Result artifact

Write `IMPLEMENTER_RESULT.md` to `.agent-work/w3a-465/g1-implement/IMPLEMENTER_RESULT.md`.
