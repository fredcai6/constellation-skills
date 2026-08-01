# x2 evidence — do project-local hooks fire for subagents and headless runs?

**Excursion:** explore-138 / x2. **Date:** 2026-07-12. **Harness:** Claude Code CLI `2.1.206`, Windows 11, node `v24.15.0`.
**Method:** official docs (cited) + live probes in an out-of-repo scratch dir (`%TEMP%\hookprobe`, never touched the constellation repo). Probe logs pasted below.

## Bottom line

1. **Yes — project-local `.claude/settings.json` hooks fire for headless `claude -p` runs.** Live-confirmed: `SessionStart` (source `startup`), `UserPromptSubmit`, `PreToolUse`, `Stop`, `SessionEnd` all fired in a plain `claude -p` invocation.
2. **Yes — they fire for Agent/Task-tool subagents.** A dispatched subagent produces `SubagentStart` → the subagent's own tool calls fire `PreToolUse` (tagged with `agent_id`/`agent_type`) → `SubagentStop`. The subagent shares the **parent `session_id`** and gets **no separate `SessionStart`**; its `Stop` is delivered to the parent as `SubagentStop`.
3. **`Stop` can block a stop and force the agent to act** on a `reason`, live-confirmed even in headless `-p`. `stop_hook_active:true` is the re-entry loop guard.
4. **`SessionStart` distinguishes `source: "compact"`** and **`PreCompact` distinguishes `manual` vs `auto`** — per docs; NOT probed live (see NOT-tested).

## Matrix: hook event × invocation mode

