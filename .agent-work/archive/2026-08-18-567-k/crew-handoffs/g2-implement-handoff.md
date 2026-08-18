# Implementer handoff — g2: declare the bookends in the role spine templates

**Result path (write here before ending your turn — that write is the delivery):**
`.agent-work/567-k/crew-handoffs/g2-implement-result.md`

**Suggested Model Tier:** sonnet. A small, well-specified JSON edit to three files, plus one test.

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Branch: `feat/567-k-one-spine-mutable-middle`.

## Assigned task

Gate `g1` taught the engine to honour a `"bookend": true` declaration on a gate. **Nothing
declares one yet**, so the guard currently protects nothing. Declare the bookends in the three
role spine templates this lane owns, and pin the declaration with a test.

## Exactly what to declare

| Template | `bookend: true` on | and on |
|---|---|---|
| `skills/commander/templates/COMMANDER_SPINE.template.json` | `init` | `archive` |
| `skills/admiral/templates/ADMIRAL_SPINE.template.json` | `init` | `closeout` |
| `skills/explorer/templates/EXPLORER_SPINE.template.json` | `init` | `route` |

**On those gates and no others.** Add the key to the task object, beside the existing per-task keys
(`status`, `rework_count`, and the ad-hoc ones like `why_exempt`). Do not restructure, reorder or
reformat anything else in these files — a noisy diff here is a real cost, because these templates
are read constantly.

## Why these gates, so you can check the reasoning rather than take it

- **The opening gate** of each spine claims the lease and establishes provenance. A run that can
  amend it away can start without ever claiming, which is the thing the lease exists to prevent.
- **The closing gate** is the one measured to be exposed. A Commander at `execute` was observed
  deleting its own `review`, `feedback` and `archive` in one delta, exit 0 — evidence at
  `.agent-work/567-k/evidence/probe-closing-bookend.md`. `archive` is where the lease is released
  and the work is committed; `closeout` is where an epic is dispositioned; `route` is where an
  explorer's confirmed spec is handed on. Each is the gate that makes the run's output reach the
  world.
- **Only the outermost two per spine.** The human asked for "frozen required gates at the start and
  finish… what we do in the middle is squishy." Freezing more than the ends is not what was asked
  for. In particular do **not** freeze Commander's `review` or `feedback` even though the same
  probe deleted them — they sit inside the middle, and `archive` at the end is what keeps the run
  from terminating early.

**If you think one of these six choices is wrong, say so in your result rather than silently
changing it.** The reasoning above is the Commander's; you are allowed to disagree with it.

## Also required: a test that pins the declaration

Add to `tests/test_checklist_engine.py` (or a more apt existing test module if one clearly fits
better — say which and why) a test asserting, **per template, the exact set of bookend-flagged
gate ids** — that the intended two carry it and **every other gate does not**. An assertion that
merely checks "at least one gate is flagged" would pass in a world where the flag landed on the
wrong gate; this test must fail in that world.

The templates must still be valid: confirm each still parses and still instantiates. Say which
command you used to confirm instantiation.

## Scope — files you MAY write

- The three `*SPINE*.template.json` files named above.
- `tests/test_checklist_engine.py` (or the test module you justify instead).

## Files you MUST NOT touch — hard fences

- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py` — **gate g1, already integrated.**
  If the engine looks wrong to you, that is a finding, not an edit.
- `skills/implementer/templates/IMPLEMENTER_PLAN.template.json`, `specs/*.spine.toml`,
  `scripts/generate_spine.py` — **deliberately out of scope and floated to the Admiral.** Here is
  why, so you do not helpfully "finish the job": `IMPLEMENTER_PLAN.template.json` is **compiled**
  from `specs/implementer.spine.toml` by `generate_spine.py`, whose `_compile_gate` (`:669-684`)
  returns a **fixed field list with no `bookend` key**. A declaration added there would survive
  until the next regeneration and then vanish silently. This repo has already had exactly that
  incident (`tests/test_generate_spine.py:1694-1700`, "the artifact diverged from its source").
  Adding it anyway would create a durability hole that looks like a delivered feature.
- `scripts/run_crew.py`, `scripts/install_constellation.py`, either `LAUNCH_ORDER.template.md`
  (lane J), `map/INDEX.md` (the Admiral).
- **Never run a mutating engine verb against a live spine.** `.agent-work/567-k/spine.json`,
  `.agent-work/567-k/execute.json`, `.agent-work/epic-567-door/spine.json` are LIVE and read-only.
  Copy to a temp dir and drive the copy.

## Required verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_generate_spine.py tests/test_init_work_area.py
```

Then prove the declaration is live end to end, on a **copy**, in a fresh process: instantiate or
copy the Commander template, mark `init`..`plan` complete and `execute` in-progress, and confirm
`{"ops":[{"op":"drop","id":"archive"}]}` is now **REFUSED**. Paste the refusal.

## Test mode

Test-led for the pinning test: write it first, watch it fail against the undeclared templates,
then add the declarations and watch it pass. Report the red→green.

## Stop conditions

Stop and report rather than improvising if: a template will not instantiate after the edit; the
pinning test cannot be made to fail first; or you believe one of the six gate choices is wrong.

## Return format

`IMPLEMENTER_RESULT` with a **`Return status`** field of exactly `complete` (lowercase) — the
Commander copies it verbatim into an exact-dict-equality artifact match, so any other case leaves
the gate permanently unsatisfiable. Include: the diff summary, the red→green evidence, the pasted
refusal from the end-to-end proof, both test tallies, anything you refused to do and why, and a
**Workflow Feedback** section including your own mistakes.
