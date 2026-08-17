# docs/agents/engine-config.json is referenced by three files and does not exist

`specs/implementer.spine.toml` and `specs/reviewer.spine.toml` both set
`config_ref = "docs/agents/engine-config.json"`. The Commander spine's `context` imperative also
names it as a project delta to read. `EXECUTE_PLAN.template.json` sets the same `config_ref`.

**Measured:** `docs/agents/` contains exactly CREW_CONTEXT.md, GLOSSARY.md, ORCHESTRATOR_CONTEXT.md.
The file does not exist. The engine tolerates the dangling reference (this run's plan drove fine),
so it is latent rather than breaking.

**Candidate fix:** create the config, or drop the `config_ref` from the specs and the template.

---

## g3 addendum — two pieces of evidence that change the disposition

Re-measured at gate `g3` (lane D1, epic #567 wave 2). `find . -name engine-config.json` returns
**nothing anywhere in the repo**, and the reference is not three files but a repo-wide convention:
`docs/CHECKLIST_SCHEMA.md`, five test modules, four `episodes/` records, both `specs/` role specs and
every archived spine carry it.

**1. "Create the config" is probably the wrong half of the fix, because the absence is ruled
deliberate.** `docs/CHECKLIST_SCHEMA.md:35-38`, verbatim:

> **`config_ref` is a crash surface.** `load_config` calls `json.loads` on any `config_ref` that
> **exists**, so a `config_ref` pointing at a real non-JSON file raises an unhandled
> `JSONDecodeError` before any rail text can print. A *missing* path falls through to `{}` and is
> harmless, which is why every shipped template's nonexistent `docs/agents/engine-config.json` is
> fine.

Confirmed in the engine: `checklist_engine.load_config` (scripts/checklist_engine.py:407-422) returns
`{}` when no candidate path exists, so the plan runs on defaults (`DEFAULT_REWORK_CAP = 3`). Creating
the file would convert a documented no-op into a live crash surface for anyone who later edits it
badly. The schema doc is why this is a decision to take deliberately, not a dangling pointer to
tidy.

**2. For the SURVEY half there is already a pinned precedent going the other way.**
`skills/explorer/templates/CYCLE.template.json` — also a survey — **drops the key entirely**, and
`tests/test_explorer_templates.py:242-247` pins that choice with its reasoning:

> A survey never consults `rework_cap` (`reopen` raises for non-gated), so it needs no config. The
> key is dropped rather than pointed at a file a fresh install won't have.

`specs/reviewer.spine.toml` is `type = "survey"` and still carries the key, so the two shipped survey
artifacts state opposite conventions. Nothing pins the specs' side: `tests/test_generate_spine.py`
pins only `parent == "<parent>"` on the shipped specs, never `config_ref`.

**Sharpened candidate.** Not "create it or drop it" but two separable decisions:

- **Surveys** (`specs/reviewer.spine.toml`): drop `config_ref`, matching `CYCLE.template.json` and its
  pinned reason. Behaviourally a no-op today; it removes a contradiction between two shipped survey
  artifacts.
- **Gated plans** (`specs/implementer.spine.toml`, `EXECUTE_PLAN.template.json`): a gated plan DOES
  consult `rework_cap`, so the key is meaningful there and the question is whether a repo that ships
  no config should point at one. Answering it needs the human who owns the rework-cap default, not a
  sweep.

**Not fixed at g3, deliberately.** The handoff's bar was "free and obviously right". Half of it is
free (the survey key) and half of it is a defaults decision; and `CHECKLIST_SCHEMA.md` blesses the
current state in writing, so silently changing it inside a doctrine-vocabulary gate would be a
change nobody asked for, made against a documented ruling.