| Hook event | Fires in headless `claude -p`? | Fires for Agent/Task subagent? | Can block? | Key payload fields |
|---|---|---|---|---|
| `SessionStart` | **Yes, live** (`source:"startup"`) | **No** — subagent inherits parent session, no own SessionStart (live) | No | `source` (`startup`/`resume`/`clear`/`compact`), `session_id`, `transcript_path`, `cwd`; can inject `additionalContext` |
| `UserPromptSubmit` | **Yes, live** | n/a (no user prompt inside a subagent) | Yes (exit 2 / `decision:"block"`) | `prompt`, `prompt_id`, `permission_mode`, `transcript_path` |
| `PreToolUse` | **Yes, live** (fires when a tool is used) | **Yes, live** — subagent's tool calls fire it, tagged `agent_id`+`agent_type` | Yes (`permissionDecision:"deny"`) | `tool_name`, `tool_input`, `tool_use_id`; subagent variant adds `agent_id`, `agent_type` |
| `SubagentStart` | n/a | **Yes, live** | No (informational) | `agent_type`, `agent_id`, `session_id` (= parent's), `transcript_path` |
| `SubagentStop` | n/a | **Yes, live** | Yes (exit 2 / `decision:"block"`) | `agent_type`, `agent_id`, `agent_transcript_path` (separate from parent), `last_assistant_message`, `stop_hook_active` |
| `Stop` | **Yes, live** (parent turn) | Parent's Stop only; subagent Stop is converted to `SubagentStop` (docs) | **Yes, live** (`decision:"block"`+`reason`; agent acts on reason) | `last_assistant_message`, `stop_hook_active`, `transcript_path`, `session_id` |
| `SessionEnd` | **Yes, live** | n/a | No | `reason`, `session_id` |
| `PreCompact` | Not probed | Not probed | Yes (exit 2 / `decision:"block"`) per docs | matcher `manual`\|`auto` distinguishes trigger |
| `PostCompact` | Not probed | Not probed | No (docs) | matcher `manual`\|`auto` |

## The three named sub-questions

**Q: Does `SessionStart` distinguish `source: compact`?** **Yes (docs).** `source` field takes `startup`, `resume`, `clear`, `compact`; `compact` = fired after a compaction. Live probe observed only `startup` (headless cold start). `compact`/`resume` NOT probed live. `SessionStart` cannot block but can inject `additionalContext` (and set `sessionTitle`, `watchPaths`, `reloadSkills`).
Source: <https://code.claude.com/docs/en/hooks> SessionStart section.

**Q: Can `Stop` refuse a stop and return a reason the agent must act on?** **Yes — live-confirmed.** Hook returned `{"decision":"block","reason":"...append PINEAPPLE..."}`; the agent, which had output "APPLE", continued and appended "PINEAPPLE" before stopping. Second Stop fired with `stop_hook_active:true` (guard against infinite loops — check it and exit 0 to allow the stop). Works in headless `-p`. Docs also note `Stop` can pass `hookSpecificOutput.additionalContext` to continue the conversation non-punitively.

**Q: Does `PreCompact` distinguish manual vs auto?** **Yes (docs).** Matcher values `manual` (user `/compact`) vs `auto` (auto-triggered at context limit). `PreCompact` can block via exit 2 / `decision:"block"`. NOT probed live.

## Probe logs (pasted)

**Probe A — headless `claude -p "say hi in exactly 3 words"`** (plain, no bypass flag), `hooks.log`:
```
{"tag":"SessionStart","source":"startup","session_id":"9bc81440","keys":[session_id,transcript_path,cwd,hook_event_name,source]}
{"tag":"UserPromptSubmit","session_id":"9bc81440","keys":[...,prompt_id,permission_mode,hook_event_name,prompt]}
{"tag":"Stop","session_id":"9bc81440","keys":[...,effort,hook_event_name,stop_hook_active,last_assistant_message,background_tasks,session_crons]}
{"tag":"SessionEnd","session_id":"9bc81440","keys":[...,hook_event_name,reason]}
```
(`PreToolUse` absent — the answer used no tool. Exit 0, output "Hi there, Fred!".)

**Probe B — headless `claude -p` that dispatches one general-purpose subagent via Task tool**, `hooks.log` (single shared session `f29c126a`):
```
SessionStart   source:startup   (parent only — no second SessionStart for subagent)
UserPromptSubmit
PreToolUse     tool=Task        (parent, no agent_type)
SubagentStart  agent_type:general-purpose  agent_id:acd251b29a3d566e0
PreToolUse     agent_type:general-purpose  agent_id:acd251b29a3d566e0   (subagent's Bash call)
SubagentStop   agent_type:general-purpose  agent_id:acd251b29a3d566e0   keys include agent_transcript_path,last_assistant_message
Stop           (parent, no agent_type)
SessionEnd
```
Interpretation: subagent tool calls DO trigger project hooks, distinguishable from parent calls only by presence of `agent_id`/`agent_type`. Subagent has its own `agent_transcript_path`.

**Probe C — Stop blocking**, `claude -p "Reply with only the word APPLE."`, hook returns `decision:block` unless `stop_hook_active`, `stop.log`:
```
{"stop_hook_active":false,"last":"APPLE"}      <- first stop, hook blocked with reason
{"stop_hook_active":true,"last":"PINEAPPLE"}   <- re-entry; hook let it stop
```
Final model output: `PINEAPPLE` (the injected instruction was obeyed).

## NOT tested live (cited to docs only)

- `SessionStart` with `source` = `compact` / `resume` / `clear` (only `startup` observed).
- `PreCompact` / `PostCompact` firing and `manual`/`auto` matcher (docs only).
- `SubagentStop` **blocking** a subagent (fired, but `decision:block` not exercised).
- `PreToolUse` **deny** path (fired, but not exercised to deny).
- `--permission-mode bypassPermissions` headless run — blocked by the auto-mode classifier ("Create Unsafe Agents"), so not tested; unrelated to hook firing.

## Gotcha for hook authors on this Windows setup

Hook `command` strings run under a shell where **MSYS converts `/tmp/...` path _arguments_ to Windows paths**, but a `/tmp/...` path **hardcoded inside a script literal is NOT converted** — node resolves it to `C:\tmp\...`. My first Stop probe silently mis-fired for this reason (wrote to `C:\tmp`, crashed before emitting its decision). Pass log/output paths as shell args, or use `%TEMP%`-style Windows paths, inside hooks.

Source docs: <https://code.claude.com/docs/en/hooks> (301 from docs.anthropic.com/en/docs/claude-code/hooks).
