# Prototype Result: MCP front door on the checklist engine

Excursion `exc-9-mcp-front-door`, run `explore-post-phase1`. Branch: logic. Location: throwaway worktree.

## Question

Does putting an MCP front door on the existing checklist engine let a cold agent drive a spine correctly with less teaching and fewer fumbles than the CLI door — and what does the production seam look like?

## Verdict

`answered-yes`

**Answer:** Yes, with a caveat that changes what you should conclude from it. Across two replicates per arm, a cold sonnet agent driving a 4-gate toy spine through MCP tools took the minimal call path both times — 14 engine calls, zero malformed calls, zero engine refusals, zero interface-discovery calls. The same agent driving the same spine through the CLI reached done both times too, but took 24 and 27 engine calls, spent 4 and 7 calls reading `--help`, and took 2 engine refusals in each replicate. Both doors work; the CLI door costs roughly twice the calls, twice the wall-clock, and 1.5x the dollars to get to the same place.

The caveat: **this is not a property of MCP as a protocol.** Two of the four distinct CLI fumble types were prevented by sentences I wrote into the tool descriptions. What MCP actually supplies is three mechanisms — argument validation before the call reaches the engine, a place to put per-verb teaching that the harness delivers exactly when that verb is in play, and config-time binding of ambient arguments the agent can then never forget. A CLI door with equally good `--help` text and no ambient arguments would close part of the gap. It could not close the ambient-binding part, and it could not deliver the teaching only-when-relevant.

## The two-arm tracer

**Setup.** A zero-dependency stdio JSON-RPC server (`proto/mcp_spine_server.py`, 308 lines) wrapping the existing engine: every tool builds an argv and calls `checklist_engine.main(argv)`, capturing stdout/stderr and the exit code. No engine logic was rewritten, so the doctrine rails, refusal composition with recovery hints, the journal sidecar, lease enforcement and the Trip advisory all come through untouched. No MCP SDK was installed — `mcp` is still absent from the environment.

Both arms were cold headless `claude -p` sessions on sonnet, launched with `--strict-mcp-config`, `--setting-sources ""` and an identical built-in toolset (`Read,Write,Bash,Glob,Grep`). Both received an identical task core; they differed only in one closing sentence. Arm 1 got "Use the available spine tools." Arm 2 got the engine invocation string plus "Pass `--session-id cli-arm` on every verb that changes state."

Two methodological guards were necessary and both held. The repo's `.claude/settings.json` carries a `Bash` PostToolUse hook that pushes spine-rail text — that fires only for the CLI arm and would have handed it free coaching, so all setting sources were disabled; the transcripts confirm zero hook firings in every run. And the CLI arm was pointed at a transparent logging pass-through (`proto/engine_cli.py`) with an identical surface and exit code, so both arms' engine calls are counted from the same kind of log rather than scraped out of a model transcript.

**Counts.**

| metric | MCP r1 | MCP r2 | CLI r1 | CLI r2 |
|---|---|---|---|---|
| prompt words supplied | 59 | 59 | 74 | 74 |
| total engine calls | 14 | 14 | 27 | 24 |
| malformed calls (argparse rejected) | 0 | 0 | 2 | 0 |
| engine refusals | 0 | 0 | 2 | 2 |
| `--help` discovery calls | 0 | 0 | 4 | 7 |
| status polls | 1 | 1 | 7 | 3 |
| agent tool calls (all tools) | 20 | 19 | 32 | 23 |
| errored tool results | 0 | 0 | 4 | 1 |
| turns | 21 | 20 | 33 | 24 |
| wall clock (s) | 51 | 42 | 110 | 71 |
| cost (USD) | 0.35 | 0.25 | 0.53 | 0.35 |
| reached done | yes | yes | yes | yes |

The minimal path for this spine is 13 calls. The MCP arm took 14 both times (minimal plus one status read) and never varied. The CLI arm took 24–27.

