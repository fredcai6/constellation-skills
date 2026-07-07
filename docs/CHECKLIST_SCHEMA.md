# Checklist Schema (HTN-derived)

Status: **draft / pre-build.** Companion to `CHECKLIST_ENGINE_DESIGN.md`. Expect practical implementation to move things.

## Scope: one agent, one plan

A checklist is **one plan that one agent works through** — not the whole multi-tier hierarchy in a single file. The agent is usually *handed* the plan and executes against it. Who handed it down, and how context is translated across tiers, is the **handoff / envelope** concern (see the design doc), not part of this schema. There are therefore **no owner/executor tags** — from the schema's point of view there is just the agent and its plan.

Composition is **by reference, not by nesting.** A gate that delegates work points to a **child checklist** (a separate artifact / work-id); it does not inline the sub-agent's tasks. Every agent has its own plan: Commander (spine and execute.json), implementer, reviewer. The implementer's plan is self-authored, full of primitives, and simply never handed further down.

## Two checklist types

Every checklist is an ordered list of items and declares one type:

| type | walk | append | item failure | completes when | output |
|---|---|---|---|---|---|
| `gated` | ordered; satisfy each to advance | no | **blocks** (rework / reopen) | every item complete or skipped | the work is done |
| `survey` | visit every item | **yes** (extend from context) | **recorded, never blocks** | every item visited (resulted or skipped) | a **consolidated** result |

- **`gated`** is execution: the Commander spine, Commander's execute.json, the implementer's own plan. Ordered, blocking, fixed.
- **`survey`** is inquiry / verification: the **Interrogator's questions** and the **reviewer's checks** are the same shape — hit every item, add items as context warrants, nothing gates anything, then consolidate (a resolved understanding; an APPROVE/BLOCK verdict). A survey is handed a *starting* list and told "verify these, and add more based on the context we gave you."

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
  "engine_session": null            // optional: actor-authority lease over this checklist's STATE (see below)
}
```

`triage_candidates` and `blockers` are honest, separate bubble-up channels (no vague "signals"). Both surface to the **parent agent** first; the parent escalates to the human only if it cannot resolve them. Triage drains `triage_candidates` in clean-up.

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

Once an **active** lease exists, the state-changing verbs (`start`, `advance`, `record`, `consolidate`, `skip`, `block`, `reopen`, `append`, `attest`, `waive`, `attach`, `flag-candidate`) **refuse** unless `--session-id` matches the active lease's `session_id`. The read-only `current` needs no session and reports active-lease metadata when present.

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
| `directives` | `[string]` \| null | forced primitive specifics handed down |
| `child_checklist` | work-id \| null | a **delegating** gate: the sub-plan this gate waits on |
| `status` | enum | `pending \| in-progress \| blocked \| complete \| skipped` |
| `status_detail` | object | per-status required fields (see Status) |
| `result` | `pass`\|`fail`\| null | **survey only**: the check's outcome |
| `finding` | string \| null | **survey only**: what the check found |
| `evidence` | `[Evidence]` | attached artifacts |
| `rework_count` | int | reopen count vs `config.rework_cap` |

There is no `owner`/`executor` (see Scope) and no `compound`/`primitive` flag — a gate is "delegating" iff `child_checklist` is set, otherwise it is a primitive the agent does itself.

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

By default the engine **refuses** advancement when any postcondition is unmet, and a failed `command` check leaves a `command-output` evidence record with its exit status and a `shell` field naming the shell that ran it (`posix`, or `cmd-fallback` on a bash-less Windows box). `command` checks run under a POSIX shell so authored `grep`/`&&`/pipe checks are portable. That refusal is the whole point: it kills accidental advancement past a failing gate. But a human sometimes legitimately decides a check is non-blocking (e.g. a flaky type-check at a docs-only closeout). That decision belongs to the human, not the engine — so the engine offers a **waiver** path that records *who* accepted the risk and *why*, rather than letting an agent quietly mark a condition satisfied.

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
| `type` | enum | `command-output \| review-result \| file-diff \| user-decision \| cartographer-verification \| waiver \| artifact-policy` |
| `payload` | object | command output, diff ref, decision text, verdict, packet ref; for `command-output`: `{cmd, exit, shell}` where `shell` is `posix` or `cmd-fallback` (which shell ran the check); for `waiver`: `{cond, authority, reason, forced}`; for `artifact-policy`: `{mode, violations, files_checked}` (the violations a `git-change-policy` check found, so a later waiver records which rule was bypassed) |
| `produced_by` | string | role/tier |
| `ts` | string | |

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
```

