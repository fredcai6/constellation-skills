# Checklist Schema (HTN-derived)

Status: **built / shipped.** Companion to `CHECKLIST_ENGINE_DESIGN.md`. The engine (`scripts/checklist_engine.py`) is built and in use; this schema tracks the shipped behavior, including the epic-#178 Context-Governor additions (`why_trail`, `why_exempt`, why-capture `advance`, the `DIGEST:` / `REFRESH REQUESTED:` display, the `refresh-request` evidence type, and the Trip two-band gate policy).

## Scope: one agent, one plan

A checklist is **one plan that one agent works through** — not the whole multi-tier hierarchy in a single file. The agent is usually *handed* the plan and executes against it. Who handed it down, and how context is translated across tiers, is the **handoff / envelope** concern (see the design doc), not part of this schema. There are therefore **no owner/executor tags** — from the schema's point of view there is just the agent and its plan.

Composition is **by reference, not by nesting.** A gate that delegates work points to a **child checklist** (a separate artifact / work-id); it does not inline the sub-agent's tasks. Every agent has its own plan: Commander (spine and execute.json), implementer, reviewer. The implementer's plan is self-authored, full of primitives, and simply never handed further down.

## Who writes a checklist (epic-559/c2)

Until now every checklist in this corpus was hand-authored. `scripts/generate_spine.py` is the first
**producer** of the shape this document describes: it compiles a TOML spec into a checklist and calls
`scripts/validate_spine.py`'s `validate()` as the literal last statement before writing, so it cannot
emit anything the oracle would reject. The spec has **no raw-command field** — a check is one of five
typed kinds (`qualitative`, `pytest`, `script`, `population`, `artifact`), each with a generation-time
probe — because a check typed from memory is where hand-authored spines actually broke.

Nothing about the on-disk format changed. The engine is unchanged; this is a new writer of an existing
shape, and `docs/agents/*` is untouched.

Three engine behaviours this document already implies were measured directly while building it, and
their **consequences** are worth stating here because a reader can otherwise miss them:

