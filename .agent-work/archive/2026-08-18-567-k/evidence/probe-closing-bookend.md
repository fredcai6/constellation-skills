# Probe: is the closing bookend frozen? — answer: **NO**

Run 2026-08-18. Fresh process, explicit paths, `SPINE_*` and `CREW_SCRATCH_DIR` stripped.
Engine at `9b38b9d9`. **Every mutating verb ran against a COPY; the live spines were only read.**

This is the measurement behind lane K's central claim. I ran it myself rather than taking it
from the launch order or from a crew.

## 1. Live Admiral spine — read-only, exits 0, untouched

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
    py scripts/checklist_engine.py \
    --file /home/tommy/projects/constellation-skills/.agent-work/epic-567-door/spine.json current
LEASE active: constellation/epic-567-door (by admiral, heartbeat 2026-08-18T04:35:30.378001+00:00)
ACTIVE execute [in-progress] — ...
postconditions:
  c1 [unmet] null — every epic issue dispositioned ...
exit: 0
```

## 2. A non-owner cannot amend — but that is the lease, not a bookend

On a **copy** of the live Admiral spine, `drop closeout` without the session id:

```
REFUSED: checklist is owned by active session 'constellation/epic-567-door';
pass --session-id 'constellation/epic-567-door' or take over with `claim --force --reason ...`
exit: 1
```

The lease is **not** a bookend guard. It keeps *other* sessions out. The agent that would drop
its own closing bookend is the owner, and the owner passes this check by definition.

## 3. Supplying the owner's session id — refused only by accident of status

```
REFUSED: drop closeout: only a pending gate can be dropped (is 'blocked')
exit: 1
```

The Admiral's `closeout` is currently `blocked` (it is waiting on human acceptance). It is
protected **by the accident of its present status**, not by any rule that says a closing bookend
is frozen. A `pending` closeout would have been dropped.

## 4. The general case — a Commander at `execute` deletes its own closing bookend

Synthetic fixture built from `skills/commander/templates/COMMANDER_SPINE.template.json`:
`init`/`context`/`understand`/`plan` complete, `execute` in-progress, the rest pending. This is
the ordinary mid-run state of every Commander in the corpus.

Delta:

```json
{"ops":[{"op":"drop","id":"archive"},{"op":"drop","id":"feedback"},{"op":"drop","id":"review"}]}
```

Result:

```
amended: dropped archive, dropped feedback, dropped review (authority probe)
exit: 0

items now: ['init','context','understand','plan','execute','reconcile','triage']
amendments: [{'ts':'2026-08-18T04:54:27.983710+00:00',
              'reason':'probe: is the CLOSING bookend frozen?',
              'authority':'probe',
              'ops':['dropped archive','dropped feedback','dropped review']}]
```

Saved fixture: `.agent-work/567-k/evidence/probe-closing-bookend-dropped.json`.

## What this proves

A role standing in the middle of its own run can amend away its **entire closing bookend** in one
delta and reach a terminal state having never been independently reviewed, never captured
episodes, and never archived. The `review` step is the corpus's own stated safety net —
`README.md`: "An independent reviewer, every time." At `9b38b9d9` it is amendable away by the
author it is meant to check, with a single `amend` call and no `--force`.

`_floor()` (`checklist_engine.py:3036`) freezes what has **already been started**, which is why
the *opening* bookend needs nothing new: by the time you could amend, `init`/`context` are
already non-pending. The *closing* bookend is pending for the whole run and has no guard at all.
The asymmetry is not a policy choice anyone made — it falls out of using status as a proxy for
"frozen".

## What this does NOT prove

- It does not show anyone has actually done this in a real run. It is a capability finding, not
  an incident report. I did not search the journals for an occurrence.
- It says nothing about survey checklists — `amend` on a survey already accepts only
  `retext-check` (`:3013`).
- It does not evaluate whether the *opening* bookend needs an explicit declaration too; `_floor()`
  covers it only so long as the opening gates are always started before any amend, which is true
  for the three shipped templates but is not enforced.
- `authority` here was the literal string `probe`. The engine requires the field to be non-empty
  and never checks it against anything. That is a separate observation, not part of this claim.
