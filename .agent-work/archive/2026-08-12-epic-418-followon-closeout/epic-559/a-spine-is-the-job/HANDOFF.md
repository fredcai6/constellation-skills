# Implementer handoff — A: make the spine the job, not a document beside it

**Work id:** `epic-559/a-spine-is-the-job` · **Gate:** `g1-implement` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job` (branch `epic-559/a-spine-is-the-job`, off `main`@`9d593e0a`)
**Your spine:** `.agent-work/epic-559/a-spine-is-the-job/IMPLEMENTER_PLAN.json` — drive it gate by gate.

## Task

A dispatched crew is told to read a handoff document. Make it read its spine instead.

Four changes, all in three files.

1. **`scripts/run_crew.py::build_crew_argv`** — the crew's whole prompt is currently:
   *"You are the constellation {role} crew for session {session}. Read the handoff at {handoff} and
   execute it exactly. The run is only complete when the result artifact the handoff names exists."*
   It never mentions the spine. Add a branch: when a spine is given and no handoff is, the prompt
   names no document at all and tells the crew to call `mcp__spine__spine_status` first, then drive
   gate by gate until the spine reports done. Keep the existing handoff branch byte-identical so
   every current dispatch and every current test still passes.
2. **`--handoff` becomes optional**, with a refusal when neither `--spine` nor `--handoff` is given.
   `_require_handoff` runs only when a handoff was supplied. `CrewSpec.handoff` becomes nullable and
   the registry records `null`. The `external` backend keeps requiring a handoff — it cannot bind a
   spine, so a spine-only dispatch there would leave the crew with no job at all. Refuse that
   combination explicitly rather than letting it through.
3. **`skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md`** — both currently tell a
   dispatched crew it does not own the bound spine and should *"drive your own plan through the CLI
   fallback instead"*. That instruction is why crews use the CLI. Replace it: your spine is bound
   for you, `spine_status` is your first call, do not author a plan of your own. Do not mention the
   engine CLI to a crew at all.
4. **A crew may no longer waive its own check.** The human's ruling, verbatim:
   *"agent cannot waive itself. I'll allow commander to waive crew, admiral to waive commander,
   human for admiral. always ask up."*
   The narrow part of that ruling in your scope: remove the crew's ability to waive its own bound
   spine. Today `CREW_ALLOWED_TOOLS` grants `mcp__spine__spine_evidence`, whose `waive` action goes
   straight through, and the engine accepts any non-empty `--authority` string — so a crew whose
   change broke the suite can close its own failing gate with `authority: "human"`.
   You may not simply drop `spine_evidence` from the grant: `attest` and `attach` are in the same
   tool and a crew needs both. Solve it so `waive` is unreachable for a crew while `attest` and
   `attach` still work. **A crew that hits a check it cannot satisfy must block and return** — that
   is the "always ask up" half of the ruling, and the blocked path already exists (`spine_halt`).
   Make sure the refusal tells the crew that, rather than leaving it stuck.

## Also fix the coupling that caused a real failure yesterday

`CREW_ALLOWED_TOOLS` is a hand-typed list of tool names mirroring `mcp_spine_server.TOOLS`. It froze
at seven while the door grew to nine, so two tools were denied to every crew with only a generic
permission message — a reviewer hit it four times and fell back to the CLI, and it read as the agent
preferring the CLI. **Derive the `mcp__spine__*` entries from the door's own tool list instead of
restating them.** The non-MCP entries (`Bash`, `Read`, …) stay as they are.

If deriving it means importing `mcp_spine_server` at module scope and that turns out to be
awkward — it reads `SPINE_FILE` and `SPINE_ENGINE` from the environment at import — say so in your
result and do the smallest honest thing instead, e.g. a test that fails when the two lists diverge.
A test that ties them is acceptable; a second hand-typed copy is not.

## Intent

The spine already carries everything needed to instruct a crew: the engine shows one gate at a time,
with its imperative, its unmet conditions, its constraints and its legal next verbs. Nothing had to
be built for the spine to be the job. The only reason it is ignorable is that the launcher hands the
crew a document and says that document is the job.

This is the first step of a larger direction (#535): the request lives in the spine, dispatch becomes
"start the spine with this identifier", and spine creation gets mechanized so no agent hand-writes
JSON. You are not doing that part. You are removing the competing document.

## Scope

**In:** `scripts/run_crew.py`, `skills/implementer/SKILL.md`, `skills/reviewer/SKILL.md`, and tests.

**Out — hard no-gos:**
- Do **not** modify `checklist_engine.py` or `mcp_spine_server.py`.
- Do **not** touch `settings.json` or `docs/agents/*`.
- Do **not** delete `IMPLEMENTER_HANDOFF.template.md` or the other handoff templates. The
  `external` backend still needs them.
- Do **not** change spine templates — another crew owns those this wave. If you find something that
  belongs there, write it in your result.
- **No merge or push to `main`.** Local commits on your branch.

## Required evidence

- **A control first:** show that today's dispatch tells the crew to read a document and never names
  the spine. `build_crew_argv` is pure — assert on the argv it returns, no subprocess needed.
- The new branch produces a prompt naming no file path and naming `spine_status`.
- The old branch is byte-identical to today's, proven by an assertion, so existing dispatches are
  untouched.
- A crew grant that no longer permits waive, with `attest` and `attach` shown still working.
- The two lists (crew grant vs door tools) shown to be tied — a test that goes red if one changes
  without the other.
- Tests that fail without your change.
- Full suite with real counts:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  Use `python`, not `python3`.

## Drive your own spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` for you. Use the `mcp__spine__*` tools, found
via `ToolSearch`. The door now covers all 18 engine verbs, so there is nothing you need the CLI for.
If you reach for the CLI, say so in your result and say what made it the natural move — that is
useful evidence about the very thing you are fixing, and it is not a mark against you.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **The goal is a weaker agent than you.** The human's intent: this must work with less capable
  agents, so prose instruction is a liability and anything that can sit behind a tool should.
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.

## Deliverable

`.agent-work/epic-559/a-spine-is-the-job/IMPLEMENTER_RESULT.md`, from the implementer skill's
template, including its **Workflow Feedback** section. Write it before ending your turn.
