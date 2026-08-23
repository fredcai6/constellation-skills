# Implementer Handoff

## Gate
g4-implement (execute.json, work-id w3-promote)

## Task
Promote real `check: null` conditions in `skills/explorer/templates/EXPLORER_SPINE.template.json`
using only the engine's existing check kinds — per `decision:no-new-check-kinds`. Then red-proof
each promotion and sync the `.agent-work/templates/` overlay.

## Protected Intent
No decorative artifact conditions. A check that cannot fail is worse than the honest `check: null`
it replaces.

## Test Mode
Test-after allowed.

## Close Criteria
Fresh-verify each against the real shipped JSON first (the shapes below are this Commander's own
hand-assessment, adjust if your fresh read disagrees, and say so):
1. `init.c2` ("engine session lease claimed...") → `command`, same seam as `g1`'s already-landed
   `COMMANDER_SPINE.template.json` `init.c1`. The exact shipped shape (mirror verbatim):
   `{"kind": "command", "command": "python3 -c \"import json,sys; d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', encoding='utf-8')); sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""}`.
   Confirm `command`-kind is independently justified against THIS template's own existing checks
   (EXPLORER_SPINE already has live `command`-kind checks — cite the specific sibling condition by
   grep).
2. `context.c1` ("doctrine + project deltas + map read where they exist; IDEAS_BOARD.md seeded
   from template") → SPLIT promotion: promote ONLY the "IDEAS_BOARD.md seeded" half — existence
   check for `.agent-work/<work-id>/IDEAS_BOARD.md`. Do NOT change the condition's `statement`
   text (the doctrine/map-read half stays unverified by this check, same as COMMANDER_SPINE's own
   `context.c1`, which stayed fully `check: null` for exactly this reason — do not over-promote
   here just because a partial locator exists).
3. `spec.c1` ("DESIGN_SPEC.md crystallized from the board with per-section approval; load-bearing
   interfaces designed-it-twice or skipped...") → SPLIT promotion: existence check for
   `.agent-work/<work-id>/DESIGN_SPEC.md` ONLY. The approval/fidelity half stays unverified — same
   shape as COMMANDER_SPINE's `plan.c2`.
4. `route.c1` ("confirmed spec routed (handed off / shaped-design issue filed / shelved with
   UNCONFIRMED header); work area archived; engine lease released") → investigate whether this is
   a genuine FULL promotion candidate: 3 named outcomes, each potentially having its own real
   artifact. Before committing to an enum-`match` shape, verify each of the 3 outcomes actually has
   an independently-checkable artifact (read `route`'s own imperative in the template for the exact
   file/marker each outcome produces). If even one outcome lacks a real artifact, do NOT force the
   enum — either promote existence-only for the sub-facts that do have real artifacts (archived,
   lease released), or leave this condition null and say so.
- Every other `check: null` condition in this file stays untouched.
- `.agent-work/templates/EXPLORER_SPINE.template.json` byte-matches the edited source.
- A red-proof test class in `tests/test_checklist_engine.py`, same pattern as g1's.
- Update `tests/test_validate_spine.py`'s floor if an all-null gate clears.
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/explorer/templates/EXPLORER_SPINE.template.json` (raw text hand-edit only).
- `.agent-work/templates/EXPLORER_SPINE.template.json` (overlay sync).
- `tests/test_checklist_engine.py` (new test class only).
- `tests/test_validate_spine.py` (floor numbers only, if triggered).

## Specific Exclusions
Do not touch COMMANDER_SPINE.template.json, ADMIRAL_SPINE.template.json, or their overlays
(g1/g3 own them, already landed by the time you run). Do not touch `checklist_engine.py`.

## Constraints
- `decision:no-new-check-kinds`.
- `decision:blocking-where-adjudicated` — blocking only for kinds already live in THIS template;
  a first-use-in-this-template candidate is a stop condition, consult before shipping blocking.
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md` (note: `verify_spec_confirmed.py` and
  `verify_cycles.py` are already live-wired in THIS file — read their existing command checks
  before inventing a new locator for `route.c1`), `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human · leans g4-implement`;
  `decision:blocking-where-adjudicated` `@grade: settled/human · leans g4-implement`.

## Deliverable Path Check
- **Committed** — `skills/explorer/templates/EXPLORER_SPINE.template.json`; verify
  `git check-ignore skills/explorer/templates/EXPLORER_SPINE.template.json` exits 1.
- **Committed** — `.agent-work/templates/EXPLORER_SPINE.template.json`; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/explorer/templates/EXPLORER_SPINE.template.json`.
- JSON parse-check command output.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/explorer/templates/EXPLORER_SPINE.template.json` before/after.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/explorer/templates/EXPLORER_SPINE.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded — mirrors g1's already-proven pattern.

## Authority
Which conditions to promote is a first-pass judgment call, not frozen — adjust and report if your
fresh read disagrees.

## Stop Conditions
Stop and return if: `route.c1`'s enum outcomes lack real per-outcome artifacts; a promotion would
be first-use-of-kind in this template and blocking-vs-report-only is unclear; any edit would
require touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g4-implementer-result.md` before ending your turn.
