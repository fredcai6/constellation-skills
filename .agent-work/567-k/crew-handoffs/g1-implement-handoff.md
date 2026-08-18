# Implementer handoff — g1: the bookend guard in `amend()`

**Result path (write here before ending your turn — that write is the delivery):**
`.agent-work/567-k/crew-handoffs/g1-implement-result.md`

**Suggested Model Tier:** sonnet. Bounded, well-specified engine change against a brief that
already carries the source reads and the test list; breadth over reasoning depth.

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Branch: `feat/567-k-one-spine-mutable-middle`. Base `9b38b9d9`; all line numbers pinned there.

## Assigned task

Give `amend()` a **declared-bookend guard**, so a role cannot amend away its own **closing**
bookend, while the middle of its plan stays freely mutable.

## Protected intent (issue #634)

The human, verbatim:

> "there should likely be frozen required gates at the start and finish, but what we do in the
> middle is squishy and is totally reasonable to change as we're executing and understanding the
> problem better"

## Why this is needed — the measurement, not a theory

`_floor()` (`scripts/checklist_engine.py:3036`) is the only freeze the engine has:
`1 + index of the last non-pending gate`. It freezes what has **already been started**. That
gives the *opening* bookend for free and gives the *closing* bookend **nothing** — every closing
gate is `pending` for the whole run.

Measured on a synthetic Commander spine (`init`..`plan` complete, `execute` in-progress, rest
pending — the ordinary mid-run state):

```
$ ... amend --delta '{"ops":[{"op":"drop","id":"archive"},
                             {"op":"drop","id":"feedback"},
                             {"op":"drop","id":"review"}]}'
amended: dropped archive, dropped feedback, dropped review (authority probe)
exit: 0
```

A Commander deleted its own `review`, `feedback` and `archive` — including the independent-review
step `README.md` calls the corpus's core safety net — with no `--force`. Full evidence:
`.agent-work/567-k/evidence/probe-closing-bookend.md`.

## Scope — files you MAY write

- `scripts/checklist_engine.py`
- `scripts/mcp_spine_server.py` (expected: **prose only** — the `spine_amend` tool needs no schema
  change; three independent design agents each concluded the door already forwards the delta and
  returns `EngineError` through the existing channel. Add a sentence to the tool description so an
  agent learns of the refusal without a failed call. If you find the door needs more than prose,
  **stop and say so in your result** rather than redesigning it.)
- `tests/test_checklist_engine.py` and, if genuinely needed, `tests/test_mcp_spine_server.py`

## Files you MUST NOT touch — hard fences

- `scripts/run_crew.py`, `scripts/install_constellation.py`, either `LAUNCH_ORDER.template.md` —
  **lane J's**, a concurrent lane.
- `map/INDEX.md` — the Admiral's.
- `scripts/generate_spine.py`, `specs/*.spine.toml`,
  `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` — **out of scope and floated**.
- The `*SPINE*.template.json` files — those are **gate g2**, not this gate. Do not pre-empt them.
- **Never run a mutating engine verb against a live spine.** `.agent-work/567-k/spine.json`,
  `.agent-work/567-k/execute.json` and `.agent-work/epic-567-door/spine.json` are LIVE and are
  read-only to you. Copy to a temp dir and drive the copy.

## The change

Implement the **per-gate `bookend` flag** (design candidate B; full text at
`.agent-work/567-k/crew-handoffs/design-B-result.md`, comparison at
`.agent-work/567-k/DESIGN_COMPARISON.md`).

**The declaration form is the human's to change, so isolate it.** Put the "is this gate frozen?"
question behind **one small helper function**. Everything else — the four guard sites — is common
to every candidate. A future swap to a positional rule or a plan-level region key must be a change
to that one helper, not a rewrite. This is a real requirement, not a style note.

1. **One helper**, beside `_floor()` (`:3036`), answering "is this gate a declared bookend?" from
   `task.get("bookend")`. Optional boolean key on the task object, exactly like the existing
   ad-hoc per-task keys the engine already reads with `.get()` (`why_exempt` at `:2374`/`:2683`,
   `override_policy`). There is no task-schema validator to update — confirm that yourself.
2. **`add` (`:3047`)** — a **ceiling**, mirroring the existing `_floor()` refusal at `:3067-3072`:
   an insert may not land after the last bookend-marked gate. Without this, a new gate could be
   appended after `archive` and "frozen finish" would stop meaning finish.
