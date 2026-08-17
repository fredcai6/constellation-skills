This file holds the EXACT target content for the three workbench files and the CREW_CONTEXT.md
edit, for the implementer to apply byte-for-byte. Not committed as final documentation -- a
working spec consumed by g1-implement/g1-review.

=== skills/workbench/SKILL.md (full replacement) ===
---
name: constellation-workbench
description: Use when work needs the shared workflow templates, or a pointer to the checklist engine's CLI fallback and MCP door -- the engine's verbs and mechanism are taught by the door's own tool descriptions, not by this skill.
---

# Constellation Workbench

Retired as a taught procedure (issue #565): the MCP door's own tool descriptions now teach the
checklist engine's verbs, evidence shape, and mechanism directly, so this skill no longer
restates them. What remains: the four shared templates every role's checklist instantiates
from (`templates/`), and the one pointer below, which stays load-bearing because other skills
and two independent test suites cite it directly.

## Checklist engine

Drive a controller one step at a time — by default via the MCP door's `spine_status`/`spine_lease`/`spine_start`/`spine_advance`/`spine_evidence`/`spine_halt`/`spine_survey_result` tools when this agent owns the process's bound spine (see `references/checklist-engine.md` — MCP door); CLI fallback, always available and the only path for an in-session dispatched crew member driving its own plan or survey: the absolute path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless that repo vendors the script. See `references/checklist-engine.md`.

Templates: `templates/DEFAULT.template.json`, `templates/WORKFLOW_CLOSEOUT.template.md`, `templates/STATE_NOTE.template.md`, `templates/CONSTELLATION_FEEDBACK.template.md`. References: `references/checklist-engine.md`, `references/status-model.md`.
=== end SKILL.md ===

=== skills/workbench/references/checklist-engine.md (full replacement) ===
# Workbench Checklist Engine

Retired as a taught procedure (issue #565): the verb loop, session-lease claim/heartbeat/release
mechanics beyond what's below, refresh fulfilment mechanics beyond what's below, waive, the
engine's guaranteed mechanism, bubble-up channels, the context-read step, and the template-set
table are now taught by the MCP door's own tool descriptions and by each role's own spine/survey
template, not by this file. What remains is the content proven load-bearing: the sole written
authority (an existing test suite, `tests/test_mcp_adoption.py`, pins it verbatim) that the MCP
door is the default path while the CLI fallback survives, plus a companion reference two other
skills cite by section name.

The engine is the deterministic state machine an agent transacts with **one step at a time**. It holds canonical state and enforces *mechanism* — ordering, evidence shape, the rework cap, the consolidation guard — and never judges quality. An agent does not re-read and self-manage a checklist; it asks the engine what to do, does it, and reports back.

Tool, by default when this agent owns the process's bound spine: the MCP door's `spine_status`/`spine_lease`/`spine_start`/`spine_advance`/`spine_evidence`/`spine_halt`/`spine_survey_result` tools (see "MCP door" below). CLI fallback, always available, and the only path for an in-session dispatched crew member driving its own plan or survey: `python <skill-dir>/scripts/checklist_engine.py --file <checklist.json> <verb>`. Installed copies rewrite that command to an absolute path; run that absolute path and do not resolve `scripts/` from the target repo unless that repo vendors the script. In this source repo, the same script lives at `scripts/checklist_engine.py`. Schema: `docs/CHECKLIST_SCHEMA.md`. Model: `docs/CHECKLIST_ENGINE_DESIGN.md`.

## MCP door: default path, and who it is NOT for

An MCP door (`scripts/mcp_spine_server.py`, tool prefix `mcp__spine__`) wraps this engine as 9 tools covering all 18 of its verbs: `spine_status` (`current`), `spine_lease` (`claim`/`release`/`heartbeat`), `spine_start` (`start`), `spine_advance` (`advance`), `spine_evidence` (`attest`/`attach`/`waive`), `spine_halt` (`block`/`resume`/`skip`/`reopen`), `spine_survey_result` (`record`/`consolidate`), `spine_capture` (`append`/`flag-candidate`), `spine_amend` (`amend`). It never reimplements the engine — every tool builds an argv and calls `checklist_engine.main(argv)`, so refusals, evidence, and the rework cap ride through unchanged.

**Default:** when it is configured for your session and it is YOUR OWN spine — the one this process's door is bound to — call these tools instead of shelling out to the CLI. They wrap the identical engine call and surface the identical refusal/evidence contract, so nothing about drive discipline changes; only the invocation does.

**Where the binding comes from (issue #603).** There are exactly **two** moments, and neither is a per-call argument: `SPINE_FILE`/`SPINE_SESSION` read from the environment at server start, **or** a successful `spine_open`, which binds this process to the spine it just minted. That second moment is what lets a session that starts with nothing bound mint its own work and immediately drive it — before #603 the binding was fixed at launch, which is before the spine exists, so an orchestrator had to fall back to the CLI.

Two properties follow, and both are enforced rather than described:

- **Unbound fails closed.** An unset, empty, missing, non-file or unreadable `SPINE_FILE` makes every tool return a refusal naming how to bind — never a confident answer about some other spine, never a crash, never silence.
- **Still one spine per process.** `_identity_violation` continues to refuse any call resolving to a spine other than the bound one, and a rebind is refused while this process holds an active lease. Bind-on-open changed *when* the binding is decided, never *how many* are live at once.

**The door does not follow you into a Task-tool subagent's OWN work.** A Task-tool subagent inherits its dispatching process's MCP scope wholesale, so the tools are technically callable from inside it — but they stay bound to whatever spine the DISPATCHER's process was launched for, never the subagent's own plan or survey file. Concretely: a Commander may drive `spine.json` through the door, because that is the Commander's own process's bound spine. A dispatched Task-tool Implementer or Reviewer subagent must drive its own `IMPLEMENTER_PLAN.json` or `REVIEW_SURVEY.json` through the CLI (`scripts/checklist_engine.py`) instead — calling a door tool from inside that subagent would operate on the Commander's `spine.json`, not on the file the subagent actually owns. This is not a style preference: the door is a pass-through to whichever file its own environment named, and that file is the parent's.

**A `run_crew.py`-dispatched crew is not that case — it IS the door's owner.** `run_crew.py` launches a fresh headless `claude -p` process with its own `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` bound in ITS OWN environment before its MCP server starts, so that process's door is bound to its own plan or survey from the first call, never the dispatcher's. Such a crew drives its own spine through the door, gate by gate, exactly as the implementer and reviewer skills instruct — do not send it to the CLI instead.

**Every verb has a door tool; none is CLI-only anymore.** The door used to cover 13 of 18 verbs and leave `skip`, `reopen`, `append`, `amend` and `flag-candidate` CLI-only; that carve-out is retired (issue #559: "anything that we want to do for the spine needs to be accessible via mcp... anything that we can only do via the cli is a defect"). There is no CLI-fallback table below this one — every verb the engine has is reachable through this door.

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
=== end checklist-engine.md ===

=== skills/workbench/references/status-model.md (full replacement) ===
# Constellation Status Model

Retired as a taught procedure (issue #565) except for the two sections below, which stay
load-bearing: `Crew Return Status` is pinned verbatim by `tests/test_commander_evidence_convention.py`
and cited by `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`; `Review Verdict` is
the field `skills/reviewer/templates/REVIEW_RESULT.template.md` and
`skills/implementer/templates/IMPLEMENTER_RESULT.template.md` both point at by name. Gate status
is directly observable from the engine's own `current` output (`global-everyone.md`, "Engine
output is the state channel") and needs no separate table; Commander Gate Decision vocabulary
is uncited internal prose, not an engine-enforced convention.

## Crew Return Status

Use for implementer/reviewer result status:

```text
complete | partial | blocked | out-of-scope | failed
```

Rules:

- `partial` requires completed portion, missing portion, and next action.
- `blocked` requires blocker and needed authority/evidence.
- `out-of-scope` requires scope concern and return-to-Commander note.
- `failed` requires failure evidence and recommended recovery.

## Review Verdict

Use for reviewer judgment:

```text
APPROVE | BLOCK | COMMENT
```

Rules:

- `APPROVE` means no blockers found against handoff, evidence, scope, and project rules.
- `BLOCK` requires blockers.
- `COMMENT` means observations only; gate may still need Commander decision.
=== end status-model.md ===

=== docs/agents/CREW_CONTEXT.md -- edit ONLY the "Python Invocation" section (lines ~17-38), everything else unchanged ===
Replace this exact block:

    Measured on this host on 2026-08-10: `py` and `python` both resolve to
    `/home/tommy/.local/bin/{py,python}`, both report Python 3.12.3, and both have pytest
    9.1.1. `python3` resolves to `/usr/bin/python3.12`, also Python 3.12.3, but has no pytest
    installed. None of this is guaranteed to match CI's pin — a local green is evidence,
    never the gate.

with:

    Measured on this host on 2026-08-17: `py`, `python`, and `python3` all resolve to
    Python 3.12.3 with pytest 9.1.1 installed (`py` and `python` at
    `/home/tommy/.local/bin/{py,python}`; `python3` at `/usr/bin/python3.12`). This superseded
    an earlier 2026-08-10 measurement on this same host that found `python3` without pytest --
    the interpreter-to-pytest mapping on a given host is not fixed over time, which is exactly
    why the check-before-you-run instruction above stands regardless of any measurement here.
    None of this is guaranteed to match CI's pin — a local green is evidence, never the gate.

Do not touch anything else in CREW_CONTEXT.md.
=== end CREW_CONTEXT.md edit ===
