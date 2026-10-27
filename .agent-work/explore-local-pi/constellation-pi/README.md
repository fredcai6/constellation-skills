# Constellation Pi

A small, evolving foundation for running Constellation workflows as Pi sessions.
Pi owns the Commander, Implementer, and Reviewer sessions. Claude supplies the model.
The existing Constellation engine owns checklist state, checks, evidence, and leases.
Its CLI and MCP interfaces remain unchanged.

This first version runs a narrow Commander path:

1. Commander proposes a plan; the human approves it.
2. Commander dispatches an Implementer in a separate Pi session.
3. Commander dispatches an independent Reviewer in another Pi session.
4. Human accepts the result; the runtime releases the Commander lease.

It does not yet run every gate of the installed Commander skill. Remote access,
additional model providers, GPU inference, worktree creation, and publishing are deferred.
Crew tools follow role conventions; this is not a security sandbox. Use a dedicated
branch or worktree for engineering tasks. Reviewer can run tests through bash.

## Install

Requires Node 22.19+ and a working Python 3.11+ distribution. Pi SDK is pinned in
package-lock.json; install lifecycle scripts are unnecessary.

```bash
npm ci --ignore-scripts
export ANTHROPIC_API_KEY='your key' # Prefer loading through your existing secret mechanism.
```

No credentials are copied into the project or run records. The runtime ignores ambient
Pi extensions, packages, MCP servers, skills and auto-loaded instruction files. Each role
gets a short explicit workflow prompt and reads the target project's AGENTS.md itself.

## Start a task

```bash
npm start -- new --cwd /path/to/target-repo \
  --source /path/to/constellation-skills --python /path/to/working/python \
  --id first-task --task 'Describe a small, concrete repository change'
```

The command prints a run directory under the target's `.constellation-pi/`. Add that
folder to the target's local Git exclude file if needed; it holds task text, model
conversations, results, engine evidence, and usage. Never commit it automatically.

Use the returned absolute path below:

```bash
npm start -- chat --run /path/to/run --message 'Propose a plan'
npm start -- approve --run /path/to/run --reason 'I approve this plan'
npm start -- chat --run /path/to/run --message 'Dispatch implementation'
npm start -- chat --run /path/to/run --message 'Dispatch independent review'
npm start -- status --run /path/to/run
npm start -- approve --run /path/to/run --reason 'I reviewed and accept the result'
```

Every chat resumes the same Commander JSONL session. Crews have separate persisted
sessions and their own engine checklists. A crew that stops without submitting a
structured result cannot advance the parent gate. An APPROVE verdict is necessary
for the review gate. Evidence is the crew's recorded observations, not independent
proof that its claims are true; the reviewer and human still assess the work.

## Overrides and recovery

Ordinary actions depend on the current gate. Overrides are for an explicit direction
from the human or higher-level agent. Record that principal and their reason:

```bash
npm start -- override --run /path/to/run --authority human \
  --reason 'I explicitly accept this missing check for this run' \
  -- waive review --cond evidence
```

After a reviewer BLOCK, `repair --run /path/to/run --reason 'Address the findings'`
returns work to implementation with the reviewer findings included in its handoff.
Commander can request the same repair within the approved plan.

This uses the engine's actual waive/reopen/resume/skip/amend/start/advance/attest operations. Engine rules
still apply. It is an auditable expression of authority, not an identity proof.
A waiver alone does not silently advance a gate. For a pending gate, explicitly
`override ... -- start GATE` before advancing; the directing principal and reason
are recorded for each operation. Terminal override advancement releases the lease. An explicitly directed
`override ... -- advance review` can advance it using the recorded reason.
An explicit reopen of implement/review also resets the corresponding crew gates
so prior successful results are not reused as new work. Recovery commands and routine
transitions will expand as we exercise actual failures; never edit checklist state
by hand. Use the existing engine CLI with the binding in run.json when an operation
is not yet exposed through this client.

A crashed controller can leave `controller.lock`. Verify its recorded PID is stopped
before removing the lock. The engine lease persists separately. A model timeout or
error preserves known session usage and its JSONL file for resumption.

## Cost and verification

Default model: `anthropic/claude-haiku-4-5` (override with `new --model`). Each prompt
has a 6-turn ceiling, 1024 output tokens per response, and a 120-second timeout.
For code-writing tasks, set `--max-output-tokens 4096` on `new` or `chat`; the
setting persists for subsequent Commander and crew invocations. Existing
`--max-turns`, `--timeout-ms`, and `--max-calls` limits can also be explicitly
updated on `chat` when resuming real work; counters and sessions are retained.
Turns/time/calls remain separately bounded. A truncated response stops the invocation with its
saved session and known usage, rather than repeating writes under the same cap.
A run allows 12 prompt invocations, including nested crew invocations. Counters persist
across resume. Known model cost is reported in status. These are request limits, not a
hard dollar cap; interrupted provider work may be billed before Pi receives usage.
Automatic retries, compaction calls, and cache warming are disabled.

```bash
CONSTELLATION_SOURCE=/path/to/constellation-skills \
CONSTELLATION_PYTHON=/path/to/working/python npm test
npm run typecheck
```

Tests use the real engine and mocked model sessions. They spend no model tokens.

A complete hosted Haiku fixture, including interrupted-session recovery, is recorded in
[the live validation report](docs/validation/live-commander-2026-10-22.md).

Commander dispatch accepts an optional bounded `instructions` handoff, so task
steering and review feedback reach the crew in addition to the approved plan.