`survey` items reach `complete` once the check is **performed** — a `fail` result is still complete (recorded, not blocking). Required `status_detail`: `skipped` → reason; `blocked` → blocker + authority needed + next action (also appended to `blockers`); `complete` (gated) → evidence ref or note.

**`accept` folds into `advance`.** Within one plan the agent just advances its gate; the "return is a proposal the invoker may reject" duality lives at the *handoff between two plans*, not inside one.

## Consolidation (survey output)

A survey's output is **as structured as its consumer requires, and no more.**

- Consumed by a **machine** (a parent gate's `artifact` check) → the consolidation carries the matched field. A reviewer survey carries `verdict` (plus a prose `findings` list); the parent reads `consolidation.verdict`. The consolidation **is** the `review-result` artifact — no separate plumbing.
- Consumed by a **human** (e.g. a plan-approval checkpoint) → the consolidation can be pure prose. The Interrogator's "resolved understanding" needs no machine field.

Beyond that one field, consolidation is the agent's prose summary, handed up.

**Consistency guard (engine-enforced):** `consolidate` refuses a `verdict: APPROVE` while any item still has `result: fail`, unless an explicit `override_reason` is supplied. This is pure shape-checking — the engine is not judging quality, only refusing a verdict that contradicts its own recorded findings. It kills the weak-reviewer failure mode: dutifully recording "v3: fail," then rubber-stamping APPROVE.

## Engine verbs ↔ schema

| verb | applies | reads/writes |
|---|---|---|
| `current` | both | walk to the active item; emit its `imperative`; reports active-lease metadata when present (no session needed) |
| `claim --session-id <id> --claimed-by <role> [--worktree .] [--force --reason …]` | both | take the actor-authority lease; idempotent same-session resume; refuses a different active lease unless forced |
| `heartbeat --session-id <id>` | both | refresh the active lease's `last_heartbeat` (owner only) |
| `release --session-id <id> [--force --reason …]` | both | close the lease (`status: released`); owner only unless forced |
| `criteria <id>` | gated | emit `postconditions` + implied evidence types |
| `start <id>` | both | engine checks any `command`/`artifact` preconditions; agent asserts qualitative ones; `→ in-progress` |
| `advance <id> --evidence …` | gated | check all `postconditions`; `→ complete` |
| `record <id> --result pass\|fail [--finding …]` | survey | record the check outcome; `→ complete`; never blocks |
| `append <id> …` | survey | add an item from context |
| `consolidate` | survey | every item visited → produce `consolidation` (verdict / understanding) |
| `skip <id> --reason …` | both | `→ skipped` (OBE; state op) |
| `block <id> …` | both | `→ blocked`; append to `blockers` (bubble to parent) |
| `reopen <id> --reason …` | gated | `complete → in-progress`; `rework_count++`; escalate at cap; clears any `waived`/`attested` markers |
| `attest <id> --cond <id> [--which preconditions\|postconditions] [--evidence <eid>]` | both | satisfy a `check: null` condition by manual attestation; OR satisfy an `artifact` postcondition **by reference** to an already-attached artifact `<eid>` (verified: exists + `evidence_type` + `match`) — avoids re-attaching the same artifact to a sibling gate. `--which` selects the condition list (default `preconditions`). Refuses `command`/`git-change-policy` checks. |
| `waive <id> --cond <id> [--which postconditions] --authority … --reason … [--force]` | both | human override: satisfy a condition **by waiver**; refused unless its `override_policy.allowed` (or `--force`); records a `waiver` evidence record + a durable `waived` marker |
| `flag-candidate …` | both | record an out-of-scope discovery in `triage_candidates` |

Every **mutating** verb above (`start`/`advance`/`record`/`consolidate`/`skip`/`block`/`reopen`/`append`/`attest`/`waive`/`attach`/`flag-candidate`) accepts an optional `--session-id`; it is required, and checked against the active lease, **only once a lease has been claimed** (see *Engine session*).

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
3. **Cross-artifact write-back.** A child survey's `consolidation` *is* the parent gate's `review-result` evidence (the parent's `artifact` check reads `consolidation.verdict`). The remaining mechanic is how the engine — working on one checklist file at a time — attaches that to the parent file; likely an `attach`/`--from-child <work-id>` step before the parent's `advance`.
4. **Evidence payload typing.** Left loose; `review-result` vs `command-output` differ a lot. May need per-type payload schemas before `artifact` checks validate reliably.
