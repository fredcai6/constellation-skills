# Checklist Schema (HTN-derived)

Status: **draft / pre-build.** Companion to `CHECKLIST_ENGINE_DESIGN.md`. First concrete cut of the node + envelope + config shapes. Expect practical implementation to move things.

## What we borrow from HTN, and what we reject

We borrow Hierarchical Task Network vocabulary because it fits:

- **Task** — a unit of work. **Compound** (decomposes into a method) or **primitive** (a leaf, executed directly).
- **Method** — the decomposition of a compound task into an ordered list of subtasks.
- **Preconditions** — what must hold before a task may start. These are the *valve* a conductor hands down: the givens the next tier may rely on.
- **Postconditions** (effects) — what must be true when the task completes. These **are** the close criteria.

We **reject** classic HTN's offline stance — expanding the whole network to primitives before executing. We do **slice-at-a-time lazy expansion**: a conductor expands exactly **one level deeper** (authoring the method for the task in front of it), executes, and the next conductor expands the next level when it gets there. This is what keeps it tractable and human-verifiable — you never hand the human a fully-expanded primitive network to approve; you hand them one slice. It also matches the Commander-is-one-shot rule: plan a level, get it verified, proceed.

Two HTN concessions we make for simplicity now:

- **Ordered methods only** (total order). Partial-order methods are deferred. The Interrogator's question queue — which *should* be semi-ordered — is modeled as an **unordered** method (scattershot) for now.
- A compound task's author may **pin specifics** down the boundary: either a forced method (pre-authored subtasks) or `directives` (forced primitive constraints), for when a constraint forces a specific implementation rather than leaving it to the executor.

## Storage model

A tree is a flat task registry plus a root pointer. The tree is defined by `method.subtasks` (ordered id references) and `anchor.parent`. Flat-with-refs keeps it resumable: load the dict, find the active leaf, continue.

```json
{
  "work_id": "issue-123-slug",
  "root": "t0",
  "config_ref": "charter",
  "tasks": { "t0": { ... }, "t0.understand": { ... }, ... }
}
```

## Task

| field | type | notes |
|---|---|---|
| `id` | string | stable, unique within the tree |
| `type` | `compound` \| `primitive` | compound owns a method; primitive is a leaf |
| `title` | string | short label |
| `imperative` | string | the *do-this-now* instruction surfaced to the executor (tool output is a prompt) |
| `tier` | `commander`\|`pilot`\|`crew`\|`probe` | dispatch hint — which tier executes it |
| `anchor` | object | `{ work_id, parent: task-id\|null, struct: "struct:<id>"\|null }` |
| `preconditions` | `[Condition]` | entry guard; must be satisfied to enter `in-progress` |
| `postconditions` | `[Condition]` | close criteria; must be satisfied to propose `complete` |
| `constraints` | `[string]` | rules; **inherited down the subtree**; forced specifics live here |
| `directives` | `[string]` \| null | forced primitive specifics handed down by the author |
| `method` | `Method` \| null | compound only; **null = unexpanded** (conductor authors it on arrival) |
| `status` | enum | `pending\|in-progress\|blocked\|complete\|skipped` |
| `status_detail` | object | reason/blocker fields required per status (see Status) |
| `evidence` | `[Evidence]` | attached artifacts |
| `accepted` | bool | owner has accepted the returned packet (see accept vs advance, Pinch Points) |
| `rework_count` | int | increments on reopen; compared to `config.rework_cap` |
| `owner` | string | role/tier that authored this task (may mutate structure) |
| `executor` | string \| null | role/tier dispatched to run it (may mutate state only) |

## Method

| field | type | notes |
|---|---|---|
| `ordered` | bool | `true` = total order (default, `strict-sequential`); `false` = scattershot (Interrogator) |
| `subtasks` | `[task-id]` | in order when `ordered` |

`current` walks the tree to the deepest open leaf: descend through `in-progress` compound tasks; within an ordered method, the active subtask is the first non-`complete`/`skipped` one; within an unordered method, any open subtask (executor picks).

## Condition (pre / post)

The unit that makes "gate on shape, not quality" mechanical.

| field | type | notes |
|---|---|---|
| `id` | string | |
| `statement` | string | human/agent-readable assertion |
| `check` | object \| null | how the engine verifies it; `null` = agent/human-asserted |
| `satisfied` | bool | |
| `satisfied_by` | string \| null | evidence-id or note |

`check` kinds:

| `check.kind` | engine verifies | satisfied when |
|---|---|---|
| `command` | runs `check.command` | exit 0 |
| `evidence` | presence of `check.evidence_type` in `task.evidence` | present + shape-valid |
| `review-verdict` | a `review-result` evidence | verdict `APPROVE` (or owner override w/ reason) |
| `user-decision` | a `user-decision` evidence | present (this is a human checkpoint) |
| `task-postcondition` | references `check.task_id` | auto-satisfied when that task is `accepted` |

A `null` check means the engine cannot verify the condition itself — it records the agent's/human's assertion and leans on the two-tier verification (reviewer + invoker) for truth. **The engine enforces presence and shape; it never judges quality.**

The `task-postcondition` kind is what chains an ordered method: a subtask's precondition can reference the prior subtask's id, so state carried forward is mechanical, not asserted.

## Evidence

| field | type | notes |
|---|---|---|
| `id` | string | |
| `type` | enum | `command-output\|review-result\|file-diff\|user-decision\|cartographer-verification` |
| `payload` | object | command output, diff ref, decision text, verdict, packet ref |
| `produced_by` | string | role/tier |
| `ts` | string | |

## Envelope (a projection, not stored)

The envelope is the task projected across a tier boundary and translated to the executor's language. It is *derived* from the task, not a separate record.

