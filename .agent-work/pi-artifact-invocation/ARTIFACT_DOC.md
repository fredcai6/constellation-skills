## Artifact invocation

Run one bounded Implementer handoff directly, without a Commander paraphrase:

```bash
npm start -- invoke --role implementer --input /path/to/handoff.md \
  --cwd /path/to/repo --source /path/to/constellation-skills \
  --python /path/to/working/python
npm start -- invoke-status --run /printed/run/directory
npm start -- invoke --run /printed/run/directory
npm start -- usage --run /printed/run/directory
```

The input is the existing Constellation Implementer Markdown handoff. Required
sections: Gate, Task, Protected Intent, Test Mode, Close Criteria, Allowed Scope,
Required Evidence, Verification Commands, Authority, Stop Conditions, Return Format.
Name the exact output path in `## Result Artifact`; filled older handoffs using
`Write the full IMPLEMENTER_RESULT to ...` with backticked name/path also work.
Paths are resolved against `--cwd`; referenced project documents remain references.
The template is in the Constellation corpus; this project doesn't define another
assignment format. An example is `examples/artifact-invocation/implementer.md`.
Run that example only in a fresh disposable directory, not in a project root.

The invocation records an exact input snapshot/hash, stable versioned Implementer
prompt, Pi session pointer, attempts, and a single engine gate. This narrow path
has its own gate; it neither binds nor advances an external Commander's gate and
does not claim the full installed Implementer skill workflow. Existing `new/chat`
Commander behavior is unchanged. This version supports Implementer only.

Default bounds: Sonnet, 3 attempts, 20 turns per attempt, 8192 output tokens per
response, 600 seconds. Override limits at creation with the existing limit flags.
Resume uses recorded configuration. It refuses edited input/snapshot files; make
a corrected handoff and a new invocation instead. A new invocation refuses an
already-existing result. `--message` and `--task` are not assignment channels.

The agent writes its named result then calls argument-free `submit_result`.
Delivery validates freshness, assigned gate, lowercase status and key result
sections; it does not judge whether the claims are true. Only `complete` after a
successful runtime invocation advances/releases the invocation gate. Other results,
missing outputs, and provider failures leave it open for inspection/resume. The
receipt contains paths/hashes/status/timing/usage, never the agent's explanatory
narrative. Independent review and human acceptance remain separate responsibilities.

Before recovering a crashed controller, inspect its lock and verify the recorded
PID is no longer running; only then remove the stale controller.lock. Resume with
`--recover-interrupted yes` explicitly records an interrupted attempt; it never
assumes its usage was zero or its output complete. A successful runtime followed
by engine integration failure can recover its verified result without another
model request. Do not edit engine checklist files.

Each role session now writes `events.jsonl`: invocation/request IDs, timestamps,
monotonic durations, first streamed content latency, usage including cache reads
and writes, tool durations when available, and outcomes. No prompts or tool output
are copied into this metadata ledger. `usage` lists every recorded request and
known estimated dollar subtotal; missing usage stays null with an unknown count.
Costs come from Pi's model catalog, not a provider invoice. Request duration
includes provider/network wait; queue time cannot currently be separated. Legacy
sessions before this change have no new ledger, so `usage` is not historical billing.
Nested Commander/crew costs are counted per request; their overlapping elapsed
times must not be added as though they were sequential. Hosted cache hit rates
are measured, not guaranteed. Existing Commander prompts are not migrated yet.