3. **`drop` (`:3076`)** — refuse when the target carries the flag, **regardless of status**. This
   is the guard that closes the measured gap above.
4. **`rescope` (`:3089`)** — same refusal, placed **before** the field overwrite.
5. **`retext-check` (`:3115`)** — same refusal.
   **This one is a deliberate, contested decision — implement it, and understand why.** Design
   candidate A argued the opposite: a bookend whose typo'd check can never be corrected is worse.
   Overridden on this ground: `retext-check` can rewrite a frozen gate's `command` check to
   something trivially true and let it pass, which defeats the freeze completely while leaving the
   gate standing. **A freeze that only stops deletion is not a freeze.** The typo case keeps two
   sanctioned paths that do not require weakening the guard: fix the template and re-instantiate,
   or `waive` the condition under a recorded authority.
6. **Add `"bookend"` to `rescope`'s `overwritable` tuple (`:3099-3100`).** Today nothing could ever
   *set* the flag through the engine. This is the **retrofit path** — it is how a spine already
   running gets frozen without hand-editing, which this repo's doctrine forbids. Because the guard
   in step 4 sits **before** the overwrite, the flag becomes a **one-way latch**: once set, every
   later `rescope` of that gate is refused, including one trying to set `bookend: false`. Assert
   that latch in a test; it is a property, not an accident.

**Hard requirement — backward compatibility.** An **undeclared** plan must behave **exactly** as
it does at `9b38b9d9`. Every spine in flight today, including the two live under this epic,
carries no declaration. A missing key reads as not-a-bookend.

**Preserve `amend()`'s all-or-nothing discipline** (`:3031` build-on-copies, `:3177` commit). A
refused op must leave the checklist **unmutated** — `main()` persists `cl` even on the error path,
so this matters.

**Do not touch `advance(--from_child)` (`:2617`) or `consolidate()` (`:2733`).** The parent/child
verdict seam is out of scope and must survive untouched.

## Required tests

In `tests/test_checklist_engine.py`. Negative tests carry the weight here.

- `drop` of a bookend gate is **REFUSED** — and refused for a `pending` gate specifically, since
  that is the hole today.
- `rescope` of a bookend gate is **REFUSED**.
- `retext-check` of a bookend gate is **REFUSED**.
- `add` that would insert **after** the last bookend is **REFUSED**; an `add` into the middle
  still **succeeds**.
- **All-or-nothing:** a delta mixing one legal op with one bookend-violating op leaves the
  checklist completely unmutated — assert `items` *and* that the legal op did not land.
- **Backward compatibility:** a plan with no `bookend` key anywhere behaves exactly as today —
  `drop` of a pending closing gate still succeeds.
- **The one-way latch:** `rescope {bookend: true}` on an unmarked pending gate succeeds; a
  following `rescope {bookend: false}` on that same gate is REFUSED.
- The reproduction of the measured gap: the three-drop delta from the evidence file is now
  REFUSED on a declared plan.

## Required verification commands (POSIX, absolute paths)

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py
```

Both must pass. Paste the tallies into your result.

## Test mode

Test-led where the surface exists — and it does: `tests/test_checklist_engine.py` already covers
`amend` thoroughly. Write the negative tests **first**, watch them fail against today's engine,
then make them pass. Report that red→green transition in your result; it is the evidence that the
tests can fail.

## Constraints

- The engine under edit is **not** the engine in play: hooks resolve `CLAUDE_PROJECT_DIR` once at
  session launch (#269), so validate in a **fresh process with explicit paths**, never by
  observing this session's own behaviour.
- Match the surrounding code's idiom: `EngineError` with `task_id`/`verb`/`status` kwargs like the
  neighbouring refusals, and a recovery-shaped message. Read `:3080-3085` for the house style.
- Do not reformat, reorganise, or "improve" code you were not asked to change.

## Stop conditions

Stop and report rather than improvising if: the door turns out to need a schema change; a fenced
file would have to change; a required test cannot be made to fail before it passes; or the
backward-compatibility requirement conflicts with the guard.

## Return format

`IMPLEMENTER_RESULT` with a **`Return status`** field whose value is exactly `complete` (lowercase)
when done — the Commander copies it verbatim into an engine artifact match that is exact dict
equality, so any other case or shape leaves the gate permanently unsatisfiable. Include: what you
changed and where (`file:line`), the red→green evidence, both test tallies, anything you refused
to do and why, and a **Workflow Feedback** section including your own mistakes.
