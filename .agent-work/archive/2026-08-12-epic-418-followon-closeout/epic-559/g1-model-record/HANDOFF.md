# Handoff — G1: the registry does not record what model a crew ran at

**Work id:** `epic-559/g1-model-record` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/g1-model-record` (branch
`epic-559/g1-model-record`, base `5469c906` = current `main`)
**Deliverable:** `.agent-work/epic-559/g1-model-record/IMPLEMENTER_RESULT.md`

## The defect, measured

`scripts/run_crew.py` accepts `--model`, forwards it correctly to the spawned `claude -p` (line
`603`: `argv += ["--model", model]`), and **never records it in the registry entry on the path that
spawns anything.**

- `build_entry(...)` supports the field: `if model: entry["model"] = model` (line ~884).
- The **external** backend passes it: `build_entry(..., model=spec.model, ...)` (line ~1228).
- The **cli** backend does not: `build_entry(...)` at line ~1102 omits `model` entirely.

So every spawned crew in this repo's history has a registry entry with no `model` key, while the
record-only backend has one. **The field's presence on the external path is exactly what made the
omission look like data.**

### The Admiral's reproduction, which you should re-run first

Dispatched a real crew with an explicit `--model sonnet`:

- `--model sonnet` is visible on `run_crew.py`'s own process command line;
- `--model sonnet` is visible on the child `claude -p` process command line;
- the registry entry for that crew still has **no `model` key**.

Confirm this yourself before changing anything. If it does not reproduce, stop and say so — the whole
task rests on it.

### Why it matters beyond tidiness

An Admiral read that absent field as evidence that a Commander had never passed `--model`, and built a
finding on it across nine dispatches. The finding was wrong. **A field that is absent for two
different reasons — never supplied, or supplied and dropped — cannot distinguish them**, which is the
defect class this whole epic exists to remove, sitting in the run record itself.

Until this lands, no run record in `.agent-work/` can answer "what model did this crew run at?"

## The task

1. **Red control first.** Write the failing test before the fix: dispatch (or construct) a cli-backend
   entry with a model and assert the entry carries it. Run it, watch it fail, paste the failure.
2. **Fix:** pass `model=spec.model` in the cli backend's `build_entry(...)` call.
3. **Pin both paths.** A test asserting the cli path records what it was given, and one asserting the
   external path still does. **The asymmetry is the bug** — pin the symmetry, not just the line.
4. **Say what else is asymmetric.** Compare the two `build_entry(...)` call sites argument by argument
   and report **every** field one passes and the other does not. Enumerate them all rather than
   confirming the one you fixed. If `model` is the only one, say so plainly — that is a complete
   answer. If there are others, do not fix them; report them.

## Scope

**In:** `scripts/run_crew.py`, `tests/test_crew_launcher.py`.

**Out — hard no-gos:** `scripts/checklist_engine.py`, `scripts/validate_spine.py`,
`scripts/generate_spine.py`, `settings.json`, `.mcp.json`, anything under `skills/`. Do not
retroactively backfill historical registry entries — the past is unknowable and inventing a value
would be worse than the absence. No merge or push to `main`.

**Do not run `scripts/install_constellation.py`** — it rewrites the tracked `.mcp.json` interpreter
(known defect, #539).

## Test mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`. Unsetting the three spine variables matters: `mcp_spine_server.py` reads
`SPINE_FILE` at import time and raises `KeyError` without it. Baseline on this branch is **2689
passed, 3 skipped, 1121 subtests**.

## Standing rulings

- **A guard needs a violating case.** The repo's pattern is
  `tests/test_mcp_adoption.py::_cli_only_verb_violations` — VIOLATING / INNOCENT /
  ACCEPTED_FALSE_ALARM. A test that only exercises the happy path measures the mechanism, not the
  boundary. Four reviews in this wave missed defects for exactly that reason.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.
- **Honest null:** a measured negative is a complete deliverable.
- **Block, do not force.** A check you cannot satisfy means `spine_halt block`, naming your parent
  (`SPINE_PARENT`), and returning. Never waive your own gate.

## Deliverable

`.agent-work/epic-559/g1-model-record/IMPLEMENTER_RESULT.md`, from the implementer skill's template,
including its **Workflow Feedback** section. State the red control's failure output verbatim, and the
full asymmetry enumeration from task 4.
