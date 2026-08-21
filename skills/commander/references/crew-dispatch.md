# Crew dispatch mechanics

How a Commander gate dispatches an Implementer/Reviewer crew: the launch wrapper, the two backends, and crew recovery. Read this before dispatching a crew from a `gN-implement`/`gN-review` task (a reasoning gate dispatches no crew, so none of this applies to it).

## Never hand-launch a crew

When a gate dispatches a crew, that dispatch goes through `scripts/run_crew.py`, not a raw CLI call. The wrapper launches foreground/blocking, assigns a stable session name, records durable launch metadata in `.agent-work/<work-id>/crew-runs.json` before the crew starts, captures stdout/stderr, and refuses to return success unless the expected result artifact exists **and is fresh** (mtime at/after dispatch, so a stale prior-attempt leftover never passes). It refuses a duplicate crew on the same gate/worktree unless the prior attempt is explicitly abandoned (`--abandon <session> --relaunch`).

**The write to this job/gate-addressed result path — `.agent-work/<work-id>/crew-handoffs/<gate>-<role>-result.md` — is the delivery**, not the crew's `SendMessage` announcement on completion (that ping is best-effort only, per `commander-core.md`; the instance it targets may no longer be live, or may never have been addressable to it at all — #507, #370, #413). A **resumed or relaunched Commander runs `scripts/recover_crews.py <work-id>` FIRST on cold start** — before assuming any dispatch is still needed, not only "before each dispatch" — because `classify_entry` discovers an already-`STATE_COMPLETE` crew purely from the durable registry and result artifact, with zero dependency on which Commander instance is asking. A relaunched Commander that skips this and redispatches blind duplicates a crew whose result was already sitting on disk, undelivered only because the announcement misrouted.

Before `execute` and before each dispatch, run `scripts/recover_crews.py <work-id>` and only launch when it reports no unresolved running/resumable/conflicting crew; resume a recoverable attempt (`run_crew.py --resume <session>`) or explicitly abandon/relaunch rather than colliding two crews in one worktree. The wrapper is the process/launch layer only: it does not advance gates, integrate results, or touch git.

## A harness-backgrounded command is never awaitable — do not park

`run_crew.py` **launches** foreground/blocking, but your own **process ends when your turn ends**. The agent harness can auto-background any Bash call that runs long — and the full suite (the postcondition every gated lane must run) takes on the order of two minutes, which is enough to trigger it. Once the harness has moved a call to the background, "wait for the completion notification" is **never a valid way to end a turn**: nothing resumes your process to act on that notification, so ending the turn to wait for it is indistinguishable from abandoning the run, no matter how correctly the underlying work finishes.

The fix is not "wait less" or "wait more carefully" — it is to never let a long-running step become backgroundable at all. Run it as one **foreground command that does not return until the result exists**, by polling from inside the same Bash call instead of ending your turn:

```bash
nohup <long command> > /tmp/out.log 2>&1 &
until grep -qE '<completion pattern>' /tmp/out.log; do sleep 15; done
tail -5 /tmp/out.log
```

Concretely, for the full-suite check that triggers this most often:

```bash
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q > /tmp/suite.log 2>&1 &
until grep -qE '^[0-9]+ (passed|failed|error)' /tmp/suite.log; do sleep 15; done
tail -5 /tmp/suite.log
```

The `until` loop itself is the one foreground command your turn is waiting on — it does not return until the suite's own summary line lands in the log, so there is nothing left to be silently backgrounded.

When a step genuinely cannot finish inside your turn, do not park on it either: run `spine_halt block` (the `spine_halt` MCP tool with `action=block`), recording the crew id and what you were waiting on, so a parent resumes deliberately (the E1 fail-up path). A prohibition alone ("do not park") does not prevent this — it has been stated explicitly in a launch order and still failed, because at the moment a turn ends, waiting looks like the correct and careful thing to do. Reach for the idiom above by name; do not improvise a new wait.

This Stop hook is authoritative over the context-trip advisory shown on `spine_status`/`current`: the advisory is non-binding guidance, never license to end a mid-gate turn. When the advisory says hand off and an open gate says otherwise, the gate wins — the resolution is `spine_halt block`, not a turn-end handoff.

## Backend: CLI vs Agent-tool harness

The wrapper is backend-pluggable behind one result contract (see `docs/superpowers/specs/2026-07-07-crew-backend-design.md`). Two backends:

- **`cli`** spawns a headless `claude` CLI subprocess.
- **`external`** records the durable entry + duplicate-guard but spawns nothing — the crew is dispatched out-of-band as your own synchronous Agent-tool subagent, then verified with `run_crew.py --verify-result <session>`.

Select with `--backend {auto,cli,external}` (auto-detects: CLI on PATH → `cli`, else `external`); the `--dispatch {spawn,external}` form also works and an explicit choice always wins. In the Constellation Agent-tool harness there is no headless `claude` CLI, so dispatch the implementer/reviewer as synchronous Agent-tool subagents via `--dispatch external` (or `--backend external`) + `--verify-result`; do not re-derive a hand-rolled workaround.

## Name a tier: the handoff's Suggested Model Tier field is what you resolve --model from

`run_crew.py` refuses a fresh or relaunched dispatch that names no tier at all (`CrewSpec.__post_init__`,
`decision:refuse-a-tierless-dispatch`) — never inherited from the dispatching process, never
defaulted. This file used to say nothing about model; it does now, because the place a tier is
deliberated (the handoff) and the place it takes effect (this dispatch) were disconnected until
this doctrine named the link explicitly. Every handoff's own **Suggested Model Tier** field
(`IMPLEMENTER_HANDOFF.template.md:94`, `REVIEWER_HANDOFF.template.md:60`) is the thing you resolve
`--model` from before calling `run_crew.py` — read it, decide the tier it implies, and pass
`run_crew.py --model <tier>` explicitly on that dispatch, not after. If the suggestion names a
reason tied to reasoning depth ("stronger — concurrency correctness rewards careful reasoning"),
also pass `--reasoning-effort <level>`, which the `cli` backend forwards to the launcher's own
`--effort` flag. `--resume` and a bare `--abandon` construct no `CrewSpec` and so need no `--model`
at all — the refusal, and this instruction, apply only to a fresh or relaunched dispatch.

## Name your dispatcher: --parent is required, and it is your own SPINE_SESSION

`run_crew.py` refuses a fresh or relaunched dispatch that names no `--parent` at all
(`CrewSpec.__post_init__`) — `crew-runs.json:parent` is what `verify_declared_dispatch.py`
checks a crew's dispatch against, and an absent value cannot be checked. Pass your own
`SPINE_SESSION` (the identity you were bound with, read from your own environment) as
`--parent`: `run_crew.py --parent "$SPINE_SESSION" ...`. `--resume` and a bare `--abandon`
construct no `CrewSpec` and so need no `--parent` at all — the refusal, like the model
requirement above, applies only to a fresh or relaunched dispatch.

## Crew recovery

External recovery is out-of-band: `SendMessage` to the crew's `agentId` to resume it in place, else `--abandon … --relaunch`. Key the recovery decision to `recover_crews.py`'s state vocabulary:

- A **`resumable`** crew (recorded running, PID dead, result missing) is resumed IN PLACE via the `SendMessage` primitive (see `skills/_shared/windows.md` §2 "Resuming a previously-spawned agent" — the primitive is a tool call, not a CLI flag).
- A **`needs-abandon`** crew is retired with `--abandon <session> --relaunch`.
- A **`conflict`** (a rival crew already live on this gate/worktree) is a Commander decision, not an automatic relaunch.