- **down (dispatch):** `imperative`, `preconditions` (givens), `postconditions` (success target), union of inherited `constraints`, `directives`, the evidence types implied by postcondition checks, and stop conditions.
- **up (return):** `task.id`, claimed status, `evidence[]`, per-postcondition satisfaction, deviations (skips / OBE with reasons), and `signals[]` (bubbled new-info / out-of-scope / triage candidates).

## Config (Charter-owned)

| field | type | notes |
|---|---|---|
| `rework_cap` | int | reopen attempts per node before escalation up a tier / to the user |
| `replan` | `abort-and-reissue` | Commander is one-shot; a failed plan ends the run and re-issues |
| `human_checkpoints` | `[string]` | the **rigor dial**: which checkpoints require `user-decision`. e.g. `understand.done`, `plan.approved`, `architecture.intent`, `run.accept` |
| `rules_root` | `[string]` | project-wide constraints inherited from the root |

## Status

```
pending ──(preconditions satisfied)──▶ in-progress
in-progress ──(postconditions satisfied + evidence shapes present)──▶ complete   [a proposal]
in-progress ──(blocker)──▶ blocked
{any} ──(reason; OBE)──▶ skipped
complete ──(owner reopen, reason)──▶ in-progress   (rework_count++; escalate at cap)
complete ──(owner accept)──▶ accepted/closed
```

Required `status_detail`:

- `skipped` → `reason` (the OBE justification)
- `blocked` → `blocker`, `authority_needed`, `next_action`
- `complete` → at least one `evidence` ref (or note)
- reopen → `reason`

A parent compound task cannot reach `complete` until every subtask in its method is `complete`/`skipped` and accepted.

## Worked example (abridged)

```json
{
  "id": "t0.execute.g1",
  "type": "primitive",
  "title": "Add fail-safe bounds check to controller",
  "imperative": "Implement the bounds check in controller.m per directives; tests must pass and a reviewer must APPROVE.",
  "tier": "crew",
  "anchor": { "work_id": "issue-123", "parent": "t0.execute", "struct": "struct:ctrl-core" },
  "preconditions": [
    { "id": "p1", "statement": "Plan approved", "check": { "kind": "task-postcondition", "task_id": "t0.plan" }, "satisfied": true, "satisfied_by": "t0.plan" }
  ],
  "postconditions": [
    { "id": "c1", "statement": "Unit tests pass", "check": { "kind": "command", "command": "make test" }, "satisfied": false },
    { "id": "c2", "statement": "Reviewer approves", "check": { "kind": "review-verdict" }, "satisfied": false }
  ],
  "constraints": ["must work with MATLAB Coder", "fail-safe on out-of-range input"],
  "directives": ["saturate, do not throw, on out-of-range"],
  "method": null,
  "status": "in-progress",
  "evidence": [],
  "accepted": false,
  "rework_count": 0,
  "owner": "pilot",
  "executor": "crew:implementer"
}
```

Note the inherited `constraints` (handed down from a `struct:ctrl-core`-anchored ancestor) and the `directives` (a forced specific — saturate, don't throw). The implementer authors no method (it's primitive); it just satisfies the postconditions and returns evidence. The reviewer crew verifies `c2`; the engine checks `c1` by running `make test`.

## Engine verbs ↔ schema

| verb | reads/writes |
|---|---|
| `current` | walk to deepest open leaf; emit its `imperative` |
| `criteria <id>` | emit `postconditions` + implied evidence types |
| `expand <id> --method …` | compound only; author `method` (the slice); owner-only |
| `start <id>` | check `preconditions`; `pending → in-progress` |
| `advance <id> --evidence …` | check all `postconditions` (run command checks, verify evidence shapes); `→ complete` (proposal) |
| `skip <id> --reason …` | `→ skipped` (state op; universal executor right) |
| `block <id> …` | `→ blocked` with required detail |
| `append <id> …` | unordered methods only; executor structural add (Interrogator) |
| `reopen <id> --reason …` | owner-only; `complete → in-progress`; `rework_count++`; escalate at cap |
| `accept <id>` | owner finalizes; `complete → accepted` |
| `signal <id> …` | attach a bubbled `signal` (new-info / out-of-scope / triage) for the owner |

## Pinch points (flagged early)

1. **accept vs advance.** Modeled as distinct (`advance` = executor proposes `complete`; `accept` = owner finalizes). Collapsing them loses the "return is a proposal" property. Keep distinct unless it proves noisy.
2. **Lazy expansion vs handed-down postconditions.** A task's postconditions are authored by its *parent*; its method by its *own* conductor on arrival. If, on expansion, the conductor finds the postconditions unachievable — does it re-author its own slice (allowed: it owns its method) or bubble up (required: it does **not** own its parent's postconditions)? Proposed rule: **re-authoring your own method is free; changing handed-down pre/postconditions is a signal up.** One-shot applies at the Commander tier; lower conductors may re-slice within the frozen plan.
3. **Condition expressiveness.** Free-text `statement` + optional `check`. The `task-postcondition` check is the only structured dependency. If chains get richer (a precondition needing *several* prior postconditions, or negation), conditions may need a small predicate grammar. Resisting that until forced.
4. **Unordered `current`.** With `ordered:false`, `current` is ambiguous (any open subtask). Fine for scattershot questions; revisit if a real partial order (some questions block others) becomes necessary.
5. **Inherited constraints — union or override?** Currently union down the subtree. A child that must *relax* an ancestor constraint has no mechanism. Probably fine (relaxation should be rare and explicit), but flag it.
6. **Evidence payload typing.** Left loose (`object`). Reviewer-result vs command-output have very different shapes; the engine only shape-checks minimally. May need per-type payload schemas before the engine can validate `review-verdict` reliably.
</content>
