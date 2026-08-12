# Implementer handoff — B: turn "run this script" instructions into checks the engine runs

**Work id:** `epic-559/b-instructions-to-checks` · **Gate:** `g1-implement` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks` (branch `epic-559/b-instructions-to-checks`, off `main`@`9d593e0a`)
**Your spine:** `.agent-work/epic-559/b-instructions-to-checks/IMPLEMENTER_PLAN.json` — drive it gate by gate.

## Task

The shipped spine templates tell agents to run scripts. Move that work into the engine.

Where a gate's imperative says "run `verify_state_note.py`", "run
`verify_iterative_role_artifacts.py` in the foreground before launching", "run
`verify_episode_captured.py` before advancing" — the script should instead be a **command
postcondition on that gate**. The engine already runs command checks and already refuses to advance
when one fails. The agent should never need to know the script exists.

**Scope: all five role templates.** The human ruled "all roles", including the Admiral's own.

```
skills/admiral/templates/ADMIRAL_SPINE.template.json
skills/commander/templates/COMMANDER_SPINE.template.json
skills/commander/templates/EXECUTE_PLAN.template.json
skills/explorer/templates/EXPLORER_SPINE.template.json
skills/implementer/templates/IMPLEMENTER_PLAN.template.json
skills/reviewer/templates/REVIEW_SURVEY.template.json
```

## Intent

The human's intent, in their words: *"we should be aggressively figuring out how to replace prose
with scripts... my intent is for this to be used with less capable agents. the more we can remove
from instructions and put behind tools the better."*

An instruction is a thing an agent can misread, skip, or run at the wrong time. A check is a thing
that is simply true or not when the gate closes. Every instruction converted is one fewer way for a
weaker agent to go wrong — and it makes the check impossible to forget, rather than merely
documented.

## The pre-ruling on which instructions become blocking checks

Do not deliberate this per case:

- **Becomes a blocking command postcondition:** anything the doctrine already treats as mandatory
  before proceeding — text of the form "run X before Y", "a nonzero result refuses the launch", "run
  the capture gate before advancing", "prove it with X".
- **Stays as it is:** anything deliberately fail-open or advisory. `scripts/hooks/spine_rail.py` is
  explicitly designed never to block ("any error anywhere prints nothing and exits 0") — do not
  convert an advisory rail into a refusal.
- **If you cannot tell**, leave it and list it in your result. An unconverted instruction is a
  smaller problem than a gate that now refuses for the wrong reason.

Keep the imperative readable. Removing the "run X" sentence is the point; do not strip the
surrounding intent that tells the agent *why* the gate exists.

## Second task: fix the gate that cannot fail (#562)

`skills/commander/templates/EXECUTE_PLAN.template.json`, gate `g1-implement`, condition `c1`:

```json
{"statement": "IMPLEMENTER_RESULT returned with no unresolved blockers",
 "check": {"kind": "artifact", "evidence_type": "implementer-result"}}
```

There is no `match`. The engine does `all(... for k, v in want.items())` over an empty `want`, which
is vacuously true, so **any** `implementer-result` evidence satisfies it — including one reporting
the work as blocked. The clause "with no unresolved blockers" is enforced by nothing.

The same file gets it right twice, which is how you can tell this is a slip and not a convention:
`g1-review.c1` claims only "REVIEW_RESULT returned" and is honest with a bare artifact check;
`g1-integrate.c2` claims "reviewer verdict is APPROVE" and carries `match: {"verdict": "APPROVE"}`.

Fix it, and **sweep all six templates for the same shape**: a statement that asserts a property
while its check only proves an artifact of some type arrived. Either constrain the check to the
claim or weaken the statement to what the check actually proves. Say which you chose and why for
each one. See #562.

## Hard no-gos

- Do **not** modify `scripts/checklist_engine.py` — the engine already runs command checks.
- Do **not** modify `scripts/run_crew.py` or the crew skill files. Another crew owns those this
  wave; if you find something that belongs there, write it in your result.
- Do **not** touch `settings.json` or `docs/agents/*`.
- **Edit compact-format JSON templates surgically as raw text.** Never round-trip them through
  `json.load`/`json.dump` — it reflows the whole file and destroys blame. Re-validate with
  `json.load` afterwards.
- **No merge or push to `main`.**

## A caution that applies specifically to you

You are editing the templates that govern how orchestrators run, including the Admiral's. A gate
that now refuses for the wrong reason will block a real run. So for each converted check, show the
command actually passing in a clean checkout — a check that refuses a healthy repo is worse than the
instruction it replaced.

Watch for scripts that take a work-id or a path argument. The template resolves placeholders like
`<work-id>` at instantiation (`scripts/init_work_area.py::resolve_spine`); your command must use the
same placeholders so it resolves the same way, and must not hardcode a path from this worktree.

## Required evidence

- A before/after list: every instruction converted, with the gate it landed on and the command.
- Every converted command run in a clean checkout, shown passing.
- At least one shown **failing** for the right reason when its precondition is genuinely unmet —
  a check that cannot fail is the defect you are here to remove, not to add.
- The #562 fix, plus the sweep result for all six templates.
- Full suite with real counts:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  Use `python`, not `python3`. Several tests check shipped-template structure, so expect them to
  have opinions.

## Drive your own spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` for you. Use the `mcp__spine__*` tools, found
via `ToolSearch`. The door covers all 18 engine verbs.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **Honest null:** a measured negative is a complete deliverable. If a category of instruction turns
  out not to be convertible, saying so clearly is the deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.

## Deliverable

`.agent-work/epic-559/b-instructions-to-checks/IMPLEMENTER_RESULT.md`, from the implementer skill's
template, including its **Workflow Feedback** section. Write it before ending your turn.
