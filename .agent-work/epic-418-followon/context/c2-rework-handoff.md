# Rework handoff — C2: the generator can author the one thing it exists to prevent

**Work id:** `epic-559/c2-generate-the-spine` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`
**Under rework:** `b406cc13` and whatever `g2`/`g3` add on top of it.

## Start with what stands, because most of it does

The design is right and the reviewer was right that it is right. Five closed check kinds and **no
raw-command field anywhere in the format** means an author cannot type a shell command from memory —
that is the mission's central property and it holds. Each kind forecloses one of the four historical
defects by construction: `pytest` compiles the corpus's self-checking idiom with the selector
`shlex.quote`d; `script` probes the target by `ast.parse` of its `add_argument` literals and never
imports it, which kills both the wrong-flag defect and the import-needs-a-bound-spine defect at once;
`population` probes by executing the compiled command itself, so the thing probed is the thing
shipped. `validate()` runs as the literal last statement before success and any `Fault` **or any
`.undecidable` entry** refuses with nothing written. The corpus sweep still reports exactly 23 fault
lines, so no shipped template moved.

None of that is in question. Four things are.

## First: what the Commander already reworked — verify, do not redo

C2's own `g2` cold reviewer returned **BLOCK** and the Commander ran its own rework round before this
handoff reached you. That reviewer earned its keep: the `magnitude=large` escalation — the mechanism
implementing the human's *"greater claim requires greater review"* — injects correctly and its rollup
lands on the right gate, so **every shape check passed**. The reviewer went further, copied the
generated spine out, claimed it, and drove all six items through a real engine. The mechanism does
not fire: `advance` enforces the injected check, `record` and `consolidate` do not, so on a `survey`
host the escalation is decorative.

**That is not yours to fix.** It is fixed, or being fixed, upstream of you. Your job on it is to
**confirm it now fires on `record` and `consolidate`, by driving a survey host — not by reading the
diff.** If it does not, say so and stop; that is a blocker, not a note.

The same applies to anything else the Commander's rework round closed. Confirm by running. Redoing a
closed fix costs a round; assuming one closed costs a defect.

## Blocker 1 — an author can write a check that always passes

`_compile_population` interpolates `expected`, `expected_min` and `expected_max` into the shell
**unquoted and untyped**, and `spec_shape_faults` type-checks none of them. A string value carrying
`||` compiles to:

```
cd <repo-root> && test $(...count...) -eq 1 || echo X
```

which exits **0 regardless of the count**. Verified: `test $(echo 99) -eq 1 || echo PWNED` → exit 0.

**That is a check that cannot fail, authored through the format whose stated purpose is to make one
impossible.** The Admiral reproduced it directly against `compile_condition` with
`{"kind":"population","root":".","glob":"*.py","expected":"1 || echo PWNED"}` and
`spec_shape_faults` returned no faults.

Same root cause, lower severity: `_compile_pytest` interpolates `min_collect` unquoted, so a string
injects a command. It chains with `&&` and pytest still gates the exit code (verified exit 1), so it
is injection without defeating the check. Fix both.

**Why this was easy to miss, which matters more than the bug.** `selector`, `targets`, `path`,
`args`, `root` and `glob` are all correctly `shlex.quote`d or `shlex.join`ed. The careful handling of
every obvious surface is exactly what makes the remaining one skimmable. The three *numeric* fields
were assumed to be numbers and never checked.

**The fix is small and additive:** type-check the four fields in `spec_shape_faults` so a non-integer
refuses at spec-shape time. Do not change the compiled output for a valid spec — `g2` and `g3` build
on it and their work must stay valid.

**The fix is not the deliverable. The boundary test is.** See Blocker 2.

## Blocker 2 — the guard has no violating case, and neither did the review

The cold reviewer approved this. It was not careless: it compiled all five kinds, diffed output
against `DESIGN_NOTE.md` §4 character by character, and round-tripped a deliberately awkward selector
(`"TestFoo or TestBar and not slow"` — spaces plus boolean operators, chosen to differ from every
fixture) through `validate_spine`'s own parser to prove byte-identical recovery. It then wrote that
the property *"holds under adversarial-shaped input."*

It stress-tested the field that was **already protected**, while `min_collect: 2` sat in the same
call untested. It proved the quoting works where quoting was applied and never enumerated where it
was absent.

That is the failure mode of a careful reviewer, and it is this epic's founding defect one tier up:
**absence does not announce itself.** A check that cannot fail looks like one that passed. A field
that was never quoted looks like a field that did not need quoting.

The corrective was already in the launch order, under "Three-way guard fixtures": the repo's own
pattern from `tests/test_mcp_adoption.py::_cli_only_verb_violations` — a **VIOLATING** case the guard
must catch, an **INNOCENT** one it must not, and an **ACCEPTED_FALSE_ALARM** it knowingly tolerates.
The review built an excellent INNOCENT case and no VIOLATING case at all.

**So the deliverable here is the boundary, not the patch.** For every field that reaches a compiled
command, the test file carries a VIOLATING fixture proving the guard refuses it. A fix without that
fixture is the same defect again: a guard whose only evidence is that it does not fire.

## Blocker 3 — nine dispatches, zero `--parent`, zero `--model`

Every crew this run was dispatched with `model` unset and `parent=admiral-epic-418-followon` — my id,
not the Commander's. Both are wrong and both were stated repeatedly:

- **`--model sonnet`** was a `settled/human` pre-ruling in the launch order and appears **nine more
  times as the word "Sonnet"** inside the Commander's own frozen `execute.json`. It never became
  `--model` on a command line. `run_crew.py` adds the flag to argv only when set (`603`), so every
  crew ran at the session default tier.
- **`--parent`** is never mentioned in `execute.json` at all. `parent` reaches the registry only from
  `args.parent` (`1629` → `874`) with no environment fallback, and `_crew_door_env`'s own docstring
  states the rule: a dispatching crew's `SPINE_PARENT` names *"the grandparent, not the dispatcher"*
  and must never leak. The guard works; the Commander passed my id down explicitly instead of naming
  itself. A blocked sub-crew would have asked up two rungs, past the only tier that briefed it.

Pass both on every dispatch from here. `--parent` names your own session:
`constellation/epic-559/c2-generate-the-spine/execute/commander`.

**The instruction is not the fix, and this is the point.** Ten statements produced zero flags. Do not
respond to this by writing an eleventh. Either the dispatch refuses without them, or nothing has
changed — and that refusal is filed as a triage candidate on `run_crew.py`, so **it is not yours to
build here.** Your job is to pass the flags and to say in your result whether you think the refusal
is the right remedy.

## Blocker 4 — the wrong parent is baked into two shipped role specs

`specs/implementer.spine.toml:4` and `specs/reviewer.spine.toml:4` both carry:

```toml
parent = "admiral-epic-418-followon"
```

That is one specific Admiral session id, hardcoded into two **reusable role templates**, and
`generate_spine.py:372` feeds it into the handback contract via
`hand_back_to = spec.get("parent") or "unknown"`. Every future implementer instantiated from that
spec would be told to hand back to a session that ceased to exist when this epic closed.

This is worse than the dispatch-flag miss in Blocker 3, because that one is per-run and ephemeral
while this ships. It is the same root value, leaked one layer further.

**The design around it is right and stays.** `or "unknown"` is the correct honest-null default: a
crew that does not know its parent should say so rather than guess. It was handed a wrong value, not
built wrong.

**The fix follows from the placeholder ruling you are already implementing.** These files are
templates, and a placeholder in a template is a legitimate slot — so `parent = "<parent>"`, resolved
at instantiation, is the correct form. Omitting the line entirely is also acceptable, because
defaulting to `unknown` is a *true* statement where the current value is a stale one.

Add a check that a shipped spec under `specs/` carries no session-specific literal. A VIOLATING
fixture proves it, per Blocker 2.

## What this whole finding is evidence for — say something about it

The mission's settling question was whether the spec format removes the hand-authored-check defect or
merely moves it. **The honest answer is that it moved, and the move was worth making.** An author can
no longer write a bad shell command, because there is no field for one. But the *compiler* can now
write one on their behalf, and that is where the defect went.

That is a good trade and you should say so plainly rather than treat it as a failure: the defect went
from a discipline every author must maintain forever, to one function, pinned by one fixture. Closing
it is a patch. Closing the authoring version was never possible.

Put that in your result. It is the most useful sentence in this workstream.

## Scope

**In:** `scripts/generate_spine.py`, `tests/test_generate_spine.py`, and the dispatch flags on any
crew you launch.

**Out — hard no-gos:** `scripts/checklist_engine.py`, `scripts/validate_spine.py` (it is the oracle;
moving it is a float, not a patch), `scripts/run_crew.py` (the refusal is a separate triage
candidate), `settings.json`, `docs/agents/*`. No merge or push to `main`. Do not edit a shipped
template to make anything pass. The corpus sweep must still report exactly **23** fault lines.

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`. Unsetting the three spine variables matters —
`scripts/mcp_spine_server.py` reads `SPINE_FILE` at import time and raises `KeyError` without it.

## Deliverable

Overwrite `.agent-work/epic-559/c2-generate-the-spine/IMPLEMENTER_RESULT.md` from the implementer
skill's template, including its **Workflow Feedback** section. Say explicitly:

1. which fields now refuse a non-integer, and which VIOLATING fixture proves each one;
2. whether any other field reaching a compiled command is still unvalidated — enumerate them all
   rather than confirming the ones you fixed;
3. your answer on the settling question, in the terms above.
