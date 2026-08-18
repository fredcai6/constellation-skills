# Self-hosting proof — #634 lane K

`decision:self-hosting-proof`: this change alters the rule the Admiral's own live spine runs
under. So: a **read-only** verb on the live spine must exit 0, and every **mutating** verb is
proven against a **COPY**, never the live file. Fresh process, explicit paths, `SPINE_*` and
`CREW_SCRATCH_DIR` stripped. Tree at `eb94b150`.

`ENVU` below is `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`.

## 1. Read-only on the LIVE Admiral spine — exit 0

```
$ ENVU py scripts/checklist_engine.py \
    --file /home/tommy/projects/constellation-skills/.agent-work/epic-567-door/spine.json current
LEASE active: constellation/epic-567-door (by admiral, heartbeat 2026-08-18T04:35:30.378001+00:00)
exit=0
```

The Admiral's spine still reads correctly under the patched engine, lease and all.

## 2. Read-only on my OWN live spine — exit 0

```
$ ENVU py scripts/checklist_engine.py --file .agent-work/567-k/spine.json current
RAIL: A working solution is the MIDDLE of this run — you are 6 steps from done
exit=0
```

Worth stating plainly: **the engine I am running is the engine I just changed.** Both live spines
in this epic still project correctly under it.

## 3. Mutating verbs — against a COPY only

Fixture: a copy of `COMMANDER_SPINE.template.json` (which now declares `init` and `archive` as
bookends), with `init`/`context`/`understand` complete and `plan` in-progress — a Commander
standing at `plan`, the ordinary state in which it would author its work gates.

### 3a. Drop the frozen closing bookend — REFUSED

```
$ ENVU py scripts/checklist_engine.py --file $COPY amend \
    --delta '{"ops":[{"op":"drop","id":"archive"}]}' --reason proof --authority proof
REFUSED: drop archive: a declared bookend gate cannot be dropped, regardless of status
```

This is the exact delta that succeeded at `9b38b9d9`
(`.agent-work/567-k/evidence/probe-closing-bookend.md`).

### 3b. Grow the middle — SUCCEEDS

```
$ ENVU ... amend --delta '{"ops":[{"op":"add","id":"g1-implement","after":"plan", ...}]}'
amended: added g1-implement (authority proof)
```

The freeze did not cost the mutability. **This is the half a guard could easily have broken
while still passing every refusal test**, which is why it is proven here and not assumed.

### 3c. All-or-nothing — a mixed delta leaves the plan unmutated

```
$ ENVU ... amend --delta '{"ops":[{"op":"drop","id":"reconcile"},
                                  {"op":"drop","id":"archive"}]}'
REFUSED: drop archive: a declared bookend gate cannot be dropped, regardless of status

items: ['init','context','understand','plan','g1-implement','execute',
        'reconcile','triage','review','feedback','archive']
```

`reconcile` — the **legal** op in that delta — did **not** land. The refusal rolled the whole
delta back, which matters because `main()` persists the checklist even on the error path.

## 4. The live spines were not touched

```
$ git -C /home/tommy/projects/constellation-skills status --porcelain .agent-work/epic-567-door/
(no output)
```

The Admiral's work area is unmodified by any of the above.

## What this does NOT prove

- It does not prove the guard holds against a hand-edited `spine.json`. Nothing cross-checks the
  file against the journal; `load()` is a bare `json.loads`. The refusal is scoped to the engine's
  verbs, never to the file. All three design candidates independently said so.
- It does not exercise the **retrofit** path (`rescope {bookend: true}` on a spine already
  running). That is covered by unit tests, not by this proof, and it was deliberately **not** run
  against either live spine.
- The `authority` string here is the literal `proof`. The engine requires it to be non-empty and
  never checks it against anything.