**The CLI fumbles, by class.** Four distinct types, and which mechanism would have caught each:

1. `current --session-id cli-arm` — argparse rejected it; `current` takes no session flag. This is live orchestrator fumble #3 reproduced by a cold agent with no prompting. *Caught by schema validation.*
2. `status` — an invented verb that does not exist. *Caught by schema validation* (the tool list has no such name).
3. `attest g1 --cond c1` on a machine-checked condition — engine refused. Happened in **both** CLI replicates and **neither** MCP replicate. *Caught by tool-description text*, not by structure: the `spine_attest` description says "Conditions that ARE machine-checked are verified by the engine when you advance — do not attest those, just make them true."
4. `record g1 --result pass` on a gated spine — a survey verb on the wrong spine type. *Caught by tool-description text* (`spine_survey_result` says "Survey spines only").

A fifth difference is structural rather than a fumble. CLI r1 never claimed the lease before starting work — the engine's backward-compat gate allows mutations while no lease exists — then hit a refusal on `release` at the end and needed a four-call claim-then-release recovery. The MCP arm claimed first both times because the `spine_lease` description says to. This also produced a real measurement defect worth flagging separately: because the engine's `refusals` counter is armed by `claim`, CLI r1 finished a run with 2 real refusals and a recorded `refusals: 0`, while CLI r2 claimed earlier and recorded `refusals: 2`. The counter's arming dependence is documented in `docs/CHECKLIST_SCHEMA.md`, but this is the first run I know of where it silently under-reported a real run to zero.

**Ambient binding was neutralized, deliberately.** The engine runs `command`-kind checks through `subprocess.run([shell, "-c", command])` with **no `cwd`** (`scripts/checklist_engine.py:731`), so a relative path in a check passes or fails depending on where the caller's shell happens to be — live orchestrator fumble #4. Left in, that would have swamped the comparison in the CLI arm's favour-against, so the toy spine bakes absolute paths into its checks. The finding stands on its own: an MCP server has a fixed process working directory, so this class of drift disappears at the door; the CLI door will keep producing it until the engine passes `cwd` explicitly.

## What was tested AND what was NOT tested

**Tested.** A live MCP round trip, end to end: the server registered in a cold headless session and its seven tools were listed and called by a real model, with no session restart required. The server also drives the toy spine to done under a raw JSON-RPC driver with no model in the loop (`proto/drive_via_mcp.py`, prints `SELFTEST: PASS`), which pins any later failure to the harness rather than the server. Two replicates per arm. Subagent MCP tool inheritance, tested directly. The context-gauge advisory riding a tool result, demonstrated with a synthetic reading rather than argued.

**NOT tested.**
- **The registration risk the handoff flagged never materialized, but only because I routed around it.** `claude -p --mcp-config --strict-mcp-config` picks up a new server immediately. Whether an *interactive* Claude Code session picks up a newly written project `.mcp.json` without a restart was **not** tested.
- n = 2 per arm, one model (sonnet), one harness. No statistics — this is a tracer, not an experiment.
- A toy 4-gate spine, not a real role spine. The Commander spine has 10 tasks, child-checklist delegation, `git-change-policy` checks and a rework path; none of that was exercised.
- Untouched engine surface: `block`/`resume`, survey spines (`record`/`consolidate`), `reopen`/rework, `waive`, `attach` and evidence payloads, `amend`, `heartbeat`, `skip`, `flag-candidate`. The tool surface covers some of these; the tracer exercised none.
- Concurrency: one agent, one server, one spine. Two agents against one server was not tested.
- Real-run token cost of the schemas over a long session.
- **Author bias was not controlled.** I wrote both the tool descriptions and the CLI arm's prompt. Fumbles 3 and 4 were prevented by my prose, not by MCP.

**Next variant, and it is the one that matters.** Re-run arm 1 with deliberately bare tool descriptions — names and parameter types only, no per-verb guidance — against the same CLI control. That separates "MCP structure" from "good descriptions I happened to write," and it is the single cheapest thing that would make this result load-bearing rather than suggestive. Budget: one arm, ~$0.30.

