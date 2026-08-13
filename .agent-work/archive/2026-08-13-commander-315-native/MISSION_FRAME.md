# Mission Frame — engine-native worktree isolation against a stored spine origin

Work id: `commander-315-native`. Epic 568, wave 1 recut.

**Map status: DEGRADED-UNPARSEABLE, anchor count 0.** This repo has no architecture map:
`docs/architecture/` is absent, `map/INDEX.md` is an unfilled template and `map/ids.jsonl`
is empty. The orientation receipt at `.agent-work/commander-315-native/map-orientation.json`
hash-pinned the reading I did instead. This frame is therefore cut from that declared
reading, not from map anchor ids — and it deliberately carries **no** anchor-id tokens,
because in a degraded run there is no inventory for one to be a member of.

## Declared reading this frame is built from

- `docs/CHECKLIST_ENGINE_DESIGN.md` — the engine's design record: what the engine owns,
  what a verb may refuse, and why state lives in one file the engine alone writes.
- `docs/CHECKLIST_SCHEMA.md` — the spine schema: top-level keys, check kinds, and the
  `base` field's existing meaning (branch base ref) which this run must not collide with.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project deltas: "Workflow mechanisms and
  verifiers" is a **strengthened durable system**, so the plan owes targeted automated
  tests plus the relevant broader suite.
- `docs/agents/GLOSSARY.md` — `spine`, `gate`, `lease`, `latitude`, `projection`,
  `two-bin rule`, `scoped null`. One name per thing; this frame uses those names.
- `README.md` — repo purpose and layout.

## Intent

Make a spine carry its own repo reference from creation, and have the engine enforce
worktree isolation natively against it. The engine currently cannot answer "am I in the
tree this work belongs to" itself; it delegates the judgment to a subprocess check that a
template author can omit, mis-wire, or delete.

**What this change delivers, stated precisely** (corrected after the cold critic; the first
draft of this frame overclaimed and a reviewer would have certified a property the change
does not have):

- **Coverage.** The judgment applies to every guarded verb on every spine that carries
  `origin`, not only to whichever gate an author remembered to wire a check onto.
- **Unbypassability from the spine.** The comparison lives in the engine. It cannot be
  deleted from a template, cannot be left out of a new role's spine, and cannot be
  pre-satisfied in the JSON.
- **An independent expected side.** The expected value comes from state stamped at
  creation, not from check text a spine author writes.

**What it does NOT deliver.** It is not non-forwardable in the strong sense. The engine's
subject is `Path.cwd()`, and `_run_check_command` (`checklist_engine.py:786`) already runs
command checks with no `cwd=`, so the existing `--here` check reads the *same* ambient
value one indirection later. An agent that prefixes `cd <origin.worktree> &&` to its engine
call satisfies the guard and can still edit in the wrong tree. The guard proves where the
engine process stood, never where the work happened. That limit is real, it is not closed
by this change, and it must not be certified away.

## Affected capabilities (named by path, since no map exists)

- **Spine instantiation** — `scripts/init_work_area.py`. Today it resolves the root, uses
  it for `<repo-root>` substitution, and discards it. After this run it also records it.
- **Engine verb dispatch** — `scripts/checklist_engine.py`, `dispatch()`. The single CLI
  chokepoint every verb already passes through; the lease gate, the trip gate and the
  doctrine rail all hang off it. The native comparison joins them.
- **Worktree isolation verification** — `scripts/verify_worktree_isolation.py`. Unchanged
  by this run. Its `--here` mode stays the Admiral's pre-wave gate and the pasted-output
  self-check; what changes is that it is no longer the *only* place the judgment lives.
- **Spine lifecycle** — `scripts/spine_lifecycle.py`. `build_origin()` already produces the
  `origin` block shape and `open_work()` already injects it. Zero changes; this run makes
  `init_work_area.py` stamp a compatible subset so the two paths agree.

## Structural facts the plan depends on

