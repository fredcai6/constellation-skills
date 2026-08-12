# Latitude Contract: `epic-418-followon` — REFRESHED 2026-08-10

**STATUS: REFRESHED and CONFIRMED by Tommy, 2026-08-10, in session.** The 2026-08-09 contract
expired at its own stated expiry (the wave-1 boundary; #424 merged two waves ago). This replaces it.
The superseded text is preserved in git history and in `ADMIRAL_LOG.md`.

The predecessor contract's full text, decision classes and pre-rulings are carried forward except
where this document overrides them. Everything under "Standing rulings carried forward" in the
superseded version remains binding.

## What changed, and why this needed a refresh

Two things moved at once:

1. **The goal changed.** Tommy, 2026-08-10: *"the goal of this round is make agents use the mcp
   instead of the cli. in doing this, we should also maintain usability across multiple systems."*
   That supersedes the confirmed wave plan, under which wave 2 was #421 (C) and wave 3 was #423 (E).
   #423 is already out of the epic at his direction; #421 is blocked on a launchable, usable door.
2. **The ownership model was specified.** See the next section. It is new doctrine for how spines,
   agents and leases relate, and it is what the current work implements.

## The ownership model — CONFIRMED 2026-08-10

Tommy's specification, in his terms:

> spines are really assigned per task and then we assign agents to work the spine (one at a time).
> there can be multiple spines, e.g. a commander spine will have a task to kick off an implementer
> spine, so we have traceability all the way down. our mcp invocation therefore needs to be per
> task, but we'll want to provide a who as well so we don't accidentally step on each other. I want
> to make sure we're robust from the beginning for agents dropping off a task and respawning so the
> identity of who is working on what isnt lost. [...] how do you make sure agents don't accidentally
> claim the wrong thing? this is what a lease has done in the past and we gave the ability to force
> claim a lease. the same construct should basically work, basically throws a flag to have an agent
> double check that it's working on the right thing if there looks like a conflict. we don't have to
> make it foolproof, just keep out the easy failures for now.

Settled consequences, confirmed with *"that sounds about right, or at least good enough to start
working"*:

- **A spine belongs to a task, not to an agent or a session.** Agents are assigned to it, one at a
  time. Spines nest, and the nesting is the traceability.
- **The lease keys on the ASSIGNMENT, not the process instance.**
  `constellation/<work-id>/<gate>/<role>` — deliberately **without** `run_crew.py`'s `attempt-<n>`
  tail. Keying on the attempt would make every legitimate respawn read as a different claimant,
  turning routine recovery into a recorded force-takeover. `attempt-<n>` stays in the crew registry
  and log paths, where its job is tracing which process did what.
- **Identity is derived, never typed.** Every spine file already carries `work_id`, which is exactly
  the nesting the identity needs; the claiming role supplies the rest. Observed drift that motivates
  this: four live spines in this epic carry four different ad-hoc conventions — a session UUID, a
  never-claimed `None`, and two hand-typed `<gate>-session` strings — while this very spine's own
  `init` imperative asks for the stable `admiral-epic-418-followon`.
- **Conflict handling is the existing lease construct, unchanged.** Same id → idempotent resume;
  a different active non-stale id → refuse, which is the flag that makes an agent double-check;
  `--force --reason` → takeover recording `previous_session_id` and `takeover_reason`; staleness
  (1800s default) lets a genuinely dead agent self-yield. **Not foolproof by design.**
- **Per-process door binding, not per-call addressing** (Admiral ruling, 2026-08-10, delegated).
  One door per task-process satisfies "per task" because exactly one agent works a spine at a time.
  This preserves `_identity_violation` whole, including the `from_child` path confinement that stops
  any JSON carrying a `consolidation` key from closing a gate. Per-call addressing remains available
  later if a genuine cross-spine mutation appears; today the only cross-spine operation is
  `from_child`, which already works.

## Epic Intent (revised)

Make agents use the MCP door instead of the CLI, with per-task spine ownership and an identity that
survives an agent dropping off and respawning. Cross-platform usability matters but is explicitly
**not** this round's problem — Windows may stay broken if the fix is not trivial.

## Success Shape

- An agent dispatched through `run_crew.py` drives **its own** spine through the door, measured from
  its own call record: door calls > 0 and CLI engine invocations == 0, per the F/F2 measurement
  contract (`decision:count-from-the-call-record`).
- A respawned agent on the same assignment **resumes** its lease rather than force-claiming it —
  no recorded override for routine recovery.
- A **measured negative is a complete, successful deliverable.** Carried unchanged.

## Checkpoint Protocol — AFK MODE

**Tommy is AFK.** Granted 2026-08-10: *"you're free to get stuff rolling again. I'm going afk, so
you have latitude to try things and use your best judgement."*

- **Run ahead.** Do not stop and wait at wave boundaries. Write the transition, log it, continue.
- **A surfaced decision QUEUES; it does not halt the run.** Append it to
  `.agent-work/epic-418-followon/DECISIONS_PENDING.md` with the options and a recommendation, route
  the work around it, and keep going. Halt the whole run only if nothing else can proceed without it.
- **The AFK grant is latitude to try things, not to do irreversible things.** The hard floor below
  is unchanged by it.

## Hard floor — still surfaced, AFK grant notwithstanding

These are outward-facing or costly to reverse, and the grant to "try things" does not reach them:

| Action | Disposition |
|---|---|
| Merge or push to `main` | **surfaced** — matches `ORCHESTRATOR_CONTEXT.md`; local commits stay allowed |
| Closing an issue | **surfaced** (carried) |
| Editing `docs/agents/*` doctrine | **surfaced — always** (carried; ORCHESTRATOR_CONTEXT names it a human's call) |
| Scope change: adding or dropping an issue | **surfaced** |
| A workstream cannot meet its stated obligation | **surfaced — always** (the #308 shape) |
| Out-of-taxonomy | **queues** with one line on why it fit no class |

Everything else the predecessor contract delegated stays delegated: wave composition and replanning,
architecture and structural change, issue filing and commenting, fix-now triage under R4, model tier,
and departing from the spec's stated order when a link proves untrue.

## Permission Prerequisites

Every row of the predecessor's pre-cleared table carries forward. Explicitly still in force for this
round's work: **starting MCP server processes**, **writing project-scope `.mcp.json`**, per-dispatch
config generation, **local MCP scope registration** (`claude mcp add -s local`, which writes
`~/.claude.json` and no tracked file), running the installer, the full test suite, and local commits.
`settings.json` is never touched — that boundary is in the spec and is unchanged.

Test suite invocation, settled and not to be re-derived (#454):
`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`. **Local caveat, measured 2026-08-10:** on this
host `py` and `python` are the same install at `~/.local/bin` and both carry pytest 9.1.1;
`/usr/bin/python3` is the one WITHOUT pytest. `docs/agents/CREW_CONTEXT.md` states the opposite and
is wrong here — filed as #561, not patched, because `docs/agents/*` is a human's call.

## Pre-Rulings

All predecessor pre-rulings carry forward unchanged. Added this refresh:

- `decision:identity-is-derived` — the lease identity is computed from the spine's own `work_id` plus
  the claiming role. It is never hand-typed into an imperative, a state note, or a launch order.
  Drift was observed four times in this epic alone. @grade: settled/human · 2026-08-10
- `decision:lease-keys-on-assignment` — the lease identity excludes `attempt-<n>`, so a respawn
  resumes instead of force-claiming. @grade: settled/human · 2026-08-10
- `decision:door-binds-per-process` — one door per task-process; no per-call spine addressing until
  something forces it. @grade: settled/admiral · 2026-08-10 · reversible
- `decision:cold-review-every-implementer` — carried from the 2026-08-10 human ruling: every
  implementer gets a cold reviewer. Two review rounds on #555 each found a real user-scope write
  that CI was green through. @grade: settled/human

## Expiry

**Tommy's return from AFK**, or **2026-08-13T00:00Z**, whichever comes first. On return, present the
queued decisions in `DECISIONS_PENDING.md` and re-confirm before further dispatch.

## Confirmation

**2026-08-10 — CONFIRMED by Tommy in session.** The ownership model confirmed with *"yup, that
sounds about right, or at least good enough to start working"*; the latitude granted with *"you're
free to get stuff rolling again. I'm going afk, so you have latitude to try things and use your best
judgement."* Recorded as the `resume` reason on the spine's `execute` gate and in `ADMIRAL_LOG.md`.
