# Implementer handoff — N3: remove the CLI from agent-facing instruction and name the MCP server (#559)

**Work id:** `epic-418-followon/n3-corpus-rewrite`
**Gate:** `g1-implement` · **Role:** implementer · **Model:** Sonnet
**Worktree:** to be provisioned off `main` after N1 merges
**Your spine:** `.agent-work/epic-418-followon/n3-corpus-rewrite/IMPLEMENTER_PLAN.json`

## Task

Stop the skill corpus from telling agents about the engine CLI, and start it naming the MCP server
the agents are supposed to use instead.

## Intent

The human's ruling: *"anything that we want to do for the spine needs to be accessible via mcp. the
agents should not know about the cli. period."* And on the undefined token: *"engine is the cli into
the spine (or was at some point). we should absolutely clarify and give the specific mcp server
name."*

N1 closed the verb gap, so removing the CLI no longer strands an agent mid-run. That ordering was
deliberate — do not reopen it.

## The measured surface

- **19 mentions of `checklist_engine` across 13 files** in `skills/` and `docs/agents/`.
- **9 occurrences of the `<engine>` token across 5 files.**

**`<engine>` needs deleting, not defining.** Every one of the 9 sits inside a "CLI fallback:" clause
that the templates already treat as secondary — they read *"by default call the `spine_lease` MCP
tool … CLI fallback: `<engine>` claim --session-id …"*. Remove the fallback clause and the undefined
token goes with it. That token being undefined for this long, and the previous Admiral reading it as
the CLI without noticing it was a choice, is the drift this whole epic exists to correct.

## What replaces it

Name the server, not just the tool. The tools are `mcp__spine__*`, and **the `spine` prefix comes
from the server's key in `.mcp.json`, not from the server itself** — if a project registers it under
a different key, the prefix changes. Say that plainly once, in shared doctrine, rather than leaving
a reader to infer it. An agent that knows to look for `mcp__spine__*` can find the tools with
`ToolSearch`; that is how the one successful arm in wave 2 found them, without any role instruction.

## Scope

**In:** `skills/` and its templates.

**Edit the canonical source.** `skills/_shared/global-*.md` is canonical; `skills/<role>/references/
global-*.md` is an **install-time copy that `install_constellation.py` regenerates**, so an edit
there is silently overwritten on the next install. Check which you are touching before you type.

**Out — hard no-gos:**
- **`docs/agents/CREW_CONTEXT.md` is the human's call. Leave it alone** — it carries 2 of the 19
  mentions. Report them; do not edit them.
- Do **not** modify `checklist_engine.py`, `mcp_spine_server.py`, or `run_crew.py`.
- Do **not** remove the CLI itself. It stays as the implementation behind the door. This is about
  what agents are *told*, not about deleting a program. Non-agent readers — the human, the
  verifiers, the launcher — still use it.
- **No merge or push to `main`.**

## Required evidence

- A before/after count: `grep -rn 'checklist_engine' skills/` and `grep -rn '<engine>' skills/
  templates/` reduced to what remains, with each remaining mention justified as non-agent-facing.
- **Drive a real role spine end to end from the rewritten text, using only the door, and reach
  DONE.** A corpus that reads well and cannot be driven is the failure mode here. This is the
  acceptance evidence; a grep count alone is not.
- Full suite with real counts. Several tests check corpus structure and shipped-template shape, so
  expect them to have opinions:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
- If a template is compact-format JSON, **edit the raw text surgically** — never round-trip it
  through `json.load`/`json.dump`, which reflows the whole file and destroys blame — then
  re-validate with `json.load`.

## A caution specific to this task

You are rewriting instructions that agents load. It is easy to produce text that is *cleaner* and
*less usable*: the fallback clauses currently carry real information about argument shapes
(`--session-id` on every mutating CLI call, which the door tools never take). When you delete a
clause, check whether it was the only place something true was written down, and if so, say the true
thing in the door's terms rather than dropping it.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **Honest null:** a measured negative is a complete, successful deliverable.
- **Cold review:** an independent reviewer will check this, and will re-drive a spine from your text.
- **Stage by name.** `.agent-work/` is tracked here.

## Deliverable

`.agent-work/epic-418-followon/n3-corpus-rewrite/IMPLEMENTER_RESULT.md`, from the implementer
skill's template, including its **Workflow Feedback** section. Write it before ending your turn.
