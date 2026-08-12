# Implementer handoff — gate `g4a-implement` (#542 criterion 1, adoption)

## Task

Make role spine instructions name the **MCP door's tools as the default path**, with the
**CLI documented as the remaining fallback**. Then pin both halves with a test.

## Protected intent

The door (`scripts/mcp_spine_server.py`, 7 tools over 13 of the engine's 18 verbs) has been
built, merged, and is **completely unused**: measured on this base, **zero** files under
`skills/` mention it. This gate is what makes an agent reach for it.

**The CLI door stays. F is additive.** Adoption changes the **default**, never the
**availability**. An edit that removes a CLI path **fails this gate**. This is a
settled/human pre-ruling (`the-cli-door-stays`), not a preference.

## The invariant chain — pre-authored, so you verify a frozen list rather than invent a proxy

This is a **doc-only gate**. There is no runtime behaviour to lean on, which is exactly the
condition under which an under-specified crew invents a grep-for-a-marker proxy. So the
operative invariants are enumerated here, and your test verifies **this list**:

**Tier 1 — literal engine command lines an agent executes. Each of these 7 imperative
fields must name a door tool as the default, by JSON field path:**

| File | Field paths |
|---|---|
| `skills/commander/templates/COMMANDER_SPINE.template.json` | `.tasks.init.imperative`, `.tasks.plan.imperative`, `.tasks.archive.imperative` |
| `skills/admiral/templates/ADMIRAL_SPINE.template.json` | `.tasks.init.imperative`, `.tasks.closeout.imperative` |
| `skills/explorer/templates/EXPLORER_SPINE.template.json` | `.tasks.init.imperative`, `.tasks.route.imperative` |

Plus `skills/commander/references/commander-core.md:127` (the delegated-mode `attach`
command line).

**Tier 2 — default-path prose in SKILL bodies.** Each must name the door as the default and
keep the CLI as the fallback:
`skills/workbench/SKILL.md`, `skills/charter/SKILL.md`, `skills/reviewer/SKILL.md`,
`skills/interrogator/SKILL.md`, `skills/implementer/SKILL.md`, `skills/explorer/SKILL.md`.

**Tier 3 — the engine CLI reference every one of those points at, and the single
highest-leverage file:** `skills/workbench/references/checklist-engine.md`.

**Tier 4 — authoring templates that would otherwise propagate the CLI default to future
skills:** `skills/write-a-skill/templates/gated-engine-SKILL.template.md`,
`skills/write-a-skill/templates/survey-SKILL.template.md`.

**Tier 5 — DO NOT TOUCH.** `skills/_shared/global-everyone.md` (~lines 70, 178, 254) and
`skills/admiral/references/fleet-doctrine.md` (~234) name `checklist_engine.py` as an
**artifact** in narrative prose, not as a command to run. Leaving them is deliberate.

## Close criteria

1. Every Tier 1 imperative field names a door tool as the default path.
2. Every Tier 1–4 file **still names the CLI** as the documented fallback.
3. The **5 CLI-only verbs** — `skip`, `reopen`, `append`, `amend`, `flag-candidate` — are
   still documented as CLI, because **no door tool exists for them**. The authority on
   which verbs those are is the fallback table in `mcp_spine_server.py`'s module docstring.
   An instruction that sends an agent to a tool that does not exist is worse than the CLI
   instruction it replaced.
4. `tests/test_mcp_adoption.py` exists and asserts **both halves per file**.

## The test must be two-sided or it is not evidence

A test asserting only "a door tool is named" **would also pass an edit that deleted the
CLI**. Every assertion is two-sided. Prove it: after writing the test, temporarily delete a
CLI mention from one file and confirm the test goes **RED**, then restore. Paste that
evidence. This run has already had four separate pins defeated for being weaker than the
claim they protected — do not add a fifth.

Assert on the **imperative field itself**, by JSON field path, not on the file's text.
A file-level `assert "mcp__spine__" in text` passes an edit that adds one sentence to a
header while every literal command line still says `checklist_engine.py`.

## Allowed scope

The Tier 1–4 files above, and `tests/test_mcp_adoption.py` (new).

## Specific exclusions

- **Never** `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  `scripts/install_constellation.py`, `scripts/hooks/spine_rail.py`.
- **Never** the Tier 5 files.
- Do not remove, deprecate, or discourage the CLI anywhere. Discouraging it is removing it
  in prose.

## Constraints

- **Canonical shared doctrine is `skills/_shared/global-*.md`, NEVER
  `skills/<role>/references/global-*.md`** — `install_constellation.py` regenerates the
  latter at install time and silently overwrites it. An edit there is lost work.
- **Edit compact-format JSON templates as RAW TEXT, surgically.** Never round-trip through
  `json.load`/`json.dump` — it reflows the whole file and destroys blame. **Re-validate
  with `json.load` afterward.**
- Run the suite as **`python -m pytest`**, NEVER `python3 -m pytest` — `/usr/bin/python3`
  has no pytest here and its non-zero exit reads as a red suite and is not one.
- **Never pipe a command into `head`/`tail` and read the exit code.** Redirect to a file,
  capture `$?`.
- **Rebuild the code map as part of your commit**: `python -m scripts.code_map build
  --root .`. Adding a test module changes entity counts and
  `tests/test_code_map.py::MapTreeFreshnessTests` will otherwise go red.
- Avoid backticks and command-looking text inside engine string arguments.
- Windows writes need `encoding='utf-8', newline='\n'` explicitly on every write.
- Work only in this worktree; `/home/tommy/projects/constellation-skills` is fenced
  read-only.

## Anchors

**Structural:** the 7 imperative fields in the 3 spine templates (Tier 1);
`skills/workbench/references/checklist-engine.md` — the canonical invocation (~line 5) and
the lease verb table (~69-78); the 6 SKILL bodies; the 2 authoring templates.

**Constraint:** the CLI door stays, F is additive. 13 of 18 verbs have a door tool; the
other 5 are CLI-only **by design**, documented in `mcp_spine_server.py`'s fallback table
with a stated reason each.

**Decision:** `the-cli-door-stays` — settled/human, leans g4a. And from g1
(`IDENTITY_TRADE.md`): **an in-session dispatched crew member cannot drive its own plan
through the door** — a Commander may use the door for its own spine, but an Implementer or
Reviewer it dispatches in-session must use the CLI. **The instructions you write must say
this**, or a crew will reach for a door bound to someone else's spine.

**Confidence flag:** doc-only gate. The invariant chain above is the frozen list your test
verifies; it is not background reading.

## Verification commands

```
python -m pytest -q tests/test_mcp_adoption.py
python -c "import json;[json.load(open(p)) for p in ['skills/commander/templates/COMMANDER_SPINE.template.json','skills/admiral/templates/ADMIRAL_SPINE.template.json','skills/explorer/templates/EXPLORER_SPINE.template.json']]"
python -m pytest -q
```

Also report the re-measured adoption count:
`grep -rlE 'mcp__spine__|spine_status|spine_lease|spine_start|spine_advance|spine_evidence|spine_halt|spine_survey_result' skills/` — it was **0** at the wave boundary. Report it as
a **number**, not as this gate's evidence; the gate closes on the two-sided test.

## Deliverable path check

Run `git check-ignore <path>` for each committed deliverable; confirm **exit 1**.

## Authority

Admiral, epic-418-followon, wave 2. The Commander is delegated; the human is AFK. If you
hit a decision this handoff does not settle, **say so in your result** rather than guessing.

## Result

Write your `IMPLEMENTER_RESULT` — what changed per file, the two-sided test evidence
including the deliberate CLI-deletion going red, the re-measured count, anything you could
not do, and a `Workflow Feedback` section — to
`.agent-work/epic-418-followon/commander-f2/crew-handoffs/g4a-implement-implementer-result.md`.
**That write is the delivery.**