- **No artifact-based gate can be enforced on a `survey`.** §Two checklist types already records that
  `null`/`artifact`-kind postconditions on a survey item are unevaluated by `record` (#422/#328). The
  consequence, verified by driving a survey to consolidation: `consolidate` reads only each item's
  `result` field, so an `artifact` postcondition on a survey item is never consulted by *either* closing
  verb. A survey reaches `APPROVE` with such a postcondition unsatisfied and no evidence attached. On a
  `gated` gate, `advance` checks every postcondition with no kind filter, so the same postcondition is
  genuinely load-bearing there. The asymmetry is real and pre-existing; the generator now refuses to
  emit a postcondition the engine will never consult, and states the non-enforcement instead.
- **`config_ref` is a crash surface.** `load_config` calls `json.loads` on any `config_ref` that
  **exists**, so a `config_ref` pointing at a real non-JSON file raises an unhandled `JSONDecodeError`
  before any rail text can print. A *missing* path falls through to `{}` and is harmless, which is why
  every shipped template's nonexistent `docs/agents/engine-config.json` is fine. `validate_spine.py`
  carries no fault for the crashing case.
- **A `command` check receives no `cwd`.** Already noted in `init_work_area.resolve_spine`'s docstring
  (#341); measured live here as a check that silently found nothing when run from outside the repo.
  Every command the generator emits is therefore anchored `cd <repo-root> && …`.

## Two checklist types

Every checklist is an ordered list of items and declares one type:

| type | walk | append | item failure | completes when | output |
|---|---|---|---|---|---|
| `gated` | ordered; satisfy each to advance | no | **blocks** (rework / reopen) | every item complete or skipped | the work is done |
| `survey` | visit every item | **yes** (extend from context) | **recorded, never blocks** — except a `command`-kind postcondition on the item (#422/#328) | every item visited (resulted or skipped) | a **consolidated** result |

- **`gated`** is execution: the Commander spine, Commander's execute.json, the implementer's own plan. Ordered, blocking, fixed.
- **`survey`** is inquiry / verification: the **Interrogator's questions** and the **reviewer's checks** are the same shape — hit every item, add items as context warrants, then consolidate (a resolved understanding; an APPROVE/BLOCK verdict). A survey is handed a *starting* list and told "verify these, and add more based on the context we gave you." Nothing gates *appending*; a `command`-kind postcondition on an item is the one exception to "nothing gates anything" — `record <id> --result pass` REFUSES if that command fails (`zc-consolidate`, `r6-fowler`), mirroring `advance`'s check the same way. `record --result fail` is never gated by it. `null`/`artifact`-kind postconditions on a survey item remain unevaluated by `record` (#422/#328's scope).

**Append is inherent to `survey`, not a separate flag**; `gated` never appends.

## What we borrow from HTN, and what we reject

Borrow the vocabulary: a **task** with **preconditions** (entry valve) and **postconditions** (effects = close criteria). A checklist's ordered `items` list is the HTN **method**; **decomposition** is a delegating gate referencing a child checklist.

Reject HTN's offline stance (expand the whole network to primitives before executing). We do **slice-at-a-time lazy expansion**: a conductor expands exactly one level (authors the plan in front of it), executes, and the next agent expands the next level when it gets there. This keeps it tractable and human-verifiable — you never approve a fully-expanded primitive network, just one slice. Trees are shallow in practice and bottom out at primitives.

## Storage model

```json
{
  "work_id": "issue-204-execute",
  "type": "gated",
  "config_ref": "charter",
  "items": ["g1", "g2"],            // ordered item ids
  "tasks": { "g1": { Task }, "g2": { Task } },
  "consolidation": null,            // survey only: the consolidated result (verdict / understanding)
  "triage_candidates": [],          // out-of-scope discoveries, bubbled to the parent agent
  "blockers": [],                   // stuck items, bubbled to the parent agent
  "amendments": [],                 // audit log of `amend` deltas: gated, plus a survey's retext-check (see Amend delta)
  "why_trail": [],                  // optional, append-only: the running-understanding trail (see Why-capture)
  "trip_ledger": [],                // optional, append-only: BEGINs judged at/over the hard line (see Trip ledger)
  "refusals": 0,                    // optional: checklist-scoped refusal tally, ARMED by `claim` (see below)
  "origin": null,                   // optional: the worktree this file was created in (see below)
  "engine_session": null            // optional: actor-authority lease over this checklist's STATE (see below)
}
```

### `refusals` — this checklist's refusal tally

A monotonic count of the refusals taken against this checklist: one per `EngineError` that reaches `main()`'s refusal path and is persisted there. Every **increment** happens at the CLI boundary — no verb function counts a refusal — while the initial arming write (`cl.setdefault("refusals", 0)`) sits inside `claim()`, deliberately, for the reason in the first bullet below. It is the **only** engine-state record that a refusal happened at all: the journal sidecar is success-only by construction (`append_journal_entry` runs after the refusal path has already returned), so before this counter a refusal left no trace in any file.

Three properties are load-bearing, and each exists because the field feeds `docs/EPISODE_STORE.md`'s mechanical bin, where a plausible wrong number is worse than an absent one:

- **Armed by `claim`, not created on first refusal.** A fresh, reclaimed or forced lease sets `refusals: 0` via `setdefault`; the idempotent same-session resume does not. So `0` reads as *"an engine that counts refusals drove this run and none happened"*, and **absence** reads as *"this checklist predates the counter"*. Those are different facts and they stay tellable apart. The arming write is the one piece of this counter that lives in a verb, and it has to: it must sit *after* `claim`'s idempotent-resume early return, or a same-session re-claim would backdate a `0` over refusals that really happened.
- **Only an armed counter increments.** A refusal on a checklist with no `refusals` key leaves it absent rather than writing `1` onto a run whose real total is unknown.
- **Checklist-scoped, not step-scoped** — unlike `rework_count`, which lives on the Task. A refusal does not always name a task (an unknown item id, a lease conflict), so a per-step tally would silently drop exactly those. A **malformed verb** is deliberately not in that list: argparse exits `2` before the checklist is ever loaded, so it is never counted.
- **Scoped to the FILE, not to the leaseholder — and say it that way.** Measured, not theoretical: a refusal from a *foreign* session increments the owning run's tally (`start b --session-id SOMEONE-ELSE` against a held lease → exit `1`, `refusals: 1 → 2`). Any teammate, parent poll, or stale-lease retry against this checklist counts. So the honest reading is *"refusals taken against this checklist"*, not *"refusals this agent took"*. Filtering to the leaseholder's own session would be a change of meaning with its own under-count — a refusal where `--session-id` was simply forgotten is genuinely this run's — and is tracked as separate work rather than guessed at here.

Fully backward compatible: no existing field changes meaning, and every reader works unchanged on a checklist that lacks the key.

`triage_candidates` and `blockers` are honest, separate bubble-up channels (no vague "signals"). Both surface to the **parent agent** first; the parent escalates to the human only if it cannot resolve them. Triage drains `triage_candidates` in clean-up. `amendments` is a separate append-only audit log: each `amend` verb (gated, plus a survey's `retext-check`) appends one entry `{ts, reason, authority, ops:[...]}` recording an intentional mid-run re-plan (see *Amend delta — intentional mid-run re-planning*). The field is created lazily on the first amendment. `why_trail` is a separate append-only trail of running-understanding records, one appended per non-exempt `advance` (see *Why-capture — the running-understanding trail*); it too is created lazily on the first write.

### `origin` — the worktree this file belongs to

An optional top-level block naming where this checklist was created. Two producers write it, and the engine reads one field of it:

```json
"origin": {
  "work_id": "issue-204-execute",
  "worktree": "/home/dev/wt/issue-204",   // the ONLY field the engine reads
  "opened_by": "init_work_area"
}
```

| field | written by | meaning |
|---|---|---|
| `work_id` | both | the checklist's own work-id, repeated here |
| `worktree` | both | the tree the file was created in; `spine_lifecycle.build_origin` stores `str(Path(worktree))` (native separators), `init_work_area.instantiate_spine` stores `Path(root).resolve().as_posix()` |
| `opened_by` | both | `spine_open` or `init_work_area` |
| `branch` / `base` / `opened_at` / `parent` | `spine_lifecycle.build_origin` only | the rest of `LIFECYCLE_CONTRACT.md` section 3. `init_work_area` does not know them and **omits** them rather than emitting a plausible wrong value |

`instantiate_spine` stamps the block with `setdefault`, so a template that already carries an `origin` keeps its own.

**What reads it: nothing that decides anything (#315/#568, retired by #609).** `origin.worktree` is **provenance**. It records where a spine was created, for a human or a reconciler reading the file afterwards, and no engine path reads it to decide whether a verb may run.

It used to. On every guarded verb, `origin_worktree_refusal` compared `origin.worktree` against a worktree toplevel the engine resolved from its own ambient cwd, and printed `REFUSED:` to stderr and exited `1` without writing the file when the two disagreed. That predicate, the `ORIGIN_GUARDED_VERBS` / `ORIGIN_EXEMPT_VERBS` sets that fed it, and the per-verb `git` call that supplied the other side are all deleted from `scripts/checklist_engine.py`. **This supersedes the 2026-08-15 worktree-identity ruling** (equality rather than containment, #588): that ruling settled how to resolve the two sides of a comparison that no longer exists.

**Removing it removed no guard *wherever a lease exists*, and widened the leaseless path.** The comparison answered *where am I*, never *is this mine* — ownership is the **lease** (`engine_session`, below) — but that holds only where a lease is actually held. `require_session` gates mutating verbs **only once an active lease exists** and returns early otherwise, and `_active_lease` reads a **released** lease as absent. So on a spine with **no active lease** — never claimed, or claimed and since released — the origin comparison was the *sole* refusal, and the engine now asserts **nothing** about location. Measured base-vs-tree, driven from a foreign worktree: `start` and `attach` on a never-claimed spine, and `start` after the lease was released, all went from `REFUSED` / exit 1 to **exit 0, writing state into a tree the agent is not standing in**. On a spine under an **active** lease held by another session, nothing changed — refused before, refused after.

**That widening is accepted, deliberately, and it is not a no-op.** A `cd <worktree> &&` prefix defeated the comparison, so it was never a security boundary — its own docstring had already withdrawn that claim — but **a forgeable guard is not the same as no guard**, and what is being accepted here is a widening on the leaseless path rather than a subtraction that changed nothing. What the comparison genuinely had, coverage over every verb and an expected side a spine's own text could not edit, it had over a *location* question the engine no longer asks: **the engine reads no location, ambient or derived.** There is no second value that can disagree with the first, and no ambient reading a check command could forge by `cd`-ing first, because the engine no longer asks the question anywhere.

The lexical rule that derives a worktree from a spine's path is **not** retired — only the engine's copy of it is. The rule lives in the stdlib-only hook, as `spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s case table is its specification. The engine-side copy was deleted in #609 g2 under `ADMIRAL_RULING-2` N2: it had **two** consumers — the shape question inside `origin_worktree_refusal`, deleted by that same gate, and #315's `cwd` thread, re-homed to #610 by `ADMIRAL_RULING-1` R3 — and a third that `ADMIRAL_RULING-1` R2 withdrew before it ever existed. Three sound decisions in a row, and a definition nothing calls is not shipped. It re-lands in #610's wave together with #315 — the consumer that threads `cwd` into the engine's check runner — and re-derives against that same table.

One consequence worth stating plainly: the per-template `command` check that used to assert the same thing — `verify_worktree_isolation.py --here` on the Commander spine's `init` precondition `c0` — was deleted in #315/#568 in favour of the engine-native comparison, and that comparison is now gone too. **Nothing checks at engine level that an agent is standing in the spine's worktree.** That is deliberate: standing somewhere was never owning something, and the lease is unchanged — which, per the paragraphs above, leaves a spine with **no active lease** guarded by nothing at all. `scripts/verify_worktree_isolation.py` remains available to any caller that wants the location assertion explicitly.

**Every shape is inert.** `origin` absent, `null`, a string, a list, or `{}`; `worktree` absent, empty, or not a string — none of it changes engine behaviour, because none of it is read. `tests/test_spine_origin_isolation.py::TheStampIsProvenanceNotADecisionInput` pins that by driving the same guarded verbs against the same spine differing only in `origin.worktree` and demanding one answer for every value; it also pins that both producers still write the stamp, so the pairing "written, and read by nothing" goes red if either half breaks.

## Engine session — actor authority over the state

The engine owns canonical state and enforces *mechanism*. It also enforces **actor authority** over that state: a single, leasing agent owns the right to mutate a given checklist at a time. A lost-and-resurrected parent session once produced two controlling agents in one worktree; the lease refuses that conflicting mutation. Authority is over the checklist **state**, not over each item — there are still no per-task owner/executor tags (see Scope).

A claimed lease lives in the optional top-level `engine_session`:

```json
"engine_session": {
  "session_id": "commander/issue-420/attempt-2",
  "status": "active",                  // active | released
  "claimed_at": "<iso8601>",
  "last_heartbeat": "<iso8601>",
  "claimed_by": "commander",           // role that claimed it (advisory)
  "worktree": ".",
  "previous_session_id": "commander/issue-420/attempt-1",  // set on takeover/reclaim, else null
  "takeover_reason": null              // set on force takeover / stale reclaim, else null
}
```

| field | type | notes |
|---|---|---|
| `session_id` | string | the owning session; passed to mutating verbs as `--session-id` |
| `status` | `active`\|`released` | only an **active** lease gates mutation |
| `claimed_at` / `last_heartbeat` | iso8601 | real timestamps; staleness is `now - last_heartbeat > lease_stale_seconds` |
| `claimed_by` | string | role (advisory audit) |
| `worktree` | string | where the session runs |
| `previous_session_id` | string \| null | the prior owner, recorded on force takeover or stale reclaim |
| `takeover_reason` | string \| null | why the takeover happened (force requires a non-empty reason) |

### The backward-compat gate

**A checklist with no `engine_session` behaves exactly as before:** mutating verbs work without `--session-id`. Session enforcement only kicks in **once a lease has been claimed** (an active `engine_session` exists). `--session-id` is optional on every mutating verb; it is only required, and only checked, once an active lease is present. No shipped template requires a lease except the Commander spine, which claims one at `init` and releases it at `archive`.

### Leasing verbs

| verb | shape | effect |
|---|---|---|
| `claim` | `--session-id <id> --claimed-by <role> [--worktree .] [--force --reason "..."]` | create an active lease (none exists); **idempotently resume + refresh heartbeat** if the same `session_id` already owns it; **refuse** if a different active, non-stale lease exists. `--force --reason "..."` takes over an active/ambiguous lease, recording `previous_session_id` + `takeover_reason`; force requires a non-empty reason. |
| `heartbeat` | `--session-id <id>` | refresh `last_heartbeat`; only the owning session may heartbeat |
| `release` | `--session-id <id> [--force --reason "..."]` | mark the lease `status: released` (closed); only the owning session may release, unless `--force --reason` overrides. After release a new `claim` succeeds. |

### Mutating verbs and stale leases

Once an **active** lease exists, the state-changing verbs (`start`, `advance`, `record`, `consolidate`, `skip`, `block`, `resume`, `reopen`, `append`, `amend`, `attest`, `waive`, `attach`, `flag-candidate`) **refuse** unless `--session-id` matches the active lease's `session_id`. The read-only `current` needs no session and reports active-lease metadata when present.

A lease whose `last_heartbeat` is older than `lease_stale_seconds` is **stale**. Staleness gates **non-owners only** — it answers "has the owner gone quiet long enough that someone else may seize the lease?" The rightful **owner is never blocked by its own staleness**: every mutating verb the owner issues **and that succeeds** refreshes `last_heartbeat` (the completed work itself is the liveness signal), so an actively-working owner never goes stale and a genuine idle gap self-heals on the owner's next successful verb — no re-claim, and **no takeover record** (resuming your own work is not a takeover). A **refused** mutating verb (one that passes the ownership gate but the verb itself raises — e.g. `start` on an unmet precondition or `advance` on a failing postcondition) does **not** refresh `last_heartbeat`, even though `main()` still persists any state it mutated on the error path: a session that only issues failing verbs must still be able to go stale and be reclaimed. A **different** session against a stale lease is still **refused with an instruction to `claim` first**; that reclaim records the prior session in `previous_session_id`. Timestamps are real (the engine has a single `_now()` time hook); staleness is computed by parsing `last_heartbeat`.

## Task

| field | type | notes |
|---|---|---|
| `id` | string | unique within the checklist |
| `title` | string | short label |
| `imperative` | string | the *do-this-now* instruction surfaced to the agent (tool output is a prompt) |
| `preconditions` | `[Condition]` | *optional*; an unmet precondition **fails** the task — hard dependencies only |
| `postconditions` | `[Condition]` | `gated`: **required (≥1)**. `survey`: usually none — the item *is* the check |
| `constraints` | `[string]` | rules; inherited down a delegated child; forced specifics |
| `anchors` | `{category: [string]\|string}` \| `[string]` \| absent | *optional*; map-context carried down from the mission frame at plan time — categories are `structural`/`capability`/`constraint`/`decision`/`evidence`/`confidence_flags` per the Commander's `MISSION_FRAME.template.md`, though the engine does not enforce that set. A category's value is a list of strings, or (e.g. `EXECUTE_PLAN.template.json`'s `g1-review` gate: `{"inherits": "..."}`) a single bare string; a legacy/simple gate may instead carry a flat `[string]`. When populated, `current` renders it (issue #420) — see *Rendering* below. |
| `directives` | `{name: {…contract}}` \| `[string]` \| null | *optional*; forced primitive specifics handed down — a standing contract the gate must satisfy. The corpus carries the **dict** shape: a directive name mapping to a nested contract dict (e.g. `replan_input` → `{template, output, evidence_fields, classifications, check}`). The flat `[string]` form is also valid and is what the `add`/`rescope` amend ops build. When populated, `current` renders it (issue #433) — see *Rendering* below. |
| `context_refs` | `[{root, path, required}]` \| absent | *optional*; an ordered list declaring which files `scripts/context_manifest.py` projects for this task — `root` is one of `skill`\|`repo`\|`durable`, `path` is a posix-relative path under that root, `required` is advisory (not enforced by the producer). Absent means an empty manifest; declaration order is content and is never sorted. The declaration sits *beside* the `imperative` prose, not in place of it — `scripts/verify_context_declaration.py` lints that every declared path appears verbatim in the task's own `imperative`. |
| `child_checklist` | work-id \| null | a **delegating** gate: the sub-plan this gate waits on |
| `map_check_note` | string | *optional*; **template-only, read by no code.** Prose parked beside the `imperative` it qualifies, addressed to whoever EDITS that step's check rather than to a run following it — why the check is worded and placed as it is, what it does and does not prove, and which cheap-looking fix would destroy the property. `render_human` emits a fixed field set (`imperative`, conditions, `constraints`, `anchors`, `directives`), so a note costs a run nothing. Same role as `context_headroom_note`. Carried by the Commander spine's `context` and `plan` steps |
| `why_exempt` | bool | *optional*; **opt-out, default NOT exempt.** A gate WITHOUT `why_exempt: true` (missing key included) must supply a running understanding on `advance` — see *Why-capture*. A missing key is treated as not-exempt (**fail-closed**), so a legacy gate refuses a why-less advance cleanly rather than skipping capture |
| `status` | enum | `pending \| in-progress \| blocked \| complete \| skipped` |
| `status_detail` | object | per-status required fields (see Status) |
| `result` | `pass`\|`fail`\| null | **survey only**: the check's outcome |
| `finding` | string \| null | **survey only**: what the check found |
| `evidence` | `[Evidence]` | attached artifacts |
| `bookend` | bool | *optional*; **opt-in, default NOT a bookend.** A gate with `bookend: true` is a **frozen bookend** (#634): `amend` refuses `drop`, `rescope` and `retext-check` on it **regardless of status**, and refuses an `add` that would land after the last bookend. A missing key reads as not-a-bookend, so an undeclared plan behaves exactly as before. Settable through the engine via `rescope` — and because the refusal precedes the overwrite, the flag is a **one-way latch** (a later `rescope` unsetting it is refused). See *Bookends — the frozen ends of a mutable plan* |
| `rework_count` | int | reopen count vs `config.rework_cap` |

There is no `owner`/`executor` (see Scope) and no `compound`/`primitive` flag — a gate is "delegating" iff `child_checklist` is set, otherwise it is a primitive the agent does itself.

### Rendering — which Task fields `current` shows (issues #420, #433)

`current`'s projection (`state()`/`render_human()` in `checklist_engine.py`) renders a populated `constraints` block, a populated `anchors` block (all three shapes above) and a populated `directives` block on the active gate; each is omitted entirely when absent or empty, so an unpopulated field adds no output. This closed a gap where those fields carried real corpus content the engine never surfaced — `constraints`/`anchors` under #420, and `directives` under #433, which found 8 populated blocks in the corpus (including the shipped Commander spine's own `execute` gate) whose standing instruction never reached the agent it bound. Both live `directives` shapes render: the key-to-nested-contract-dict shape the corpus carries, and the flat `[string]` the table above declares.

The completeness property test in `tests/test_checklist_engine.py` (`TaskFieldCompleteness`) enumerates the Task fields above and fails — naming the offending field — if a populated field goes unrendered. #433 made that property *capable* of failing: a total leaf extractor (the previous one returned nothing for the nested-dict shape, so the check asserted nothing while reporting green), a per-field ledger in place of a single flag that let any field cover for any other, and an assertion that the fixture's key set is a superset of the engine's own Task builder, so a field added to the engine and forgotten in the fixture fails mechanically. An in-suite negative self-test proves the assertion path can actually go red. Residual limit: a field introduced only by a template — carried in a shipped checklist JSON but built by neither the amend-task builder nor `append()` — is still invisible to the property and needs a human to add it to the fixture.

## Condition (pre / post)

A condition is an assertion. The engine can mechanically verify only two kinds of thing; everything else is asserted and verified socially (the dependent agent, the reviewer, the human).

| field | type | notes |
|---|---|---|
| `id` | string | |
| `statement` | string | human/agent-readable assertion |
| `check` | object \| null | how it is verified; `null` = qualitative/asserted |
| `satisfied` | bool | |
| `satisfied_by` | string \| null | evidence-id or note |
| `override_policy` | object \| null | *optional*; makes the condition **waivable** by a human (see below). Absent → not waivable. |
| `waived` | object \| null | set by the `waive` verb when a human accepts the condition; a durable marker that survives re-evaluation |
| `attested` | object \| null | set by `attest --evidence` when an `artifact` postcondition is satisfied by reference to an already-attached artifact; a durable marker (like `waived`) that survives re-evaluation; cleared by `reopen` |

### What "engine-checked" means

| `check.kind` | the engine does | satisfied when |
|---|---|---|
| `command` | runs `check.command` | exit 0 — "the tests/build actually pass" |
| `artifact` | confirms an evidence item of `check.evidence_type` is attached (optional field match, e.g. `verdict: APPROVE`) | present + shape-valid |
| `git-change-policy` | collects the staged (`git diff --cached`) or branch (`git diff <base>...HEAD`) diff and evaluates each changed file against an inline artifact policy (globs, size, binary) | **no** files violate the policy — "the closeout diff carries no suspicious artifacts" |

That is the entire mechanical surface. A human checkpoint is `artifact`/`user-decision`; a crew review gate is `artifact`/`review-result` matching `verdict: APPROVE` (produced by a `survey` review's consolidation). An `artifact` postcondition may also be satisfied by `attest --evidence <id>` referencing an already-attached artifact of the matching type, instead of re-attaching it to a second task — the engine still verifies the referenced artifact exists and matches the required `evidence_type` + `match`, so this never asserts an artifact from thin air.

### `git-change-policy` — artifact-output guardrails at closeout

A `git-change-policy` check refuses advancement when the staged or pending diff includes **suspicious artifacts**: oversized files, generated record dumps, disallowed artifact directories, binary/blob additions, or large data files (parquet/pickle/model/checkpoint). It is mechanical only — globs, size, binary — and does **not** judge whether an artifact is semantically useful. The policy is configured **inline on the `check`**:

```json
{
  "kind": "git-change-policy",
  "mode": "staged",                       // "staged" (git diff --cached) | "branch" (vs base)
  "base": "origin/main",                  // used only when mode == "branch"
  "max_file_bytes": 1000000,
  "deny_globs": ["*.parquet","*.pkl","*.pickle","*.joblib","*.pt","*.onnx","data/generated/**","records/**"],
  "allow_globs": ["docs/**","src/**","tests/**","skills/**","scripts/**",".agent-work/**"],
  "require_human_waiver_for_binary": true
}
```

| field | type | meaning |
|---|---|---|
| `mode` | `staged`\|`branch` | which diff to evaluate; `staged` = `git diff --cached`, `branch` = `git diff <base>...HEAD` |
| `base` | string | branch base ref, used only when `mode == "branch"` (default `origin/main`) |
| `max_file_bytes` | int \| null | a changed file larger than this violates; `null`/absent = no size constraint |
| `deny_globs` | `[glob]` | a changed path matching any of these **always** violates (an explicit deny beats an allow) |
| `allow_globs` | `[glob]` | a changed path matching any of these is **exempt from the size and binary checks** (deny still denies) |
| `require_human_waiver_for_binary` | bool | when true, a binary/blob addition (outside an `allow_glob`) violates |

**Per-file violation semantics.** A changed file VIOLATES if it matches any `deny_glob`; OR its size exceeds `max_file_bytes`; OR it is binary and `require_human_waiver_for_binary` is true — **UNLESS** it matches an `allow_glob`, which exempts it from the size/binary checks only. An explicit `deny_glob` always wins (a deny inside an allowed directory still denies). Globs use `**` for any number of path segments and `*` within a segment; a bare-basename glob like `*.parquet` matches anywhere in the tree. Empty/missing policy lists mean "no constraint of that kind," and a clean (or empty) diff yields zero violations → satisfied.

**Implementation note (testability).** The engine splits this into a PURE evaluator `evaluate_git_change_policy(files, policy) -> [violations]` (no git, no filesystem; `files` are `{path,size,binary}` dicts) and a thin git collector `_collect_changed_files(policy, base_dir)`. The semantics above are fully unit-testable without a working tree.

**Blocks by default; waivable via the override path.** The check **blocks advance by default**. A human who intends an artifact does not hand-mark the condition — they carry an `override_policy` on it and `waive` it (see *Override policy*). The check's `artifact-policy` evidence (below) records exactly which rule was bypassed, so the waiver's audit trail names the violation.

**Rigor dial.** `max_file_bytes`, `deny_globs`, `allow_globs`, and `require_human_waiver_for_binary` are the **rigor dial** for closeout. They are tuned per project by editing the inline policy on the check in the project's templates (Charter owns the templates / engine-config). There is no separate config loader — the inline policy on the check is the single source.

### Override policy — a deliberate, auditable waiver

By default the engine **refuses** advancement when any postcondition is unmet, and a failed `command` check leaves a `command-output` evidence record with its exit status and a `shell` field naming the shell that ran it (`posix`, or `no-posix-shell` on a bash-less Windows box). `command` checks run under a POSIX shell so authored `grep`/`&&`/pipe checks are portable; on a bash-less Windows box the engine **refuses** to run the POSIX-form text through cmd.exe and instead records a visible failure (returncode 127, `shell: no-posix-shell`) rather than silently passing or misinterpreting the check. That refusal is the whole point: it kills accidental advancement past a failing gate. But a human sometimes legitimately decides a check is non-blocking (e.g. a flaky type-check at a docs-only closeout). That decision belongs to the human, not the engine — so the engine offers a **waiver** path that records *who* accepted the risk and *why*, rather than letting an agent quietly mark a condition satisfied.

A condition opts into being waivable with an optional sibling field `override_policy` (a **sibling of** `check`, not nested inside it):

```json
"override_policy": { "allowed": true, "authority": "human", "reason_required": true }
```

| `override_policy` field | type | meaning |
|---|---|---|
| `allowed` | bool | the condition may be waived (no `--force` needed) |
| `authority` | string | who is expected to accept the risk (advisory) |
| `reason_required` | bool | the `waive` verb refuses an empty `--reason` |

**Absent `override_policy` means the condition is NOT waivable.** All existing conditions behave exactly as before; only a condition that carries this field is waivable through the normal path. A condition without a policy can still be waived, but only via the high-friction `--force` flag, which always demands authority + reason and is recorded as a forced override.

When `waive` succeeds it does three durable things on the condition: sets `satisfied: true`, sets `satisfied_by` to the new waiver evidence id, and stamps a `waived` marker `{authority, reason, evidence, forced}`. The marker matters because `command`/`artifact` checks are **re-evaluated at every `advance`**: the engine short-circuits a waived condition (honors it without re-running its check) so the waiver is not silently overwritten and un-waived. A `reopen` clears the `waived` marker — rework re-evaluates from scratch, so a prior waiver does not carry over.

### Qualitative conditions (`check: null`) — trust but verify

Most conditions, especially **preconditions**, are qualitative. The engine records the agent's assertion and leans on the tiers for truth. A precondition is verified by **the very agent that depends on it**: told "you need an interface that does X," its first job is to confirm that interface exists — which doubles as a second review of the upstream work. We chose this over mechanical id-chaining: trust but verify, and keep the engine simple.

## Evidence

| field | type | notes |
|---|---|---|
| `id` | string | |
| `type` | enum | `command-output \| review-result \| file-diff \| user-decision \| cartographer-verification \| waiver \| artifact-policy \| refresh-request` |
| `payload` | object | command output, diff ref, decision text, verdict, packet ref; for `command-output`: `{cmd, exit, shell}` where `shell` is `posix` or `no-posix-shell` (a bash-less Windows box, where the engine refuses to run POSIX-form text through cmd.exe and records a visible failure — returncode 127 — instead); for `waiver`: `{cond, authority, reason, forced}`; for `artifact-policy`: `{mode, violations, files_checked}` (the violations a `git-change-policy` check found, so a later waiver records which rule was bypassed); for `refresh-request`: **POINTERS ONLY** `{seam: <gate/item id it concerns>, why_ref: <why-record id it was raised against>}` — never copies of state (see *Refresh requests*) |
| `produced_by` | string | role/tier |
| `ts` | string | |
| `superseded` | object \| null | *optional, additive*; set by the `reopen` cascade to `{by, reason, ts}` (`by` is `reopen:<gate-id>`). The evidence is **retained** (the audit trail is never deleted) but rendered **inert for satisfaction**: the `_check_condition` artifact branch skips a superseded item, and `attest --evidence` refuses to satisfy a condition from one. So a reopened gate cannot re-pass an artifact postcondition from the stale approval the reopen just invalidated — fresh evidence is required. |

## Envelope (a projection, not stored)

The envelope is the task projected across a tier boundary, translated to the receiving agent's language. Derived from the task, not a separate record.

- **down (dispatch):** `imperative`, `preconditions` (givens), `postconditions` (success target), inherited `constraints`, `directives`, evidence types implied by postcondition checks, stop conditions. For a `survey` handoff, also the starting item list and "extend from context."
- **up (return):** the consolidated result (or per-gate evidence), per-postcondition satisfaction, deviations (skips / OBE), and any `triage_candidates` / `blockers` to bubble.

## Config (Charter-owned)

| field | type | notes |
|---|---|---|
| `rework_cap` | int | reopen attempts per node before escalation to the parent / human |
| `replan` | `abort-and-reissue` | Commander is one-shot; a failed plan ends the run and re-issues |
| `human_checkpoints` | `[string]` | the **rigor dial**: which checkpoints require a `user-decision` (e.g. `understand.done`, `plan.approved`, `run.accept`) |
| `lease_stale_seconds` | int | a lease whose `last_heartbeat` is older than this is **stale** and may be reclaimed (default 1800) |

## Status

```
pending ──(preconditions satisfied, if any)──▶ in-progress
in-progress ──(postconditions satisfied + evidence shapes present)──▶ complete   [gated]
in-progress ──(check performed; result recorded)──▶ complete                     [survey: pass OR fail]
in-progress ──(blocker)──▶ blocked
{any} ──(reason; OBE)──▶ skipped
complete ──(reopen, reason)──▶ in-progress   (rework_count++; escalate at cap)
blocked ──(resume, reason)──▶ pending | in-progress   (restores pre-block status)
```

`survey` items reach `complete` once the check is **performed** — a `fail` result is still complete (recorded, not blocking). Required `status_detail`: `skipped` → reason; `blocked` → blocker + authority needed + next action (also appended to `blockers`); `complete` (gated) → evidence ref or note.

**`accept` folds into `advance`.** Within one plan the agent just advances its gate; the "return is a proposal the invoker may reject" duality lives at the *handoff between two plans*, not inside one.

## Consolidation (survey output)

A survey's output is **as structured as its consumer requires, and no more.**

- Consumed by a **machine** (a parent gate's `artifact` check) → the consolidation carries the matched field. A reviewer survey carries `verdict` (plus a prose `findings` list); the parent reads `consolidation.verdict`. The consolidation **is** the `review-result` artifact — no separate plumbing.
- Consumed by a **human** (e.g. a plan-approval checkpoint) → the consolidation can be pure prose. The Interrogator's "resolved understanding" needs no machine field.

Beyond that one field, consolidation is the agent's prose summary, handed up.

**Consistency guard (engine-enforced):** `consolidate` refuses a `verdict: APPROVE` while any item still has `result: fail`, unless an explicit `override_reason` is supplied. This is pure shape-checking — the engine is not judging quality, only refusing a verdict that contradicts its own recorded findings. It kills the weak-reviewer failure mode: dutifully recording "v3: fail," then rubber-stamping APPROVE.

## Amend delta — intentional mid-run re-planning

A `gated` plan is frozen once authored — the agent works the gates it was handed, it does not hand-edit the JSON. The one sanctioned way to change a gated plan mid-run is the `amend` verb, the planning-time counterpart to `waive`: like a waiver it demands a non-empty `--reason` and `--authority` (human ratification), and like a waiver the engine does not judge whether the re-plan is wise — it enforces *mechanism* and records who authorized it. `amend` applies to **gated** checklists; on a **survey**, `retext-check` is additionally available and is the **only** permitted op — `add`/`drop`/`rescope` stay gated-only, a conservative choice rather than a type-level impossibility, and the refusal says so.

```
amend --delta <file.json> --reason "..." --authority human [--session-id <id>]
```

The delta file is JSON `{"ops": [...]}` with a non-empty `ops` list. Every op touches **PENDING gates only**, with one exception: `retext-check` also edits an **IN-PROGRESS** gate's check text (never a `complete`/`blocked`/`skipped` one). Four op kinds:

| op | shape | effect |
|---|---|---|
| `add` | `{"op":"add","id":"…","title":"…","imperative":"…","postconditions":[…],"after":"<gate-id>"?, …}` | insert a **new pending gate**. `id` must match `^[a-z0-9][a-z0-9-]*$` and be unique; `title` and `imperative` non-empty; **≥1 postcondition**. `after` names an existing gate to insert **behind** (omit to append at the end). `preconditions`/`constraints` default to empty, `directives`/`child_checklist` to null — the same shape `append` builds. |
| `drop` | `{"op":"drop","id":"<gate-id>"}` | remove a **pending** gate (dropping a non-pending gate is refused). |
| `rescope` | `{"op":"rescope","id":"<gate-id>", …fields}` | overwrite provided fields on a **pending** gate; overwritable fields are `title`, `imperative`, `postconditions`, `preconditions`, `constraints`, `directives`, `bookend`. (`bookend` is the retrofit path for a plan already running — see *Bookends*.) At least one is required; if `postconditions` is given it must stay **≥1**. |
| `retext-check` | `{"op":"retext-check","id":"<gate-id>","cond":"<cond-id>","which":"postconditions"?,"command":"…"}` or `{…,"check":{…}}` | correct the **check TEXT** of one condition on a **pending or in-progress** gate (`which` defaults to `postconditions`) — `command` corrects a `command` check, or a same-kind `check` object replaces it. **Never changes the check kind**; deep-copy all-or-nothing like the others; **resets that condition to unsatisfied** (clears `satisfied`/`satisfied_by`/`waived`/`attested`) so no stale approval survives — but **never marks it satisfied** (that stays `waive`'s job). Refused on a `check: null` condition (nothing to correct — use `attest`/`waive`). |

**Position / floor rule (`add`).** A new gate may not be inserted **before a frozen (non-pending) gate**. The engine computes a *floor* = one past the index of the last non-pending gate; an `add` whose landing index falls below the floor is refused, naming the frozen gate that blocks it. So an amendment can reorder and extend the pending tail but never re-sequence work that is already underway or done.

**Bookends — the frozen ends of a mutable plan (#634).** The floor rule above freezes what has already been
**started**, which covers a plan's *opening* by accident of status and covers its *closing* not at all: a closing
gate is `pending` for the whole run, and before #634 a Commander standing at `execute` could `drop` its own
`archive`, `review` and `feedback` in one delta and terminate having never been reviewed or archived. A gate
declaring `bookend: true` is therefore frozen **by declaration rather than by status**: `drop`, `rescope` and
`retext-check` on it are refused whatever its status, and an `add` may not land **after** the last bookend, so a
frozen finish keeps meaning finish. `retext-check` is covered deliberately — it could otherwise rewrite a frozen
gate's `command` check to something trivially true and pass it, and a freeze that only stops deletion is not a
freeze. Between the floor and the last bookend the plan stays **freely mutable**: this is what lets a role author
its own work gates into its own spine mid-run instead of into a second file. The declaration is read in exactly one
helper (`_is_bookend`), so the form it takes is one function's worth of change. The shipped role spines declare
`init` + `archive` (Commander), `init` + `closeout` (Admiral), `init` + `route` (Explorer). **Not covered:** crew
plans, whose template is compiled by `scripts/generate_spine.py` — its gate compiler emits a fixed field list, so a
`bookend` key in a spec would be dropped silently.

`current` renders which gates are frozen. #634 shipped the refusal but not its visibility: an agent planning an
amend had no sanctioned way to learn a gate was frozen except attempting the amend and being refused, since
opening `spine.json` to check `bookend` directly is itself a doctrine violation. `current`'s output now carries a
`bookend (frozen …): <id>[, <id>…]` line, listing every declared bookend gate in plan order, whenever the plan has
at least one — emitted once, ahead of the `ACTIVE …` line (or `DONE …` / `ALL ITEMS VISITED …`), in the same prefix
slot the lease line already occupies. A plan with no `bookend` key anywhere renders no such line, so an undeclared
plan's `current` output is unchanged.

**All-or-nothing.** The whole delta is validated and built on **copies**; canonical state is touched only once *every* op passes. Any invalid op refuses the entire amendment and leaves the checklist **unmutated** — important, because the engine persists state even on the error path, so a partially-applied delta could otherwise leak. On success the engine appends one audit entry to the top-level `amendments` list: `{ts, reason, authority, ops:[…]}` (the `ops` are human-readable summaries such as `"added g3"`, `"dropped g4"`, `"rescoped g2"`). `amend` is a mutating verb: once a lease exists it needs the owning `--session-id`, and a successful amend refreshes the lease.

## Why-capture — the running-understanding trail (`why_trail`)

Part of the Context Governor (epic-#178). As an agent advances gates it accumulates a **running understanding** of the work; that understanding is captured at each gate boundary so a fresh agent can cold-start from it (the reach-up / refresh flow). The capture is the optional top-level, **append-only** `why_trail`.

```json
"why_trail": [
  { "id": "w-1", "gate": "g1", "why": "chose staged-diff mode so closeout catches only what's committed", "mechanical": false, "ts": "<iso8601>" },
  { "id": "w-2", "gate": "g2", "why": null, "mechanical": true, "ts": "<iso8601>" }
]
```

- **Appended per non-exempt `advance`.** One record is appended each time a **non-exempt** gate advances (`_append_why`). Ids are sequential `w-1`, `w-2`, … (`w-<n>` for the n-th record). A record carries `{id, gate, why, mechanical, ts}`: `why` is the running-understanding text (or `null` for a mechanical step), `mechanical` a bool.
- **Append-only.** Earlier records are **never mutated or deleted**; the trail is created lazily on first write (`setdefault`), so a spine with no `why_trail` drives unchanged and gets one on its first non-exempt advance.
- **DIGEST = the live understanding.** The **digest** is the `why` of the latest **non-mechanical, non-superseded** record (`_latest_why_record` / `_digest`). A `--mechanical` marker (`why: null`, `mechanical: true`) carries no understanding and **never** becomes the digest.
- **`reopen` freshens the digest by appending, not editing.** The `reopen` cascade appends a **reopen-marker** record for each gate it resets. A prior `why` for a gate is treated as **superseded** once a later reopen-marker names that gate, so `_latest_why_record` skips past it — the reopened tail's digest freshens **without editing any prior row** (the append-only invariant holds).

### The `--why` / `--mechanical` advance interface (fail-closed)

A **non-exempt** gate's `advance` (a gate without `why_exempt: true` — see the Task table) is **REFUSED** unless it carries either a running `--why "<understanding>"` **or** an explicit `--mechanical` marker. **Silence fails closed** — an advance with neither is refused, never silently skipped. `--mechanical` is a distinct flag (not a magic `--why` string) that records a marker which never becomes the digest.

- **Postconditions are proven BEFORE the why is solicited.** `advance` checks all postconditions first; a **failing postcondition yields the postcondition refusal, not the why prompt** — there is no buying past unfinished work with a why string.
- **Reference, don't duplicate.** The `--why` text is meant to reference the task state (the running understanding), not re-copy the postcondition evidence.
- **Backward compatible.** An existing-shape spine (no `why_trail`, no `why_exempt`) still drives: a missing `why_exempt` ⇒ not exempt (so the gate asks for a why), and `why_trail` is created on the first write.

### The `DIGEST:` / `REFRESH REQUESTED:` lines on `current`

The read-only `current` verb appends up to two why-capture lines to its output (`_why_suffix`) — a new verb was **not** added; these ride `current`:

- **`DIGEST:`** — the latest running understanding (the live digest, above). Appended whenever a live digest exists.
- **`REFRESH REQUESTED:`** — appended while a refresh-request is **pending for the active gate/item**, naming the gate and the why-record it was raised against (`REFRESH REQUESTED: <gate> (why_ref <w-id>)`).

**These render for BOTH `gated` AND `survey` checklists (#189).** This was gated-only before #189; it is now current behavior for both. A **survey never accumulates a `why_trail`** (`_append_why` only fires on `advance`, which surveys refuse), so `_digest` is `None` and **no `DIGEST:` line appears for a survey** — only the `REFRESH REQUESTED:` line does. That line is the **reach-up cold-start surface for survey roles** (e.g. the reviewer), which is why the parity matters.

### Refresh requests — `has_pending_refresh_request` (why_ref-aware, #190)

A **`refresh-request`** is a `refresh-request`-typed evidence item attached through the ordinary `attach` verb, e.g. `attach <gate> --type refresh-request --field seam=<gate> --field why_ref=<why-id>`. Its payload contains pointers only: `seam`, `why_ref`, and, when an active lease exists, the engine-stamped `lease_claimed_at`. Callers do not supply the claim stamp. A `superseded` marker (set by the `reopen` cascade) makes a refresh-request **inert**, exactly as it does for any other evidence.

```
has_pending_refresh_request(cl, gate, why_ref=None) -> bool
```

A **pure predicate** (no side effects): **true** while a non-superseded `refresh-request` targets `gate` and any claim stamp still matches the active lease. Its filters are:

- **`lease_claimed_at` present** — the request is pending only while the active lease has the same `claimed_at`. Any later claim, including a same-session re-claim, consumes it. A legacy unstamped request keeps the earlier gate-and-supersession behavior.
- **`why_ref=None` (default)** — the **DISPLAY semantic** used by `current`: *any* pending request for this gate matches. Unchanged from the pre-#190 gate-only behavior.
- **`why_ref` given** — an **identity check**: the pending request must **also** carry the matching `payload.why_ref`. The **HARD band keys its release on the current-digest why-record id** (`_latest_why_record`), so a **distinct new trip on a still-open gate cannot ride an earlier/stale request's coattails**. A `None` current-why-id (no `why_trail` — e.g. a `why_exempt` gate) **degrades to the gate-only match**, preserving all prior behavior.

### Trip — two-band context-gauge gate policy (SOFT advisory / HARD guards the BEGIN verbs)

Part of the Context Governor (epic-#178, Module 3). At each **gate boundary** the engine reads the context-fullness **gauge** — a **sibling of the spine** (`Path(spine).parent`, the `base_dir`) — and applies **model-keyed thresholds**. Two bands, both **fail-safe on a missing/stale reading** (a stale/absent/corrupt reading collapses to `None` inside the reader, yielding no advice and never forcing):

**Which file (#600).** A reading belongs to an **agent**, not to a folder. When this checklist holds an **active lease**, the engine reads `gauge-<owner>.json`, where `<owner>` is `gauge_reader.owner_key(lease.session_id)` — the same name the writer hook independently composes from the binding entry's `engine_session`, which is the very string that `claim --session-id` carried. When there is **no lease** (or a released one, or nothing to key on), there is no owner and the engine reads the unowned `gauge.json` and trips on it **exactly as before**. Where a lease *does* name an owner and no file of that name exists, the answer is **no reading** — there is deliberately **no fallback** to the shared file, which would reinstate the folder-owned file this change exists to remove and hand this session a number another agent sampled. A record whose `owner` field disagrees with the filename it sits in is a **defect**, so the reading is declined and the disagreement is reported by name rather than absorbed into silence.

Before this, two agents whose spines shared one work directory wrote to one path and the last one won — measured live, an orchestrator's `0.9` overwriting a dispatched agent's `0.02` with nothing noticing. **Identity handles that concurrent case; the `claimed_at` comparison below handles the sequential relaunch case. Both are permanent** — a relaunched agent reuses its predecessor's lease name by design, so no identity scheme can separate those two legs.

- **SOFT (`fill >= soft`)** — an **advisory** stop-by-default suffix on the read-only `current` (`_trip_advisory`): "you've used most of your context; unless you're basically done, hand off here at this seam." SOFT **never forces** — the agent may decline (any reason accepted in v1) simply by advancing, which SOFT never blocks.
- **HARD (`fill >= hard`)** — the engine **REFUSES the verbs that BEGIN work at a gate**: `start` (opens a `pending` gate) and `reopen` (drives a `complete` gate back to `in-progress` and cascades downstream) — the set `TRIP_HARD_GUARDED_VERBS`, enforced by `_trip_hard_gate`. The refusal stands until a `refresh-request` exists for that gate, **keyed to the current understanding** (per #190 — the pending request's `why_ref` must match the current-digest why-record id). It names the exact `attach` command, carrying the **concrete live why-record id** rather than a `<why-id>` placeholder.

**HARD does not refuse `advance`** (#467). Closing the gate you are already inside **is** the handoff: an agent running out of context must be able to finish and hand off the gate it is in. What HARD refuses is **beginning** work it cannot finish. `resume` is likewise **not** guarded — it only restores a `blocked` gate to the status it already held, which for an `in-progress` prior returns the agent to the gate it is mid-way through.

**At/over hard, though, a gate may not be closed in SILENCE.** `advance --mechanical` is **refused** and `why_exempt` is **suspended**, so the closing `advance` must carry a real `--why` and that understanding is actually appended to the `why_trail`. Without this the tripped agent closes with a mechanical marker, `_latest_why_record` skips it, the `DIGEST:` line stays pre-trip, and the fresh agent cold-starts from an understanding written **before** the work it is inheriting (issue #431). This is a refusal of silence, not of the advance, and its message names the compliant form: `advance <id> --why "<understanding>"`.

**HARD means "wrap up", never "you are unsafe".** The HARD advisory is worded as a **changed instruction** — close this gate carrying your handoff, request a refresh, and stop — and deliberately carries no alarm language; an agent that reads an alarm looks for a way past it instead of doing the one thing it is being asked to do.

Both bands are **gated-only** (empty for surveys) and ride the **CLI boundary** in `dispatch` — SOFT is a suffix on `current`'s output; HARD is a pre-verb guard on `start`/`reopen` plus a `require_why` flag `dispatch` passes into `advance` — so the verb functions stay **pure** (their return values are unchanged, so existing exact-equality tests keep passing, and a direct non-`dispatch` call to `advance` is unaffected because `require_why` defaults to `False`). A refusal is raised **before** the liveness stamp, so it never refreshes the lease and never changes the gate's status. Since #467 it does make **exactly one** state change: it appends the `trip_ledger` entry recording the attempt (next section). The mid-gate runaway is a deliberately accepted limit: there is **no mid-gate check**. (A rollout-ordering caveat about enabling the HARD band lives as a code comment, not in this schema.)

### The trip ledger — the engine's own record of BEGINs over the hard line (`trip_ledger`)

The Trip bands above tell an agent to wrap up. Nothing until #467 recorded whether it **did**. The
question that matters is not "did a handoff artifact appear before the next advance" — `advance`
already refuses a non-exempt gate that carries no `--why`, so that is true in the healthy world and
in the defective one alike, and it therefore discriminates nothing. The question that separates the
two worlds is: **did anyone BEGIN work while over the line?**

The `trip_ledger` is the optional top-level, **append-only** list that answers it. One entry is
appended every time the HARD band is evaluated at a **mutating** chokepoint and found tripped —
that is, inside `_trip_hard_gate`, which guards `start` and `reopen`.

```json
"trip_ledger": [
  {"id": "tl-1", "gate": "g2", "verb": "start", "outcome": "begin-refused",
   "fill": 0.95, "hard": 0.9, "model": "claude-opus-4-8",
   "why_ref": "w-1", "ts": "2026-08-08T12:00:00+00:00"}
]
```

| field | meaning |
|---|---|
| `id` | positional, `tl-<n>`, assigned at append |
| `gate` | the gate whose BEGIN was judged |
| `verb` | the begin verb that was run (`start` or `reopen`) |
| `outcome` | `begin-refused`, `begin-released`, or `begin-instructed` — see below |
| `fill` | the gauge's fill fraction at the moment of the trip |
| `hard` | the hard line the agent was judged against, **after** that gate's own `context_headroom_tokens` reserve — so the recorded pair is the same pair the agent was shown |
| `model` | the model the reading was taken on |
| `why_ref` | the live why-record id at the moment of the trip; this is what keys the entry to an understanding |
| `ts` | engine timestamp |

Three outcomes, because all three are **begin** outcomes:

- **`begin-refused`** — no keyed `refresh-request` was pending, so the verb **raised**. The entry
  still survives: `main()` persists state on the `EngineError` path for any verb that is not
  `current` and not `--dry-run`.
- **`begin-released`** — a keyed `refresh-request` **was** pending, so the guard released and the
  verb **proceeded while still over the line**. This is the worst of the three: work actually began.
- **`begin-instructed`** — a keyed request was pending *and* the begin is the one the HARD advisory
  itself instructs (#510). Recorded like any other entry, but **not counted** as an over-the-line
  begin.

**Why `begin-instructed` exists, and why it is not a loophole.** `advance` is refused on a pending
gate, so an over-the-line agent standing at one cannot leave its handoff without first entering the
gate. The HARD advisory therefore names an exact sequence — request the refresh, `start` this gate,
then `advance --why`. That `start` **is** the handoff mechanism; it begins no work it cannot finish.
Recording it as an over-the-line begin made the compliance signal report an offence for obeying the
engine, so obedience and evasion produced the same ledger.

Nothing is hidden by the split. The entry is appended exactly as before, same fields, same
append-only guarantee, so an auditor still sees that a begin happened over the line and why it was
allowed. What changes is only which outcomes the compliance selectors count — see
`begin_over_line_records`, which counts `begin-refused` and `begin-released` and ignores anything
outside that pair.

The exemption is as narrow as the instruction that earns it, and is keyed to the state the advisory
is rendered from rather than to a verb name. **All three** of these must hold: the verb is `start`,
the gate is the **active** one, and its status is `pending`. `reopen` (which cascades downstream and
is never instructed), a `start` with no keyed request pending (the advisory says request *first*),
and a `start` aimed at any other gate all remain exactly as they were.

**Scoped honesty about `begin-released`.** The entry records the decision **at the guard**, which is
where the band is evaluated — before the verb runs. If the verb then raises for an unrelated reason
(unmet preconditions, say), the ledger still shows `begin-released`. It is a faithful record of what
the governor did, not a claim about what the verb returned.

**Two places evaluate the same band and deliberately do NOT write here.** `_trip_advisory` is
reached from `current`, and `main()` does not save on `current`, so a write there would be silently
discarded — and would be a lie in a read-only verb. The close side (`advance`'s `require_why`) is a
**close**, not a begin; neither outcome value fits it, and closing the gate you are inside is not the
offence.

#### The compliance signal — `begin_over_line_records(cl)`

A **pure** selector over stored state: every ledger entry whose `why_ref` is the id of the **live**
why-record. Its **emptiness is the predicate**. It reads `trip_ledger` and `_latest_why_record` and
nothing else — no subprocess, no gauge read, no clock — so it is safe on the read-only `current`
path.

Keying it to the live understanding is what stops a historical mark from reading as present-tense
non-compliance. When the understanding moves on, the entry is **retained and never edited**, it
simply stops matching. Two things move the understanding on, and the mechanism **cannot tell them
apart**: a `reopen` appending a reopen-marker, **or the same offending agent closing the very gate
its own HARD advisory just told it to close** — the only legal close at/over hard is
`advance --why`, and that write is what supersedes the old why-record. The second case is not a
corner case; it is the **likeliest** superseder in exactly the runaway this ledger exists to catch,
because the HARD band's own instruction is "close THIS gate" (see *#467 B1* below and the fourth
limit in the next section).

It is surfaced by **extending the existing HARD branch** of `_trip_advisory`, in both of that
branch's sub-branches, as up to two added lines — this one and the historical one below. There is
exactly one computation of each fact in the engine; nothing else renders either.

**In the healthy world there is no ledger at all.** The agent that was told to wrap up closed its
gate and stopped, so no begin verb ever ran, so nothing was ever appended. That is the whole value of
the signal: it differs between the two worlds.

**Fail-safe: an empty result is not a claim of compliance.** A missing, stale, or clock-skewed gauge
collapses to no reading, and then `_trip_hard_gate` returns before writing anything **and** the
advisory says nothing about either ledger read. Silence reads as *neither compliant nor
non-compliant*. A signal that read silence as "clean" would be the same defect class as a check that
cannot fail.

**Backward compatible.** The list is created lazily on first write (`setdefault`, the `why_trail`
idiom), so a spine with no `trip_ledger` drives unchanged and never acquires the key for nothing. An
existing ledger is extended, never replaced.

**Engine-written only.** No CLI verb creates, edits, or deletes an entry. The only writer is
`_append_trip_entry`; its only caller is `_trip_hard_gate`; and `_trip_hard_gate`'s only caller is
`dispatch`, which runs it **before** `_run_verb` — the function every verb is dispatched through.
Entries are append-only: no code path mutates or removes one. `begin_over_line_records_historical`
below reads the same append-only list; it is a second reader, never a second writer.

#### The historical read — `begin_over_line_records_historical(cl)` (#467 B1 rework)

A second **pure** selector, additive to the live one above and **not a replacement for it**: every
`begin-refused`/`begin-released` `trip_ledger` entry, filtered the same way, but with **no `why_ref`
keying at all**. Where the live selector answers "is there an over-the-line begin under the
understanding now in force" — and is therefore emptied by the mandated close, as above — this
answers "has this checklist ever recorded one", and nothing that changes which understanding is live
can affect the answer.

**Why it exists.** The HARD band's own instruction is "close THIS gate carrying your handoff", and
closing a gate is exactly the act that supersedes the live why-record. The live selector's keying
(close criterion (b), correctly implemented and **not changed by this addition**) therefore
guarantees that the one close an over-the-line agent is required to make is also the one thing that
empties the only rendered signal — byte-identical, at the seam, to an agent that never went over the
line at all. The historical selector is unkeyed *because* nothing keyed to the live understanding can
survive the mandated close.

Rendered as its own line — `TRIP HISTORY`, deliberately not sharing the `TRIP LEDGER` label with the
live line — in the same one render site as the live line, naming the total and the latest entry, and
stating plainly that no close clears it. **It renders whenever anything is on record at all, even
when the live list is empty** — that seam (live 0, historical N) is precisely the case it exists for.

Pure, fail-safe, and engine-written-only in exactly the same senses as the live selector (see above):
no subprocess/gauge/clock; a malformed `trip_ledger` (`None`, a string, a dict, or a list holding
non-dict entries) degrades to an empty result rather than raising; and it is a reader only, called
from `_trip_advisory` alongside the live selector.

#### The limit — what this cannot observe

The engine **cannot** observe an agent that is told to wrap up and simply **stops without running another verb**.
`main()` does not save on `current`, which is where the band is evaluated read-only, and there is no
mid-gate check. That case is visible to the invoker only as a stale `DIGEST` at the seam.

Two consequences worth stating plainly rather than leaving fuzzy:

- The ledger records **begins**, not **work**. An agent that keeps working inside the gate it is
  already in, over the line, without running any verb, leaves no mark.
- An empty ledger therefore means "no recorded begin over the line under this understanding" — never
  "this run was compliant".

**The fourth: the live signal goes silent at exactly the close it mandates.** The HARD band's own
instruction is "close THIS gate carrying your handoff", and closing a gate is what writes the new
`why_trail` record that becomes live. The live selector is keyed to that live record by design (close
criterion (b)), so the mandated close is **guaranteed** to empty it — on the live line alone, a
compliant agent that never went over the line and an offender who did and then closed the very gate
its own advisory told it to close render **identically absent**. That is why the historical read
exists (`begin_over_line_records_historical`, above): it carries no keying for the close to supersede,
so it is where the two worlds actually differ. A reader who checks only the live line at the seam
learns nothing; the historical line is what has to be read.

## Engine verbs ↔ schema

| verb | applies | reads/writes |
|---|---|---|
| `current` | both | walk to the active item; emit its `imperative`; reports active-lease metadata when present (no session needed) |
| `claim --session-id <id> --claimed-by <role> [--worktree .] [--force --reason …]` | both | take the actor-authority lease; idempotent same-session resume; refuses a different active lease unless forced |
| `heartbeat --session-id <id>` | both | refresh the active lease's `last_heartbeat` (owner only) |
| `release --session-id <id> [--force --reason …]` | both | close the lease (`status: released`); owner only unless forced |
| `criteria <id>` | gated | emit `postconditions` + implied evidence types |
| `start <id>` | both | engine checks any `command`/`artifact` preconditions; agent asserts qualitative ones; `→ in-progress`. **Refused at/over the Trip HARD threshold** without a matching `refresh-request` — `start` BEGINS work (see *Trip*). Either way, at/over hard the engine appends one `trip_ledger` entry recording the attempt (see *Trip ledger*) |
| `advance <id> [--why "…" \| --mechanical] --evidence …` | gated | check all `postconditions`; then, for a **non-exempt** gate, require a running `--why` **or** an explicit `--mechanical` marker (silence **fails closed**) and append a `why_trail` record; `→ complete` (see *Why-capture*). **Never refused by Trip HARD** — closing the gate you are in is the handoff — but at/over hard `--mechanical` is refused and `why_exempt` is suspended, so the close must carry a real `--why` (see *Trip*) |
| `record <id> --result pass\|fail [--finding …]` | survey | record the check outcome; `→ complete`; `--result fail` never blocks. `--result pass` REFUSES if the item carries an unmet `command`-kind postcondition (checked via the same `_check_condition` `advance` uses) — `null`/`artifact`-kind postconditions on a survey item are not evaluated here (#422/#328) |
| `append <id> …` | survey | add an item from context |
| `consolidate` | survey | every item visited → produce `consolidation` (verdict / understanding) |
| `skip <id> --reason …` | both | `→ skipped` (OBE; state op) |
| `block <id> …` | both | `→ blocked`; append to `blockers` (bubble to parent) |
| `resume <id> --reason … [--note]` | both | move a **resolved `block`** forward: restore the gate to the `pending`/`in-progress` status it held **before** it was blocked (recorded by `block` as `status_detail.prior_status`). Refuses a gate that is not `blocked`, an empty `--reason`, and a block with **no restorable prior** (a reopen rework-cap escalation, or a legacy block predating `resume`) — those need `reopen`/`skip`/a human decision, not `resume`. On success pops `prior_status`, records `resume_reason`/`resume_note` in `status_detail`, and drops the gate from the top-level `blockers` list. |
| `reopen <id> --reason …` | gated | **Refused at/over the Trip HARD threshold** without a matching `refresh-request` — `reopen` BEGINS work (see *Trip*). Either way, at/over hard the engine appends one `trip_ledger` entry recording the attempt (see *Trip ledger*). `complete → in-progress`; `rework_count++`; escalate at cap; resets the gate's postconditions (clears any `waived`/`attested` markers) and **cascades**: every downstream `complete`/`in-progress` gate resets to `pending` (pre- and postconditions cleared, `status_detail.superseded_by_reopen` stamped); `skipped`/`blocked` downstream gates are left untouched. Evidence on the target and each cascaded gate is marked `superseded` — **retained**, but inert for satisfaction, so the reopened work needs fresh evidence |
| `amend --delta <file> --reason … --authority …` | gated (survey: `retext-check` only) | intentional mid-run re-plan: apply a validated delta of `add`/`drop`/`rescope`/`retext-check` ops; all but `retext-check` touch **PENDING gates only**, `retext-check` also corrects a **pending-or-in-progress** gate's check text; on a **survey** only a `retext-check`-only delta is accepted (`add`/`drop`/`rescope` refused as a conservative choice); **all-or-nothing** (an invalid op leaves the checklist unmutated); appends an audit entry to `amendments`. Needs `--reason` + `--authority` (human ratification), like `waive` (see *Amend delta*) |
| `attest <id> --cond <id> [--which preconditions\|postconditions] [--evidence <eid>]` | both | satisfy a `check: null` condition by manual attestation; OR satisfy an `artifact` postcondition **by reference** to an already-attached artifact `<eid>` (verified: exists + `evidence_type` + `match`) — avoids re-attaching the same artifact to a sibling gate. `--which` selects the condition list (default `preconditions`); the other list is searched as a fallback when the id is not found in the selected one. **Invariant: a task's precondition and postcondition ids must be disjoint** (convention `p*`/`c*`; every shipped template complies). The fallback resolves by first match, so a cond id duplicated across both lists would be silently resolved from the `--which` list — keep the lists disjoint rather than relying on `--which` to disambiguate. Refuses `command`/`git-change-policy` checks. |
| `waive <id> --cond <id> [--which postconditions] --authority … --reason … [--force]` | both | human override: satisfy a condition **by waiver**; refused unless its `override_policy.allowed` (or `--force`); records a `waiver` evidence record + a durable `waived` marker |
| `flag-candidate …` | both | record an out-of-scope discovery in `triage_candidates` |

Every **mutating** verb above (`start`/`advance`/`record`/`consolidate`/`skip`/`block`/`resume`/`reopen`/`append`/`amend`/`attest`/`waive`/`attach`/`flag-candidate`) accepts an optional `--session-id`; it is required, and checked against the active lease, **only once a lease has been claimed** (see *Engine session*).

**A gate is closed by the evidence on it, never by a path named on the call.** `advance <id> --from-child <path>` used to read a child checklist's `consolidation` and attach it as the gate's `review-result` before advancing. It was **cut at #634** and must not be restored.

It was cut as dead weight, measured over the whole corpus: every gate declaring a `child_checklist` carried **no** `review-result`, and all 253 `review-result` items on disk sat on gates declaring **no** child, with `attach`-shaped payloads. The two halves of that seam never met in a real run — 25 consolidated surveys, 0 consolidations ever ingested. It also carried real reach: because `review-result` is what an `artifact` postcondition consumes, any JSON file with a `consolidation` key could close a gate, and one outside the binding was measured advancing a gate to `complete` on a fabricated APPROVE.

A parent that needs a child's verdict attaches it explicitly — `attach` the verdict, or `attest` citing the child's per-gate evidence — which is what every real run already did. `child_checklist` itself **stays**: it declares custody, and `spine_lifecycle._release_child_plans` reads it at closeout to release the child's lease.

## Example: two linked checklists

Mid-run. A `gated` Commander execute.json; gate `g1` delegated its review to a `survey`, which found a problem and sent `g1` back. See `examples/` for the full JSON.

```
issue-204-execute        (gated)   g1 ⟶ child_checklist: issue-204-g1-review
                                    g1 in rework (review BLOCKed); g2 pending
issue-204-g1-review      (survey)  v1 pass, v2 pass, v3 (appended) FAIL
                                    consolidation: BLOCK ["v3: dynamic alloc in hot path"]
```

`g1`'s postcondition "reviewer approves" is an `artifact`/`review-result` matching `verdict: APPROVE`. The survey's `consolidation` *is* that artifact — here it's `BLOCK`, so the postcondition is unsatisfied and `g1` is reopened. The survey shows its nature: `v3` was **appended** from the inherited "no allocation in hot path" constraint, it **failed without blocking** `v1`/`v2`, and all three consolidated into one verdict.

## Pinch points (open)

1. **Consolidation shape.** `survey` output is a verdict + findings (reviewer) or a resolved understanding (interrogator). Those differ enough that `consolidation` may need a small per-purpose shape.
2. **Condition expressiveness.** Free-text `statement` + optional `command`/`artifact` check; no structured task-to-task dependency (qualitative trust-but-verify instead). Revisit only if cross-task deps prove error-prone.
3. **Cross-artifact write-back — CLOSED, and closed against the mechanic this entry proposed.** The entry read: a child survey's `consolidation` *is* the parent gate's `review-result`, and the engine needs a way to attach it across files, "likely an `attach`/`--from-child <work-id>` step". That step was built and then **cut at #634**, never having been used once. The answer is that the agent holding the gate attaches the verdict itself, as an explicit act, and the engine keeps working on one checklist file at a time.
4. **Evidence payload typing.** Left loose; `review-result` vs `command-output` differ a lot. May need per-type payload schemas before `artifact` checks validate reliably.
