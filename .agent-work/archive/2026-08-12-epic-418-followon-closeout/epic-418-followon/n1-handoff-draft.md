# Implementer handoff — N1: close the verb gap so the door covers every spine action (#559)

**Work id:** `epic-418-followon/n1-verb-closure`
**Gate:** `g1-implement` · **Role:** implementer · **Model:** Sonnet
**Worktree:** to be provisioned off `main` after M2 merges
**Your spine:** `.agent-work/epic-418-followon/n1-verb-closure/IMPLEMENTER_PLAN.json`

## Task

Give the MCP door a tool path for the five engine verbs it does not cover: **`skip`, `reopen`,
`append`, `amend`, `flag-candidate`.** After this change, every one of the engine's 18 verbs is
reachable through `mcp__spine__*`.

## Intent — the rule that makes this a defect rather than a gap

The human's ruling, verbatim:

> anything that we want to do for the spine needs to be accessible via mcp. the agents should not
> know about the cli. period. anything that we can only do via the cli is a defect.

`scripts/mcp_spine_server.py`'s own docstring records the decision this overturns:

> `skip`, `amend`, `append`, `reopen` and `flag-candidate` are genuinely rarer — deliberate
> re-planning, escalation and out-of-scope capture, not the drive loop's everyday path — so they
> stay CLI-only rather than inflating the tool count to be safe.
>
> 13 of 18 verbs covered. Verb coverage is a grouping decision, not a cap: this budget must be
> revisited if a later gate proves one of the 5 CLI-only verbs is load-bearing on the drive loop.

That escape clause set the wrong test. Coverage is no longer a question of which verbs turn out to
be load-bearing, and no longer a tool-count budget question at all. **Update that docstring section
to say so** — including the `13 of 18` line and the `decision:mcp-is-the-vehicle` "roughly seven"
budget it cites. Leaving the old rationale in place while the code contradicts it is the same drift
this epic exists to stop. Also delete the **CLI-fallback table** below it; there is no fallback now.

## Suggested grouping — argue with it if you have better

The door groups verbs into tools rather than one tool per verb, and that style should hold.

| tool | verbs | why they group |
|---|---|---|
| `spine_halt` (existing, extended) | `block`, `resume`, **`skip`**, **`reopen`** | all four change a gate's status without doing the gate's work |
| `spine_capture` (new) | **`append`**, **`flag-candidate`** | both add a new item to the plan: a task, or an out-of-scope candidate |
| `spine_amend` (new) | **`amend`** | deliberate re-planning under a named authority; a different concern from either of the above |

7 tools become 9. **Do not rename `spine_halt`** even though "halt" reads oddly once it also skips
and reopens — a rename breaks any agent mid-run, and stability outranks the naming tension. Say in
your result if you think the tension is worth a follow-up issue.

If you find a grouping that reads better, take it — but say why, and keep the tool count near this.

## `amend` is a pass-through, and this is the part to get right

`checklist_engine.py amend` takes `--delta DELTA`, a **path** to a JSON file of the form
`{"ops": [...]}`, plus `--reason` and `--authority`.

The door must **not** re-derive or validate the delta schema at the MCP boundary. That would create
a second definition of the op grammar, which is exactly the second-rendering-path failure this epic
keeps hitting. Instead:

1. Accept the delta as a JSON value in the tool arguments.
2. Write it to a file under **the bound spine's own `.agent-work/` directory** — the human's ruling:
   *"we can and should use the agent work folder that is coherent per task just like the spine."*
   Beside the spine it amends, not in a system temp dir, so the artifact is per-task coherent and
   survives for audit.
3. Hand the engine the same `--delta <path>` it already parses, and let it do the validating.

**Confine that path the same way `spine_advance.from_child` is confined.** `_identity_violation`
already restricts `from_child` to the bound spine's own directory tree; the delta path must not be
caller-controlled in a way that escapes it. Reuse that mechanism — do not write a second one.

## Hard no-gos

- Do **not** weaken `_identity_violation`. Every new verb goes through the same argv guard, and the
  guard asks **argparse**, not a token scanner. Six predecessors each modelled a shape a redirect
  might take and each was defeated by a shape they had not enumerated; read that docstring before
  you touch it.
- Do **not** open per-call spine addressing. Per-process binding is the ruled design: the door binds
  `SPINE_FILE`/`SPINE_SESSION` at launch so a model cannot redirect it mid-conversation.
- Do **not** modify `checklist_engine.py` at all. The engine already implements all five verbs; this
  is door work only.
- Do **not** touch `settings.json` or `docs/agents/*`.
- **No merge or push to `main`.**

## Out of scope — the rest of #559 is separate work

Removing the CLI from the corpus's instruction text (19 mentions across 13 files) and withholding
the engine from the crew tool grant are **not** yours. They land after this, deliberately: remove
the CLI before the door covers these verbs and an agent strands mid-run on a verb it can no longer
reach. Finding them is fine; doing them is not.

## Required evidence

- **A control per verb, before the fix:** show that the verb is unreachable through the door today.
- Each new tool exercised against a real scratch spine through a real JSON-RPC handshake, not only
  through unit tests — the door has been "proven" by prose before in this epic and it was wrong.
- For `amend`: show the delta file lands under the task's `.agent-work/`, show the engine accepts
  it, and show a path that tries to escape the confinement is refused.
- Tests that fail without the change.
- Full suite with real counts:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  Use `python`, not `python3`; `/usr/bin/python3` here has no pytest. `docs/agents/CREW_CONTEXT.md`
  shows you how to check that on any host.

## Drive your spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` automatically. Use `mcp__spine__*`, found via
`ToolSearch`. You are building the door while driving it; if a tool you are adding would have helped
you drive your own spine, say so — that is the best evidence this change is right.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **Honest null:** a measured negative is a complete, successful deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here; two crews have already committed run artifacts
  with `git add -A`.

## Deliverable

`.agent-work/epic-418-followon/n1-verb-closure/IMPLEMENTER_RESULT.md`, from the implementer skill's
template, including its **Workflow Feedback** section. Write it before ending your turn.
