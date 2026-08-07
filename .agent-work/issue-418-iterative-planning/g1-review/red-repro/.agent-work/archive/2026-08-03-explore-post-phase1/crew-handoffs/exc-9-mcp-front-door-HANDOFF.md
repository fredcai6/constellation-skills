# Excursion handoff: exc-9-mcp-front-door (PROTOTYPE_HANDOFF)

Full brief: `### EXCURSION_BRIEF exc-9-mcp-front-door` in `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/IDEAS_BOARD.md` — read it first. Load the **constellation-prototyper** skill (Skill tool) and drive its workflow with this handoff.

## Question
Does putting an MCP front door on the existing checklist engine let a cold agent drive a spine correctly with less teaching and fewer fumbles than the CLI door — and what does the production seam look like?

Background (why this is believed, not yet shown):
- Tommy's framing: "we may be working too hard for the checklist engine. this seems like exactly what MCP is for, and models are trained on MCP."
- Live evidence from the current orchestrator session: four CLI fumbles in one run (`attest` without `--cond`, `resume` without `--reason`, `--session-id` passed to `current` which does not take it, a relative `--file` path broken by shell working-directory drift). Each cost a round trip. Tool schemas would catch or prevent all four.
- A large share of always-loaded skill prose teaches engine calling conventions. MCP moves that teaching into tool schemas the harness delivers for free.

## Branch
logic

**Why this branch:** mechanism/interface behavior — how agents call the engine — no UI, no measurement apparatus beyond simple counts.

## Host-project conventions
- **Runtime / language:** Python 3.12
- **Task runner:** run tests as `python -m pytest` (NOT `py -m pytest` — #313)
- **Routing:** n/a
- **Other conventions:** the engine is `scripts/checklist_engine.py`; spines instantiate from `skills/<role>/templates/*_SPINE.template.json`; the engine's rendered output is the canonical channel agents read. The engine currently has a CLI door driven via shell.

## Location
worktree

**Driver:** agent-driven → throwaway worktree. Create it yourself off main; dispose per prototyper doctrine when done (or keep with a named reason).

## Stop conditions
- "Answered" requires all three of:
  1. **A live two-arm tracer:** build a minimal stdio MCP server that wraps the existing engine module (import it; do not rewrite engine logic) and exposes ~6 coarse tools covering the drive loop (suggested: current/status, claim+start, attest, advance, record+consolidate, block/resume — pick a sensible grouping and state it). Register it ONLY inside the worktree (project-scope `.mcp.json` in the worktree root). Author a small toy spine (3–4 gates with mixed attest/command conditions). Arm 1: ONE cold subagent (Agent tool, model sonnet or lower, worktree-scoped) prompted only "drive this spine to done using the available spine tools" — zero CLI teaching. Arm 2 (control): one cold subagent driving the SAME toy spine through the CLI with an equivalently minimal prompt plus only the invocation string. Count per arm: invalid/malformed calls, engine refusals, retries, total calls, and prompt words supplied. Report the counts side by side.
  2. **The seam description:** what a production MCP door looks like — one engine core with two doors (CLI stays for hooks and non-MCP harnesses); the tool list and schema shape; how the per-gate imperative and refusal text ride tool results; what breaks or needs care: headless/cron runs, subagent tool inheritance, lease/session identity, schema token cost in context.
  3. **The governor note, scoped:** state whether the server could push a context-gauge reading inside its tool responses, and name the identity question it inherits (which agent is calling) without solving it.
- Budget: ~3 variants on the tool shape if the first fails; report even if inconclusive; scoped nulls — state what was and was NOT tested (e.g. only one harness, n=1 per arm, toy spine not a real role spine).
- Exclusions: nothing lands on main; do NOT modify `C:/Users/fredc/.claude/settings.json` or any global/user-scope config; `.mcp.json` and any MCP SDK install (pip) live only in the throwaway worktree/venv; do not wire hooks.

## Return format
`PROTOTYPE_RESULT` written to `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/evidence/exc-9-mcp-front-door-RESULT.md` (main checkout path, not your worktree): the answer, the two-arm counts table, what was tested and NOT tested, the seam description, the governor note, what it taught, any surviving module, worktree disposition. Final return message: one verdict line + that path.
