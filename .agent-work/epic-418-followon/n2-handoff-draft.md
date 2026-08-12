# Implementer handoff — N2: withhold the engine CLI from the crew grant (#559)

**Work id:** `epic-418-followon/n2-engine-withheld`
**Gate:** `g1-implement` · **Role:** implementer · **Model:** Sonnet
**Worktree:** to be provisioned off `main` after N1 merges
**Your spine:** `.agent-work/epic-418-followon/n2-engine-withheld/IMPLEMENTER_PLAN.json`

## Task

Make `scripts/run_crew.py` dispatch a crew that **can reach the MCP door and cannot reach the engine
CLI**. One property, stated as a property: after this change, a crew that tries to run
`checklist_engine.py` is refused.

## Intent — why this is the load-bearing change of the wave

The human ruled: *"agree, enforce mechanically."* The evidence for that ruling is now direct, and it
is the strongest measurement this epic has produced.

N1's crew — dispatched to build the door's verb closure — made **zero door calls** and hand-typed
the lease `implementer-n1-verb-closure-1786418243`, while:

- its own process environment (read live from `/proc/<pid>/environ`) carried
  `SPINE_FILE` pointed at its own plan and
  `SPINE_SESSION=constellation/epic-418-followon/n1-verb-closure/g1-implement/implementer`;
- a control probe in a fresh worktree off the same commit, with byte-identical `.mcp.json`,
  `settings.json` and `settings.local.json`, answered **DOOR PRESENT**;
- its handoff named the `mcp__spine__*` tools explicitly and quoted the ruling.

A correctly bound, available, explicitly-instructed door was ignored. **Instruction plus
availability is not enough.** That is why this issue exists and why it matters more than the corpus
rewrite that follows it.

## The trap this change exists to avoid

Omitting the engine from the allow-list does **not** withhold it. `CREW_ALLOWED_TOOLS` grants
unrestricted `Bash`, and `Bash` reaches `checklist_engine.py` whatever the MCP allow-list says. The
M2 cold reviewer found this independently. Do not "fix" this by shortening the tool list.

## What has already been probed — reproduce it, do not trust it

The Admiral ran two arms in one worktree with the same prompt (*run `py
scripts/checklist_engine.py --help`*):

| arm | flags | result |
|---|---|---|
| A | none | ran it; returned `usage: checklist_engine.py [-h] --file FILE [--dry-run]` |
| B | `--disallowedTools "Bash(*checklist_engine.py*)"` | refused; the agent asked for approval instead |

So `--disallowedTools` exists, takes `Bash(...)` patterns, and the mechanism works. **That is the
Admiral's probe, not your evidence.** Run your own control — a claim you did not personally
reproduce is exactly what this epic keeps catching.

**One observation worth designing against:** the refused agent immediately proposed re-spelling the
command (`python3 …` instead of `py …`). The same pattern catches that, because it keys on the
script name rather than the interpreter. Key on the thing that cannot be re-spelled. The human's
standing ruling applies — *"we don't have to make it foolproof, just keep out the easy failures for
now"* — so do not build a sandbox; make the obvious route refuse.

## Scope

**In:** `scripts/run_crew.py` and its tests.

**Out — hard no-gos:**
- A crew must still be able to do ordinary engineering work. If your deny rule blocks unrelated
  Bash, that is a defect, not caution — show what still works.
- Do **not** use `--dangerously-skip-permissions` or `bypassPermissions` anywhere.
- Do **not** modify `checklist_engine.py` or `mcp_spine_server.py`.
- Do **not** touch `settings.json` or `docs/agents/*`.
- **No merge or push to `main`.**

## Required evidence

- **A red control:** a crew dispatched through `run_crew.py` reaches the engine today. Show the
  command and its real output.
- The same recipe refused after the change.
- **Show the refusal is legible.** A crew that hits this should be able to tell it was refused on
  purpose and file a finding, rather than concluding the spine is broken. Say what the crew sees.
- **Show ordinary work still works** — a crew can still run the test suite, git, grep, and the
  project's other scripts. The verifiers, `run_crew.py` itself and the episode tools stay reachable
  by the human's explicit ruling: the no-CLI rule covers the spine, not every auxiliary script.
- Tests that fail without the change.
- Full suite with real counts:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  Use `python`, not `python3`.

## Drive your spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` automatically, and after N1 the door covers
every engine verb — so there is nothing you need the CLI for. Use `mcp__spine__*`, found via
`ToolSearch`.

**You are the first crew that will be dispatched under your own change.** If you find yourself
reaching for the engine and refused, that is the feature working; record what you were trying to do
and whether the door had a path for it. If the door did **not** have a path, that is a defect in N1
and it is the most valuable thing you could return.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **Honest null:** a measured negative is a complete, successful deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here.

## Deliverable

`.agent-work/epic-418-followon/n2-engine-withheld/IMPLEMENTER_RESULT.md`, from the implementer
skill's template, including its **Workflow Feedback** section. Write it before ending your turn.
