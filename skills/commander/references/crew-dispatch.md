# Crew dispatch mechanics

How a Commander gate dispatches an Implementer/Reviewer crew: the launch wrapper, the two backends, and crew recovery. Read this before dispatching a crew from a `gN-implement`/`gN-review` task (a reasoning gate dispatches no crew, so none of this applies to it).

## Never hand-launch a crew

When a gate dispatches a crew, that dispatch goes through `scripts/run_crew.py`, not a raw CLI call. The wrapper launches foreground/blocking, assigns a stable session name, records durable launch metadata in `.agent-work/<work-id>/crew-runs.json` before the crew starts, captures stdout/stderr, and refuses to return success unless the expected result artifact exists **and is fresh** (mtime at/after dispatch, so a stale prior-attempt leftover never passes). It refuses a duplicate crew on the same gate/worktree unless the prior attempt is explicitly abandoned (`--abandon <session> --relaunch`).

**The write to this job/gate-addressed result path — `.agent-work/<work-id>/crew-handoffs/<gate>-<role>-result.md` — is the delivery**, not the crew's `SendMessage` announcement on completion (that ping is best-effort only, per `commander-core.md`; the instance it targets may no longer be live, or may never have been addressable to it at all — #507, #370, #413). A **resumed or relaunched Commander runs `scripts/recover_crews.py <work-id>` FIRST on cold start** — before assuming any dispatch is still needed, not only "before each dispatch" — because `classify_entry` discovers an already-`STATE_COMPLETE` crew purely from the durable registry and result artifact, with zero dependency on which Commander instance is asking. A relaunched Commander that skips this and redispatches blind duplicates a crew whose result was already sitting on disk, undelivered only because the announcement misrouted.

Before `execute` and before each dispatch, run `scripts/recover_crews.py <work-id>` and only launch when it reports no unresolved running/resumable/conflicting crew; resume a recoverable attempt (`run_crew.py --resume <session>`) or explicitly abandon/relaunch rather than colliding two crews in one worktree. The wrapper is the process/launch layer only: it does not advance gates, integrate results, or touch git.

## Backend: CLI vs Agent-tool harness

The wrapper is backend-pluggable behind one result contract (see `docs/superpowers/specs/2026-07-07-crew-backend-design.md`). Two backends:

- **`cli`** spawns a headless `claude` CLI subprocess.
- **`external`** records the durable entry + duplicate-guard but spawns nothing — the crew is dispatched out-of-band as your own synchronous Agent-tool subagent, then verified with `run_crew.py --verify-result <session>`.

Select with `--backend {auto,cli,external}` (auto-detects: CLI on PATH → `cli`, else `external`); the `--dispatch {spawn,external}` form also works and an explicit choice always wins. In the Constellation Agent-tool harness there is no headless `claude` CLI, so dispatch the implementer/reviewer as synchronous Agent-tool subagents via `--dispatch external` (or `--backend external`) + `--verify-result`; do not re-derive a hand-rolled workaround.

## Crew recovery

External recovery is out-of-band: `SendMessage` to the crew's `agentId` to resume it in place, else `--abandon … --relaunch`. Key the recovery decision to `recover_crews.py`'s state vocabulary:

- A **`resumable`** crew (recorded running, PID dead, result missing) is resumed IN PLACE via the `SendMessage` primitive (see `skills/_shared/windows.md` §2 "Resuming a previously-spawned agent" — the primitive is a tool call, not a CLI flag).
- A **`needs-abandon`** crew is retired with `--abandon <session> --relaunch`.
- A **`conflict`** (a rival crew already live on this gate/worktree) is a Commander decision, not an automatic relaunch.