## The seam: what a production MCP door looks like

**One core, two doors.** The prototype is already the shape: the MCP server builds an argv and calls the engine's own `main()`. Nothing was duplicated, and the rails, refusals, recovery hints and journal all rode through unchanged. A production version should call `dispatch()` directly rather than `main()` to avoid the stdout capture dance, but that is a refinement, not a redesign. **The CLI must stay** — the `Bash` PostToolUse spine-rail hook, cron/headless runs, and any non-MCP harness all reach the engine through it, and none of them can speak MCP.

**Tool surface: seven tools over eighteen verbs.** `spine_status` (current), `spine_lease` (claim | release), `spine_start`, `spine_attest`, `spine_advance`, `spine_halt` (block | resume), `spine_survey_result` (record | consolidate). Paired state-toggle verbs merge behind an `action` enum; the rest map one to one. Uncovered verbs — `heartbeat`, `skip`, `reopen`, `waive`, `attach`, `amend`, `flag-candidate` — are deliberately absent from the prototype and would need either tools or a documented CLI fallback.

**Schema cost: 3,997 bytes of tool JSON, roughly 1,000 tokens,** delivered by the harness on every turn. Set that against what it displaces, which is where the handoff's premise needs correcting. I measured it: the always-loaded `SKILL.md` files carry only **1–2 lines each** of engine-calling teaching, not "a large share." The real concentration is `skills/workbench/references/checklist-engine.md` at 18,012 characters (~4,500 tokens, loaded on demand) and the invocation strings embedded in spine-template imperatives — 7 of 21 template tasks, 10,298 characters. So the honest trade is: ~1,000 always-loaded schema tokens in exchange for stripping invocation strings out of imperatives and shrinking the on-demand reference. That is a real win but a narrower one than "MCP deletes the teaching prose."

**The per-gate imperative rides tool results unchanged.** `spine_status` returns the engine's rendered `current` output verbatim — the RAIL banner, the ACTIVE gate, the imperative, the per-condition met/unmet list, `next:`. Refusals come back as `isError: true` with the engine's own `REFUSED: ... ` line and its composed recovery hint, so the model sees a failed tool call rather than prose it has to parse. This matters more than it sounds: it means the spine templates remain the single source of the imperative and the MCP door adds no second rendering path.

**What breaks or needs care.**

- **Lease identity is the serious one.** Subagents inherit the parent's MCP tools automatically — tested and confirmed: a spawned sonnet subagent listed all seven `mcp__spine__*` tools and called `spine_status` successfully with no extra wiring. But it inherits the *same server process*, therefore the same env-bound `SPINE_SESSION` and the same bound spine file. A Commander and its implementer subagent would both present as one session id, and the engine's actor-authority lease — which exists precisely to refuse two controlling agents in one worktree — could no longer tell them apart. The CLI door does not have this problem because each agent passes its own `--session-id`. A production door must either take `session_id` as a tool argument (giving back the fumble it was meant to remove) or derive caller identity some other way. **This is a regression risk, not a nitpick.**
- **Ambient binding is the door's biggest ergonomic win and its biggest coupling.** Binding `--file` and `--session-id` at server-config time is what removes the path-drift and forgotten-session fumble classes outright. It also means one server instance serves exactly one spine, so a harness driving several spines needs several server entries or a spine argument.
- **Headless and cron runs have no MCP client.** They keep the CLI. Anything that must work in both places has to stay expressible through the CLI door.
- **The spine path should not appear in the agent's prompt.** Both MCP replicates read `spine.json` directly (via `Read` or `cat`) instead of polling `spine_status`, because the prompt handed them the path. With the file bound only inside the server, every read goes through the rendered channel and the rail stays canonical.

## The governor note, scoped

