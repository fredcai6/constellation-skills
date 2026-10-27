# Ideas Board — explore-local-pi

## The point

Explore a local Pi setup connecting Claude, Codex, and a local model; remote access through the existing Telegram bot or another interface; a skill other agents can use to operate Pi; and native Constellation integration. User requested research and discussion. Installation and a final design have not been requested yet.

## Current candidates

- Pi uses hosted models and a local inference endpoint directly.
- Pi delegates bounded tasks to existing Claude Code and Codex agents.
- A hybrid supports both paths with explicit model and agent selection.
- Existing journal-system Telegram bot gains an explicit Pi command or conversation mode.
- A separate Telegram bot fronts Pi, sharing a local session adapter with the agent-facing skill.

All candidates are proposals, not user decisions.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Pi documents skills, MCP, RPC, and custom model endpoints | Documentation read; no installation or runtime validation | https://pi.dev/docs/latest/skills ; https://pi.dev/docs/latest/mcp ; https://pi.dev/docs/latest/rpc ; https://pi.dev/docs/latest/models |
| Constellation needs Pi integration work | At source revision 3ac7a1ab: installer targets Claude, Codex, Cursor, Gemini; managed CLI crew launch builds Claude commands; hook wiring targets Claude. External dispatch exists. Pi runtime compatibility not tested | scripts/install_constellation.py; scripts/run_crew.py; docs/CONSTELLATION_OVERVIEW.md |
| Existing local pieces may be reusable | journal-system guide, Telegram architecture packet, main.py and compose inspected. Bot uses polling; local llama.cpp configured on 8005 behind a profile, alias local, default Qwen3.5-4B-Q4_K_M.gguf. Running state and tool-use ability not tested | /home/tommy/projects/journal-system/docs/agents/AGENT_GUIDE.md; docs/architecture/packets/telegram.md; services/telegram/app/main.py; infra/docker/docker-compose.yml |
| Pi and Ollama absent from this shell PATH | command lookup only; other installs not ruled out. Node, Claude, Codex found | Initial shell inspection |

## Open threads

- Confirm pi.dev is the intended project (user wrote py.dev).
- Pending user question: direct model access, existing agent delegation, or both?
- Pick exploration cycle flavor; compare seems useful once the intended capability is clear.
- Confirm whether the journal-system bot is the intended Telegram bot.
- What should a first real remote task accomplish, and how much autonomy should it have?
- Is the existing local model sufficient for intended work? Test actual tool use before choosing a role.
- Define agent-facing operations: start, status, steer, cancel, resume, collect result are possible candidates.
- Distinguish skill discovery, checklist/MCP integration, crew lifecycle, and harness event hooks when defining native integration.

## Rejected ideas (with reasons)

None.

## Cycle log

No cycle consolidated. Initial context gathered; awaiting user direction.
