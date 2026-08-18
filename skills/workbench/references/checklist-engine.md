# Workbench Checklist Engine

Retired as a taught procedure (issue #565): the verb loop, session-lease claim/heartbeat/release
mechanics beyond what's below, refresh fulfilment mechanics beyond what's below, waive, the
engine's guaranteed mechanism, bubble-up channels, the context-read step, and the template-set
table are now taught by the MCP door's own tool descriptions and by each role's own spine/survey
template, not by this file. What remains is the content proven load-bearing: the sole written
authority (an existing test suite, `tests/test_mcp_adoption.py`, pins it verbatim) that the MCP
door is the default path, plus a companion reference two other skills cite by section name.

The engine is the deterministic state machine an agent transacts with **one step at a time**. It holds canonical state and enforces *mechanism* — ordering, evidence shape, the rework cap, the consolidation guard — and never judges quality. An agent does not re-read and self-manage a checklist; it asks the engine what to do, does it, and reports back.

Tool, by default when this agent owns the process's bound spine: the MCP door's `spine_status`/`spine_lease`/`spine_start`/`spine_advance`/`spine_evidence`/`spine_halt`/`spine_survey_result` tools (see "MCP door" below). An in-session dispatched crew member driving its own plan or survey is not that case: one door drives one spine at a time and refuses to rebind while its owner still holds that spine's lease, so the door cannot reach that file at all. That is not a second-best path with a working primary behind it — such a plan or survey is driven by this skill's bundled checklist engine, and by nothing else. Schema: `docs/CHECKLIST_SCHEMA.md`. Model: `docs/CHECKLIST_ENGINE_DESIGN.md`.

## MCP door: default path, and who it is NOT for

An MCP door (`scripts/mcp_spine_server.py`, tool prefix `mcp__spine__`) wraps this engine as 9 tools covering all 18 of its verbs: `spine_status` (`current`), `spine_lease` (`claim`/`release`/`heartbeat`), `spine_start` (`start`), `spine_advance` (`advance`), `spine_evidence` (`attest`/`attach`/`waive`), `spine_halt` (`block`/`resume`/`skip`/`reopen`), `spine_survey_result` (`record`/`consolidate`), `spine_capture` (`append`/`flag-candidate`), `spine_amend` (`amend`). It never reimplements the engine — every tool builds an argv and calls `checklist_engine.main(argv)`, so refusals, evidence, and the rework cap ride through unchanged.

**Default:** when it is configured for your session and it is YOUR OWN spine — the one this process's door is bound to — call these tools instead of shelling out to the CLI. They wrap the identical engine call and surface the identical refusal/evidence contract, so nothing about drive discipline changes; only the invocation does.

**Where the binding comes from (issue #603).** There are exactly **two** moments, and neither is a per-call argument: `SPINE_FILE`/`SPINE_SESSION` read from the environment at server start, **or** a successful `spine_open`, which binds this process to the spine it just minted. That second moment is what lets a session that starts with nothing bound mint its own work and immediately drive it — before #603 the binding was fixed at launch, which is before the spine exists, so an orchestrator had to fall back to the CLI.

Two properties follow, and both are enforced rather than described:

- **Unbound fails closed.** An unset, empty, missing, non-file or unreadable `SPINE_FILE` makes every tool return a refusal naming how to bind — never a confident answer about some other spine, never a crash, never silence.
- **Still one spine per process.** `_identity_violation` continues to refuse any call resolving to a spine other than the bound one, and a rebind is refused while this process holds an active lease. Bind-on-open changed *when* the binding is decided, never *how many* are live at once.

**The door does not follow you into a Task-tool subagent's OWN work.** A Task-tool subagent inherits its dispatching process's MCP scope wholesale, so the tools are technically callable from inside it — but they stay bound to whatever spine the DISPATCHER's process was launched for, never the subagent's own plan or survey file. Concretely: a Commander may drive `spine.json` through the door, because that is the Commander's own process's bound spine. A dispatched Task-tool Implementer or Reviewer subagent must drive its own `IMPLEMENTER_PLAN.json` or `REVIEW_SURVEY.json` through this skill's bundled checklist engine instead — calling a door tool from inside that subagent would operate on the Commander's `spine.json`, not on the file the subagent actually owns. This is not a style preference: the door is a pass-through to whichever file its own environment named, and that file is the parent's.

**A `run_crew.py`-dispatched crew is not that case — it IS the door's owner.** `run_crew.py` launches a fresh headless `claude -p` process with its own `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` bound in ITS OWN environment before its MCP server starts, so that process's door is bound to its own plan or survey from the first call, never the dispatcher's. Such a crew drives its own spine through the door, gate by gate, exactly as the implementer and reviewer skills instruct — do not send it to the CLI instead.

**Every verb has a door tool; none is CLI-only anymore.** The door used to cover 13 of 18 verbs and leave `skip`, `reopen`, `append`, `amend` and `flag-candidate` CLI-only; that carve-out is retired (issue #559: "anything that we want to do for the spine needs to be accessible via mcp... anything that we can only do via the cli is a defect"). There is no CLI-only-verb table below this one — every verb the engine has is reachable through this door.

The CLI is always available and always correct; the door is an additive fast path for the agent that owns the bound spine. Nothing here removes or discourages the CLI.

## Session lease: who owns the checklist state

The engine enforces **actor authority** over a checklist's state so a resumed or duplicated parent session cannot concurrently mutate the same plan. One session leases the checklist; mutating verbs then require that session's id.

```
claim     --session-id <id> --claimed-by <role> [--worktree .] [--force --reason "..."]
heartbeat --session-id <id>
release   --session-id <id>
```

Door equivalent, when this is your own bound spine: the `spine_lease` tool, with `action=claim|heartbeat|release`, `claimed_by`, `worktree`, `force`, `reason` — no session id argument at all; the door reads the bound session from `SPINE_SESSION` in its own environment, so it cannot be pointed at another session's lease by argument.

- `claim` takes the lease. The **same** `session_id` re-claiming is idempotent (it just refreshes the heartbeat) — safe to call on resume. A **different** active session is refused; take over only with `--force --reason "..."`, which records the prior session for audit.
- `heartbeat` proactively refreshes your lease — only needed for an idle wait where no mutating verb will fire (mutating verbs refresh it for you); `release` closes it when you are done.
- **Once a lease exists, every mutating verb needs `--session-id <id>` matching the active lease** (`start`, `advance`, `record`, `consolidate`, `skip`, `block`, `reopen`, `append`, `amend`, `attest`, `waive`, `attach`, `flag-candidate`). Pass it on each call. Read-only `current` needs no session and shows the active lease.
- A lease goes **stale** if its heartbeat lapses (config `lease_stale_seconds`, default 1800s). Staleness gates **non-owners only**: as the **owner** you are never blocked by your own staleness — every mutating verb you issue refreshes the heartbeat, so a long step or idle gap self-heals on your next verb (no re-claim, no takeover record). A **different** session must `claim` the stale lease (same id, or `--force --reason`) before mutating — the engine refuses it and tells it to claim.
- A checklist with **no lease** behaves exactly as before: mutating verbs work without `--session-id`. Only claim a lease when your workflow wires it (the Commander spine claims at `init`, releases at `archive`).

## Refresh: reach-up without a handoff doc

A `refresh-request` (#179) is an ordinary evidence item — `attach <gate> --type refresh-request --field seam=<gate> --field why_ref=<why-record id>` — pointers only, never a copy of state. `has_pending_refresh_request(cl, gate)` is a pure predicate: true while a non-superseded `refresh-request` targets that gate. `current` surfaces both halves of this for a cold-starting agent: a `DIGEST:` line (the latest running understanding — the latest non-mechanical, non-superseded `why`) and, when one is pending, a `REFRESH REQUESTED:` line naming the gate and the why-record it was raised against. Together these **are** the handoff (`global-everyone.md` §reach-up) — no separate document is written or read.

**Fulfilment.** Nothing marks a refresh-request's evidence item superseded on its own path — only `reopen`'s cascade supersedes evidence, and that resets the gate for rework, the wrong tool here. Instead, fulfilment falls out of the predicate's own shape: both `has_pending_refresh_request` and the `current` display are always evaluated against the checklist's **current** active gate, never a historical one. Once the fresh agent advances the gate the request named, `active_id(cl)` moves past it, and the request's `seam` no longer matches anything being asked about — `REFRESH REQUESTED:` simply stops appearing. No new verb, no evidence mutation, no hand-edited JSON: completing the gate the request named is what clears it.

The reach-up `current`-alone cold start holds for both `gated` and `survey`-driving roles (reviewer, interrogator) — a `refresh-request` attached to a `survey` checklist now surfaces on `current` too.

## Obey refusals

The engine answers illegal moves with an imperative, e.g. `REFUSED: g1: postconditions unmet ['c1']`. Treat that as the next instruction — fix the named gap, do not work around it. The refusal *is* the gate.