**Can the server push a gauge reading inside its tool responses? Yes — and it already does, with no new code.** `spine_status` wraps `current`, and `dispatch()` appends `_trip_advisory()` to `current`'s output, so the reading rides the tool result for free. Demonstrated with a synthetic gauge sidecar: a reading of `fill_fraction: 0.11` on `claude-sonnet-5` came back inside the `spine_status` tool result as

> `CONTEXT 11% (>= soft): you've used most of your context. Unless you're basically done, hand off here at g1 rather than pushing through (advisory — decline with a reason if you're nearly done).`

The HARD backstop rides `advance` the same way and needs no MCP-specific work either. This is consistent with the standing doctrine that the reading is pushed by the engine on tool use, never pulled by the agent — the MCP door changes the transport, not the direction.

**The identity question it inherits, named and not solved.** The gauge sidecar is written by a hook that must bind a session to a spine, and the engine already has a `CONTEXT GAUGE SILENT: ambiguous-binding` path for when it cannot. An MCP server makes that binding harder in exactly the way the lease problem above describes: the server is one process, config-bound to one session id, shared by the parent agent and every subagent that inherits its tools. So a subagent calling `spine_status` would be handed **the parent's** context reading as if it were its own — a plausible wrong number, which is the one thing this gauge must never produce. Whether the answer is per-agent server instances, a caller-identity argument, or leaving the gauge on the CLI door is a design decision this prototype does not make.

## What it taught beyond the question

- **The engine runs `command` checks with no `cwd`** (`scripts/checklist_engine.py:731`). Relative-path checks are therefore caller-location-dependent. This is a real defect in the engine, independent of any door, and it is cheap to fix.
- **The `refusals` counter can silently report zero for a run that took refusals**, when the lease is claimed after the refusals happen. Observed directly: CLI r1 took 2 refusals and recorded 0. The arming behaviour is documented; the failure mode reaching zero on a real run may not be.
- **The premise about always-loaded prose was wrong** and the measurement is above. Worth correcting wherever it is being carried forward.
- **A cold agent reproduced a live orchestrator fumble unprompted** (`--session-id` on `current`). That is decent evidence the fumbles are interface-shaped rather than attention-shaped.
- **`claude -p --mcp-config --strict-mcp-config --setting-sources ""` is a clean cold-arm rig** for this kind of tracer: real MCP, real model, no restart, no user config, hooks suppressed, and a `stream-json` transcript that scores objectively. Reusable for future excursions.

## Surviving pure module

None absorbed. `proto/mcp_spine_server.py` is a working reference for the seam and would be the starting point for a production door, but it is prototype code and should be rewritten against `dispatch()` rather than lifted.

## Disposition

`captured-to-worktree`

**Detail:** Worktree `C:/Programs/.proto-exc9-mcp-front-door`, branch `proto/exc9-mcp-front-door`, commit `de6a084`. Kept because it is the concrete referent for a design decision the human has not yet ruled on, and because the named next variant (bare tool descriptions) reruns directly against it. Owning pointer: excursion `exc-9-mcp-front-door` in `explore-post-phase1`. To be re-affirmed or disposed at epic close. Run outputs under `runs/` are gitignored.

**Containment verified at closeout:** main checkout `git status` unchanged from session start; `C:/Users/fredc/.claude/settings.json` untouched (mtime Jul 31); no `.mcp.json` anywhere in the main checkout; no pip install performed (`mcp` still absent); no hooks wired.

## One command to run

Server self-check, no model and no cost:

```
python C:/Programs/.proto-exc9-mcp-front-door/proto/make_toy_spine.py C:/Programs/.proto-exc9-mcp-front-door/runs/selftest && python C:/Programs/.proto-exc9-mcp-front-door/proto/drive_via_mcp.py C:/Programs/.proto-exc9-mcp-front-door/runs/selftest
```

Full tracer (spends money): `python proto/run_arm.py mcp <name>` / `python proto/run_arm.py cli <name>`, then `python proto/score.py`.