- `dispatch()` early-returns `heartbeat`, `release` and `current` before the mutating path,
  and already has an actor-authority gate and a trip gate at verb entry. There is an
  existing seam; this run does not invent one. **But "early-returned" is not "read-only"** —
  an earlier draft of this frame said so and was wrong. `heartbeat` (`:1048`) writes
  `last_heartbeat`; `release` (`:1063`) writes `status`/`released_at`; and `main()` persists
  on both the success and the refusal path for every verb except `current` (`:3299-3345`).
  Only `current` is genuinely read-only.
- Because `main()` saves on the `EngineError` path, a refusal raised inside `dispatch()`
  would itself write into the very tree the guard exists to protect — and would write back a
  spine loaded before the refusal, clobbering any concurrent legitimate write. The guard
  must therefore refuse in `main()` **before** `dispatch()` and **without** persisting.
- `instantiate_spine` writes one filename only: `spine.json` (`init_work_area.py:165`).
  Reviewer surveys (`review.json`) and implementer plans (`IMPLEMENTER_PLAN.json`) are
  created by other paths and will not carry `origin`. The guard is therefore inert on the
  child checklists crew subagents actually drive — a real, stated limit of this change.
- `base_dir` is `path.parent` of the spine file. It is **also** the gauge path base and the
  `--from-child` base. The stored root must never be threaded through it.
- `origin` appears nowhere in the engine today and only in `spine_lifecycle.py` elsewhere,
  so stamping it collides with nothing. `validate_spine.py` uses a denylist of known-wrong
  top-level key names, not an allowlist, so a new top-level key validates.
- The hooks do **not** subprocess the engine. `scripts/hooks/spine_rail.py` says so in its
  own docstring and keeps it: it reads the spine state file and reconstructs `current`
  in-process, and its one subprocess is `git worktree list`.
  `scripts/hooks/gauge_writer_hook.py` writes `gauge.json` and never calls the engine.

## Governing constraints and assumptions

- **Engine-native, never a forwarded cwd.** Forwarding a cwd to the subprocess check makes
  the comparison `X == X`, because the stored root and the EXPECTED value in the check text
  derive from the same resolved root at creation. This is the falsified direction.
- **Both halves land together.** The read side is inert without the stamp — it would report
  green while doing nothing, which is the check-that-cannot-fail defect in its purest form.
- **The stored root is a parameter distinct from `base_dir`.** Overloading `base_dir` breaks
  the gauge path and `--from-child`.
- **`scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` are not editable.** If the
  change wants them, stop and float.
- **Fail visibly, no hidden fallback** (inherited universal posture). A spine with no
  `origin` gets today's behaviour exactly — that is a stated fallback, not a hidden one.
