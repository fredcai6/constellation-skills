# notes-465 — an instruction with no affordance behind it

Working notes for dispatch `w3a-465`, issue #465, epic #418 wave 3.
Worktree `C:/Programs/wt-w3a-465`, branch `epic-418/w3a-465`.

## Problem statement (reconciled against LAUNCH_ORDER, delegated mode)

Three things to settle, all one shape: **prose telling an agent to do something the machinery
does not let it do.**

1. `r6-fowler`'s imperative in `skills/reviewer/templates/REVIEW_SURVEY.template.json` orders the
   reviewer to "fill this item's postcondition command with the real record path". No engine verb
   can do that on a survey.
2. Improvising the fill by hand in text mode rewrites every line ending in the survey file.
3. `skills/reviewer/SKILL.md` says "an open fail cannot consolidate to APPROVE"; the engine ships
   `--override-reason` for exactly that.

## Evidence

### Is the filled value load-bearing? YES — the engine executes it.

`scripts/checklist_engine.py:1887` `record()`:

```
if result == "pass":
    posts = t.get("postconditions", [])
    command_posts = [c for c in posts if _condition_kind(c) == "command"]
    unmet = [c["id"] for c in command_posts if not _check_condition(c, t, base_dir)]
    if unmet:
        raise EngineError(f"{iid}: command postconditions unmet {unmet}; cannot record pass", ...)
```

`_check_condition` (line 763) runs a `command` check through `_run_check_command`. So the string
`python scripts/verify_fowler_pass.py <fowler-pass-record-path>` is **executed** on the reviewer's
own `record r6-fowler --result pass`. Unfilled, it fails and blocks the pass. The value is not
decorative and it is not merely read — it is run, and it is the only thing standing between a
reviewer and a Fowler pass it never verified.

By the launch order's own rule ("if something reads it, the verb is required and the imperative
must name it"), removal is off the table: deleting the placeholder means deleting the check, and
that drops the Fowler rail to prose-only, which the repo's own two-bin rule says enforces nothing.

### Can any engine verb fill it? NO.

`amend` is the only verb that edits check text. First line of `amend()`
(`scripts/checklist_engine.py:2128`):

```
if cl.get("type") != GATED:
    raise EngineError("amend applies to gated checklists")
```

`REVIEW_SURVEY.template.json` line 3 is `"type": "survey"`. Confirmed by running it — see
`red/amend-refusal.txt`.

### Why this is not a survey-authoring quirk

Every other placeholder-bearing command check in the corpus lives in a **gated** template
(`COMMANDER_SPINE`, `ADMIRAL_SPINE`, `EXPLORER_SPINE`, `EXECUTE_PLAN`, `IMPLEMENTER_PLAN`), where
`amend --op retext-check` is available. The two that live in a **survey** are `r6-fowler` and the
interrogator's `zc-consolidate` — and those two are exactly the two imperatives that tell the agent
to fill the placeholder by hand. The defect tracks the checklist type, not the author.

### The line-ending defect is in the engine's own writer

`scripts/checklist_engine.py:169`:

```
def save(path: Path, data: dict) -> None:
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
```

`write_text` with no `newline=` is text mode with newline translation. On Windows every `\n`
becomes `\r\n`; on POSIX every `\r\n` in an existing file becomes `\n` on the next write. The repo's
`.gitattributes` is `* text=auto`, so checked-out JSON is CRLF on Windows and LF on POSIX — meaning
the engine rewrites the whole file's line endings on **one** of the two platforms for **every**
checklist it touches. Same defect as the #447 g3 reviewer's hand-fill, one layer down.

## Decisions

- **Placeholder: add the affordance and name it in the imperative.** Not a new verb — lift the
  existing `amend --op retext-check` op to survey checklists. `add`/`drop`/`rescope` stay
  gated-only: those are gate re-planning and a survey has no gates to replan. `retext-check` is an
  authoring-fix op and is the one the imperative needs. FLOATED to the Admiral per LAUNCH_ORDER
  ("a new engine verb is a change to a shared interface").
- **Line endings: the engine preserves the file's existing ending and writes bytes.** Per
  `decision:binary-io-for-engine-state`.
- **`SKILL.md` contradiction: the prose moves.** `docs/CHECKLIST_SCHEMA.md:276` documents the
  override as intentional: the guard "is pure shape-checking — the engine is not judging quality,
  only refusing a verdict that contradicts its own recorded findings. It kills the weak-reviewer
  failure mode." The affordance is a deliberate, logged escape hatch, the same pattern as the
  Fowler `overridden` verdict in the same skill. Deleting it would remove a documented mechanism;
  the prose is the thing that is wrong.

## Showing the red

The trap the launch order names: on Windows a CRLF round-trip test passes in the healthy world and
the broken one alike, because `write_text` happens to emit CRLF here. The discriminating fixture on
this platform is **LF**. The test asserts *preservation, whatever the ending is*, with both
fixtures, so it is red on every platform: the LF fixture is red on Windows, the CRLF fixture is red
on POSIX.

## Out of scope — passed up

- `skills/interrogator/templates/INTERROGATION.template.json` `zc-consolidate` carries the identical
  defect, word for word ("Before consolidating, fill this item's postcondition command with the real
  record path"). Outside this dispatch's fence. Triage candidate.
- The same file's prose says `py scripts/verify_interrogation.py`; #454 ruled `py` is never the
  pytest/python entry. Triage candidate.

---

The full dispatch result is at `.agent-work/w3a-465/RESULT.md` (verdict, evidence, the red, exit code, isolation proof, triage candidates, workflow feedback).
