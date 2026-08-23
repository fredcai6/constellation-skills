# Implementer Handoff

## Gate
g5-implement (execute.json, work-id w3-promote)

## Task
Promote real `check: null` conditions in `skills/charter/templates/CHARTER.template.json` using
only the engine's existing check kinds — per `decision:no-new-check-kinds`. Then red-proof each
promotion and sync the `.agent-work/templates/` overlay.

## Protected Intent
No decorative artifact conditions. A check that cannot fail is worse than the honest `check: null`
it replaces.

## Test Mode
Test-after allowed.

## Close Criteria
Fresh-verify each against the real shipped JSON first:
1. `project-templates.c1` ("project-specific templates seeded") → `artifact`, reusing the exact
   enum-match pattern already shipped on COMMANDER_SPINE's `plan.c1` (should be landed on this
   branch already by the time you run — read it and mirror its shape): `match: {"status":
   ["seeded", "skipped-no-need"]}` (the imperative's own text says "skip with reason if none
   needed" — your enum values must match what an agent following THIS gate's own imperative would
   actually report, read `project-templates`'s imperative text and confirm the exact status
   vocabulary before committing to it).
2. `closeout.c1` ("durable outputs complete; work area archived") → SPLIT promotion: existence
   check for the archived-work-area half ONLY (confirm the real archive path convention from
   `scripts/spine_lifecycle.py`, do not invent one — if none is confirmable, leave this whole
   condition `check: null` and say so). "Durable outputs complete, no open questions, contradiction
   pass done" stays unverified.
3. `interrogate.c1` ("doctrine resolved to role-operable decisions") → ONLY IF a real, reusable
   verifier for `interrogation.json`'s terminal/consolidated state already exists somewhere in
   `scripts/` (check `docs/CHECK_SCRIPT_CENSUS.md` for `verify_interrogation.py` — it's listed
   live elsewhere in the corpus; confirm whether reusing it here is a legitimate promotion or a
   category mismatch). If no clean reuse exists, leave this condition `check: null`.
- Do NOT touch `orchestrator-context.c1` or `agent-guide.c1` — both already carry real checks
  (only their redundant PRECONDITIONS are null, which stay null per this file's own established
  gate-order pattern — do not touch `orchestrator-context.p1` or `agent-guide.p1` either).
- Every other `check: null` condition in this file stays untouched.
- `.agent-work/templates/CHARTER.template.json` byte-matches the edited source.
- A red-proof test class in `tests/test_checklist_engine.py`, same pattern as g1's.
- Note in your result: CHARTER runs once per repo (bootstrap), not per-issue — state this
  frequency difference plainly since it changes the cost of a false-negative here relative to
  COMMANDER_SPINE.
- Update `tests/test_validate_spine.py`'s floor if an all-null gate clears (this file currently
  has 6 all-null gates — context, explore, interrogate, rigor, project-templates, closeout —
  clearing even one changes the corpus count).
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/charter/templates/CHARTER.template.json` (raw text hand-edit only).
- `.agent-work/templates/CHARTER.template.json` (overlay sync).
- `tests/test_checklist_engine.py` (new test class only).
- `tests/test_validate_spine.py` (floor numbers only, if triggered).

## Specific Exclusions
Do not touch `orchestrator-context.c1`/`agent-guide.c1` (already real-checked). Do not touch other
already-landed templates from prior gates. Do not touch `checklist_engine.py`.

## Constraints
- `decision:no-new-check-kinds`.
- `decision:blocking-where-adjudicated` — blocking only for kinds already live in THIS template;
  first-use-in-this-template is a stop condition.
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md`, `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human · leans g5-implement`;
  `decision:blocking-where-adjudicated` `@grade: settled/human · leans g5-implement`.

## Deliverable Path Check
- **Committed** — `skills/charter/templates/CHARTER.template.json`; verify
  `git check-ignore skills/charter/templates/CHARTER.template.json` exits 1.
- **Committed** — `.agent-work/templates/CHARTER.template.json`; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/charter/templates/CHARTER.template.json`.
- JSON parse-check command output.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/charter/templates/CHARTER.template.json` before/after.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/charter/templates/CHARTER.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded.

## Authority
Which conditions to promote is a first-pass judgment call, not frozen — adjust and report if your
fresh read disagrees. An honest zero for `interrogate.c1`/`closeout.c1` is acceptable if no real
locator confirms.

## Stop Conditions
Stop and return if: no stable archive path convention exists for `closeout.c1`;
`verify_interrogation.py`'s reuse for `interrogate.c1` is ambiguous; any edit would require
touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g5-implementer-result.md` before ending your turn.