- **A check that cannot fail** (inherited, and this repo's `two-bin rule`). Any check this
  run adds must be demonstrated failing in the defective world and passing in the healthy
  one, in the same evidence set.

## Rulings inherited frozen from the launch order

Written without anchor-id tokens on purpose (degraded run, no inventory).

- Ruling **engine-native-not-forwarded-cwd** — settled/measured. Leans on the implement gate.
- Ruling **both-halves-one-change** — settled/human. Leans on the implement gate. Not mine
  to unsettle.
- Ruling **delete-not-repair-init-c0** — settled/measured. **Contradicted by new
  measurement this run** (see below); floated, not taken.
- Ruling **door-not-a-prerequisite** — settled/measured. `open_work()` is not on this path.
- Ruling **root-distinct-from-base-dir** — settled/measured. Leans on the implement gate.
- Ruling **backfill-is-two** — guess, settle during implementation.

## Decision pressure this run forces

- **Verb scope of the native comparison.** Left to my latitude by the launch order.
  Decided, after the cold critic corrected the first cut: guard `MUTATING_VERBS` plus
  `claim` plus `heartbeat`; exempt `current` and `release`.
  - `current` is exempt because it is the one genuinely read-only verb, and inherited
    orchestrator doctrine has an invoker read a subordinate's `current` cross-tree to see a
    `REFRESH REQUESTED:` line. Refusing it would break a doctrine-mandated workflow.
  - `heartbeat` is guarded, reversing the first cut. It writes, and keeping a lease alive
    from the wrong tree defeats stale-lease reclaim. Guarding it costs nothing real, because
    heartbeating requires owning the lease and `claim` is guarded.
  - `release` stays exempt **deliberately, as the one recovery escape hatch**, and this is a
    hole that carries a bounded write — stated, not hidden. A lease on a spine whose
    worktree has been removed at closeout must remain clearable from somewhere, and a
    non-owner release already demands `--force --reason` on the record.
- **Backfill of the live origin-less spines.** Two pre-existed this run
  (`.agent-work/commander-315/spine.json`, `examples/mcp-interactive-demo/spine.json`); this
  run's own spine makes three. Decided at the implement gate.
- **`init.c0`'s fate.** Measured collision, floated to the Admiral. Not decided here.

## Claims this run must re-confirm with evidence

- The native comparison **refuses** an engine standing in the main checkout driving a
  worktree spine that carries `origin`, and **passes** the same spine driven from inside
  its worktree. Both sides, same evidence set.
- A spine with **no** `origin` behaves exactly as it does today. The merged guard
  `tests/test_worktree_precondition_wiring.py` staying green is evidence for **this claim
  only**: every fixture in it builds an origin-less spine by hand, so it is green *by
  construction* under this change and is structurally blind to the new origin-carrying path.
  The launch order's reading — "a green run is evidence both halves landed" — does not hold,
  and the run must not lean on it. The new path needs its own deliberate-breakage coverage.
- The exhaustive fallback shape: `origin` absent, `null`, not a dict, a dict without
  `worktree`, `worktree` empty, and `worktree` not a string all take today's behaviour.
  `validate_spine.py` guards none of these — probed and confirmed, it returns an identical
  fault set for `origin: "not-a-dict"` — so the engine must handle every shape itself and
  must not raise an uncaught `AttributeError` that `main()` would not catch.
- The stamp writes a schema-valid spine that `validate_spine.py` accepts and the engine
  drives without change.
- No new failures against `main`'s own baseline failure set.

## Map confidence, staleness, disputes

- The map is absent, not stale — anchor count 0. Escalated to the Admiral at the context
  step; the launch order already states it. Consequence for this plan: gate anchors are
  file paths and named rulings, not anchor ids, and every structural claim above was read
  from source rather than taken from a map.
- One inherited context claim was **falsified** by measurement: the launch order states the
  wired hooks call the engine being changed. They do not. The plan does not carry a hook
  gate.

## Cold critic — what it changed

A cold critic read this frame and the gate plan with no authoring context and returned 17
confirmed findings. Every one was triaged; the disposition is recorded in
`.agent-work/commander-315-native/PLAN_CRITIC_TRIAGE.md`. Six changed the plan materially:
the intent claim above was overclaimed; `heartbeat`/`release` are not read-only; the guard's
own refusal would have written into the protected tree; the converged design in
`PLAN_ALTERNATIVES.md` had not reached the frozen plan (which said `== Path.cwd()`, a
regression against containment); the two producers of `origin.worktree` emit different value
formats; and `tests/test_explorer_templates.py` breaks by construction and was not in the
gate's test command. Three more became triage candidates rather than work.

## Out of scope

- `scripts/spine_lifecycle.py` — zero changes, ruled.
- `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py` — not editable.
- The `spine_open` MCP door and `open_work()` — not a prerequisite, ruled.
- The 17 cwd-dependent command checks in `skills/*/templates` — measured to need no edits
  under a stored root; not re-derived and not touched.
- Repairing `init.c0` — forbidden by ruling. Deleting it — floated, not taken this run.
